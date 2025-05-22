# Weather forecast display


### Bord

Raspberry Pi Pico W

### Display

Waveshare Pico-ePaper-7.5B 
[documentation](https://www.waveshare.com/wiki/Pico-ePaper-7.5-B)



| e-Paper | Pico/Pico2 | Description                                                         |
| :-----: | :--------: | :------------------------------------------------------------------ |
|   VCC   |    VSYS    | Power input                                                         |
|   GND   |    GND     | Ground                                                              |
|   DIN   |    GP11    | MOSI pin of SPI interface, data transmitted from the Host to Slave. |
|   CLK   |    GP10    | SCK pin of SPI interface, clock input of the Slave                  |
|   CS    |    GP9     | Chip select pin of SPI interface, Low Active                        |
|   DC    |    GP8     | Data/Command control pin (High: Data; Low: Command)                 |
|   RST   |    GP12    | Reset pin, low active                                               |
|  BUSY   |    GP13    | Busy output pin                                                     |

### Weather forecast source

Accuweather

[login](https://developer.accuweather.com/user/login?destination=user/481045/app-detail/ea2fc5b4-dad4-4855-97f5-88ceb1355dea&autologout_timeout=1)
[apis](https://developer.accuweather.com/apis)

[get city id](https://developer.accuweather.com/accuweather-locations-api/apis/get/locations/v1/cities/search)

267224 Sicienko

273875 Bydgoszcz

[get current weather conditions](https://developer.accuweather.com/accuweather-current-conditions-api/apis/get/currentconditions/v1/%7BlocationKey%7D)

[1 day forecast](https://developer.accuweather.com/accuweather-forecast-api/apis/get/forecasts/v1/daily/1day/%7BlocationKey%7D)

icons: 
https://openweathermap.org/weather-conditions


# Server

## Setup

800 x 480