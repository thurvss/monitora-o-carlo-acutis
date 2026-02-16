import requests
import time
from datetime import datetime

URL = "https://anjodajuventude.com.br/"
BOT_TOKEN = "8305296309:AAEtnnYV9HIe6hv-KO8I_nNCz-l1Pm1lAS8"
CHAT_ID = "7100064741"

CHECK_INTERVAL = 30
PHRASE_BLOCKED = "envio de novos pedidos está suspenso"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def is_blocked(page_text):
    return PHRASE_BLOCKED in page_text.lower()

print("Monitor iniciado...")

last_status = None

while True:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(URL, headers=headers, timeout=10)
        page = response.text.lower()

        current_status = "FECHADO" if is_blocked(page) else "ABERTO"
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if last_status is None:
            last_status = current_status
            print("Status inicial:", current_status)

        elif current_status != last_status:

            if current_status == "ABERTO":
                for _ in range(3):
                    send_telegram(
                        f"🟢 PEDIDOS ABERTOS!\n"
                        f"Horário: {now}\n"
                        f"{URL}"
                    )
                    time.sleep(2)

            elif current_status == "FECHADO":
                send_telegram(
                    f"🔴 PEDIDOS FECHARAM.\nHorário: {now}"
                )

            last_status = current_status

        else:
            print(f"{now} - Sem mudança ({current_status})")

    except Exception as e:
        print("Erro:", e)

    time.sleep(CHECK_INTERVAL)
