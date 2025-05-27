import io
import imgkit

from PIL import Image
import numpy as np


class PixelColor:
    White = 0
    Black = 1


def get_pixel_color(image_pixel: np.typing.NDArray) -> PixelColor:

    # pixel_sum = sum(image_pixel[:-1]) / (255 * 3)
    if (image_pixel == [255, 255, 255, 255]).all():
        return PixelColor.White
    return PixelColor.Black


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
    img = imgkit.from_url("http://127.0.0.1:5000", False, options=options)
    img = Image.open(io.BytesIO(img))

    original_ss = np.array(img)
    black_and_white_image = np.array(img)
    buffer_black = bytearray(EPD_HEIGHT * EPD_WIDTH // 8)

    for x in range(original_ss.shape[0]):
        for y in range(original_ss.shape[1]):
            index = (x * EPD_WIDTH + y) // 8
            bit_index = (x * EPD_WIDTH + y) % 8

            if get_pixel_color(original_ss[x, y]) == PixelColor.White:
                buffer_black[index] = buffer_black[index] | 0x1 << (7 - bit_index)
                black_and_white_image[x, y] = [255, 255, 255, 255]
            else:
                buffer_black[index] = buffer_black[index] | 0x0 << (7 - bit_index)
                black_and_white_image[x, y] = [0, 0, 0, 255]

    Image.fromarray(original_ss).save("original_file.png")
    Image.fromarray(black_and_white_image).save("black_and_white_image.png")

    return buffer_black


if __name__ == "__main__":
    get_grayscale_screenshot()
