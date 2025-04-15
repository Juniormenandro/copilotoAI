from datetime import datetime, timedelta
import dateparser

def interpretar_data_relativa(texto: str) -> str:
    """
    Converte datas relativas como 'amanhã', 'sexta-feira', 'daqui a 3 dias'
    para o formato YYYY-MM-DD.
    """
    if not texto:
        return None

    data_parseada = dateparser.parse(texto, settings={'PREFER_DATES_FROM': 'future'})
    if data_parseada:
        return data_parseada.strftime("%Y-%m-%d")
    return None
