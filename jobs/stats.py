from datetime import datetime, time, timedelta
import pytz
from telegram.ext import CallbackContext
from database import get_connection

TIMEZONE = pytz.timezone('Europe/Moscow')

async def weekly_stats(context: CallbackContext):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                h.name,
                COUNT(CASE WHEN s.is_completed = 1 THEN 1 END) as completed,
                COUNT(CASE WHEN s.is_completed = 0 THEN 1 END) as skipped,
                COUNT(*) as total
            FROM Stats s
            JOIN Habits h ON s.habit_id = h.id
            WHERE date(s.dispatch_date) >= date('now', '-7 days')
            GROUP BY h.name
        """)
        
        stats = cursor.fetchall()
        
        if stats:
            message = "Итоги недели:\n\n"
            for name, completed, skipped, total in stats:
                success_rate = int((completed / total) * 100) if total > 0 else 0
                message += (
                    f"{name}:\n"
                    f"   {completed} выполнено\n"
                    f"   {skipped} пропущено\n"
                    f"   Успешность: {success_rate}%\n\n"
                )
            
            cursor.execute("SELECT user_id FROM Users")
            for (user_id,) in cursor.fetchall():
                try:
                    await context.bot.send_message(chat_id=user_id, text=message)
            
                    avg_success = sum(completed / total for _, completed, _, total in stats if total > 0) / len(stats)
            
                    if avg_success >= 0.8:
                        await context.bot.send_sticker(
                            chat_id=user_id,
                            sticker="CAACAgIAAxkBAAEOdf5oIgN0jSnwpOK4_XJ4leLfUDSWAAOzBgACY4tGDE01muxnA7Q9NgQ"
                            )
                    elif avg_success >= 0.5:
                        await context.bot.send_sticker(
                            chat_id=user_id,
                            sticker="CAACAgIAAxkBAAEOdgABaCIELhuyhQ4wl-Cl53zrmJqpJTQAAq4GAAJji0YMgWowf_NWP982BA"
                            )
                    else:
                        await context.bot.send_sticker(
                            chat_id=user_id,
                            sticker="CAACAgIAAxkBAAEOdgJoIgRhsZ_myf7iSLOPdL61PmZ5nwACrQYAAmOLRgz33yY9tU9adDYE"
                            )
                except Exception as e:
                    print(f"Не удалось отправить статистику пользователю {user_id}: {e}")
        
        cursor.execute("""
            DELETE FROM Stats 
            WHERE date(dispatch_date) < date('now', '-7 days')
        """)
        conn.commit()
        
    finally:
        conn.close()

def next_occurrence(target_time: time):
    now = datetime.now(TIMEZONE)
    days_ahead = (7 - now.weekday()) % 7
    next_monday = now + timedelta(days=days_ahead)
    return next_monday.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=0,
        microsecond=0
    )

def setup_stats_jobs(application):
    job_queue = application.job_queue
    stats_time = time(hour=7, minute=30, tzinfo=TIMEZONE)
    
    next_monday = next_occurrence(stats_time)
    job_queue.run_once(
        weekly_stats,
        when=next_monday,
        name="weekly_stats"
    )