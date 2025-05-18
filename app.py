# app.py 
from flask import Flask, request, Response, render_template, jsonify # type: ignore
from dotenv import load_dotenv # type: ignore
from pymongo import MongoClient # type: ignore
from db.users import salvar_ou_atualizar_usuario
from db.historico import salvar_mensagem
from core.mensageiro import enviar_resposta
from jobs.scheduler import iniciar_agendador
from utils.transcrever_audio import transcrever_audio_do_whatsapp
from context.verificar_conversa import verificar_necessidade_resumo
from Agent_copiloto.triagem import triage_copiloto_agent
from Agent_serviflex.Agent_principal import Agent_principal
from agents import Runner # type: ignore
import tempfile
import requests # type: ignore
import asyncio
import os
from flask_cors import CORS # type: ignore
from openai import OpenAI # type: ignore


load_dotenv()
app = Flask(__name__)
CORS(app)
client = OpenAI()


VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["copilotoAI"]
users_collection = db["users"]

@app.route("/")
def index():
    return render_template('index.html')

# Simula memória de curto prazo com histórico simples por sessão
def formatar_historico_para_prompt(history):
    mensagens_formatadas = []
    for msg in history:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            mensagens_formatadas.append(f"Usuário: {content}")
        elif role == "assistant":
            mensagens_formatadas.append(f"Assistente: {content}")
    return "\n".join(mensagens_formatadas)



@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    history = data.get('history', [])
    if not message:
        return jsonify({'error': 'Mensagem vazia'}), 400
    formatted_history = formatar_historico_para_prompt(history)
    entrada_formatada = f"{formatted_history}\nUsuário: {message}"
    try:
        result = asyncio.run(Runner.run(
            Agent_principal,
            input=entrada_formatada,
        ))
        reply = getattr(result, "final_output", str(result))
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
        mensagens = data["entry"][0]["changes"][0]["value"].get("messages")
    except (KeyError, IndexError):
        return Response(status=200)
    if not mensagens:
        return Response(status=200)
    for mensagem in mensagens:
        message_id = mensagem.get("id")
        if db.historico.find_one({"message_id": message_id}):
            continue
        wa_id = mensagem["from"]
        nome = data["entry"][0]["changes"][0]["value"].get("contacts", [{}])[0].get("profile", {}).get("name", "amigo")
        if mensagem["type"] == "text":
            user_message = mensagem["text"]["body"]
            salvar_ou_atualizar_usuario(wa_id, nome)
            salvar_mensagem(wa_id, "usuario", user_message)
            print(f"📥 Mensagem recebida: '{user_message}' de {nome} ({wa_id})")
            try:
                res = asyncio.run(verificar_necessidade_resumo(wa_id, user_message ))
                if isinstance(res, str):
                    resposta = res.strip()
                    salvar_mensagem(wa_id, "copiloto", resposta)
                    enviar_resposta(wa_id, resposta)
                    return Response(status=200)
                else:
                    print("❌ Erro ao processar a retorno no agent:") 
            except Exception as e:
                print("❌ Erro ao processar a mensagem:", e)
        
        elif mensagem["type"] == "audio":
            try:
                audio_id = mensagem["audio"]["id"]
                media_info_url = f"https://graph.facebook.com/v17.0/{audio_id}"
                headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                media_info_resp = requests.get(media_info_url, headers=headers)
                if media_info_resp.status_code != 200:
                    raise Exception("Erro ao obter URL da mídia")
                media_download_url = media_info_resp.json().get("url")
                if not media_download_url:
                    raise Exception("URL de download não encontrada")
                # Agora baixa realmente o arquivo
                audio_response = requests.get(media_download_url, headers=headers)
                if audio_response.status_code != 200:
                    raise Exception("Erro ao baixar o áudio do WhatsApp")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
                    temp_audio.write(audio_response.content)
                    temp_audio_path = temp_audio.name
                user_message = transcrever_audio_do_whatsapp(temp_audio_path)
                os.unlink(temp_audio_path)
                # Salva ou atualizar usuario e salva mensagem nno historico
                salvar_ou_atualizar_usuario(wa_id, nome)
                salvar_mensagem(wa_id, "usuario", user_message)
                print(f"🎙️ Transcrição do áudio: '{user_message}' de {nome} ({wa_id})")
                try:
                    res = asyncio.run(verificar_necessidade_resumo(wa_id, user_message ))
                    if isinstance(res, str):
                        resposta = res.strip()
                        salvar_mensagem(wa_id, "copiloto", resposta)
                        enviar_resposta(wa_id, resposta)
                        return Response(status=200)
                    else:
                        print("❌ Erro ao processar a retorno no agent:") 
                except Exception as e:
                    print("❌ Erro ao processar a mensagem:", e)
                
            except Exception as e:
                print("❌ Erro ao processar áudio:", e)
                user_message = "Não consegui entender o áudio. Pode tentar digitar?"
        
        else:
            print("⚠️ Tipo de mensagem não suportado:", mensagem["type"])
            return Response(status=200)







iniciar_agendador()
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
