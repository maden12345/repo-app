import sqlite3

conn = sqlite3.connect('ip_logs.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        ip TEXT,
        user_agent TEXT,
        referer TEXT,
        cookie TEXT,
        screen_width INTEGER,
        screen_height INTEGER,
        device_type TEXT,
        previous_visits INTEGER
    )
''')
conn.commit()
conn.close()

