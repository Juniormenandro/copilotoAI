import asyncio
from comportamento_agent import executor_comportamento
from copiloto_context import CopilotoContext

async def testar():
    contexto = CopilotoContext(wa_id="99999999", nome="Júnior")
    mensagem = input("🗣️ Digite a mensagem do usuário para análise comportamental:\n> ")
    resultado = await executor_comportamento(mensagem, contexto)

    print("\n🧾 Resultado final salvo no banco de dados:")
    for chave, valor in resultado.items():
        print(f"- {chave}: {valor}")

if __name__ == "__main__":
    asyncio.run(testar())


# ando muito cansado msa tenho raiva de deixar as coisas para ser feitas, preciso de foco e comportamento para finalizar tudo 