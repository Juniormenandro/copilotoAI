# --- db/historico.py ---
from db.mongo import db
from datetime import datetime

historico_collection = db["historico"]
#historico_collection = db["historico_conversas"]



def salvar_mensagem(wa_id, origem, texto):
    historico_collection.insert_one({
        "wa_id": wa_id,
        "origem": origem,  # "usuario" ou "copiloto"
        "mensagem": texto,
        "timestamp": datetime.utcnow()
    })
    print(f"💾 Mensagem registrada: [{origem}] {texto}")

def registrar_mensagem(wa_id, origem, conteudo, timestamp=None):
    historico_collection.insert_one({
        "wa_id": wa_id,
        "origem": origem,  # "usuario" ou "copiloto"
        "conteudo": conteudo,
        "timestamp": timestamp or int(datetime.utcnow().timestamp())
    })
    print("💾 Mensagem atualizada:")
def consultar_historico(wa_id, limite=20):
    mensagens = historico_collection.find({"wa_id": wa_id}).sort("timestamp", -1).limit(limite)
    return list(mensagens)[::-1]  # ordem cronológica normal
