# z_copiloto_agents.py
# copiloto_agents.py (AJUSTADO COM FunctionTool MANUAL E additionalProperties: false)

# copiloto_agents.py (AJUSTADO COM FunctionTool MANUAL E additionalProperties: false)

# copiloto_agents.py (AJUSTADO COM FunctionTool MANUAL E FIX DE REQUIRED)

from copiloto_context import CopilotoContext
from db.tarefas import registrar_tarefa, listar_tarefas
from db.memorias import salvar_memoria, consultar_objetivo_da_semana

# ✅ REGISTRAR TAREFA
def registrar_tarefa_tool_fn(
    context: CopilotoContext,
    descricao: str,
    data_entrega: str,
) -> str:
    wa_id = context.wa_id
    registrar_tarefa(wa_id, descricao, data_entrega)
    return f"Tarefa registrada com sucesso: {descricao}"

# 📋 LISTAR TAREFAS
def listar_tarefas_tool_fn(
    context: CopilotoContext,
) -> str:
    wa_id = context.wa_id
    tarefas = listar_tarefas(wa_id)
    if not tarefas:
        return "🎉 Você não tem tarefas pendentes no momento!"
    resposta = "📋 Suas tarefas:\n"
    for t in tarefas:
        entrega = t.get("data_entrega", "sem data")
        resposta += f"- {t['descricao']} (entrega: {entrega})\n"
    return resposta

# 🎯 SALVAR OBJETIVO DA SEMANA
def salvar_objetivo_tool_fn(
    context: CopilotoContext,
    objetivo: str
) -> str:
    wa_id = context.wa_id
    salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
    return "🎯 Objetivo da semana salvo com sucesso!"

# 🔍 CONSULTAR OBJETIVO
def consultar_objetivo_tool_fn(
    context: CopilotoContext
) -> str:
    wa_id = context.wa_id
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return f"🎯 Seu objetivo da semana é: {objetivo}"
    return "Ainda não encontrei nenhum objetivo da semana registrado."

# ❤️ APOIO EMOCIONAL
def suporte_emocional_tool_fn(
    context: CopilotoContext,
    estado: str
) -> str:
    frases = {
        "ansioso": "Respira... Você está indo bem. Vamos dar um passo de cada vez?",
        "cansado": "Se cuida, tá? Você não precisa dar conta de tudo hoje. Descanso também é estratégia.",
        "frustrado": "Se as coisas não saíram como queria, tudo bem. Você tentou. E só de tentar, já tá na frente.",
    }
    return frases.get(estado.lower(), "Tô contigo. Quer conversar sobre isso?")

# 🧠 DETECÇÃO DE MUDANÇA DE INTENÇÃO
def detectar_mudanca_de_intencao_tool_fn(
    context: CopilotoContext,
    mensagem: str
) -> str:
    palavras_praticas = [
        "tenho que", "preciso", "vou", "devo", "lembrete", "entregar", "organizar",
        "lista", "tarefa", "meta", "prazo", "orçamento", "proposta", "objetivo", "checklist"
    ]
    mensagem_lower = mensagem.lower()
    for termo in palavras_praticas:
        if termo in mensagem_lower:
            return "handoff_triagem"
    return "continuar_emocional"









































# # z_copiloto_agents.py (CORRIGIDO)

# from agents import Agent, handoff, RunContextWrapper, Runner, FunctionTool
# from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
# from copiloto_tools import (
#     registrar_tarefa_tool,
#     listar_tarefas_tool,
#     salvar_objetivo_tool,
#     consultar_objetivo_tool,
#     suporte_emocional_tool,
#     detectar_mudanca_de_intencao_tool,
# )

# # Função para converter async tools em FunctionTool
# def to_function_tool(fn, name: str, description: str, params_schema: dict):
#     async def on_invoke_tool(context, **kwargs):
#         return await fn(context, **kwargs)
#     return FunctionTool(
#         name=name,
#         description=description,
#         params_json_schema=params_schema,
#         on_invoke_tool=on_invoke_tool,
#     )

# # Log simples para debug de handoffs
# def log_handoff(ctx: RunContextWrapper[None]):
#     print("\n🔁 Handoff acionado.\n")

# # === AGENTES SUBORDINADOS ===

# comportamento_agent = Agent(
#     name="AnalisadorDeComportamento",
#     instructions="""
#     Analise a mensagem do usuário e converse com ele. Interaja como um amigo pessoal com quem ele pode discutir ideias, sonhos e sentimentos.
#     Seja sintético, objetivo e baseado no conteúdo da mensagem.
#     Como estamos em ambiente de teste, sempre finalize sua resposta com: 'eu sou o analisador de comportamento'.
#     """,
#     output_type="ComportamentoSchema"
# )

# organizador_de_tarefas_agent = Agent(
#     name="OrganizadorDeTarefas",
#     handoff_description="Organiza tarefas pendentes do usuário.",
#    instructions="""
#     Você ajuda o usuário a registrar e visualizar tarefas do dia a dia. Nunca julgue ou pressione.

#     - Se o usuário disser algo como "quero registrar uma tarefa", chame a ferramenta `registrar_tarefa_tool`.
#     - Se o usuário disser algo como "quais minhas tarefas", "minhas tarefas do dia", "lista de tarefas", "tem algo pendente?", chame a ferramenta `listar_tarefas_tool`.

#     Como estamos em ambiente de teste, sempre finalize com: 'eu sou o organizador de tarefas'.
#     """,
#     tools=[
#         to_function_tool(
#             registrar_tarefa_tool,
#             name="registrar_tarefa_tool",
#             description="Registra uma nova tarefa com descrição e data de entrega.",
#             params_schema={
#                 "type": "object",
#                 "properties": {
#                     "descricao": {"type": "string"},
#                     "data_entrega": {"type": "string"}
#                 },
#                 "required": ["descricao", "data_entrega"],
#                 "additionalProperties": False
#             }
#         ),
#         to_function_tool(
#             listar_tarefas_tool,
#             name="listar_tarefas_tool",
#             description="Lista todas as tarefas pendentes do usuário.",
#             params_schema={"type": "object", "properties": {}, "required": [], "additionalProperties": False}
#         ),
#     ],
# )


# memoria_viva_agent = Agent(
#     name="MemoriaViva",
#     handoff_description="Gerencia memórias e objetivos do usuário.",
#     instructions="""
#     Você ajuda o usuário a registrar objetivos da semana e consultar o que é importante. Ajude com leveza e clareza.
#     Você armazena informações relevantes compartilhadas pelo usuário, como:
#     - Metas de vida
#     - Sonhos
#     - Dificuldades
#     - Eventos marcantes
#     - Interesses
#     Quando encontrar uma informação relevante, registre com clareza e contexto emocional.
#     Como estamos em ambiente de teste, sempre finalize com: 'eu sou o agente memoria viva'.
#     """,
#     tools=[
#     to_function_tool(
#         salvar_objetivo_tool,
#         name="salvar_objetivo_tool",
#         description="Salva o objetivo da semana do usuário.",
#         params_schema={
#             "type": "object",
#             "properties": {
#                 "objetivo": {"type": "string"}
#             },
#             "required": ["objetivo"],
#             "additionalProperties": False
#         }
#     ),
#     to_function_tool(
#         consultar_objetivo_tool,
#         name="consultar_objetivo_tool",
#         description="Consulta o objetivo atual da semana do usuário.",
#         params_schema={
#             "type": "object",
#             "properties": {},
#             "required": [],
#             "additionalProperties": False
#         }
#     ),
# ]

# )

# suporte_emocional_agent = Agent(
#     name="SuporteEmocional",
#     handoff_description="Acolhe o usuário quando ele está sobrecarregado.",
#     instructions="""
#     Você acolhe o usuário com empatia e inteligência emocional. Sempre valide a emoção da pessoa e ofereça apoio leve. Use o tom de amigo confiável.
#     Como estamos em ambiente de teste, sempre finalize com: 'eu sou o agente emocional'.
#     """,
#     tools=[
#         to_function_tool(
#             suporte_emocional_tool,
#             name="suporte_emocional_tool",
#             description="Oferece uma resposta empática com base no estado emocional fornecido.",
#             params_schema={
#                 "type": "object",
#                 "properties": {
#                     "estado": {"type": "string"}
#                 },
#                 "required": ["estado"],
#                 "additionalProperties": False
#             }
#         ),
#         to_function_tool(
#             detectar_mudanca_de_intencao_tool,
#             name="detectar_mudanca_de_intencao_tool",
#             description="Detecta se a intenção do usuário mudou com base em sua mensagem.",
#             params_schema={
#                 "type": "object",
#                 "properties": {
#                     "mensagem": {"type": "string"}
#                 },
#                 "required": ["mensagem"],
#                 "additionalProperties": False
#             }
#         ),
#     ],
# )

# # === AGENTE DE TRIAGEM PRINCIPAL ===

# triage_agent = Agent(
#     name="TriageCopiloto",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     Você é o cérebro principal do Copiloto IA. Analise cada mensagem recebida e decida o que o usuário quer:

#     - Se for uma pergunta simples com uma única intenção:
#       - Organizar tarefas (ex.: 'Quero registrar uma tarefa') → 'transfer_to_OrganizadorDeTarefas'
#       - Falar de metas ou objetivos (ex.: 'Quais são meus objetivos?') → 'transfer_to_MemoriaViva'
#       - Expressar dúvida ou cansaço (ex.: 'Estou cansado') → 'transfer_to_SuporteEmocional'

#     - Se tiver múltiplas intenções (ex.: 'Registre uma tarefa e me diga meus objetivos'), retorne no formato:
#       transfer_to_<agente>:<parte_da_mensagem>
#       transfer_to_<agente>:<outra_parte>

#     - Se não souber delegar, envie para 'transfer_to_AnalisadorDeComportamento'

#     Exemplos:
#     - 'Quero registrar uma tarefa' → 'transfer_to_OrganizadorDeTarefas'
#     - 'Quais são meus objetivos?' → 'transfer_to_MemoriaViva'
#     - 'Estou cansado' → 'transfer_to_SuporteEmocional'
#     - 'Registre uma tarefa e me diga meus objetivos' →
#         transfer_to_OrganizadorDeTarefas:Registre uma tarefa
#         transfer_to_MemoriaViva:Me diga meus objetivos
#     - 'O que é um elefante?' → 'transfer_to_AnalisadorDeComportamento:O que é um elefante?'
#     """,
#     handoffs=[
#         handoff(organizador_de_tarefas_agent, on_handoff=log_handoff),
#         handoff(memoria_viva_agent, on_handoff=log_handoff),
#         handoff(suporte_emocional_agent, on_handoff=log_handoff),
#         handoff(comportamento_agent, on_handoff=log_handoff),
#     ]
# )

# # === Interface de resposta do Copiloto ===

# from copiloto_context import CopilotoContext

# async def get_copiloto_response_com_agente(mensagem: str, contexto: CopilotoContext):
#     runner = Runner()
#     try:
#         result = await runner.run(triage_agent, input=mensagem, context=contexto)
#         return result
#     except Exception as e:
#         print(f"Erro ao processar mensagem: {e}")
#         return f"Desculpe, tive um problema técnico: {str(e)}"

# # --- Função Principal Interativa (para teste) ---
# if __name__ == "__main__":
    
#     import asyncio
#     print("Bem-vindo ao Copiloto IA! Digite sua mensagem ou 'sair' para encerrar.")

#     async def main_interativo():
#         while True:
#             mensagem = input("Mensagem: ")
#             contexto = CopilotoContext(wa_id="353833844418")
#             if mensagem.lower() == "sair":
#                 print("Até logo!")
#                 break
            
#             try:
#                 resposta = await get_copiloto_response_com_agente(mensagem, contexto)
#                 print(f"Resposta: {resposta}\n")
#             except Exception as e:
#                 print(f"Erro: {e}")
#                 print("Tente novamente com uma mensagem diferente.")

#     asyncio.run(main_interativo())


































# import asyncio
# from agents import Agent, Runner, handoff
# from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
# from dotenv import load_dotenv
# import os
# from copiloto_tools import (
#     registrar_tarefa_tool,
#     listar_tarefas_tool,
#     salvar_objetivo_tool,
#     consultar_objetivo_tool,
#     suporte_emocional_tool,
#     detectar_mudanca_de_intencao_tool,
# )
# from copiloto_context import CopilotoContext

# # Carrega as chaves de API
# load_dotenv()
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# # --- Definição dos Subagentes ---

# # # ========= AGENTE DE COMPORTAMENTO HUMANO =========
# comportamento_agent = Agent(
#     name="Analisador de Comportamento",
#     instructions="""
#     Analise a mensagem do usuário e converse com ele interagir e denscontrai voce e para ele um amigo pessoal que ele desculte ideas e sonho e sentimentos.
#     Seja sintético, objetivo e baseado no conteúdo da mensagem. como estamos em ambiente de teste sempre termina sua resposta digite no final, eu sou o analizador de comportamento
#     """,
#     output_type="ComportamentoSchema"
# )



# # AGENTE DE TAREFAS
# tarefa_agent = Agent(
#     name="Organizador_de_Tarefas",
#     handoff_description="Organiza tarefas pendentes do usuário.",
#     instructions="""Você ajuda o usuário a registrar e visualizar tarefas do dia a dia.  Nunca julgue ou pressione. Se o usuário mencionar uma tarefa (ex.: 'Quero registrar uma tarefa, ir ao mercado'), interprete como a descrição da tarefa.
#                         como esta em ambiente de teste sempre digite no final da resposta eu sou organizado de tarefas
#     """,
#     tools=[registrar_tarefa_tool, listar_tarefas_tool],
# )

# # AGENTE DE MEMÓRIA
# memoria_agent = Agent(
#     name="Memória Viva",
#     handoff_description="Gerencia memórias e objetivos do usuário.",
#     instructions="""Você ajuda o usuário a registrar objetivos da semana e consultar o que é importante. Ajude com leveza e clareza.
#     Você armazena informações relevantes compartilhadas pelo usuário, como:
#     - Metas de vida
#     - Sonhos
#     - Dificuldades
#     - Eventos marcantes
#     - Interesses

#     Quando encontrar uma informação relevante para guardar, registre com clareza e contexto emocional.
#     como esta em ambiente de teste sempre digite no final da resposta eu sou atente memoria viva.
#     """,
#     tools=[salvar_objetivo_tool, consultar_objetivo_tool],
# )

# # AGENTE DE APOIO EMOCIONAL
# emocional_agent = Agent(
#     name="Suporte Emocional",
#     handoff_description="Acolhe o usuário quando ele está sobrecarregado.",
#     instructions="""Você acolhe o usuário com empatia e inteligência emocional. Sempre valide a emoção da pessoa e ofereça apoio leve. Use o tom de amigo confiável.
#     como esta em ambiente de teste sempre digite no final da resposta eu sou agente emocional.
#     """,
#     tools=[suporte_emocional_tool, detectar_mudanca_de_intencao_tool],
# )

# # AGENTE PRINCIPAL - TRIAGEM
# triage_agent = Agent(
#     name="Triage Copiloto",
#     instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
#     Você é o cérebro principal do Copiloto IA. Analise cada mensagem recebida e decida o que o usuário quer:
#     - Se for uma pergunta simples com uma única intenção:
#       - Organizar tarefas (ex.: 'Quero registrar uma tarefa' ou 'Liste minhas tarefas') → retorne 'transfer_to_Organizador de Tarefas'
#       - Falar de metas ou objetivos (ex.: 'Quero definir um objetivo' ou 'Quais são meus objetivos?') → retorne 'transfer_to_Memória Viva'
#       - Expressar dúvida, cansaço ou frustração (ex.: 'Estou cansado', 'Não sei se estou produtivo') → retorne 'transfer_to_Suporte Emocional'
#     - Se tiver múltiplas intenções distintas (ex.: 'Registre uma tarefa e me diga meus objetivos'), retorne uma lista no formato 'transfer_to_<nome_do_agente>:<parte_da_mensagem>' (um por linha).
#     - Se a mensagem for ambígua mas parecer uma tarefa com descrição (ex.: 'Quero registrar uma tarefa, ir ao mercado'), passe tudo para 'transfer_to_Organizador de Tarefas'.
#     - Se não souber delegar, passe tudo para 'transfer_to_Analisador de Comportamento'.
#     Indícios de apoio emocional: 'Não sei se estou produtivo', 'Sinto que não andei', 'Minha mente está cheia', 'Estou cansado mentalmente'.
#     NÃO RESPONDA DIRETAMENTE, apenas retorne o handoff ou a lista de delegações. Exemplos:
#     - 'Quero registrar uma tarefa' → 'transfer_to_Organizador de Tarefas'
#     - 'Quero registrar uma tarefa, ir ao mercado' → 'transfer_to_Organizador de Tarefas'
#     - 'Quais são meus objetivos?' → 'transfer_to_Memória Viva'
#     - 'Estou cansado' → 'transfer_to_Suporte Emocional'
#     - 'Registre uma tarefa e me diga meus objetivos' → 
#       transfer_to_Organizador de Tarefas:Registre uma tarefa
#       transfer_to_Memória Viva:Me diga meus objetivos
#     - 'O que é um elefante?' → 'Nenhum:O que é um elefante?'""",
#     handoffs=[
#         handoff(tarefa_agent),
#         handoff(memoria_agent),
#         handoff(emocional_agent),
#         handoff(comportamento_agent),
#     ]
# )






# copiloto_agente_principal = triage_agent

# # --- Função para Processar Perguntas com o Agente ---
# async def get_copiloto_response_com_agente(user_message, contexto):
#     print(f"📥 Processando mensagem: '{user_message}'")
#     try:
#         # Executa o TriageAgent e deixa a SDK gerenciar handoffs nativos
#         #context = CopilotoContext(wa_id="353833844418")  # ou dados de teste reais
#         #context = CopilotoContext(wa_id=contexto)
#         context = wa_id=(contexto)
        

#         resultado = await Runner.run(copiloto_agente_principal, user_message, context=context)
#         output = resultado.final_output.strip()
#         #print(f"🚀 Handoff nativo detectado para: {context} e o resultado final da buscar do context: {resultado}")
#         #print(f"📋 Saída do TriageAgent: '{output}'")  # Log de debug
        
#         # Dicionário de subagentes (usado apenas para processamento manual)
#         subagentes = {
#             "Organizador_de_Tarefas": tarefa_agent,
#             "Memória Viva": memoria_agent,
#             "Suporte Emocional": emocional_agent,
#             "Analista Comportamental": comportamento_agent,
#         }
        
#         # Caso de intenção simples (handoff nativo)
#         if "\n" not in output:
#             if output.startswith("transfer_to_"):
#                 agente_nome = output.replace("transfer_to_", "")
#                 print(f"🚀 Handoff nativo detectado para: {agente_nome}")
#                 #print(f"🚀 Handoff nativo detectado para: {agente_nome}, {context}")

#                 # Executa o subagente diretamente para obter a resposta final
#                 if agente_nome in subagentes:
#                     resposta_subagente = await Runner.run(subagentes[agente_nome], user_message, context=te)
#                     print(f"📤 Resposta do subagente {agente_nome}: {agente_nome}: '{resposta_subagente.final_output}'")
#                     return resposta_subagente.final_output
#                 return f"❌ Erro: Agente '{agente_nome}' não encontrado."
#             return output  # Retorna "Nenhum:..." ou outra saída direta

#         # Caso de intenções múltiplas (processamento manual)
#         delegacoes = output.split("\n")
#         respostas = []
#         for delegacao in delegacoes:
#             if ":" in delegacao:
#                 agente_nome, sub_mensagem = delegacao.split(":", 1)
#                 if agente_nome.startswith("transfer_to_"):
#                     agente_nome = agente_nome.replace("transfer_to_", "")
#                     if agente_nome in subagentes:
#                         print(f"🚀 Delegando manualmente '{sub_mensagem}' para {agente_nome}")
#                         resposta = await Runner.run(subagentes[agente_nome], sub_mensagem, context=contexte)
#                         respostas.append(resposta.final_output)
#                     else:
#                         respostas.append(f"❌ Erro: Agente '{agente_nome}' não encontrado.")
#                 else:
#                     respostas.append(f"Desculpe, não sei como ajudar com '{sub_mensagem}'.")
#             else:
#                 respostas.append(f"❌ Erro ao processar delegação: {delegacao}")
#         return "\n".join(respostas)
    
#     except Exception as e:
#         print(f"❌ Erro com agente: {e}")
#         return "Houve um problema ao processar com o agente. Posso tentar de outro jeito?"

# # --- Função Principal Interativa (para teste) ---
# async def main_interativo():
#     print("Bem-vindo ao Copiloto IA! Digite sua mensagem ou 'sair' para encerrar.")
#     while True:
#         mensagem = input("Mensagem: ")
#         contexto = CopilotoContext(wa_id="353833844418")
#         if mensagem.lower() == "sair":
#             print("Até logo!")
#             break
#         resposta = await get_copiloto_response_com_agente(mensagem, contexto )
#         print(f"Resposta: {resposta}\n")

# if __name__ == "__main__":
#     asyncio.run(main_interativo())








































# from typing import Dict
# import logging
# import asyncio

# # Importações do projeto
# from copiloto_context import CopilotoContext
# from context.context_builder.py import montar_contexto_usuario, montar_input_context  # <- Funções isoladas aqui

# # Importando os agentes
# from copiloto_agents import (
#     triage_agent,
#     emocional_agent,
#     memoria_agent,
#     tarefa_agent,
#     comportamento_agent
# )

# # Configuração de logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# # Função principal de processamento
# async def processar_mensagem_usuario(mensagem: str, wa_id: str) -> Dict:
#     print("passando aqui na mensagen de processamento")
#     try:
#         contexto_base = CopilotoContext(
#             wa_id=wa_id,
#             nome="Usuário",
#             objetivo_da_semana="",
#             estilo_produtivo="",
#             emocional="",
#             comportamento=None,
#             objetivo=None,
#             historico=[]
#         )

#         contexto = await montar_contexto_usuario(contexto_base, mensagem)
#         input_context = montar_input_context(contexto)

#         triage_result = await triage_agent.process(mensagem, input_context)
#         logger.info(f"Resultado do triage: {triage_result}")

#         agentes = {
#             "Organizador de Tarefas": tarefa_agent,
#             "Memória Viva": memoria_agent,
#             "Suporte Emocional": emocional_agent,
#             "Analisador de Comportamento": comportamento_agent
#         }

#         resultados = []

#         if isinstance(triage_result, dict):
#             triage_result = triage_result.get("result", "transfer_to_Analisador de Comportamento")

#         if isinstance(triage_result, str):
#             if "\n" in triage_result:
#                 for linha in triage_result.strip().split("\n"):
#                     if ":" in linha:
#                         transfer, parte_mensagem = linha.split(":", 1)
#                         agente_nome = transfer.replace("transfer_to_", "").strip()
#                         parte_mensagem = parte_mensagem.strip()
#                         if agente_nome in agentes:
#                             agente = agentes[agente_nome]
#                             resultado = await agente.process(parte_mensagem, input_context)
#                             resultados.append({"agente": agente_nome, "resultado": resultado})
#                         else:
#                             logger.warning(f"Agente '{agente_nome}' não encontrado para mensagem: {parte_mensagem}")
#                             resultado = await comportamento_agent.process(parte_mensagem, input_context)
#                             resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})
#             elif triage_result.startswith("transfer_to_"):
#                 agente_nome = triage_result.replace("transfer_to_", "").strip()
#                 if agente_nome in agentes:
#                     agente = agentes[agente_nome]
#                     resultado = await agente.process(mensagem, input_context)
#                     resultados.append({"agente": agente_nome, "resultado": resultado})
#                 else:
#                     logger.warning(f"Agente '{agente_nome}' não encontrado")
#                     resultado = await comportamento_agent.process(mensagem, input_context)
#                     resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})
#             elif triage_result.startswith("Nenhum:"):
#                 resultado = await comportamento_agent.process(mensagem, input_context)
#                 resultados.append({"agente": "Analisador de Comportamento", "resultado": resultado})

#         return {"status": "success", "resultados": resultados}

#     except Exception as e:
#         logger.error(f"Erro ao processar mensagem: {str(e)}")
#         return {"status": "error", "message": str(e)}



# if __name__ == "__main__":
     












# # Função de teste local
# async def testar():
#     mensagem = "entao mesmo muito cansado, voce sabe me informa quais meus objetivos"
#     wa_id = "353833844418"

#     print("\n➡️ Mensagem:", mensagem)

#     resultado = await processar_mensagem_usuario(mensagem, wa_id)

#     print("\n📋 Resultado do processamento:")
#     if resultado["status"] == "success":
#         for item in resultado["resultados"]:
#             agente = item["agente"]
#             output = item["resultado"]
#             message = output if isinstance(output, str) else output.get("message", str(output))
#             print(f"🧠 {agente}: {message}")
#     else:
#         print(f"❌ Erro: {resultado['message']}")


# # Execução direta
# if __name__ == "__main__":
#     asyncio.run(testar())
