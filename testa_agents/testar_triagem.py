import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from agents import Runner #type: ignore
from pymongo import MongoClient #type: ignore
from dotenv import load_dotenv #type: ignore
from agentes_copiloto.triagem import triage_copiloto_agent
from context.sintetizar import salvar_contexto_usuario
from agentes_copiloto.triagem import triage_copiloto_agent
from context.verificar_conversa import verificar_necessidade_resumo
from agentes_copiloto.spinsalinng import spinselling_agent
from agentes_copiloto.solucoes_ai import solucoes_ai_em_demanda_agent
from core.mensageiro import enviar_resposta
from db.historico import salvar_mensagem

load_dotenv() 
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]

cenarios = [
    # #Organizador de memória
    # ("Preciso agendar minhas reuniões da próxima semana", "organizador_memoria_agent"),
    # ("Lembre-me de enviar o relatório até sexta-feira", "organizador_memoria_agent"),

    # Apoio emocional / comportamental
    ("Estou me sentindo sobrecarregado com tantas demandas", "emocional_comportamental_agent"),
    ("Não paro de pensar em tudo que tenho que fazer e quero descansar", "emocional_comportamental_agent"),
    ("quero encerrar a conversar!", "optimum_writer_agent"),

    # # Otimizador de textos / writer
    # ("Me ajude a criar o roteiro de um webinar sobre finanças", "optimum_writer_agent"),
    # ("Escreva uma thread para o Twitter sobre hábitos de leitura", "optimum_writer_agent"),
    # ("quero encerrar a conversar!", "optimum_writer_agent"),

    # # Soluções de IA sob demanda
    # ("Quais APIs de NLP vocês recomendam para análise de sentimentos?", "solucoes_ai_em_demanda_agent"),
    # ("Como integrar reconhecimento de voz em uma aplicação web?", "solucoes_ai_em_demanda_agent"),
    # ("quero encerrar a conversar!", "solucoes_ai_em_demanda_agent"),

    # Estratégia intelectual
    # ("quero encerrar a conversar!", "estrategista_intelectual_agent"),
    # ("Qual é a melhor estratégia para expandir meu negócio internacionalmente?", "estrategista_intelectual_agent"),
    ("Preciso de um plano de ação para aumentar meu faturamento no próximo semestre", "estrategista_intelectual_agent"),
    ("quero encerrar a conversar!", "spinselling_agent"),

    # SPIN Selling
    # ("quero encerrar a conversar!", "spinselling_agent"),
    # ("Gostaria de aprender SPIN Selling para vender consultorias B2B", "spinselling_agent"),
    # ("Como aplicar SPIN Selling para clientes de software?", "spinselling_agent"),
    # ("quero encerrar a conversar!", "spinselling_agent"),

    # # Fallback (quando não se enquadra em nenhum agente específico)
    # ("Qual é a cor preferida dos gatos?", "estrategista_intelectual_agent"),
    # ("Conte-me um fato curioso sobre a Via Láctea", "estrategista_intelectual_agent"),
    # ("quero encerar a conversar")
]


async def testar_triagem():
    for i, (mensagem, esperado) in enumerate(cenarios, 1):
        print("✅================ TESTE: TRIAGEM INTELIGENTE =================✅")
        print(f"_❓_ Cenário {i}: {mensagem}")
        wa_id = "353833844418"
        resposta_contexto = await verificar_necessidade_resumo(wa_id, mensagem)
        contexto = resposta_contexto
        # print(contexto)
        if isinstance(resposta_contexto, str):
            resposta_texto = resposta_contexto.strip()
            print(f"_❓__❓_⚡ Resposta direta do agente ativo: {resposta_texto}")
            estado_mongo = users_collection.find_one(
                {"wa_id": wa_id},
                {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1, "conversa_em_andamento":1}
            )
            print(f"_💾_ Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")    
            print(f"_💾_ Contexto Mongo: conversa_em_andamento = {estado_mongo.get('conversa_em_andamento')}")     
            print("================ AGENTE DIRETO — FIM =================")
            return 


        resposta = await Runner.run(triage_copiloto_agent, input=mensagem, context=contexto)
        resposta_agent = resposta.final_output.strip()
        # await salvar_contexto_usuario(wa_id, contexto)
        # print("__✅__" * 10)
        print(f"💬 Resposta final: {resposta_agent}\n")

        # estado_mongo = users_collection.find_one(
        #     {"wa_id": wa_id},
        #     {"_id": 0, "agente_em_conversa": 1, "ultima_interacao": 1, "conversa_em_andamento":1}
        # )
        # print(f"_💾__💾_ Contexto Mongo: agente_em_conversa = {estado_mongo.get('agente_em_conversa')}")    
        # print(f"_💾__💾_ Contexto Mongo: conversa_em_andamento = {estado_mongo.get('conversa_em_andamento')}")        
        # resposta_final = estado_mongo.get('agente_em_conversa')
        # if resposta_final == esperado:
        #     print(f"✅ PASSOU | Esperado: {esperado} | Atual: {resposta_final}")
        #     #print("_✅_" * 25)
        #     print("================ TESTE: TRIAGEM INTELIGENTE FIM =================")
        # else:
        #     print(f"❌ FALHOU | Esperado: {esperado} | Atual: {estado_mongo}")
        #     #print("_❌_" * 25)
        #     print("================ TESTE: TRIAGEM INTELIGENTE FIM =================")
        print("================ TESTE: TRIAGEM INTELIGENTE FIM =================")

if __name__ == "__main__":
    asyncio.run(testar_triagem())
