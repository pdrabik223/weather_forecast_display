import io
import imgkit

from PIL import Image
import numpy as np
import os


# returns 800 x 480 bytearray
def get_grayscale_screenshot() -> bytearray:
    EPD_WIDTH = 800
    EPD_HEIGHT = 480

    options = {
        "format": "png",
        "height": str(EPD_HEIGHT),
        "width": str(EPD_WIDTH),
        "crop-h": str(EPD_HEIGHT),
        "crop-w": str(EPD_WIDTH),
        "encoding": "UTF-8",
        "quiet": "",
        "enable-javascript": "",
        "quality": str(100),
        "javascript-delay": str(800),
        "enable-local-file-access": "",
    }
    # temp_image_path = "temp.jpg"
    img = imgkit.from_file("templates/weather_page.html", False, options=options)
    img = Image.open(io.BytesIO(img))
    original_ss = np.array(img)
    img.save("original_file.png")
    print(original_ss.shape)

    for x in range(original_ss.shape[0]):
        for y in range(original_ss.shape[1]):
            if (original_ss[x, y] == [255, 255, 255, 255]).all():
                original_ss[x, y] = [255, 255, 255, 255]
            else:
                original_ss[x, y] = [0, 0, 0, 255]

    img = Image.fromarray(original_ss)
    img.save("b_w_file.png")

    buffer_black = bytearray(EPD_HEIGHT * EPD_WIDTH // 8)

    for x in range(original_ss.shape[0]):
        for y in range(original_ss.shape[1]):
            index = (x * EPD_WIDTH + y) // 8
            bit_index = (x * EPD_WIDTH + y) % 8

            if (original_ss[x, y] == [255, 255, 255, 255]).all():
                buffer_black[index] = buffer_black[index] | 0x1 << (7 - bit_index)
            else:
                buffer_black[index] = buffer_black[index] | 0x0 << (7 - bit_index)

    return buffer_black


if __name__ == "__main__":
    get_grayscale_screenshot()
