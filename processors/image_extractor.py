import io
from importlib import import_module


try:
    pdfium = import_module("pypdfium2")
except ImportError:
    pdfium = None
    
def generate_pdf_thumbnail_bytes(file_bytes: bytes, filename: str) -> bytes:
    
    if pdfium is None:
        return None
    if not filename.lower().endswith(".pdf"):
        return None
    
    try:
        file = pdfium.PdfDocument(file_bytes)
        page = file[0]
        pil_image = page.render(scale=1).to_pil()
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format="PNG")
        return img_byte_arr.getvalue()

    except Exception as e:
        print(f"Aviso: Não foi possível gerar miniatura para {filename}: {e}")
        return None