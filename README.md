# FastAPI Weather Data Application

## Overview

This FastAPI application provides endpoints for fetching weather data from the OpenWeather API. It allows users to start a background task to retrieve weather information for a list of cities and track the status of these tasks. The data is downloaded and stored internally in a json file.

## Project Structure

- `app/`: Contains the main application logic and configuration.
  - `main.py`: Defines the FastAPI application, endpoints, and background tasks.
  - `config.py`: Configuration settings, including API keys, file paths and list of city IDs.

- `tests/`: Contains the test suite for the application.
  - `test_main.py`: Test cases for the application's endpoints.
  - `config.py`: Configuration specific to testing.

- `requirements.txt`: Lists the Python dependencies required for the project.
- `Dockerfile`: Defines the Docker image for the application.

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. **Clone the repository:**

       git clone https://github.com/UWMarcus/weather-service.git

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install the required packages:**

        pip install -r requirements.txt

4. **Set up environment variables:**

   You need to set the OPENWEATHER_API_KEY environment variable. Create a .env file or set it in your shell:

       export OPENWEATHER_API_KEY='your_openweather_api_key'

## Usage

### Running the Application

1. **Start the FastAPI server**

       uvicorn app.main:app --reload

      By default, the server will run on http://127.0.0.1:8000.

2. **Access the API documentation:**

      Visit http://127.0.0.1:8000/docs for interactive API documentation provided by FastAPI.

### API Endpoints

- Start Weather Data Collection Task

      POST /get_weather_data/{user_id}

    Starts a background task to fetch weather data from Open Weather for the specified user_id. Returns the task status.

  **Request Example:**

      POST /get_weather_data/1

  **Response Example:**

      {
        "user_id": 1,
        "status": "Started"
      }

- Get Status from the POST Request

      GET /get_weather_data_status/{user_id}

  Retrieves the status and progress of the weather data task for the specified user_id.

  **Request Example:**

      GET /get_weather_data_status/1

  **Response Example:**

      {
        "user_id": 1,
        "status": "running",
        "progress": 50
      }

## Testing

1. **Before Running Tests Instructions:**

    1. In the **app/main.py** file, go to the import of the config file and change its source to be from the **tests** folder instead of the **app** (remember to change it back after you've done testing otherwise the application may fail)

            from tests.config import Config
    
    2. Make sure you delete (if it exists) the data.json file from the **tests** folder (NOT FROM APP)
   
2. **Run the tests using pytest:**

       pytest

   This will execute the test suite defined in tests/test_main.py which consists of:
   - `test_start_task`: just test is the POST method starts correctly
   - `test_start_task_duplicate_user_id`: test the response for a POST request for a duplicated user_id
   - `test_get_status_initial`: test the GET method response for a non-existent user_id
   - `test_get_status_after_start`: test the GET response for the standard status of the task

## Docker

To build and run the application using Docker:

1. **Build the Docker image:**

        docker build -t fastapi-weather-app .

2. **Run the Docker container:**

   Set the OPENWEATHER_API_KEY environment variable directly in the docker run command:

       docker run -p 8000:8000 -e OPENWEATHER_API_KEY='your_openweather_api_key' fastapi-weather-app

   Replace 'your_openweather_api_key' with your actual OpenWeather API key.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - For the powerful and intuitive web framework.
- [OpenWeather API](https://openweathermap.org/api) - For providing the weather data used in this application.
