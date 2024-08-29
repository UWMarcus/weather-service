import pytest
import time
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def client():
    return AsyncClient(app=app, base_url='http://test')

@pytest.mark.asyncio
async def test_start_task(client):
    response = await client.post('/get_weather_data/-1')
    assert response.status_code == 200
    assert response.json() == {'user_id': -1, 'status': 'Started'}

@pytest.mark.asyncio
async def test_start_task_duplicate_user_id(client):
    # Start the task first
    await client.post('/get_weather_data/-2')
    
    # Attempt to start it again
    response = await client.post('/get_weather_data/-2')
    assert response.status_code == 200
    assert response.json() == {'user_id': -2, 'status': 'Not started due to duplicated user_id'}

@pytest.mark.asyncio
async def test_get_status_initial(client):
    response = await client.get('/get_weather_data_status/-3')
    assert response.status_code == 200
    assert response.json() == {'user_id': -3, 'status': None, 'progress': None}

@pytest.mark.asyncio
async def test_get_status_after_start(client):
    # Start the task first
    await client.post('/get_weather_data/-4')
    
    # Wait for some time to ensure progress can be updated
    time.sleep(2)
    
    response = await client.get('/get_weather_data_status/-4')
    assert response.status_code == 200
    status_data = response.json()
    assert status_data['user_id'] == -4
    assert status_data['status'] in ['started', 'running', 'completed']
    assert status_data['progress'] is not None


