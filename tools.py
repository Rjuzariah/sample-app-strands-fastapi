from strands import tool

from pypdf import PdfReader
from io import BytesIO


@tool
def query_product_database(query: str) -> str:
    """Query the internal product database for inventory and pricing information.

    Args:
        query: Search query for products (e.g., "wireless headphones", "USB-C hub")
    """
    products = {
        "wireless headphones": "SKU-WH100: Wireless Headphones Pro - $79.99, 142 in stock, 4.5★ rating, launched 2025-03",
        "usb-c hub": "SKU-UC200: USB-C Hub 7-in-1 - $45.00, 89 in stock, 4.2★ rating, launched 2024-11",
        "mechanical keyboard": "SKU-MK300: Mechanical Keyboard RGB - $149.99, 23 in stock, 4.8★ rating, launched 2025-01",
        "noise cancelling": "SKU-NC400: Noise Cancelling Earbuds - $129.99, 67 in stock, 4.6★ rating, launched 2025-05",
    }
    key = query.lower()
    matches = [info for product_key, info in products.items() if product_key in key]
    if matches:
        return "\n".join(matches)
    return f"No products found matching '{query}'. Available: wireless headphones, usb-c hub, mechanical keyboard, noise cancelling"


def pdf_reader(pdf_bytes: bytes) -> str:
    """Extract text content from a PDF file.

    Args:
        pdf_bytes: The PDF file content in bytes.
    """


    reader = PdfReader(BytesIO(pdf_bytes))
    text_content = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_content += page_text + "\n"
    return text_content.strip() if text_content else "No text found in the PDF."    