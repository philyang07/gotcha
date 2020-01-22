from celery import Celery

app = Celery('tasks', backend='amqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj', broker="pyamqp://dyfobtkj:YsAQDCL9MtX8dNjL7a91-fdlhJzaR9H2@vulture.rmq.cloudamqp.com/dyfobtkj")

@app.task
def add(x, y):
    return x + y