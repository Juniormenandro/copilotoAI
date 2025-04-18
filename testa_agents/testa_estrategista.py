import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from context.sintetizar import carregar_contexto_usuario, salvar_contexto_usuario
from agentes_copiloto.estrategista import estrategista_intelectual_agent
from agents import Runner
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]



mensagens_teste = [
    # Continuidade temática (mantém contexto de escrita)
    "Preciso criar um artigo para um blog de tecnologia voltado para iniciantes. Pode me ajudar?",
    "Tema específico: Sobre qual tecnologia large lingue model, Público-alvo: idade 23 a 40,  Tom desejado: Amigável, extensão: 345 palavras",
    # "Você pode sugerir a estrutura ideal com subtítulos e o que abordar em cada seção?",
    "Agora desenvolva o primeiro tópico com exemplos práticos.",

    # # Injeção emocional
    # "Desculpa, tô um pouco cansado hoje... talvez esteja sobrecarregado.",
]

async def testar_estrategista():
    wa_id = "353833844418"
    contexto = await carregar_contexto_usuario(wa_id)

    print("\n================ TESTE DE CONTINUIDADE: OPTIMUM WRITER =================\n")

    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"❓ Pergunta {i}: {mensagem}")
        resposta = await Runner.run(
            estrategista_intelectual_agent,
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
    asyncio.run(testar_estrategista())
