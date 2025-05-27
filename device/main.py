from app import App, load_html, format_dit
from machine import Pin
from config import *
import requests
from e_paper_7_5_B import EPD_7in5_B, EPD_WIDTH, EPD_HEIGHT
import framebuf
import time


def home_page(cl, params, named_params: dict):

    print(named_params)

    load_data = named_params.get("load_data", None)

    if load_data != None:
        load_weather_data()

    raw_html = format_dit(
        load_html("index.html"),
        {
            "remote_url": remote_url,
            "auto_refresh_interval_minutes": str(auto_refresh_interval_minutes),
            "location": location,
            "weather_api_key": weather_api_key,
        },
    )

    cl.send(raw_html)


def load_weather_data():

    response = requests.get(
        f"{remote_url}/weather_screenshot?api_key={weather_api_key}&location_key={location_key}&location={location}"
    )
    for i in range(len(epd.buffer_black)):
        epd.buffer_black[i] = response.content[i]

    epd.imageblack = framebuf.FrameBuffer(
        epd.buffer_black, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB
    )
    epd.display()


Pin("LED", Pin.OUT).value(1)
epd = EPD_7in5_B()
import _thread

if __name__ == "__main__":
    app = App()
    app.register_endpoint("/", home_page)
    app.register_endpoint("/load_weather_data", load_weather_data)

    try:

        _thread.start_new_thread(app.main_loop, ())

        while True:
            load_weather_data()
            time.sleep(60 * auto_refresh_interval_minutes)
            
    except (KeyboardInterrupt, Exception) as ex:
        print("safe exiting")

    Pin("LED", Pin.OUT).value(0)
