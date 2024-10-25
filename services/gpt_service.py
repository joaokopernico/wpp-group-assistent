# services/gpt_service.py
import json
from datetime import datetime
from database import get_db_connection
from services.message_service import send_message
from services.event_service import cadastrar_evento_geral
import services.elevenlabs_service as eleven
import openai
from config import OPENAI_API_KEY
import sqlite3
import config

def gpt_register_event(nome_evento: str, data_evento: str, hora_evento: str, local: str, descricao: str, chat: str, sender: str):
    print('entrei no gpt register event')
    return cadastrar_evento_geral(sender, nome_evento, data_evento, hora_evento, local, descricao, chat)

def gpt_send_message(phone: str, text: str):

    return send_message(phone, text)

def obter_historico_mensagens(chat, limite=60):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT sender, message, date
        FROM memoria
        WHERE chat = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (chat, limite))

    historico = cursor.fetchall()
    conn.close()

    mensagens_formatadas = []
    for mensagem in reversed(historico):
        sender, message, date = mensagem
        role = 'user' if sender != 'GPT' else 'assistant'
        mensagens_formatadas.append({"role": role, "content": f"{sender}: {message}"})

    return mensagens_formatadas

def salvar_mensagem(message, chat, sender, date):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO memoria (message, chat, sender, date)
            VALUES (?, ?, ?, ?)
        ''', (message, chat, sender, date))

        conn.commit()
        print("Mensagem salva com sucesso!")

    except sqlite3.Error as e:
        print(f"Erro ao salvar a mensagem: {e}")

    finally:
        conn.close()

def handle_gpt4(prompt: str, chat: str, sender: str):
    
    openai.api_key = OPENAI_API_KEY
  
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT system_prompt FROM config_gpt WHERE chat = ?', (chat,))
    config_gpt = cursor.fetchone()


    # Definição das ferramentas (funções) que o GPT pode chamar
    tools = [
        {
            "type": "function",
            "name": "gpt_register_event",
            "description": "Registra um novo evento com os detalhes fornecidos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome_evento": {
                        "type": "string",
                        "description": "Nome do evento."
                    },
                    "data_evento": {
                        "type": "string",
                        "description": "Data do evento no formato dd/mm/aaaa."
                    },
                    "hora_evento": {
                        "type": "string",
                        "description": "Hora do evento no formato HH:MM."
                    },
                    "local": {
                        "type": "string",
                        "description": "Local do evento."
                    },
                    "descricao": {
                        "type": "string",
                        "description": "Descrição detalhada do evento."
                    },
                    "chat": {
                        "type": "string",
                        "description": "ID do chat onde o evento será registrado."
                    },
                    "sender": {
                        "type": "string",
                        "description": "ID do usuário que está registrando o evento."
                    }
                },
                "required": ["nome_evento", "data_evento", "hora_evento", "local", "descricao", "chat", "sender"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "send_message",
            "description": "Envia uma mensagem para um número de telefone específico.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone": {
                        "type": "string",
                        "description": "Número de telefone para enviar a mensagem."
                    },
                    "text": {
                        "type": "string",
                        "description": "Conteúdo da mensagem."
                    }
                },
                "required": ["phone", "text"],
                "additionalProperties": False
            }
        },
        {
            "type": "function",
            "name": "send_audio",
            "description": "Responde com uma mensagem de audio",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio": {
                        "type": "string",
                        "description": "Conteúdo do audio a ser enviado, deve ter no maximo 200 caracteres"
                    }
                },
                "required": ["audio"],
                "additionalProperties": False
            }
        }
    ]
    
    system_prompt = ''

    # Verificar se existe resultado
    if config_gpt:
        print('entrei no config')
        # Extrair o valor do system_prompt (o primeiro item da tupla retornada)
        system_prompt = config_gpt[0]
        # system_prompt2 = "IMPORTANTE!!! A RESPOSTA NÃO DEVE TER EMOJIS E A RISADA DEVE SER NO PADRÃO 'HAHAHA'" + system_prompt

     # Buscar histórico de mensagens para o chat
    historico_mensagens = obter_historico_mensagens(chat, limite=10)
    # Adicionar a mensagem do usuário
    historico_mensagens.append({"role": "user", "content": f"{sender}: {prompt}"})

    try:
        
        # Fazer a requisição para a API da OpenAI com Function Calling
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}
        ] + historico_mensagens + [
            {"role": "user", "content": f"chat: {chat},sender: {sender}: {prompt}"}
        ],
            functions=tools,
            function_call="auto",  # Permite que o GPT escolha qual função chamar
            max_tokens=500,
            temperature=0.7
        )

        message = response['choices'][0]['message']
        print(message)

        if "function_call" in message:
            function_name = message['function_call']['name']
            function_args = json.loads(message['function_call']['arguments'])
            
            if function_name == "gpt_register_event":
                # Chamar a função gpt_register_event com os argumentos fornecidos
                result = gpt_register_event(
                    nome_evento=function_args.get("nome_evento"),
                    data_evento=function_args.get("data_evento"),
                    hora_evento=function_args.get("hora_evento"),
                    local=function_args.get("local"),
                    descricao=function_args.get("descricao"),
                    chat=function_args.get("chat"),
                    sender=function_args.get("sender")
                )
                return result  # A função gpt_register_event deve retornar uma mensagem de confirmação
                
            elif function_name == "send_message":
                
                
                # Chamar a função send_custom_message com os argumentos fornecidos
                phone = function_args.get("phone")
                text = function_args.get("text")
                
                if sender not in config.ALLOWED_ADMIN:
                    if phone not in config.ALLOWED_SEND_MESSAGE:
                        return send_message(chat, 'Você não pode enviar mensagem para essa pessoa 🚫📵')
                    
                
                
                result = send_message(phone, text)
                return result  # A função send_custom_message deve retornar uma mensagem de confirmação
            
            elif function_name == "send_audio":
                
                # Chamar a função send_custom_message com os argumentos fornecidos
                audio = function_args.get("audio")
                    
                return eleven.handle_eleven_labs(audio, chat)
                
            else:
                print(f"Função não reconhecida: {function_name}")
                return send_message(chat, "Desculpe, não reconheço essa função.")
        
        else:
            # Se o GPT não chamou nenhuma função, simplesmente responda com a mensagem
            reply = message.get('content', '').strip()
            if reply:
                salvar_mensagem(reply, chat, sender='GPT', date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                send_message(chat, reply)
            return reply
    
    except openai.error.OpenAIError as e:
        print(f"Erro com a API da OpenAI: {e}")
        return send_message(chat, "Desculpe, ocorreu um erro ao processar sua solicitação.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return send_message(chat, "Desculpe, ocorreu um erro inesperado.")
    
    

def handle_change_config(config: str, chat: str):
    # Obter a conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se já existe algum registro na tabela config_gpt
        cursor.execute('SELECT * FROM config_gpt WHERE chat = ?', (chat,))
        result = cursor.fetchone()

        if result is None:
            # Se não existe nenhum registro, cria o registro com id = 1 e system_prompt = config
            cursor.execute('''
                INSERT INTO config_gpt (system_prompt, chat)
                VALUES (?, ?)
            ''', (config, chat,))
            print("Configuração criada com sucesso.")
        else:
            # Se já existe, atualiza o valor do system_prompt
            cursor.execute('''
                UPDATE config_gpt
                SET system_prompt = ?
                WHERE chat = ?
            ''', (config, chat))
            print("Configuração atualizada com sucesso.")

        # Confirmar a transação para salvar as alterações no banco de dados
        conn.commit()

    except Exception as e:
        # Se algo der errado, faz rollback e exibe o erro
        conn.rollback()
        print(f"Ocorreu um erro: {e}")

    finally:
        # Fechar o cursor e a conexão
        cursor.close()
        conn.close()

def handle_see_config(chat: str):
    # Obter a conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se já existe algum registro na tabela config_gpt
        cursor.execute('SELECT * FROM config_gpt WHERE id = 1')
        result = cursor.fetchone()

        if result is None:
            send_message(chat, "Nenhuma configuração encontrada.")
        else:
            send_message(chat, result['system_prompt'])

    except Exception as e:
        # Se algo der errado, faz rollback e exibe o erro
        conn.rollback()
        print(f"Ocorreu um erro: {e}")

    finally:
        # Fechar o cursor e a conexão
        cursor.close()
        conn.close()
    