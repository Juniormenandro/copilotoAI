from copiloto_context import CopilotoContext
from db.usuarios import buscar_usuario_por_id
from db.comportamento import buscar_comportamento_por_id
from db.memoria import buscar_memorias_por_id
from db.tarefas import buscar_tarefas_por_id

def montar_input_context(wa_id: str) -> CopilotoContext:
    """
    Monta o contexto completo do usuário com base no número wa_id,
    buscando os dados de usuário, comportamento, memórias e tarefas no banco de dados.
    """
    usuario = buscar_usuario_por_id(wa_id)
    comportamento = buscar_comportamento_por_id(wa_id)
    memorias = buscar_memorias_por_id(wa_id)
    tarefas = buscar_tarefas_por_id(wa_id)

    return CopilotoContext(
        wa_id=wa_id,
        nome=usuario.get("nome", "Usuário") if usuario else "Usuário",
        comportamento=comportamento,
        memorias=memorias,
        tarefas=tarefas
    )

def montar_contexto_usuario(wa_id: str) -> dict:
    """
    Retorna um dicionário simples apenas com nome e wa_id.
    Usado para chamadas rápidas sem contexto completo.
    """
    usuario = buscar_usuario_por_id(wa_id)
    return {
        "wa_id": wa_id,
        "nome": usuario.get("nome", "Usuário") if usuario else "Usuário"
    }
