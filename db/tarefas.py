from db.mongo import db
from datetime import datetime

tarefas_collection = db["tarefas"]

def registrar_tarefa(wa_id, descricao, prioridade="normal", data_entrega=None):
    print(f"💾 Registrando no Mongo: {wa_id}, {descricao}, {data_entrega}")
    tarefa = {
        "wa_id": wa_id,
        "descricao": descricao,
        "status": "pendente",
        "prioridade": prioridade,
        "data_criacao": datetime.now().strftime("%Y-%m-%d"),
        "data_entrega": data_entrega
    }
    tarefas_collection.insert_one(tarefa)

def listar_tarefas(wa_id, status="pendente"):
    print(f"🔍 Buscando tarefas de {wa_id} com status {status}")
    tarefas = list(tarefas_collection.find({
        "wa_id": wa_id,
        "status": status
    }))
    print(f"🔍 Encontradas: {len(tarefas)}")
    return tarefas
