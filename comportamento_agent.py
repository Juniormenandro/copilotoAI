from agents import Agent
from pydantic import BaseModel, Field
from copiloto_context import CopilotoContext
from db.comportamento import salvar_comportamento


# 🔐 Novo schema válido para o agente
class ComportamentoSchema(BaseModel):
    personalidade: str = Field(..., description="Resumo da personalidade do usuário")
    emocao: str = Field(..., description="Emoção predominante detectada")
    traços_comunicacao: str = Field(..., description="Estilo de comunicação percebido")
    dores: str = Field(..., description="Dores ou desafios percebidos")
    desejos: str = Field(..., description="Desejos ou aspirações percebidas")
    linguagem_preferida: str = Field(..., description="Tipo de linguagem mais adequada")
    tom_recomendado: str = Field(..., description="Tom de comunicação ideal")

# 🧠 Agente de análise comportamental
comportamento_agent = Agent(
    name="Analista Comportamental",
    instructions="""
Você é um analista especialista em comportamento humano e comunicação empática.

Com base na mensagem do usuário, extraia o máximo de informações possíveis nos seguintes campos:
- personalidade (resumida em uma frase)
- emoções detectadas
- traços de comunicação (ex.: objetivo, ansioso, introspectivo, etc.)
- possíveis dores ou desafios
- possíveis desejos
- tipo de linguagem que parece preferir (ex.: informal, direta, amigável, técnica)
- tom adequado para se comunicar com essa pessoa

Responda com o JSON exato que preencha os campos do schema.
Se não souber, use "?".
""",
    output_type=ComportamentoSchema,
)

# 🎯 Função de execução isolada
async def executor_comportamento(mensagem: str, contexto: CopilotoContext):
    from agents import Runner
    resultado = await Runner.run(comportamento_agent, mensagem, context=contexto)
    dados = resultado.final_output

    print("🧠 Resultado do agente de comportamento:", dados)

    # Salva no banco
    salvar_comportamento(contexto.wa_id, dados.model_dump())
    return dados

