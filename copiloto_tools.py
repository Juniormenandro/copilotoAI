
# copiloto_tools.py (ATUALIZADO)
from db.tarefas import registrar_tarefa, listar_tarefas, concluir_tarefa, adiar_tarefa
from db.memorias import salvar_memoria, consultar_objetivo_da_semana

from utils.data import interpretar_data_relativa  
from datetime import datetime



# # ✅ REGISTRAR TAREFA
# def registrar_tarefa_tool(wa_id: int, descricao: str, data_entrega: str) -> dict:
#     print(f"📌 Salvando tarefa para: {wa_id}")

#     # Converte a data relativa (ex: "amanhã") para o formato YYYY-MM-DD
#     data_formatada = interpretar_data_relativa(data_entrega)
#     if not data_formatada:
#         return {"message": "❌ Não entendi a data que você informou. Tente algo como 'amanhã' ou 'sexta-feira'."}

#     registrar_tarefa(wa_id, descricao, data_entrega=data_formatada)

#     return {
#         "message": f"Tarefa registrada com sucesso: \"{descricao}\" para {data_formatada}."
#     }





# ✅ REGISTRAR TAREFA
def registrar_tarefa_tool(wa_id: int, descricao: str, data_entrega: str) -> dict:
    print(f"📌 Salvando tarefa para: {wa_id}")

    # Converte a data relativa (ex: "amanhã") para o formato YYYY-MM-DD
    data_formatada = interpretar_data_relativa(data_entrega)
    if not data_formatada:
        return {"message": "❌ Não entendi a data que você informou. Tente algo como 'amanhã' ou 'sexta-feira'."}

    registrar_tarefa(wa_id, descricao, data_entrega=data_formatada)

    return {
        "message": f"Tarefa registrada com sucesso: \"{descricao}\" para {data_formatada}."
    }

# 📋 LISTAR TAREFAS
def listar_tarefas_tool(wa_id: int) -> dict:
    print(f"📋 Listando tarefas para {wa_id}")
    tarefas = listar_tarefas(wa_id)
    if not tarefas:
        return {"message": "🎉 Você não tem tarefas pendentes no momento!"}
    
    tarefas_hoje, tarefas_futuras, tarefas_vencidas = [], [], []
    from datetime import date

    for t in tarefas:
        entrega = t.get("data_entrega")
        descricao = t["descricao"]

        if not entrega:
            tarefas_futuras.append(f"- {descricao}")
        else:
            entrega_date = date.fromisoformat(entrega)
            hoje = date.today()
            if entrega_date < hoje:
                tarefas_vencidas.append(f"- {descricao} (Vencida em: {entrega_date.strftime('%Y-%m-%d')})")
            elif entrega_date == hoje:
                tarefas_hoje.append(f"- {descricao}")
            else:
                tarefas_futuras.append(f"- {descricao}")

    resposta = "Aqui estão suas tarefas pendentes:\n"
    if tarefas_hoje:
        resposta += "\n📆 **Hoje:**\n" + "\n".join(tarefas_hoje)
    if tarefas_futuras:
        resposta += "\n\n📅 **Futuras:**\n" + "\n".join(tarefas_futuras)
    if tarefas_vencidas:
        resposta += "\n\n⚠️ **Atrasadas:**\n" + "\n".join(tarefas_vencidas)

    return {"message": resposta.strip() + "\n\neu sou o organizador e memória viva."}

# ✅ CONCLUIR TAREFA
def concluir_tarefa_tool(wa_id: int, descricao: str) -> dict:
    sucesso = concluir_tarefa(wa_id, descricao)
    if sucesso:
        return {"message": f'A tarefa "{descricao}" foi marcada como concluída com sucesso. Se precisar de algo mais, estou aqui para ajudar!\n\n**"eu sou o organizador e memória viva."**'}
    return {"message": f'Parece que não encontrei nenhuma tarefa chamada "{descricao}" para concluir. Pode verificar se o nome está correto ou se já foi concluída anteriormente? Estou aqui para ajudar!\n\n**"eu sou o organizador e memória viva."**'}

# ✅ ADIAR TAREFA
def adiar_tarefa_tool(wa_id: int, descricao: str, nova_data: str) -> dict:
    sucesso = adiar_tarefa(wa_id, descricao, nova_data)
    if sucesso:
        return {"message": f'A tarefa "{descricao}" foi adiada para {nova_data}. Se precisar de mais alguma coisa, estou aqui! **"eu sou o organizador e memória viva."**'}
    return {"message": f'Parece que não encontrei uma tarefa chamada "{descricao}" para adiar. Talvez o nome esteja um pouco diferente. Quer tentar novamente ou verificar a lista de tarefas atuais?\n\n**"eu sou o organizador e memória viva."**'}

# 🎯 SALVAR OBJETIVO
def salvar_objetivo_tool(wa_id: int, objetivo: str) -> dict:
    salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
    print(f"📌 Salvando memória para: {wa_id}")
    return {"message": "🎯 Objetivo da semana salvo com sucesso!"}

# 🔍 CONSULTAR OBJETIVO
def consultar_objetivo_tool(wa_id: int) -> dict:
    print(f"📌 Consultando memória para: {wa_id}")
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return {"message": f"🎯 Seu objetivo da semana é: {objetivo}"}
    return {"message": "Ainda não encontrei nenhum objetivo da semana registrado."}

# 🔍 VER CONTEXTO
async def ver_contexto_tool(confirmacao: str, context=None):
    try:
        print("🧪 Entrou na função ver_contexto_tool")
        print("📦 Context recebido:", context)

        if confirmacao.lower() != "sim":
            return "Beleza! Não vou mostrar o contexto agora. 😉"

        contexto_dict = getattr(context, "context", None)
        if not contexto_dict or not isinstance(contexto_dict, dict):
            return "❌ Não consegui acessar o contexto de forma adequada."

        comportamento = contexto_dict.get("comportamento", {})
        objetivo = contexto_dict.get("objetivo", {})
        historico = contexto_dict.get("historico", [])

        resumo = "📌 **Contexto Atual Recebido:**\n"

        if comportamento:
            resumo += f"\n🧠 **Comportamento:**\n- Tom: {comportamento.get('tom_ideal', 'N/A')}\n- Gatilhos: {', '.join(comportamento.get('gatilhos', []))}\n- Estilo: {comportamento.get('estilo', 'N/A')}\n"

        if objetivo:
            resumo += f"\n🎯 **Objetivo da Semana:** {objetivo.get('descricao', 'Não informado')}\n"

        if historico:
            resumo += "\n📜 **Últimas Mensagens:**\n"
            for h in historico[-5:]:
                tipo = "👤" if h.get("tipo") == "usuario" else "🤖"
                resumo += f"{tipo} {h.get('mensagem')}\n"

        return resumo or "🧐 Contexto está vazio ou não disponível."

    except Exception as e:
        return f"⚠️ Erro ao acessar contexto: {str(e)}"
