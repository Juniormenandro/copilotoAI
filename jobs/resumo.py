from db.tarefas import listar_tarefas
from db.memorias import consultar_objetivo_da_semana
from core.mensageiro import enviar_resposta
from db.mongo import db

def enviar_resumo_semanal():
    print("📅 Rodando resumo semanal...")

    usuarios = db["users"].find()

    for user in usuarios:
        wa_id = user["wa_id"]
        nome = user.get("nome", "comandante")

        objetivo = consultar_objetivo_da_semana(wa_id)
        tarefas = listar_tarefas(wa_id)

        if not objetivo and not tarefas:
            continue  # pula usuários sem nada registrado

        texto = f"🚀 Oi {nome}! Bora revisar sua semana?\n\n"

        if objetivo:
            texto += f"🎯 Seu objetivo da semana foi:\n👉 {objetivo}\n\n"

        if tarefas:
            texto += "📋 Tarefas pendentes:\n"
            for t in tarefas:
                entrega = t.get("data_entrega", "sem data")
                texto += f"- {t['descricao']} (entrega: {entrega})\n"
        else:
            texto += "🎉 Você concluiu todas as suas tarefas!\n"

        texto += "\nSe quiser, já posso anotar seu foco da próxima semana. Me diga!"

        enviar_resposta(wa_id, texto)
