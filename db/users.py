from db.mongo import db
import time

users_collection = db["users"]

def salvar_ou_atualizar_usuario(wa_id, nome=None):
    users_collection.update_one(
        {"wa_id": wa_id},
        {
            "$set": {
                "nome": nome,
                "ultimo_acesso": time.time()
            },
            
        },
        upsert=True
    )

def consultar_perfil_usuario(wa_id):
    return users_collection.find_one({"wa_id": wa_id})
