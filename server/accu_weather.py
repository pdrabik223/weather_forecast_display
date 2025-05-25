import requests
from typing import Any, TypedDict


class Location(TypedDict):
    name: str
    key: int
    parent_city: str | None
    supplemental_admin_area: list[str] | None


class Weather(TypedDict):
    epoch_time: int
    weather_icon: int

    # is there something falling from the sky
    has_precipitation: bool
    # the type of precipitation will be returned.
    # Possible values are Rain, Snow, Ice, or Mixed.
    # Null in the absence of precipitation.
    precipitation_type: str | None
    temperature: float
    precipitation_intensity: str | None


class OneDayPrediction(TypedDict):
    epoch_time: int
    headline_category: str
    headline_text: str

    min_temperature: float
    max_temperature: float

    day_icon: int
    day_has_precipitation: bool
    day_precipitation_type: str | None
    day_precipitation_intensity: str | None

    night_icon: int
    night_has_precipitation: bool
    night_precipitation_type: str | None
    night_precipitation_intensity: str | None


class HourlyPrediction(TypedDict):
    epoch_time: int
    weather_icon: int

    # is there something falling from the sky
    has_precipitation: bool
    # the type of precipitation will be returned.
    # Possible values are Rain, Snow, Ice, or Mixed.
    # Null in the absence of precipitation.
    # precipitation_type: str | None
    temperature: float
    precipitation_probability: int


def get_param(function) -> Any | None:
    try:
        return function()
    except KeyError as err:
        return None


def get_locations(city: str | int, api_key: str) -> None | list[Location]:
    response: list[Location] = []
    r = requests.get(
        "http://dataservice.accuweather.com/locations/v1/cities/search",
        params={"apikey": api_key, "q": city},
    )

    if r.status_code != 200:
        return None

    for resp in r.json():
        response.append(
            {
                "name": resp["LocalizedName"],
                "key": resp["Key"],
                "parent_city": get_param(lambda: resp["ParentCity"]["LocalizedName"]),
                "supplemental_admin_areas": [
                    get_param(lambda: i["LocalizedName"])
                    for i in resp["SupplementalAdminAreas"]
                ],
            }
        )
    return response


def get_current_conditions(location_key: int, api_key: str) -> Weather | None:

    r = requests.get(
        f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}",
        params={"apikey": api_key},
    )

    if r.status_code != 200:
        return None

    resp = r.json()[0]

    return {
        "epoch_time": resp["EpochTime"],
        "temperature": resp["Temperature"]["Metric"]["Value"],
        "has_precipitation": resp["HasPrecipitation"],
        "precipitation_type": resp["PrecipitationType"],
        "weather_icon": resp["WeatherIcon"],
    }


def get_one_day_forecast(location_key: int, api_key: str) -> OneDayPrediction | None:
    r = requests.get(
        f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}",
        params={"apikey": api_key, "metric": True},
    )

    if r.status_code != 200:
        return None

    resp = r.json()

    return {
        "epoch_time": resp["Headline"]["EffectiveEpochDate"],
        "headline_category": resp["Headline"]["Category"],
        "headline_text": resp["Headline"]["Text"],
        "min_temperature": resp["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"],
        "max_temperature": resp["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"],
        "day_icon": resp["DailyForecasts"][0]["Day"]["Icon"],
        "day_has_precipitation": resp["DailyForecasts"][0]["Day"]["HasPrecipitation"],
        "day_precipitation_type": get_param(
            lambda: resp["DailyForecasts"][0]["Day"]["PrecipitationType"]
        ),
        "day_precipitation_intensity": get_param(
            lambda: resp["DailyForecasts"][0]["Day"]["PrecipitationIntensity"]
        ),
        "night_icon": resp["DailyForecasts"][0]["Night"]["Icon"],
        "night_has_precipitation": resp["DailyForecasts"][0]["Night"][
            "HasPrecipitation"
        ],
        "night_precipitation_intensity": get_param(
            lambda: resp["DailyForecasts"][0]["Night"]["PrecipitationType"]
        ),
        "night_precipitation_intensity": get_param(
            lambda: resp["DailyForecasts"][0]["Night"]["PrecipitationIntensity"]
        ),
    }


def get_one_day_hourly_forecast(location_key: int, api_key: str):
    r = requests.get(
        f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}",
        params={"apikey": api_key},
    )

    if r.status_code != 200:
        return None

    resp = r.json()
    response: list[HourlyPrediction] = []

    for day in resp:
        response.append(
            {
                "epoch_time": day["EpochDateTime"],
                "temperature": day["Temperature"]["Value"],
                "weather_icon": day["WeatherIcon"],
                "has_precipitation": day["HasPrecipitation"],
                "precipitation_probability": day["PrecipitationProbability"],
            }
        )
    return response


if __name__ == "__main__":
    # print(get_locations(API_KEY, CITY))
    # print(get_current_conditions(274340, API_KEY))
    print(get_one_day_forecast(274340, API_KEY))
    # print(get_one_day_hourly_forecast(274340, API_KEY))
