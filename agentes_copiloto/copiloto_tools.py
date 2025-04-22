# copiloto_tools.py (VERSÃO FINAL COM CONTEXTO ATUALIZADO)
import json
from db.tarefas import registrar_tarefa, listar_tarefas, concluir_tarefa, adiar_tarefa
from db.memorias import salvar_memoria, consultar_objetivo_da_semana
from utils.data import interpretar_data_relativa
from context.sintetizar import salvar_contexto_usuario
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
     #  print(f"_🛠️ _ Tool recebida: {tool_input}")
        # print(f"_🚨_ tool_input final: {tool_input}")
        # print(f"_🚨_ context.context: {getattr(context, 'context', {})}")

       # 🔧 Corrige tool_input se vier como string
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except Exception:
                tool_input = {}


        # 🧠 Busca wa_id do contexto corretamente mesmo se aninhado
        context_dict = getattr(context, "context", {})
        wa_id_from_context = (
            context_dict.get("wa_id")
            or context_dict.get("contexto", {}).get("wa_id")
        )

        # ⚠️ Se ainda não achou, previne salvamento errado
        if wa_id_from_context:
            tool_input["wa_id"] = wa_id_from_context
          #  print(f"_🧠 _ wa_id forçado: {tool_input['wa_id']}")
        else:
            print("🚨 ERRO: wa_id ausente no contexto! Tool pode falhar ao salvar.")

        # print(f"_🛠️ _ tool_input final: {tool_input}")
        # print(f"_🛠️ _ context.context: {context_dict}")

        if "context" in inspect.signature(fn).parameters:
            return await fn(**tool_input, context=context)
        return await fn(**tool_input)


    return FunctionTool(
        name=name,
        description=description,
        params_json_schema=params_schema,
        on_invoke_tool=on_invoke_tool
    )


# ============== ✅ REGISTRAR TAREFA ==========================
async def registrar_tarefa_tool(wa_id: int, descricao: str = None, data_entrega: str = None, context: dict = {}) -> dict:
  #  print(f"_🛠️ _ Registrando tarefa para: {wa_id}")
    # print(interpretar_data_relativa("amanhã às 15h"))
    # print(interpretar_data_relativa("sexta-feira"))
    # print(interpretar_data_relativa("25 de abril"))
    # print(interpretar_data_relativa("daqui a 3 dias"))
    # Garante acesso correto ao contexto editável
    context_dict = context.context if hasattr(context, "context") else context
    if descricao and data_entrega:
        data_formatada, observacao_extra = parse_data_inteligente(data_entrega)
      #  print(f"_🛠️ _ 📦 Tarefa recebida: {descricao} | Data interpretada: {data_formatada}")
        if not data_formatada:
            return {
                "message": f"Parece que houve um problema para registrar a data como \"{data_entrega}\". Que tal apenas 'amanhã'? Posso registrar assim."
            }
      #  print(f"_🛠️ __💾_ Registrando tarefa no banco: {descricao} para {data_formatada}")
        from db.tarefas import registrar_tarefa
        registrar_tarefa(wa_id, descricao, data_entrega=data_formatada)
        context_dict.pop("tarefa_em_construcao", None)
        context_dict["agente_em_conversa"] = None
        return {
            "message": f"Tarefa registrada com sucesso para {data_entrega}: \"{descricao}\".\n\nSe precisar de mais alguma coisa, estou por aqui!\n\n**organizador do Copiloto IA.**"
        }
    # Se descrição sem data ainda
    if descricao and not data_entrega:
        context_dict["tarefa_em_construcao"] = {
            "descricao": descricao,
            "status": "aguardando_data"
        }
        return {
            "message": f"Entendi! Você quer registrar a tarefa \"{descricao}\". Para quando ela deve ser feita?"
        }
    # Se data sem descrição
    if data_entrega and not descricao:
        tarefa_pendente = context_dict.get("tarefa_em_construcao")
        if not tarefa_pendente:
            return {
                "message": "❌ Não encontrei uma tarefa pendente para agendar. Me diga o que você quer fazer primeiro."
            }
        descricao = tarefa_pendente["descricao"]
    # Caso final: confirmar tarefa pendente
    tarefa_pendente = context_dict.get("tarefa_em_construcao")
    if tarefa_pendente and tarefa_pendente.get("status") == "aguardando_confirmacao":
        descricao = tarefa_pendente["descricao"]
        data_formatada = tarefa_pendente["data_formatada"]
        registrar_tarefa(wa_id, descricao, data_entrega=data_formatada)
        context_dict.pop("tarefa_em_construcao", None)
        context_dict["agente_em_conversa"] = None
        return {
            "message": f"Tarefa confirmada e registrada: \"{descricao}\" para {data_formatada}.\n\n**eu sou o organizador e memória viva.**"
        }
    return {"message": "👀 Você disse 'sim', mas não encontrei uma tarefa pendente para confirmar."}
#======= registrar_tarefa chamada pelo Agent ================
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
   # print(f"_💾_ 📋 Listando tarefas para {wa_id}")
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
                entrega_date = parser.parse(entrega).date()  # <-- parse flexível
            except Exception as e:
                print(f"❌ Erro ao interpretar data: {entrega} | Erro: {e}")
                continue  # ignora essa tarefa com data inválida
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
#==========listar_tarefas chamada pelo agent ==================
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
#==========concluir_tarefa chamada pelo agent ==================
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
#========== adiar_tarefa chamada pelo agent ==================
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
   # print(f"_🛠️ __💾_ Salvando memória para: {wa_id}")
    return {"message": "🎯 Objetivo da semana salvo com sucesso!"}
#==========salvar_objetivo  chamada pelo agent ==================
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
   # print(f"_🛠️ _ Consultando memória para: {wa_id}")
    objetivo = consultar_objetivo_da_semana(wa_id)
    if objetivo:
        return {"message": f"🎯 Seu objetivo da semana é: {objetivo}"}
    return {"message": "Ainda não encontrei nenhum objetivo da semana registrado."}
#==========  chamada pelo agent ==================
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











# ======================== 🔍 VER CONTEXTO ========================
# =================== tools para o agente de emocional para teste de acesso ao context. 
async def ver_contexto_tool(confirmacao: str, context=None):
    try:
       # print("_🛠️ _ Entrou na função ver_contexto_tool")
      #  print("_🛠️ __📦_ Context recebido:", context)
        if confirmacao.lower() != "sim":
            return "Beleza! Não vou mostrar o contexto agora. 😉"
        contexto_dict = getattr(context, "context", None)
        if not contexto_dict or not isinstance(contexto_dict, dict):
            return "_🛠️ __📦_ ❌ Não consegui acessar o contexto de forma adequada."
        comportamento = contexto_dict.get("comportamento", {})
        objetivo = contexto_dict.get("objetivo", {})
        historico = contexto_dict.get("historico", [])
        resumo = "_🛠️ __📦_ 📌 **Contexto Atual Recebido:**\n"
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











#========= Função base que altera o contexto ===========================
async def _setar_em_andamento(wa_id=None, context=None):
    context_dict = context.context if hasattr(context, "context") else context
   # print(f"_🛠️ _ dentro da tools de conversa em andamento (wa_id: {wa_id})")

    if wa_id is None:
        wa_id = context_dict.get("wa_id")

    # 🧠 Corrigido: preservar agente mesmo se contexto for aninhado
    if isinstance(context_dict, dict):
        if "contexto" in context_dict:
            contexto_limpo = context_dict["contexto"]
            contexto_limpo["wa_id"] = wa_id
            if "agente_em_conversa" in context_dict:
                contexto_limpo["agente_em_conversa"] = context_dict["agente_em_conversa"]
        else:
            contexto_limpo = context_dict

        contexto_limpo["conversa_em_andamento"] = True
        contexto_limpo["ultima_interacao"] = datetime.now(timezone.utc)

       # print("_🛠️ __💾_ Salvar context. aqui pelo tools _setar_em_andamento", contexto_limpo.get("conversa_em_andamento"))
        await salvar_contexto_usuario(wa_id, contexto_limpo)
        return {"message": "Conversa marcada como em andamento com sucesso."}
    else:
        return {"message": "Erro: context inválido para marcação."}


# Registro oficial da tool com a função adaptada
marcar_conversa_em_andamento_tool = to_function_tool(
    fn=_setar_em_andamento,
    name="marcar_conversa_em_andamento",
    description="Marca que a conversa está em andamento (ativa) para o usuário.",
    params_schema={
        "type": "object",
        "properties": {
            "wa_id": {"type": "string"}
        },
        "required": ["wa_id"],
        "additionalProperties": False
    }
)






#=============Criação das tools de setar agente (usando a função acima)================
def criar_tool_setar_agente(nome_agente):
    async def setar_agente_em_conversa(wa_id: str, context):
        context_dict = context.context if hasattr(context, "context") else context
       # print(f"_🛠️ _ dentro da tools setar_agente_em_conversa (wa_id: {wa_id})")
        context_dict["agente_em_conversa"] = nome_agente
        context_dict["conversa_em_andamento"] = True
       # print("_🛠️ __💾_ Salvar context. aqui pelo tools setar_agente_em_conversa", context_dict.get("agente_em_conversa"))
        await salvar_contexto_usuario(wa_id, context_dict)
        return {"message": f"Agente definido como {nome_agente}."}
    return to_function_tool(
        fn=setar_agente_em_conversa,
        name="setar_agente_em_conversa",
        description=f"Define o agente atual como {nome_agente} no contexto do usuário.",
        params_schema={
            "type": "object",
            "properties": {
                "wa_id": {"type": "string"}
            },
            "required": ["wa_id"],
            "additionalProperties": False
        }
    )
# Tools específicas (finalmente unificadas e padronizadas)
setar_agente_tool_organizador = criar_tool_setar_agente("organizador_agent")
setar_agente_tool_optimum_writer = criar_tool_setar_agente("optimum_writer_agent")
setar_agente_tool_emocional = criar_tool_setar_agente("emocional_agent")
setar_agente_tool_estrategista = criar_tool_setar_agente("estrategista_intelectual_agent")
setar_agente_tool_solucoes_ai = criar_tool_setar_agente("solucoes_ai_em_demanda_agent")
setar_agente_tool_spinsalinng = criar_tool_setar_agente("spinselling_agent")








