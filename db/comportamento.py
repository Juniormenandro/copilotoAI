from db.mongo import db

comportamento_collection = db["comportamento"]

def criar_comportamento_padrao(wa_id):
    comportamento = {
        "wa_id": wa_id,
        "tom_ideal": "leve, empático e direto",
        "gatilhos": [
            "evita rejeição",
            "se sobrecarrega fácil",
            "precisa de reforço positivo",
            "não gosta de cobrança dura"
        ],
        "estilo": "curto e motivacional",
        "foco": "clareza mental com leveza emocional"
    }

    existente = comportamento_collection.find_one({"wa_id": wa_id})
    if not existente:
        comportamento_collection.insert_one(comportamento)
        print(f"🧠 Perfil comportamental padrão salvo para {wa_id}")

def salvar_comportamento(wa_id, dados):
    """
    Substitui completamente os dados anteriores por novos dados comportamentais,
    exceto o wa_id que sempre é mantido.
    """
    dados_completos = {
        "wa_id": wa_id,
        **dados
    }

    comportamento_collection.update_one(
        {"wa_id": wa_id},
        {"$set": dados_completos},
        upsert=True
    )
    print(f"🧠 Dados comportamentais atualizados para {wa_id}")

def consultar_comportamento(wa_id):
    return comportamento_collection.find_one({"wa_id": wa_id})
