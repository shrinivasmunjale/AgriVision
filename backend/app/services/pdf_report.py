from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import Dict, List

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
        
        status_color = "#34A65F" if disease_name == "Healthy" else "#FF6B6B"
        
        detection_text = f"""
        <b>Detected Condition:</b> <font color="{status_color}">{disease_name}</font><br/>
        <b>Confidence Level:</b> {confidence_percent}<br/>
        <b>Analysis Date:</b> {prediction_data.get('created_at', 'N/A')}<br/>
        """
        detection = Paragraph(detection_text, self.styles['Normal'])
        story.append(detection)
        story.append(Spacer(1, 0.2*inch))
        
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
                    Composition: {fert.get('composition', 'N/A')}<br/>
                    Dosage: {fert.get('dosage', 'N/A')}<br/>
                    Application Stage: {fert.get('application_stage', 'N/A')}<br/>
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

pdf_generator = PDFReportGenerator()
