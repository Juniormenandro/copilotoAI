from pymongo import MongoClient # type: ignore
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

# Conexão Mongo
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise EnvironmentError("MONGO_URI não configurado no .env")
client = MongoClient(mongo_uri)
db = client["copilotoAI"]

users = db["users"]
comportamento_collection = db["comportamento"]
historico_collection = db["historico"]

def carregar_contexto_usuario(wa_id: str) -> dict:
    context = {"wa_id": wa_id}

    # Comportamento
    comportamento = comportamento_collection.find_one({"wa_id": wa_id})
    context["comportamento"] = comportamento or None

    # Histórico (últimas 20 mensagens)
    historico_cursor = historico_collection.find({"wa_id": wa_id}).sort("timestamp", -1).limit(20)
    historico = list(historico_cursor)
    context["historico"] = list(reversed(historico))  # coloca em ordem cronológica

    # Dados do usuário (agente atual, última interação)
    usuario = users.find_one({"wa_id": wa_id})
    if usuario:
        context["agente_em_conversa"] = usuario.get("agente_em_conversa")
        context["ultima_interacao"] = usuario.get("ultima_interacao")
    else:
        context["agente_em_conversa"] = None
        context["ultima_interacao"] = None

    return context
