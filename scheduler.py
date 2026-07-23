import schedule
import time
from datetime import datetime
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def parse_datetime(date_str: str) -> datetime:
    """
    Parses a datetime string in format 'YYYY-MM-DD HH:MM' and returns a datetime object.
    Validates it's in the future.
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        # Make timezone aware using local timezone
        dt = dt.astimezone()
        
        now = datetime.now().astimezone()
        if dt <= now:
            raise ValueError("Scheduled time must be in the future.")
        return dt
    except ValueError as e:
        raise ValueError(f"Error parsing datetime: {e}")

def schedule_email(send_function: Callable, send_time: datetime, **kwargs: Any) -> schedule.Job:
    """
    Schedules a function call at a specific datetime.
    Uses the schedule library. Prints countdown info.
    """
    time_str = send_time.strftime("%H:%M")
    
    def job_wrapper():
        now = datetime.now().astimezone()
        # Check if we have reached or passed the target date
        if now.date() >= send_time.date():
            print(f"\n[{now.strftime('%Y-%m-%d %H:%M:%S')}] Executing scheduled email send...")
            send_function(**kwargs)
            return schedule.CancelJob
    
    # Schedule to run every day at the specified time, wrapper ensures it only executes on/after target date
    job = schedule.every().day.at(time_str).do(job_wrapper)
    print(f"Email scheduled for {send_time.strftime('%Y-%m-%d %H:%M %Z')}.")
    return job

def run_scheduler() -> None:
    """
    Runs the schedule event loop, checking every second.
    Prints a waiting message periodically.
    """
    print("Starting scheduler... Press Ctrl+C to cancel.")
    counter = 0
    try:
        while schedule.get_jobs():
            schedule.run_pending()
            time.sleep(1)
            counter += 1
            if counter % 60 == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler is waiting...")
    except KeyboardInterrupt:
        print("\nScheduler interrupted by user. Cancelling jobs.")
        schedule.clear()
    finally:
        print("Scheduler finished.")
