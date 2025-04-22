from db.mongo import db
from datetime import datetime

memorias_collection = db["memorias"]

def salvar_memoria(wa_id, tipo, conteudo):
    memoria = {
        "wa_id": wa_id,
        "tipo": tipo,
        "conteudo": conteudo,
        "data": datetime.utcnow().strftime("%Y-%m-%d")
    }
    memorias_collection.insert_one(memoria)
   # print(f"🧠 Memória salva: {tipo} para {wa_id}")


def ja_foi_acolhido(wa_id):
    memoria = memorias_collection.find_one({
        "wa_id": wa_id,
        "tipo": "onboarding",
        "chave": "acolhimento_inicial"
    })
    return memoria is not None


def registrar_acolhimento(wa_id):
    memoria = {
        "wa_id": wa_id,
        "tipo": "onboarding",
        "chave": "acolhimento_inicial",
        "valor": "sim",
        "data": datetime.utcnow().strftime("%Y-%m-%d")
    }
    memorias_collection.insert_one(memoria)
   # print(f"🙌 Acolhimento inicial registrado para {wa_id}")


def consultar_objetivo_da_semana(wa_id):
    memoria = memorias_collection.find_one(
        {"wa_id": wa_id, "tipo": "objetivo_da_semana"},
        sort=[("data", -1)]
    )
    # if memoria:
    #     print(f"🎯 Objetivo encontrado para {wa_id}: {memoria['conteudo']}")
    # else:
    #     print(f"📭 Nenhum objetivo encontrado para {wa_id}")
    return memoria["conteudo"] if memoria else None
