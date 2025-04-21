from pymongo import MongoClient # type: ignore
from datetime import datetime

# 📌 Conexão com seu banco
client = MongoClient("mongodb+srv://jojuniorjo:ieYmunRe9JMcpsuJ@cluster0.xld3pvt.mongodb.net")
db = client["copilotoAI"]

wa_id = "353833844418"

# 1. Inserir comportamento padrão
db.comportamento.update_one(
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
            "timestamp": datetime.utcnow()
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
        "timestamp": datetime.utcnow()
    },
    {
        "wa_id": wa_id,
        "origem": "copiloto",
        "mensagem": "Sinto muito que você esteja se sentindo assim. Quer conversar?",
        "agente": "copiloto",
        "timestamp": datetime.utcnow()
    },
]

db.historico.insert_many(mensagens)

# 3. Criar documento do usuário com agente atual
db.users.update_one(
    {"wa_id": wa_id},
    {
        "$set": {
            "nome": "Junior Menandro",
            "ultima_interacao": datetime.utcnow().isoformat(),
            "agente_em_conversa": "emocional_comportamental_agent"
        }
    },
    upsert=True
)

print("✅ Dados simulados inseridos com sucesso no MongoDB!")
