# # save this as app.py
import io
import requests
from flask import Flask, render_template, jsonify, send_file

from e_ink_screen_tools import get_grayscale_screenshot

app = Flask(__name__)

# #TODO add sql db for users and login



@app.route("/")
def index():
    return render_template("weather_page.html")


@app.route("/w")
def get_weather_screenshot():
    data = io.BytesIO(get_grayscale_screenshot())
    print(data.getbuffer().nbytes)
    return send_file(
        data,
        mimetype="application/x-binary",
        download_name="weather_forecast_location_time",
        # as_attachment=True,
    )


