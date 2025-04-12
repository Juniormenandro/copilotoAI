import os
import requests
from dotenv import load_dotenv

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

def enviar_resposta(numero, mensagem):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensagem}
    }

    print("📤 Enviando para número:", numero)
    print("📦 Payload:", payload)

    response = requests.post(url, headers=headers, json=payload)
    print("🔁 Resposta completa:", response.status_code, response.text)

    if response.status_code == 200:
        print(f"✅ Mensagem enviada para {numero}")
    else:
        print(f"❌ Erro ao enviar: {response.status_code} - {response.text}")
