from pi_pico_w_server_tools.app import App, compose_response, load_html, format_dict
from machine import Pin
from config import *
import requests
from e_paper_7_5_B import EPD_7in5_B, EPD_WIDTH, EPD_HEIGHT
import framebuf
import time


def home_page(cl, params: dict):

    print(params)

    load_data = params.get("load_data", None)

    if load_data != None:
        load_weather_data()

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
import _thread

if __name__ == "__main__":

    app = App(hostname="weather_station.local")
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
