import json
from pi_pico_w_server_tools.wifi_tools import check_connection
from pi_pico_w_server_tools.app import App, compose_response, load_html, format_dict
from machine import Pin
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

    def get_dict(self, obscure_weather_api_key: bool = False):
        return {
            "remote_url": self.remote_url,
            "auto_refresh_interval_minutes": self.auto_refresh_interval_minutes,
            "location": self.location,
            "location_key": self.location_key,
            "weather_api_key": (
                obscure_api_key(self.weather_api_key)
                if obscure_weather_api_key
                else self.weather_api_key
            ),
        }

    def update_config(self):
        data = self.get_dict()

        config: dict[str, str] = self.__get_gate_config()

        write_settings_to_file = False

        for key in config:
            try:
                if data[key] != config[key]:
                    write_settings_to_file = True
                    break
            except KeyError as err:
                write_settings_to_file = True
                break

        if not write_settings_to_file:
            print("config file is already up to date")
            return

        print("saving config to file")
        try:
            with open(self.path, "w") as file:
                file.write(json.dumps(data))
                file.flush()

        except Exception:
            print(f"{self.path} file not found")
            raise Exception(f"{self.path} file not found")


def obscure_api_key(key: str) -> str:

    return "".join(["•" for _ in range(len(key) - 5)]) + key[-5:]


def home_page(cl, params: dict):

    cl.sendall(compose_response(response=load_html("static/index.html")))


def update_local_config(cl, params: dict) -> bool:

    if params.get("remote_url") is not None:
        gate_config.remote_url = params.get("remote_url")

    if params.get("weather_api_key") is not None:
        key = str(params.get("weather_api_key"))
        if "•" not in key:
            gate_config.weather_api_key = key

    if params.get("location") is not None:
        gate_config.location = params.get("location")

    if params.get("auto_refresh_interval_minutes") is not None:
        gate_config.auto_refresh_interval_minutes = int(
            params.get("auto_refresh_interval_minutes")
        )

    gate_config.update_config()

    cl.sendall(compose_response())


def get_local_config(cl, params: dict) -> bool:
    data = gate_config.get_dict(True)

    data["has_access_to_internet"] = check_connection()
    data["has_access_to_server"] = check_connection(gate_config.remote_url)

    cl.sendall(compose_response(response=json.dumps(data)))


def search_for_location_data(cl, params: dict):
    print(params)
    cl.sendall(compose_response())


def load_weather_data() -> bool:

    try:
        response = requests.get(
            f"{gate_config.remote_url}/weather_screenshot?api_key={gate_config.weather_api_key}&location_key={gate_config.location_key}&location={gate_config.location}",
            timeout=5,
        )
    except Exception as ex:
        print(str(ex))
        return False

    if response.status_code != 200:
        print(f"{gate_config.remote_url}, connection closed")
        return False

    for i in range(len(epd.buffer_black)):
        epd.buffer_black[i] = response.content[i]

    epd.imageblack = framebuf.FrameBuffer(
        epd.buffer_black, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB
    )

    epd.display()
    return True


def load_weather_data_endpoint(cl, params: dict):
    if load_weather_data():
        cl.sendall(compose_response())
    else:
        cl.sendall(compose_response(500, "Failed to load new weather data"))


epd = EPD_7in5_B()
gate_config = GateConfig()
app = App(hostname="weather_station.local")


import _thread

if __name__ == "__main__":

    app.register_endpoint("/v1", home_page)
    app.register_endpoint("/v1/load_weather_data", load_weather_data_endpoint)
    app.register_endpoint("/v1/get_config", get_local_config)
    app.register_endpoint("/v1/set_config", update_local_config)
    app.register_endpoint("/v1/search_for_location", search_for_location_data)

    Pin("LED", Pin.OUT).value(1)

    try:

        app.main_loop()

        # while True:
        #     load_weather_data()
        #     time.sleep(60 * auto_refresh_interval_minutes)

    except (KeyboardInterrupt, Exception) as ex:
        print(f"exiting: {ex}")

    Pin("LED", Pin.OUT).value(0)
