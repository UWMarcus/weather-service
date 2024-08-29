import json
import requests
import os
import time
from fastapi import FastAPI, BackgroundTasks
from typing import Dict
from threading import Lock
from datetime import datetime, timezone

from app.config import Config

app = FastAPI()

tasks_status: Dict[int, str] = {}
tasks_progress: Dict[int, int] = {}

status_lock = Lock()
progress_lock = Lock()
data_lock = Lock()

def read_stored_data():
    with data_lock:
        if os.path.exists(Config.JSON_FILE_NAME):
            with open(Config.JSON_FILE_NAME, 'r') as file:
                return json.load(file)
        return None

def append_stored_data(result):
    with data_lock:
        with open(Config.JSON_FILE_NAME, 'r+') as file:
            data = json.load(file)
            data.append(result)
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

def create_empty_data_file():
    with open(Config.JSON_FILE_NAME, 'w') as file:
        json.dump([], file)

def initialize_variables():
    data = read_stored_data()
    if data:
        for record in data:
            tasks_status[record['user_id']] = 'completed'
            tasks_progress[record['user_id']] = 100
    else:
        create_empty_data_file()

def partition_list(large_list, max_size=Config.MAX_CITIES_PER_MINUTE):
    partitioned_list = []
    
    for i in range(0, len(large_list), max_size):
        partitioned_list.append(large_list[i:i + max_size])
    
    return partitioned_list

def get_open_weather_data(user_id: int):
    with status_lock:
        tasks_status[user_id] = 'running'

    data = {}
    request_timestamp_datetime = datetime.now(timezone.utc)
    request_timestamp = request_timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')

    url = Config.OPENWEATHER_API_URL
    results = []
    
    batches = partition_list(Config.CITIES_IDS)
    start_reference_time = datetime.now(timezone.utc)
    for batch in batches:
        for city_id in batch:
            params = {
                'id': str(city_id),
                'appid': Config.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response =  requests.get(url, params=params)
            weather_data = response.json()
            if weather_data:
                results.append({
                    'city_id': city_id,
                    'temperature_celsius': weather_data['main']['temp'],
                    'humidity': weather_data['main']['humidity']
                })
                with progress_lock:
                    tasks_progress[user_id] = 100*len(results)/len(Config.CITIES_IDS)

        if len(results) == len(Config.CITIES_IDS):
            break

        while ((datetime.now(timezone.utc) - start_reference_time).seconds/60) < 1:
            time.sleep(Config.DEFAULT_WAIT_INTERVAL)
        start_reference_time = datetime.now(timezone.utc)
    
    data = {
        'user_id': user_id,
        'datetime': request_timestamp,
        'weather_data': results
    }
    append_stored_data(data)

    with status_lock:
        tasks_status[user_id] = 'completed'

initialize_variables()

@app.post('/get_weather_data/{user_id}')
def start_task(user_id: int, background_tasks: BackgroundTasks):
    
    if user_id not in tasks_status:
        with status_lock:
            tasks_status[user_id] = 'started'
        with progress_lock:
            tasks_progress[user_id] = 0
        background_tasks.add_task(get_open_weather_data, user_id)
        return {'user_id': user_id, 'status': 'Started'}
    else:
        return {'user_id': user_id, 'status': 'Not started due to duplicated user_id'}

@app.get('/get_weather_data_status/{user_id}')
def get_status(user_id: int):
    with status_lock:
        status = tasks_status.get(user_id)
    with progress_lock:
        progress = tasks_progress.get(user_id)
    return {
        'user_id': user_id,
        'status': status,
        'progress': progress
    }

# Para rodar o aplicativo:
# uvicorn app.main:app --reload