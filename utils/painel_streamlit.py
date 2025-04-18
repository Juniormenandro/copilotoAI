from pymongo import MongoClient
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuração do layout (must be the first Streamlit command)
st.set_page_config(page_title="Painel Copiloto IA", layout="wide")
st.title("📊 Painel do Copiloto IA")

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://jojuniorjo:ieYmunRe9JMcpsuJ@cluster0.xld3pvt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(mongo_uri)
db = client.copilotoAI

# Testar conexão
try:
    client.admin.command('ping')
    st.success("✅ Conectado ao MongoDB!")
except Exception as e:
    st.error(f"❌ Falha na conexão: {e}")
    st.stop()

# Carregar dados de múltiplas coleções
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        # Verificar se o banco copilotoAI tem coleções
        if not db.list_collection_names():
            st.error("❌ Nenhuma coleção encontrada no banco 'copilotoAI'. Verifique o banco de dados.")
            return pd.DataFrame()

        # Carregar histórico
        collection_name = "historico"
        if collection_name not in db.list_collection_names():
            st.warning(f"⚠️ Coleção '{collection_name}' não encontrada. Coleções disponíveis: {db.list_collection_names()}")
            return pd.DataFrame()

        historico = list(db[collection_name].find())
        st.write(f"Número de documentos em {collection_name}:", len(historico))
        if historico:
            st.write(f"Exemplo de documento em {collection_name}:", historico[0])
        
        df_historico = pd.DataFrame(historico)
        if df_historico.empty:
            st.warning(f"⚠️ Coleção '{collection_name}' está vazia")
            return pd.DataFrame()
        if "wa_id" not in df_historico.columns:
            st.error(f"❌ Campo 'wa_id' não encontrado na coleção '{collection_name}'")
            return pd.DataFrame()
        df_historico["wa_id"] = df_historico["wa_id"].astype(str)
        st.write("Valores únicos de wa_id em historico:", df_historico["wa_id"].unique().tolist())

        # Carregar comportamentos
        collection_name = "comportamento"
        if collection_name not in db.list_collection_names():
            st.warning(f"⚠️ Coleção '{collection_name}' não encontrada")
            df_comportamento = pd.DataFrame(columns=["wa_id"])
        else:
            comportamento = list(db[collection_name].find())
            st.write(f"Número de documentos em {collection_name}:", len(comportamento))
            df_comportamento = pd.DataFrame(comportamento)
            if df_comportamento.empty:
                st.warning(f"⚠️ Coleção '{collection_name}' está vazia")
                df_comportamento = pd.DataFrame(columns=["wa_id"])
            if "wa_id" not in df_comportamento.columns:
                st.error(f"❌ Campo 'wa_id' não encontrado na coleção '{collection_name}'")
                df_comportamento["wa_id"] = None
            df_comportamento["wa_id"] = df_comportamento["wa_id"].astype(str)
            st.write("Valores únicos de wa_id em comportamento:", df_comportamento["wa_id"].unique().tolist())

        # Carregar usuários
        collection_name = "users"
        if collection_name not in db.list_collection_names():
            st.warning(f"⚠️ Coleção '{collection_name}' não encontrada")
            df_usuarios = pd.DataFrame(columns=["wa_id"])
        else:
            usuarios = list(db[collection_name].find())
            st.write(f"Número de documentos em {collection_name}:", len(usuarios))
            df_usuarios = pd.DataFrame(usuarios)
            if df_usuarios.empty:
                st.warning(f"⚠️ Coleção '{collection_name}' está vazia")
                df_usuarios = pd.DataFrame(columns=["wa_id"])
            if "wa_id" not in df_usuarios.columns:
                st.error(f"❌ Campo 'wa_id' não encontrado na coleção '{collection_name}'")
                df_usuarios["wa_id"] = None
            df_usuarios["wa_id"] = df_usuarios["wa_id"].astype(str)
            st.write("Valores únicos de wa_id em users:", df_usuarios["wa_id"].unique().tolist())

        # Merge de dados
        df = pd.merge(df_historico, df_comportamento, on="wa_id", how="left")
        df = pd.merge(df, df_usuarios, on="wa_id", how="left")
        
        if df.empty:
            st.warning("⚠️ Merge resultou em DataFrame vazio. Verifique correspondência de wa_id.")
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

# Continuação do código
df = carregar_dados()

# Tratamento de dados
if not df.empty:
    # Debugging: Inspecionar timestamp
    if "timestamp" in df.columns:
        st.write("Valores de timestamp antes da conversão:", df["timestamp"].head().tolist())
        st.write("Tipos de timestamp:", df["timestamp"].apply(type).unique().tolist())
    else:
        st.warning("⚠️ Coluna 'timestamp' não encontrada no DataFrame")

    try:
        if "timestamp" in df.columns:
            # Função para normalizar diferentes formatos de timestamp
            def parse_timestamp(x):
                if pd.isna(x):
                    return None
                if isinstance(x, dict) and "$date" in x:
                    # Formato MongoDB: {"$date": {"$numberLong": "..."}}
                    return pd.to_datetime(int(x["$date"]["$numberLong"]), unit="ms") if "$numberLong" in x["$date"] else pd.to_datetime(x["$date"], unit="ms")
                try:
                    # Já é datetime ou pode ser convertido diretamente
                    return pd.to_datetime(x)
                except:
                    return None

            df["timestamp"] = df["timestamp"].apply(parse_timestamp)
            if df["timestamp"].notna().any():
                df["data_formatada"] = df["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
            else:
                st.warning("⚠️ Nenhum timestamp válido encontrado após conversão")
        else:
            st.warning("⚠️ Coluna 'timestamp' não encontrada, pulando conversão")
    except Exception as e:
        st.error(f"❌ Erro ao processar timestamp: {e}")

    conversions = {
        "_id_x": "object",
        "_id_y": "object",
        "lembrar_preferencias": "bool",
        "ultimo_acesso": "datetime64[ns]"
    }
    
    for col, dtype in conversions.items():
        if col in df.columns:
            try:
                df[col] = df[col].astype(dtype)
            except Exception as e:
                st.warning(f"⚠️ Erro ao converter {col}: {e}")

# Filtros laterais
st.sidebar.header("📌 Filtros")

if not df.empty:
    usuarios = ["Todos"] + df["wa_id"].dropna().unique().tolist()
    numero = st.sidebar.selectbox("Filtrar por número:", usuarios)
    
    if numero != "Todos":
        df = df[df["wa_id"] == numero]

    origens = ["Todos"] + df["origem"].dropna().unique().tolist()
    origem = st.sidebar.selectbox("Filtrar por origem:", origens)
    
    if origem != "Todos":
        df = df[df["origem"] == origem]

    palavra = st.sidebar.text_input("🔍 Buscar por palavra-chave:")
    if palavra:
        df = df[df["mensagem"].str.contains(palavra, case=False, na=False)]

# Exibição da tabela
st.subheader("📬 Mensagens registradas:")

if not df.empty:
    colunas = [
        "data_formatada", 
        "wa_id", 
        "origem", 
        "mensagem", 
        "tom_ideal", 
        "estilo",
        "produtividade"
    ]
    
    colunas_disponiveis = [c for c in colunas if c in df.columns]
    st.dataframe(df[colunas_disponiveis], use_container_width=True)
else:
    st.warning("⚠️ Nenhum dado encontrado na base de dados")

# Rodapé
st.markdown("---")
st.caption("Copiloto IA © 2025 • Visualização e análise de histórico de interações.")