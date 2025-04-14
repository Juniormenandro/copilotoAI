from typing import Dict
from copiloto_context import CopilotoContext
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from agents import Runner
import logging
from comportamento_agent import comportamento_agent

# Configuração do logging
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Conexão com MongoDB
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise EnvironmentError("MONGO_URI não configurado no .env")
client = MongoClient(mongo_uri)
db = client.copilotoAI

def consultar_historico_com_agente(wa_id, agente_nome, limite=10):
    mensagens = db.historico.find({
        "wa_id": wa_id,
        "origem": {"$in": ["usuario", agente_nome]}
    }).sort("timestamp", -1).limit(limite)
    return list(mensagens)[::-1]

async def montar_contexto_usuario(contexto_base: CopilotoContext, mensagem_atual: str = "", agente_destino: str = None) -> CopilotoContext:
    try:
        colecao_users = db["users"]
        colecao_objetivos = db["memorias"]
        colecao_comportamento = db["comportamento"]

        wa_id = contexto_base.wa_id
        if not wa_id:
            logger.error("wa_id não fornecido")
            raise ValueError("wa_id é obrigatório")

        user = colecao_users.find_one({"wa_id": wa_id})
        nome = user.get("nome", contexto_base.nome) if user else contexto_base.nome

        objetivo = colecao_objetivos.find_one({"wa_id": wa_id}, sort=[("timestamp", -1)])
        objetivo_dict = {"descricao": objetivo["descricao"]} if objetivo and objetivo.get("descricao") else None
        objetivo_da_semana = objetivo.get("descricao", contexto_base.objetivo_da_semana) if objetivo else contexto_base.objetivo_da_semana

        comportamento = colecao_comportamento.find_one({"wa_id": wa_id}, sort=[("timestamp", -1)])
        estilo_produtivo = comportamento.get("estilo_produtivo", contexto_base.estilo_produtivo) if comportamento else contexto_base.estilo_produtivo
        emocional = comportamento.get("emocao", contexto_base.emocional) if comportamento else contexto_base.emocional
        comportamento_dict = comportamento if comportamento else None

        if agente_destino:
            historico = consultar_historico_com_agente(wa_id, agente_destino)
        else:
            historico = []

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
        logger.error(f"Erro ao montar contexto: {str(e)}")
        return contexto_base

def montar_input_context(contexto: CopilotoContext) -> dict:
    try:
        return {
            "wa_id": contexto.wa_id or "",
            "nome": contexto.nome or "Usuário",
            "objetivo_da_semana": contexto.objetivo_da_semana or "",
            "estilo_produtivo": contexto.estilo_produtivo or "",
            "emocional": contexto.emocional or "",
            "comportamento": contexto.comportamento or {},
            "objetivo": contexto.objetivo or {},
            "historico": contexto.historico or []
        }
    except Exception as e:
        logger.error(f"Erro ao montar input context: {str(e)}")
        return {}

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
        triage_result = await Runner.run(comportamento_agent, input=mensagem, context=input_context)
        logger.info(f"Resultado do triage: {triage_result}")
        print(f"Resultado do triage: {triage_result}")
        return {"status": "success", "resultados": triage_result}

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return {"status": "error", "message": str(e)}