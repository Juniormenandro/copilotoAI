from flask import Flask, request, Response, render_template
import os
import requests
from dotenv import load_dotenv
import time
import asyncio
from agents import Runner
from pymongo import MongoClient
from datetime import datetime
from z_copiloto_agents import get_copiloto_response_com_agente
from context.context_builder import montar_contexto_usuario
from db.users import salvar_ou_atualizar_usuario
from db.memorias import salvar_memoria, consultar_objetivo_da_semana, ja_foi_acolhido, registrar_acolhimento
from db.tarefas import registrar_tarefa, listar_tarefas
from db.comportamento import consultar_comportamento
from db.historico import salvar_mensagem
from core.mensageiro import enviar_resposta
from comportamento_agent import executor_comportamento
from copiloto_context import CopilotoContext
from jobs.scheduler import iniciar_agendador

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.copilotoAI

def montar_input_context(wa_id: str) -> dict:
    """Monta o contexto completo do usuário com base nas collections."""
    
    # Coleta o perfil do usuário
    user_data = db.users.find_one({"wa_id": wa_id})
    
    # Coleta o perfil emocional mais recente
    emocional = db.comportamento.find_one({"wa_id": wa_id}, sort=[("timestamp", -1)])
    
    # Coleta objetivo ativo da semana (se houver)
    objetivo = db.objetivos.find_one({"wa_id": wa_id, "ativo": True})
    
    # Coleta as 5 últimas mensagens
    historico_cursor = db.historico.find({"wa_id": wa_id}).sort("timestamp", -1).limit(5)
    historico = [
        {
            "mensagem": doc.get("mensagem"),
            "origem": doc.get("origem"),
            "data": doc.get("timestamp")
        }
        for doc in historico_cursor
    ]
    
    # Monta o dicionário de contexto
    return {
        "wa_id": wa_id,
        "nome": user_data.get("nome") if user_data else None,
        "linguagem_preferida": emocional.get("linguagem_preferida") if emocional else None,
        "tom_recomendado": emocional.get("tom_recomendado") if emocional else None,
        "estado_emocional": emocional.get("emocao") if emocional else None,
        "personalidade": emocional.get("personalidade") if emocional else None,
        "desejos": emocional.get("desejos") if emocional else None,
        "dores": emocional.get("dores") if emocional else None,
        "objetivo_da_semana": objetivo.get("descricao") if objetivo else None,
        "historico_recente": historico
    }

# Teste local (você pode usar isso no seu main)
# contexto = montar_input_context("353833844418")
# print(contexto)







@app.route("/")
def index():
    return render_template('index.html')


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificado com sucesso!")
        return challenge, 200
    else:
        print("❌ Erro na verificação do Webhook")
        return "Erro de verificação", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    try:
        mensagens = data["entry"][0]["changes"][0]["value"]["messages"]
    except (KeyError, IndexError):
        return "⚠️ Nenhuma mensagem recebida", 200

    for mensagem in mensagens:
        if mensagem["type"] == "text":
            user_message = mensagem["text"]["body"]
            wa_id = mensagem["from"]
            nome = data["entry"][0]["changes"][0]["value"].get("contacts", [{}])[0].get("profile", {}).get("name", "amigo")

            async def rodar_tudo():
                salvar_ou_atualizar_usuario(wa_id, nome)

                # 🔹 Salvar mensagem recebida
                contexto = CopilotoContext(wa_id=wa_id, nome=nome)
                salvar_mensagem(wa_id, "usuario", user_message)
                print(contexto)
                # 🔹 Rodar resposta principal do Copiloto IA
                resposta = await get_copiloto_response_com_agente(user_message, wa_id)

                # 🔹 Salvar resposta do Copiloto
                salvar_mensagem(wa_id, "copiloto", resposta)

                # 🔹 Enviar resposta pelo WhatsApp
                enviar_resposta(wa_id, resposta)

                # 🔹 Executar o agente de comportamento
                await executor_comportamento(user_message, CopilotoContext(wa_id=wa_id, nome=nome))

            asyncio.run(rodar_tudo())

    return Response(status=200)


iniciar_agendador()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)