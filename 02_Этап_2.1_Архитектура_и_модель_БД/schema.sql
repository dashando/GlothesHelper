-- =========================================================================
-- СХЕМА РЕЛЯЦИОННОЙ БАЗЫ ДАННЫХ SQLite / Room
-- Проект: «Система интеллектуального подбора одежды “Умный гардероб”»
-- Шифр: WARDROBE-AI (ClothesHelper)
-- Кафедра № 41 ГУАП, 2026
-- =========================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = "UTF-8";

-- Таблица категорий одежды
CREATE TABLE IF NOT EXISTS categories (
    code TEXT PRIMARY KEY NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT
);

INSERT OR IGNORE INTO categories (code, display_name, description) VALUES
('top', 'Верх', 'Футболки, рубашки, свитеры, худи, лонгсливы'),
('bottom', 'Брюки/юбка', 'Джинсы, классические брюки, юбки, шорты'),
('dress', 'Платье', 'Платья, сарафаны, цельные комбинезоны'),
('outerwear', 'Верхняя одежда', 'Куртки, пальто, плащи, ветровки, пуховики'),
('shoes', 'Обувь', 'Кроссовки, ботинки, туфли, сапоги, сандалии'),
('accessory', 'Аксессуар', 'Шарфы, шапки, перчатки, зонты, ремни');

-- Основная таблица предметов одежды («Цифровой шкаф»)
CREATE TABLE IF NOT EXISTS clothing_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) > 0 AND length(title) <= 100),
    category_code TEXT NOT NULL,
    color_tone TEXT NOT NULL,
    warmth_level TEXT NOT NULL CHECK(warmth_level IN ('light', 'demi', 'warm', 'winter')),
    style_type TEXT NOT NULL CHECK(style_type IN ('casual', 'formal', 'sport')),
    is_waterproof INTEGER NOT NULL DEFAULT 0 CHECK(is_waterproof IN (0, 1)),
    image_path TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    FOREIGN KEY (category_code) REFERENCES categories(code) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Таблица кэша метеорологических прогнозов (для экономии трафика и офлайн доступа)
CREATE TABLE IF NOT EXISTS weather_cache (
    city_name TEXT PRIMARY KEY NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    timezone TEXT NOT NULL,
    forecast_time INTEGER NOT NULL,
    temperature REAL NOT NULL,
    apparent_temperature REAL NOT NULL,
    precipitation_probability INTEGER NOT NULL,
    wind_speed REAL NOT NULL,
    raw_payload_json TEXT NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Индексы для сверхбыстрой фильтрации согласно п. 4.1.3 ТЗ (< 0.2 с)
CREATE INDEX IF NOT EXISTS idx_clothing_cat_warmth ON clothing_items(category_code, warmth_level);
CREATE INDEX IF NOT EXISTS idx_clothing_style ON clothing_items(style_type);
CREATE INDEX IF NOT EXISTS idx_clothing_waterproof ON clothing_items(is_waterproof);
CREATE INDEX IF NOT EXISTS idx_clothing_color ON clothing_items(color_tone);
