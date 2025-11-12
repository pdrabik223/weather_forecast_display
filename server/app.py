# # save this as app.py
import datetime
import io
from flask import Flask, json, render_template, request, send_file

from e_ink_screen_tools import get_grayscale_screenshot
from accu_weather import (
    OneDayPrediction,
    get_locations,
    get_one_day_forecast,
    get_one_day_hourly_forecast,
)

app = Flask(__name__)


months_polish = [
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "października",
    "listopada",
    "grudnia",
]

days_polish = [
    "poniedziałek",
    "wtorek",
    "środa",
    "czwartek",
    "piątek",
    "sobota",
    "niedziela",
]


icons_path = "static/"


def get_icon(icon_id) -> str:

    icons = {
        1: "icons8-sun-96.png",  # clear sky
        2: "icons8-partly-cloudy-day-96.png",  # few clouds
        3: "icons8-cloud-96.png",  # scattered clouds
        4: "icons8-cloud-96.png",  # broken clouds
        5: "icons8-rain-96.png",  # shower rain
        6: "icons8-wet-96.png",  # rain
        7: "icons8-cloud-lightning-96.png",  # thunderstorm
        8: "icons8-winter-96.png",  # snow
    }

    try:
        return icons_path + icons[icon_id]
    except KeyError as err:
        return icons_path + "icons8-cloud-96.png"


def get_headline(location: str) -> str:
    now = datetime.datetime.now()

    month = months_polish[now.month - 1]

    day = days_polish[datetime.datetime.today().weekday()]

    return f"{day} {now.day} {month} {location}"


def get_day_prediction(location_key: int, api_key: str) -> dict:
    one_day_prediction: OneDayPrediction = get_one_day_forecast(location_key, api_key)

    if one_day_prediction == None:
        return None

    da_fuck_f_string_1 = round(one_day_prediction["min_temperature"])
    da_fuck_f_string_2 = round(one_day_prediction["max_temperature"])

    return {
        "temp_min": f"Min: {da_fuck_f_string_1}°C",
        "temp_max": f"Max: {da_fuck_f_string_2}°C",
        "precipitation": "Wilgotność: 30%",
        "day_icon": get_icon(one_day_prediction["day_icon"]),
    }


def get_hourly_prediction(location_key: int, api_key: str) -> dict:
    pred_dict = {}
    no_weather_boxes = 8
    now = datetime.datetime.now()

    hourly_predictions = get_one_day_hourly_forecast(location_key, api_key)

    if hourly_predictions == None:
        return None

    for i in range(no_weather_boxes):
        print(i, hourly_predictions[i]["weather_icon"])
        pred_dict.update(
            {
                f"hour_{i}": f"{now.hour + i}:00",
                f"pred_icon_{i}": get_icon(hourly_predictions[i]["weather_icon"]),
                f"hour_temp_{i}": str(round(hourly_predictions[i]["temperature"]))
                + "°",
                f"precipitation_probability_{i}": str(
                    round(hourly_predictions[i]["precipitation_probability"])
                )
                + "%",
            }
        )
    return pred_dict


@app.route("/v1/status")
def status():
    return {"status": "ok"}, 200


@app.route("/v1/")
def index():

    api_key = request.args.get("api_key", default=None)
    location_key = request.args.get("location_key", default=None)
    location = request.args.get("location", default=None)

    location_key = int(location_key)

    if api_key == None or location_key == None or location == None:
        return {}, 500

    day = get_day_prediction(location_key, api_key)
    hour = get_hourly_prediction(location_key, api_key)

    if day == None or hour == None:
        return render_template(
            "error_page.html",
            description="Błąd pobierania danych",
        )

    return render_template(
        "weather_page.html",
        headline=get_headline(location),
        **day,
        **hour,
    )


@app.route("/v1/weather_screenshot")
def get_weather_screenshot():

    api_key = request.args.get("api_key", default=None)
    location_key = request.args.get("location_key", default=None)
    location = request.args.get("location", default=None)

    if api_key is None or location_key is None or location is None:
        return {}, 400
    try:
        if type(location_key) is str:
            location_key = int(location_key)
    except Exception as ex:
        print("incorrect location_key")
        return {}, 400

    url = "http://192.168.0.108:5000/v1/"
    url = f"{url}?api_key={api_key}&location_key={location_key}&location={location}"

    try:
        data = io.BytesIO(get_grayscale_screenshot(url))
    except Exception as ex:
        pass

    return send_file(
        data,
        mimetype="application/x-binary",
        download_name="weather_forecast_location_time",
    )


@app.route("/v1/location")
def get_location():

    api_key = request.args.get("api_key", default=None)
    location = request.args.get("location", default=None)

    if api_key is None or location is None:
        print(api_key)
        print(location)
        return {}, 400

    location = (
        location.encode("latin-1")
        .decode("unicode_escape")
        .encode("latin-1")
        .decode("utf-8")
    )

    try:
        locations = get_locations(location, api_key)

        if locations is None:
            return {}, 500

    except Exception as ex:
        print(str(ex))
        pass

    return json.dumps(locations), 200
