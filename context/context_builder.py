from typing import Dict
from copiloto_context import CopilotoContext
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import logging
from copiloto_agents import (
    triage_agent,
    tarefa_agent,
    memoria_agent,
    emocional_agent,
    comportamento_agent
)

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

async def montar_contexto_usuario(contexto_base: CopilotoContext, mensagem_atual: str = "") -> CopilotoContext:
    try:
        colecao_mensagens = db["historico"]
        colecao_users = db["users"]
        colecao_objetivos = db["memorias"]
        colecao_comportamento = db["comportamento"]

        wa_id = contexto_base.wa_id
        if not wa_id:
            logger.error("wa_id não fornecido")
            raise ValueError("wa_id é obrigatório")

        wa_id_formatted = f"wa_id:{wa_id}"

        user = colecao_users.find_one({"wa_id": wa_id_formatted})
        nome = user.get("nome", contexto_base.nome) if user else contexto_base.nome

        objetivo = colecao_objetivos.find_one({"wa_id": wa_id_formatted}, sort=[("timestamp", -1)])
        objetivo_dict = {"descricao": objetivo["descricao"]} if objetivo and objetivo.get("descricao") else None
        objetivo_da_semana = objetivo.get("descricao", contexto_base.objetivo_da_semana) if objetivo else contexto_base.objetivo_da_semana

        comportamento = colecao_comportamento.find_one({"wa_id": wa_id_formatted}, sort=[("timestamp", -1)])
        estilo_produtivo = comportamento.get("estilo_produtivo", contexto_base.estilo_produtivo) if comportamento else contexto_base.estilo_produtivo
        emocional = comportamento.get("emocao", contexto_base.emocional) if comportamento else contexto_base.emocional
        comportamento_dict = comportamento if comportamento else None

        historico_cursor = colecao_mensagens.find({"wa_id": wa_id_formatted}).sort("timestamp", -1).limit(10)
        historico = [
            {
                "mensagem": msg.get("mensagem", msg.get("conteudo", "")),
                "tipo": msg.get("origem", "desconhecido")
            }
            for msg in historico_cursor if msg.get("mensagem") or msg.get("conteudo")
        ][::-1]

        contexto_atualizado = CopilotoContext(
            wa_id=wa_id,
            nome=nome or "Usuário",
            objetivo_da_semana=objetivo_da_semana,
            estilo_produtivo=estilo_produtivo,
            emocional=emocional,
            comportamento=comportamento_dict,
            objetivo=objetivo_dict,
            historico=historico + ([{"mensagem": mensagem_atual, "tipo": "usuário"}] if mensagem_atual else [])
        )

        logger.info(f"Contexto montado com sucesso para wa_id: {wa_id}")
        return contexto_atualizado

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

# Função principal de processamento
async def processar_mensagem_usuario(mensagem: str, wa_id: str) -> Dict:
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

        contexto = await montar_contexto_usuario(contexto_base, mensagem)
        input_context = montar_input_context(contexto)

        triage_result = await triage_agent.process(mensagem, input_context)
        logger.info(f"Resultado do triage: {triage_result}")

        agentes = {
            "Organizador de Tarefas": tarefa_agent,
            "Memória Viva": memoria_agent,
            "Suporte Emocional": emocional_agent,
            "Analisador de Comportamento": comportamento_agent
        }

        resultados = []

        if isinstance(triage_result, dict):
            triage_result = triage_result.get("result", "transfer_to_Analisador de Comportamento")

        if isinstance(triage_result, str):
            if "\n" in triage_result:
                for linha in triage_result.strip().split("\n"):
                    if ":" in linha:
                        transfer, parte_mensagem = linha.split(":", 1)
                        agente_nome = transfer.replace("transfer_to_", "").strip()
                        parte_mensagem = parte_mensagem.strip()
                        if agente_nome in agentes:
                            agente = agentes[agente_nome]
                            resultado = await agente.process(parte_mensagem, input_context)
                            resultados.append({"agente": agente_nome, "resultado": resultado})
                        else:
                            logger.warning(f"Agente '{agente_nome}' não encontrado para mensagem: {parte_mensagem}")
                            resultado = await comportamento_agent.process(parte_mensagem, input_context)
                            resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})
            elif triage_result.startswith("transfer_to_"):
                agente_nome = triage_result.replace("transfer_to_", "").strip()
                if agente_nome in agentes:
                    agente = agentes[agente_nome]
                    resultado = await agente.process(mensagem, input_context)
                    resultados.append({"agente": agente_nome, "resultado": resultado})
                else:
                    logger.warning(f"Agente '{agente_nome}' não encontrado")
                    resultado = await comportamento_agent.process(mensagem, input_context)
                    resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})
            elif triage_result.startswith("Nenhum:"):
                resultado = await comportamento_agent.process(mensagem, input_context)
                resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})

        return {"status": "success", "resultados": resultados}

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        return {"status": "error", "message": str(e)}
