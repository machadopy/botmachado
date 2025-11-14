import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH")
IMAGES_PATH = os.getenv("IMAGES_PATH")

bot = telebot.TeleBot(BOT_TOKEN)

# =====================================================
# TECLADO INICIAL
# =====================================================
keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
button = KeyboardButton(text="Logar informações", request_contact=True)
keyboard.add(button)

# =====================================================
# BANCO DE DADOS
# =====================================================
with sqlite3.connect(DB_PATH) as connection:
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ordem_servico TEXT NOT NULL,
            serial_ont TEXT NOT NULL,
            data_registro TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS imagens(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id INTEGER,
            caminho TEXT,
            data_envio TEXT,
            FOREIGN KEY(registro_id) REFERENCES registros(id)
        );
    """)

# =====================================================
# LOGIN
# =====================================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Bem-vindo ao *MachadoBot*, seu assistente de controle de estoque!\n\n"
        "Antes de começar, compartilhe seu login clicando no botão abaixo:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['contact'])
def contact(message):
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO users (id, first_name, last_name, phone_number)
            VALUES (?, ?, ?, ?)
        """, (
            message.contact.user_id,
            message.contact.first_name,
            message.contact.last_name,
            message.contact.phone_number
        ))

    bot.send_message(
        message.chat.id,
        f"✅ Login realizado com sucesso, {message.contact.first_name}!"
    )
    start(message)

# =====================================================
# MENU
# =====================================================
@bot.message_handler(commands=['start', 'menu'])
def start(msg: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton('➕ Adicionar Histórico', callback_data='botaoadicionar'),
        telebot.types.InlineKeyboardButton('📦 Consultar Almox', callback_data='botaoconsultar')
    )
    bot.send_message(msg.chat.id, 'O que deseja fazer?', reply_markup=markup)

@bot.callback_query_handler()
def resp_btn(call: telebot.types.CallbackQuery):
    match call.data:
        case 'botaoadicionar':
            if not hasattr(bot, 'user_data'):
                bot.user_data = {}
            msg = bot.send_message(call.message.chat.id, 'Digite o número da *Ordem de Serviço (O.S.):*', parse_mode="Markdown")
            bot.register_next_step_handler(msg, get_ordem_servico)

        case 'botaoconsultar':
            escolher_tipo_consulta(call.message)

# =====================================================
# ETAPA 1 - O.S.
# =====================================================
def get_ordem_servico(message):
    os_number = message.text.strip()
    bot.user_data[message.chat.id] = {'os': os_number}
    msg = bot.send_message(message.chat.id, 'Digite o *Serial da ONT:*', parse_mode="Markdown")
    bot.register_next_step_handler(msg, get_serial_ont)

# =====================================================
# ETAPA 2 - SERIAL
# =====================================================
def get_serial_ont(message):
    chat_id = message.chat.id
    serial_ont = message.text.strip()
    bot.user_data[chat_id]['serial'] = serial_ont
    bot.user_data[chat_id]['images'] = []

    msg = bot.send_message(
        chat_id,
        "📸 Agora envie a *1° foto* relacionadas à O.S.\n"
        "Ou digite /pular se não quiser enviar imagens.",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, receber_imagem_ou_pular)

# =====================================================
# ETAPA 3 - RECEBER IMAGENS (CORRIGIDO)
# =====================================================

# ⛔ Removido o handler global que causava duplicação
# ❗ Agora é APENAS uma função comum chamada pelo next_step_handler

def receber_imagem_ou_pular(message):
    chat_id = message.chat.id

    if chat_id not in bot.user_data:
        return

    # Usuário enviou foto
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Nome único com microssegundos
        filename = f"{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        path = os.path.join(IMAGES_PATH, filename)

        with open(path, 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.user_data[chat_id]['images'].append(path)
        qtd = len(bot.user_data[chat_id]['images'])

        if qtd < 2:
            msg = bot.send_message(chat_id, f"Imagem {qtd} recebida! Envie mais uma (ou digite /pular).")
            bot.register_next_step_handler(msg, receber_imagem_ou_pular)
        else:
            bot.send_message(chat_id, "📁 Duas imagens recebidas! Salvando registro...")
            finalizar_registro(chat_id)

    elif message.text.lower() == '/pular':
        finalizar_registro(chat_id)

    else:
        bot.send_message(chat_id, "Envie uma foto válida ou digite /pular para continuar.")
        bot.register_next_step_handler(message, receber_imagem_ou_pular)

# =====================================================
# ETAPA 4 - SALVAR NO BANCO
# =====================================================
def finalizar_registro(chat_id):
    try:
        dados = bot.user_data.get(chat_id)
        if not dados:
            bot.send_message(chat_id, "❌ Nenhum dado encontrado. Recomece com /start.")
            return

        os_number = dados['os']
        serial = dados['serial']
        imagens = dados.get('images', [])
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")

        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO registros (user_id, ordem_servico, serial_ont, data_registro)
                VALUES (?, ?, ?, ?)
            """, (chat_id, os_number, serial, data_atual))
            registro_id = cursor.lastrowid

            for path in imagens:
                cursor.execute("""
                    INSERT INTO imagens (registro_id, caminho, data_envio)
                    VALUES (?, ?, ?)
                """, (registro_id, path, data_atual))
            connection.commit()

        del bot.user_data[chat_id]
        bot.send_message(
            chat_id,
            f"✅ Registro salvo com sucesso!\n"
            f"O.S.: *{os_number}*\nSerial: *{serial}*\n"
            f"🕒 Data/Hora: *{data_atual}*\n"
            f"📸 Imagens: {len(imagens)} enviada(s)",
            parse_mode="Markdown"
        )

    except Exception as e:
        bot.send_message(chat_id, f"❌ Erro ao salvar registro: {e}")

# =====================================================
# CONSULTA
# =====================================================
def escolher_tipo_consulta(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🔍 Por SA (O.S.)", "📡 Por Serial ONT", "📦 Todos")
    bot.send_message(message.chat.id, "Como deseja consultar os registros?", reply_markup=markup)
    bot.register_next_step_handler(message, tipo_consulta_escolhido)

def tipo_consulta_escolhido(message):
    opcao = message.text.strip().lower()

    if "sa" in opcao:
        msg = bot.send_message(message.chat.id, "Digite o número da *Ordem de Serviço (O.S.):*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: consultar_registros(m.chat.id, tipo="os", valor=m.text.strip()))

    elif "serial" in opcao or "ont" in opcao:
        msg = bot.send_message(message.chat.id, "Digite o *Serial da ONT:*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, lambda m: consultar_registros(m.chat.id, tipo="serial", valor=m.text.strip()))

    elif "todos" in opcao:
        consultar_registros(message.chat.id, tipo="todos")

    else:
        bot.send_message(message.chat.id, "❌ Opção inválida. Use /menu para tentar novamente.")

def consultar_registros(chat_id, tipo="todos", valor=None):
    try:
        query = "SELECT id, ordem_servico, serial_ont, data_registro FROM registros WHERE user_id = ?"
        params = [chat_id]

        if tipo == "os" and valor:
            query += " AND ordem_servico LIKE ?"
            params.append(f"%{valor}%")
        elif tipo == "serial" and valor:
            query += " AND serial_ont LIKE ?"
            params.append(f"%{valor}%")

        query += " ORDER BY id DESC LIMIT 10"

        with sqlite3.connect(DB_PATH) as connection:
            cursor = connection.cursor()
            cursor.execute(query, params)
            registros = cursor.fetchall()

        if not registros:
            bot.send_message(chat_id, "📭 Nenhum registro encontrado.")
            return

        bot.send_message(chat_id, f"🔎 Foram encontrados *{len(registros)}* registro(s):", parse_mode="Markdown")

        for reg in registros:
            reg_id, os_num, serial, data = reg
            bot.send_message(
                chat_id,
                f"📋 *Registro #{reg_id}*\n"
                f"O.S.: *{os_num}*\n"
                f"Serial: *{serial}*\n"
                f"🕒 Data/Hora: *{data}*",
                parse_mode="Markdown"
            )

            with sqlite3.connect(DB_PATH) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT caminho FROM imagens WHERE registro_id = ?", (reg_id,))
                imagens = cursor.fetchall()

            for img in imagens:
                path = img[0]
                if os.path.exists(path):
                    with open(path, 'rb') as f:
                        bot.send_photo(chat_id, f)
                else:
                    bot.send_message(chat_id, "⚠️ Imagem não encontrada.")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Erro ao consultar registros: {e}")

# =====================================================
# EXECUÇÃO
# =====================================================
if not hasattr(bot, 'user_data'):
    bot.user_data = {}

try:
    print("🤖 Bot rodando! Pressione Ctrl+C para parar.")
    bot.infinity_polling()
except KeyboardInterrupt:
    print("\n[Parada Elegante] Bot desligado pelo usuário (Ctrl+C).")
