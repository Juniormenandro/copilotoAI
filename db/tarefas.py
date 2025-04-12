from db.mongo import db
from datetime import datetime

tarefas_collection = db["tarefas"]

def registrar_tarefa(wa_id, descricao, prioridade="normal", data_entrega=None):
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
    return list(tarefas_collection.find({
        "wa_id": wa_id,
        "status": status
    }))
