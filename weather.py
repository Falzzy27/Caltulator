import tkinter as tk
import requests
from PIL import Image, ImageTk
from itertools import count, cycle


# --- Константы ---
day = "1 день"
days = "3 дня"
is_hourly_visible = False
cached_forecast = None
cached_city = None
ip_token = '26f8959fa50541'
weather_token = "0e0d04f2f8974df8d4d2fad884daf679"

# --- Получение города по IP ---
def get_city_by_ip():
    try:
        response = requests.get(f"https://ipinfo.io/json?token={ip_token}")
        data = response.json()
        return data.get('city', '') if data is not None else "F"
    except requests.exceptions.RequestException as e:
        print(f"Ошибка получения местоположения: {e}")
        return None

# --- Получение данных о погоде ---
def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?APPID={weather_token}&lang=ru&q={city}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("cod") != "200":
        return "not_found"

    # Почасовой прогноз на 1 день (8 записей)
    hourly_forecast = []
    for item in data['list'][:8]:
        dt_txt = item['dt_txt'][11:16]
        temp = round(item['main']['temp'] - 273.15)
        icon = item['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon}.png"
        icon_path = f"{icon}.png"
        with open(icon_path, "wb") as f:
            f.write(requests.get(icon_url).content)
        hourly_forecast.append((dt_txt, temp, icon_path))

    # Прогноз на 3 дня
    daily_data = {}
    for item in data['list']:
        date = item['dt_txt'][:10]
        temp = round(item['main']['temp'] - 273.15)
        status = item['weather'][0]['description']
        if date not in daily_data:
            daily_data[date] = []
        daily_data[date].append((temp, status))

    daily_forecast = []
    for date, values in list(daily_data.items())[:3]:
        avg_temp = round(sum(t for t, _ in values) / len(values))
        common_status = values[0][1]
        daily_forecast.append((common_status, avg_temp))

    return hourly_forecast, daily_forecast


# --- Плавное появление иконки ---
def fade_in_icon(label, img, steps=30, delay=20):
    def step(alpha):
        img_resized = img.resize((32 + alpha // 2, 32 + alpha // 2), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img_resized)
        label.configure(image=photo)
        label.image = photo
        if alpha < steps:
            label.after(delay, lambda: step(alpha + 1))

    step(0)


# --- Проверка на погодные предупреждения ---
def check_weather_warning(result):
    weather_warning_label.config(text="")
    hourly_forecast, daily_forecast = result

    # Проверка на экстремальные температуры
    temperatures = [temp for _, temp, _ in hourly_forecast]
    min_temp = min(temperatures)
    max_temp = max(temperatures)

    if max_temp > 35:
        weather_warning_label.config(text="Внимание: Ожидается сильная жара! Берегитесь перегрева.", fg="#D64B29")
    elif min_temp < -10:
        weather_warning_label.config(text="Внимание: Очень холодная погода. Оденьтесь тепло.", fg="#005F73")
    else:
        weather_warning_label.config(text="Погода стабильная и комфортная.", fg="#2F6A72")

    # Проверка на осадки или неблагоприятные погодные условия
    for status, _ in daily_forecast:
        if "дождь" in status or "снег" in status:
            weather_warning_label.config(text="Внимание: Ожидаются осадки. Не забудьте зонт!", fg="#F2A007")

# --- UI и отображение ---
def show_weather(city):
    global cached_city, cached_forecast

    clear_frame()
    result = get_weather_data(city)
    if result == "not_found":
        show_error('Город не найден!')
    else:
        cached_city = city
        cached_forecast = result
        check_weather_warning(result)  # Добавляем проверку на предупреждения
        show_hourly_and_daily_forecast(city, *result)


# --- Отображение прогноза ---
def show_hourly_and_daily_forecast(city, hourly, daily):
    bg_color = DARK_BG if is_dark_theme else LIGHT_BG
    text_color = DARK_TEXT_COLOR if is_dark_theme else LIGHT_TEXT_COLOR

    title = tk.Label(frame, text=f"Погода по часам: {city}", font=('Arial', 14, 'bold'), bg=bg_color, fg=text_color)
    title.grid(row=1, column=0, pady=(10, 10), columnspan=8)

    row = tk.Frame(frame, bg=bg_color)
    row.grid(row=2, column=0, columnspan=8, pady=(5, 10))

    # Настройка веса колонок для центрирования
    for i in range(8):
        row.grid_columnconfigure(i, weight=1, uniform="equal")

    for i, (time, temp, icon_path) in enumerate(hourly):
        column = tk.Frame(row, bg=bg_color)
        column.grid(row=0, column=i, padx=10, sticky="nsew")

        tk.Label(column, text=time, font=('Arial', 10), bg=bg_color, fg=text_color).grid(row=0, column=0)

        img = Image.open(icon_path).resize((32, 32), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        label_img = tk.Label(column, image=photo, bg=bg_color)
        label_img.image = photo
        label_img.grid(row=1, column=0)

        fade_in_icon(label_img, img)  # Плавное появление иконки

        tk.Label(column, text=f"{temp}°C", font=('Arial', 10), bg=bg_color, fg=text_color).grid(row=2, column=0)

    # Местоположение для прогноза на 3 дня
    daily_title = tk.Label(frame, text=f"Прогноз на 3 дня:", font=('Arial', 14, 'bold'), bg=bg_color, fg=text_color)
    daily_title.grid(row=3, column=0, pady=(20, 5), columnspan=8)

    for i, (status, temp) in enumerate(daily):
        tk.Label(frame, text=f"День {i+1}: {status}, {temp}°C", font=('Arial', 12), bg=bg_color, fg=text_color).grid(row=4 + i, column=0, pady=5)


# --- Вспомогательные функции ---
def clear_frame():
    error_label.config(text="")
    for widget in frame.winfo_children():
        widget.destroy()

def show_error(message):
    error_label.config(text=message, fg=DARK_ERROR_COLOR if is_dark_theme else LIGHT_ERROR_COLOR)

def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    root.configure(bg=DARK_BG if is_dark_theme else LIGHT_BG)
    city_label.configure(bg=root['bg'], fg=DARK_TEXT_COLOR if is_dark_theme else LIGHT_TEXT_COLOR)
    city_entry.configure(bg=DARK_PRIMARY_COLOR if is_dark_theme else LIGHT_PRIMARY_COLOR,
                         fg=DARK_SECONDARY_COLOR if is_dark_theme else LIGHT_SECONDARY_COLOR)
    error_label.configure(bg=root['bg'])
    frame.configure(bg=root['bg'])
    theme_button.configure(bg=DARK_PRIMARY_COLOR if is_dark_theme else LIGHT_PRIMARY_COLOR,
                           fg=DARK_SECONDARY_COLOR if is_dark_theme else LIGHT_SECONDARY_COLOR)
    if cached_forecast and cached_city:
        clear_frame()
        show_hourly_and_daily_forecast(cached_city, *cached_forecast)

# --- Цветовые схемы ---
LIGHT_BG = '#F0F4F8'  # Светлый, мягкий фон
LIGHT_PRIMARY_COLOR = "#76B041"  # Мягкий зеленый
LIGHT_SECONDARY_COLOR = "#FFFFFF"
LIGHT_ERROR_COLOR = "#F28D8C"
LIGHT_TEXT_COLOR = "#2F4F4F"  # Тёмный, но не слишком яркий текст

DARK_BG = '#2C3E50'  # Темный фон
DARK_PRIMARY_COLOR = "#3498DB"  # Яркий синий
DARK_SECONDARY_COLOR = "#ECF0F1"
DARK_ERROR_COLOR = "#E74C3C"
DARK_TEXT_COLOR = "#ECF0F1"  # Светлый текст для темной темы

is_dark_theme = False

# --- Интерфейс ---
root = tk.Tk()
root.geometry("800x800+450+100")
root.title("Погода")
root.configure(bg=LIGHT_BG)
root.resizable(True, True)  # Делаем окно ресайзируемым

city_label = tk.Label(root, text="Город:", font=('Arial', 14), bg=LIGHT_BG, fg=LIGHT_TEXT_COLOR)
city_label.grid(row=0, column=0, pady=20, padx=20, sticky=tk.W)

city_entry = tk.Entry(root, width=25, font=('Arial', 14), bg=LIGHT_PRIMARY_COLOR, fg=LIGHT_SECONDARY_COLOR, borderwidth=2, relief='solid')
city_entry.grid(row=0, column=1, pady=20, padx=20)

default_city = get_city_by_ip()
if default_city:
    city_label.config(text=f"Город: {default_city}")
    city_entry.insert(0, default_city)

# Кнопка обновления прогноза
refresh_button = tk.Button(root, text="Обновить прогноз", command=lambda: show_weather(city_entry.get()), bg=LIGHT_PRIMARY_COLOR, fg=LIGHT_SECONDARY_COLOR)
refresh_button.grid(row=1, column=0, pady=10, padx=20)

# Смена темы
theme_button = tk.Button(root, text="Сменить тему", command=toggle_theme, bg=LIGHT_PRIMARY_COLOR, fg=LIGHT_SECONDARY_COLOR)
theme_button.grid(row=1, column=1, pady=10)

# Метка для ошибок
error_label = tk.Label(root, text="", font=('Arial', 12), bg=LIGHT_BG, fg=LIGHT_ERROR_COLOR)
error_label.grid(row=2, column=0, columnspan=4)

# Метка для предупреждений
weather_warning_label = tk.Label(root, text="", font=('Arial', 12, 'bold'), bg=LIGHT_BG, fg="green")
weather_warning_label.grid(row=3, column=0, columnspan=4)

frame = tk.Frame(root, bg=LIGHT_BG)
frame.grid(row=4, column=0, columnspan=4)

# Настройка выравнивания в колонках для всех строк
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# Старт
show_weather(default_city or "")
root.mainloop()
