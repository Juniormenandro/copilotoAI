from db.mongo import db
import time
from db.comportamento import criar_comportamento_padrao

users_collection = db["users"]

def salvar_ou_atualizar_usuario(wa_id, nome=None):
    users_collection.update_one(
        {"wa_id": wa_id},
        {
            "$set": {
                "nome": nome,
                "ultimo_acesso": time.time()
            },
            "$setOnInsert": {
                "criado_em": time.time(),
                "produtividade": "neutra",
                "lembrar_preferencias": True
            }
        },
        upsert=True
    )
    criar_comportamento_padrao(wa_id)

def consultar_perfil_usuario(wa_id):
    return users_collection.find_one({"wa_id": wa_id})
