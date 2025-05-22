# # save this as app.py
from flask import Flask, render_template, jsonify

from e_ink_screen_tools import get_grayscale_screenshot

app = Flask(__name__)

# #TODO add sql db for users and login


API_KEY = "your_openweathermap_api_key"
CITY = "London"


@app.route("/")
def index():
    return render_template("weather_page.html")


@app.route("/weather")
def weather():

    weather_info = {
        "city": "rest",
        "data": {
            "year": 2025,
            "month": "czerwiec",
            "day": 4,
            "day_of_the_week": "czwartek",
        },
        "min_temp": "10",
        "max_temp": "30",
        "current_temp": 10,
        "current_temp_felt": 10,
        "current_icon": 2,
        "current_rainfall_percentage": 10,
        "temperature_for_next_12h": {
            "7": {
                "temp": 30,
                "Icon": 2,
                "felt_temp": 30,
                "rainfall": 30,
            },
            "8": {
                "temp": 29,
                "Icon": 2,
                "felt_temp": 29,
                "rainfall": 20,
            },
            "9": {
                "temp": 25,
                "Icon": 2,
                "felt_temp": 25,
                "rainfall": 10,
            },
            "10": {
                "temp": 20,
                "Icon": 2,
                "felt_temp": 20,
                "rainfall": 50,
            },
            "11": {
                "temp": 25,
                "Icon": 2,
                "felt_temp": 25,
                "rainfall": 60,
            },
            "12": {
                "temp": 28,
                "Icon": 2,
                "felt_temp": 28,
                "rainfall": 30,
            },
            "13": {
                "temp": 30,
                "Icon": 2,
                "felt_temp": 30,
                "rainfall": 50,
            },
            "14": {
                "temp": 29,
                "Icon": 2,
                "felt_temp": 29,
                "rainfall": 60,
            },
            "15": {
                "temp": 25,
                "Icon": 2,
                "felt_temp": 25,
                "rainfall": 30,
            },
            "16": {
                "temp": 20,
                "Icon": 2,
                "felt_temp": 20,
                "rainfall": 30,
            },
            "17": {
                "temp": 25,
                "Icon": 2,
                "felt_temp": 25,
                "rainfall": 50,
            },
            "18": {
                "temp": 28,
                "Icon": 2,
                "felt_temp": 28,
                "rainfall": 60,
            },
        },
    }
    return jsonify(weather_info)


@app.route("/w")
def get_weather_screenshot():
    return str(
        get_grayscale_screenshot(
            "https://www.w3schools.com/python/python_file_remove.asp"
        )
    )
