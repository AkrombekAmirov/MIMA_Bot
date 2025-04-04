from subprocess import Popen, PIPE
from threading import Thread


def ngrok_config_path():
    ngrok_command = f"ngrok start --config=ngrok.yml app"
    ngrok_process = Popen(ngrok_command.split(), stdout=PIPE)

    ngrok_url = None
    for line in ngrok_process.stdout:
        line = line.decode("utf-8").strip()
        if line.startswith("Forwarding"):
            ngrok_url = line.split()[1]
            break
    ngrok_process.terminate()


def start_uvicon():
    uvicorn_command = "python -m uvicorn main:app --host 0.0.0.0 --port 8002"
    uvicorn_process = Popen(uvicorn_command.split(), stdout=PIPE)
    uvicorn_process.communicate()


fast = Thread(target=start_uvicon)
ngrok = Thread(target=ngrok_config_path)
fast.start()
ngrok.start()
