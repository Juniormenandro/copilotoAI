from pymongo import MongoClient # type: ignore
from datetime import datetime 
from dotenv import load_dotenv # type: ignore
from datetime import datetime, timezone # type: ignore
import os

# Carrega variáveis de ambiente
load_dotenv()

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise EnvironmentError("MONGO_URI não configurado no .env")
client = MongoClient(mongo_uri)
db = client["copilotoAI"]


wa_id = "353833844418"
comportamento_collection = db["comportamento"]
historico = db["historico"]
users = db['users']

# 1. Inserir comportamento padrão
comportamento_collection.update_one(
    {"wa_id": wa_id},
    {
        "$set": {
            "tom_ideal": "leve, empático e direto",
            "gatilhos": [
                "evita rejeição",
                "se sobrecarrega fácil",
                "precisa de reforço positivo",
                "não gosta de cobrança dura"
            ],
            "estilo": "curto e motivacional",
            "foco": "clareza mental com leveza emocional",
            "timestamp": datetime.now(timezone.utc)
        }
    },
    upsert=True
)

# 2. Inserir histórico simulado
mensagens = [
    {
        "wa_id": wa_id,
        "origem": "usuario",
        "mensagem": "Me sinto muito cansado",
        "timestamp": datetime.now(timezone.utc)
    },
    {
        "wa_id": wa_id,
        "origem": "copiloto",
        "mensagem": "Sinto muito que você esteja se sentindo assim. Quer conversar?",
        "agente": "copiloto",
        "timestamp": datetime.now(timezone.utc)
    },
]

historico.insert_many(mensagens)

# 3. Criar documento do usuário com agente atual
users.update_one(
    {"wa_id": wa_id},
    {
        "$set": {
            "nome": "Junior Menandro",
            "ultima_interacao": datetime.now(timezone.utc).isoformat(),
            "agente_em_conversa": "emocional_comportamental_agent"
        }
    },
    upsert=True
)

# print("✅ Dados simulados inseridos com sucesso no MongoDB!")
