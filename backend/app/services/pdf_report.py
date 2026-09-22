from reportlab.lib.pagesizes import letter
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
from PIL import Image as PILImage, ImageOps


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0B2B1E'),
            spaceAfter=15,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1B4332'),
            spaceAfter=8,
            spaceBefore=12
        ))

        self.styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=self.styles['Heading3'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#2D6A4F'),
            spaceAfter=4,
            spaceBefore=6
        ))

        self.styles.add(ParagraphStyle(
            name='EvidenceCard',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#1F2937')
        ))

        self.styles.add(ParagraphStyle(
            name='MetaText',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=14,
            textColor=colors.HexColor('#374151')
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
                raw_img = PILImage.open(img_path)
                pil_img = ImageOps.exif_transpose(raw_img).convert("RGB")
            elif path_str.startswith("http://") or path_str.startswith("https://"):
                resp = httpx.get(path_str, timeout=5.0)
                resp.raise_for_status()
                raw_img = PILImage.open(BytesIO(resp.content))
                pil_img = ImageOps.exif_transpose(raw_img).convert("RGB")
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

    @staticmethod
    def _as_bullets(items: List[str]) -> str:
        """Format a list of strings as PDF-safe bullet lines."""
        return "<br/>".join(f"• {item}" for item in items if str(item).strip())

    def _render_evidence_cards(self, evidence_list: List[Dict], story: List, is_healthy: bool = False):
        """Render Evidence-Backed Treatment & Management section cards in PDF story."""
        rec_header = Paragraph("Evidence-Backed Treatment & Management", self.styles['SectionHeader'])
        story.append(rec_header)

        subtext = Paragraph(
            "<i>Authoritative pesticide, IPM, and crop management references from Government agencies, ICAR, and Agricultural Universities.</i>",
            self.styles['MetaText']
        )
        story.append(subtext)
        story.append(Spacer(1, 0.08*inch))

        if is_healthy:
            healthy_text = """
            <b>No Chemical Treatment Required</b><br/>
            The analyzed plant exhibits healthy foliage with no active symptoms of disease. 
            Continue standard crop maintenance, balanced nutrition, and regular field scouting.
            """
            healthy_card = Table([[Paragraph(healthy_text, self.styles['EvidenceCard'])]], colWidths=[6.5*inch])
            healthy_card.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF7ED')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2E7D32')),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(healthy_card)
            story.append(Spacer(1, 0.15*inch))
            return

        if not evidence_list:
            no_data = Paragraph(
                "<i>No specific registered chemical recommendation on file for this condition. Follow general organic and preventive practices.</i>",
                self.styles['MetaText']
            )
            story.append(no_data)
            story.append(Spacer(1, 0.15*inch))
            return

        for idx, rec in enumerate(evidence_list, 1):
            source = rec.get('source') or {}
            rec_type = rec.get('type') or rec.get('recommendation_type') or 'Disease Management'
            active_ing = rec.get('active_ingredient') or 'IPM Reference'
            formulation = f" ({rec.get('formulation')})" if rec.get('formulation') else ""
            
            dose_val = rec.get('dose') or ''
            dose_unit = rec.get('dose_unit') or ''
            dose = f"{dose_val} {dose_unit}".strip() if (dose_val or dose_unit) else 'As specified on label'
            
            water = rec.get('water_volume') or 'As recommended'
            app_method = rec.get('application_method') or 'Foliar application'
            crop_stage = rec.get('crop_stage') or 'Vegetative / Fruiting'
            frequency = rec.get('frequency') or 'As specified by advisory'
            phi = rec.get('pre_harvest_interval') or 'N/A'
            rei = rec.get('re_entry_period') or 'N/A'

            org = source.get('organization') or rec.get('source_organization') or 'Agricultural Authority'
            src_type = source.get('source_type') or rec.get('source_type') or 'Government / Research Advisory'
            doc = source.get('document') or rec.get('source_document') or ''
            note = source.get('evidence_note') or rec.get('evidence_note') or ''

            card_lines = [
                f"<b>{idx}. [{rec_type.upper()}] {active_ing}{formulation}</b>",
                f"<b>Dosage:</b> {dose} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Water Volume:</b> {water}",
                f"<b>Application Method:</b> {app_method} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Crop Stage:</b> {crop_stage}",
                f"<b>Frequency:</b> {frequency}",
                f"<b>Pre-Harvest Interval (PHI):</b> {phi} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Re-Entry Period (REI):</b> {rei}",
                f"<font color=\"#1B4332\"><b>Authority Source:</b> {org} ({src_type})</font>",
            ]
            if doc:
                card_lines.append(f"<b>Document:</b> {doc}")
            if note:
                card_lines.append(f"<i>Evidence Note: &ldquo;{note}&rdquo;</i>")

            card_text = "<br/>".join(card_lines)
            card_p = Paragraph(card_text, self.styles['EvidenceCard'])
            card_table = Table([[card_p]], colWidths=[6.5*inch])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F8F5')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2D6A4F')),
                ('TOPPADDING', (0,0), (-1,-1), 7),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LEFTPADDING', (0,0), (-1,-1), 9),
                ('RIGHTPADDING', (0,0), (-1,-1), 9),
            ]))
            story.append(card_table)
            story.append(Spacer(1, 0.08*inch))

        story.append(Spacer(1, 0.1*inch))
    
    def generate_report(
        self, 
        prediction_data: Dict,
        user_data: Dict,
        disease_data: Dict,
        recommendations: Optional[List[Dict]] = None,
        evidence_recommendations: Optional[List[Dict]] = None,
        disease_details: Optional[Dict] = None,
    ) -> BytesIO:
        """
        Generate a PDF report for a single prediction with Evidence-Backed Treatment & Management
        """
        from app.services.recommendation import recommendation_engine
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        # Title
        title = Paragraph("AgriVision AI - Plant Health & Advisory Report", self.styles['CustomTitle'])
        story.append(title)
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y %I:%M %p")
        metadata_text = f"""
        <b>Report Date:</b> {report_date} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Farmer:</b> {user_data.get('name', 'N/A')}<br/>
        <b>Farm / Location:</b> {user_data.get('farm_name', 'N/A')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Email:</b> {user_data.get('email', 'N/A')}
        """
        metadata = Paragraph(metadata_text, self.styles['MetaText'])
        story.append(metadata)
        story.append(Spacer(1, 0.15*inch))
        
        # Analysis results section
        analysis_header = Paragraph("Diagnostic Analysis Results", self.styles['SectionHeader'])
        story.append(analysis_header)
        
        # Disease detection info
        disease_name = disease_data.get('name', 'Unknown')
        is_healthy = disease_name.lower() in ["healthy", "tomato healthy"]
        
        confidence = prediction_data.get('confidence_score', 0.0)
        confidence_percent = f"{confidence * 100:.1f}%" if confidence <= 1.0 else f"{confidence:.1f}%"
        
        status_color = "#2E7D32" if is_healthy else "#C62828"
        
        raw_url = str(prediction_data.get('image_url') or "")
        img_name = prediction_data.get('filename') or (raw_url.split('/')[-1] if '/' in raw_url else "Uploaded Image")
        
        life_stage_info = f"<br/><b>Life Stage:</b> {prediction_data.get('life_stage')}" if prediction_data.get('life_stage') else ""
        if prediction_data.get('crop_age_days'):
            life_stage_info += f" ({prediction_data.get('crop_age_days')} days)"

        detection_text = f"""
        <b>Image Name:</b> {img_name}<br/><br/>
        <b>Detected Condition:</b> <font color="{status_color}"><b>{disease_name}</b></font><br/><br/>
        <b>Diagnostic Confidence:</b> {confidence_percent}<br/><br/>
        <b>Analysis Timestamp:</b> {prediction_data.get('created_at', report_date)}{life_stage_info}
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
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(results_table)
        else:
            story.append(detection_para)

        story.append(Spacer(1, 0.15*inch))
        
        # Detailed Disease Profile from knowledge repository
        details = disease_details or recommendation_engine.get_disease_knowledge(disease_name) or {}
        
        if not is_healthy and (disease_data or details):
            disease_info_header = Paragraph("Disease Profile & Symptoms", self.styles['SectionHeader'])
            story.append(disease_info_header)
            
            sci_name = details.get('scientific_name') or disease_data.get('scientific_name')
            severity = details.get('severity') or disease_data.get('severity_level') or 'Moderate'
            desc = details.get('description') or disease_data.get('description') or 'N/A'
            
            profile_lines = []
            if sci_name:
                profile_lines.append(f"<b>Scientific Name:</b> <i>{sci_name}</i> &nbsp;|&nbsp; <b>Severity:</b> {severity}")
            else:
                profile_lines.append(f"<b>Severity:</b> {severity}")
            profile_lines.append(f"<b>Description:</b> {desc}")
            
            story.append(Paragraph("<br/>".join(profile_lines), self.styles['Normal']))
            story.append(Spacer(1, 0.08*inch))

            symptoms = details.get('symptoms') or (
                [disease_data['symptoms']] if disease_data.get('symptoms') and isinstance(disease_data['symptoms'], str) else []
            )
            if symptoms:
                story.append(Paragraph("<b>Key Symptoms:</b><br/>" + self._as_bullets(symptoms), self.styles['Normal']))
                story.append(Spacer(1, 0.08*inch))

            causes = details.get('causes') or (
                [disease_data['causes']] if disease_data.get('causes') and isinstance(disease_data['causes'], str) else []
            )
            if causes:
                story.append(Paragraph("<b>Primary Causes & Transmission:</b><br/>" + self._as_bullets(causes), self.styles['Normal']))
                story.append(Spacer(1, 0.12*inch))

            # Integrated Pest Management (IPM) & Cultural Controls
            organic = details.get('organic_control') or []
            preventive = details.get('preventive_measures') or []
            recovery = details.get('recovery_tips') or []

            if organic or preventive or recovery:
                ipm_header = Paragraph("Integrated Pest Management (IPM) & Cultural Control", self.styles['SectionHeader'])
                story.append(ipm_header)

                if organic:
                    story.append(Paragraph("<b>Organic & Biological Control:</b><br/>" + self._as_bullets(organic), self.styles['Normal']))
                    story.append(Spacer(1, 0.08*inch))

                if preventive:
                    story.append(Paragraph("<b>Preventive Measures & Cultural Practices:</b><br/>" + self._as_bullets(preventive), self.styles['Normal']))
                    story.append(Spacer(1, 0.08*inch))

                if recovery:
                    story.append(Paragraph("<b>Crop Recovery & Field Management Tips:</b><br/>" + self._as_bullets(recovery), self.styles['Normal']))
                    story.append(Spacer(1, 0.12*inch))

        # Evidence-Backed Treatment Section
        ev_list = evidence_recommendations if evidence_recommendations is not None else []
        self._render_evidence_cards(ev_list, story, is_healthy=is_healthy)
        
        # Footer & Disclaimer
        footer_text = """
        <i><b>Disclaimer:</b> This report is generated by AgriVision AI for advisory and educational purposes. 
        Recommendations are evidence-backed references from official agricultural authorities (ICAR, PPQS, State Agricultural Universities). 
        Always follow current registered product labels, local agricultural guidance, and safety regulations before application.</i>
        """
        story.append(Paragraph(footer_text, self.styles['MetaText']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_batch_report(
        self,
        user_data: Dict,
        batch_data: Dict,
        evidence_by_disease: Optional[Dict[str, List[Dict]]] = None,
    ) -> BytesIO:
        """
        Generate a batch PDF report listing every detected condition across the batch,
        including crop image previews, symptoms, organic control, and evidence-backed treatments.
        """
        from app.services.recommendation import recommendation_engine

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        # Title
        title = Paragraph("AgriVision AI - Batch Crop Health & Advisory Report", self.styles['CustomTitle'])
        story.append(title)

        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y %I:%M %p")
        metadata_text = (
            f"<b>Report Date:</b> {report_date} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Farmer:</b> {user_data.get('name', 'N/A')}<br/>"
            f"<b>Farm / Location:</b> {user_data.get('farm_name', 'N/A')} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Email:</b> {user_data.get('email', 'N/A')}"
        )
        story.append(Paragraph(metadata_text, self.styles['MetaText']))
        story.append(Spacer(1, 0.15*inch))

        # Batch summary metrics
        batch_header = Paragraph("Batch Scan Summary", self.styles['SectionHeader'])
        story.append(batch_header)
        summary_text = (
            f"<b>Total Uploaded:</b> {batch_data.get('total_uploaded', 0)} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Processed:</b> {batch_data.get('processed', 0)} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Ignored:</b> {batch_data.get('ignored', 0)}<br/>"
            f"<b>Healthy Plants:</b> {batch_data.get('healthy', 0)} &nbsp;&nbsp;|&nbsp;&nbsp; "
            f"<b>Infected Plants:</b> {batch_data.get('infected', 0)}"
        )
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.15*inch))

        # Visual Analyzed Crop Images Section
        valid_predictions = batch_data.get('valid_predictions') or []
        if valid_predictions:
            imgs_header = Paragraph("Analyzed Crop Images & Diagnoses", self.styles['SectionHeader'])
            story.append(imgs_header)
            story.append(Spacer(1, 0.08*inch))

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
                
                is_h = disease_name.lower() in ["healthy", "tomato healthy"]
                status_color = "#2E7D32" if is_h else "#C62828"

                text_info = f"""
                <b>Image Name:</b> {filename}<br/><br/>
                <b>Detected Condition:</b> <font color="{status_color}"><b>{disease_name}</b></font><br/><br/>
                <b>Confidence:</b> {confidence_percent}<br/>
                """
                info_para = Paragraph(text_info, self.styles['Normal'])

                img_elem = self._load_image_element(img_url, max_w=2.2*inch, max_h=1.8*inch)

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
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ('RIGHTPADDING', (0,0), (-1,-1), 8),
                ]))
                story.append(item_table)
                story.append(Spacer(1, 0.1*inch))

            story.append(Spacer(1, 0.15*inch))

        # Disease breakdown & Evidence-Backed Treatments
        disease_summary = batch_data.get('disease_summary') or {}
        evidence_dict = evidence_by_disease or {}

        if not disease_summary:
            no_data = Paragraph(
                "<b>No disease detected across this batch.</b>",
                self.styles['Normal']
            )
            story.append(no_data)
            story.append(Spacer(1, 0.2*inch))
        else:
            for disease_name, files in disease_summary.items():
                is_h = disease_name.lower() in ["healthy", "tomato healthy"]
                disease_header = Paragraph(f"Condition: {disease_name}", self.styles['SectionHeader'])
                story.append(disease_header)

                files_text = ", ".join(files) if files else "-"
                story.append(
                    Paragraph(f"<b>Affected images ({len(files)}):</b> {files_text}", self.styles['MetaText'])
                )
                story.append(Spacer(1, 0.08*inch))

                knowledge = recommendation_engine.get_disease_knowledge(disease_name)
                if knowledge and not is_h:
                    # General info
                    info_text = f"<b>Severity:</b> {knowledge.get('severity', 'Moderate')}<br/>"
                    if knowledge.get('scientific_name'):
                        info_text += f"<b>Scientific Name:</b> <i>{knowledge.get('scientific_name')}</i><br/>"
                    if knowledge.get('description'):
                        info_text += f"<b>Description:</b> {knowledge.get('description')}<br/>"
                    story.append(Paragraph(info_text, self.styles['Normal']))
                    story.append(Spacer(1, 0.08*inch))

                    # Symptoms & Causes
                    symptoms = knowledge.get('symptoms') or []
                    if symptoms:
                        story.append(Paragraph("<b>Symptoms:</b><br/>" + self._as_bullets(symptoms), self.styles['Normal']))
                        story.append(Spacer(1, 0.08*inch))

                    causes = knowledge.get('causes') or []
                    if causes:
                        story.append(Paragraph("<b>Causes:</b><br/>" + self._as_bullets(causes), self.styles['Normal']))
                        story.append(Spacer(1, 0.08*inch))

                    # Organic & Preventive
                    organic = knowledge.get('organic_control') or []
                    if organic:
                        story.append(Paragraph("<b>Organic Control:</b><br/>" + self._as_bullets(organic), self.styles['Normal']))
                        story.append(Spacer(1, 0.08*inch))

                    preventive = knowledge.get('preventive_measures') or []
                    if preventive:
                        story.append(Paragraph("<b>Preventive Measures:</b><br/>" + self._as_bullets(preventive), self.styles['Normal']))
                        story.append(Spacer(1, 0.08*inch))

                # Render Evidence Recommendations for this disease
                disease_evidence = evidence_dict.get(disease_name, [])
                self._render_evidence_cards(disease_evidence, story, is_healthy=is_h)

        # Ignored images if any
        ignored_images = batch_data.get('ignored_images') or []
        if ignored_images:
            ignored_header = Paragraph("Ignored Images", self.styles['SectionHeader'])
            story.append(ignored_header)
            for item in ignored_images:
                story.append(
                    Paragraph(
                        f"• <b>{item.get('filename', 'image')}</b>: {item.get('reason', 'Invalid image')}",
                        self.styles['Normal']
                    )
                )
            story.append(Spacer(1, 0.15*inch))

        # Footer & Disclaimer
        footer_text = (
            "<i><b>Disclaimer:</b> This report is generated by AgriVision AI for advisory and educational purposes. "
            "Recommendations are evidence-backed references from official agricultural authorities (ICAR, PPQS, State Agricultural Universities). "
            "Always follow current registered product labels, local agricultural guidance, and safety regulations before application.</i>"
        )
        story.append(Paragraph(footer_text, self.styles['MetaText']))

        doc.build(story)
        buffer.seek(0)
        return buffer


pdf_generator = PDFReportGenerator()
