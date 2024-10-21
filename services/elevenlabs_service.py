# services/elevenlabs_service.py
import requests
import json
import base64
from datetime import datetime
from services.message_service import send_audio_message
from config import ELEVEN_LABS_API_KEY, ELEVEN_LABS_VOICE_ID
from fastapi import HTTPException

def handle_eleven_labs(prompt: str, chat: str):
    if not ELEVEN_LABS_API_KEY or not ELEVEN_LABS_VOICE_ID:
        raise HTTPException(status_code=500, detail="Configuração da API da Eleven Labs está incompleta.")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_LABS_VOICE_ID}/stream"

    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": prompt,
        "model_id": "eleven_turbo_v2_5",  # Ou outro modelo conforme necessário
        "output_format": "mp3_22050_32",
        "voice_settings": {
            "stability": 1.0,  # Ajuste conforme desejado
            "similarity_boost": 1.0,  # Ajuste conforme desejado
            "style_exaggeration": 2.0
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        audio_content = response.content

        audio_base64 = 'data:audio/mpeg;base64,' + base64.b64encode(audio_content).decode('utf-8')

        send_audio_message(chat, audio_base64)

    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao conectar com a Eleven Labs: {http_err}")
        raise HTTPException(status_code=502, detail="Erro ao conectar com o serviço de geração de voz.")
    except Exception as err:
        print(f"Erro inesperado ao gerar voz com a Eleven Labs: {err}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar voz.")
