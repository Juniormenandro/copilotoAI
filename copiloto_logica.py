import asyncio
from context.context_builder import processar_mensagem_usuario

async def get_copiloto_response_com_agente(user_message: str, wa_id: str = "353833844418") -> str:
    resultado = await processar_mensagem_usuario(user_message, wa_id)

    if resultado["status"] == "success":
        respostas = []
        for item in resultado["resultados"]:
            agente = item["agente"]
            output = item["resultado"]
            resposta = output if isinstance(output, str) else output.get("message", str(output))
            respostas.append(f"{resposta}")
        return "\n".join(respostas)
    else:
        return "Houve um problema ao processar com o agente. Posso tentar de outro jeito?"

# --- Teste Interativo ---
async def main_interativo():
    print("🧠 Copiloto IA iniciado! Digite sua mensagem ou 'sair' para encerrar.")
    while True:
        mensagem = input("\nMensagem: ")
        if mensagem.lower() in ["sair", "exit", "quit"]:
            print("👋 Até logo!")
            break
        resposta = await get_copiloto_response_com_agente(mensagem)
        print(f"\n🤖 Resposta do Copiloto:\n{resposta}")

if __name__ == "__main__":
    asyncio.run(main_interativo())
