import requests
import time
from datetime import datetime

URL = "https://anjodajuventude.com.br/#pedido"  # coloque a URL exata da página
BOT_TOKEN = "8305296309:AAG1iFblD59AhmxllWDdkj-0CkDynhgRPQ8"
CHAT_ID = "7100064741"

CHECK_INTERVAL = 30  # segundos
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
        response = requests.get(URL, timeout=10)
        page = response.text.lower()

        current_status = "FECHADO" if is_blocked(page) else "ABERTO"
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if last_status is None:
            last_status = current_status
            print(f"Status inicial: {current_status}")

        elif current_status != last_status:

            if current_status == "ABERTO":
                for i in range(3):
                    send_telegram(
                        f"🟢 PEDIDOS ABERTOS!\n"
                        f"Horário detectado: {now}\n"
                        f"Acesse: {URL}"
                    )
                    time.sleep(2)

            elif current_status == "FECHADO":
                send_telegram(
                    f"🔴 PEDIDOS FECHARAM.\n"
                    f"Horário detectado: {now}"
                )

            last_status = current_status

        else:
            print(f"{now} - Sem mudança ({current_status})")

    except Exception as e:
        print("Erro:", e)

    time.sleep(CHECK_INTERVAL)
