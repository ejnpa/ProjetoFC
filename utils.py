import io
import os
import json
from importlib import import_module
from storage import get_storage_provider

try:
    pdfium = import_module("pypdfium2")
except ImportError:
    pdfium = None


def generate_file_thumbnail(file_bytes: bytes, safe_filename: str) -> str:
    
    if pdfium is None:
        raise ImportError("pypdfium2 is required for PDF processing")

    if not safe_filename.lower().endswith(".pdf"):
        return None
    
    try:
        file = pdfium.PdfDocument(file_bytes)
        page = file[0]
        pil_image = page.render(scale=1).to_pil()
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format="PNG")
        thumb_bytes = img_byte_arr.getvalue()
        
        thumb_filename = f"thumb_{safe_filename}.png"
        storage = get_storage_provider()
        thumbnail_url = storage.upload_files_to_storage(thumb_bytes, thumb_filename)
        
        return thumbnail_url
    except Exception as e:
        print(f"Aviso: Não foi possível gerar miniatura para {safe_filename}: {e}")
        return None
        
def load_structure():
    """Lê o JSON com a estrutura de escolas, cursos, anos e disciplinas 
    para popular os dropdowns."""
    
    filepath = os.path.join(os.path.dirname(__file__), "dados_ipcb.json")
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"avisos": "Ficheiro de estrutura não encontrado."}
    except Exception as e:
        print(f"Erro ao carregar dados da escola: {e}")
        return {"avisos": f"Erro ao carregar dados da escola: {e}"}

def extract_text_from_file(file_bytes: bytes) -> str:
    try:
        file = pdfium.PdfDocument(file_bytes)
        extracted_text = ""
        for page in file:
            text_page = page.get_textpage()
            extracted_text += text_page.get_text_range() + "\n\n"
        file.close()
        return extracted_text
    except Exception as e:
        return f"Erro ao extrair texto do ficheiro: {e}"    
        