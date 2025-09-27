# watermark/watermark.py
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black
from reportlab.lib.units import inch

def _create_text_watermark_stream(page_width, page_height, text_lines, opacity=0.12, font_size=12):
    """
    Create a PDF in memory with the watermark text placed diagonally.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(page_width, page_height))
    c.setFillColor(Color(0, 0, 0, alpha=opacity))
    c.setFont("Helvetica", font_size)

    # Draw repeated lines across the page (diagonal-ish)
    x_start = -page_width * 0.2
    y_step = page_height * 0.18
    for i, y in enumerate([page_height - j * y_step for j in range(10)]):
        # Compose text: combine all lines in one string for this pass
        text = " • ".join(text_lines)
        c.saveState()
        c.translate(x_start + i * (page_width * 0.08), y)
        c.rotate(25)
        c.drawString(0, 0, text)
        c.restoreState()

    c.showPage()
    c.save()
    packet.seek(0)
    return packet

def add_watermark(input_pdf_path: str, output_pdf_path: str, buyer_name: str, license_type: str, extra_id: str = ""):
    """
    Adds a light, repeated watermark containing buyer_name and license_type to each page of the PDF.
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Prepare watermark text lines
    lines = [f"{buyer_name}", f"{license_type}"]
    if extra_id:
        lines.append(f"ID:{extra_id}")

    # Use first page size to generate watermark; for safety, produce a watermark per page size when sizes vary
    for page in reader.pages:
        media_box = page.mediabox
        page_width = float(media_box.width)
        page_height = float(media_box.height)

        # Create watermark stream for this page size
        wm_stream = _create_text_watermark_stream(page_width, page_height, lines, opacity=0.12, font_size=max(10, int(min(page_width, page_height) * 0.03)))
        wm_reader = PdfReader(wm_stream)
        wm_page = wm_reader.pages[0]

        # Merge watermark (wm_page) onto the page
        try:
            page.merge_page(wm_page)
        except Exception:
            # fallback: just add page if merge fails (shouldn't normally happen)
            pass

        writer.add_page(page)

    # Write output file
    with open(output_pdf_path, "wb") as out_f:
        writer.write(out_f)
