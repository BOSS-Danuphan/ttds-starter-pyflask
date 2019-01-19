from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def minutes_job():
    with open('scheduler-log.txt', 'w+') as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('This job is run every minutes.')

sched.start()
