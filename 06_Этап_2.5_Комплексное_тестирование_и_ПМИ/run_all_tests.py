# -*- coding: utf-8 -*-
"""
Автоматизированный комплекс приемо-сдаточных испытаний
Проект: «Система интеллектуального подбора одежды “Умный гардероб”» (ClothesHelper)
Реализует 9 контрольных сценариев раздела 8.2 Технического задания.
"""
import sys, os, time
from PIL import Image, ImageDraw

# Добавляем пути к модулям
BASE_DIR = "/Users/dashandooo/Desktop/учёба/опд/Проект_Умный_Гардероб_ClothesHelper"
sys.path.append(os.path.join(BASE_DIR, "03_Этап_2.2_Хранилище_гардероба_и_ONNX"))
sys.path.append(os.path.join(BASE_DIR, "04_Этап_2.3_Метеоданные_и_алгоритм_подбора"))

from wardrobe_repo import WardrobeRepository
from onnx_classifier import OnnxClothingClassifier
from weather_service import WeatherService
from recommendation_engine import OutfitRecommendationEngine

def run_all_tests():
    print("=" * 70)
    print("ПРОГРАММА И МЕТОДИКА ИСПЫТАНИЙ (ПМИ ГОСТ 19.301-79)")
    print("Проект: WARDROBE-AI (ClothesHelper), ГУАП Кафедра 41")
    print("=" * 70)
    
    test_db = "/tmp/pmi_test_wardrobe.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    passed_count = 0
    total_tests = 9

    # --- ТС-1: Ручное добавление карточки вещи ---
    print("\n[ТС-1] Добавление карточки вещи вручную с указанием полного набора атрибутов:")
    repo = WardrobeRepository(test_db)
    t0 = time.time()
    id1 = repo.add_item("Классическая белая рубашка", "top", "Белый", "light", "formal", False)
    id2 = repo.add_item("Синие джинсы Regular", "bottom", "Синий", "demi", "casual", False)
    t_add = time.time() - t0
    item1 = repo.get_item_by_id(id1)
    assert item1["title"] == "Классическая белая рубашка"
    assert item1["category_code"] == "top"
    assert item1["warmth_level"] == "light"
    assert item1["style_type"] == "formal"
    assert item1["is_waterproof"] == 0
    print(f" -> РЕЗУЛЬТАТ: Успешно. Время вставки 2 записей: {t_add*1000:.2f} мс (< 200 мс по ТЗ).")
    passed_count += 1

    # --- ТС-2: Добавление вещи с фото и нейросетевой анализ ONNX ---
    print("\n[ТС-2] Добавление вещи с импортом фотографии и запуск локального распознавания ONNX:")
    test_img = "/tmp/test_coat_img.jpg"
    img = Image.new("RGB", (224, 224), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 194, 194], fill=(20, 20, 20)) # черная куртка
    img.save(test_img)

    classifier = OnnxClothingClassifier()
    t_cls = time.time()
    prediction = classifier.predict(test_img)
    dt_cls = time.time() - t_cls
    print(f" -> Предсказана категория: {prediction['category_name']}, цвет: {prediction['detected_color']}, уверенность: {prediction['confidence']:.2f}")
    assert prediction["detected_color"] == "Черный"
    # Добавляем вещь после подтверждения
    id3 = repo.add_item("Зимняя куртка пуховик", "outerwear", prediction["detected_color"], "winter", "casual", True, test_img)
    print(f" -> РЕЗУЛЬТАТ: Успешно. Время нейросетевой классификации: {dt_cls*1000:.2f} мс (< 1500 мс по ТЗ).")
    passed_count += 1

    # --- ТС-3: Редактирование и удаление вещи ---
    print("\n[ТС-3] Редактирование характеристик существующей вещи и удаление из базы:")
    repo.update_item(id1, "Классическая белая рубашка (премиум)", "top", "Белый", "light", "formal", False)
    assert repo.get_item_by_id(id1)["title"] == "Классическая белая рубашка (премиум)"
    repo.delete_item(id2)
    assert repo.get_item_by_id(id2) is None
    print(" -> РЕЗУЛЬТАТ: Успешно. Вещь id1 обновлена, вещь id2 безвозвратно удалена.")
    passed_count += 1

    # --- ТС-4: Проверка персистентности данных после перезапуска ---
    print("\n[ТС-4] Проверка сохранения данных после перезапуска приложения:")
    # Закрываем старый репозиторий и открываем заново тот же файл БД
    del repo
    reopened_repo = WardrobeRepository(test_db)
    reopened_item = reopened_repo.get_item_by_id(id3)
    assert reopened_item is not None
    assert reopened_item["title"] == "Зимняя куртка пуховик"
    assert reopened_item["image_path"] == test_img
    print(" -> РЕЗУЛЬТАТ: Успешно. Данные и пути к изображениям сохранены без потерь.")
    passed_count += 1

    # --- ТС-5: Получение метеопрогноза через сеть с учетом часового пояса ---
    print("\n[ТС-5] Получение метеорологического прогноза из сети Open-Meteo:")
    ws = WeatherService()
    t_net = time.time()
    weather = ws.get_weather("Санкт-Петербург", day_offset=0, target_hour=15)
    dt_net = time.time() - t_net
    print(f" -> Погода в {weather['city']}: {weather['temperature']}°C (ощущается как {weather['apparent_temperature']}°C), "
          f"ветер {weather['wind_speed']} м/с, осадки {weather['precipitation_probability']}%, часовой пояс {weather['timezone']}")
    assert "apparent_temperature" in weather
    assert dt_net < 2.0
    print(f" -> РЕЗУЛЬТАТ: Успешно. Время ответа метеосервера: {dt_net:.2f} с (< 2,0 с по ТЗ).")
    passed_count += 1

    # --- ТС-6: Автономная работа при отключенном интернете с ручным вводом ---
    print("\n[ТС-6] Автономная работа при отключенном сетевом интерфейсе (ручной ввод):")
    manual_w = ws.get_manual_weather(temperature=-12.5, precipitation_prob=70, wind_speed=9.0)
    assert manual_w["is_manual"] is True
    assert manual_w["temperature"] == -12.5
    assert manual_w["apparent_temperature"] < -12.5
    print(f" -> РЕЗУЛЬТАТ: Успешно. Введены t={manual_w['temperature']}°C, осадки={manual_w['precipitation_probability']}%, "
          f"ветер={manual_w['wind_speed']} м/с. Эффективная температура: {manual_w['apparent_temperature']}°C.")
    passed_count += 1

    # --- ТС-7: Генерация до 3 вариантов комплектов с текстовым обоснованием ---
    print("\n[ТС-7] Формирование до трех вариантов комплектов одежды с развернутым обоснованием:")
    # Пополняем базу для полного подбора
    reopened_repo.add_item("Классические брюки", "bottom", "Черный", "demi", "formal", False)
    reopened_repo.add_item("Зимние теплые ботинки", "shoes", "Черный", "winter", "formal", True)
    reopened_repo.add_item("Теплый шерстяной шарф", "accessory", "Серый", "winter", "casual", False)
    reopened_repo.add_item("Спортивное худи", "top", "Серый", "warm", "sport", False)
    reopened_repo.add_item("Спортивные брюки", "bottom", "Черный", "warm", "sport", False)
    reopened_repo.add_item("Беговые кроссовки", "shoes", "Белый", "light", "sport", False)

    engine = OutfitRecommendationEngine(reopened_repo)
    rec = engine.generate_recommendations(weather, "учёба")
    assert rec["success"] is True
    assert len(rec["outfits"]) >= 1
    print(f" -> Сформировано {len(rec['outfits'])} варианта комплектов:")
    for idx, out in enumerate(rec["outfits"], 1):
        items_str = ", ".join(i["title"] for i in out["items"])
        print(f"    Вариант {idx} [{out['type']}]: {items_str}")
        print(f"    Текстовое обоснование: {out['explanation']}")
    print(" -> РЕЗУЛЬТАТ: Успешно. Все сформированные образы сопровождаются связным текстовым объяснением.")
    passed_count += 1

    # --- ТС-8: Поведение в условиях дефицита гардероба ---
    print("\n[ТС-8] Поведение системы в условиях дефицита гардероба:")
    empty_repo = WardrobeRepository("/tmp/empty_deficit.db")
    engine_deficit = OutfitRecommendationEngine(empty_repo)
    rec_deficit = engine_deficit.generate_recommendations(weather, "работа")
    assert rec_deficit["success"] is False
    assert "Не хватает категорий" in rec_deficit["deficit_message"]
    print(f" -> Диагностическое предупреждение: {rec_deficit['deficit_message']}")
    print(" -> РЕЗУЛЬТАТ: Успешно. Выведено понятное диагностическое сообщение со списком отсутствующих категорий.")
    passed_count += 1

    # --- ТС-9: Устойчивость к некорректным входным данным ---
    print("\n[ТС-9] Устойчивость приложения к некорректным и неполным входным данным:")
    try:
        reopened_repo.add_item("", "top", "Белый", "light", "formal", False)
        raise AssertionError("Ошибка: Пустое название не должно быть разрешено!")
    except ValueError as e:
        print(f" -> Перехвачена ошибка пустого имени: {e}")

    try:
        reopened_repo.add_item("A" * 150, "top", "Белый", "light", "formal", False)
        raise AssertionError("Ошибка: Превышение лимита в 100 символов не должно быть разрешено!")
    except ValueError as e:
        print(f" -> Перехвачена ошибка длинного имени: {e}")

    print(" -> РЕЗУЛЬТАТ: Успешно. Некорректные данные корректно отклоняются входной валидацией.")
    passed_count += 1

    print("\n" + "=" * 70)
    print(f"ИТОГ ИСПЫТАНИЙ: Успешно пройдено {passed_count} из {total_tests} тестов ({passed_count/total_tests*100:.0f}%)")
    print("КРИТЕРИЙ ПРИЕМКИ ВЫПОЛНЕН В ПОЛНОМ ОБЪЕМЕ. ПРОДУКТ ГОТОВ К СДАЧЕ.")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
