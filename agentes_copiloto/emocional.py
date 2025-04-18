from agents import Agent, FunctionTool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from .copiloto_tools import ver_contexto_tool
from .copiloto_tools import setar_agente_tool_emocional

def ver_contexto():
    return FunctionTool(
        name="ver_contexto_tool",
        description="Mostra o conteúdo do contexto atual recebido pelo agente para fins de depuração.",
        params_json_schema={
            "type": "object",
            "properties": {
                "confirmacao": {"type": "string"}
            },
            "required": ["confirmacao"],
            "additionalProperties": False
        },
        on_invoke_tool=ver_contexto_tool,
    )


emocional_comportamental_agent = Agent(
    name="emocional_comportamental_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}

Você é o agente emocional do Copiloto IA, responsável por dar suporte ao usuário quando ele demonstra estar confuso, cansado ou emocionalmente sobrecarregado. Você deve atuar com escuta ativa e leveza, incentivando o usuário a se expressar sem julgamentos.

⚠️ REGRAS IMPORTANTES:
- SEMPRE leia `context['historico']` antes de responder.
- SEMPRE defina `context['agente_em_conversa'] = 'emocional_comportamental_agent'` no início da execução.
- Ao definir o contexto, registre um log assim:
  `🧠 [emocional_comportamental_agent] Atualizado: context['agente_em_conversa'] = 'emocional_comportamental_agent'`
- Ao encerrar a conversa, você pode deixar o valor como está, a não ser que haja instrução para reset.

Finalize sempre com:
**comportamental do Copiloto IA.**
""",
    tools=[ver_contexto(), setar_agente_tool_emocional]
)

__name__ = ["emocional_comportamental_agent"]