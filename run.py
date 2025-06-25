from sys import executable, prefix
from subprocess import Popen, PIPE
from os.path import join, isfile
from threading import Thread
from shutil import which
from time import sleep
from os import name

# Joriy venv ichidagi python interpreteri
PYTHON = executable

# Ngrok’ni venv ichidan topish
def find_ngrok():
    # 1) PATH’da
    ng = which("ngrok")
    if ng:
        return ng
    # 2) Windows uchun Scripts/ngrok.exe
    possible = join(prefix, "Scripts", "ngrok.exe")
    if name == "nt" and isfile(possible):
        return possible
    # 3) Unix uchun bin/ngrok
    possible = join(prefix, "bin", "ngrok")
    if name != "nt" and isfile(possible):
        return possible
    raise FileNotFoundError("Ngrok topilmadi – iltimos, ngrok binar faylini venv/Scripts yoki PATH ga joylang.")

def start_ngrok():
    ngrok_bin = find_ngrok()
    # ngrok.yml ichida tunnellar nomi "app" deb belgilangani faraz
    cmd = [ngrok_bin, "start", "--config=ngrok.yml", "app"]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)

    # Chiquvchi satrlarni o‘qib, Forwarding URL ini aniqlaymiz
    for line in proc.stdout:
        line = line.strip()
        if line.startswith("Forwarding"):
            url = line.split()[1]
            print(f"[ngrok] Public URL: {url}")
            break
    # Kerak bo‘lsa protsessni to‘xtatish:
    # proc.terminate()

def start_uvicorn():
    # sys.executable orqali venv ichidagi python ishlatiladi
    cmd = [
        PYTHON, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8002",
    ]
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE, text=True)
    # Optional: loglarni real-time chiqarish
    for line in proc.stdout:
        print(f"[uvicorn] {line.strip()}")

if __name__ == "__main__":
    # 1) Avvalo FastAPI serverni ishga tushiramiz
    uv_thread = Thread(target=start_uvicorn, daemon=True)
    # 2) Keyin ngrok tunnellni ochamiz
    ng_thread = Thread(target=start_ngrok, daemon=True)

    uv_thread.start()
    # uvicorn to‘liq yuklanishini biroz kutish tavsiya etiladi
    sleep(1)
    ng_thread.start()

    # Ikkala thread ham ishlayotganini saqlab turamiz
    uv_thread.join()
    ng_thread.join()
