from .reminders import setup_reminder_jobs
from .stats import setup_stats_jobs

def setup_jobs(application):
    setup_reminder_jobs(application)
    setup_stats_jobs(application)