import os
from dotenv import load_dotenv
from telegram.ext import Application, JobQueue
from handlers import setup_handlers
from jobs import setup_jobs

load_dotenv('htb.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')

def main():
    if not BOT_TOKEN:
        raise ValueError("Токен не найден! Проверьте файл htb.env")
    
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .job_queue(JobQueue())
        .build()
    )

    setup_handlers(application)
    setup_jobs(application)
    
    print("Бот успешно запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()