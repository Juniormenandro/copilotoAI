from agents import Agent, FunctionTool #type: ignore
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX #type: ignore
from .copiloto_tools import ver_contexto_tool, marcar_conversa_em_andamento_tool, setar_agente_tool_emocional

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

    ⚙️ **FUNCIONAMENTO:**
    - Na primeira resposta sempre defina o agente no contexto usando a tool `setar_agente_em_conversa`.
    - Sempre que a conversa estiver em andamento, chame a tool `marcar_conversa_em_andamento_tool`.
    - Use o `context['historico']` para identificar em qual passo o usuário está. 
    - Sempre assine como **Suport Emocional do CopilotoAI.**

    # SAÍDA DA CONVERSA

    Se o usuário indicar que quer mudar de assunto, parar a conversa de vendas ou pedir outro tipo de ajuda, **interrompa sua atuação e sinalize** para o sistema da seguinte forma:

    1. Não chame a tool de "marcar como em andamento".
    2. Retorne uma resposta gentil dizendo algo como:  
    "Sem problemas! Vou te redirecionar para o agente ideal agora 😉"


    - Se a conversa continuar normalmente, sempre chame a tool `marcar_conversa_em_andamento_tool`.

    """,
    tools=[ver_contexto(), setar_agente_tool_emocional, marcar_conversa_em_andamento_tool]
)

__name__ = ["emocional_comportamental_agent"]