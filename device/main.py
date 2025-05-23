from app import App, load_html, format_dit
from machine import Pin
from config import *
import requests
from e_paper_7_5_B import EPD_7in5_B, EPD_WIDTH, EPD_HEIGHT
import framebuf


def home_page(cl, params, named_params: dict):

    print(named_params)

    load_data = named_params.get("load_data", None)

    if load_data != None:
        load_weather_data()

    # weather_api_key = str(named_params.get("weather_api_key")) or weather_api_key
    # location = str(named_params.get("location")) or location
    # remote_url = str(named_params.get("remote_url")) or remote_url
    # auto_refresh_interval_minutes = (
    #     int(named_params.get("auto_refresh_interval_minutes"))
    #     or auto_refresh_interval_minutes
    # )

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

    print("loading new data")
    response = requests.get("http://192.168.0.101:5000/w")

    for i in range(len(epd.buffer_black)):
        epd.buffer_black[i] = response.content[i]

    epd.imageblack = framebuf.FrameBuffer(
        epd.buffer_black, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB
    )
    epd.display()


Pin("LED", Pin.OUT).value(1)
epd = EPD_7in5_B()

if __name__ == "__main__":
    app = App()
    app.register_endpoint("/", home_page)
    app.register_endpoint("/load_weather_data", load_weather_data)

    load_weather_data()

    try:
        app.main_loop()
    except (KeyboardInterrupt, Exception) as ex:
        print("safe exiting")

    Pin("LED", Pin.OUT).value(0)
