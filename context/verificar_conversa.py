import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents import Runner # type: ignore
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
from Agent_copiloto.triagem import triage_copiloto_agent
from Agent_serviflex.Agent_principal import Agent_principal

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]
historico_collection = db["historico"]

async def carregar_contexto_simples(wa_id: str) -> dict:
     # 🧹 Buscar apenas mensagens do usuário (últimas 5)
    historico_bruto = list(
        historico_collection.find(
            {"wa_id": wa_id, "origem": "usuario"}
        ).sort("timestamp", -1).limit(6)
    )
    historico = sorted(historico_bruto, key=lambda x: x["timestamp"])
    # print(historico)
    return {
        "wa_id": wa_id,
        "historico": historico,
    }

def formatar_historico_para_prompt_mongo(historico: list, mensagem_atual: str) -> str:
    mensagens_formatadas = []
    for msg in historico:
        origem = msg.get("origem")
        content = msg.get("mensagem")
        if origem == "usuario":
            mensagens_formatadas.append(f"Usuário: {content}")
        elif origem == "copiloto":
            mensagens_formatadas.append(f"Assistente: {content}")
    # adiciona a nova mensagem no fim
    mensagens_formatadas.append(f"Usuário: {mensagem_atual}")
    return "\n".join(mensagens_formatadas)


#------------ verifica se a conversa esta em andamento -----------------#
async def verificar_necessidade_resumo(wa_id: str, mensagem) -> dict:
    print(f"_🔁_ Conversa iniciada")
    contexto = await carregar_contexto_simples(wa_id)
    historico_mensagens = contexto.get("historico", [])
    input_formatado = formatar_historico_para_prompt_mongo(historico_mensagens, mensagem)

    resposta = await Runner.run(
        triage_copiloto_agent,
        input=input_formatado
    )
    print("_🔁_======== Fim da lógica do agent direto ===========🔁 ")
    return resposta.final_output


