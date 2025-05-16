from .start import setup_start_handlers
from .habits import setup_habits_handlers
from .reminders import setup_reminders_handlers

def setup_handlers(application):
    setup_start_handlers(application)
    setup_habits_handlers(application)
    setup_reminders_handlers(application)