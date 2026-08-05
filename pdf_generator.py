from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image
)

import os


styles = getSampleStyleSheet()


# ==========================================
# COMPANY INFORMATION
# ==========================================

COMPANY_NAME = "Your Company Name"

COMPANY_ADDRESS = """
Street 123,
Lahore, Pakistan
"""

COMPANY_PHONE = "+92-300-0000000"

COMPANY_EMAIL = "info@company.com"

LOGO_PATH = "assets/logo.png"

STAMP_PATH = "assets/stamp.jpg"


# ==========================================
# HELPERS
# ==========================================

def company_header(story):
    """
    Draw company logo and information.
    """

    if os.path.exists(LOGO_PATH):

        logo = Image(
            LOGO_PATH,
            width=1.2*inch,
            height=1.2*inch
        )

        story.append(logo)

    story.append(
        Paragraph(
            f"<b>{COMPANY_NAME}</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            COMPANY_ADDRESS,
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            COMPANY_PHONE,
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            COMPANY_EMAIL,
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 20)
    )


def footer(story):

    story.append(
        Spacer(1, 25)
    )

    if os.path.exists(STAMP_PATH):

        stamp = Image(
            STAMP_PATH,
            width=1.4*inch,
            height=1.4*inch
        )

        story.append(stamp)

    story.append(
        Paragraph(
            "<b>Authorized Signature</b>",
            styles["Heading3"]
        )
    )

# ==========================================
# INVOICE PDF
# ==========================================

def generate_invoice_pdf(
    filename,
    invoice_no,
    customer_name,
    invoice_date,
    items,
    notes=""
):
    """
    Generate Professional Invoice PDF.

    items = [
        {
            "product": "...",
            "qty": 2,
            "price": 100,
            "total": 200
        }
    ]
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    story = []

    company_header(story)

    story.append(
        Paragraph(
            "<b><font size=18>INVOICE</font></b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>Invoice #:</b> {invoice_no}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {invoice_date}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Customer:</b> {customer_name}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ==========================
    # Invoice Table
    # ==========================

    table_data = [[
        "Product",
        "Qty",
        "Unit Price",
        "Total"
    ]]

    grand_total = 0

    for item in items:

        grand_total += item["total"]

        table_data.append([
            item["product"],
            item["qty"],
            f"{item['price']:.2f}",
            f"{item['total']:.2f}"
        ])

    table_data.append([
        "",
        "",
        "Grand Total",
        f"{grand_total:.2f}"
    ])

    table = Table(
        table_data,
        colWidths=[
            3.2*inch,
            0.8*inch,
            1.2*inch,
            1.3*inch
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("BACKGROUND",(-2,-1),(-1,-1),colors.lightgrey),

        ("ALIGN",(1,1),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),10)

    ]))

    story.append(table)

    story.append(Spacer(1,20))

    if notes:

        story.append(
            Paragraph(
                f"<b>Notes:</b><br/>{notes}",
                styles["BodyText"]
            )
        )

    footer(story)

    doc.build(story)

    return filename

# ==========================================
# QUOTATION PDF
# ==========================================

def generate_quotation_pdf(
    filename,
    quotation_no,
    customer_name,
    quotation_date,
    items,
    notes=""
):
    """
    Generate Professional Quotation PDF.

    items = [
        {
            "product": "...",
            "qty": 2,
            "price": 100,
            "total": 200
        }
    ]
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    story = []

    company_header(story)

    story.append(
        Paragraph(
            "<b><font size=18>QUOTATION</font></b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>Quotation #:</b> {quotation_no}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Date:</b> {quotation_date}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Customer:</b> {customer_name}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ==========================================
    # QUOTATION TABLE
    # ==========================================

    table_data = [[
        "Product",
        "Qty",
        "Unit Price",
        "Total"
    ]]

    grand_total = 0

    for item in items:

        grand_total += item["total"]

        table_data.append([
            item["product"],
            item["qty"],
            f"{item['price']:.2f}",
            f"{item['total']:.2f}"
        ])

    table_data.append([
        "",
        "",
        "Grand Total",
        f"{grand_total:.2f}"
    ])

    table = Table(
        table_data,
        colWidths=[
            3.2*inch,
            0.8*inch,
            1.2*inch,
            1.3*inch
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkgreen),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),

        ("BACKGROUND",(-2,-1),(-1,-1),colors.beige),

        ("ALIGN",(1,1),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),10)

    ]))

    story.append(table)

    story.append(Spacer(1,20))

    if notes:

        story.append(
            Paragraph(
                f"<b>Notes:</b><br/>{notes}",
                styles["BodyText"]
            )
        )

        story.append(Spacer(1,15))

    story.append(
        Paragraph(
            "<b>Terms & Conditions</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "• This quotation is valid for 30 days.<br/>"
            "• Prices are subject to stock availability.<br/>"
            "• Payment terms are agreed mutually before delivery.",
            styles["BodyText"]
        )
    )

    footer(story)

    doc.build(story)

    return filename

# ==========================================
# DELIVERY CHALLAN PDF
# ==========================================

def generate_delivery_challan_pdf(
    filename,
    challan_no,
    customer_name,
    delivery_date,
    items,
    notes=""
):
    """
    Generate Professional Delivery Challan PDF.

    items = [
        {
            "product": "...",
            "qty": 2
        }
    ]
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    story = []

    company_header(story)

    story.append(
        Paragraph(
            "<b><font size=18>DELIVERY CHALLAN</font></b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            f"<b>Challan No:</b> {challan_no}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Delivery Date:</b> {delivery_date}",
            styles["BodyText"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Customer:</b> {customer_name}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 20))

    # ==========================================
    # DELIVERY TABLE
    # ==========================================

    table_data = [[
        "Sr",
        "Product",
        "Quantity"
    ]]

    for index, item in enumerate(items, start=1):

        table_data.append([
            index,
            item["product"],
            item["qty"]
        ])

    table = Table(
        table_data,
        colWidths=[
            0.8 * inch,
            4.5 * inch,
            1.2 * inch
        ]
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("BOTTOMPADDING", (0,0), (-1,0), 10)

    ]))

    story.append(table)

    story.append(Spacer(1,20))

    if notes:

        story.append(
            Paragraph(
                f"<b>Notes:</b><br/>{notes}",
                styles["BodyText"]
            )
        )

        story.append(Spacer(1,20))

    # ==========================================
    # SIGNATURES
    # ==========================================

    signature_table = Table(
        [[
            "Receiver Signature",
            "Authorized Signature"
        ]],
        colWidths=[
            3.2 * inch,
            3.2 * inch
        ]
    )

    signature_table.setStyle(TableStyle([

        ("LINEABOVE", (0,0), (0,0), 1, colors.black),
        ("LINEABOVE", (1,0), (1,0), 1, colors.black),

        ("TOPPADDING", (0,0), (-1,-1), 25),

        ("ALIGN", (0,0), (-1,-1), "CENTER"),

        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold")

    ]))

    story.append(signature_table)

    story.append(Spacer(1,20))

    if os.path.exists(STAMP_PATH):

        stamp = Image(
            STAMP_PATH,
            width=1.4 * inch,
            height=1.4 * inch
        )

        story.append(stamp)

    doc.build(story)

    return filename

# ==========================================
# PDF UTILITIES
# ==========================================

from datetime import datetime
import os


PDF_FOLDER = "generated_pdfs"


def ensure_pdf_folder():
    """
    Create PDF folder if it does not exist.
    """

    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)


def get_pdf_path(filename):
    """
    Return full PDF path.
    """

    ensure_pdf_folder()

    return os.path.join(
        PDF_FOLDER,
        filename
    )


def generate_invoice_filename():
    """
    Example:
    Invoice_20260805_154520.pdf
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return get_pdf_path(
        f"Invoice_{timestamp}.pdf"
    )


def generate_quotation_filename():
    """
    Example:
    Quotation_20260805_154520.pdf
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return get_pdf_path(
        f"Quotation_{timestamp}.pdf"
    )


def generate_challan_filename():
    """
    Example:
    DeliveryChallan_20260805_154520.pdf
    """

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    return get_pdf_path(
        f"DeliveryChallan_{timestamp}.pdf"
    )


# ==========================================
# SAMPLE DATA
# ==========================================

def sample_items():

    return [

        {
            "product": "Dell Laptop",
            "qty": 2,
            "price": 85000,
            "total": 170000
        },

        {
            "product": "Wireless Mouse",
            "qty": 3,
            "price": 2500,
            "total": 7500
        }

    ]


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    invoice_file = generate_invoice_filename()

    generate_invoice_pdf(
        filename=invoice_file,
        invoice_no="INV-1001",
        customer_name="Demo Customer",
        invoice_date=datetime.today().strftime("%Y-%m-%d"),
        items=sample_items(),
        notes="Thank you for your business."
    )

    print("Invoice Created:")
    print(invoice_file)

