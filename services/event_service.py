# services/event_service.py
import re
import json
from datetime import datetime
from database import get_db_connection
from services.message_service import send_message
import sqlite3
import config

def criar_evento(sender: str, nome_evento: str, data_evento: str, hora_evento: str, local: str, descricao: str, chat: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO eventos (sender, nome_evento, data_evento, hora_evento, local, descricao, status, chat, datetime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sender,
            nome_evento,
            data_evento,
            hora_evento,
            local,
            descricao,
            'ativo',
            chat,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        conn.commit()
        evento_id = cursor.lastrowid
        conn.close()
        return evento_id
    except sqlite3.Error as e:
        print(f"Erro ao criar evento: {e}")
        return None

def cadastrar_evento_geral(sender: str, nome_evento: str, data_evento: str, hora_evento: str, local: str, descricao: str, chat: str):
    # Validar os parâmetros
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_evento):
        return send_message(chat, "📅 Formato de data inválido. Use dd/mm/aaaa.")
    if not re.match(r'^\d{2}:\d{2}$', hora_evento):
        return send_message(chat, "🕒 Formato de hora inválido. Use HH:MM.")
    if len(local.strip()) <= 7:
        return send_message(chat, "📍 Erro com o local. Por favor, forneça um endereço mais detalhado. 🏠")
    if len(descricao) <= 11:
        return send_message(chat, "⚠️ Erro com a descrição. Por favor, forneça uma descrição mais detalhada. 📝")

    evento_id = criar_evento(sender, nome_evento, data_evento, hora_evento, local, descricao, chat)
    if evento_id:
        return send_message(chat, f"🎉 Evento '{nome_evento}' agendado para o dia 📅 {data_evento} às 🕒 {hora_evento} no local 📍 {local}.")   
    else:
        return send_message(chat, "Erro ao criar o evento. Por favor, tente novamente mais tarde.")

def handle_data(id_evento: int, data_evento: str, chat: str):

    # Verificar o formato da data
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', data_evento):
        return send_message(chat, "⚠️ Formato de data inválido. Use dd/mm/aaaa. 🗓️")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o evento existe e está ativo
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (id_evento,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "🔍 Nenhum evento ativo encontrado com o ID fornecido.")

    # Atualizar a data do evento
    cursor.execute('''
        UPDATE eventos
        SET data_evento = ?
        WHERE id = ?
    ''', (data_evento, id_evento))
    conn.commit()
    conn.close()

    return send_message(chat, "📅 Data registrada com sucesso! Por favor, informe a hora do evento no formato HH:MM usando o comando !hora <HH:MM>. 🕒")

def handle_hora(id_evento: int, hora_evento: str, chat: str):
  
    # Verificar o formato da hora
    if not re.match(r'^\d{2}:\d{2}$', hora_evento):
        return send_message(chat, "⚠️ Formato de hora inválido. Use HH:MM. 🕒")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o evento existe e está ativo
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (id_evento,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "🔍 Nenhum evento ativo encontrado com o ID fornecido.")

    # Atualizar a hora do evento
    cursor.execute('''
        UPDATE eventos
        SET hora_evento = ?
        WHERE id = ?
    ''', (hora_evento, id_evento))
    conn.commit()
    conn.close()

    return send_message(chat, f"🕒 Hora registrada para {hora_evento}. \n📍 Use !local <endereço completo> para adicionar a localização.")

def handle_local(id_evento: int, local: str, chat: str):
    """
    Atualiza o local de um evento ativo com base no ID fornecido.

    Args:
        id_evento (int): O ID do evento a ser atualizado.
        local (str): O novo local para o evento.
        chat (str): O ID do chat de onde a mensagem foi originada.
    """
    # Verificar o formato do local (exemplo simples)
    if len(local.strip()) <= 7:
        return send_message(chat, "⚠️ Erro com o local. Por favor, forneça um endereço mais detalhado. 📍")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o evento existe e está ativo
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (id_evento,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "🔍 Nenhum evento ativo encontrado com o ID fornecido.")

    # Atualizar o local do evento
    cursor.execute('''
        UPDATE eventos
        SET local = ?
        WHERE id = ?
    ''', (local, id_evento))
    conn.commit()
    conn.close()

    return send_message(chat, f"📍 Local registrado em {local}. \n📝 Use !descricao <descrição> para adicionar uma descrição.")

def handle_desc(id_evento: int, descricao: str, chat: str):
    """
    Atualiza a descrição de um evento ativo com base no ID fornecido.

    Args:
        id_evento (int): O ID do evento a ser atualizado.
        descricao (str): A nova descrição para o evento.
        chat (str): O ID do chat de onde a mensagem foi originada.
    """
    # Verificar o formato da descrição (exemplo simples)
    if len(descricao.strip()) <= 11:
        return send_message(chat, "⚠️ Erro com a descrição. Por favor, forneça uma descrição mais detalhada. 📝")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar se o evento existe e está ativo
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (id_evento,))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "🔍 Nenhum evento ativo encontrado com o ID fornecido.")

    # Atualizar a descrição e definir o status como 'ativo' (caso já não esteja)
    cursor.execute('''
        UPDATE eventos
        SET descricao = ?, status = 'ativo'
        WHERE id = ?
    ''', (descricao, id_evento))
    conn.commit()
    conn.close()

    return send_message(chat, f"📝 Evento '{evento['nome_evento']}' agendado para o dia {evento['data_evento']} às {evento['hora_evento']}. 🎉")

def handle_eventos(chat: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM eventos
        WHERE status = 'ativo'
        AND chat = ?
    ''', (chat,))

    eventos = cursor.fetchall()

    print('sou eventos')
    print(eventos)
    conn.close()

    if not eventos:
        return send_message(chat, "🔍 Nenhum evento ativo encontrado.")

    mensagem = "Eventos Ativos:\n\n"
    for evento in eventos:
        # Carregar confirmados do JSON
        confirmados = json.loads(evento['confirmados']) if evento['confirmados'] else []
        confirmados_str = "\n".join([f"- {c['nome']} ({c['sender']})" for c in confirmados]) if confirmados else "Nenhum confirmado ainda."

        mensagem += f"""
🔥 ID: {evento['id']} 🔥
🎉 {evento['nome_evento']} 🎉

✨ {evento['descricao']} ✨
📅 Data: {evento['data_evento']}
🕒 Horário: {evento['hora_evento']}
📍 Local: {evento['local']}

💌 Criado por: {evento['sender']}

✅ Confirmados:
{confirmados_str}

📲 Para confirmar sua presença, use o comando:
**!confirmar {evento['id']} <seu_nome>**

🔥 Não perca! Chame a galera e confirme sua presença!
                        """

    return send_message(chat, mensagem)

def handle_cancelar(sender: str, evento_id: str, chat: str, allowed_admins: list):
    if not evento_id.isdigit():
        return send_message(chat, "ID inválido. Use o comando !cancelar <id>.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica se o sender está na lista de administradores
    if sender not in config.ALLOWED_ADMIN:
        # Consulta eventos para um sender específico
        cursor.execute('''
            SELECT * FROM eventos
            WHERE id = ? AND sender = ?
        ''', (int(evento_id), sender))
    else:
        cursor.execute('''
            SELECT * FROM eventos
            WHERE id = ? 
        ''', (int(evento_id),))

    evento = cursor.fetchone()

    print(evento)

    if not evento:
        conn.close()
        return send_message(chat, "Evento não encontrado ou você não tem permissão para cancelar.")

    cursor.execute('''
        UPDATE eventos
        SET status = 'cancelado'
        WHERE id = ?
    ''', (int(evento_id),))
    conn.commit()
    conn.close()

    return send_message(chat, f"Evento '{evento['nome_evento']}' foi cancelado com sucesso.")

def handle_confirmar(sender: str, argument: str, chat: str):
    parts = argument.split(" ", 1)
    if len(parts) != 2:
        return send_message(chat, "Uso correto: !confirmar <id> <nome>")

    evento_id, nome = parts
    if not evento_id.isdigit():
        return send_message(chat, "ID inválido. Use um número válido para o ID do evento.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (int(evento_id),))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "Evento não encontrado ou não está ativo.")

    confirmados = json.loads(evento['confirmados']) if evento['confirmados'] else []

    # Verificar se o sender já está confirmado
    for confirmado in confirmados:
        if confirmado['sender'] == sender:
            confirmado['nome'] = nome  # Atualizar nome
            break
    else:
        # Se não estiver confirmado, adicionar
        confirmados.append({"nome": nome, "sender": sender})

    # Atualizar a lista de confirmados no banco de dados
    cursor.execute('''
        UPDATE eventos
        SET confirmados = ?
        WHERE id = ?
    ''', (json.dumps(confirmados), evento['id']))
    conn.commit()
    conn.close()

    return send_message(chat, f"Você confirmou presença no evento '{evento['nome_evento']}' com o nome '{nome}'.")

def handle_desconfirmar(sender: str, argument: str, chat: str):
    parts = argument.split(" ", 1)
    if len(parts) != 1:
        return send_message(chat, "Uso correto: !desconfirmar <id>")

    evento_id = parts[0]
    if not evento_id.isdigit():
        return send_message(chat, "ID inválido. Use um número válido para o ID do evento.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (int(evento_id),))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "Evento não encontrado ou não está ativo.")

    confirmados = json.loads(evento['confirmados']) if evento['confirmados'] else []

    for confirmado in confirmados:
        if confirmado['sender'] == sender:
            confirmados.remove(confirmado)  # Remover o confirmado correspondente
            break

    # Atualizar a lista de confirmados no banco de dados
    cursor.execute('''
        UPDATE eventos
        SET confirmados = ?
        WHERE id = ?
    ''', (json.dumps(confirmados), evento['id']))
    conn.commit()
    conn.close()

    return send_message(chat, f"Você falou que não vai no '{evento['nome_evento']}', espero que tenha um bom motivo.")

def handle_confirmar_outro(sender: str, argument: str, chat: str, allowed_admins: list):
    parts = argument.split(" ", 1)
    if len(parts) != 2:
        return send_message(chat, "Uso correto: !confirmar <id> <nome>")

    evento_id, nome = parts
    if not evento_id.isdigit():
        return send_message(chat, "ID inválido. Use um número válido para o ID do evento.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (int(evento_id),))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "Evento não encontrado ou não está ativo.")

    if sender not in config.ALLOWED_ADMIN:
        conn.close()
        return send_message(chat, "Você não tem permissão para usar esse recurso! Fala co Jão")

    confirmados = json.loads(evento['confirmados']) if evento['confirmados'] else []

    # Verificar se há senders com menos de 3 dígitos
    senders_menos_3_digitos = [int(confirmado['sender']) for confirmado in confirmados if len(str(confirmado['sender'])) < 3]

    # Se houver senders com menos de 3 dígitos, pega o maior e incrementa
    if senders_menos_3_digitos:
        novo_sender = max(senders_menos_3_digitos) + 1
    else:
        # Se não houver, atribui 1
        novo_sender = 1

    confirmados.append({"nome": nome, "sender": novo_sender})

    # Atualizar a lista de confirmados no banco de dados
    cursor.execute('''
        UPDATE eventos
        SET confirmados = ?
        WHERE id = ?
    ''', (json.dumps(confirmados), evento['id']))
    conn.commit()
    conn.close()

    return send_message(chat, f"Presença de terceiro no evento '{evento['nome_evento']}' com o nome '{nome}' confirmada! 👀.")

def handle_evento(evento_id: str, chat: str):
    evento_id = evento_id.strip()
    if not evento_id.isdigit():
        return send_message(chat, "ID inválido. Use um número válido para o ID do evento.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM eventos
        WHERE id = ? AND status = 'ativo'
    ''', (int(evento_id),))
    evento = cursor.fetchone()

    if not evento:
        conn.close()
        return send_message(chat, "Evento não encontrado ou não está ativo.")

    # Carregar confirmados do JSON
    confirmados = json.loads(evento['confirmados']) if evento['confirmados'] else []
    confirmados_str = "\n".join([f"- {c['nome']} ({c['sender']})" for c in confirmados]) if confirmados else "Nenhum confirmado ainda."

    mensagem = f"""
🔥 ID: {evento['id']} 🔥
🎉 {evento['nome_evento']} 🎉

✨ {evento['descricao']} ✨
📅 Data: {evento['data_evento']}
🕒 Horário: {evento['hora_evento']}
📍 Local: {evento['local']}

🎭 Dress Code: Venha como preferir, mas arrase! 😎
🍕🍻 Vai ter muita comida e bebida!

💌 Criado por: {evento['sender']}

✅ Confirmados:
{confirmados_str}

🔥 Não perca! Chame a galera e confirme sua presença!
                """

    conn.close()
    return send_message(chat, mensagem)

def handle_change_config(config: str, id: str):
    # Obter a conexão com o banco de dados
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se já existe algum registro na tabela config_gpt
        cursor.execute('SELECT * FROM config_gpt WHERE id = ?', (int(id),))
        result = cursor.fetchone()

        if result is None:
            # Se não existe nenhum registro, cria o registro com id = 1 e system_prompt = config
            cursor.execute('''
                INSERT INTO config_gpt (id, system_prompt)
                VALUES (1, ?)
            ''', (config,))
            print("Configuração criada com sucesso.")
        else:
            # Se já existe, atualiza o valor do system_prompt
            cursor.execute('''
                UPDATE config_gpt
                SET system_prompt = ?
                WHERE id = 1
            ''', (config,))
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
