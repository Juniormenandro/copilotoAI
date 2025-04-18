import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise EnvironmentError("MONGO_URI não configurado no .env")
client = MongoClient(mongo_uri)
db = client["copilotoAI"]


def salvar_mensagem(wa_id: str, origem: str, mensagem: str) -> None:
    """Salva uma mensagem no histórico no MongoDB."""
    try:
        colecao_mensagens = db["historico"]
        documento = {
            "wa_id": f"wa_id:{wa_id}",
            "mensagem": mensagem,
            "origem": origem,  # "usuario" ou "copiloto"
            "timestamp": int(time.time())
        }
        colecao_mensagens.insert_one(documento)
        print(f"💾 Mensagem salva: {mensagem}")
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem: {e}")

def salvar_comportamento(wa_id: str, comportamento: dict) -> None:
    """Salva dados de comportamento no MongoDB."""
    try:
        colecao_comportamento = db["comportamento"]
        documento = {
            "wa_id": f"wa_id:{wa_id}",
            "comportamento": comportamento,
            "timestamp": int(time.time())
        }
        colecao_comportamento.insert_one(documento)
        print(f"💾 Comportamento salvo: {comportamento}")
    except Exception as e:
        print(f"❌ Erro ao salvar comportamento: {e}")