# app.py 
from flask import Flask, request, Response, render_template, jsonify # type: ignore
from dotenv import load_dotenv # type: ignore
from pymongo import MongoClient # type: ignore
from db.users import salvar_ou_atualizar_usuario
from db.historico import salvar_mensagem
from core.mensageiro import enviar_resposta
from jobs.scheduler import iniciar_agendador
from utils.transcrever_audio import transcrever_audio_do_whatsapp
from context.sintetizar import salvar_contexto_usuario
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
            #print(f"📥 Mensagem recebida: '{user_message}' de {nome} ({wa_id})")
            
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


















from agents import Agent, handoff #type: ignore
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX #type: ignore
from .organizador import organizador_memoria_agent
from .optimum_writer import optimum_writer_agent
from .emocional import emocional_comportamental_agent
from .estrategista import estrategista_intelectual_agent
from .solucoes_ai import solucoes_ai_em_demanda_agent
from .spinsalinng import spinselling_agent

triage_copiloto_agent = Agent(
    name="triage_copiloto_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

    Você é o agente de triagem invisível do Copiloto IA. Seu papel é ler e entender profundamente cada mensagem do usuário, consultando o contexto, o histórico e o estado emocional atual. Com base nisso, você deve encaminhar a mensagem ao agente mais adequado para continuar a conversa. Você **nunca responde diretamente ao usuário** — apenas redireciona silenciosamente para o agente certo com o input e o contexto corretos.

    ⚠️ REGRAS IMPORTANTES:
    - SEMPRE use `context['historico']` como base da resposta.
    - Nunca responda ao usuário.
    - ÚNICO formato PERMITIDO DE RESPOSTA: `transfer_to_<agent_name>`.

    ⚙️ FUNCIONAMENTO:
    - Utilize o `context['historico']` para identificar em qual passo o usuário está e, assim, determinar o encaminhamento correto ao agente.
    - Não troque de agente sem necessidade.

    🎯 OBJETIVO:
    Roteie com precisão cada mensagem recebida para o agente especializado correto, garantindo que a continuidade da conversa seja mantida e que o tom, o foco e as necessidades do usuário sejam respeitados.

    🔑 REGRAS DE OURO:
    1. Nunca responda ao usuário.
    2. Utilize todo o contexto disponível: comportamento, resumo emocional, agente anterior, tarefas em andamento, memórias.
    3. Se o usuário demonstrar cansaço, repetição ou confusão, direcione para `transfer_to_emocional_comportamental_agent`.
    4. Não altere o agente atual sem uma boa razão.

    🧭 Tabela de Roteamento:
    | Situação Identificada                                             | Direcionar Para                                    |
    |------------------------------------------------------------------|----------------------------------------------------|
    | Organização, tarefas, rotina, lembretes                          | `transfer_to_organizador_memoria_agent`            |
    | Dúvidas sobre metas, clareza mental ou sobrecarga emocional      | `transfer_to_emocional_comportamental_agent`       |
    | Criação de textos, roteiros, conteúdos ou ideias                 | `transfer_to_optimum_writer_agent`                 |
    | Perguntas sobre IA, automação                                    | `transfer_to_solucoes_ai_em_demanda_agent`         |
    | Reflexões complexas, estratégias de negócio, visão a longo prazo  | `transfer_to_estrategista_intelectual_agent`       |
    | Vendas, ajuda para vender, técnicas de SPIN Selling              | `transfer_to_spinselling_agent`                    |
    | Agradecimentos, despedidas ou respostas curtas                   | mantenha o agente atual                            |
    | Silêncio, hesitação ou confusão                                  | `transfer_to_emocional_comportamental_agent`       |
    | **Fallback (quando não se encaixar em nenhum caso acima)**       | `transfer_to_estrategista_intelectual_agent`       |

    🔍 Checklist de Decisão:
    1. O assunto da nova mensagem é diferente do anterior?  
    2. O agente atual ainda é o mais apropriado?  
    3. A troca vai gerar mais clareza e valor para o usuário?  
    4. O contexto indica mudança emocional ou de foco?  

    🧠 Exemplo de Uso:
    - Mensagem: “Eu só queria colocar a cabeça no lugar e seguir com calma.”  
    - Ação: `transfer_to_emocional_comportamental_agent`  
    
    

    """,
     handoffs=[
        handoff(organizador_memoria_agent),
        handoff(emocional_comportamental_agent),
        handoff(estrategista_intelectual_agent),
        handoff(optimum_writer_agent),
        handoff(solucoes_ai_em_demanda_agent),
        handoff(spinselling_agent),
    ]
)
