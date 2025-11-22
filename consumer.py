import json
import os
import argparse
import hvac
import pika
import requests
from datetime import datetime

print("DEBUG: consumer started")


VAULT_ADDR = "http://127.0.0.1:8200"


def get_secret(path):
    client = hvac.Client(url=VAULT_ADDR)
    client.token = os.environ.get("VAULT_TOKEN")

    secret = client.secrets.kv.read_secret_version(path=path)
    return secret["data"]["data"]


def process_weather(params):
    city = params["city"]
    secrets = get_secret("foodgram/api_weather")
    api_key = secrets["API_KEY"]

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()

    save_result("weather", response)


def process_currency(params):
    secrets = get_secret("foodgram/api_currency")
    base = params["base"]
    target = params["target"]

    url = f"https://api.exchangerate.host/convert?from={base}&to={target}"
    response = requests.get(url).json()

    save_result("currency", response)


def save_result(task, data):
    os.makedirs("results", exist_ok=True)
    filename = f"results/{task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✔ Результат сохранён в {filename}")


def callback(ch, method, properties, body):
    message = json.loads(body)
    task = message["task"]
    params = message["params"]

    print(f"← Получено сообщение: {message}")

    if task == "weather":
        process_weather(params)
    elif task == "currency":
        process_currency(params)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer(queue_name):
    rabbit = get_secret("foodgram/rabbitmq")
    user = rabbit["RABBITMQ_USER"]
    password = rabbit["RABBITMQ_PASSWORD"]

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            port=5672,
            credentials=pika.PlainCredentials(user, password)
        )
    )

    channel = connection.channel()

    channel.exchange_declare(
        exchange="foodgram_exchange",
        exchange_type="direct",
        durable=True
    )

    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(
        exchange="foodgram_exchange",
        queue=queue_name,
        routing_key=queue_name
    )

    print(f"✔ Ожидание сообщений из очереди: {queue_name}")
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", required=True)
    args = parser.parse_args()

    start_consumer(args.queue)
