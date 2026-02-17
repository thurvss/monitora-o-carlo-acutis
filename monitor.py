import requests
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import threading

URL = "https://anjodajuventude.com.br/"
BOT_TOKEN = "8305296309:AAEtnnYV9HIe6hv-KO8I_nNCz-l1Pm1lAS8"
AUTHORIZED_USERS = [
    7100064741, # Arthur
    6866743029 # Jonnybel
]

CHECK_INTERVAL = 30
PHRASE_BLOCKED = "envio de novos pedidos está suspenso"

last_status = None
last_open_time = None
last_close_time = None
last_update_id = None
bot_online = True
last_error = None


def send_telegram(message):
    for user_id in AUTHORIZED_USERS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": user_id,
            "text": message
        }
        requests.post(url, data=data)

def get_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 30}

    if last_update_id:
        params["offset"] = last_update_id + 1

    response = requests.get(url, params=params)
    data = response.json()

    for update in data.get("result", []):
        last_update_id = update["update_id"]
        message = update.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if chat_id in AUTHORIZED_USERS:
            handle_command(text)

def handle_command(text):
    global last_status, last_open_time, last_close_time

    if text == "/start":
        send_telegram("🤖 Bot já está online e monitorando corretamente.")

    elif text == "/status":
        status_bot = "🟢 Online" if bot_online else f"🔴 Erro: {last_error}"

        if last_status == "ABERTO":
            info = f"🟢 Solicitações ABERTAS desde:\n{last_open_time}"
        elif last_status == "FECHADO":
            info = f"🔴 Solicitações FECHADAS em:\n{last_close_time}"
        else:
            info = "⏳ Ainda verificando status inicial..."

        send_telegram(
            f"📊 STATUS DO BOT\n"
            f"{status_bot}\n\n"
            f"📌 STATUS DAS SOLICITAÇÕES\n"
            f"{info}"
        )

def check_site():
    global last_status, last_open_time, last_close_time, bot_online, last_error

    while True:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(URL, headers=headers, timeout=10)
            page = response.text.lower()

            current_status = "FECHADO" if PHRASE_BLOCKED in page else "ABERTO"
            now = datetime.now(ZoneInfo("America/Manaus")).strftime("%d/%m/%Y %H:%M:%S")

            if last_status is None:
                last_status = current_status

                if current_status == "ABERTO":
                    last_open_time = now
                else:
                    last_close_time = now

            elif current_status != last_status:

                if current_status == "ABERTO":
                    last_open_time = now

                    for _ in range(3):
                        send_telegram("🟢 SOLICITAÇÕES ABERTAS!")
                        time.sleep(2)

                elif current_status == "FECHADO":
                    last_close_time = now
                    send_telegram(f"🔴 SOLICITAÇÕES FECHARAM.\n{now}")

                last_status = current_status

            bot_online = True
            last_error = None

        except Exception as e:
            bot_online = False
            last_error = str(e)

        time.sleep(CHECK_INTERVAL)

def bot_listener():
    while True:
        try:
            get_updates()
        except Exception:
            pass


# Inicia tudo
threading.Thread(target=check_site).start()
threading.Thread(target=bot_listener).start()

send_telegram("🤖 Bot online e monitorando solicitações.")
print("Bot iniciado com sucesso.")



