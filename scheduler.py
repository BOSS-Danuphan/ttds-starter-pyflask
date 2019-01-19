from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def minutes_job():
    print('This job is run every minutes.', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    with open('scheduler-log.txt', 'w+') as f:
        print('Writing log: start', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('Writing log: done', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

sched.start()
