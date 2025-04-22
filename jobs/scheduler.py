from sched import scheduler
from apscheduler.schedulers.background import BackgroundScheduler # type: ignore
from db.users import consultar_perfil_usuario
from db.tarefas import listar_tarefas
from db.memorias import consultar_objetivo_da_semana
from core.mensageiro import enviar_resposta
from db.mongo import db
from datetime import datetime
from db.comportamento import consultar_comportamento
from jobs.resumo import enviar_resumo_semanal


def checkin_diario():
   # print("⏰ Executando check-in diário...")



    users = db["users"].find()

    for user in users:
        wa_id = user["wa_id"]
        nome = user.get("nome", "amigo")

        objetivo = consultar_objetivo_da_semana(wa_id)
        tarefas = listar_tarefas(wa_id)

        mensagem = f"👋 Olá, {nome}!\n"

        if objetivo:
            mensagem += f"🎯 Seu objetivo da semana: {objetivo}\n"
        if tarefas:
            mensagem += "📋 Você ainda tem essas tarefas pendentes:\n"
            for t in tarefas[:3]:
                entrega = t.get("data_entrega", "sem data")
                mensagem += f"- {t['descricao']} (até: {entrega})\n"
        else:
            mensagem += "🎉 Nenhuma tarefa pendente por aqui. Boa!"

        enviar_resposta(wa_id, mensagem)


def lembrar_tarefas_do_dia():
   # print("🔔 Buscando tarefas com data de hoje...")

    hoje = datetime.now().strftime("%Y-%m-%d")

    usuarios = db["users"].find()
    for user in usuarios:
        wa_id = user["wa_id"]
        nome = user.get("nome", "amigo")

        tarefas = listar_tarefas(wa_id)
        tarefas_hoje = [t for t in tarefas if t.get("data_entrega") == hoje]

        if not tarefas_hoje:
            continue

        msg = f"🔔 Oi {nome}, lembrete do dia:\n"

        for t in tarefas_hoje:
            msg += f"- {t['descricao']}\n"

        enviar_resposta(wa_id, msg)

def reforco_emocional():
   # print("💬 Enviando reforços emocionais...")

    usuarios = db["users"].find()
    for user in usuarios:
        wa_id = user["wa_id"]
        nome = user.get("nome", "amigo")

        comportamento = consultar_comportamento(wa_id) or {}
        gatilhos = comportamento.get("gatilhos", [])

        if not gatilhos:
            continue  # pula quem ainda não tem perfil emocional

        mensagens = []

        if "evita rejeição" in gatilhos:
            mensagens.append("Você não precisa da aprovação de ninguém. Seu progresso fala por si.")

        if "se sobrecarrega fácil" in gatilhos:
            mensagens.append("Respira. Vamos focar só no essencial hoje.")

        if "precisa de reforço positivo" in gatilhos:
            mensagens.append("Lembre-se: só de estar aqui, você já tá vencendo.")

        if not mensagens:
            continue

        texto_final = f"👋 Oi {nome}, só um lembrete importante pra você hoje:\n\n"
        texto_final += "\n".join(mensagens)

        enviar_resposta(wa_id, texto_final)

def iniciar_agendador():
    scheduler.start()
  #  print("✅ Agendador de tarefas iniciado.")




def iniciar_agendador():
    scheduler = BackgroundScheduler()
    #scheduler.add_job(checkin_diario, trigger="interval", minutes=1)
    #scheduler.add_job(lembrar_tarefas_do_dia, trigger="interval", minutes=1)
    #scheduler.add_job(enviar_resumo_semanal,  trigger="interval", minutes=1)

    scheduler.add_job(enviar_resumo_semanal, "cron", day_of_week="sun", hour=19, minute=0)
    scheduler.add_job(checkin_diario, trigger="cron", hour=9, minute=0)
    scheduler.add_job(lembrar_tarefas_do_dia, trigger="cron", hour=8, minute=30)
    scheduler.add_job(reforco_emocional, trigger="cron", hour=10, minute=30)


    scheduler.start()
   # print("✅ Agendador iniciado com sucesso.")



