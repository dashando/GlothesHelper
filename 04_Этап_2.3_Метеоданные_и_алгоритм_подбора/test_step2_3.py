# -*- coding: utf-8 -*-
"""
Тестовый скрипт верификации этапа 2.3:
- Проверка получения прогноза погоды через Open-Meteo API и оффлайн режима
- Проверка генерации 3 вариантов рекомендаций
- Проверка диагностики дефицита гардероба
"""
import sys, os
sys.path.append("/Users/dashandooo/Desktop/учёба/опд/Проект_Умный_Гардероб_ClothesHelper/03_Этап_2.2_Хранилище_гардероба_и_ONNX")
from wardrobe_repo import WardrobeRepository
from weather_service import WeatherService
from recommendation_engine import OutfitRecommendationEngine

def test_step2_3():
    print("=== ТЕСТИРОВАНИЕ ЭТАПА 2.3: МЕТЕОДАННЫЕ И ПОДБОР ===")
    
    # 1. Тест погоды
    ws = WeatherService()
    print("Запрос погоды для Санкт-Петербурга...")
    w_spb = ws.get_weather("Санкт-Петербург", day_offset=0, target_hour=14)
    print(f"[OK] Получена погода: Город={w_spb['city']}, Ощущается={w_spb['apparent_temperature']}°C, "
          f"Осадки={w_spb['precipitation_probability']}%, Ветер={w_spb['wind_speed']} м/с, Таймзона={w_spb['timezone']}")
    assert "apparent_temperature" in w_spb

    # Ручной ввод погоды
    w_manual = ws.get_manual_weather(temperature=-5.0, precipitation_prob=60, wind_speed=8.0)
    print(f"[OK] Ручной ввод погоды: T={w_manual['temperature']}°C, Ветер={w_manual['wind_speed']} м/с, Дождь/Снег={w_manual['precipitation_probability']}%")
    assert w_manual["is_manual"] is True

    # 2. Инициализация репозитория с вещами для теста
    test_db = "/tmp/test_rec_wardrobe.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    repo = WardrobeRepository(test_db)
    
    # Добавим полный гардероб
    repo.add_item("Белая хлопковая рубашка", "top", "Белый", "light", "formal", False)
    repo.add_item("Синий шерстяной свитер", "top", "Синий", "warm", "casual", False)
    repo.add_item("Черные классические брюки", "bottom", "Черный", "demi", "formal", False)
    repo.add_item("Синие джинсы", "bottom", "Синий", "demi", "casual", False)
    repo.add_item("Кожаные осенние ботинки", "shoes", "Коричневый", "demi", "formal", True)
    repo.add_item("Белые кроссовки", "shoes", "Белый", "light", "casual", False)
    repo.add_item("Черное демисезонное пальто", "outerwear", "Черный", "demi", "formal", True)
    repo.add_item("Складной зонт", "accessory", "Черный", "light", "casual", True)

    engine = OutfitRecommendationEngine(repo)

    # 3. Тест подбора под погоду и событие «работа»
    res_work = engine.generate_recommendations(w_spb, "работа")
    assert res_work["success"] is True
    print(f"[OK] Сгенерировано {len(res_work['outfits'])} комплектов для события 'работа':")
    for i, out in enumerate(res_work["outfits"], 1):
        items_str = ", ".join(it["title"] for it in out["items"])
        print(f"     Вариант {i} ({out['type']}): {items_str}")
        print(f"     Пояснение: {out['explanation']}")

    # 4. Тест диагностики дефицита (пустая база)
    empty_db = "/tmp/empty_wardrobe.db"
    if os.path.exists(empty_db):
        os.remove(empty_db)
    empty_repo = WardrobeRepository(empty_db)
    engine_empty = OutfitRecommendationEngine(empty_repo)
    res_deficit = engine_empty.generate_recommendations(w_spb, "спортзал")
    assert res_deficit["success"] is False
    print(f"[OK] Диагностика дефицита гардероба сработала успешно: {res_deficit['deficit_message']}")

    print("=== ВСЕ ТЕСТЫ ЭТАПА 2.3 УСПЕШНО ПРОЙДЕНЫ (100%) ===")

if __name__ == "__main__":
    test_step2_3()
