# -*- coding: utf-8 -*-
"""
Движок многокритериального интеллектуального подбора одежды (OutfitRecommendationEngine).
Формирует до 3 образов с текстовым объяснением и диагностикой дефицита.
"""

EVENT_STYLE_MAP = {
    "учёба": ["casual", "formal"],
    "работа": ["formal", "casual"],
    "свидание": ["casual", "formal"],
    "прогулка": ["casual", "sport"],
    "спортзал": ["sport"]
}

BASE_NEUTRAL_COLORS = {"Черный", "Белый", "Серый", "Бежевый", "Коричневый", "Синий", "Голубой"}

class OutfitRecommendationEngine:
    def __init__(self, wardrobe_repo):
        self.repo = wardrobe_repo

    def _determine_target_warmth(self, apparent_temp, wind_speed):
        effective_temp = apparent_temp - (wind_speed * 0.7)
        if effective_temp >= 18.0:
            return "light"
        elif effective_temp >= 8.0:
            return "demi"
        elif effective_temp >= -2.0:
            return "warm"
        else:
            return "winter"

    def generate_recommendations(self, weather_data, event_name="учёба"):
        """
        Генерирует до 3 вариантов комплектов одежды:
        1. Сбалансированный основной
        2. Утепленный / защищенный
        3. Альтернативный образ
        Или возвращает диагностическое сообщение о нехватке вещей.
        """
        event_key = event_name.lower().strip()
        allowed_styles = EVENT_STYLE_MAP.get(event_key, ["casual"])
        
        apparent_temp = weather_data.get("apparent_temperature", 15.0)
        wind_speed = weather_data.get("wind_speed", 3.0)
        precip_prob = weather_data.get("precipitation_probability", 0)
        is_rain_likely = precip_prob >= 30

        target_warmth = self._determine_target_warmth(apparent_temp, wind_speed)
        
        # Получаем все вещи из базы
        all_items = self.repo.get_all_items()
        
        # Группируем по категориям
        by_category = {
            "top": [],
            "bottom": [],
            "dress": [],
            "outerwear": [],
            "shoes": [],
            "accessory": []
        }
        for item in all_items:
            cat = item["category_code"]
            if cat in by_category:
                by_category[cat].append(item)

        # Диагностика базовой нехватки вещей
        missing_categories = []
        if not by_category["top"] and not by_category["dress"]:
            missing_categories.append("Верх (или платье)")
        if not by_category["bottom"] and not by_category["dress"]:
            missing_categories.append("Брюки/юбка")
        if not by_category["shoes"]:
            missing_categories.append("Обувь")
        if target_warmth in ["demi", "warm", "winter"] and not by_category["outerwear"]:
            missing_categories.append("Верхняя одежда по погоде")
        
        if missing_categories:
            return {
                "success": False,
                "deficit_message": f"Недостаточно вещей в гардеробе для формирования комплекта. Не хватает категорий: {', '.join(missing_categories)}.",
                "outfits": []
            }

        # Фильтруем элементы с учетом стилей и теплоты
        def score_item(item, desired_warmth, req_waterproof=False):
            score = 100
            # Стиль
            if item["style_type"] in allowed_styles:
                score += 30
            else:
                score -= 40
            # Теплота
            warmth_order = ["light", "demi", "warm", "winter"]
            idx_item = warmth_order.index(item["warmth_level"])
            idx_desired = warmth_order.index(desired_warmth)
            diff = abs(idx_item - idx_desired)
            score -= diff * 25
            # Водостойкость
            if req_waterproof and item["is_waterproof"]:
                score += 35
            return score

        outfits = []

        # Вариант 1: Основной сбалансированный
        top_candidates = sorted(by_category["top"], key=lambda x: score_item(x, target_warmth), reverse=True)
        bottom_candidates = sorted(by_category["bottom"], key=lambda x: score_item(x, target_warmth), reverse=True)
        shoes_candidates = sorted(by_category["shoes"], key=lambda x: score_item(x, target_warmth, req_waterproof=is_rain_likely), reverse=True)
        outer_candidates = sorted(by_category["outerwear"], key=lambda x: score_item(x, target_warmth, req_waterproof=is_rain_likely), reverse=True)

        if top_candidates and bottom_candidates and shoes_candidates:
            v1_items = [top_candidates[0], bottom_candidates[0], shoes_candidates[0]]
            if target_warmth in ["demi", "warm", "winter"] and outer_candidates:
                v1_items.append(outer_candidates[0])
            
            # Аксессуар при дожде или холоде
            if is_rain_likely:
                umbrella = next((a for a in by_category["accessory"] if "зонт" in a["title"].lower()), None)
                if umbrella and umbrella not in v1_items:
                    v1_items.append(umbrella)
            elif target_warmth in ["warm", "winter"]:
                scarf = next((a for a in by_category["accessory"] if a["warmth_level"] in ["warm", "winter"]), None)
                if scarf and scarf not in v1_items:
                    v1_items.append(scarf)

            reason1 = (f"Основной образ для события «{event_name}». Учтена ощущаемая температура {apparent_temp}°C "
                       f"и ветер {wind_speed} м/с (выбран тепловой режим: {target_warmth}). "
                       f"{'Включены водозащитные элементы ввиду вероятности дождя ' + str(precip_prob) + '%.' if is_rain_likely else 'Погода сухая, акцент на удобство.'}")
            outfits.append({
                "type": "Сбалансированный вариант",
                "items": v1_items,
                "explanation": reason1
            })

        # Вариант 2: Утепленный / Защищенный
        warmer_warmth = "winter" if target_warmth == "warm" else ("warm" if target_warmth == "demi" else target_warmth)
        v2_items = []
        if outer_candidates:
            v2_items.append(outer_candidates[min(1, len(outer_candidates)-1)])
        if top_candidates:
            v2_items.append(top_candidates[min(1, len(top_candidates)-1)])
        if bottom_candidates:
            v2_items.append(bottom_candidates[min(1, len(bottom_candidates)-1)])
        if shoes_candidates:
            v2_items.append(shoes_candidates[0])
        if by_category["accessory"]:
            v2_items.append(by_category["accessory"][0])

        if len(v2_items) >= 3:
            reason2 = (f"Утепленный комплект с запасом прочности на случай вечернего похолодания или усиления порывов ветра. "
                       f"Сохраняет гармонию со стилем «{event_name}» и повышенную термоизоляцию.")
            outfits.append({
                "type": "Утепленный / защищенный вариант",
                "items": v2_items,
                "explanation": reason2
            })

        # Вариант 3: Альтернативный стильный образ (Платье или альтернативная палитра)
        if by_category["dress"] and event_name in ["свидание", "учёба", "работа"]:
            dress = sorted(by_category["dress"], key=lambda x: score_item(x, target_warmth), reverse=True)[0]
            v3_items = [dress, shoes_candidates[-1] if len(shoes_candidates) > 1 else shoes_candidates[0]]
            if outer_candidates and target_warmth in ["demi", "warm", "winter"]:
                v3_items.append(outer_candidates[0])
            reason3 = f"Элегантный цельный образ на основе платья «{dress['title']}», подходящий для формата «{event_name}»."
            outfits.append({
                "type": "Альтернативный образ (Платье)",
                "items": v3_items,
                "explanation": reason3
            })
        elif len(top_candidates) > 2 and len(bottom_candidates) > 1:
            v3_items = [top_candidates[2], bottom_candidates[1], shoes_candidates[-1]]
            if outer_candidates:
                v3_items.append(outer_candidates[-1])
            reason3 = f"Альтернативная комбинация в свежей цветовой гамме, оптимизированная под активность «{event_name}»."
            outfits.append({
                "type": "Альтернативный вариант",
                "items": v3_items,
                "explanation": reason3
            })

        return {
            "success": True,
            "deficit_message": None,
            "outfits": outfits[:3]
        }
