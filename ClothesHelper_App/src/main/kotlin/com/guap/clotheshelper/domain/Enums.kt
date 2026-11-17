package com.guap.clotheshelper.domain

/**
 * Перечисления доменной области «ClothesHelper» (WARDROBE-AI).
 */
enum class ClothingCategory(val code: String, val displayName: String) {
    TOP("top", "Верх"),
    BOTTOM("bottom", "Брюки/юбка"),
    DRESS("dress", "Платье"),
    OUTERWEAR("outerwear", "Верхняя одежда"),
    SHOES("shoes", "Обувь"),
    ACCESSORY("accessory", "Аксессуар");

    companion object {
        fun fromCode(code: String): ClothingCategory =
            values().firstOrNull { it.code.equals(code, ignoreCase = true) } ?: TOP
    }
}

enum class WarmthLevel(val code: String, val displayName: String, val minTemp: Double, val maxTemp: Double) {
    LIGHT("light", "Лёгкая", 18.0, 35.0),
    DEMI("demi", "Демисезонная", 8.0, 18.0),
    WARM("warm", "Тёплая", -2.0, 8.0),
    WINTER("winter", "Зимняя", -40.0, -2.0);

    companion object {
        fun fromCode(code: String): WarmthLevel =
            values().firstOrNull { it.code.equals(code, ignoreCase = true) } ?: DEMI
    }
}

enum class ClothingStyle(val code: String, val displayName: String) {
    CASUAL("casual", "Повседневный"),
    FORMAL("formal", "Деловой / Formal"),
    SPORT("sport", "Спортивный");

    companion object {
        fun fromCode(code: String): ClothingStyle =
            values().firstOrNull { it.code.equals(code, ignoreCase = true) } ?: CASUAL
    }
}

enum class TargetEvent(val code: String, val displayName: String, val compatibleStyles: List<ClothingStyle>) {
    STUDY("study", "Учёба", listOf(ClothingStyle.CASUAL, ClothingStyle.FORMAL)),
    WORK("work", "Работа", listOf(ClothingStyle.FORMAL, ClothingStyle.CASUAL)),
    DATE("date", "Свидание", listOf(ClothingStyle.CASUAL, ClothingStyle.FORMAL)),
    WALK("walk", "Прогулка", listOf(ClothingStyle.CASUAL, ClothingStyle.SPORT)),
    GYM("gym", "Спортзал", listOf(ClothingStyle.SPORT));

    companion object {
        fun fromCode(code: String): TargetEvent =
            values().firstOrNull { it.code.equals(code, ignoreCase = true) } ?: STUDY
    }
}
