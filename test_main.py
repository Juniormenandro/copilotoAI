from flask import Flask, request, Response, render_template
import os
import requests
from dotenv import load_dotenv
import time
import asyncio
from pymongo import MongoClient
from datetime import datetime
#from context.context_builder import processar_mensagem_usuario  # ✅ voltou ao original
from context.context_builder import processar_mensagem_usuario

from copiloto_context import CopilotoContext
from db.users import salvar_ou_atualizar_usuario
from db.memorias import salvar_memoria, consultar_objetivo_da_semana, ja_foi_acolhido, registrar_acolhimento
from db.tarefas import registrar_tarefa, listar_tarefas
from db.comportamento import consultar_comportamento
from db.historico import salvar_mensagem
from core.mensageiro import enviar_resposta
from comportamento_agent import executor_comportamento
from jobs.scheduler import iniciar_agendador

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
        if mensagem["type"] == "text":
            user_message = mensagem["text"]["body"]
            wa_id = mensagem["from"]
            nome = data["entry"][0]["changes"][0]["value"].get("contacts", [{}])[0].get("profile", {}).get("name", "amigo")

            async def rodar_tudo():
                salvar_ou_atualizar_usuario(wa_id, nome)
                salvar_mensagem(wa_id, "usuario", user_message)
                print(f"📥 Mensagem recebida: '{user_message}' de {nome} ({wa_id})")

                resultado = await processar_mensagem_usuario(user_message, wa_id)
                print(f"📋 Resultado do processamento: {resultado}")

                if resultado["status"] == "success":
                    for item in resultado["resultados"]:
                        agente = item["agente"]
                        output = item["resultado"]
                        resposta = output if isinstance(output, str) else output.get("message", str(output))
                        print(f"🧠 Resposta do agente {agente}: {resposta}")

                        if agente in ["Suporte Emocional", "Memória Viva", "Organizador de Tarefas"]:
                            salvar_mensagem(wa_id, "copiloto", resposta)
                            enviar_resposta(wa_id, resposta)
                        elif agente == "Analisador de Comportamento":
                            db.comportamento.insert_one({
                                "wa_id": f"wa_id:{wa_id}",
                                "comportamento": output,
                                "timestamp": int(time.time())
                            })

                    if not any(item["agente"] in ["Suporte Emocional", "Memória Viva", "Organizador de Tarefas"] for item in resultado["resultados"]):
                        resposta_padrao = "Não sei exatamente como te ajudar com isso, mas estou aqui pra tentar!"
                        print(f"📤 Resposta padrão: {resposta_padrao}")
                        salvar_mensagem(wa_id, "copiloto", resposta_padrao)
                        enviar_resposta(wa_id, resposta_padrao)
                else:
                    print(f"❌ Erro no processamento: {resultado['message']}")
                    erro_resposta = "Houve um problema ao processar sua mensagem. Posso tentar de outro jeito?"
                    salvar_mensagem(wa_id, "copiloto", erro_resposta)
                    enviar_resposta(wa_id, erro_resposta)

            asyncio.run(rodar_tudo())

    return Response(status=200)

iniciar_agendador()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
