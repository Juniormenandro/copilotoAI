
from openai.agents import Agent, Runner, handoff
import asyncio

# Agente de tarefas
tarefa_agent = Agent(
    name="Organizador de Tarefas",
    handoff_description="Organiza as tarefas do usuário.",
    instructions="Você ajuda o usuário a registrar tarefas e lembrar o que precisa fazer.",
)

# Agente de memória
memoria_agent = Agent(
    name="Memória Viva",
    handoff_description="Ajuda o usuário com foco e objetivo da semana.",
    instructions="Você ajuda o usuário a definir metas ou lembrar do objetivo da semana.",
)

# Agente emocional
emocional_agent = Agent(
    name="Suporte Emocional",
    handoff_description="Apoia o usuário emocionalmente.",
    instructions="Você acolhe o usuário com empatia e valida os sentimentos dele.",
)

# Agente de triagem
triage_agent = Agent(
    name="Triage Copiloto",
    instructions="""
Analise a mensagem do usuário e decida para qual agente encaminhar:
- Se for tarefa ou organização, envie para o Organizador de Tarefas.
- Se for meta ou objetivo, envie para Memória Viva.
- Se for desabafo, cansaço ou ansiedade, envie para Suporte Emocional.
""",
    handoffs=[handoff(tarefa_agent), handoff(memoria_agent), handoff(emocional_agent)],
)

async def main():
    print("\n✅ Copiloto IA com SDK oficial rodando...\n")
    while True:
        user_input = input("👤 Você: ")
        if user_input.lower() in ["sair", "exit", "quit"]:
            break

        result = await Runner.run(triage_agent, user_input)
        print(f"🤖 Copiloto: {result.final_output}\n")

if __name__ == "__main__":
    asyncio.run(main())
