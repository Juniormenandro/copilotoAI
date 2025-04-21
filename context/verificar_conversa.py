import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents import Runner # type: ignore
from datetime import datetime, timezone
from .sintetizar import carregar_contexto_usuario, salvar_contexto_usuario
from datetime import datetime, timezone
from pymongo import MongoClient # type: ignore
from dotenv import load_dotenv # type: ignore
from agentes_copiloto.organizador import organizador_memoria_agent
from agentes_copiloto.optimum_writer import optimum_writer_agent
from agentes_copiloto.emocional import emocional_comportamental_agent
from agentes_copiloto.estrategista import estrategista_intelectual_agent
from agentes_copiloto.solucoes_ai import solucoes_ai_em_demanda_agent
from agentes_copiloto.spinsalinng import spinselling_agent
 
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["copilotoAI"]
users_collection = db["users"]
historico_collection = db["historico"]


# Mapeamento nome -> agente real
AGENTES_REGISTRADOS = {
    "organizador_agent": organizador_memoria_agent,
    "optimum_writer_agent": optimum_writer_agent,
    "emocional_agent": emocional_comportamental_agent,
    "estrategista_intelectual_agent": estrategista_intelectual_agent,
    "solucoes_ai_em_demanda_agent": solucoes_ai_em_demanda_agent,
    "spinselling_agent": spinselling_agent,
}

#---------- alimenta o contexto para os agentes ---------------------------------------
async def carregar_contexto_simples(wa_id: str) -> dict:
    usuario = users_collection.find_one({"wa_id": wa_id}) or {}
     # 🧹 Buscar apenas mensagens do usuário (últimas 5)
    historico_bruto = list(
        historico_collection.find(
            {"wa_id": wa_id, "origem": "usuario"}
        ).sort("timestamp", -1).limit(6)
    )
    historico = sorted(historico_bruto, key=lambda x: x["timestamp"])  # do mais antigo pro mais recente
    minutos_passados = None
    if historico and "timestamp" in historico[-1]:
        msg_time = historico[-1]["timestamp"]
        if msg_time.tzinfo is None:
            msg_time = msg_time.replace(tzinfo=timezone.utc)
        minutos_passados = (datetime.now(timezone.utc) - msg_time).total_seconds() / 60

    return {
        "wa_id": wa_id,
        "agente_em_conversa": usuario.get("agente_em_conversa"),
        "conversa_em_andamento": usuario.get("conversa_em_andamento"),
        "ultima_interacao": usuario.get("ultima_interacao"),
        "historico": historico,
        "minutos_desde_ultima_mensagem": minutos_passados
    }



#------------ verifica se a conversa esta em andamento -----------------#
async def verificar_necessidade_resumo(wa_id: str, mensagem) -> dict:
    print(f"\n_🔎 _ Verificando se precisa resumir para {wa_id}...")
    # 1. Busca dados atuais do usuário
    usuario = users_collection.find_one({"wa_id": wa_id}) or {}
    ultima_interacao = usuario.get("ultima_interacao")
    agente_em_conversa = usuario.get("agente_em_conversa")
    conversa_em_andamento = usuario.get("conversa_em_andamento")
    print(f"\n_🔎 _verificar_necessidade_resumo = {agente_em_conversa}")
    print(f"\n_🔎 _verificar_necessidade_resumo = {conversa_em_andamento}")
    minutos_inativo = None
    if ultima_interacao:
        if ultima_interacao.tzinfo is None:
            ultima_interacao = ultima_interacao.replace(tzinfo=timezone.utc)
        agora = datetime.now(timezone.utc)
        minutos_inativo = (agora - ultima_interacao).total_seconds() / 60

    # 2. Decide qual contexto carregar
    if minutos_inativo is not None and minutos_inativo > 120:
        print(f"_⏱️ _ Inativo há {minutos_inativo:.2f} minutos — usando contexto completo.")
        contexto_simples = await carregar_contexto_simples(wa_id)
        historico = contexto_simples["historico"]
        contexto = await carregar_contexto_usuario(wa_id, historico)
        return contexto

    elif conversa_em_andamento is True and agente_em_conversa:
        print(f"_🔁_ Conversa ainda em andamento — redirecionando para agente ativo: {agente_em_conversa}")
        contexto_simples = await carregar_contexto_simples(wa_id)
        agente = AGENTES_REGISTRADOS.get(agente_em_conversa)
        if not agente:
            historico = contexto_simples["historico"]
            contexto = await carregar_contexto_usuario(wa_id, historico)
            print(f"_🔁_📍_⚠️ Agente '{agente_em_conversa}' não encontrado. Indo para fallback da triagem.")
            return {"contexto": contexto, "mensagem": mensagem}
        print("_🧪_ Antes de alterar:", contexto_simples.get("conversa_em_andamento"))
        contexto_simples["conversa_em_andamento"] = False
        contexto_simples["agente_em_conversa"] = ""
        print("_🧪_ Depois de alterar:", contexto_simples.get("conversa_em_andamento", contexto_simples.get("agente_em_conversa")))
        resposta = await Runner.run(
            agente,
            input=mensagem,
            context=contexto_simples
        )
        #print(f"_🔁_📤 salvando Resposta do agente = {contexto}")
        await salvar_contexto_usuario(wa_id, contexto_simples)
        print("_🔁_======== Fim da lógica do agent direto ===========🔁 ")
        return resposta.final_output
    else:
        print(f"_🔁_📍_ Conversa inativa ou encerrada — redirecionando para triagem.")
        contexto_simples = await carregar_contexto_simples(wa_id)
        historico = contexto_simples["historico"]
        contexto = await carregar_contexto_usuario(wa_id, historico)
        agente = AGENTES_REGISTRADOS.get(agente_em_conversa)
        return {"contexto": contexto, "mensagem": mensagem}

