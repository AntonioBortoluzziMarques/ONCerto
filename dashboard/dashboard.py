import streamlit as st
import requests
import pandas as pd

# configuração
API_URL = "https://oncerto.onrender.com/comercios"

# estilização básica (alterar URGENTE)
st.set_page_config(page_title="ONCerto - Buscador de Negócios", page_icon="📊", layout="wide")

st.title("📊 ONCerto - Buscador de Negócios")
st.markdown("Descubra os **comércios locais** e veja se estão atualizados no Google Meu Negócio.")

# input da cidade
cidade = st.text_input("Digite a cidade que deseja buscar:", placeholder="Ex: Chapecó, SC")

if st.button("🔍 Buscar"):
    if not cidade:
        st.warning("Digite uma cidade para continuar!")
    else:
        with st.spinner("Buscando comércios..."):
            try:
                response = requests.get(API_URL, params={"cidade": cidade})
                if response.status_code == 200:
                    data = response.json()
                    df = pd.DataFrame(data["dados"])

                    st.success(f"✅ {data['total']} comércios encontrados em {data['cidade']}")
                    
                    st.dataframe(df, use_container_width=True)

                    # botão pra salvar planilha (backend não está funcionando)
                    excel = df.to_excel(index=False, engine="openpyxl")
                    st.download_button(
                        "📥 Baixar resultados em Excel",
                        data=excel,
                        file_name=f"comercios_{cidade.replace(' ', '_')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error("Erro ao buscar no servidor.")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
