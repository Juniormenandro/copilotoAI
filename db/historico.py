from db.mongo import db
from datetime import datetime

historico_collection = db["historico"]

def salvar_mensagem(wa_id, origem, texto, message_id=None, agente=None):
    historico_collection.insert_one({
        "wa_id": wa_id,
        "origem": origem,  # "usuario" ou nome do agente
        "mensagem": texto,
        "timestamp": datetime.utcnow(),
    })
    # print(f"💾 Mensagem registrada de {origem}: {texto}")

def consultar_historico(wa_id, limite=30, agente=None):
    filtro = {"wa_id": wa_id}
    if agente:
        filtro["$or"] = [
            {"origem": "usuario"},
            {"agente": agente}
        ]

    mensagens = historico_collection.find(filtro).sort("timestamp", -1).limit(limite)
    return list(mensagens)[::-1]  # ordem cronológica

