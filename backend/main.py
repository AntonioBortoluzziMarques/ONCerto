from fastapi import FastAPI, Query
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

# configuração
load_dotenv()
API_KEY = os.getenv("API_KEY")
CATEGORIAS = ["lojas", "restaurantes", "mercados", "farmácias", "cafés"]

if not API_KEY:
    raise ValueError("API_KEY não encontrada. Configure no arquivo .env")

app = FastAPI()

# funções de funcionamento
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

    instagram = "instagram.com" in site.lower() if site else False

    return {
        "Nome": nome,
        "Endereço": endereco,
        "Site": site if site else "❌",
        "Instagram": "✅" if instagram else "❌",
        "Google Meu Negócio atualizado?": "✅" if status.lower() == "aberto" else "❌"
    }

# rotas
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

    # salvar planilha (atualmente com erro). O erro não interfere no funcionamento
    df = pd.DataFrame(todos_comercios)
    arquivo = f"comercios_{cidade.replace(',', '').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(arquivo, index=False)

    return {
        "cidade": cidade,
        "total": len(todos_comercios),
        "dados": todos_comercios
    }
