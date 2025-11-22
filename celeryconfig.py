from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()  # загружает .env

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "myuser")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "mypassword")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

broker_url = f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:5672//'

app = Celery('foodgram', broker=broker_url, backend='rpc://')
app.conf.task_routes = {
    'tasks.weather_task': {'queue': 'weather'},
    'tasks.currency_task': {'queue': 'currency'},
}
