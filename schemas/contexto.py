from pydantic import BaseModel


class CopilotoContext(BaseModel):
    emocao: str = ""
    wa_id: str
    nome: str | None = None
    linguagem: str| None = "pt"
    objetivo_semana: str| None = None
    ultima_interacao: str| None = None
    personalidade: str| None = None
    tom: str| None = None
    dores: str| None = None
    desejos: str| None = None
    traços_comunicacao: str| None = None
    linguagem_preferida: str| None = None
;