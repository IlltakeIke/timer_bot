# Делаем две таблицы и соед их. 
# Юзерс [id, имя, количество таймеров]
# Таймерс [id INTEGER PRIMARY KEY AUTOINCREMENT, datetime DATETIME ]

#2024-05-04 17:55:28 %Y-%m-%D %H:%M:%S

import aiosqlite

async def create_table():
    db = await aiosqlite.connect("timer_bot.db")
    await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                                id INTEGER PRIMARY KEY,
                                                name TEXT,
                                                numtim INTEGER DEFAULT 0
                                                    )''')

    await db.execute('''CREATE TABLE IF NOT EXISTS timers (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                datetime DATETIME,
                                                user_id INTEGER,
                                                message TEXT,
                                                active INTEGER DEFAULT 1,
                                                notif INTEGER, 
                                                FOREIGN KEY (user_id) REFERENCES users (id)
                                                    )''')#24 строка это чойз 
                                                    
    await db.commit()
    await db.close()

async def create_user(id_tg, name):
    db = await aiosqlite.connect("timer_bot.db")
    user_cur = await db.execute(f'SELECT id FROM users WHERE id = {id_tg}')
    user = await user_cur.fetchone() # (id,) | None
    if not user: 
        await db.execute(f"INSERT INTO users (id, name) VALUES ({id_tg}, '{name}')")
        await db.commit()
    await db.close()

async def create_timer(id_tg, timer_datetime, message): 
    db = await aiosqlite.connect("timer_bot.db")
    data_cur = await db.execute(f"INSERT INTO timers (datetime, user_id, message) VALUES ('{timer_datetime}', {id_tg}, '{message}')")
    id_timer = data_cur.lastrowid # он ноет, что int не может быть в await 
   #id_timer = await data_cur.lastrowid
    await db.commit()
    await db.close()
    return id_timer

async def update_users(user_id):
    db = await aiosqlite.connect("timer_bot.db")
    user_cur = await db.execute(f'SELECT numtim FROM users WHERE id = {user_id}')
    user = await user_cur.fetchone() #в юзере картеж(0,)
    await db.commit()
    await db.execute(f'UPDATE users SET numtim = {user[0]+1} WHERE id = {user_id}')
    await db.close()

async def get_all_timers():
    db = await aiosqlite.connect("timer_bot.db")
    user_cur = await db.execute('SELECT user_id, datetime FROM timers')
    users_data = await user_cur.fetchall() #в юзере картеж(0,)
    await db.close()
    return users_data

async def get_one_timers(user_id):
    db = await aiosqlite.connect("timer_bot.db")
    user_cur = await db.cursor()
    await user_cur.execute(f'SELECT user_id, datetime FROM timers WHERE id = {user_id}')
    users_data = await user_cur.fetchall() #в юзере картеж(0,)
    await db.close()
    return users_data

async def active(id_timer):
    db = await aiosqlite.connect("timer_bot.db")
    await db.execute(f'UPDATE timers SET active = {0} WHERE id = {id_timer}')
    await db.commit()
    await db.close()
    return True

async def check_timers(id_user):
    db = await aiosqlite.connect("timer_bot.db")
    timer_cur = await db.cursor()
    await timer_cur.execute(f'SELECT message, id, datetime FROM timers WHERE user_id = {id_user} and datetime > CURRENT_TIMESTAMP')
    user_timers = await timer_cur.fetchall()
    await db.commit()
    await db.close()
    return user_timers 
'''все таймеры чела которые в будущем (active=1) -> пихаем их в кнопки -> 'нажмите на таймер чтоб удалить' -> проверка точно ли да 

сделать всё в одном сообщении и меняются только кнопки, сообще чувака удаляются
'''

async def get_all_timers_by_user(id_user):
    db = await aiosqlite.connect("timer_bot.db")
    timer_cur = await db.cursor()
    await timer_cur.execute(f'SELECT message, id, datetime FROM timers WHERE user_id = {id_user}')
    user_timers = await timer_cur.fetchall()
    await db.commit()
    await db.close()
    return user_timers

async def remove_timer(id_timer):
    db = await aiosqlite.connect("timer_bot.db")
    timer_cur = await db.cursor()
    await timer_cur.execute(f'DELETE FROM timers WHERE id = {id_timer}')
    await db.commit()
    await db.close()

