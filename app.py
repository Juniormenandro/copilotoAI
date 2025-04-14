# test_main.py
from flask import Flask, request, Response, render_template
from dotenv import load_dotenv
from pymongo import MongoClient
from db.users import salvar_ou_atualizar_usuario
from db.historico import salvar_mensagem, consultar_historico
from db.comportamento import consultar_comportamento
from core.mensageiro import enviar_resposta
from jobs.scheduler import iniciar_agendador
from copiloto_agents import triage_agent
from context.context_builder import processar_mensagem_usuario
from agents import Runner
import asyncio
import os

load_dotenv()
app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.copilotoAI

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
        message_id = mensagem.get("id")
        if db.historico.find_one({"message_id": message_id}):
            print("⚠️ Mensagem já processada. Ignorando.")
            return Response(status=200)

        if mensagem["type"] == "text":
            user_message = mensagem["text"]["body"]
            wa_id = mensagem["from"]
            nome = data["entry"][0]["changes"][0]["value"].get("contacts", [{}])[0].get("profile", {}).get("name", "amigo")
            salvar_ou_atualizar_usuario(wa_id, user_message)
            salvar_mensagem(wa_id, "usuario", user_message)
            asyncio.run(processar_mensagem_usuario(user_message, wa_id))
            print(f"📥 Mensagem recebida: '{user_message}' de {nome} ({wa_id})")
        
        try:
            print("🚀 Executando Runner com o triage_agent...")
            print("🧠 Agente:", triage_agent.name)
            print("🛠️ Tools:", asyncio.run(triage_agent.get_all_tools()))
            comportamento = consultar_comportamento(wa_id)
            historico = consultar_historico(wa_id)
            contexto = {
                "wa_id": wa_id,
                "comportamento": comportamento,
                "historico" : historico
            }
            print("🎯 Resultado bruto:", contexto)
            resposta = asyncio.run(
                Runner.run(
                    triage_agent,
                    input=user_message,
                    context=contexto
                )
            )

            resposta_texto = resposta.output if hasattr(resposta, "output") else str(resposta)
            #print("🎯 Resultado bruto:", resposta_texto)

            salvar_mensagem(wa_id, "copiloto", resposta_texto)
            enviar_resposta(wa_id, resposta_texto)

        except Exception as e:
            print("❌ Erro ao processar a mensagem:", e)
    return Response(status=200)
iniciar_agendador()
if __name__ == "__main__": 
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
