# -*- coding: utf-8 -*-
"""
Модуль получения метеорологических данных (WeatherService).
Поддерживает Open-Meteo REST API, геокодирование, таймзоны и автономный ручной режим.
"""
import urllib.request
import urllib.parse
import json
import time

CITIES = {
    "Санкт-Петербург": {"lat": 59.9386, "lon": 30.3141, "tz": "Europe/Moscow"},
    "Москва": {"lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},
    "Новосибирск": {"lat": 55.0415, "lon": 82.9346, "tz": "Asia/Novosibirsk"},
    "Екатеринбург": {"lat": 56.8519, "lon": 60.6122, "tz": "Asia/Yekaterinburg"},
    "Казань": {"lat": 55.7887, "lon": 49.1221, "tz": "Europe/Moscow"}
}

class WeatherService:
    def __init__(self):
        self.cache = {}

    def get_weather(self, city_name="Санкт-Петербург", day_offset=0, target_hour=12):
        """
        Получает прогноз погоды для указанного города, дня (0 - сегодня, 1 - завтра) и часа.
        """
        city_info = CITIES.get(city_name, CITIES["Санкт-Петербург"])
        lat = city_info["lat"]
        lon = city_info["lon"]
        tz = city_info["tz"]
        
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&hourly=temperature_2m,apparent_temperature,precipitation_probability,wind_speed_10m"
               f"&timezone={urllib.parse.quote(tz)}&forecast_days=2")
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ClothesHelper-GUAP/1.0'})
            with urllib.request.urlopen(req, timeout=3.0) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            apparents = hourly.get("apparent_temperature", [])
            precips = hourly.get("precipitation_probability", [])
            winds = hourly.get("wind_speed_10m", [])
            
            # Индекс нужного часа: day_offset * 24 + target_hour
            idx = min(max(day_offset * 24 + target_hour, 0), len(times) - 1)
            
            result = {
                "city": city_name,
                "timezone": tz,
                "time_iso": times[idx] if times else "N/A",
                "temperature": temps[idx] if temps else 15.0,
                "apparent_temperature": apparents[idx] if apparents else 13.0,
                "precipitation_probability": precips[idx] if precips else 10,
                "wind_speed": winds[idx] if winds else 3.5,
                "is_manual": False
            }
            self.cache[city_name] = result
            return result
        except Exception as e:
            print(f"Weather API error ({e}). Using cached/default values.")
            if city_name in self.cache:
                return self.cache[city_name]
            return self.get_manual_weather(temperature=14.0, precipitation_prob=20, wind_speed=4.0, city_name=city_name)

    def get_manual_weather(self, temperature, precipitation_prob, wind_speed, city_name="Ручной ввод"):
        """
        Автономный режим: формирование структуры погоды из введенных пользователем данных.
        """
        # Эмпирический расчет ощущаемой температуры: T_app = T - (wind * 0.5)
        apparent = temperature - (wind_speed * 0.5)
        return {
            "city": city_name,
            "timezone": "Local",
            "time_iso": time.strftime("%Y-%m-%dT%H:00"),
            "temperature": round(float(temperature), 1),
            "apparent_temperature": round(apparent, 1),
            "precipitation_probability": int(precipitation_prob),
            "wind_speed": round(float(wind_speed), 1),
            "is_manual": True
        }
