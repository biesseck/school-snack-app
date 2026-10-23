import io
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_qr_image_bytes(data_str: str) -> io.BytesIO:
    """Generates QR code PNG image stream in memory."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer

def build_student_cards_pdf(students: list) -> io.BytesIO:
    """Creates a grid of printable student QR ID passes in a PDF stream."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=11, leading=13, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=11)

    cards = []
    for student in students:
        s_id = str(student.get("Student_ID", ""))
        name = str(student.get("Full_Name", ""))
        grade = str(student.get("Grade", ""))

        qr_bytes = generate_qr_image_bytes(s_id)
        qr_img = Image(qr_bytes, width=70, height=70)

        info_text = Paragraph(f"<b>{name}</b><br/>ID: {s_id}<br/>Class: {grade}", body_style)

        card_data = [
            [Paragraph("<b>SCHOOL SNACK PASS</b>", title_style), ""],
            [qr_img, info_text]
        ]

        card_table = Table(card_data, colWidths=[80, 140])
        card_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor("#E2E8F0")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        cards.append(card_table)

    # Grid layout: 2 cards per row
    grid_data = []
    for i in range(0, len(cards), 2):
        row = [cards[i]]
        if i + 1 < len(cards):
            row.append(cards[i + 1])
        else:
            row.append("")
        grid_data.append(row)

    grid_table = Table(grid_data, colWidths=[270, 270])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))

    doc.build([grid_table])
    pdf_buffer.seek(0)
    return pdf_buffer