import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from agents import Runner
from pymongo import MongoClient
from dotenv import load_dotenv

from context.sintetizar import carregar_contexto_usuario, salvar_contexto_usuario
from agentes_copiloto.triagem import triage_copiloto_agent

load_dotenv() 

client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]

cenarios = [
    #Organizador de memória
    # ("Preciso agendar minhas reuniões da próxima semana", "organizador_memoria_agent"),
    # ("Lembre-me de enviar o relatório até sexta-feira", "organizador_memoria_agent"),

    # # Apoio emocional / comportamental
    # ("Estou me sentindo sobrecarregado com tantas demandas", "emocional_comportamental_agent"),
    # ("Não paro de pensar em tudo que tenho que fazer e quero descansar", "emocional_comportamental_agent"),

    # # Otimizador de textos / writer
    # ("Me ajude a criar o roteiro de um webinar sobre finanças", "optimum_writer_agent"),
    # ("Escreva uma thread para o Twitter sobre hábitos de leitura", "optimum_writer_agent"),

    # # Soluções de IA sob demanda
    # ("Quais APIs de NLP vocês recomendam para análise de sentimentos?", "solucoes_ai_em_demanda_agent"),
    # ("Como integrar reconhecimento de voz em uma aplicação web?", "solucoes_ai_em_demanda_agent"),

    # Estratégia intelectual
    ("Qual é a melhor estratégia para expandir meu negócio internacionalmente?", "estrategista_intelectual_agent"),
    ("Preciso de um plano de ação para aumentar meu faturamento no próximo semestre", "estrategista_intelectual_agent"),

    # # SPIN Selling
    # ("Gostaria de aprender SPIN Selling para vender consultorias B2B", "spinselling_agent"),
    # ("Como aplicar SPIN Selling para clientes de software?", "spinselling_agent"),

    # # Fallback (quando não se enquadra em nenhum agente específico)
    # ("Qual é a cor preferida dos gatos?", "estrategista_intelectual_agent"),
    # ("Conte-me um fato curioso sobre a Via Láctea", "estrategista_intelectual_agent"),
]


async def testar_triagem():
    wa_id = "353833844418"
    context = await carregar_contexto_usuario(wa_id)
    contexto = context
    print("\n================ TESTE: TRIAGEM INTELIGENTE =================\n")
    for i, (mensagem, esperado) in enumerate(cenarios, 1):
        print("--" * 60)
        print(f"❓ Cenário {i}: {mensagem}")
        
        resposta = await Runner.run(triage_copiloto_agent, input=mensagem, context=context)
        resposta_agent = resposta.final_output.strip()
        #print('< . . >' * 20)
        await salvar_contexto_usuario(wa_id, contexto)
        print("-   -" * 20)
        print(f"💬 Resposta final: {resposta_agent}\n")
        print("-   -" * 20)

        estado_mongo = users_collection.find_one(
            {"wa_id": wa_id},
            {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1}
        )
        print(f"📍 Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")      
        resposta_final = estado_mongo.get('agente_em_conversa')

        if resposta_final == esperado:
            print(f"✅ PASSOU | Esperado: {esperado} | Atual: {resposta_final}")
            print("--" * 60)
        else:
            print(f"❌ FALHOU | Esperado: {esperado} | Atual: {estado_mongo}")
            print("--" * 60)

if __name__ == "__main__":
    asyncio.run(testar_triagem())
