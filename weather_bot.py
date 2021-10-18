import requests
from config import tg_bot_token, open_weather_token, timezone_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from geopy.geocoders import Nominatim

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)
geolocator = Nominatim(user_agent="Weather_Bot")


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    # Клавиатура с кнопкой запроса локации
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(button_geo)
    await message.answer("Поделиться местоположением", reply_markup=keyboard)


# Получение и обработка геолокации
@dp.message_handler(content_types=['location'])
async def location(message):
    loc = geolocator.reverse('{} {}'.format(message.location.latitude, message.location.longitude), language="en")
    city = loc.raw["address"]["city"]
    await get_weather(message, city)


# Получение и обработка текстовых сообщений
@dp.message_handler()
async def location(message: types.Message):
    city = message.text
    await get_weather(message, city)


@dp.message_handler()
async def get_weather(message, city):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U0001F327",
        "Drizzle": "Морось \U0001F326",
        "Thunderstorm": "Гроза \U0001F329",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    def weather_description(description):
        if description in code_to_smile:
            return code_to_smile[description]
        else:
            return "Посмотри в окно, не пойму, что там за погода!"

    def degToCompass(deg):
        val = int((deg / 22.5) + .5)
        arr = ["С", "ССВ", "СВ", "ВСВ", "В", "ВЮВ", "ЮВ", "ЮЮВ", "Ю", "ЮЮЗ", "ЮЗ", "ЗЮЗ", "З", "ЗСЗ", "СЗ",
               "ССЗ"]
        return arr[(val % 16)]

    def wind_gust(str_length):
        if str_length == 3:
            return f", порывы до {data['wind']['gust']} м/c"
        else:
            return ""

    def get_time(lat, lon):
        url = f'https://api.ipgeolocation.io/timezone?apiKey={timezone_token}&lat={lat}&long={lon}'
        req = requests.get(url)
        time_data = req.json()
        dt = time_data['date_time']
        return dt

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        date_time = get_time(data['coord']['lat'], data['coord']['lon'])
        city = data['name']
        weather = weather_description(data["weather"][0]["main"])
        temp = data['main']['temp']
        temp_feels_like = data['main']['feels_like']
        wind = data['wind']['speed']
        wind_gust = wind_gust(len(data['wind']))
        wind_direction = degToCompass(int(data['wind']['deg']))
        humidity = data['main']['humidity']
        pressure = int(data['main']['pressure']) * 0.75  # hPa converting

        await message.answer(
            f"В {city} сейчас:\n"
            f"{date_time}\n"
            f"Температура: {temp}°C {weather}\nПо ощущению: {temp_feels_like}°C\n"
            f"Ветер: {wind_direction} {wind} м/c{wind_gust}\nВлажность: {humidity}%\nДавление: {pressure} мм.рт.ст."
        )

    except:
        await message.reply("\U00002620 Проверьте название города \U00002620")


if __name__ == "__main__":
    executor.start_polling(dp)
