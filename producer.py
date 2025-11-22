import json
import sys
import hvac
import pika
import os


VAULT_ADDR = "http://127.0.0.1:8200"
VAULT_PATH = "secret/data/foodgram/rabbitmq"


def get_rabbit_credentials():
    client = hvac.Client(url=VAULT_ADDR)
    client.token = os.environ.get("VAULT_TOKEN")

    secret = client.secrets.kv.read_secret_version(path="foodgram/rabbitmq")
    data = secret["data"]["data"]

    return data["RABBITMQ_USER"], data["RABBITMQ_PASSWORD"]


def send_task(task_name, **params):
    user, password = get_rabbit_credentials()

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

    message = {
        "task": task_name,
        "params": params
    }

    channel.basic_publish(
        exchange="foodgram_exchange",
        routing_key=task_name,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)  # durable
    )

    print(f"→ Sent task: {message}")

    connection.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python producer.py weather Moscow")
        print("  python producer.py currency USD EUR")
        sys.exit(1)

    task = sys.argv[1]

    if task == "weather":
        city = sys.argv[2]
        send_task("weather", city=city)

    elif task == "currency":
        base = sys.argv[2]
        target = sys.argv[3]
        send_task("currency", base=base, target=target)

    else:
        print("Неизвестная задача")
