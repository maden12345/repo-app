from flask import Flask, request, jsonify, Response
from datetime import datetime
import sqlite3
from functools import wraps
from app import app  # app/__init__.py'deki Flask uygulamasını import ediyoruz

# --- Basic Auth Yardımcı Fonksiyonları ---
def check_auth(username, password):
    return username == 'admin' and password == '554433'

def authenticate():
    return Response(
        'Authentication required.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# --- Ana sayfa - IP ve cihaz bilgisi toplanıyor ve log-details endpoint'ine POST yapılıyor ---
@app.route("/")
def log_ip():
    return """
    <html>
    <body>
        <h1>IP Log Sayfası</h1>
        <script>
            let previousVisits = localStorage.getItem('previousVisits');
            if(previousVisits === null){
                previousVisits = 0;
            } else {
                previousVisits = parseInt(previousVisits);
            }
            previousVisits++;
            localStorage.setItem('previousVisits', previousVisits);

            function getDeviceType() {
                const ua = navigator.userAgent;
                if (/mobile/i.test(ua)) return 'Mobil';
                if (/tablet/i.test(ua)) return 'Tablet';
                return 'Masaüstü';
            }

            fetch('/log-details', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    screen_width: window.screen.width,
                    screen_height: window.screen.height,
                    device_type: getDeviceType(),
                    previous_visits: previousVisits
                })
            });
        </script>
    </body>
    </html>
    """

# --- Log detaylarını kaydeden API endpoint ---
@app.route("/log-details", methods=["POST"])
def log_details():
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    referer = request.headers.get('Referer')
    cookie = request.headers.get('Cookie')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    screen_width = data.get('screen_width')
    screen_height = data.get('screen_height')
    device_type = data.get('device_type')
    previous_visits = data.get('previous_visits')

    conn = sqlite3.connect('ip_logs.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (
            time, ip, user_agent, referer, cookie,
            screen_width, screen_height, device_type, previous_visits
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (time, ip, user_agent, referer, cookie, screen_width, screen_height, device_type, previous_visits))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

# --- Tüm log kayıtlarını gösteren sayfa (Basic Auth korumalı) ---
@app.route("/logs")
@requires_auth
def view_logs():
    conn = sqlite3.connect('ip_logs.db')
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = c.fetchall()
    conn.close()

    html = """
    <html>
    <head>
        <title>IP Log Kayıtları</title>
        <style>
            table, th, td { border: 1px solid black; border-collapse: collapse; padding: 5px; }
            th { background-color: #f2f2f2; }
            td { max-width: 300px; word-wrap: break-word; }
        </style>
    </head>
    <body>
        <h1>IP Log Kayıtları</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Zaman</th>
                <th>IP</th>
                <th>User Agent</th>
                <th>Referer</th>
                <th>Cookie</th>
                <th>Ekran Genişliği</th>
                <th>Ekran Yüksekliği</th>
                <th>Cihaz Türü</th>
                <th>Önceki Ziyaretler</th>
            </tr>
    """

    for log in logs:
        (id, time, ip, user_agent, referer, cookie, sw, sh, device, prev_visits) = log
        html += f"""
            <tr>
                <td>{id}</td>
                <td>{time}</td>
                <td>{ip}</td>
                <td>{user_agent}</td>
                <td>{referer}</td>
                <td>{cookie}</td>
                <td>{sw}</td>
                <td>{sh}</td>
                <td>{device}</td>
                <td>{prev_visits}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html
