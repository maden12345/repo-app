from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def log_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("ip_logs.txt", "a") as f:
        f.write(f"[{time}] IP: {ip} | Agent: {user_agent}\n")

    return "<h1>Yükleniyor...</h1><p>Bağlantı kuruluyor...</p>"
