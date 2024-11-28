import telebot
import requests
import google.generativeai as genai
from telebot import types
from datetime import datetime

# Configura tu API Key directamente en el código
API_KEY = "AIzaSyBVkx-mK8oTpNxo1v0OVwuneUxwXio8-D8"
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Token del bot de Telegram
TELEGRAM_BOT_TOKEN = "7766374394:AAGuiC0QcqkHi9oR72DXv3xpvez3H6S2W-M"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# URLs base para clima y efemérides
url_clima = 'https://wttr.in/'
url_efemerides = 'https://es.wikipedia.org/api/rest_v1/feed/onthisday/events/'

# Función para mostrar el menú principal
def mostrar_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Clima + Efeméride")
    btn2 = types.KeyboardButton("Preguntar a Gemini")
    btn3 = types.KeyboardButton("Salir")
    markup.add(btn1, btn2, btn3)
    bot.send_message(
        message.chat.id,
        "¡Hola! Bienvenida a InfoClima. Selecciona una opción:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def manejar_opciones(message):
    if message.text == "Clima + Efeméride":
        msg = bot.reply_to(message, "¿De qué ciudad quieres conocer el clima?")
        bot.register_next_step_handler(msg, obtener_clima_y_efemeride)
    elif message.text == "Preguntar a Gemini":
        msg = bot.reply_to(message, "¿Qué quieres preguntarle a Gemini?")
        bot.register_next_step_handler(msg, responder_con_gemini)
    elif message.text == "Salir":
        bot.send_message(message.chat.id, "¡Gracias por usar InfoClima! ¡Hasta pronto!")
    else:
        mostrar_menu(message)

# Función para obtener el clima y efemérides
def obtener_clima_y_efemeride(message):
    ciudad = message.text.strip()
    try:
        # Solicitar el clima
        response_clima = requests.get(f'{url_clima}{ciudad}?format=%C+%t+%h+%w&m&lang=es')
        if response_clima.status_code == 200:
            clima_info = response_clima.text.strip()
            clima_texto = f"--- Clima en {ciudad.capitalize()} ---\n{clima_info}"
        else:
            clima_texto = f"Error al obtener el clima para {ciudad}."
    except:
        clima_texto = "Error al conectar con el servicio de clima."

    try:
        # Solicitar efemérides
        today = datetime.now()
        response_efemeride = requests.get(f"{url_efemerides}{today.month}/{today.day}")
        if response_efemeride.status_code == 200:
            data = response_efemeride.json()
            if 'events' in data and len(data['events']) > 0:
                evento = data['events'][0]
                efemeride_texto = f"--- ¿Sabías que...? ---\nEn el año {evento['year']}: {evento['text']}"
            else:
                efemeride_texto = "No se encontraron efemérides para el día de hoy."
        else:
            efemeride_texto = "Error al obtener la efeméride."
    except:
        efemeride_texto = "Error al conectar con el servicio de efemérides."

    bot.send_message(message.chat.id, f"{clima_texto}\n\n{efemeride_texto}")
    mostrar_menu(message)

# Función para responder usando Gemini
def responder_con_gemini(message):
    pregunta = message.text
    respuesta = model.generate_content("siempre vas a responder las preguntas en un lenguaje jovial" + pregunta)
    bot.send_message(message.chat.id, respuesta.text)
    mostrar_menu(message)
"""

    try:
        # Usar Google Generative AI para generar la respuesta
        respuesta = genai.generate_message(prompt=pregunta, model='models/chat-bison-001')
        if respuesta and hasattr(respuesta, 'candidates') and len(respuesta.candidates) > 0:
            texto_respuesta = respuesta.candidates[0]['output']
            bot.send_message(message.chat.id, texto_respuesta.strip())
        else:
            bot.send_message(message.chat.id, "Gemini no pudo generar una respuesta.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error al generar la respuesta con Gemini: {e}")
    
"""

# Iniciar el bot
bot.polling()
