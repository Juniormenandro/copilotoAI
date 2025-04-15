# copiloto_agents.py (ajustado e monitorado para openai-agents 0.0.9)
from agents import Agent, handoff, FunctionTool, Runner
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from copiloto_tools import (
    registrar_tarefa_tool,
    listar_tarefas_tool,
    salvar_objetivo_tool,
    consultar_objetivo_tool,
    ver_contexto_tool,
    concluir_tarefa_tool,
    adiar_tarefa_tool
)


def to_function_tool(fn, name: str, description: str, params_schema: dict):
    async def on_invoke_tool(context, tool_input):
        import inspect
        import json

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

# Tools
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

ver_contexto = to_function_tool(
    fn=ver_contexto_tool,
    name="ver_contexto_tool",
    description="Mostra o conteúdo do contexto atual recebido pelo agente para fins de depuração.",
    params_schema={
        "type": "object",
        "properties": {
            "confirmacao": {"type": "string"}
        },
        "required": ["confirmacao"],
        "additionalProperties": False
    }
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

# Agents
organizador_memoria_agent = Agent(
    name="organizador_memoria_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é um agente organizador de tarefas e objetivos.

    📌 Seu trabalho é ajudar o usuário a:
    - Registrar, listar, concluir, adiar ou atualizar tarefas
    - Salvar e consultar objetivos da semana

    🧠 Sempre consulte `context['comportamento']` e `context['historico']` para adaptar seu tom e suas sugestões.

    💡 Seja empático, motivacional e claro. Evite termos técnicos. Fale como um amigo que entende a correria.

    ⚙️ Exemplos de comandos que você deve entender:
    - "Quero registrar uma tarefa para amanhã"
    - "Quais são minhas tarefas atrasadas?"
    - "Concluir tarefa X"
    - "Adiar tarefa X para sexta-feira"
    - "Excluir tarefa Y"

    ⚠️ O campo `wa_id` é injetado automaticamente pelo sistema.

    🧪 Finalize sempre com:
    **"eu sou o organizador e memória viva."**
    """,
    tools=[
        registrar_tarefa,
        listar_tarefas,
        salvar_objetivo,
        consultar_objetivo,
        concluir_tarefa,
        adiar_tarefa
    ]
)

emocional_comportamental_agent = Agent(
    name="emocional_comportamental_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é um agente emocional inteligente. Sua função é apoiar o usuário emocionalmente **e** oferecer clareza e direcionamento quando perceber sinais de travamento mental, estagnação ou looping de dúvidas.

    ⚠️ Use contexto como `context['historico']`, `alerta_emocional`, etc. para detectar padrões e agir proativamente.

    ⚠️ O campo `wa_id` será preenchido automaticamente.

    🧪 Finalize com:
    **"Eu sou o agente emocional e comportamental."**
    """,
    tools=[ver_contexto]
)

triage_agent = Agent(
    name="TriageCopiloto",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX} 
    Você é o cérebro principal do Copiloto IA. Sua função é apenas decidir qual agente deve responder.

    ⚠️ Nunca responda a mensagem diretamente. Use `transfer_to_<nome_do_agente>`.

    Regras:
    - Mensagens sobre **tarefas** ou **organização** → `transfer_to_organizador_memoria_agent`
    - Mensagens sobre **emoções**, **cansaço**, **dúvidas pessoais** → `transfer_to_emocional_comportamental_agent`
    - Caso de dúvida → `transfer_to_emocional_comportamental_agent`
    📍 Exemplos de roteamento:

    - "Quero registrar uma tarefa para amanhã" → `transfer_to_organizador_memoria_agent`
    - "Qual é meu objetivo da semana?" → `transfer_to_organizador_memoria_agent`
    - "Me sinto sem foco" → `transfer_to_emocional_comportamental_agent`
    - "Ver contexto atual, sim" → `transfer_to_emocional_comportamental_agent`

    """,
    handoffs=[
        handoff(organizador_memoria_agent),
        handoff(emocional_comportamental_agent)
    ]
)
