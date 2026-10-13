import json
import os



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