from typing import Dict, List
from copiloto_context import CopilotoContext
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from agents import Runner
import logging
from comportamento_agent import comportamento_agent
from db.comportamento import salvar_comportamento

# Setup de logging
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise EnvironmentError("MONGO_URI não configurado no .env")
client = MongoClient(mongo_uri)
db = client.copilotoAI

# Consulta o histórico mais relevante para o agente específico
def consultar_historico_com_agente(wa_id, agente_nome, limite=10):
    mensagens = db.historico.find({
        "wa_id": wa_id,
        "origem": {"$in": ["usuario", agente_nome]}
    }).sort("timestamp", -1).limit(limite)
    return list(mensagens)[::-1]

# Detecta padrões emocionais críticos
def detectar_padroes_emocionais(historico: List[Dict]) -> str:
    mensagens_usuario = [msg["mensagem"].lower() for msg in historico if msg["tipo"] == "usuario"]
    if len(mensagens_usuario) < 3:
        return ""

    repeticoes = {}
    palavras_chave = ["cansaço", "sem foco", "travado", "procrastinei", "não consigo", "de novo", "não avancei"]

    for mensagem in mensagens_usuario:
        for palavra in palavras_chave:
            if palavra in mensagem:
                repeticoes[palavra] = repeticoes.get(palavra, 0) + 1

    palavras_repetidas = [k for k, v in repeticoes.items() if v >= 2]

    if palavras_repetidas:
        return f"⚠️ Alerta de repetição emocional detectado com os padrões: {', '.join(palavras_repetidas)}"

    return ""

# Monta o contexto estruturado do usuário
async def montar_contexto_usuario(contexto_base: CopilotoContext, mensagem_atual: str = "", agente_destino: str = None) -> CopilotoContext:
    try:
        wa_id = contexto_base.wa_id
        if not wa_id:
            logger.error("❌ wa_id não fornecido.")
            raise ValueError("wa_id é obrigatório")

        user = db["users"].find_one({"wa_id": wa_id})
        nome = user.get("nome") if user else contexto_base.nome

        objetivo = db["memorias"].find_one({"wa_id": wa_id}, sort=[("timestamp", -1)])
        objetivo_dict = {"descricao": objetivo.get("descricao")} if objetivo and objetivo.get("descricao") else None
        objetivo_da_semana = objetivo.get("descricao", contexto_base.objetivo_da_semana) if objetivo else contexto_base.objetivo_da_semana

        comportamento = db["comportamento"].find_one({"wa_id": wa_id}, sort=[("timestamp", -1)])
        estilo_produtivo = comportamento.get("estilo_produtivo") if comportamento else contexto_base.estilo_produtivo
        emocional = comportamento.get("emocao") if comportamento else contexto_base.emocional
        comportamento_dict = comportamento if comportamento else {
            "tom_ideal": "leve, empático e direto",
            "gatilhos": [],
            "estilo": "natural",
            "foco": "clareza emocional"
        }

        historico = consultar_historico_com_agente(wa_id, agente_destino) if agente_destino else []

        historico_formatado = [
            {"mensagem": msg.get("mensagem", msg.get("conteudo", "")), "tipo": msg.get("origem", "desconhecido")}
            for msg in historico
        ] + ([{"mensagem": mensagem_atual, "tipo": "usuário"}] if mensagem_atual else [])

        return CopilotoContext(
            wa_id=wa_id,
            nome=nome or "Usuário",
            objetivo_da_semana=objetivo_da_semana,
            estilo_produtivo=estilo_produtivo,
            emocional=emocional,
            comportamento=comportamento_dict,
            objetivo=objetivo_dict,
            historico=historico_formatado
        )

    except Exception as e:
        logger.error(f"🚨 Erro ao montar contexto do usuário: {str(e)}")
        return contexto_base

# Converte contexto em dicionário com alerta emocional
def montar_input_context(contexto: CopilotoContext) -> dict:
    try:
        alerta_emocional = detectar_padroes_emocionais(contexto.historico or [])
        return {
            "wa_id": contexto.wa_id or "",
            "nome": contexto.nome or "Usuário",
            "objetivo_da_semana": contexto.objetivo_da_semana or "",
            "estilo_produtivo": contexto.estilo_produtivo or "",
            "emocional": contexto.emocional or "",
            "comportamento": contexto.comportamento or {},
            "objetivo": contexto.objetivo or {},
            "historico": contexto.historico or [],
            "alerta_emocional": alerta_emocional or ""
        }
    except Exception as e:
        logger.error(f"⚠️ Erro ao montar input context: {str(e)}")
        return {}

# Função principal de processamento para esse agente
async def processar_mensagem_usuario(mensagem: str, wa_id: str, agente_destino: str = "emocional_comportamental_agent") -> Dict:
    try:
        contexto_base = CopilotoContext(
            wa_id=wa_id,
            nome="Usuário",
            objetivo_da_semana="",
            estilo_produtivo="",
            emocional="",
            comportamento=None,
            objetivo=None,
            historico=[]
        )

        contexto = await montar_contexto_usuario(contexto_base, mensagem, agente_destino)
        input_context = montar_input_context(contexto)
        resultado = await Runner.run(comportamento_agent, input=mensagem, context=input_context)

        logger.info(f"🧠 Resultado do agente de comportamento: {resultado.final_output}")
        salvar_comportamento(wa_id, resultado.final_output.model_dump())

        return {"status": "success", "resultados": resultado.final_output}

    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {str(e)}")
        return {"status": "error", "message": str(e)}
