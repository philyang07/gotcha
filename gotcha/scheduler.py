from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('date', seconds=1)
def say_hello_job():
    print("Hello")

scheduler.add_job(say_hello_job)

scheduler.start()
print("NIG")
# scheduler.add_job(say_hello_job, 'interval', seconds=1)

