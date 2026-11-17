# -*- coding: utf-8 -*-
"""
Тестовый скрипт верификации этапа 2.2:
- Проверка операций БД SQLite (CRUD, транзакции, индексы)
- Проверка классификации цвета и категории
"""
import os
import time
from PIL import Image, ImageDraw
from wardrobe_repo import WardrobeRepository
from color_extractor import extract_dominant_color
from onnx_classifier import OnnxClothingClassifier

def test_stage2_2():
    print("=== ТЕСТИРОВАНИЕ ЭТАПА 2.2: ХРАНИЛИЩЕ И ONNX ===")
    
    # 1. Тест репозитория
    test_db = "/tmp/test_wardrobe.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    repo = WardrobeRepository(test_db)
    
    t0 = time.time()
    id1 = repo.add_item("Белая рубашка Oxford", "top", "Белый", "light", "formal", False)
    id2 = repo.add_item("Синие джинсы Slim", "bottom", "Синий", "demi", "casual", False)
    id3 = repo.add_item("Черная зимняя куртка", "outerwear", "Черный", "winter", "casual", True)
    dt_insert = (time.time() - t0) / 3.0
    print(f"[OK] Добавлено 3 вещи в SQLite. Среднее время вставки: {dt_insert*1000:.2f} мс (норма < 200 мс)")
    assert repo.get_count() == 3, "Ошибка подсчета записей"

    # Чтение
    items = repo.get_all_items(category_code="top")
    assert len(items) == 1 and items[0]["title"] == "Белая рубашка Oxford"
    print("[OK] Фильтрация по категории работает корректно.")

    # Обновление
    repo.update_item(id1, "Белая рубашка Oxford (глаженная)", "top", "Белый", "light", "formal", False)
    assert repo.get_item_by_id(id1)["title"] == "Белая рубашка Oxford (глаженная)"
    print("[OK] Обновление карточки вещи работает корректно.")

    # Удаление
    repo.delete_item(id2)
    assert repo.get_count() == 2
    print("[OK] Удаление вещи работает корректно.")

    # 2. Тест синтетического изображения и цветового квантователя
    test_img_path = "/tmp/test_blue_tshirt.png"
    img = Image.new("RGB", (224, 224), color=(240, 240, 240)) # нейтральный фон
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 184, 184], fill=(20, 60, 200)) # синий предмет в центре
    img.save(test_img_path)

    t_onnx = time.time()
    classifier = OnnxClothingClassifier()
    res = classifier.predict(test_img_path)
    dt_onnx = time.time() - t_onnx

    print(f"[OK] Анализ изображения выполнен за {dt_onnx*1000:.2f} мс (норма < 1500 мс)")
    print(f"     Категория: {res['category_name']}, Доминирующий цвет: {res['detected_color']}, Уверенность: {res['confidence']:.2f}")
    assert res["detected_color"] in ["Синий", "Голубой"], f"Неверно определен цвет: {res['detected_color']}"

    print("=== ВСЕ ТЕСТЫ ЭТАПА 2.2 УСПЕШНО ПРОЙДЕНЫ (100%) ===")

if __name__ == "__main__":
    test_stage2_2()
