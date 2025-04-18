# --- copiloto_context.py ---
from typing import Optional, List, Dict
from pydantic import BaseModel


class CopilotoContext(BaseModel):
    wa_id: int | None = None
    nome: str | None = None
    objetivo_da_semana: str | None = None
    estilo_produtivo: str | None = None
    emocional: str | None = None
    comportamento: Optional[Dict] = None
    objetivo: Optional[Dict] = None
    historico: Optional[List[Dict]] = None