import requests
import time
from datetime import datetime
import threading

URL = "https://anjodajuventude.com.br/"
BOT_TOKEN = "8305296309:AAEtnnYV9HIe6hv-KO8I_nNCz-l1Pm1lAS8"
CHAT_ID = "7100064741"

CHECK_INTERVAL = 30
PHRASE_BLOCKED = "envio de novos pedidos está suspenso"

last_status = None
last_update_id = None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
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

        if chat_id == int(CHAT_ID):
            handle_command(text)

def handle_command(text):
    global last_status

    if text == "/start":
        send_telegram("🤖 Monitor Carlo Acutis ativo.\nUse /status para ver situação atual.")

    elif text == "/status":
        if last_status:
            send_telegram(f"📊 Status atual: {last_status}")
        else:
            send_telegram("⏳ Ainda verificando o status...")

def check_site():
    global last_status

    while True:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(URL, headers=headers, timeout=10)
            page = response.text.lower()

            current_status = "FECHADO" if PHRASE_BLOCKED in page else "ABERTO"
            now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            if last_status is None:
                last_status = current_status

            elif current_status != last_status:

                if current_status == "ABERTO":
                    for _ in range(3):
                        send_telegram(
                            f"🟢 PEDIDOS ABERTOS!\nHorário: {now}\n{URL}"
                        )
                        time.sleep(2)

                elif current_status == "FECHADO":
                    send_telegram(
                        f"🔴 PEDIDOS FECHARAM.\nHorário: {now}"
                    )

                last_status = current_status

        except Exception as e:
            print("Erro:", e)

        time.sleep(CHECK_INTERVAL)

def bot_listener():
    while True:
        try:
            get_updates()
        except Exception as e:
            print("Erro bot:", e)

# Inicia as threads
threading.Thread(target=check_site).start()
threading.Thread(target=bot_listener).start()

print("Bot e monitor iniciados.")

