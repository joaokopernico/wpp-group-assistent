# services/message_service.py
import requests
from config import *
import json

def send_message(phone: str, text: str):
    url = "http://localhost:8900/api/1/chat/send/text"  # Substitua pela URL real do serviço

    if len(phone) > 13:
        phone = phone + "@g.us"
    payload = {
        "phone": phone,
        "text": text
    }

    print(payload)
    headers = {
        "Content-Type": "application/json"
    }

    print(text)
    response = requests.post(url, json=payload, headers=headers)
    print(response)

def send_audio_message(phone: str, text: str):
    url = "http://localhost:8900/api/1/chat/send/audio" 

    if len(phone) > 13:
        phone = phone + "@g.us"

    payload = {
        "base64": text,
        "phone": phone
    }

    print(payload)
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response)
    # Opcional: Tratar a resposta conforme necessário
