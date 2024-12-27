# routes/whatsapp.py
from fastapi import APIRouter, Request, HTTPException
from models import SendMessage
import random
from config import ALLOWED_INSTANCE_IDS, ALLOWED_CHATS, ALLOWED_ADMIN
from services.event_service import (
    handle_data,
    handle_hora,
    handle_local,
    handle_desc,
    handle_eventos,
    handle_cancelar,
    handle_confirmar,
    handle_desconfirmar,
    handle_confirmar_outro,
    handle_evento
)
from services.gpt_service import handle_gpt4, salvar_mensagem, cadastrar_evento_geral, handle_change_config, handle_see_config
from services.message_service import send_message
from services.elevenlabs_service import handle_eleven_labs

router = APIRouter()


@router.post("/api/whatsapp/message")
async def receive_message(request: Request):
    body = await request.json()

    instanceId = body.get("instanceId")
    message = body.get("message")

    # Validação 1: Verificar instanceId
    if instanceId not in ALLOWED_INSTANCE_IDS:
        print(f"Instance ID não permitido: {instanceId}")
        raise HTTPException(status_code=400, detail="Instance ID não permitido")

    # Validação 2: Verificar chat
    chat = message.get("chat")
    if chat not in ALLOWED_CHATS:
        print(f"Chat não permitido: {chat}")
        raise HTTPException(status_code=400, detail="Chat não permitido")

    sender = message.get("sender")
    body_message = message.get("body").strip()

    # Salvar mensagem na memória
    salvar_mensagem(body_message, chat, sender, message['timestamp'])

    # Processar comandos
    if body_message.startswith("!"):
        command_parts = body_message.split(" ", 2)  # Suporta até 3 partes
        command = command_parts[0].lower()
        argument = " ".join(command_parts[1:]) if len(command_parts) > 1 else ""


        if command == "!cadastrar":
            # Espera que o argumento seja no formato: nome_evento;dd/mm/aaaa;HH:MM;local;descricao
            partes = argument.split(';')
            if len(partes) != 5:
                return send_message(chat, "Uso correto: !cadastrar nome_evento;dd/mm/aaaa;HH:MM;local;descricao")
            nome_evento, data_evento, hora_evento, local, descricao = partes
            return cadastrar_evento_geral(sender, nome_evento.strip(), data_evento.strip(), hora_evento.strip(), local.strip(), descricao.strip(), chat)
        elif command == "!data":

            partes = argument.split(' ', 1)
            if len(partes) != 2:
                return send_message(chat, "⚠️ Uso correto: !data <id_evento> <dd/mm/aaaa> 📅")
            id_evento, data_evento = partes
            if not id_evento.isdigit():
                return send_message(chat, "⚠️ ID do evento inválido. Deve ser um número. 🔢")
            return handle_data(int(id_evento), data_evento.strip(), chat)
        elif command == "!hora":
            
            partes = argument.split(' ', 1)
            if len(partes) != 2:
                return send_message(chat, "⚠️ Uso correto: !hora <id_evento> <HH:MM> 🕒")
            id_evento, hora_evento = partes
            if not id_evento.isdigit():
                return send_message(chat, "⚠️ ID do evento inválido. Deve ser um número. 🔢")
            return handle_hora(int(id_evento), hora_evento.strip(), chat)
        elif command == "!local":

            partes = argument.split(' ', 1)
            if len(partes) != 2:
                return send_message(chat, "⚠️ Uso correto: !local <id_evento> <endereço completo> 📍")
            id_evento, local = partes
            if not id_evento.isdigit():
                return send_message(chat, "⚠️ ID do evento inválido. Deve ser um número. 🔢")
            return handle_local(int(id_evento), local.strip(), chat)
        elif command == "!descricao":
            
            partes = argument.split(' ', 1)
            if len(partes) != 2:
                return send_message(chat, "⚠️ Uso correto: !descricao <id_evento> <descrição> 📝")
            id_evento, descricao = partes
            if not id_evento.isdigit():
                return send_message(chat, "⚠️ ID do evento inválido. Deve ser um número. 🔢")
            return handle_desc(int(id_evento), descricao.strip(), chat)
        elif command == "!eventos":
            return handle_eventos(chat)
        elif command == "!cancelar":
            return handle_cancelar(sender, argument, chat, ALLOWED_ADMIN)
        elif command == "!confirmar":  
            return handle_confirmar(sender, argument, chat)
        elif command == "!desconfirmar":  
            return handle_desconfirmar(sender, argument, chat)
        elif command == "!terceiros":  
            return handle_confirmar_outro(sender, argument, chat, ALLOWED_ADMIN)
        elif command == "!evento":  
            return handle_evento(argument, chat)
        elif command == "!gpt":  
            return handle_gpt4(argument, chat, sender)
        elif command == "!config":  
            if sender not in ALLOWED_ADMIN:
                send_message(chat, "🚫 Você não tem permissão para executar esse comando! 🚫")
            else:    
                return handle_change_config(argument, chat)
        elif command == "!verconfig":  
            return handle_see_config(chat)
        elif command == "!lab":  
            return handle_eleven_labs(argument, chat)
        else:
            
            print("Comando não reconhecido")
            
    # Responde aleatóriamente as mensagens
    # elif random.random() <= 0.3:
    elif 1 == 1:
        return handle_gpt4(body_message, chat, sender)
    
    else:
        print("Mensagem não contém um comando válido.")
        # return send_message(chat, "Mensagem recebida, mas não contém um comando válido.")
