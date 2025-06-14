from flask import Flask, request, send_file, session, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Kendine göre güçlü bir anahtar koy

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
    with open("ip_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"[{time}] IP: {ip} | Agent: {user_agent}\n")

    return "<h1>Bağlantı kaydedildi.</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == '554433':
            session['logged_in'] = True
            return redirect(url_for('show_logs'))
        else:
            return "<h3>Hatalı kullanıcı adı veya şifre</h3>", 401
    return '''
        <form method="post">
            Kullanıcı Adı: <input type="text" name="username" /><br>
            Şifre: <input type="password" name="password" /><br>
            <input type="submit" value="Giriş" />
        </form>
    '''

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/logs")
@login_required
def show_logs():
    conn = sqlite3.connect('ip_logs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM logs ORDER BY id DESC')
    logs = c.fetchall()
    conn.close()

    html = "<h2>IP Logları (Veritabanı)</h2><ul>"
    for log in logs:
        html += f"<li>{log[1]} - {log[2]} - {log[3]}</li>"
    html += "</ul>"
    return html

@app.route("/logs-file")
@login_required
def logs_file():
    try:
        with open("ip_logs.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return "<h2>IP Logları (Dosya)</h2><pre>" + content + "</pre>"
    except FileNotFoundError:
        return "<p>Dosya bulunamadı.</p>"

@app.route("/download-logs")
@login_required
def download_logs():
    try:
        return send_file("ip_logs.txt", as_attachment=True)
    except FileNotFoundError:
        return "<p>Dosya bulunamadı.</p>"

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=10000)
