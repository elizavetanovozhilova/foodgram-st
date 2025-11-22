import requests
import json
import os
from datetime import datetime
from celeryconfig import app

def save_result(task, data):
    os.makedirs("results", exist_ok=True)
    filename = f"results/{task}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

@app.task(name="tasks.weather_task")
def weather_task(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    save_result("weather", response)
    return response

@app.task(name="tasks.currency_task")
def currency_task(base, target, api_key=None):
    url = f"https://api.exchangerate.host/convert?from={base}&to={target}"
    response = requests.get(url).json()
    save_result("currency", response)
    return response
