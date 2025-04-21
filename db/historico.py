from db.mongo import db
from datetime import datetime

historico_collection = db["historico"]

def salvar_mensagem(wa_id, origem, texto, message_id=None, agente=None):
    historico_collection.insert_one({
        "wa_id": wa_id,
        "origem": origem,  # "usuario" ou nome do agente
        "mensagem": texto,
        "agente": agente or (origem if origem != "usuario" else None),
        "timestamp": datetime.utcnow(),
        "message_id": message_id  # pode ser None se não for via webhook
    })
    # print(f"💾 Mensagem registrada de {origem}: {texto}")

def registrar_mensagem(wa_id, origem, conteudo, timestamp=None, agente=None):
    historico_collection.insert_one({
        "wa_id": wa_id,
        "origem": origem,
        "conteudo": conteudo,
        "agente": agente or (origem if origem != "usuario" else None),
        "timestamp": timestamp or datetime.utcnow()
    })
    print("💾 Mensagem atualizada (registrar_mensagem)")

def consultar_historico(wa_id, limite=30, agente=None):
    filtro = {"wa_id": wa_id}
    if agente:
        filtro["$or"] = [
            {"origem": "usuario"},
            {"agente": agente}
        ]

    mensagens = historico_collection.find(filtro).sort("timestamp", -1).limit(limite)
    return list(mensagens)[::-1]  # ordem cronológica


def consultar_historico_com_agente(wa_id, agente_nome, limite=10):
    """
    Retorna as últimas conversas entre o usuário e um agente específico.
    Inclui mensagens enviadas pelo usuário e pelo agente em questão.
    """
    mensagens = historico_collection.find({
        "wa_id": wa_id,
        "origem": {"$in": ["usuario", agente_nome]}
    }).sort("timestamp", -1).limit(limite)

    return list(mensagens)[::-1]  # retorna em ordem cronológica
