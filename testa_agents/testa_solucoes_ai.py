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
    # Continuação natural + aprofundamento estratégico
    "Quais são os produtos digitais mais promissores baseados em IA hoje?",
    "Me mostra exemplos de empresas ou pessoas ganhando dinheiro com isso na prática.",
    # "Como posso começar com diferencial e não parecer só mais um?",
    # "Qual dessas estratégias você acha que tem mais a ver com o meu momento atual?",
    # "Você gostaria de explorar uma dessas soluções de forma prática, com ferramentas ou exemplos aplicáveis?",
    # "Quer ajuda para transformar uma dessas ideias em um produto digital real com IA?",
    # "Já tenho uma ideia de público. Pode me ajudar a formatar a proposta de valor?",
    # "Tem alguma ferramenta de IA que já posso usar hoje para começar?",
    # "Pode me sugerir uma automação simples para validar minha ideia no WhatsApp?",
    # "Gostaria de montar um plano de ação simples com IA para aplicar ainda essa semana. Pode ajudar?"
]

async def testar_solucoes_ai_em_demanda():
    wa_id = "353833844418"
    contexto = await carregar_contexto_usuario(wa_id)

    print("\n================ TESTE DE CONTINUIDADE: SOLUÇÕES AI EM DEMANDA =================\n")

    for i, mensagem in enumerate(mensagens_teste, 1):
       # print(f"❓ Pergunta {i}: {mensagem}")
        resposta = await Runner.run(
            solucoes_ai_em_demanda_agent,
            input=mensagem,
            context=contexto
        )

        resposta_texto = resposta.final_output.strip()
        # print("💬 Resposta:")
        # print(resposta_texto)

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
    asyncio.run(testar_solucoes_ai_em_demanda())
