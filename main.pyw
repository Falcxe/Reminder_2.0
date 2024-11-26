import serial
import time
import requests
import subprocess
import psutil
from datetime import datetime

# Настройки
arduino_port = 'COM6'  # Замените на ваш порт
baud_rate = 9600
api_key = "a693dba8e0d34842a2b110534240511"  # Замените на ваш API-ключ OpenWeatherMap
city_name = "moscow"  # Ваш город
steam_path = "C:\\Program Files (x86)\\Steam\\steam.exe"  # Путь к Steam

# Подключение к Arduino
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
time.sleep(2)  # Пауза для инициализации

# Переменные слайдов и отслеживания
slide_index = 0
slides = ["DATETIME", "WEATHER"]  # Убрали "SYSTEM_LOAD"


def center_text(text, width=16):
    """Функция для центрирования текста."""
    spaces = (width - len(text)) // 2
    return ' ' * spaces + text


def get_weather():
    base_url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city_name}&aqi=no"
    for attempt in range(3):  # Попытки сделать запрос три раза
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()
            weather_data = response.json()
            if "current" in weather_data:
                temperature = weather_data["current"]["temp_c"]
                weather_message = f"{city_name.capitalize()}: {temperature}C"
                return center_text(weather_message)
        except requests.RequestException as e:
            print(f"Ошибка запроса: {e}")
            time.sleep(2)  # Подождите 2 секунды перед следующей попыткой
    return center_text("Weather data error")


def send_to_arduino(command):
    """Отправляет команду на Arduino."""
    print(f"Sending to Arduino: {command}")  # Добавим вывод перед отправкой
    ser.write((command + '\n').encode())


def update_display():
    """Обновляет текущий слайд на экране."""
    if slides[slide_index] == "DATETIME":
        current_time = center_text(datetime.now().strftime("%H:%M:%S"))
        current_date = center_text(datetime.now().strftime("%d-%m-%Y"))
        send_to_arduino(f"LCD:{current_time}|{current_date}")
    elif slides[slide_index] == "WEATHER":
        weather_info = get_weather()
        send_to_arduino("LCD:" + weather_info)


def open_program(command):
    """Открывает программу без ожидания завершения."""
    subprocess.Popen(command, shell=True)


def open_steam():
    """Открывает Steam, если он ещё не запущен."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'steam.exe':
            print("Steam уже запущен.")
            return
    print("Запускаю Steam...")
    subprocess.Popen(f'"{steam_path}"', shell=True)


def check_buttons():
    """Обрабатывает нажатия кнопок с Arduino."""
    global slide_index
    if ser.in_waiting > 0:
        message = ser.readline().decode().strip()
        print(f"Received from Arduino: {message}")

        if message == "BUTTON1":  # Переключение слайдов
            slide_index = (slide_index + 1) % len(slides)
            update_display()

        elif message == "BUTTON2":  # Запуск Steam
            open_steam()

        elif message == "BUTTON3":  # Запуск Telegram
            open_program(
                "C:\\Users\\mxms1\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe")  # Замените путь на путь к Telegram

        elif message == "BUTTON4":  # Открытие YouTube
            open_program("start https://www.youtube.com")  # Открывает YouTube в браузере

        elif message == "BUTTON5":  # Действие для новой кнопки
            open_program("C:/Path/To/YourAnotherApp.exe")  # Замените путь на путь к другому приложению


try:
    while True:
        check_buttons()
        update_display()
        time.sleep(0.5)  # Увеличьте время ожидания для снижения нагрузки
except KeyboardInterrupt:
    print("Программа остановлена.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
finally:
    ser.close()
