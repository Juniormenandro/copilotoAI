# utils/data_parser.py
from datetime import datetime, timedelta
import dateparser

def parse_data_relativa(texto: str) -> str:
    """
    Converte expressões como "amanhã", "quarta-feira", "daqui a 3 dias" em uma data string YYYY-MM-DD
    """
    data = dateparser.parse(texto, settings={"PREFER_DATES_FROM": "future"})
    if not data:
        return ""
    return data.strftime("%Y-%m-%d")


def categorizar_tarefas_por_data(tarefas: list) -> dict:
    hoje = datetime.today().date()
    categorizadas = {
        "atrasadas": [],
        "hoje": [],
        "proximas": []
    }
    for tarefa in tarefas:
        data_entrega = tarefa.get("data_entrega")
        if not data_entrega:
            categorizadas["proximas"].append(tarefa)
            continue
        try:
            data = datetime.strptime(data_entrega, "%Y-%m-%d").date()
            if data < hoje:
                categorizadas["atrasadas"].append(tarefa)
            elif data == hoje:
                categorizadas["hoje"].append(tarefa)
            else:
                categorizadas["proximas"].append(tarefa)
        except ValueError:
            categorizadas["proximas"].append(tarefa)
    return categorizadas

