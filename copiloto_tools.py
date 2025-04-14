# copiloto_tools.py
from db.tarefas import registrar_tarefa, listar_tarefas
from db.memorias import salvar_memoria, consultar_objetivo_da_semana

# ✅ REGISTRAR TAREFA
def registrar_tarefa_tool(wa_id: int, descricao: str, data_entrega: str) -> dict:
    print(f"📌 Salvando tarefa para: {wa_id}")  # Adiciona isso se ainda não tiver
    registrar_tarefa(wa_id, descricao, data_entrega)
    return {"message": f"Tarefa registrada com sucesso: {descricao}"}

# 📋 LISTAR TAREFAS
def listar_tarefas_tool(wa_id: int) -> dict:
    print(wa_id)
    tarefas = listar_tarefas(wa_id)
    if not tarefas:
        return {"message": "🎉 Você não tem tarefas pendentes no momento!"}
    resposta = "📋 Suas tarefas:\n"
    for t in tarefas:
        entrega = t.get("data_entrega", "sem data")
        resposta += f"- {t['descricao']} (entrega: {entrega})\n"
    return {"message": resposta.strip()}

# 🎯 SALVAR OBJETIVO DA SEMANA
def salvar_objetivo_tool(wa_id: int, objetivo: str) -> dict:
    salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
    print(f"📌 Salvando salvando memoria para: {wa_id}")
    return {"message": "🎯 Objetivo da semana salvo com sucesso!"}

# 🔍 CONSULTAR OBJETIVO
def consultar_objetivo_tool(wa_id: int) -> dict:
    print(f"📌 consutando  memoria para: {wa_id}")
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return {"message": f"🎯 Seu objetivo da semana é: {objetivo}"}
    return {"message": "Ainda não encontrei nenhum objetivo da semana registrado."}

# ❤️ APOIO EMOCIONAL
def suporte_emocional_tool(estado: str) -> dict:
    frases = {
        "ansioso": "Respira... Você está indo bem. Vamos dar um passo de cada vez?",
        "cansado": "Se cuida, tá? Você não precisa dar conta de tudo hoje. Descanso também é estratégia.",
        "frustrado": "Se as coisas não saíram como queria, tudo bem. Você tentou. E só de tentar, já tá na frente.",
    }
    return {"message": frases.get(estado.lower(), "Tô contigo. Quer conversar sobre isso?")}

# 🧠 DETECÇÃO DE MUDANÇA DE INTENÇÃO
def detectar_mudanca_de_intencao_tool(mensagem: str) -> dict:
    palavras_praticas = [
        "tenho que", "preciso", "vou", "devo", "lembrete", "entregar", "organizar",
        "lista", "tarefa", "meta", "prazo", "orçamento", "proposta", "objetivo", "checklist"
    ]
    mensagem_lower = mensagem.lower()
    for termo in palavras_praticas:
        if termo in mensagem_lower:
            return {"message": "handoff_triagem"}
    return {"message": "continuar_emocional"}

