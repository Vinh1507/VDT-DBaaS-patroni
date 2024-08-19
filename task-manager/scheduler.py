from apscheduler.schedulers.blocking import BlockingScheduler
from tasks import print_message, check_patroni_schedule

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', seconds=5)
def scheduled_task():
    print_message.send("Hello from the scheduler!")
    check_patroni_schedule.send()

if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()
