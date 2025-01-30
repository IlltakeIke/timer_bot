from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
)
import datetime

from states import CHECK
from bd import check_timers
from babel.dates import format_datetime


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = []
    user_timers = await check_timers(update.effective_user.id)
    text = ""
    i = 1
    for timer in user_timers:
        date_obj = datetime.datetime.strptime(timer[2], "%Y-%m-%d %H:%M:%S")
        mess = (
            timer[0]
            if timer[0] != "Ваш таймер истек"
            else f"Таймер {timer[1]} - {format_datetime(date_obj, 'hh:mm:ss d MMMM y года', locale='ru')}"
        )
        if mess == "[]":
            mess = timer[2]
        text += f"{i}. {mess}\n"
        button = InlineKeyboardButton(f"Таймер {timer[1]}", callback_data=f"{timer[1]}")
        keyboard.append([button])
        i += 1
    if not text:
        text = "У вас пока нет дат"

    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=f"{text}", reply_markup=markup)
    return CHECK
