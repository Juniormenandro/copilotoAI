# app.py 
from flask import Flask, request, Response, render_template # type: ignore
from dotenv import load_dotenv # type: ignore
from pymongo import MongoClient # type: ignore
from db.users import salvar_ou_atualizar_usuario
from db.historico import salvar_mensagem
from core.mensageiro import enviar_resposta
from jobs.scheduler import iniciar_agendador
from utils.transcrever_audio import transcrever_audio_do_whatsapp
from context.sintetizar import salvar_contexto_usuario
from context.verificar_conversa import verificar_necessidade_resumo
from agentes_copiloto.triagem import triage_copiloto_agent
from agents import Runner # type: ignore
import tempfile
import requests # type: ignore
import asyncio
import os

load_dotenv()
app = Flask(__name__)

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
        if not mensagens:
          #  print("⚠️ Nenhuma mensagem recebida")
            return Response(status=200)
    except (KeyError, IndexError):
       # print("⚠️ Erro no formato da mensagem")
        return Response(status=200)

    for mensagem in mensagens:
        message_id = mensagem.get("id")
        if db.historico.find_one({"message_id": message_id}):
           # print("⚠️ Mensagem já processada. Ignorando.")
            continue

        wa_id = mensagem["from"]
        nome = data["entry"][0]["changes"][0]["value"].get("contacts", [{}])[0].get("profile", {}).get("name", "amigo")
        
        if mensagem["type"] == "text":
            user_message = mensagem["text"]["body"]
            salvar_ou_atualizar_usuario(wa_id, user_message)
            salvar_mensagem(wa_id, "usuario", user_message)
           # print(f"📥 Mensagem recebida: '{user_message}' de {nome} ({wa_id})")
            
            try:
               # print("================ TESTE: TRIAGEM INTELIGENTE =================")
                contexto = asyncio.run(verificar_necessidade_resumo(wa_id, user_message ))
                if isinstance(contexto, str):
                    resposta = contexto.strip()
                   # print(f"_❓__❓_⚡ Resposta direta do agente ativo: {resposta}")
                    salvar_mensagem(wa_id, "copiloto", resposta)
                    enviar_resposta(wa_id, resposta)
                  #  print("================ AGENTE DIRETO — FIM =================")
                    return Response(status=200)

                resposta = asyncio.run(Runner.run(triage_copiloto_agent, input=user_message, context=contexto))
                # asyncio.run(salvar_contexto_usuario(wa_id, contexto))
                resposta_texto = getattr(resposta, "final_output", str(resposta))
               # print(f"✅ Resultado extraído com .final_output: {resposta_texto}")
                salvar_mensagem(wa_id, "copiloto", resposta_texto)
                enviar_resposta(wa_id, resposta_texto)
              #  print("================ TESTE: TRIAGEM INTELIGENTE FIM=================")
                return Response(status=200)
            except Exception as e:
                print("❌ Erro ao processar a mensagem:", e)
        
        elif mensagem["type"] == "audio":
            try:
                audio_id = mensagem["audio"]["id"]
                # Primeiro, obtém URL final para download
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
                
                salvar_ou_atualizar_usuario(wa_id, user_message)
                salvar_mensagem(wa_id, "usuario", user_message)
              #  print(f"🎙️ Transcrição do áudio: '{user_message}' de {nome} ({wa_id})")

                try:
                  #  print("================ TESTE: TRIAGEM INTELIGENTE =================")
                    contexto = asyncio.run(verificar_necessidade_resumo(wa_id, user_message))
                    if isinstance(contexto, str):
                        resposta = contexto.strip()
                      #  print(f"_❓__❓_⚡ Resposta direta do agente ativo: {resposta}")
                        salvar_mensagem(wa_id, "copiloto", resposta)
                        enviar_resposta(wa_id, resposta)
                     #   print("================ AGENTE DIRETO — FIM =================")
                        return Response(status=200)

                    resposta = asyncio.run(Runner.run(triage_copiloto_agent, input=user_message, context=contexto))
                    resposta_texto = resposta.final_output.strip()
                    asyncio.run(salvar_contexto_usuario(wa_id, contexto))
                    salvar_mensagem(wa_id, "copiloto", resposta_texto)
                    enviar_resposta(wa_id, resposta_texto)
                  #  print("================ TESTE: TRIAGEM INTELIGENTE FIM=================")
                    return Response(status=200)
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
