from datetime import time, timedelta
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database import get_connection

TIMEZONE = pytz.timezone('Europe/Moscow')

async def send_reminders(context: CallbackContext):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT h.id, h.user_id, h.name, u.first_name 
        FROM Habits h
        JOIN Users u ON h.user_id = u.user_id
        WHERE h.is_active = 1
    """)

    habits = cursor.fetchall()
    conn.close()

    for i, (habit_id, user_id, habit_name, first_name) in enumerate(habits):
        context.job_queue.run_once(
            callback=send_single_reminder,
            when=timedelta(minutes=1*i),
            data={
                'habit_id': habit_id,
                'user_id': user_id,
                'habit_name': habit_name,
                'first_name': first_name
            },
            name=f"reminder_{user_id}_{habit_id}"
        )

async def send_single_reminder(context: CallbackContext):
    job = context.job
    data = job.data
    
    try:
        keyboard = [
            [InlineKeyboardButton("✔ Да", callback_data=f"done_{data['habit_id']}"),
             InlineKeyboardButton("✘ Нет", callback_data=f"skip_{data['habit_id']}")]
        ]
        
        await context.bot.send_message(
            chat_id=data['user_id'],
            text=f"{data['first_name']}, выполнили: {data['habit_name']}?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Stats (habit_id, dispatch_date, is_completed)
            VALUES (?, datetime('now'), 0)
        """, (data['habit_id'],))
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def setup_reminder_jobs(application):
    job_queue = application.job_queue
    
    morning_time = time(hour=7, minute=30, tzinfo=TIMEZONE)
    afternoon_time = time(hour=12, minute=30, tzinfo=TIMEZONE)
    evening_time = time(hour=20, minute=30, tzinfo=TIMEZONE)

    job_queue.run_daily(
        send_reminders,
        time=morning_time,
        days=tuple(range(7)),
        name="morning_reminders"
    )
    
    job_queue.run_daily(
        send_reminders,
        time=afternoon_time,
        days=tuple(range(7)),
        name="afternoon_reminders"
    )

    job_queue.run_daily(
        send_reminders,
        time=evening_time,
        days=tuple(range(7)),
        name="evening_reminders"
    )