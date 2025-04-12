from typing import List, Dict, Any
import logging
from copiloto_context import CopilotoContext

# Importando as ferramentas de tools.py
from copiloto_tools import (
    registrar_tarefa_tool,
    listar_tarefas_tool,
    salvar_objetivo_tool,
    consultar_objetivo_tool,
    suporte_emocional_tool,
    detectar_mudanca_de_intencao_tool
)

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name: str, instructions: str, handoff_description: str = "", tools: List = None, handoffs: List = None, output_type: str = None):
        self.name = name
        self.instructions = instructions
        self.handoff_description = handoff_description
        self.tools = tools or []
        self.handoffs = handoffs or []
        self.output_type = output_type

    async def process(self, message: str, context: Dict) -> Any:
        logger.info(f"Agente {self.name} processando mensagem: {message}")
        ctx = CopilotoContext(
            wa_id=context.get("wa_id", ""),
            nome=context.get("nome", "Usuário"),
            objetivo_da_semana=context.get("objetivo_da_semana", ""),
            estilo_produtivo=context.get("estilo_produtivo", ""),
            emocional=context.get("emocional", ""),
            comportamento=context.get("comportamento"),
            objetivo=context.get("objetivo"),
            historico=context.get("historico", [])
        )

        if self.name == "Triage Copiloto":
            message_lower = message.lower()
            if "cansado" in message_lower:
                return "transfer_to_Suporte Emocional:entao mesmo muito cansado\ntransfer_to_Memória Viva:voce sabe me informa quais meus objetivos"
            elif any(keyword in message_lower for keyword in ["tarefa", "tarefas", "lista", "listar"]):
                return "transfer_to_Organizador de Tarefas"
            elif any(keyword in message_lower for keyword in ["objetivo", "objetivos", "meta", "metas"]):
                return "transfer_to_Memória Viva"
            return "transfer_to_Analisador de Comportamento"
        elif self.name == "Suporte Emocional":
            estado = "cansado" if "cansado" in message.lower() else "neutro"
            return await suporte_emocional_tool(ctx, estado)
        elif self.name == "Memória Viva":
            message_lower = message.lower()
            if any(keyword in message_lower for keyword in ["anote", "registre", "salvar"]):
                for keyword in ["anote", "registre", "salvar"]:
                    if keyword in message_lower:
                        objetivo = message.split(keyword, 1)[-1].strip()
                        return await salvar_objetivo_tool(ctx, objetivo)
                return "Desculpe, não consegui entender o objetivo. Pode mandar de novo?"
            return await consultar_objetivo_tool(ctx)
        elif self.name == "Analisador de Comportamento":
            return {
                "personalidade": "Introspectiva",
                "emocao": "Cansaço",
                "estilo_comunicacao": "Informal",
                "dores": "Sobrecarga mental",
                "desejos": "Clareza e descanso",
                "linguagem": "Informal",
                "tom_recomendado": "Empático"
            }
        elif self.name == "Organizador de Tarefas":
            if "registrar" in message.lower():
                descricao = message.split("registrar", 1)[-1].strip()
                return await registrar_tarefa_tool(ctx, descricao)
            return await listar_tarefas_tool(ctx)
        return {"result": f"Processado por {self.name}"}

def handoff(agent):
    return {"name": agent.name, "description": agent.handoff_description}

# Definição dos agentes
comportamento_agent = Agent(
    name="Analisador de Comportamento",
    instructions="""
    Analise a mensagem do usuário e descreva:
    - Personalidade aparente
    - Emoção dominante
    - Estilo de comunicação
    - Dores mais prováveis
    - Desejos implícitos
    - Linguagem preferida (informal, direta, técnica...)
    - Tom de voz recomendado para responder

    Seja sintético, objetivo e baseado no conteúdo da mensagem.
    """,
    output_type="ComportamentoSchema"
)

tarefa_agent = Agent(
    name="Organizador de Tarefas",
    handoff_description="Organiza tarefas pendentes do usuário.",
    instructions="""Você ajuda o usuário a registrar e visualizar tarefas do dia a dia. Nunca julgue ou pressione. Se o usuário mencionar uma tarefa (ex.: 'Quero registrar uma tarefa, ir ao mercado'), interprete como a descrição da tarefa.""",
    tools=[registrar_tarefa_tool, listar_tarefas_tool],
)

memoria_agent = Agent(
    name="Memória Viva",
    handoff_description="Gerencia memórias e objetivos do usuário.",
    instructions="""Você ajuda o usuário a registrar objetivos da semana e consultar o que é importante. Ajude com leveza e clareza.
    Você armazena informações relevantes compartilhadas pelo usuário, como:
    - Metas de vida
    - Sonhos
    - Dificuldades
    - Eventos marcantes
    - Interesses

    Quando encontrar uma informação relevante para guardar, registre com clareza e contexto emocional.
    """,
    tools=[salvar_objetivo_tool, consultar_objetivo_tool],
)

emocional_agent = Agent(
    name="Suporte Emocional",
    handoff_description="Acolhe o usuário quando ele está sobrecarregado.",
    instructions="""Você acolhe o usuário com empatia e inteligência emocional. Sempre valide a emoção da pessoa e ofereça apoio leve. Use o tom de amigo confiável.""",
    tools=[suporte_emocional_tool, detectar_mudanca_de_intencao_tool],
)

triage_agent = Agent(
    name="Triage Copiloto",
    instructions="""
    Você é o cérebro principal do Copiloto IA. Analise cada mensagem recebida e decida o que o usuário quer:
    - Se for uma pergunta simples com uma única intenção:
      - Organizar tarefas (ex.: 'Quero registrar uma tarefa' ou 'Liste minhas tarefas') → retorne 'transfer_to_Organizador de Tarefas'
      - Falar de metas ou objetivos (ex.: 'Quero definir um objetivo' ou 'Quais são meus objetivos?') → retorne 'transfer_to_Memória Viva'
      - Expressar dúvida, cansaço ou frustração (ex.: 'Estou cansado', 'Não sei se estou produtivo') → retorne 'transfer_to_Suporte Emocional'
    - Se tiver múltiplas intenções distintas (ex.: 'Registre uma tarefa e me diga meus objetivos'), retorne uma lista no formato 'transfer_to_<nome_do_agente>:<parte_da_mensagem>' (um por linha).
    - Se a mensagem for ambígua mas parecer uma tarefa com descrição (ex.: 'Quero registrar uma tarefa, ir ao mercado'), passe tudo para 'transfer_to_Organizador de Tarefas'.
    - Se não souber delegar, passe tudo para 'transfer_to_Analisador de Comportamento'.
    Indícios de apoio emocional: 'Não sei se estou produtivo', 'Sinto que não andei', 'Minha mente está cheia', 'Estou cansado mentalmente'.
    NÃO RESPONDA DIRETAMENTE, apenas retorne o handoff ou a lista de delegações. Exemplos:
    - 'Quero registrar uma tarefa' → 'transfer_to_Organizador de Tarefas'
    - 'Quero registrar uma tarefa, ir ao mercado' → 'transfer_to_Organizador de Tarefas'
    - 'Quais são meus objetivos?' → 'transfer_to_Memória Viva'
    - 'Estou cansado' → 'transfer_to_Suporte Emocional'
    - 'Registre uma tarefa e me diga meus objetivos' → 
      transfer_to_Organizador de Tarefas:Registre uma tarefa
      transfer_to_Memória Viva:Me diga meus objetivos
    - 'O que é um elefante?' → 'Nenhum:O que é um elefante?'
    """,
    handoffs=[
        handoff(tarefa_agent),
        handoff(memoria_agent),
        handoff(emocional_agent),
        handoff(comportamento_agent),
    ]
)
