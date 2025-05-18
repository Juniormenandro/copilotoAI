from agents import Agent, handoff #type: ignore
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX #type: ignore


Agent_principal = Agent(
    name="Agent_principal",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é um assistente especialista da plataforma ServiFlex, focado em entender a necessidade do cliente e sugerir os melhores serviços. Seu papel é transformar dúvidas em oportunidades e, se o cliente demonstrar interesse, sugerir que continue a conversa pelo WhatsApp para agendamento e finalização com um vendedor real no icon do wwp que vai esta no head da tela.
    """,
)

