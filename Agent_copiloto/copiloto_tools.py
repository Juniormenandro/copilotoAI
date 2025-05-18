# copiloto_tools.py (VERSÃO FINAL COM CONTEXTO ATUALIZADO)
import json
from db.tarefas import registrar_tarefa, listar_tarefas, concluir_tarefa, adiar_tarefa
from db.memorias import salvar_memoria, consultar_objetivo_da_semana
from utils.data import interpretar_data_relativa
from datetime import date, datetime, timezone
from dateutil import parser # type: ignore
from agents import FunctionTool # type: ignore
import inspect
# 🧠 Nova função para interpretar data e extrair observações ========================
def parse_data_inteligente(texto: str):
    if not texto:
        return None, None
    partes = texto.split(" ")
    for i in range(len(partes), 0, -1):
        tentativa = " ".join(partes[:i])
        data = interpretar_data_relativa(tentativa)
        if data:
            observacao = " ".join(partes[i:]).strip()
            return data, observacao or None
    return None, texto

# ======================== ✅  ========================
def to_function_tool(fn, name: str, description: str, params_schema: dict):
    async def on_invoke_tool(context, tool_input):
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except Exception:
                tool_input = {}

        if "context" in inspect.signature(fn).parameters:
            return await fn(**tool_input)
        return await fn(**tool_input)

    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=params_schema,
        on_invoke_tool=on_invoke_tool
    )


# ============== ✅ REGISTRAR TAREFA ==========================
async def registrar_tarefa_tool(wa_id: int, descricao: str = None, data_entrega: str = None) -> dict:
    if descricao and data_entrega:
        data_formatada, observacao_extra = parse_data_inteligente(data_entrega)
        if not data_formatada:
            return {
                "message": f"Parece que houve um problema para registrar a data como \"{data_entrega}\". Que tal apenas 'amanhã'? Posso registrar assim."
            }
        registrar_tarefa(wa_id, descricao, data_entrega=data_formatada)
        return {
            "message": f"Tarefa registrada com sucesso para {data_entrega}: \"{descricao}\".\n\nSe precisar de mais alguma coisa, estou por aqui!\n\n**organizador do Copiloto IA.**"
        }
    return {"message": "❌ Você precisa informar uma descrição e uma data para registrar a tarefa."}

registrar_tarefa_tool_func = to_function_tool(
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


# 📋 ============= LISTAR TAREFAS ========================
async def listar_tarefas_tool(wa_id: int) -> dict:
    tarefas = listar_tarefas(wa_id)
    if not tarefas:
        return {"message": "🎉 Você não tem tarefas pendentes no momento!"}
    tarefas_hoje, tarefas_futuras, tarefas_vencidas = [], [], []
    for t in tarefas:
        entrega = t.get("data_entrega")
        descricao = t["descricao"]
        if not entrega:
            tarefas_futuras.append(f"- {descricao}")
        else:
            try:
                entrega_date = parser.parse(entrega).date()
            except Exception as e:
                print(f"❌ Erro ao interpretar data: {entrega} | Erro: {e}")
                continue
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
    return {"message": resposta.strip() + "\neu sou o organizador e memória viva."}

listar_tarefas_tool_func = to_function_tool(
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


# ======================== ✅ CONCLUIR TAREFA ========================
async def concluir_tarefa_tool(wa_id: int, descricao: str) -> dict:
    sucesso = concluir_tarefa(wa_id, descricao)
    if sucesso:
        return {"message": f'A tarefa "{descricao}" foi marcada como concluída com sucesso. Se precisar de algo mais, estou aqui para ajudar!\n\n**"eu sou o organizador e memória viva."**'}
    return {"message": f'Parece que não encontrei nenhuma tarefa chamada "{descricao}" para concluir. Pode verificar se o nome está correto ou se já foi concluída anteriormente? Estou aqui para ajudar!\n\n**"eu sou o organizador e memória viva."**'}

concluir_tarefa_tool_func = to_function_tool(
    concluir_tarefa_tool,
    name="concluir_tarefa_tool",
    description="Marca uma tarefa como concluída com base na descrição e no wa_id.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "descricao": {"type": "string"},
        },
        "required": ["wa_id", "descricao"],
        "additionalProperties": False,
    },
)


# ======================== ✅ ADIAR TAREFA ========================
async def adiar_tarefa_tool(wa_id: int, descricao: str, nova_data: str) -> dict:
    sucesso = adiar_tarefa(wa_id, descricao, nova_data)
    if sucesso:
        return {"message": f'A tarefa "{descricao}" foi adiada para {nova_data}. Se precisar de mais alguma coisa, estou aqui! **"eu sou o organizador e memória viva."**'}
    return {"message": f'Parece que não encontrei uma tarefa chamada "{descricao}" para adiar. Talvez o nome esteja um pouco diferente. Quer tentar novamente ou verificar a lista de tarefas atuais?\n\n**"eu sou o organizador e memória viva."**'}

adiar_tarefa_tool_func = to_function_tool(
    adiar_tarefa_tool,
    name="adiar_tarefa_tool",
    description="Adia uma tarefa existente para uma nova data de entrega.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"},
            "descricao": {"type": "string"},
            "nova_data": {"type": "string"},
        },
        "required": ["wa_id", "descricao", "nova_data"],
        "additionalProperties": False,
    },
)


# ======================== 🎯 SALVAR OBJETIVO ========================
async def salvar_objetivo_tool(wa_id: int, objetivo: str) -> dict:
    salvar_memoria(wa_id, "objetivo_da_semana", objetivo)
    return {"message": "🎯 Objetivo da semana salvo com sucesso!"}

salvar_objetivo_tool_func = to_function_tool(
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


# ======================== 🔍 CONSULTAR OBJETIVO ========================
async def consultar_objetivo_tool(wa_id: int) -> dict:
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return {"message": f"🎯 Seu objetivo da semana é: {objetivo}"}
    return {"message": "Ainda não encontrei nenhum objetivo da semana registrado."}

consultar_objetivo_tool_func = to_function_tool(
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
