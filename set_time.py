from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    ContextTypes,
)

import datetime
import pytz

from bd import create_timer, get_one_timers
from states import GETDATE, GETTIME, GETMESS, CHOICE
from start import start
from all_jobs import timer_call, counter


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("Назад ◀️", callback_data="back")]]
    markup = InlineKeyboardMarkup(keyboard)
    message = await query.edit_message_text(
        text="Введите дату из будущего или прошлого\n(В формате: DD.MM.YYYY или DDMMYYYY)",
        reply_markup=markup,
    )
    context.user_data["message_id"] = message.id
    return GETDATE


async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pers_date = ""
    answer = update.effective_message.text
    answer = answer.lower()
    if "." in answer:
        answer = answer.split(".")
    else:
        answer = answer[:2], answer[2:4], answer[4:8]

    for i in range(3):
        pers_date += answer[i] + "."

    pers_date = pers_date[:-1]
    context.user_data["pers_data"] = pers_date
    date = pers_date[-4:] + "-" + pers_date[3:5] + "-" + pers_date[:2]
    context.user_data["date"] = date
    keyboard = [[InlineKeyboardButton("пропустить ⏭️", callback_data="skip")]]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
    await context.bot.edit_message_text(
        text=f"{pers_date}\nВведите время выбранной даты в формате:\nHH:MM\nHHMM\nHH-MM",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["message_id"],
        reply_markup=markup,
    )
    return GETTIME


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
    time = update.effective_message.text
    time = time[:2] + ":" + time[-2:]
    time = time + ":" + "00"
    context.user_data["time_once"] = time
    full_date = context.user_data["date"] + " " + context.user_data["time_once"]
    context.user_data["full_date"] = full_date
    query = update.callback_query
    keyboard = [[InlineKeyboardButton("пропустить ⏭️", callback_data="skip_time")]]
    markup = InlineKeyboardMarkup(keyboard)
    if query:
        await query.answer()
        await query.edit_message_text(
            text="Введите имя для таймера ⏰", reply_markup=markup
        )
    else:
        await context.bot.edit_message_text(
            text="Введите имя для таймера ⏰",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["message_id"],
            reply_markup=markup,
        )
    return GETMESS


async def skip_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    full_date = context.user_data["date"] + " 00:00:00"
    context.user_data["full_date"] = full_date
    keyboard = [[InlineKeyboardButton("пропустить ⏭️", callback_data="skip_time")]]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Введите имя для таймера ⏰", reply_markup=markup
    )
    return GETMESS


async def get_mess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    context.user_data["message"] = message
    keyboard = [
        [InlineKeyboardButton("Добавить отсчет", callback_data="yes")],
        [InlineKeyboardButton("пропустить ⏭️", callback_data="no")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(
        text="Желаете ли вы выбрать время для ежедневного отсчета?\n(Бот будет присылать количество дней от/до даты в выбранное вами время.)",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["message_id"],
        reply_markup=markup,
    )

    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
    return CHOICE


async def skip_mess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    date = await get_one_timers(update.effective_user.id)
    message = f"{date}"
    context.user_data["message"] = message
    keyboard = [
        [InlineKeyboardButton("Добавить отсчет", callback_data="yes")],
        [InlineKeyboardButton("пропустить ⏭️", callback_data="no")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Желаете ли вы выбрать время для ежедневного отсчета?\n(Бот будет присылать количество дней от/до даты в выбранное вами время.)",
        reply_markup=markup,
    )
    return CHOICE


async def choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "yes":
        await query.edit_message_text(
            text="Напишите во сколько вы хотите получать ежедневное уведомление?"
        )
    else:
        time = "12:00"
        context.user_data["time_daily"] = time

        return await put_timer_to_bd(update, context)


async def get_time_notif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.effective_message.text
    time = time[:2] + ":" + time[-2:]
    time = time + ":" + "00"
    context.user_data["time_daily"] = time
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Каждый день в {time[:-3]} будет отправляться уведомление",
    )
    await context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.effective_message.id
    )
    await put_timer_to_bd(update, context)


async def put_timer_to_bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data["message"]
    full_date = context.user_data.get("full_date")

    
    id_timer = await create_timer(update.effective_user.id, full_date, message, context.user_data["time_daily"])

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Ваш таймер успешно добавлен ✅"
    )
    point = datetime.datetime.strptime(full_date, "%Y-%m-%d %H:%M:%S")
    # проверка будущее/прошлое

    chat_id = update.effective_chat.id

    if point > datetime.datetime.now():  # дата в будущем
        difference = point - datetime.datetime.now()
        day_before = difference.days + 1
        message = context.user_data["message"]
        await context.bot.send_message(
            chat_id=chat_id, text=f"До {message} осталось {day_before} дней."
        )

        context.job_queue.run_once(
            timer_call,
            point,
            data={"full_date": point, "message": message, "id_timer": id_timer},
            chat_id=update.effective_user.id,
            name=f"job_ro_{id_timer}",
        )

    else:  # дата в прошлом
        difference = datetime.datetime.now() - point
        day_after = difference.days
        message = context.user_data["message"] if message != "[]" else f"{point}"
        await context.bot.send_message(
            chat_id=chat_id, text=f"С {message} прошло {day_after} дней."
        )

    time_lst = list(map(int, context.user_data["time_daily"].split(":")))
    time = datetime.time(
        hour=time_lst[0], minute=time_lst[1], tzinfo=pytz.timezone("Etc/GMT-3")
    )

    context.job_queue.run_daily(
        counter,
        time,
        data={"full_date": point, "message": message},
        chat_id=update.effective_user.id,
        name=f"job_{id_timer}",
    )

    return await start(update, context)
