from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import get_connection

async def handle_button(update, context):
    query = update.callback_query
    await query.answer("⌛ Обрабатываю ваш ответ...")
    
    try:
        user_id = query.from_user.id
        action, habit_id = query.data.split('_')
        habit_id = int(habit_id)
        is_completed = 1 if action == 'done' else 0

        await query.edit_message_text(
            text=f"{query.message.text}\n\n⌛ Обработка ответа...",
            reply_markup=None
        )
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM Stats
            WHERE habit_id = ?
            ORDER BY dispatch_date DESC
            LIMIT 1
        """, (habit_id,))
        
        last_stat = cursor.fetchone()
        if not last_stat:
            await query.edit_message_text("✘ Не найдено записей для обновления")
            return
            
        stat_id = last_stat[0]

        cursor.execute("""
            UPDATE Stats 
            SET is_completed = ?
            WHERE id = ?
        """, (is_completed, stat_id))
        
        if not is_completed:
            cursor.execute("""
                SELECT COUNT(*) FROM Stats
                WHERE habit_id = ? 
                AND is_completed = 0
                AND date(dispatch_date) >= date('now', '-7 days')
            """, (habit_id,))
            
            if cursor.fetchone()[0] >= 7:
                cursor.execute("UPDATE Habits SET is_active = 0 WHERE id = ?", (habit_id,))
                await query.edit_message_text("Привычка деактивирована (7 пропусков)")
                conn.commit()
                return
        
        conn.commit()

        await query.edit_message_text(
            text=f"{query.message.text}\n\n{'✔ Выполнено' if is_completed else '✘ Пропущено'}"
        )
        
    except Exception as e:
        print(f"Ошибка обработки кнопки: {str(e)}")
        await query.edit_message_text("✘ Ошибка при обработке ответа")
    finally:
        if 'conn' in locals():
            conn.close()

def setup_reminders_handlers(application):
    application.add_handler(CallbackQueryHandler(handle_button))