import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import Agent, FunctionTool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from .copiloto_tools import registrar_tarefa_tool, listar_tarefas_tool, salvar_objetivo_tool, consultar_objetivo_tool, concluir_tarefa_tool, adiar_tarefa_tool, setar_agente_tool_organizador

import inspect
import json

# Function Tools

def to_function_tool(fn, name: str, description: str, params_schema: dict):
    async def on_invoke_tool(context, tool_input):
        if not isinstance(tool_input, dict):
            print(f"⚠️ Tool recebeu string. Tentando interpretar como JSON: {tool_input}")
            tool_input = json.loads(tool_input)

        wa_id_from_context = getattr(context, "context", {}).get("wa_id")
        if "wa_id" in inspect.signature(fn).parameters:
            if wa_id_from_context:
                tool_input["wa_id"] = wa_id_from_context
                print(f"📌 'wa_id' sobrescrito com valor do contexto: {wa_id_from_context}")
            else:
                print("🚨 'wa_id' não encontrado no contexto!")

        print(f"🛠️ Executando tool: {name} com input: {tool_input}")

        if "context" in inspect.signature(fn).parameters:
            if inspect.iscoroutinefunction(fn):
                return await fn(**tool_input, context=context)
            return fn(**tool_input, context=context)

        if inspect.iscoroutinefunction(fn):
            return await fn(**tool_input)
        return fn(**tool_input)

    print(f"✅ Tool registrada: {name}")
    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=params_schema,
        on_invoke_tool=on_invoke_tool,
    )

registrar_tarefa = to_function_tool(
    registrar_tarefa_tool,
    name="registrar_tarefa_tool",
    description="Registra uma nova tarefa com descricao, data_entrega e wa_id.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "descricao": {"type": "string"},
            "data_entrega": {"type": "string"},
        },
        "required": ["wa_id", "descricao", "data_entrega"],
        "additionalProperties": False,
    },
)

listar_tarefas = to_function_tool(
    listar_tarefas_tool,
    name="listar_tarefas_tool",
    description="Lista todas as tarefas pendentes com base no wa_id.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
        },
        "required": ["wa_id"],
        "additionalProperties": False,
    },
)

salvar_objetivo = to_function_tool(
    salvar_objetivo_tool,
    name="salvar_objetivo_tool",
    description="Salva o objetivo da semana do usuário.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "objetivo": {"type": "string"},
        },
        "required": ["wa_id", "objetivo"],
        "additionalProperties": False,
    },
)

consultar_objetivo = to_function_tool(
    consultar_objetivo_tool,
    name="consultar_objetivo_tool",
    description="Consulta o objetivo da semana com base no wa_id.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
        },
        "required": ["wa_id"],
        "additionalProperties": False,
    },
)

concluir_tarefa = to_function_tool(
    concluir_tarefa_tool,
    name="concluir_tarefa_tool",
    description="Marca uma tarefa como concluída com base na descrição e no wa_id.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "descricao": {"type": "string"},
        },
        "required": ["wa_id", "descricao"],
        "additionalProperties": False,
    },
)

adiar_tarefa = to_function_tool(
    adiar_tarefa_tool,
    name="adiar_tarefa_tool",
    description="Adia uma tarefa existente para uma nova data de entrega.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "descricao": {"type": "string"},
            "nova_data": {"type": "string"},
        },
        "required": ["wa_id", "descricao", "nova_data"],
        "additionalProperties": False,
    },
)

organizador_memoria_agent = Agent(
    name="organizador_memoria_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

Você é o agente organizador do Copiloto IA. Sua missão é ajudar o usuário a lidar com suas tarefas e organização mental. Use sempre linguagem prática e leve, sem pressionar.

⚙️ Você deve:
- Usar o histórico do usuário (`context['historico']`) e comportamento (`context['comportamento']`) sempre que disponível.
- Registrar tarefas, objetivos, e ajustar datas quando necessário.

⚠️ REGRAS IMPORTANTES:
- SEMPRE defina `context['agente_em_conversa'] = 'organizador_memoria_agent'` ao iniciar.
- Registre os logs:
  - Início: `📒 [organizador_memoria_agent] Iniciando. Contexto definido.`
  - Fim: `📒 [organizador_memoria_agent] Finalizado. Contexto resetado.`

Finalize com:
**organizador do Copiloto IA.**
""",
    tools=[
        registrar_tarefa,
        listar_tarefas,
        salvar_objetivo,
        consultar_objetivo,
        concluir_tarefa,
        adiar_tarefa,
        setar_agente_tool_organizador
    ]
)


__name__ = ["organizador_memoria_agent"]