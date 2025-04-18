import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from context.sintetizar import carregar_contexto_usuario, salvar_contexto_usuario
from agentes_copiloto.organizador import organizador_memoria_agent
from agents import Runner
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]



mensagens_teste = [
    # Continuidade temática (mantém contexto de escrita)
    # "Preciso criar um artigo para um blog de tecnologia voltado para iniciantes. pode salva no registro tarefas para domingo as 17h.",
    # "tecnologia large lingue model resgistra como tarefa de estudo ate segunda feira as 13h",
    "listar minhas tarefas",

    # # Injeção emocional
    "Desculpa, tô um pouco cansado hoje... talvez esteja sobrecarregado.",
]

async def testar_organizador():
    wa_id = "353833844418"
    contexto = await carregar_contexto_usuario(wa_id)

    print("\n================ TESTE DE CONTINUIDADE: OPTIMUM WRITER =================\n")

    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"❓ Pergunta {i}: {mensagem}")
        resposta = await Runner.run(
            organizador_memoria_agent,
            input=mensagem,
            context=contexto
        )

        resposta_texto = resposta.final_output.strip()
        print("💬 Resposta:")
        print(resposta_texto)

        # Atualiza o banco com o contexto mais recente
        await salvar_contexto_usuario(wa_id, contexto)

        # Verifica diretamente no Mongo
        estado_mongo = users_collection.find_one(
            {"wa_id": wa_id},
            {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1}
        )
        print(f"📍 Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")
        print("-" * 60)

if __name__ == "__main__":
    asyncio.run(testar_organizador())
