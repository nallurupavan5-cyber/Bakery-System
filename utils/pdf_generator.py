import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from models.settings import SystemSetting


def generate_invoice_pdf(order):
    """Generates a downloadable PDF buffer for an Order and its Bill."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    bakery_name = SystemSetting.get_value('bakery_name', 'Sweet Delights Artisan Bakery')
    bakery_phone = SystemSetting.get_value('bakery_phone', '+1 (555) 234-5678')
    bakery_email = SystemSetting.get_value('bakery_email', 'contact@sweetdelightsbakery.com')
    bakery_address = SystemSetting.get_value('bakery_address', '124 Sugarloaf Lane, Flour District')
    currency = SystemSetting.get_value('currency_symbol', '$')

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'BakeryTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#3E2723'),
        spaceAfter=4
    )
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#5D4037'),
        leading=12
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#8D6E63'),
        spaceAfter=6
    )
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#2C1810')
    )

    elements = []

    # Header section
    inv_num = order.bill.invoice_number if order.bill else f"ORD-{order.order_number}"
    date_str = order.order_date.strftime('%B %d, %Y - %I:%M %p')

    header_data = [
        [
            Paragraph(f"<b>{bakery_name}</b><br/>{bakery_address}<br/>Phone: {bakery_phone}<br/>Email: {bakery_email}", meta_style),
            Paragraph(f"<b>INVOICE</b><br/><b>Invoice #:</b> {inv_num}<br/><b>Order #:</b> {order.order_number}<br/><b>Date:</b> {date_str}", meta_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#D97706'), spaceAfter=15))

    # Customer & Payment Info
    cust_name = order.customer.name if order.customer else 'Walk-in Customer'
    cust_phone = order.customer.phone if order.customer else 'N/A'
    cust_email = order.customer.email if order.customer and order.customer.email else 'N/A'
    cust_addr = order.customer.address if order.customer and order.customer.address else 'Counter Pickup'

    info_data = [
        [
            Paragraph(f"<b>Billed To:</b><br/>{cust_name}<br/>Phone: {cust_phone}<br/>Address: {cust_addr}", meta_style),
            Paragraph(f"<b>Order Details:</b><br/>Order Type: <b>{order.order_type}</b><br/>Payment Mode: <b>{order.payment_mode}</b><br/>Payment Status: <b>{order.payment_status}</b><br/>Order Status: <b>{order.status}</b>", meta_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[3.5 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # Items Table
    table_rows = [
        [Paragraph('<b>Item Description</b>', bold_style), Paragraph('<b>Qty</b>', bold_style), Paragraph('<b>Unit Price</b>', bold_style), Paragraph('<b>Subtotal</b>', bold_style)]
    ]

    for item in order.items:
        table_rows.append([
            Paragraph(item.item_name, styles['Normal']),
            str(item.quantity),
            f"{currency}{item.price:.2f}",
            f"{currency}{item.subtotal:.2f}"
        ])

    items_table = Table(table_rows, colWidths=[3.8 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FAF3EB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#3E2723')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#D97706')),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    # Summary Table
    summary_data = [
        ['', Paragraph('<b>Subtotal:</b>', meta_style), f"{currency}{order.subtotal:.2f}"],
        ['', Paragraph('<b>Discount:</b>', meta_style), f"-{currency}{order.discount:.2f}"],
        ['', Paragraph('<b>Tax:</b>', meta_style), f"+{currency}{order.tax:.2f}"],
        ['', Paragraph('<b>Grand Total:</b>', bold_style), f"<b>{currency}{order.total_amount:.2f}</b>"],
    ]
    summary_table = Table(summary_data, colWidths=[3.8 * inch, 1.8 * inch, 1.4 * inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (1, 3), (2, 3), 1, colors.HexColor('#3E2723')),
    ]))
    elements.append(summary_table)

    elements.append(Spacer(1, 25))
    if order.special_instructions:
        elements.append(Paragraph(f"<b>Special Instructions:</b> {order.special_instructions}", meta_style))
        elements.append(Spacer(1, 10))

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Italic'],
        fontSize=9,
        textColor=colors.HexColor('#8D6E63'),
        alignment=1  # Centered
    )
    elements.append(Paragraph("Thank you for your business! Freshly baked with love.", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
