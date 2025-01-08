import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from telegram.ext import (
    ContextTypes,
)

import datetime
import pytz

from bd import create_user, create_timer, get_one_timers
from states import MAINMENU, SETTIME, GETDATE, GETTIME, GETMESS, CHOICE
from all_jobs import send_all_notif
from start import start
from all_jobs import timer_call, counter


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введи дату из будущего или прошлого (В формате: \n DD.MM.YYYY \n DDMMYYYY)",
    )
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

    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"вот - {pers_date}"
    )
    context.user_data["date"] = date

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите время выбранной даты\n формат:\nHH:MM\nHHMM\nHH-MM \n (Необъязательно - /skip, чтобы пропустить)",
    )
    return GETTIME


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.effective_message.text
    time = time[:2] + ":" + time[-2:]
    time = time + ":" + "00"
    context.user_data["time"] = time
    full_date = context.user_data["date"] + " " + context.user_data["time"]
    context.user_data["full_date"] = full_date
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите сообщение для таймера или пропустите (/skip)",
    )
    return GETMESS


async def skip_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_date = context.user_data["date"] + " 00:00:00"
    context.user_data["full_date"] = full_date
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите сообщение для таймера или пропустите (/skip)",
    )
    return GETMESS


async def get_mess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    context.user_data["message"] = message
    keyboard = [
        [InlineKeyboardButton("Добавить отсчет", callback_data="yes")],
        [InlineKeyboardButton("пропустить", callback_data="no")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Желаете ли вы выбрать время для ежедневного отсчета? (Бот будет присылать количество дней от/до даты в выбранное вами время.)",
        reply_markup=markup,
    )

    return CHOICE


async def skip_mess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = await get_one_timers(update.effective_user.id)
    message = f"{date}"
    context.user_data["message"] = message
    keyboard = [
        [InlineKeyboardButton("Добавить отсчет", callback_data="yes")],
        [InlineKeyboardButton("пропустить", callback_data="no")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Желаете ли вы выбрать время для ежедневного отсчета? (Бот будет присылать количество дней от/до даты в выбранное вами время.)",
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
        context.user_data["time"] = time
        return await put_timer_to_bd(update, context)


async def get_time_notif(update: Update, context: ContextTypes.DEFAULT_TYPE):  
    time = update.effective_message.text
    time = time[:2] + ":" + time[-2:]
    time = time + ":" + "00"
    context.user_data["time"] = time
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Каждый день в {time[:-3]} будет отправляться уведомление",
    )
    await put_timer_to_bd(update, context)


async def put_timer_to_bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = context.user_data["message"]
    full_date = context.user_data.get("full_date")
    id_timer = await create_timer(update.effective_user.id, full_date, message)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Ваш таймер успешно добавлен"
    )
    point = datetime.datetime.strptime(full_date, "%Y-%m-%d %H:%M:%S")

    context.job_queue.run_once(
        timer_call,
        point,
        data={"full_date": point, "message": message, "id_timer": id_timer},
        chat_id=update.effective_user.id,
    )
    time_lst = list(map(int, context.user_data["time"].split(":")))
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
