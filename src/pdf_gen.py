"""
PDF REPORT GENERATION MODULE
Creates professional medical diagnosis reports
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
import cv2
import numpy as np
from PIL import Image as PILImage


def generate_report(prediction, confidence, original_image, heatmap_image, 
                   patient_id="P-10001", output_filename="diagnosis_report.pdf"):
    """
    Generate a professional PDF medical report.
    
    Parameters:
    -----------
    prediction : int
        0 = NORMAL, 1 = PNEUMONIA
    confidence : float
        Confidence score (0-1)
    original_image : np.array or PIL.Image
        Original chest X-ray image
    heatmap_image : np.array
        Grad-CAM heatmap
    patient_id : str
        Patient identifier
    output_filename : str
        Output PDF filename
    
    Returns:
    --------
    pdf_bytes : bytes
        PDF file as bytes (for streaming/download)
    """
    
    # Create PDF document
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Get styles
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5090'),
        spaceAfter=6,
        spaceBefore=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=4
    )
    
    # ===== TITLE SECTION =====
    story.append(Paragraph("🫁 MEDICAL DIAGNOSIS REPORT", title_style))
    story.append(Paragraph("Pneumonia Detection System (AI-Assisted)", styles['Normal']))
    story.append(Spacer(1, 0.15*inch))
    
    # ===== REPORT METADATA =====
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = datetime.now().strftime("RPT-%Y%m%d-%H%M%S")
    
    metadata_data = [
        ['Report ID:', report_id],
        ['Date & Time:', timestamp],
        ['Patient ID:', patient_id],
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 3.5*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== DIAGNOSIS SECTION =====
    story.append(Paragraph("DIAGNOSIS RESULT", heading_style))
    
    pred_text = "🔴 PNEUMONIA DETECTED" if prediction == 1 else "🟢 NORMAL"
    pred_color = colors.HexColor('#d32f2f') if prediction == 1 else colors.HexColor('#388e3c')
    
    diagnosis_data = [
        ['Prediction:', Paragraph(f"<b><font color='{pred_color.hexval()}'>{pred_text}</font></b>", styles['Normal'])],
        ['Confidence:', f"{confidence*100:.2f}%"],
        ['Interpretation:', 
         "Pneumonia detected" if prediction == 1 
         else "No pneumonia detected"],
    ]
    
    diag_table = Table(diagnosis_data, colWidths=[2*inch, 3.5*inch])
    diag_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f7')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(diag_table)
    story.append(Spacer(1, 0.2*inch))
    
    # ===== CONFIDENCE INTERPRETATION =====
    story.append(Paragraph("CONFIDENCE INTERPRETATION", heading_style))
    
    conf_percent = confidence * 100
    if conf_percent >= 90:
        confidence_interpretation = "High confidence - Strong prediction reliability"
    elif conf_percent >= 75:
        confidence_interpretation = "Good confidence - Reliable prediction"
    elif conf_percent >= 60:
        confidence_interpretation = "Moderate confidence - Prediction should be verified"
    else:
        confidence_interpretation = "Low confidence - Medical review recommended"
    
    story.append(Paragraph(f"<b>Confidence Level: {conf_percent:.1f}%</b>", normal_style))
    story.append(Paragraph(confidence_interpretation, normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # ===== MEDICAL IMAGES SECTION =====
    story.append(Paragraph("CHEST X-RAY ANALYSIS", heading_style))
    
    # Save temporary images
    temp_original_path = "/tmp/temp_original.jpg"
    temp_heatmap_path = "/tmp/temp_heatmap.jpg"
    
    try:
        # Save original image
        if isinstance(original_image, PILImage.Image):
            original_image.save(temp_original_path, "JPEG", quality=95)
        else:
            # Convert numpy array to image
            if original_image.max() <= 1.0:
                original_image = (original_image * 255).astype(np.uint8)
            original_pil = PILImage.fromarray(original_image.squeeze(), mode='L')
            original_pil.save(temp_original_path, "JPEG", quality=95)
        
        # Save heatmap
        if heatmap_image.max() <= 1.0:
            heatmap_image = (heatmap_image * 255).astype(np.uint8)
        heatmap_pil = PILImage.fromarray(heatmap_image.squeeze(), mode='L')
        heatmap_pil.save(temp_heatmap_path, "JPEG", quality=95)
        
        # Add images to PDF
        img_width = 2.5 * inch
        img_height = 2.5 * inch
        
        image_data = [
            [RLImage(temp_original_path, width=img_width, height=img_height),
             RLImage(temp_heatmap_path, width=img_width, height=img_height)],
            ['Original Chest X-ray', 'Grad-CAM Heatmap\n(Red = Pneumonia areas)']
        ]
        
        image_table = Table(image_data, colWidths=[3*inch, 3*inch])
        image_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, 1), 10),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ]))
        
        story.append(image_table)
        
    except Exception as e:
        story.append(Paragraph(f"<b>Error loading images: {str(e)}</b>", normal_style))
    
    story.append(Spacer(1, 0.2*inch))
    
    # ===== INTERPRETATION GUIDE =====
    story.append(Paragraph("INTERPRETATION GUIDE", heading_style))
    
    interpretation_text = """
    <b>What is Grad-CAM?</b><br/>
    The red/yellow areas in the Grad-CAM heatmap show which regions of the chest X-ray 
    influenced the AI's prediction. These areas may contain features associated with pneumonia.<br/>
    <br/>
    <b>Understanding the Results:</b><br/>
    • <b>Confidence > 90%:</b> High certainty in prediction<br/>
    • <b>Confidence 70-90%:</b> Good certainty in prediction<br/>
    • <b>Confidence < 70%:</b> Lower certainty, recommend medical review<br/>
    """
    
    story.append(Paragraph(interpretation_text, normal_style))
    story.append(Spacer(1, 0.15*inch))
    
    # ===== MEDICAL DISCLAIMER =====
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#c62828'),
        alignment=0,
        spaceAfter=4
    )
    
    disclaimer_text = """
    <b>⚠️ MEDICAL DISCLAIMER</b><br/>
    This report is generated by an AI-assisted pneumonia detection system for clinical support only. 
    <b>This system is NOT a substitute for professional medical judgment.</b> 
    Final diagnosis must be confirmed by a qualified radiologist or medical professional. 
    This system should never replace professional medical review and should be used only as a 
    second opinion tool. Always consult with a licensed healthcare provider for medical decisions.
    """
    
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF bytes
    pdf_buffer.seek(0)
    pdf_bytes = pdf_buffer.getvalue()
    
    print(f"✓ PDF report generated successfully!")
    
    return pdf_bytes


def save_report_to_file(pdf_bytes, filename="diagnosis_report.pdf"):
    """
    Save PDF bytes to a file.
    
    Parameters:
    -----------
    pdf_bytes : bytes
        PDF content as bytes
    filename : str
        Output filename
    """
    with open(filename, 'wb') as f:
        f.write(pdf_bytes)
    print(f"✓ Report saved to {filename}")
    pdf.ln(10)
    
    # Diagnosis Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Doctor's Notes:", ln=True)
    pdf.set_font("Arial", size=10)
    if prediction == "PNEUMONIA":
        message = "The AI model detected patterns consistent with Pneumonia. Clinical correlation is recommended."
    else:
        message = "The lungs appear normal based on the AI analysis. No signs of infection found."
    pdf.multi_cell(0, 10, message)
    pdf.ln(10)
    
    # Images (Save heatmap temporarily or use raw)
    # For simplicity in this demo, we assume image path is passed
    # pdf.image(heatmap_image, x=10, w=100)
    
    pdf.output(output_path)
    return output_path
