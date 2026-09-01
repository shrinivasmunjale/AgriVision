from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import httpx
from PIL import Image as PILImage

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
            spaceAfter=30,
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

    @staticmethod
    def _load_image_element(image_source: Optional[str], max_w=2.4*inch, max_h=2.2*inch) -> Optional[RLImage]:
        """Resolve image source (URL or local path) and return scaled ReportLab Image object."""
        if not image_source or not str(image_source).strip():
            return None

        path_str = str(image_source).strip()
        img_path = None

        # 1. Check if relative to /uploads/
        if "/uploads/" in path_str:
            filename = path_str.split("/uploads/")[-1]
            candidates = [
                Path("uploads") / filename,
                Path("backend/uploads") / filename,
                Path(__file__).resolve().parents[2] / "uploads" / filename,
            ]
            for cand in candidates:
                if cand.exists():
                    img_path = cand
                    break

        if img_path is None and not (path_str.startswith("http://") or path_str.startswith("https://")):
            p = Path(path_str)
            if p.exists():
                img_path = p

        try:
            if img_path and img_path.exists():
                pil_img = PILImage.open(img_path).convert("RGB")
            elif path_str.startswith("http://") or path_str.startswith("https://"):
                resp = httpx.get(path_str, timeout=5.0)
                resp.raise_for_status()
                pil_img = PILImage.open(BytesIO(resp.content)).convert("RGB")
            else:
                return None

            orig_w, orig_h = pil_img.size
            if orig_w <= 0 or orig_h <= 0:
                return None

            aspect = orig_w / float(orig_h)
            calc_w = max_w
            calc_h = calc_w / aspect
            if calc_h > max_h:
                calc_h = max_h
                calc_w = calc_h * aspect

            buf = BytesIO()
            pil_img.save(buf, format="JPEG", quality=90)
            buf.seek(0)
            return RLImage(buf, width=calc_w, height=calc_h)
        except Exception as e:
            print(f"[PDF Generator] Could not load image '{path_str}' for PDF: {e}")
            return None
    
    def generate_report(
        self, 
        prediction_data: Dict,
        user_data: Dict,
        disease_data: Dict,
        recommendations: List[Dict]
    ) -> BytesIO:
        """
        Generate a PDF report for a single prediction
        Returns BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("AgriVision AI - Crop Health Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
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
        story.append(Spacer(1, 0.3*inch))
        
        # Analysis results section
        analysis_header = Paragraph("Analysis Results", self.styles['SectionHeader'])
        story.append(analysis_header)
        
        # Disease detection
        disease_name = disease_data.get('name', 'Unknown')
        confidence = prediction_data.get('confidence_score', 0.0)
        confidence_percent = f"{confidence * 100:.1f}%"
        
        status_color = "#34A65F" if disease_name == "Healthy" else "#D9534F"
        
        # Derive image name
        raw_url = str(prediction_data.get('image_url') or "")
        img_name = prediction_data.get('filename') or (raw_url.split('/')[-1] if '/' in raw_url else "Uploaded Image")
        
        detection_text = f"""
        <b>Image Name:</b> {img_name}<br/><br/>
        <b>Detected Condition:</b> <font color="{status_color}">{disease_name}</font><br/><br/>
        <b>Confidence Level:</b> {confidence_percent}<br/><br/>
        <b>Analysis Date:</b> {prediction_data.get('created_at', 'N/A')}<br/>
        """
        detection_para = Paragraph(detection_text, self.styles['Normal'])

        # Load leaf image if available
        img_element = self._load_image_element(prediction_data.get('image_url'))

        if img_element:
            caption_style = ParagraphStyle(
                name='ImgCaption',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#555555'),
                alignment=TA_CENTER
            )
            img_caption = Paragraph(f"<b>File:</b> {img_name}", caption_style)
            right_column = [img_element, Spacer(1, 4), img_caption]

            table_data = [[detection_para, right_column]]
            results_table = Table(table_data, colWidths=[3.8*inch, 2.7*inch])
            results_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (1,0), (1,0), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F7F5')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D8E2DC')),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(results_table)
        else:
            story.append(detection_para)

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
                    pest_text = f"""
                    {idx}. <b>{pest['pesticide_name']}</b><br/>
                    Active Ingredient: {pest.get('active_ingredient', 'N/A')}<br/>
                    Dosage: {pest.get('dosage', 'N/A')}<br/>
                    Application: {pest.get('application_method', 'N/A')}<br/>
                    Match Score: {pest.get('similarity_score', 0.0):.2f}
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
                    Active Ingredient: {fert.get('active_ingredient', 'N/A')}<br/>
                    Dosage: {fert.get('dosage', 'N/A')}<br/>
                    Application Method: {fert.get('application_method', 'N/A')}<br/>
                    Suitable Life Stages: {fert.get('suitable_life_stages', 'N/A')}<br/>
                    Match Score: {fert.get('similarity_score', 0.0):.2f}
                    """
                    story.append(Paragraph(fert_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
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

    def generate_batch_report(
        self,
        user_data: Dict,
        batch_data: Dict
    ) -> BytesIO:
        """
        Generate a batch PDF report listing every detected disease across the batch,
        including crop image previews, symptoms, organic control, and recommendations.
        """
        from app.services.recommendation import recommendation_engine

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Title
        title = Paragraph("AgriVision AI - Batch Crop Health Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))

        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y %I:%M %p")
        metadata_text = (
            f"<b>Report Generated:</b> {report_date}<br/>"
            f"<b>Farmer:</b> {user_data.get('name', 'N/A')}<br/>"
            f"<b>Farm:</b> {user_data.get('farm_name', 'N/A')}<br/>"
            f"<b>Email:</b> {user_data.get('email', 'N/A')}<br/>"
        )
        story.append(Paragraph(metadata_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Batch summary
        batch_header = Paragraph("Batch Summary", self.styles['SectionHeader'])
        story.append(batch_header)
        summary_text = (
            f"<b>Images Uploaded:</b> {batch_data.get('total_uploaded', 0)} &nbsp;&nbsp; "
            f"<b>Processed:</b> {batch_data.get('processed', 0)} &nbsp;&nbsp; "
            f"<b>Ignored:</b> {batch_data.get('ignored', 0)}<br/>"
            f"<b>Healthy:</b> {batch_data.get('healthy', 0)} &nbsp;&nbsp; "
            f"<b>Infected:</b> {batch_data.get('infected', 0)}"
        )
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.25*inch))

        # Visual Analyzed Crop Images Section
        valid_predictions = batch_data.get('valid_predictions') or []
        if valid_predictions:
            imgs_header = Paragraph("Analyzed Crop Images", self.styles['SectionHeader'])
            story.append(imgs_header)
            story.append(Spacer(1, 0.1*inch))

            caption_style = ParagraphStyle(
                name='BatchImgCaption',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#555555'),
                alignment=TA_CENTER
            )

            for pred in valid_predictions:
                img_url = pred.get('image_url')
                disease_name = pred.get('disease_name') or "Unknown"
                confidence = pred.get('confidence_score', 0.0)
                confidence_percent = f"{confidence * 100:.1f}%" if confidence <= 1.0 else f"{confidence:.1f}%"
                
                raw_url = str(img_url or "")
                filename = pred.get('filename') or (raw_url.split('/')[-1] if '/' in raw_url else "Uploaded Image")
                
                status_color = "#34A65F" if disease_name == "Healthy" else "#D9534F"

                text_info = f"""
                <b>Image Name:</b> {filename}<br/><br/>
                <b>Detected Condition:</b> <font color="{status_color}">{disease_name}</font><br/><br/>
                <b>Confidence Level:</b> {confidence_percent}<br/>
                """
                info_para = Paragraph(text_info, self.styles['Normal'])

                img_elem = self._load_image_element(img_url, max_w=2.2*inch, max_h=2.0*inch)

                if img_elem:
                    img_cap = Paragraph(f"<b>File:</b> {filename}", caption_style)
                    right_col = [img_elem, Spacer(1, 3), img_cap]
                    tbl_data = [[info_para, right_col]]
                else:
                    tbl_data = [[info_para]]

                item_table = Table(tbl_data, colWidths=[3.8*inch, 2.7*inch] if img_elem else [6.5*inch])
                item_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (1,0), (1,0), 'CENTER'),
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F7F5')),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#D8E2DC')),
                    ('TOPPADDING', (0,0), (-1,-1), 8),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                    ('LEFTPADDING', (0,0), (-1,-1), 10),
                    ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ]))
                story.append(item_table)
                story.append(Spacer(1, 0.15*inch))

            story.append(Spacer(1, 0.2*inch))

        # Disease breakdown
        disease_summary = batch_data.get('disease_summary') or {}

        if not disease_summary:
            no_data = Paragraph(
                "<b>No valid disease information available for this batch.</b>",
                self.styles['Normal']
            )
            story.append(no_data)
            story.append(Spacer(1, 0.3*inch))
        else:
            for disease_name, files in disease_summary.items():
                disease_header = Paragraph(disease_name, self.styles['SectionHeader'])
                story.append(disease_header)

                files_text = ", ".join(files) if files else "-"
                story.append(
                    Paragraph(f"<b>Affected images ({len(files)}):</b> {files_text}", self.styles['Normal'])
                )
                story.append(Spacer(1, 0.15*inch))

                knowledge = recommendation_engine.get_disease_knowledge(disease_name)
                if not knowledge:
                    story.append(Paragraph("Detailed information unavailable.", self.styles['Normal']))
                    story.append(Spacer(1, 0.25*inch))
                    continue

                # General info
                info_text = f"<b>Severity:</b> {knowledge.get('severity', 'N/A')}<br/>"
                if knowledge.get('scientific_name'):
                    info_text += f"<b>Scientific Name:</b> {knowledge.get('scientific_name')}<br/>"
                if knowledge.get('description'):
                    info_text += f"<b>Description:</b><br/>{knowledge.get('description')}<br/>"
                story.append(Paragraph(info_text, self.styles['Normal']))
                story.append(Spacer(1, 0.12*inch))

                # Symptoms
                symptoms = knowledge.get('symptoms') or []
                if symptoms:
                    story.append(Paragraph("<b>Symptoms:</b><br/>" + self._as_bullets(symptoms), self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Causes
                causes = knowledge.get('causes') or []
                if causes:
                    story.append(Paragraph("<b>Causes:</b><br/>" + self._as_bullets(causes), self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Organic control
                organic = knowledge.get('organic_control') or []
                if organic:
                    story.append(Paragraph("<b>Organic Control:</b><br/>" + self._as_bullets(organic), self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Recommended pesticides
                pesticides = knowledge.get('recommended_pesticides') or []
                if pesticides:
                    story.append(Paragraph("<b>Recommended Pesticides:</b>", self.styles['Normal']))
                    for p in pesticides:
                        p_text = (
                            f"- <b>{p.get('name', 'N/A')}</b>"
                            f" (Dosage: {p.get('dosage', 'N/A')}; "
                            f"Application: {p.get('application_method', 'N/A')})"
                        )
                        story.append(Paragraph(p_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Recommended fertilizers
                fertilizers = knowledge.get('recommended_fertilizers') or []
                if fertilizers:
                    story.append(Paragraph("<b>Recommended Fertilizers:</b>", self.styles['Normal']))
                    for f in fertilizers:
                        f_text = (
                            f"- <b>{f.get('name', 'N/A')}</b>"
                            f" (Dosage: {f.get('dosage', 'N/A')}; "
                            f"Application: {f.get('application_method', 'N/A')})"
                        )
                        story.append(Paragraph(f_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Preventive measures
                preventive = knowledge.get('preventive_measures') or []
                if preventive:
                    story.append(Paragraph("<b>Preventive Measures:</b><br/>" + self._as_bullets(preventive), self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

                # Recovery tips
                recovery = knowledge.get('recovery_tips') or []
                if recovery:
                    story.append(Paragraph("<b>Recovery Tips:</b><br/>" + self._as_bullets(recovery), self.styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))

        # Ignored images
        ignored_images = batch_data.get('ignored_images') or []
        if ignored_images:
            ignored_header = Paragraph("Ignored Images", self.styles['SectionHeader'])
            story.append(ignored_header)
            for item in ignored_images:
                story.append(
                    Paragraph(
                        f"- <b>{item.get('filename', 'image')}</b>: {item.get('reason', 'Invalid image')}",
                        self.styles['Normal']
                    )
                )
            story.append(Spacer(1, 0.2*inch))

        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = (
            "<i>This report is generated by AgriVision AI and should be used as a guide. "
            "Please consult with agricultural experts for final treatment decisions.</i>"
        )
        story.append(Paragraph(footer_text, self.styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def _as_bullets(items: List[str]) -> str:
        """Format a list of strings as PDF-safe bullet lines."""
        return "<br/>".join(f"- {item}" for item in items if str(item).strip())


pdf_generator = PDFReportGenerator()
