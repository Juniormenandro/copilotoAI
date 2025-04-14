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


def salvar_comportamento(wa_id, novos_dados):
    existente = comportamento_collection.find_one({"wa_id": wa_id})

    if not existente:
        # Se ainda não existir, insere o padrão
        comportamento = {
            "wa_id": wa_id,
            **novos_dados
        }
        comportamento_collection.insert_one(comportamento)
        print(f"🧠 Comportamento criado para {wa_id}")
        return

    # Descobre o que realmente mudou
    atualizacoes = {}
    for campo, novo_valor in novos_dados.items():
        valor_atual = existente.get(campo)
        if valor_atual != novo_valor:
            atualizacoes[campo] = novo_valor

    if atualizacoes:
        comportamento_collection.update_one(
            {"wa_id": wa_id},
            {"$set": atualizacoes}
        )
        print(f"🧠 Campos atualizados para {wa_id}: {list(atualizacoes.keys())}")
    else:
        print(f"✅ Nenhuma mudança detectada para {wa_id}, nada foi alterado.")



def consultar_comportamento(wa_id):
    return comportamento_collection.find_one({"wa_id": wa_id})
