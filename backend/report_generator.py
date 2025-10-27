
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import os
from typing import List, Dict, Any
import time

def create_report_pdf(report_data: Dict[str, List[Dict[str, Any]]], output_filename: str) -> str | None:
    print(f"--- 📄 Starting PDF Generation: {output_filename} ---")
    doc = SimpleDocTemplate(output_filename, pagesize=(8.5*inch, 11*inch),
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    if not report_data or not isinstance(report_data, dict):
        print("❌ Error: Invalid or empty report_data provided for PDF generation.")
        story = [Paragraph("Error: Report Generation Failed", styles['h1']),
                 Paragraph("Invalid or no data received from the generation process. Check agent logs.", styles['Normal'])]
        try:
            doc.build(story)
            print(f"Generated error PDF: {output_filename}")
            return output_filename
        except Exception as e:
            print(f"CRITICAL: Error building the error PDF: {e}")
            return None

    styles.add(ParagraphStyle(name='TitleStyle', parent=styles['h1'], alignment=TA_CENTER, spaceAfter=20, fontSize=18, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='HeadingStyle', parent=styles['h2'], spaceBefore=14, spaceAfter=8, keepWithNext=1, fontSize=14, textColor=colors.darkslategray))
    styles.add(ParagraphStyle(name='BodyStyle', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=10, leading=15, fontSize=11))
    styles.add(ParagraphStyle(name='CaptionStyle', parent=styles['Italic'], alignment=TA_CENTER, fontSize=9, spaceBefore=4, spaceAfter=12, textColor=colors.dimgray))
    styles.add(ParagraphStyle(name='ErrorStyle', parent=styles['Italic'], alignment=TA_LEFT, textColor=colors.red, spaceAfter=8, fontSize=10))
    table_text_style = ParagraphStyle(name='TableTextStyle', parent=styles['Normal'], alignment=TA_LEFT, fontSize=8, leading=10)

    story.append(Paragraph("Generated Medical Report: NAFLD Analysis", styles['TitleStyle']))

    section_keys = list(report_data.keys())
    for i, section_title in enumerate(section_keys):
        content_blocks = report_data.get(section_title, [])
        clean_section_title = section_title.replace('_', ' ').title()
        print(f"📄 Adding PDF Section: '{clean_section_title}'")
        story.append(Paragraph(clean_section_title, styles['HeadingStyle']))

        if not content_blocks or not isinstance(content_blocks, list):
            story.append(Paragraph("[No valid content was provided for this section]", styles['ErrorStyle']))
            if i < len(section_keys) - 1: story.append(Spacer(1, 0.25*inch))
            continue

        for block_num, block in enumerate(content_blocks):
            if not isinstance(block, dict):
                story.append(Paragraph(f"[Invalid content block format encountered: {block}]", styles['ErrorStyle']))
                continue

            block_type = block.get("type", "text")
            print(f"  -> Rendering block {block_num+1}: {block_type}")

            try:
                if block_type == "text":
                    text = str(block.get("content", "[Content missing]")).replace('\n', '<br/>')
                    story.append(Paragraph(text, styles['BodyStyle']))

                elif block_type == "image":
                    img_path = block.get("path")
                    caption = block.get("caption", os.path.basename(img_path) if img_path else "Image")
                    if img_path and os.path.exists(img_path):
                        try:
                            img = Image(img_path)
                            max_width = 6.5 * inch
                            max_height = 8.0 * inch
                            img_width, img_height = img.drawWidth, img.drawHeight
                            width_ratio = max_width / img_width if img_width > max_width else 1
                            height_ratio = max_height / img_height if img_height > max_height else 1
                            scale_ratio = min(width_ratio, height_ratio)
                            if scale_ratio < 1:
                                img.drawWidth = img_width * scale_ratio
                                img.drawHeight = img_height * scale_ratio
                            img.hAlign = 'CENTER'
                            img_container = KeepTogether([
                                Spacer(1, 0.1*inch), img, Spacer(1, 0.05*inch),
                                Paragraph(f"Figure: {caption}", styles['CaptionStyle'])
                            ])
                            story.append(img_container)
                        except Exception as img_err:
                            print(f"    ⚠️ Error loading/processing image {img_path}: {img_err}")
                            story.append(Paragraph(f"[Error rendering image: {caption} - {img_err}]", styles['ErrorStyle']))
                    else:
                        print(f"    ⚠️ Warning: Image path not found or invalid: {img_path}")
                        story.append(Paragraph(f"[Image not found: {caption}]", styles['ErrorStyle']))

                elif block_type == "table":
                    table_data = block.get("data")
                    caption = block.get("caption", "Table")
                    if isinstance(table_data, list) and len(table_data) > 0 and all(isinstance(r, list) for r in table_data) and len(table_data[0]) > 0:
                        styled_table_data = [[Paragraph(str(cell), table_text_style) for cell in row] for row in table_data]
                        num_cols = len(styled_table_data[0])
                        col_widths = [doc.width/num_cols] * num_cols
                        table = Table(styled_table_data, colWidths=col_widths, hAlign='CENTER', repeatRows=1)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.darkslategray),
                            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                            ('ALIGN', (0,0), (-1,0), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0,0), (-1,0), 10),
                            ('TOPPADDING', (0,0), (-1,0), 6),
                            ('BACKGROUND', (0,1), (-1,-1), colors.lavenderblush),
                            ('TEXTCOLOR',(0,1),(-1,-1),colors.black),
                            ('ALIGN', (0,1), (-1,-1), 'LEFT'),
                            ('TOPPADDING', (0,1), (-1,-1), 4),
                            ('BOTTOMPADDING', (0,1), (-1,-1), 4),
                            ('GRID', (0,0), (-1,-1), 1, colors.darkgrey),
                            ('BOX', (0,0), (-1,-1), 1.5, colors.black),
                            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.grey),
                        ]))
                        table_container = KeepTogether([
                            Spacer(1, 0.1*inch),
                            Paragraph(f"Table: {caption}", styles['CaptionStyle']),
                            table
                        ])
                        story.append(table_container)
                    else:
                        print(f"    ⚠️ Warning: Invalid or empty table data for '{caption}'")
                        story.append(Paragraph(f"[Invalid or empty table data: {caption}]", styles['ErrorStyle']))
                else:
                    print(f"    ⚠️ Warning: Unknown block type '{block_type}' found.")
                    story.append(Paragraph(f"[Unsupported content type: {block_type}]", styles['ErrorStyle']))

                story.append(Spacer(1, 0.1*inch))

            except Exception as block_error:
                print(f"  ❌ Error rendering block ({block_type}) in section '{section_title}': {block_error}")
                story.append(Paragraph(f"[Error rendering content block - Check logs]", styles['ErrorStyle']))

        if i < len(section_keys) - 1:
            story.append(Spacer(1, 0.3*inch))

    try:
        doc.build(story)
        print(f"--- ✅ Successfully generated PDF: {output_filename} ---")
        return output_filename
    except Exception as e:
        print(f"--- ❌ Error building final PDF document: {e} ---")
        try:
            doc_err = SimpleDocTemplate(output_filename)
            story_err = [Paragraph("Fatal Error Building Report PDF", styles['h1']),
                         Paragraph(f"An error occurred during final PDF generation: {e}", styles['Normal']),
                         Paragraph("Please check server logs.", styles['Normal'])]
            doc_err.build(story_err)
            return output_filename
        except:
            print(f"!!! CRITICAL: Failed even to build the error PDF !!!")
            return None
        
