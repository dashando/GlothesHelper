# -*- coding: utf-8 -*-
"""
Модуль извлечения доминирующего цвета одежды (ColorExtractor).
Устойчив к шумам и контрастному нейтральному фону.
"""
from PIL import Image
import colorsys

COLOR_PALETTE = {
    "Черный": (0, 0, 15),
    "Белый": (0, 0, 95),
    "Серый": (0, 0, 50),
    "Красный": (0, 80, 70),
    "Оранжевый": (30, 85, 80),
    "Желтый": (55, 85, 85),
    "Зеленый": (120, 70, 60),
    "Голубой": (195, 70, 75),
    "Синий": (230, 80, 50),
    "Фиолетовый": (280, 70, 55),
    "Розовый": (330, 60, 80),
    "Бежевый": (35, 30, 85),
    "Коричневый": (25, 60, 35)
}

def extract_dominant_color(image_path):
    """
    Анализирует изображение и определяет базовый доминирующий тон одежды.
    Игнорирует фон по периметру кадра.
    """
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((150, 150))
        w, h = img.size
        
        # Берем центральную область (20% от краев отсекаем)
        left = int(w * 0.2)
        top = int(h * 0.2)
        right = int(w * 0.8)
        bottom = int(h * 0.8)
        
        center_crop = img.crop((left, top, right, bottom))
        pixels = list(center_crop.getdata())
        
        # Анализ пикселей
        color_scores = {c: 0 for c in COLOR_PALETTE}
        
        for r, g, b in pixels:
            # Преобразуем в HSV
            h_val, s_val, v_val = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            h_deg = h_val * 360.0
            s_pct = s_val * 100.0
            v_pct = v_val * 100.0
            
            # Классификация оттенка
            if v_pct < 20:
                color_scores["Черный"] += 1.5
            elif s_pct < 15 and v_pct > 80:
                color_scores["Белый"] += 1.0
            elif s_pct < 18:
                color_scores["Серый"] += 1.0
            elif s_pct < 35 and 20 <= h_deg <= 45 and v_pct > 60:
                color_scores["Бежевый"] += 1.5
            elif 10 <= h_deg <= 40 and v_pct < 50:
                color_scores["Коричневый"] += 1.2
            elif (h_deg >= 345 or h_deg < 15):
                color_scores["Красный"] += 1.0
            elif 15 <= h_deg < 45:
                color_scores["Оранжевый"] += 1.0
            elif 45 <= h_deg < 70:
                color_scores["Желтый"] += 1.0
            elif 70 <= h_deg < 165:
                color_scores["Зеленый"] += 1.0
            elif 165 <= h_deg < 210:
                color_scores["Голубой"] += 1.0
            elif 210 <= h_deg < 260:
                color_scores["Синий"] += 1.0
            elif 260 <= h_deg < 310:
                color_scores["Фиолетовый"] += 1.0
            elif 310 <= h_deg < 345:
                color_scores["Розовый"] += 1.0

        dominant = max(color_scores, key=color_scores.get)
        return dominant
    except Exception as e:
        print(f"Color extraction error: {e}")
        return "Черный"
