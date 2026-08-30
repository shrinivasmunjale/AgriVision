import os
import httpx
from io import BytesIO
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0B2B1E'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1B4332'),
            spaceAfter=12,
            spaceBefore=12
        ))

    def _get_image_flowable(self, image_url: Optional[str]) -> Optional[RLImage]:
        """Fetch image from local disk or URL and return ReportLab Image flowable with proper aspect ratio."""
        if not image_url:
            return None
        try:
            import base64
            from PIL import Image as PILImage
            img_source = None

            # 1. Check if Base64 Data URL
            if isinstance(image_url, str) and image_url.startswith("data:image/"):
                try:
                    _, encoded = image_url.split(",", 1)
                    img_data = base64.b64decode(encoded)
                    img_source = BytesIO(img_data)
                except Exception as b64_err:
                    print(f"[PDF] Error decoding base64 image: {b64_err}")

            # 2. Check if image is stored in local uploads directory
            if not img_source and isinstance(image_url, str) and ("uploads/" in image_url or "/uploads/" in image_url):
                clean_name = image_url.split("uploads/")[-1].lstrip("/\\").split("?")[0]
                backend_dir = Path(__file__).resolve().parent.parent.parent
                candidates = [
                    backend_dir / "uploads" / clean_name,
                    Path.cwd() / "backend" / "uploads" / clean_name,
                    Path.cwd() / "uploads" / clean_name,
                    Path("backend/uploads") / clean_name,
                    Path("uploads") / clean_name,
                ]
                for cand in candidates:
                    if cand.exists() and cand.is_file():
                        img_source = str(cand.resolve())
                        break

            # 3. Check if image_url is a direct local file path
            if not img_source and isinstance(image_url, str):
                direct_cand = Path(image_url)
                if direct_cand.exists() and direct_cand.is_file():
                    img_source = str(direct_cand.resolve())

            # 4. If remote URL (e.g. Cloudflare R2 / S3), download via httpx
            if not img_source and isinstance(image_url, str) and (image_url.startswith("http://") or image_url.startswith("https://")):
                try:
                    with httpx.Client(timeout=10.0) as client:
                        resp = client.get(image_url)
                        if resp.status_code == 200:
                            img_source = BytesIO(resp.content)
                except Exception as http_err:
                    print(f"[PDF] HTTP fetch failed for ({image_url}): {http_err}")

            if img_source:
                # Open with PIL to calculate proportional width and height (max 4.5" x 3.2")
                pil_img = PILImage.open(img_source)
                
                # Convert RGBA / P to RGB to avoid ReportLab PDF issues
                if pil_img.mode in ("RGBA", "P"):
                    rgb_buf = BytesIO()
                    pil_img.convert("RGB").save(rgb_buf, format="JPEG", quality=95)
                    rgb_buf.seek(0)
                    img_source = rgb_buf
                    pil_img = PILImage.open(img_source)

                orig_w, orig_h = pil_img.size
                
                max_w = 4.5 * inch
                max_h = 3.2 * inch
                
                scale = min(max_w / orig_w, max_h / orig_h)
                render_w = orig_w * scale
                render_h = orig_h * scale

                # If BytesIO, rewind
                if isinstance(img_source, BytesIO):
                    img_source.seek(0)

                rl_img = RLImage(img_source, width=render_w, height=render_h)
                rl_img.hAlign = 'CENTER'
                return rl_img
        except Exception as e:
            print(f"[PDF] Error loading image for PDF report ({image_url}): {e}")
        return None
    
    def generate_report(
        self, 
        prediction_data: Dict,
        user_data: Dict,
        disease_data: Dict,
        recommendations: List[Dict]
    ) -> BytesIO:
        """
        Generate a PDF report for a prediction
        Returns BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("AgriVision AI - Crop Health Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y %I:%M %p")
        metadata_text = f"""
        <b>Report Generated:</b> {report_date}<br/>
        <b>Farmer:</b> {user_data.get('name', 'N/A')}<br/>
        <b>Farm:</b> {user_data.get('farm_name', 'N/A')}<br/>
        <b>Email:</b> {user_data.get('email', 'N/A')}<br/>
        """
        metadata = Paragraph(metadata_text, self.styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 0.2*inch))
        
        # Analysis results section
        analysis_header = Paragraph("Analysis Results", self.styles['SectionHeader'])
        story.append(analysis_header)
        
        # Disease detection
        disease_name = disease_data.get('name', 'Unknown')
        confidence = prediction_data.get('confidence_score', 0.0)
        confidence_percent = f"{confidence * 100:.1f}%"
        
        status_color = "#34A65F" if disease_name == "Healthy" else "#FF6B6B"
        
        detection_text = f"""
        <b>Detected Condition:</b> <font color="{status_color}">{disease_name}</font><br/>
        <b>Confidence Level:</b> {confidence_percent}<br/>
        <b>Analysis Date:</b> {prediction_data.get('created_at', 'N/A')}<br/>
        """
        detection = Paragraph(detection_text, self.styles['Normal'])
        story.append(detection)
        story.append(Spacer(1, 0.2*inch))

        # Visual Inspection & YOLO Bounding Box Evidence Section
        annotated_url = prediction_data.get('annotated_image_url')
        original_url = prediction_data.get('image_url')
        
        img_flowable = self._get_image_flowable(annotated_url) if annotated_url else None
        if not img_flowable and original_url:
            img_flowable = self._get_image_flowable(original_url)

        if img_flowable:
            story.append(Paragraph("Visual Inspection & Diagnosis", self.styles['SectionHeader']))
            story.append(img_flowable)
            caption_text = "Figure 1: AI Visual inspection & Bounding Box annotation highlighting detected condition." if annotated_url else "Figure 1: Uploaded crop image for AI diagnosis."
            caption = Paragraph(f"<font color='#64748B' size='8'><i>{caption_text}</i></font>", self.styles['Normal'])
            story.append(caption)
            story.append(Spacer(1, 0.25*inch))
        
        # Disease information
        if disease_data and disease_name != "Healthy":
            disease_info_header = Paragraph("Disease Information", self.styles['SectionHeader'])
            story.append(disease_info_header)
            
            disease_info_text = f"""
            <b>Description:</b><br/>
            {disease_data.get('description', 'N/A')}<br/><br/>
            <b>Symptoms:</b><br/>
            {disease_data.get('symptoms', 'N/A')}<br/><br/>
            <b>Causes:</b><br/>
            {disease_data.get('causes', 'N/A')}<br/><br/>
            <b>Severity Level:</b> {disease_data.get('severity_level', 'N/A')}
            """
            disease_info = Paragraph(disease_info_text, self.styles['Normal'])
            story.append(disease_info)
            story.append(Spacer(1, 0.3*inch))
        
        # Recommendations section
        if recommendations and disease_name != "Healthy":
            rec_header = Paragraph("Treatment Recommendations", self.styles['SectionHeader'])
            story.append(rec_header)
            
            # Pesticides
            pesticides = [r for r in recommendations if r.get('pesticide_name')]
            if pesticides:
                pest_header = Paragraph("<b>Recommended Pesticides:</b>", self.styles['Normal'])
                story.append(pest_header)
                story.append(Spacer(1, 0.1*inch))
                
                for idx, pest in enumerate(pesticides, 1):
                    type_str = f" [{pest.get('type')}]" if pest.get('type') else ""
                    interval_str = f"<br/>Spray Interval: {pest.get('spray_interval')}" if pest.get('spray_interval') else ""
                    waiting_str = f"<br/>Waiting Period: {pest.get('waiting_period')}" if pest.get('waiting_period') else ""
                    effect_str = f"<br/>Effectiveness: {pest.get('effectiveness')}" if pest.get('effectiveness') else ""
                    pest_text = f"""
                    {idx}. <b>{pest['pesticide_name']}</b>{type_str}<br/>
                    Active Ingredient: {pest.get('active_ingredient', 'N/A')}<br/>
                    Dosage: {pest.get('dosage', 'N/A')}<br/>
                    Application: {pest.get('application_method', 'N/A')}{interval_str}{waiting_str}{effect_str}
                    """
                    story.append(Paragraph(pest_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
            
            # Fertilizers
            fertilizers = [r for r in recommendations if r.get('fertilizer_name')]
            if fertilizers:
                fert_header = Paragraph("<b>Recommended Fertilizers:</b>", self.styles['Normal'])
                story.append(fert_header)
                story.append(Spacer(1, 0.1*inch))
                
                for idx, fert in enumerate(fertilizers, 1):
                    fert_text = f"""
                    {idx}. <b>{fert['fertilizer_name']}</b><br/>
                    Composition: {fert.get('composition', 'N/A')}<br/>
                    Dosage: {fert.get('dosage', 'N/A')}<br/>
                    Application Stage: {fert.get('application_stage', 'N/A')}<br/>
                    Match Score: {fert.get('similarity_score', 0.0):.2f}
                    """
                    story.append(Paragraph(fert_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = """
        <i>This report is generated by AgriVision AI and should be used as a guide. 
        Please consult with agricultural experts for final treatment decisions.</i>
        """
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

pdf_generator = PDFReportGenerator()
