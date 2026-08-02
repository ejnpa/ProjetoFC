import io
import re 
import pypdfium2 as pdfium
from storage import upload_files_to_storage
import os
import json


def generate_file_thumbnail(file_bytes: bytes, safe_filename:str) -> str:
    
    if not safe_filename.lower().endswith(".pdf"):
        return None
    
    try:
        file = pdfium.PdfDocument(file_bytes)
        page = file[0]
        pil_image  = page.render(scale=1).to_pil()
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format="PNG")
        thumb_bytes = img_byte_arr.getvalue()
        
        thumb_filename = f"thumb_{safe_filename}.png"
        thumbnail_url = upload_files_to_storage(thumb_bytes,thumb_filename)
        
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

        