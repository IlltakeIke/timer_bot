# Делаем две таблицы и соед их. 
# Юзерс [id, имя, количество таймеров]
# Таймерс [id INTEGER PRIMARY KEY AUTOINCREMENT, datetime DATETIME ]

#2024-05-04 17:55:28 %Y-%m-%D %H:%M:%S

import sqlite3

def create_table():
    conn = sqlite3.connect("timer_bot.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                                                id INTEGER PRIMARY KEY,
                                                name TEXT,
                                                numtim INTEGER DEFAULT 0
                                                    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS timers (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                datetime DATETIME,
                                                user_id INTEGER,
                                                FOREIGN KEY (user_id) REFERENCES users (id)
                                                    )''')
                                                    
    conn.commit()
    conn.close()

def create_user(id_tg, name):
    conn = sqlite3.connect("timer_bot.db")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO users (id, name) VALUES ({id_tg}, '{name}')")
    conn.commit()
    conn.close()

def create_timer(id_tg, timer_datetime):
    conn = sqlite3.connect("timer_bot.db")
    cur = conn.cursor()
    cur.execute(f"INSERT INTO timers (datetime, user_id) VALUES ('{timer_datetime}', {id_tg})")
    conn.commit()
    conn.close()

def update_users(user_id):
    conn = sqlite3.connect("timer_bot.db")
    cur = conn.cursor()
    cur.execute(f'SELECT numtim FROM users WHERE id = {user_id}')
    user = cur.fetchone() #в юзере картеж(0,)
    cur.execute(f'UPDATE users SET numtim = {user[0]+1} WHERE id = {user_id}')
    conn.commit()
    conn.close()

def get_all_timers():
    conn = sqlite3.connect("timer_bot.db")
    cur = conn.cursor()
    cur.execute('SELECT user_id, datetime FROM timers')
    users_data = cur.fetchall() #в юзере картеж(0,)
    conn.close()
    return users_data
    