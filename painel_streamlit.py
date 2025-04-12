from pymongo import MongoClient
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

# Configuração do layout
st.set_page_config(page_title="Painel Copiloto IA", layout="wide")
st.title("📊 Painel do Copiloto IA")

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.copilotoAI
colecao = db["historico"]

# Carrega os dados
query = {}
mensagens = list(colecao.find(query).sort("timestamp", -1))
df = pd.DataFrame(mensagens)

# Conversões iniciais
if "_id" in df.columns:
    df["_id"] = df["_id"].astype(str)

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["data_formatada"] = df["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
else:
    st.warning("⚠️ Nenhuma mensagem com campo 'timestamp' encontrada.")

# 🎯 Filtros laterais
st.sidebar.header("📌 Filtros")

# Filtro por número
usuarios = df["wa_id"].unique()
numero = st.sidebar.selectbox("Filtrar por número:", ["Todos"] + list(usuarios))
if numero != "Todos":
    df = df[df["wa_id"] == numero]

# Filtro por origem
origens = df["origem"].dropna().unique()
origem = st.sidebar.selectbox("Filtrar por origem:", ["Todos"] + list(origens))
if origem != "Todos":
    df = df[df["origem"] == origem]

# Filtro por palavra-chave
palavra = st.sidebar.text_input("🔍 Buscar por palavra-chave:")
if palavra:
    df = df[df["mensagem"].str.contains(palavra, case=False, na=False)]

# Exibição da tabela
st.subheader("📬 Mensagens registradas:")
colunas = ["data_formatada", "wa_id", "tipo", "conteudo", "origem", "mensagem"]
colunas = [c for c in colunas if c in df.columns]
st.dataframe(df[colunas], use_container_width=True)

# 📈 Gráficos
st.markdown("---")
st.subheader("📊 Insights Rápidos")

col1, col2 = st.columns(2)

# Gráfico de barras: mensagens por hora
with col1:
    if "timestamp" in df.columns:
        df["hora"] = df["timestamp"].dt.hour
        fig, ax = plt.subplots()
        df["hora"].value_counts().sort_index().plot(kind="bar", ax=ax)
        ax.set_title("🕒 Mensagens por Hora")
        ax.set_xlabel("Hora do Dia")
        ax.set_ylabel("Quantidade")
        st.pyplot(fig)

# WordCloud: Nuvem de palavras das mensagens
with col2:
    todas_mensagens = " ".join(df["mensagem"].dropna().astype(str).tolist())
    if todas_mensagens:
        wordcloud = WordCloud(width=800, height=300, background_color="white").generate(todas_mensagens)
        fig_wc, ax_wc = plt.subplots()
        ax_wc.imshow(wordcloud, interpolation="bilinear")
        ax_wc.axis("off")
        st.pyplot(fig_wc)

# Rodapé
st.markdown("---")
st.caption("Copiloto IA © 2025 • Visualização e análise de histórico de interações.")
