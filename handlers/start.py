from telegram.ext import CommandHandler
from database import get_connection
from datetime import datetime

async def start(update, context):
    user = update.effective_user
    user_id = user.id
    username = user.username
    firstname = user.first_name

    conn = get_connection()
    cursor = conn.cursor()

    if conn:
        cursor.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Users (user_id, user_name, first_name, created_at) VALUES (?, ?, ?, ?)", 
                         (user_id, username, firstname, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            if cursor.rowcount > 0:
                conn.commit()
                await update.message.reply_text(f"Привет, {firstname}!\nЯ бот для формирования привычек.\n"
                                                "Напоминаю о твоих целях три раза в день: утром, днем и вечером. Ты отмечаешь, сделал задачу или нет. Если пропустишь 7 раз подряд — я уберу привычку из активных, чтобы тебя не перегружать."
                                                "А еще я каждую неделю присылаю тебе статистику ツ")
                await update.message.reply_text("Команды:\n"
                                                "/start - начать\n/add_habit - добавление привычки\n/delete_habit - удаление привычки\n/list_habits - показывает список привычек")
            else:
                await update.message.reply_text("Не удалось добавить пользователя. ⍨")
        else:
            await update.message.reply_text(f"С возвращением, {firstname}! ツ")
        conn.close()
    else:
        await update.message.reply_text("Ошибка подключения")

async def help_command(update, context):
    await update.message.reply_text("/start - начать\n/add_habit - добавление привычки\n/delete_habit - удаление привычки\n/list_habits - показывает список привычек")

def setup_start_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))