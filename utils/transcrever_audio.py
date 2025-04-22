import os
import subprocess
from openai import OpenAI # type: ignore
from deep_translator import GoogleTranslator # type: ignore
from langdetect import detect # type: ignore


client = OpenAI()
translator = GoogleTranslator()

def converter_para_mp3(input_path):
    mp3_path = input_path.rsplit('.', 1)[0] + '.mp3'
    #print(f"🔄 Convertendo {input_path} para {mp3_path}")
    try:
        subprocess.run(
            ["ffmpeg", "-i", input_path, mp3_path, "-y"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        #print("✅ Conversão concluída com sucesso.")
        return mp3_path
    except subprocess.CalledProcessError as e:
        #print("❌ Falha na conversão:", e.stderr.decode())
        return None

def transcrever_audio_do_whatsapp(arquivo_ogg):
    #print(f"📥 Arquivo recebido: {arquivo_ogg}")

    # Passo 1: Conversão para MP3
    caminho_mp3 = converter_para_mp3(arquivo_ogg)
    if caminho_mp3 is None or not os.path.exists(caminho_mp3):
        #print("❌ Erro após conversão: arquivo mp3 não existe")
        return "Erro na conversão do áudio. Pode tentar digitar?"

    # Passo 2: Transcrição com Whisper
    try:
        with open(caminho_mp3, "rb") as f:
            #print(f"🎙️ Enviando arquivo para transcrição: {caminho_mp3}")
            transcricao = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        texto_transcrito = transcricao.strip()
        #print(f"🔊 Transcrição recebida: '{texto_transcrito}'")
    except Exception as e:
        #print("❌ Falha na transcrição com Whisper:", str(e))
        return "Erro na transcrição do áudio. Pode tentar digitar?"

    if not texto_transcrito:
        #print("⚠️ Transcrição vazia recebida.")
        return "Não consegui entender o áudio. Pode tentar digitar?"

    # Passo 3: Tradução condicional
    try:
        idioma_detectado = detect(texto_transcrito)
        #print(f"🔍 Idioma detectado: {idioma_detectado}")

        if idioma_detectado != 'pt':
            #print("🌍 Traduzindo para português...")
            texto_final = GoogleTranslator(source=idioma_detectado, target='pt').translate(texto_transcrito).strip()
            #print(f"✅ Tradução finalizada: '{texto_final}'")
        else:
            #print("✅ Texto já está em português. Não precisa traduzir.")
            texto_final = texto_transcrito.strip()

    except Exception as e:
        #print("❌ Falha ao detectar idioma ou traduzir:", e)
        return "Erro na tradução do áudio. Pode tentar digitar?"

    return texto_final
