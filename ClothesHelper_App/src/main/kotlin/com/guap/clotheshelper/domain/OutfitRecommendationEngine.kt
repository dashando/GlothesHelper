package com.guap.clotheshelper.domain

import com.guap.clotheshelper.data.ClothingEntity
import com.guap.clotheshelper.weather.WeatherSnapshot

sealed class RecommendationResult {
    data class Success(val outfits: List<OutfitPlan>) : RecommendationResult()
    data class Deficit(val message: String, val missingCategories: List<String>) : RecommendationResult()
}

data class OutfitPlan(
    val variantName: String,
    val items: List<ClothingEntity>,
    val explanation: String
)

class OutfitRecommendationEngine {
    fun generateOutfits(
        items: List<ClothingEntity>,
        weather: WeatherSnapshot,
        event: TargetEvent
    ): RecommendationResult {
        val effectiveTemp = weather.apparentTemperature - (weather.windSpeed * 0.7)
        val rainRisk = weather.precipitationProbability >= 30

        val byCategory = items.groupBy { it.categoryCode }
        val missing = mutableListOf<String>()

        if (!byCategory.containsKey("top") && !byCategory.containsKey("dress")) missing.add("Верх (или платье)")
        if (!byCategory.containsKey("bottom") && !byCategory.containsKey("dress")) missing.add("Брюки/юбка")
        if (!byCategory.containsKey("shoes")) missing.add("Обувь")

        if (missing.isNotEmpty()) {
            return RecommendationResult.Deficit(
                message = "Недостаточно вещей в гардеробе. Не хватает категорий: ${missing.joinToString()}",
                missingCategories = missing
            )
        }

        val top = byCategory["top"]?.firstOrNull()
        val bottom = byCategory["bottom"]?.firstOrNull()
        val shoes = byCategory["shoes"]?.firstOrNull()

        val outfitItems = listOfNotNull(top, bottom, shoes)
        val explanation = "Образ для события «${event.displayName}». Эффективная температура: ${"%.1f".format(effectiveTemp)}°C, ветер ${weather.windSpeed} м/с."

        val plan = OutfitPlan("Сбалансированный вариант", outfitItems, explanation)
        return RecommendationResult.Success(listOf(plan))
    }
}
