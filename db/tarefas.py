from db.mongo import db
from datetime import datetime
from difflib import get_close_matches

tarefas_collection = db["tarefas"]
# print(f"🚀 Conectado à coleção tarefas: {tarefas_collection.name}")


def registrar_tarefa(wa_id, descricao, prioridade="normal", data_entrega=None):
    print(f"💾 Registrando no Mongo: {wa_id}, {descricao}, {data_entrega}")
    try:
        tarefa = {
            "wa_id": wa_id,
            "descricao": descricao.strip(),
            "status": "pendente",
            "prioridade": prioridade,
            "data_criacao": datetime.now().strftime("%Y-%m-%d"),
            "data_entrega": data_entrega
        }
        result = tarefas_collection.insert_one(tarefa)
        print(f"✅ Tarefa salva no Mongo com _id: {result.inserted_id}")
    except Exception as e:
        print(f"❌ Erro ao salvar tarefa no Mongo: {e}")


def listar_tarefas(wa_id, status="pendente"):
    print(f"🔍 Buscando tarefas de {wa_id} com status {status}")
    tarefas = list(tarefas_collection.find({
        "wa_id": wa_id,
        "status": status
    }))
    print(f"🔍 Encontradas: {len(tarefas)}")
    return tarefas


def concluir_tarefa(wa_id, descricao):
    todas = listar_tarefas(wa_id)
    nomes = [t["descricao"] for t in todas]
    similares = get_close_matches(descricao.strip().lower(), [n.lower() for n in nomes], n=1, cutoff=0.6)

    if not similares:
        return False, nomes

    tarefa_encontrada = next((t for t in todas if t["descricao"].lower() == similares[0]), None)
    if tarefa_encontrada:
        tarefas_collection.update_one({"_id": tarefa_encontrada["_id"]}, {"$set": {"status": "concluida"}})
        return True, tarefa_encontrada["descricao"]

    return False, nomes


def adiar_tarefa(wa_id, descricao, nova_data):
    todas = listar_tarefas(wa_id)
    nomes = [t["descricao"] for t in todas]
    similares = get_close_matches(descricao.strip().lower(), [n.lower() for n in nomes], n=1, cutoff=0.6)

    if not similares:
        return False, nomes

    tarefa_encontrada = next((t for t in todas if t["descricao"].lower() == similares[0]), None)
    if tarefa_encontrada:
        tarefas_collection.update_one({"_id": tarefa_encontrada["_id"]}, {"$set": {"data_entrega": nova_data}})
        return True, tarefa_encontrada["descricao"]

    return False, nomes
