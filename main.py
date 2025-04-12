# from __future__ import annotations as _annotations

# import asyncio
# import random
# import uuid

# from pydantic import BaseModel

# from agents import (
#     Agent,
#     HandoffOutputItem,
#     ItemHelpers,
#     MessageOutputItem,
#     RunContextWrapper,
#     Runner,
#     ToolCallItem,
#     ToolCallOutputItem,
#     TResponseInputItem,
#     function_tool,
#     handoff,
#     trace,
# )
# from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


# from dotenv import load_dotenv
# # Carrega variáveis de ambiente do arquivo .env (por exemplo, OPENAI_API_KEY)
# load_dotenv()


# ### CONTEXT


# class AirlineAgentContext(BaseModel):
#     passenger_name: str | None = None
#     confirmation_number: str | None = None
#     seat_number: str | None = None
#     flight_number: str | None = None


# ### TOOLS


# @function_tool(
#     name_override="faq_lookup_tool", description_override="Lookup frequently asked questions."
# )
# async def faq_lookup_tool(question: str) -> str:
#     if "bag" in question or "baggage" in question:
#         return (
#             "You are allowed to bring one bag on the plane. "
#             "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
#         )
#     elif "seats" in question or "plane" in question:
#         return (
#             "There are 120 seats on the plane. "
#             "There are 22 business class seats and 98 economy seats. "
#             "Exit rows are rows 4 and 16. "
#             "Rows 5-8 are Economy Plus, with extra legroom. "
#         )
#     elif "wifi" in question:
#         return "We have free wifi on the plane, join Airline-Wifi"
#     return "I'm sorry, I don't know the answer to that question."


# @function_tool
# async def update_seat(
#     context: RunContextWrapper[AirlineAgentContext], confirmation_number: str, new_seat: str
# ) -> str:
#     """
#     Update the seat for a given confirmation number.

#     Args:
#         confirmation_number: The confirmation number for the flight.
#         new_seat: The new seat to update to.
#     """
#     # Update the context based on the customer's input
#     context.context.confirmation_number = confirmation_number
#     context.context.seat_number = new_seat
#     # Ensure that the flight number has been set by the incoming handoff
#     assert context.context.flight_number is not None, "Flight number is required"
#     return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"


# ### HOOKS


# async def on_seat_booking_handoff(context: RunContextWrapper[AirlineAgentContext]) -> None:
#     flight_number = f"FLT-{random.randint(100, 999)}"
#     context.context.flight_number = flight_number


# ### AGENTS

# faq_agent = Agent[AirlineAgentContext](
#     name="FAQ Agent",
#     handoff_description="A helpful agent that can answer questions about the airline.",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are an FAQ agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
#     Use the following routine to support the customer.
#     # Routine
#     1. Identify the last question asked by the customer.
#     2. Use the faq lookup tool to answer the question. Do not rely on your own knowledge.
#     3. If you cannot answer the question, transfer back to the triage agent.""",
#     tools=[faq_lookup_tool],
# )

# seat_booking_agent = Agent[AirlineAgentContext](
#     name="Seat Booking Agent",
#     handoff_description="A helpful agent that can update a seat on a flight.",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     You are a seat booking agent. If you are speaking to a customer, you probably were transferred to from the triage agent.
#     Use the following routine to support the customer.
#     # Routine
#     1. Ask for their confirmation number.
#     2. Ask the customer what their desired seat number is.
#     3. Use the update seat tool to update the seat on the flight.
#     If the customer asks a question that is not related to the routine, transfer back to the triage agent. """,
#     tools=[update_seat],
# )

# triage_agent = Agent[AirlineAgentContext](
#     name="Triage Agent",
#     handoff_description="A triage agent that can delegate a customer's request to the appropriate agent.",
#     instructions=(
#         f"{RECOMMENDED_PROMPT_PREFIX} "
#         "You are a helpful triaging agent. You can use your tools to delegate questions to other appropriate agents."
#     ),
#     handoffs=[
#         faq_agent,
#         handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
#     ],
# )

# faq_agent.handoffs.append(triage_agent)
# seat_booking_agent.handoffs.append(triage_agent)


# ### RUN


# async def main():
#     current_agent: Agent[AirlineAgentContext] = triage_agent
#     input_items: list[TResponseInputItem] = []
#     context = AirlineAgentContext()

#     # Normally, each input from the user would be an API request to your app, and you can wrap the request in a trace()
#     # Here, we'll just use a random UUID for the conversation ID
#     conversation_id = uuid.uuid4().hex[:16]

#     while True:
#         user_input = input("Enter your message: ")
#         with trace("Customer service", group_id=conversation_id):
#             input_items.append({"content": user_input, "role": "user"})
#             result = await Runner.run(current_agent, input_items, context=context)

#             for new_item in result.new_items:
#                 agent_name = new_item.agent.name
#                 if isinstance(new_item, MessageOutputItem):
#                     print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
#                 elif isinstance(new_item, HandoffOutputItem):
#                     print(
#                         f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
#                     )
#                 elif isinstance(new_item, ToolCallItem):
#                     print(f"{agent_name}: Calling a tool")
#                 elif isinstance(new_item, ToolCallOutputItem):
#                     print(f"{agent_name}: Tool call output: {new_item.output}")
#                 else:
#                     print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")
#             input_items = result.to_input_list()
#             current_agent = result.last_agent


# if __name__ == "__main__":
#     asyncio.run(main())









import asyncio
import requests
from agents import Agent, Runner, function_tool, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from dotenv import load_dotenv
import os
from ast import literal_eval

# Carrega as chaves de API
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# --- Subagentes e Ferramentas ---

@function_tool
def obter_clima(cidade: str) -> str:
    print(f"Chamando obter_clima para {cidade}")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        resposta = requests.get(url).json()
        if resposta.get("cod") != 200:
            return "Cidade não encontrada."
        temp = resposta["main"]["temp"]
        descricao = resposta["weather"][0]["description"]
        return f"O clima em {cidade} está {descricao} com {temp}°C."
    except Exception as e:
        return f"Erro ao consultar o clima: {str(e)}"

agente_clima = Agent(
    name="AgenteClima",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\nVocê é um especialista em clima. Responda perguntas sobre o clima usando seu conhecimento interno ou a ferramenta 'obter_clima' para dados em tempo real, conforme julgar apropriado.",
    tools=[obter_clima]
)

@function_tool
def calcular(expressao: str) -> str:
    print(f"Chamando calcular para {expressao}")
    try:
        resultado = literal_eval(expressao)
        return f"O resultado de {expressao} é {resultado}."
    except Exception:
        return "Erro ao calcular. Use uma expressão válida como '2 + 2'."

agente_matematica = Agent(
    name="AgenteMatematica",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\nVocê é um especialista em matemática. Responda perguntas matemáticas usando seu conhecimento interno ou a ferramenta 'calcular' se preferir verificar o cálculo.",
    tools=[calcular]
)

@function_tool
def fato_historico(tema: str) -> str:
    print(f"Chamando fato_historico para {tema}")
    return f"Em 1500, algo incrível aconteceu relacionado a {tema} (fictício)."

agente_historia = Agent(
    name="AgenteHistoria",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\nVocê é um especialista em história. Responda perguntas históricas com seu conhecimento interno ou use a ferramenta 'fato_historico' se quiser um fato fictício criativo.",
    tools=[fato_historico]
)

@function_tool
def traduzir(texto: str, idioma: str) -> str:
    print(f"Chamando traduzir para '{texto}' em {idioma}")
    return f"'{texto}' traduzido para {idioma} é '{texto} translated' (simulado)."

agente_traducao = Agent(
    name="AgenteTraducao",
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}\nVocê é um especialista em tradução. Responda pedidos de tradução usando seu conhecimento interno para traduções precisas ou a ferramenta 'traduzir' para uma resposta simulada, conforme julgar melhor. Pergunte ao usuário o idioma se não for especificado.",
    tools=[traduzir]
)

# --- Agente Principal com Handoffs ---
agente_principal = Agent(
    name="AgentePrincipal",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    Você é um orquestrador inteligente. Analise a pergunta do usuário:
    - Se for uma pergunta simples com uma única intenção (ex.: 'Qual o clima em SP?' ou 'Traduza dog para espanhol'), retorne apenas o handoff correspondente como 'transfer_to_<nome_do_agente>' (ex.: 'transfer_to_AgenteTraducao'). Use os nomes EXATOS: AgenteClima, AgenteMatematica, AgenteHistoria, AgenteTraducao.
    - Se tiver múltiplas intenções (ex.: 'Qual o clima em SP e quanto é 2 + 2?'), retorne uma lista de delegações no formato 'transfer_to_<nome_do_agente>:<parte_da_pergunta>' (um por linha).
    - Use:
      - 'transfer_to_AgenteClima' para clima/tempo.
      - 'transfer_to_AgenteMatematica' para cálculos.
      - 'transfer_to_AgenteHistoria' para história.
      - 'transfer_to_AgenteTraducao' para tradução.
    - Se não souber delegar uma parte, use 'Nenhum:<parte_da_pergunta>'.
    NÃO RESPONDA DIRETAMENTE, apenas retorne o handoff ou a lista de delegações. Exemplos:
    - 'Qual o clima em SP?' → 'transfer_to_AgenteClima'
    - 'Traduza dog para espanhol' → 'transfer_to_AgenteTraducao'
    - 'Qual o clima em SP e quanto é 2 + 2?' → 
      transfer_to_AgenteClima:Qual o clima em SP?
      transfer_to_AgenteMatematica:Quanto é 2 + 2?
    - 'O que é um elefante?' → 'Nenhum:O que é um elefante?'"""
    ,
    handoffs=[
        handoff(agente_clima),
        handoff(agente_matematica),
        handoff(agente_historia),
        handoff(agente_traducao)
    ]
)

# --- Função para Processar Perguntas ---
async def processar_pergunta(pergunta: str):
    print(f"Processando: {pergunta}")
    resultado = await Runner.run(agente_principal, pergunta)
    output = resultado.final_output.strip()
    print(f"Saída do AgentePrincipal: '{output}'")  # Log de debug
    
    subagentes = {
        "AgenteClima": agente_clima,
        "AgenteMatematica": agente_matematica,
        "AgenteHistoria": agente_historia,
        "AgenteTraducao": agente_traducao
    }
    
    # Caso de pergunta simples (handoff nativo)
    if "\n" not in output:
        if output.startswith("transfer_to_"):
            agente_nome = output.replace("transfer_to_", "")
            if agente_nome in subagentes:
                print(f"Delegando nativamente para {agente_nome}")
                resposta = await Runner.run(subagentes[agente_nome], pergunta)
                return resposta.final_output
            return f"Erro: Agente {agente_nome} não encontrado."
        return output  # Caso seja "Nenhum:..."

    # Caso de pergunta mista (processamento manual)
    delegacoes = output.split("\n")
    respostas = []
    for delegacao in delegacoes:
        if ":" in delegacao:
            agente_nome, sub_pergunta = delegacao.split(":", 1)
            if agente_nome.startswith("transfer_to_"):
                agente_nome = agente_nome.replace("transfer_to_", "")
                if agente_nome in subagentes:
                    print(f"Delegando manualmente '{sub_pergunta}' para {agente_nome}")
                    resposta = await Runner.run(subagentes[agente_nome], sub_pergunta)
                    respostas.append(resposta.final_output)
                else:
                    respostas.append(f"Erro: Agente {agente_nome} não encontrado.")
            else:
                respostas.append(f"Desculpe, não sei como ajudar com '{sub_pergunta}'.")
        else:
            respostas.append(f"Erro ao processar delegação: {delegacao}")
    
    return "\n".join(respostas)

# --- Função Principal Interativa ---
async def main_interativo():
    print("Bem-vindo! Digite sua pergunta ou 'sair' para encerrar.")
    while True:
        pergunta = input("Pergunta: ")
        if pergunta.lower() == "sair":
            print("Até logo!")
            break
        resposta = await processar_pergunta(pergunta)
        print(f"Resposta: {resposta}\n")

if __name__ == "__main__":
    asyncio.run(main_interativo())