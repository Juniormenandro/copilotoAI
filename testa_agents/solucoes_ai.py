import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from context.sintetizar import carregar_contexto_usuario, salvar_contexto_usuario
from agentes_copiloto.solucoes_ai import solucoes_ai_em_demanda_agent
from agents import Runner
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]

mensagens_teste = [
    # Perguntas sobre IA em demanda
    "Quais são os tipos de soluções de IA mais procuradas hoje?",
    "Me dá exemplos de aplicações práticas que estão em alta.",
    "E no Brasil? Tem alguma tendência específica de IA se destacando?",

    # Injeção emocional
    "Cara, tô me sentindo meio perdido sobre onde focar. Muita coisa acontecendo...",

    # Mudança de tópico (gatilho de triagem)
    "Você sabe quanto tá o euro hoje em Limerick?"
]

async def testar_solucoes_ai_agent():
    wa_id = "353833844418"
    contexto = await carregar_contexto_usuario(wa_id)

    print("\n================ TESTE DE CONTINUIDADE: SOLUÇÕES AI EM DEMANDA =================\n")

    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"❓ Pergunta {i}: {mensagem}")
        resposta = await Runner.run(
            solucoes_ai_em_demanda_agent,
            input=mensagem,
            context=contexto
        )

        resposta_texto = resposta.final_output.strip()
        print("💬 Resposta:")
        print(resposta_texto)

        await salvar_contexto_usuario(wa_id, contexto)

        estado_mongo = users_collection.find_one(
            {"wa_id": wa_id},
            {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1}
        )
        print(f"📍 Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(testar_solucoes_ai_agent())

 