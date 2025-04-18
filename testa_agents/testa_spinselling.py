import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import json
from context.sintetizar import carregar_contexto_usuario
from agentes_copiloto.spinsalinng import spinselling_agent
from agents import Runner
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]

mensagens_teste = [
    "Tenho um cliente que está interessado, mas ainda não entendeu completamente o valor do que eu ofereço. Como posso começar a abordagem SPIN com ele?",
    "Ele é dono de uma clínica estética e diz que os agendamentos caíram nos últimos meses. Como transformar isso numa pergunta de problema ou implicação?",
    # "Já identifiquei que ele quer aumentar o faturamento. Como posso demonstrar minha solução usando a fórmula RVB?"
]


async def testar_spinselling_agent():
    wa_id = "353833844418"
    contexto = await carregar_contexto_usuario(wa_id)

    print("\n================ TESTE DE CONTINUIDADE: SPINSELLING =================\n")

    for i, mensagem in enumerate(mensagens_teste, 1):
        # print(f"❓ Pergunta {i}: {mensagem}")
        resposta = await Runner.run(
            spinselling_agent,
            input=mensagem,
            context=contexto
        )
        resposta_texto = resposta.final_output.strip()
        # print("💬 Resposta:")
        # print(resposta_texto)
        
        users_collection.update_one(
            {"wa_id": wa_id},
            {"$set": {
                "agente_em_conversa": "spinselling_agent"
            }}
        )
        estado_mongo = users_collection.find_one(
            {"wa_id": wa_id},
            {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1}
        )
        print(f"📍 Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(testar_spinselling_agent())
