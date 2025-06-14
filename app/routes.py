from flask import Flask, request
from datetime import datetime
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('ip_logs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            ip TEXT,
            user_agent TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/")
def log_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Veritabanına kaydet
    conn = sqlite3.connect('ip_logs.db')
    c = conn.cursor()
    c.execute('INSERT INTO logs (time, ip, user_agent) VALUES (?, ?, ?)', (time, ip, user_agent))
    conn.commit()
    conn.close()

    # Dosyaya kaydet (append)
    with open("ip_logs.txt", "a") as f:
        f.write(f"[{time}] IP: {ip} | Agent: {user_agent}\n")

    return "<h1>Bağlantı kaydedildi.</h1>"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

