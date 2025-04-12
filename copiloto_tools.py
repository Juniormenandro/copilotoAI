# from copiloto_context import CopilotoContext
# from db.tarefas import registrar_tarefa, listar_tarefas
# from db.memorias import salvar_memoria, consultar_objetivo_da_semana

# # ✅ REGISTRAR TAREFA
# async def registrar_tarefa_tool(
#     context: CopilotoContext,  # Removido RunContextWrapper
#     descricao: str,
#     data_entrega: str | None = None,
# ) -> str:
#     wa_id = context.wa_id
#     registrar_tarefa(wa_id, descricao, data_entrega)
#     return f"Tarefa registrada com sucesso: {descricao}"

# # 📋 LISTAR TAREFAS
# async def listar_tarefas_tool(
#     context: CopilotoContext,  # Removido RunContextWrapper
# ) -> str:
#     wa_id = context.wa_id
#     tarefas = listar_tarefas(wa_id)
#     if not tarefas:
#         return "🎉 Você não tem tarefas pendentes no momento!"
#     resposta = "📋 Suas tarefas:\n"
#     for t in tarefas:
#         entrega = t.get("data_entrega", "sem data")
#         resposta += f"- {t['descricao']} (entrega: {entrega})\n"
#     return resposta

# # 🎯 SALVAR OBJETIVO DA SEMANA
# async def salvar_objetivo_tool(
#     context: CopilotoContext,  # Removido RunContextWrapper
#     objetivo: str
# ) -> str:
#     wa_id = context.wa_id
#     salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
#     return "🎯 Objetivo da semana salvo com sucesso!"

# # 🔍 CONSULTAR OBJETIVO
# async def consultar_objetivo_tool(
#     context: CopilotoContext  # Removido RunContextWrapper
# ) -> str:
#     wa_id = context.wa_id
#     objetivo = consultar_objetivo_da_semana(wa_id)
#     if objetivo:
#         return f"🎯 Seu objetivo da semana é: {objetivo}"
#     return "Ainda não encontrei nenhum objetivo da semana registrado."

# # ❤️ APOIO EMOCIONAL (baseado em palavra-chave)
# async def suporte_emocional_tool(
#     context: CopilotoContext,  # Removido RunContextWrapper
#     estado: str
# ) -> str:
#     frases = {
#         "ansioso": "Respira... Você está indo bem. Vamos dar um passo de cada vez?",
#         "cansado": "Se cuida, tá? Você não precisa dar conta de tudo hoje. Descanso também é estratégia.",
#         "frustrado": "Se as coisas não saíram como queria, tudo bem. Você tentou. E só de tentar, já tá na frente.",
#     }
#     return frases.get(estado.lower(), "Tô contigo. Quer conversar sobre isso?")

# # 🧠 DETECÇÃO DE MUDANÇA DE INTENÇÃO
# async def detectar_mudanca_de_intencao_tool(mensagem: str) -> str:
#     palavras_praticas = [
#         "tenho que", "preciso", "vou", "devo", "lembrete", "entregar", "organizar",
#         "lista", "tarefa", "meta", "prazo", "orçamento", "proposta", "objetivo", "checklist"
#     ]
#     mensagem_lower = mensagem.lower()
#     for termo in palavras_praticas:
#         if termo in mensagem_lower:
#             return "handoff_triagem"
#     return "continuar_emocional"



from copiloto_context import CopilotoContext
from db.tarefas import registrar_tarefa, listar_tarefas
from db.memorias import salvar_memoria, consultar_objetivo_da_semana

# ✅ REGISTRAR TAREFA
def registrar_tarefa_fn(
    context: CopilotoContext,
    descricao: str,
    data_entrega: str,
) -> str:
    wa_id = context.wa_id
    registrar_tarefa(wa_id, descricao, data_entrega)
    return f"Tarefa registrada com sucesso: {descricao}"

# 📋 LISTAR TAREFAS
def listar_tarefas_fn(
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
def salvar_objetivo_fn(
    context: CopilotoContext,
    objetivo: str
) -> str:
    wa_id = context.wa_id
    salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
    return "🎯 Objetivo da semana salvo com sucesso!"

# 🔍 CONSULTAR OBJETIVO
def consultar_objetivo_fn(
    context: CopilotoContext
) -> str:
    wa_id = context.wa_id
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return f"🎯 Seu objetivo da semana é: {objetivo}"
    return "Ainda não encontrei nenhum objetivo da semana registrado."

# ❤️ APOIO EMOCIONAL
def suporte_emocional_fn(
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
def detectar_mudanca_de_intencao_fn(
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