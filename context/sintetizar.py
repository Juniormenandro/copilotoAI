from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]

users_collection = db["users"]
comportamento_collection = db["comportamento"]
historico_collection = db["historico"]

openai_client = OpenAI()

def formatar_historico(historico):
    return "\n".join(
        f"{msg['origem'].capitalize()}: {msg['mensagem']}" for msg in historico
    )

def sintetizar_historico(historico) -> Dict:
    prompt = f"""
    Você é um analista de comportamento e contexto conversacional do Copiloto IA.

    Abaixo está o histórico de mensagens trocadas entre o usuário e o sistema:

    {formatar_historico(historico)}

    Com base nesse histórico, sua missão é:

    1. 📌 Gerar um resumo **emocional e situacional atual** do usuário, considerando cansaço, clareza, frustração, tarefas pendentes e outros sinais emocionais relevantes.

    2. 🔍 Analisar **a última mensagem do usuário** e decidir se a conversa ainda está **em andamento**, ou seja, se há expectativa de resposta do sistema. Use os critérios abaixo:

    ---

    ### Critérios para considerar que a conversa AINDA ESTÁ EM ANDAMENTO:
    - A última mensagem é uma pergunta (direta ou indireta).
    - Contém dúvidas não resolvidas ou frases como "o que você acha?", "e agora?", "me ajuda com isso", "devo continuar por onde?".
    - Há uma ação pendente esperada por parte do sistema.
    - Há continuidade emocional perceptível (exemplo: desabafo recente, pedido de apoio emocional, etc.).

    ---

    ### Critérios para considerar que a conversa FOI ENCERRADA:
    - O usuário apenas respondeu “obrigado”, “valeu”, “tá bom” ou algo similar.
    - A última mensagem é uma confirmação de encerramento ou ausência de interação.
    - O sistema já concluiu a entrega proposta (ex: artigo entregue, objetivo finalizado).

    ---

    Com base nisso, responda com um JSON contendo:

    ```json
    {{
    "resumo": "SEU RESUMO EMOCIONAL E SITUACIONAL AQUI",
    "conversa_em_andamento": true OU false
    }}
    ```

    ⚠️ NÃO invente, NÃO seja evasivo. Seja direto, prático e empático.

    Linguagem: português-BR.
    Formato da saída: apenas o JSON especificado acima.
    """

    response = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4",
        temperature=0.5
    )

    try:
        resposta = json.loads(response.choices[0].message.content)
        return resposta
    except json.JSONDecodeError:
        return {
            "resumo": response.choices[0].message.content,
            "conversa_em_andamento": None
        }

async def salvar_contexto_usuario(wa_id: str, contexto: Dict):
    print('> . . <' * 20)
    novo_valor = {
        "agente_em_conversa": contexto.get("agente_em_conversa"),
        "ultima_interacao": datetime.now(timezone.utc),
    }

    result = users_collection.update_one(
        {"wa_id": wa_id},
        {"$set": novo_valor},
        upsert=True
    )

    print(f"\n💾 Contexto salvo no MongoDB para {wa_id}: {novo_valor}")
    print('>_____>' * 20)


async def carregar_contexto_usuario(wa_id: str) -> Dict:
    usuario = users_collection.find_one({"wa_id": wa_id}) or {}
    comportamento = comportamento_collection.find_one({"wa_id": wa_id})
    historico = list(historico_collection.find({"wa_id": wa_id}).sort("timestamp", -1).limit(20))

    resumo_dados = sintetizar_historico(historico) if historico else {"resumo": None, "conversa_em_andamento": None}

    # Novo trecho: cálculo de tempo da última mensagem
    ultima_msg = historico[0] if historico else None
    minutos_passados = None
    if ultima_msg and "timestamp" in ultima_msg:
        msg_time = ultima_msg["timestamp"]
        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)
        minutos_passados = (datetime.now(timezone.utc) - msg_time).total_seconds() / 60

    # print("\n📦 Contexto carregado:")
    # print(f"- wa_id: {wa_id}")
    print(f"- agente_em_conversa: {usuario.get('agente_em_conversa')}")
    # print(f"- ultima_interacao: {usuario.get('ultima_interacao')}")
    # print(f"- comportamento: {comportamento}")
    # print(f"- historico: {len(historico)} mensagens")
    # if resumo_dados.get("resumo"):
    #     print(f"- resumo (resumo):\n{resumo_dados['resumo']}\n")
    # if minutos_passados is not None:
    #     print(f"- minutos desde última mensagem: {minutos_passados:.2f} min")

    return {
        "wa_id": wa_id,
        "agente_em_conversa": (
            usuario.get("agente_em_conversa") if resumo_dados.get("conversa_em_andamento") else None
        ),
        "ultima_interacao": usuario.get("ultima_interacao"),
        "comportamento": comportamento,
        "historico": historico,
        "resumo": resumo_dados.get("resumo"),
        "conversa_em_andamento": resumo_dados.get("conversa_em_andamento")
    }


if __name__ == "__main__":
    import asyncio
    asyncio.run(carregar_contexto_usuario("353833844418"))
