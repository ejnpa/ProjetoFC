import io
import os
from importlib import import_module

try:
    pdfium = import_module("pypdfium2")
except ImportError:
    pdfium = None

try:
    docx = import_module("docx")
except ImportError:
    docx = None
    
    
    
def _extract_pdf(file_bytes: bytes) -> str:
    if not pdfium:
        return ""
    file = pdfium.PdfDocument(file_bytes)
    text = "".join(page.get_textpage().get_text_range() + "\n\n" for page in file)
    file.close()
    return text.strip()    

def _extract_docx(file_bytes: bytes) -> str:
    if not docx:
        return ""
    doc = docx.Document(io.BytesIO(file_bytes))
    return  "\n".join([paragraph.text for paragraph in doc.paragraphs]).strip()


SUPPORTED_EXTRACTORS = {
    ".pdf": _extract_pdf,
    ".docx": _extract_docx
}    



def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    _, extension = os.path.splitext(filename.lower())
    
    extract_function = SUPPORTED_EXTRACTORS.get(extension)
    
    if not extract_function:
        return ""
    
    try:
        return extract_function(file_bytes)
    except Exception as e:
        print(f"Erro ao extrair texto do ficheiro {filename}: {e}")    
        return"" 