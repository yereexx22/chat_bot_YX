import time
import os
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Carga variables de entorno
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("❌ Falta API_KEY en .env")
    exit()

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-1.5-flash-latest"

try:
    yunix = genai.GenerativeModel(MODEL_NAME)
    chat = yunix.start_chat(history=[])
    print(f"✅ Modelo cargado: {MODEL_NAME}")
except Exception as e:
    print(f"❌ Error al cargar modelo: {e}")
    chat = None

app = Flask(__name__)

# Historial visual separado
chat_log = []
temp_response = ""

# Respuestas locales
local_responses = {
    "hola": "¡Hola! ¿Cómo estás?",
    " hola quien eres": "holiiis soy yunix tu amiga digital que te resolvera cualquier duda que tengas ❤️.",
    "adiós": "¡Hasta lueguito amiguit@!",
    "gracias": "¡De nada!",
    "como estás": "Estoy aquí para ayudarte, ¿en qué te puedo servir pero nada de cosas raras eeh?"
}

# Página principal (solo muestra historial confirmado)
@app.route("/", methods=["GET"])
def home():
    return render_template(
        "index.html",
        chat_history=chat_log,
        error=None,
        last_response=""
    )

# Procesa el mensaje y genera respuesta (sin agregar al historial aún)
@app.route("/send", methods=["POST"])
def send():
    global temp_response
    user_input = request.form.get("user_input", "").strip().lower()

    if user_input and chat:
        # Evita duplicar el mensaje del usuario
        if not chat_log or chat_log[-1]["role"] != "user" or chat_log[-1]["text"] != user_input:
            chat_log.append({"role": "user", "text": user_input})

        # Genera respuesta local o por API
        if user_input in local_responses:
            temp_response = local_responses[user_input]
        else:
            time.sleep(2)
            response = chat.send_message(user_input)
            temp_response = response.text

        # Muestra la respuesta animada (sin agregar al historial aún)
        return render_template(
            "index.html",
            chat_history=chat_log,
            error=None,
            last_response=temp_response
        )

    return redirect(url_for("home"))

# Confirma la respuesta y la agrega al historial visual
@app.route("/confirm", methods=["POST"])
def confirm_response():
    global temp_response
    if temp_response:
        # Evita duplicar la respuesta
        if not chat_log or chat_log[-1]["role"] != "model" or chat_log[-1]["text"] != temp_response:
            chat_log.append({"role": "model", "text": temp_response})
        temp_response = ""
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)