import json
from pi_pico_w_server_tools.app import App, compose_response, load_html, format_dict
from machine import Pin
from config import *
import requests
from e_paper_7_5_B import EPD_7in5_B, EPD_WIDTH, EPD_HEIGHT
import framebuf
import time


class GateConfig:
    def __init__(self):
        self.path = "gate_config.json"
        data = self.__get_gate_config()

        self.remote_url: str = data["remote_url"]
        self.auto_refresh_interval_minutes: int = data["auto_refresh_interval_minutes"]
        self.location: str = data["location"]
        self.location_key: str = data["location_key"]
        self.weather_api_key: str = data["weather_api_key"]

    def update(
        self,
        remote_url,
        auto_refresh_interval_minutes,
        location,
        location_key,
        weather_api_key,
    ):
        self.remote_url = remote_url
        self.auto_refresh_interval_minutes = auto_refresh_interval_minutes
        self.location = location
        self.location_key = location_key
        self.weather_api_key = weather_api_key

    def __get_gate_config(self) -> dict:
        try:
            with open(self.path, "r") as file:
                return json.loads(file.read())
        except Exception as err:
            print(f"{self.path} file not found")
            raise Exception(f"{self.path} file not found")

    def update_config(self):
        data = {
            "remote_url": remote_url,
            "auto_refresh_interval_minutes": auto_refresh_interval_minutes,
            "location": location,
            "location_key": location_key,
            "weather_api_key": weather_api_key,
        }

        try:
            with open(self.path, "w") as file:
                file.write(json.dumps(data))
        except Exception as err:
            print(f"{self.path} file not found")
            raise Exception(f"{self.path} file not found")


def home_page(cl, params: dict):
    if params.get("load_data") is not None:
        load_weather_data()

    if params.get("save_config") is not None:

        if params.get("remote_url") is not None:
            gate_config.remote_url = params.get("remote_url")

        if params.get("weather_api_key") is not None:
            gate_config.location_key = params.get("weather_api_key")

        if params.get("location") is not None:
            gate_config.location = params.get("location")

        if params.get("auto_refresh_interval_minutes") is not None:
            gate_config.auto_refresh_interval_minutes = int(
                params.get("auto_refresh_interval_minutes")
            )
        gate_config.update_config()

    raw_html = format_dict(
        load_html("static/index.html"),
        {
            "remote_url": remote_url,
            "auto_refresh_interval_minutes": str(auto_refresh_interval_minutes),
            "location": location,
            "weather_api_key": weather_api_key,
        },
    )

    cl.sendall(compose_response(response=raw_html))


def load_weather_data() -> bool:

    response = requests.get(
        f"{remote_url}/weather_screenshot?api_key={weather_api_key}&location_key={location_key}&location={location}"
    )

    if response.status_code != 200:
        print(f"{remote_url}, connection closed")
        return False

    for i in range(len(epd.buffer_black)):
        epd.buffer_black[i] = response.content[i]

    epd.imageblack = framebuf.FrameBuffer(
        epd.buffer_black, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB
    )

    epd.display()
    return True


Pin("LED", Pin.OUT).value(1)

epd = EPD_7in5_B()
gate_config = GateConfig()
app = App(hostname="weather_station.local")

import _thread

if __name__ == "__main__":

    app.register_endpoint("/v1", home_page)
    app.register_endpoint("/v1/load_weather_data", load_weather_data)

    try:

        app.main_loop()

        # while True:
        # load_weather_data()
        # time.sleep(60 * auto_refresh_interval_minutes)

    except (KeyboardInterrupt, Exception) as ex:
        print(f"exiting: {ex}")

    Pin("LED", Pin.OUT).value(0)
