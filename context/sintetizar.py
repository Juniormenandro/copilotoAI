from typing import Dict
from agents import Agent, Runner # type: ignore
from datetime import datetime, timezone
from pymongo import MongoClient # type: ignore
from bson import ObjectId # type: ignore
from collections import Counter
import os
import json
from dotenv import load_dotenv # type: ignore


load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]
historico_collection = db["historico"]


  
#====== salva no banco de dados quando o agente em conversa e atualizado ==========#
async def salvar_contexto_usuario(wa_id: str, contexto: Dict):
    # print('__>__' * 20)
    # print(f"conversa_em_andamento: {contexto.get('conversa_em_andamento')}")
    # print('__>__' * 20)
    novo_valor = {
        "agente_em_conversa": contexto.get("agente_em_conversa"),
        "conversa_em_andamento": contexto.get("conversa_em_andamento"),
        "ultima_interacao": datetime.now(timezone.utc),
    }
    result = users_collection.update_one(
        {"wa_id": wa_id},
        {"$set": novo_valor},
        upsert=True
    )
    # print(f"_💾_ Contexto salvo no MongoDB para {wa_id}: {novo_valor}")
    # print('__💾__' * 20)








#========== logica para reduzir mensagens  =============#
def formatar_historico(historico):
    return "\n".join(
        f"{msg['origem'].capitalize()}: {msg['mensagem']}" for msg in historico
    )
def resumir_mensagens_repetidas(historico):
   # print("_📦_ resumir_mensagens_repetidas")
    mensagens = [msg['mensagem'] for msg in historico if msg['origem'] == 'usuario']
    contagem = Counter(mensagens)
    comprimido = []
    for msg in set(mensagens):
        if contagem[msg] > 1:
            comprimido.append(f"Usuário: {msg} (repetida {contagem[msg]}x)")
        else:
            comprimido.append(f"Usuário: {msg}")
    return comprimido





#============agente treinado para analizar as mensagem =============#
analista_emocional_agent = Agent(
    name="analista_emocional_agent",
    instructions="""
    Você é um analista de contexto emocional do Copiloto IA.
    Sua função é analisar o histórico de conversa recente e:

    1. Gerar um resumo emocional e situacional atual do usuário.
    2. Dizer se a conversa ainda está em andamento ou foi encerrada, conforme critérios abaixo:
       - Em andamento: se a última mensagem for uma pergunta ou esperar ação.
       - Encerrada: se for agradecimento, confirmação ou silêncio após resposta final.

    Formato da resposta:
    ```json
    {
      "resumo": "Seu resumo aqui...",
      "conversa_em_andamento": true ou false
    }
    ```
    Seja direto, empático e objetivo. Não invente.
    Linguagem: português-BR.
    Saída apenas JSON.
    """
)





#=========== logica que chama o agent e passa as informacoes para ele analizar e retorna o resumo ======#
async def sintetizar_historico_com_agente(historico):
   # print("_📦_ dentro do sintetizar_historico_com_agente analizar e retorna o resumo")
    mensagens_formatadas = "\n".join(resumir_mensagens_repetidas(historico))
    entrada = f"Histórico recente:\n{mensagens_formatadas}"
    resposta = await Runner.run(
        analista_emocional_agent,
        input=entrada
    )
    try:
        return json.loads(resposta.final_output)
    except json.JSONDecodeError:
        return {
            "resumo": resposta.final_output,
            "conversa_em_andamento": None
        }

#===== logica principal que regencia as dados e a resposta do agent e retonar como context =========#
async def carregar_contexto_usuario(wa_id: str, historico) -> dict:
   # print(f"_📦_ dentro do carregar_contexto_usuario a logica de criacao do context")
    usuario = users_collection.find_one({"wa_id": wa_id}) or {}

    minutos_passados = None
    resumo_dados = {"resumo": None, "conversa_em_andamento": None}

    if historico and "timestamp" in historico[0]:
        resumo_dados = await sintetizar_historico_com_agente(historico)
        # print("\n_📦_ Contexto carregado com Agente 📦")
        # print(f"_📦_ wa_id: {wa_id}")
        # print(f"_📦_ resumo: {resumo_dados['resumo']}")
        # print(f"- conversa_em_andamento: {resumo_dados['conversa_em_andamento']}")
        # print('-📦-' * 20)

        msg_time = historico[0]["timestamp"]
        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)
        minutos_passados = (datetime.now(timezone.utc) - msg_time).total_seconds() / 60

    return {
        "wa_id": wa_id,
        "agente_em_conversa": (
            usuario.get("agente_em_conversa") if resumo_dados.get("conversa_em_andamento") else None
        ),
        "ultima_interacao": usuario.get("ultima_interacao"),
        "historico": historico,
        "resumo": resumo_dados.get("resumo"),
        "conversa_em_andamento": resumo_dados.get("conversa_em_andamento"),
        "minutos_desde_ultima_mensagem": minutos_passados
    }




if __name__ == "__main__":
    import asyncio
    asyncio.run(carregar_contexto_usuario("353833844418"))
