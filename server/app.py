# # save this as app.py
from flask import Flask

app = Flask(__name__)


import imgkit
from PIL import Image
import numpy as np
import os

# #TODO add sql db for users and login


@app.route("/")
def hello():
    return "Weather look"


@app.route("/w")    
def get_weather_screenshot():
    return get_grayscale_screenshot(
        "https://www.w3schools.com/python/python_file_remove.asp"
    )


# returns 800 x 480 bytearray
def get_grayscale_screenshot(url: str) -> bytearray:
    EPD_WIDTH = 800
    EPD_HEIGHT = 480

    options = {
        "format": "png",
        "crop-h": str(EPD_HEIGHT),
        "crop-w": str(EPD_WIDTH),
        # "crop-x": "3",
        # "crop-y": "3",
        "encoding": "UTF-8",
    }
    temp_image_path = "temp.jpg"
    imgkit.from_url(url, temp_image_path, options=options)
    img = Image.open(temp_image_path)
    original_ss = np.array(img)
    buffer_black = bytearray(EPD_HEIGHT * EPD_WIDTH // 8)

    for x in range(original_ss.shape[0]):
        for y in range(original_ss.shape[1]):
            index = (x * EPD_WIDTH + y) // 8
            bit_index = (x * EPD_WIDTH + y) % 8

            if (original_ss[x, y] == [255, 255, 255, 255]).all():
                buffer_black[index] = buffer_black[index] | 0x1 << bit_index
            else:
                buffer_black[index] = buffer_black[index] & 0x0 << bit_index

    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)

    return buffer_black
    