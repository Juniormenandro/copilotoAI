from datetime import datetime, timedelta
import dateparser

def interpretar_data_relativa(texto: str) -> str:
    """
    Converte expressões como 'amanhã', 'sexta', '25 de abril às 15h'
    para o formato ISO (YYYY-MM-DD).
    """
    if not texto:
        return None

    agora = datetime.now()
    data_parseada = dateparser.parse(
        texto,
        settings={
            'RELATIVE_BASE': agora,
            'PREFER_DATES_FROM': 'future',
            'DATE_ORDER': 'DMY'
        }
    )

    if data_parseada and data_parseada.year < agora.year:
        # Corrige ano errado
        data_parseada = data_parseada.replace(year=agora.year)

    if data_parseada:
        return data_parseada.strftime("%Y-%m-%d")

    return None
