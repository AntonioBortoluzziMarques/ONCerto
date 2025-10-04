from fastapi import FastAPI, Query
import requests
import pandas as pd
from datetime import datetime

# ========= CONFIG =========
API_KEY = "2b03e116913828d03c1d36ae2b48bf510b54721bbfb04ec54ddc5e253a7da779"  # substitua pela sua chave da SerpAPI
CATEGORIAS = ["lojas", "restaurantes", "mercados", "farmácias", "cafés"]

app = FastAPI()

# ========= FUNÇÕES =========
def buscar_comercios(query, local="Chapecó, SC", limite=20):
    """Busca comércios no Google Maps via SerpAPI"""
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps",
        "q": f"{query} em {local}",
        "type": "search",
        "hl": "pt-BR",
        "api_key": API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("local_results", [])[:limite]

def analisar_comercio(comercio):
    """Extrai informações úteis do comércio"""
    nome = comercio.get("title", "")
    endereco = comercio.get("address", "")
    site = comercio.get("website", "")
    status = comercio.get("status", "DESCONHECIDO")

    # Verifica Instagram no site
    instagram = "instagram.com" in site.lower() if site else False

    return {
        "Nome": nome,
        "Endereço": endereco,
        "Site": site if site else "❌",
        "Instagram": "✅" if instagram else "❌",
        "Google Meu Negócio atualizado?": "✅" if status.lower() == "aberto" else "❌"
    }

# ========= ROTAS =========
@app.get("/")
def home():
    return {"mensagem": "API de Comércios Locais - Use /comercios?cidade=Chapecó, SC"}

@app.get("/comercios")
def get_comercios(cidade: str = Query(..., description="Cidade para buscar comércios, ex: Chapecó, SC")):
    todos_comercios = []
    for categoria in CATEGORIAS:
        resultados = buscar_comercios(categoria, cidade, limite=20)
        for comercio in resultados:
            info = analisar_comercio(comercio)
            info["Categoria"] = categoria
            todos_comercios.append(info)

    # Criar DataFrame (para salvar planilha se quiser no futuro)
    df = pd.DataFrame(todos_comercios)
    arquivo = f"comercios_{cidade.replace(',', '').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(arquivo, index=False)

    return {
        "cidade": cidade,
        "total": len(todos_comercios),
        "dados": todos_comercios
    }
