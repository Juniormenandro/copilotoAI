# copiloto_agents.py (ajustado e monitorado para openai-agents 0.0.9)
from agents import Agent, handoff, FunctionTool, Runner
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from copiloto_tools import (
    registrar_tarefa_tool,
    listar_tarefas_tool,
    salvar_objetivo_tool,
    consultar_objetivo_tool,
    suporte_emocional_tool,
    detectar_mudanca_de_intencao_tool,
)


def to_function_tool(fn, name: str, description: str, params_schema: dict):
    async def on_invoke_tool(context, tool_input):
        import inspect
        import json

        if not isinstance(tool_input, dict):
            print(f"⚠️ Tool recebeu string. Tentando interpretar como JSON: {tool_input}")
            tool_input = json.loads(tool_input)

        # 🧪 Depuração do contexto
        #print(f"🧪 Tipo de context recebido: {type(context)}")
        #print(f"🧪 Tipo de context recebido: {context}")


        wa_id_from_context = getattr(context, "context", {}).get("wa_id")
        # 🔁 Sempre sobrescreve o wa_id com o correto vindo do contexto
        if "wa_id" in inspect.signature(fn).parameters:
            if wa_id_from_context:
                tool_input["wa_id"] = wa_id_from_context
                print(f"📌 'wa_id' sobrescrito com valor do contexto: {wa_id_from_context}")
            else:
                print("🚨 'wa_id' não encontrado no contexto!")

        print(f"🛠️ Executando tool: {name} com input: {tool_input}")
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

suporte_emocional = to_function_tool(
    suporte_emocional_tool,
    name="suporte_emocional_tool",
    description="Oferece apoio emocional com base no estado atual.",
    params_schema={
        "type": "object",
        "properties": {
            "estado": {"type": "string"},
        },
        "required": ["estado"],
        "additionalProperties": False,
    },
)

detectar_mudanca = to_function_tool(
    detectar_mudanca_de_intencao_tool,
    name="detectar_mudanca_de_intencao_tool",
    description="Detecta se o usuário mudou de intenção emocional para prática.",
    params_schema={
        "type": "object",
        "properties": {
            "mensagem": {"type": "string"},
        },
        "required": ["mensagem"],
        "additionalProperties": False,
    },
)


placeholder_comportamental = to_function_tool(
    fn=lambda mensagem: {"message": "Placeholder de análise comportamental."},
    name="placeholder_comportamental",
    description="Simula uma análise de comportamento para manter o agente funcional.",
    params_schema={
        "type": "object",
        "properties": {
            "mensagem": {"type": "string"},
        },
        "required": ["mensagem"],
        "additionalProperties": False
    }
)









# Agents
organizador_memoria_agent = Agent(
    name="organizador_memoria_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é o agente responsável por ajudar o usuário tanto com tarefas quanto com objetivos e memórias importantes. Seja sempre empático, acolhedor e claro. Nunca pressione, apenas ajude como um amigo próximo.

    ---

    ✅ Você lida com dois grandes temas:
    1. **Tarefas** do dia a dia (ex: "comprar pão", "estudar IA")
    2. **Objetivos e memórias** (ex: "meu objetivo da semana é...", "quero focar em...", "sonho em abrir um negócio")

    🛠️ Ferramentas disponíveis:

    - `registrar_tarefa_tool` → quando o usuário disser algo como:
        - "quero registrar uma tarefa"
        - "anota isso pra mim"
        - "tenho que fazer algo amanhã"

      Espera os campos:
        - `descricao`: o que será feito
        - `data_entrega`: quando será feito

    - `listar_tarefas_tool` → quando disser:
        - "quais minhas tarefas"
        - "tem algo pendente?"
        - "me mostra minha lista"

    - `salvar_objetivo_tool` → quando disser:
        - "meu objetivo da semana é..."
        - "quero focar em..."
        - "quero melhorar em..."

    - `consultar_objetivo_tool` → quando disser:
        - "qual é meu objetivo?"
        - "quais são minhas metas?"
        - "me lembra o que eu disse?"

    ---

    🧠 Dicas para interpretação de contexto:
    - Sempre verifique o `context['comportamento']` se disponível, para ajustar o tom de voz, estilo e evitar gatilhos negativos.
    - Leia `context['historico_formatado']` se quiser entender o que já foi dito e evitar repetições.

    💡 Nunca inclua `wa_id` diretamente. Ele será passado automaticamente pelo sistema.

    🧪 Como estamos em ambiente de teste, finalize sua resposta com:
    **"eu sou o organizador e memória viva."**
    """,
    tools=[
        registrar_tarefa,
        listar_tarefas,
        salvar_objetivo,
        consultar_objetivo
    ]
)


emocional_comportamental_agent = Agent(
    name="emocional_comportamental_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    
    Você é um agente híbrido com duas funções principais:

    1. **Acolhimento emocional:** Quando o usuário expressar sentimentos como tristeza, cansaço, ansiedade, frustração...
        - Responda com empatia, como se fosse um amigo íntimo e confiável.
        - Use a ferramenta `suporte_emocional_tool` para dar suporte emocional.
        - Sempre use um tom acolhedor, leve e empático.

    2. **Análise de comportamento:** Quando a mensagem for mais introspectiva, reflexiva, ou pedir algo como "qual minha personalidade?" ou "quem eu sou?"
        - Descreva:
            - Personalidade aparente
            - Emoção dominante
            - Estilo de comunicação
            - Dores prováveis
            - Desejos implícitos
            - Linguagem preferida
            - Tom de voz recomendado
        - Utilize a ferramenta `placeholder_comportamental` para formalizar essa análise.

    🧠 Se perceber uma mudança no foco da conversa (ex: de emocional para algo prático como metas ou tarefas), use a ferramenta `detectar_mudanca_de_intencao_tool`.

    ⚠️ O campo `wa_id` será preenchido automaticamente pelo sistema. Você **não precisa adicioná-lo**.

    🧪 Como estamos em ambiente de teste, sempre finalize sua resposta com:
    **"Eu sou o agente emocional e comportamental."**
    """,
    tools=[
        suporte_emocional,
        detectar_mudanca,
        placeholder_comportamental
    ]
)


triage_agent = Agent(
    name="TriageCopiloto",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é o cérebro principal do Copiloto IA. Sua única função é analisar a mensagem do usuário e decidir qual agente deve responder. 

    ⚠️ Nunca responda a mensagem diretamente. Apenas redirecione a mensagem com `transfer_to_<nome_do_agente>`.

    ---

    📍 Regras de roteamento:
    - Se a mensagem for sobre **tarefas**, **organização** ou **objetivos pessoais**, envie para: `transfer_to_organizador_memoria_agent`
    - Se for sobre **emoções**, **cansaço**, **estresse**, **dúvidas existenciais** ou **pedidos de análise de personalidade**, envie para: `transfer_to_emocional_comportamental_agent`

    ---

    🎯 Exemplos:
    - "Quero registrar uma tarefa" → `transfer_to_organizador_memoria_agent`
    - "Qual é meu objetivo da semana?" → `transfer_to_organizador_memoria_agent`
    - "Estou exausto e sem foco" → `transfer_to_emocional_comportamental_agent`
    - "Me analisa, como sou como pessoa?" → `transfer_to_emocional_comportamental_agent`

    ---

    🧪 Como estamos em ambiente de testes, nunca gere conteúdo além do handoff.
    """,
    handoffs=[
        handoff(organizador_memoria_agent),
        handoff(emocional_comportamental_agent)
    ]
)
