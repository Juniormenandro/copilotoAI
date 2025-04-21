from agents import Agent, Runner # type: ignore
from pydantic import BaseModel, Field # type: ignore
from copilotoAI.context.copiloto_context import CopilotoContext
from db.comportamento import salvar_comportamento
from datetime import datetime


# 🔐 Schema de output para análise comportamental
class ComportamentoSchema(BaseModel):
    personalidade: str = Field(..., description="Resumo da personalidade do usuário")
    emocao: str = Field(..., description="Emoção predominante detectada")
    traços_comunicacao: str = Field(..., description="Estilo de comunicação percebido")
    dores: str = Field(..., description="Dores ou desafios percebidos")
    desejos: str = Field(..., description="Desejos ou aspirações percebidas")
    linguagem_preferida: str = Field(..., description="Tipo de linguagem mais adequada")
    tom_recomendado: str = Field(..., description="Tom de comunicação ideal")


# 🧠 Agente especializado em análise comportamental
comportamento_agent = Agent(
    name="Analista Comportamental",
    instructions="""
Você é um analista especialista em comportamento humano e comunicação empática.

Sua função é analisar a mensagem recebida com base no contexto emocional e histórico, buscando extrair insights claros e úteis sobre a personalidade e estilo do usuário.

---

🎯 Responda preenchendo um JSON com os seguintes campos:
- **personalidade:** resumo da personalidade percebida
- **emocao:** emoção predominante ou recorrente
- **traços_comunicacao:** ex: objetivo, reflexivo, ansioso, desconfiado...
- **dores:** dores, bloqueios ou desafios percebidos
- **desejos:** aspirações ou necessidades implícitas
- **linguagem_preferida:** ex: leve, empática, direta, técnica...
- **tom_recomendado:** como o copiloto deve se comunicar com essa pessoa

---

📌 Dicas:
- Use o histórico (`context.historico`) e alerta emocional (`context.alerta_emocional`) para identificar padrões de repetição ou travas.
- Evite repetir o que o usuário disse. Gere uma análise genuína com base na intenção por trás da fala.
- Seja claro, sintético e profundo. Evite respostas genéricas.
- Se não souber algum campo, use "?" como valor.

Exemplo de resposta:
{
  "personalidade": "Reflexivo, curioso e sensível ao julgamento.",
  "emocao": "Frustração com progresso pessoal",
  "traços_comunicacao": "Direto e introspectivo",
  "dores": "Autocrítica e falta de clareza nas prioridades",
  "desejos": "Avançar com leveza e propósito",
  "linguagem_preferida": "Motivacional e acolhedora",
  "tom_recomendado": "Gentil, encorajador e direto ao ponto"
}
""",
    output_type=ComportamentoSchema,
)


# 🔁 Função que executa o agente e salva o resultado no banco
async def executor_comportamento(mensagem: str, contexto: CopilotoContext):
    resultado = await Runner.run(comportamento_agent, input=mensagem, context=contexto)
    dados = resultado.final_output

    if not dados:
        print("⚠️ Nenhum dado retornado pelo agente de comportamento.")
        return None

    dados_dict = dados.model_dump()
    dados_dict["timestamp"] = datetime.utcnow()

    print("🧠 Resultado do agente de comportamento:", dados_dict)
    salvar_comportamento(contexto.wa_id, dados_dict)
    return dados
