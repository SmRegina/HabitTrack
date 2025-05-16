from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from database import get_connection

HABIT_NAME = 1

async def start_add_habit(update: Update, context):
    await update.message.reply_text("Введите название новой привычки:")
    return HABIT_NAME

async def save_habit(update: Update, context):
    user_id = update.effective_user.id
    habit_name = update.message.text
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM Users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        await update.message.reply_text("Сначала выполните команду /start")
        conn.close()
        return ConversationHandler.END
    
    cursor.execute(
        "INSERT INTO Habits (user_id, name, is_active) VALUES (?, ?, ?)",
        (user_id, habit_name, True)
    )
    
    if cursor.rowcount > 0:
        conn.commit()
        await update.message.reply_text(f"✔ Привычка '{habit_name}' добавлена!")
    else:
        await update.message.reply_text("✘ Не удалось добавить привычку")
    
    conn.close()
    return ConversationHandler.END

async def list_habits(update: Update, context):
    user_id = update.effective_user.id
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name, is_active FROM Habits WHERE user_id=?", (user_id,))
        habits = cursor.fetchall()
        
        if not habits:
            await update.message.reply_text("У вас пока нет привычек. Добавьте через /add_habit")
            return
            
        message = "Список ваших привычек:\n\n"
        for i, (name, is_active) in enumerate(habits, 1):
            status = "- активна" if is_active else "- неактивна"
            message += f"{i}. {name} {status}\n"
            
        await update.message.reply_text(message)
    finally:
        conn.close()

async def delete_habit(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Habits WHERE user_id = ?", (user_id,))
    habits = cursor.fetchall()
    conn.close()
    
    if not habits:
        await update.message.reply_text("У вас нет привычек для удаления")
        return
    
    keyboard = [
        [InlineKeyboardButton(habit[1], callback_data=f"delete_{habit[0]}")]
        for habit in habits
    ]
    keyboard.append([InlineKeyboardButton("Отменить", callback_data="cancel")])
    
    await update.message.reply_text(
        "🗑 Выберите привычку для удаления:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_deletion(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel":
        await query.edit_message_text("✘ Удаление отменено")
        return
    
    habit_id = int(query.data.split('_')[1])
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()
    
    await query.edit_message_text("✔ Привычка успешно удалена")

def setup_habits_handlers(application):
    add_habit_handler = ConversationHandler(
        entry_points=[CommandHandler('add_habit', start_add_habit)],
        states={
            HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_habit)]
        },
        fallbacks=[]
    )
    
    application.add_handler(add_habit_handler)
    application.add_handler(CommandHandler("list_habits", list_habits))
    application.add_handler(CommandHandler("delete_habit", delete_habit))
    application.add_handler(CallbackQueryHandler(handle_deletion, pattern=r'^delete_|cancel$'))