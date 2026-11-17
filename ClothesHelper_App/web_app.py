# -*- coding: utf-8 -*-
"""
Веб-интерфейс «ClothesHelper — Умный гардероб»
Работает на локальном сервере (http://127.0.0.1:8080) с современным Material Design UI.
Поддерживает загрузку фотографий, локальный AI-анализ, SQLite и Open-Meteo API.
"""
import os
import sys
import json
import time
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
from PIL import Image
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STEP2_DIR = os.path.join(os.path.dirname(BASE_DIR), "03_Этап_2.2_Хранилище_гардероба_и_ONNX")
STEP3_DIR = os.path.join(os.path.dirname(BASE_DIR), "04_Этап_2.3_Метеоданные_и_алгоритм_подбора")

sys.path.append(STEP2_DIR)
sys.path.append(STEP3_DIR)

from wardrobe_repo import WardrobeRepository
from onnx_classifier import OnnxClothingClassifier
from weather_service import WeatherService
from recommendation_engine import OutfitRecommendationEngine

db_path = os.path.join(BASE_DIR, "wardrobe.db")
repo = WardrobeRepository(db_path)
classifier = OnnxClothingClassifier()
weather_service = WeatherService()
engine = OutfitRecommendationEngine(repo)

HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClothesHelper — Умный гардероб | ГУАП Каф. 41</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --accent: #10b981;
            --purple: #8b5cf6;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); line-height: 1.5; }
        
        /* Header */
        header {
            background: #0f172a;
            color: #ffffff;
            padding: 16px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .logo-box h1 { font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 8px; }
        .logo-box p { font-size: 13px; color: #94a3b8; }
        .author-badge { font-size: 13px; color: #94a3b8; text-align: right; }
        
        /* Nav */
        nav {
            background: #ffffff;
            border-bottom: 1px solid var(--border);
            padding: 8px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav-tabs { display: flex; gap: 8px; }
        .tab-btn {
            background: transparent;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            color: var(--text-muted);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab-btn.active { background: #eff6ff; color: var(--primary); }
        .btn-add {
            background: var(--primary);
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .btn-add:hover { background: var(--primary-hover); }

        /* Main Content */
        main { max-width: 1240px; margin: 24px auto; padding: 0 20px; }

        /* Filters */
        .filter-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            display: flex;
            gap: 16px;
            align-items: center;
            margin-bottom: 24px;
            flex-wrap: wrap;
        }
        .filter-group { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 500; }
        select, input[type="text"], input[type="number"] {
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            outline: none;
            background: #ffffff;
        }
        select:focus, input:focus { border-color: var(--primary); }

        /* Grid */
        .clothes-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: 20px;
        }
        .card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
        }
        .card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        .card-img-box {
            width: 100%;
            height: 180px;
            background: #f1f5f9;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            border-bottom: 1px solid var(--border);
        }
        .card-img-box img { width: 100%; height: 100%; object-fit: contain; }
        .card-body { padding: 14px 16px; flex: 1; display: flex; flex-direction: column; }
        .card-title { font-size: 16px; font-weight: 700; margin-bottom: 6px; color: var(--text-main); }
        .badges-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
        .badge {
            font-size: 12px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 20px;
            background: #f1f5f9;
            color: #475569;
        }
        .badge.cat { background: #dbeafe; color: #1e40af; }
        .badge.water { background: #e0f2fe; color: #0369a1; }
        .card-actions { margin-top: auto; display: flex; justify-content: flex-end; border-top: 1px solid #f1f5f9; padding-top: 10px; }
        .btn-del {
            background: #fee2e2;
            color: #b91c1c;
            border: none;
            padding: 6px 12px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
        }
        .btn-del:hover { background: #fecaca; }

        /* Photo Upload & AI Section in Modal */
        .photo-upload-box {
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            background: #f8fafc;
            margin-bottom: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .photo-upload-box:hover { border-color: var(--primary); background: #eff6ff; }
        .photo-preview-box {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-top: 10px;
        }
        .photo-preview-img {
            width: 100px;
            height: 100px;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: #ffffff;
        }
        .ai-banner {
            background: #f5f3ff;
            border: 1px solid #ddd6fe;
            border-radius: 8px;
            padding: 10px 14px;
            color: #5b21b6;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 14px;
            display: none;
            align-items: center;
            gap: 8px;
        }
        .btn-ai-action {
            background: var(--purple);
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-ai-action:hover { background: #7c3aed; }

        /* Recommendations View */
        .weather-panel {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }
        .weather-info-box {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 15px;
            font-weight: 600;
            color: #1e40af;
        }
        .events-row { display: flex; gap: 12px; margin: 16px 0; flex-wrap: wrap; }
        .event-btn {
            background: #f1f5f9;
            border: 1px solid var(--border);
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
        }
        .event-btn.active { background: var(--primary); color: #ffffff; border-color: var(--primary); }

        .outfit-card {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .outfit-header { font-size: 18px; font-weight: 800; color: var(--primary); margin-bottom: 14px; }
        .outfit-items-flex { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 14px; }
        .outfit-item-chip {
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            width: 220px;
        }
        .outfit-item-chip img { width: 48px; height: 48px; object-fit: contain; border-radius: 4px; background: #fff; }
        .expl-box {
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 12px 16px;
            border-radius: 0 8px 8px 0;
            font-size: 14px;
            color: #15803d;
        }
        .deficit-box {
            background: #fef2f2;
            border-left: 4px solid var(--danger);
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            color: #991b1b;
            margin-bottom: 24px;
            font-size: 15px;
            font-weight: 600;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(4px);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: #ffffff;
            width: 520px;
            max-width: 92%;
            max-height: 90vh;
            overflow-y: auto;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
        }
        .modal-title { font-size: 18px; font-weight: 800; margin-bottom: 16px; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 4px; color: var(--text-muted); }
        .form-group input, .form-group select { width: 100%; }
        .modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
        .btn-cancel { background: #f1f5f9; border: none; padding: 10px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; }
    </style>
</head>
<body>
    <header>
        <div class="logo-box">
            <h1>👗 ClothesHelper — Умный гардероб</h1>
            <p>Система интеллектуального подбора одежды (WARDROBE-AI)</p>
        </div>
        <div class="author-badge">
            <p><strong>Кафедра № 41 ГУАП</strong> (2026)</p>
            <p>Соколова Д. А., Мингазова Э. Р. | Рук.: доц. С. А. Чернышев</p>
        </div>
    </header>

    <nav>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('catalog')">📁 Цифровой шкаф (Каталог)</button>
            <button class="tab-btn" onclick="switchTab('recommendations')">✨ Подбор образов (AI)</button>
        </div>
        <button class="btn-add" onclick="openAddModal()">➕ Добавить вещь с фото</button>
    </nav>

    <main>
        <!-- Вкладка 1: Каталог -->
        <div id="view-catalog">
            <div class="filter-card">
                <div class="filter-group">
                    <label>Категория:</label>
                    <select id="sel-cat" onchange="loadCatalog()">
                        <option value="">Все категории</option>
                        <option value="top">Верх</option>
                        <option value="bottom">Брюки/юбка</option>
                        <option value="dress">Платье</option>
                        <option value="outerwear">Верхняя одежда</option>
                        <option value="shoes">Обувь</option>
                        <option value="accessory">Аксессуар</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Стиль:</label>
                    <select id="sel-style" onchange="loadCatalog()">
                        <option value="">Все стили</option>
                        <option value="casual">Повседневный</option>
                        <option value="formal">Деловой</option>
                        <option value="sport">Спортивный</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Теплота:</label>
                    <select id="sel-warmth" onchange="loadCatalog()">
                        <option value="">Любая</option>
                        <option value="light">Лёгкая</option>
                        <option value="demi">Демисезонная</option>
                        <option value="warm">Тёплая</option>
                        <option value="winter">Зимняя</option>
                    </select>
                </div>
                <div class="filter-group" style="flex: 1;">
                    <input type="text" id="inp-search" placeholder="Поиск по названию..." oninput="loadCatalog()" style="width: 100%;">
                </div>
                <div style="font-weight: 700; color: var(--primary);" id="items-count">Всего: 0</div>
            </div>

            <div class="clothes-grid" id="grid-container">
                <!-- Карточки наполняются JS -->
            </div>
        </div>

        <!-- Вкладка 2: Рекомендации -->
        <div id="view-recommendations" style="display: none;">
            <div class="weather-panel">
                <h2 style="font-size: 18px; font-weight: 800; margin-bottom: 12px;">🌤 Параметры выхода и погодные условия</h2>
                <div style="display: flex; gap: 16px; flex-wrap: wrap; align-items: center;">
                    <div class="filter-group">
                        <label>Город:</label>
                        <select id="rec-city" onchange="updateWeather()">
                            <option value="Санкт-Петербург" selected>Санкт-Петербург</option>
                            <option value="Москва">Москва</option>
                            <option value="Новосибирск">Новосибирск</option>
                            <option value="Екатеринбург">Екатеринбург</option>
                            <option value="Казань">Казань</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>День:</label>
                        <select id="rec-day" onchange="updateWeather()">
                            <option value="0">Сегодня</option>
                            <option value="1">Завтра</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>Время:</label>
                        <select id="rec-hour" onchange="updateWeather()">
                            <option value="9">09:00</option>
                            <option value="12">12:00</option>
                            <option value="15" selected>15:00</option>
                            <option value="18">18:00</option>
                            <option value="21">21:00</option>
                        </select>
                    </div>
                    <label style="font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                        <input type="checkbox" id="chk-manual" onchange="toggleManualWeather()"> Ручной ввод (офлайн)
                    </label>
                </div>

                <div id="manual-weather-inputs" style="display: none; margin-top: 14px; gap: 14px; align-items: center; flex-wrap: wrap;">
                    <div class="filter-group">
                        <label>Темп. (°C):</label>
                        <input type="number" id="man-temp" value="12" style="width: 80px;" onchange="updateWeather()">
                    </div>
                    <div class="filter-group">
                        <label>Осадки (%):</label>
                        <input type="number" id="man-precip" value="20" style="width: 80px;" onchange="updateWeather()">
                    </div>
                    <div class="filter-group">
                        <label>Ветер (м/с):</label>
                        <input type="number" id="man-wind" value="4.5" style="width: 80px;" onchange="updateWeather()">
                    </div>
                </div>

                <div class="weather-info-box" id="weather-banner">
                    Загрузка актуального прогноза погоды через Open-Meteo API...
                </div>

                <h3 style="font-size: 15px; font-weight: 700; margin-top: 16px;">Формат мероприятия:*</h3>
                <div class="events-row">
                    <button class="event-btn active" onclick="selectEvent('учёба', this)">🎓 Учёба</button>
                    <button class="event-btn" onclick="selectEvent('работа', this)">💼 Работа</button>
                    <button class="event-btn" onclick="selectEvent('свидание', this)">💖 Свидание</button>
                    <button class="event-btn" onclick="selectEvent('прогулка', this)">🌲 Прогулка</button>
                    <button class="event-btn" onclick="selectEvent('спортзал', this)">🏋️ Спортзал</button>
                </div>

                <button class="btn-add" style="margin-top: 8px; width: 100%; padding: 14px; font-size: 16px; justify-content: center;" onclick="generateOutfits()">
                    ✨ Сгенерировать гармоничные комплекты одежды
                </button>
            </div>

            <div id="outfits-results">
                <!-- Результаты рекомендаций -->
            </div>
        </div>
    </main>

    <!-- Модальное окно добавления вещи С ФОТОГРАФИЕЙ И AI -->
    <div class="modal" id="modal-add">
        <div class="modal-content">
            <h2 class="modal-title">➕ Добавить вещь в шкаф</h2>
            
            <!-- Загрузка фото -->
            <div class="form-group">
                <label>Фотография вещи (JPEG / PNG / WEBP):</label>
                <div class="photo-upload-box" onclick="document.getElementById('file-photo').click()">
                    <input type="file" id="file-photo" accept="image/*" style="display: none;" onchange="onFileSelected(event)">
                    <div id="upload-prompt">
                        <div style="font-size: 28px; margin-bottom: 4px;">📷</div>
                        <div style="font-weight: 600; color: var(--primary);">Нажмите для выбора фотографии вещи</div>
                        <div style="font-size: 12px; color: var(--text-muted);">или перетащите файл сюда</div>
                    </div>
                    <div class="photo-preview-box" id="preview-box" style="display: none;">
                        <img id="preview-img" class="photo-preview-img" src="" alt="Превью">
                        <div style="text-align: left; flex: 1;">
                            <div style="font-weight: 700; font-size: 13px;" id="file-name-label">photo.png</div>
                            <button type="button" class="btn-ai-action" onclick="runAiAnalysis(event)" style="margin-top: 6px;">
                                ✨ Запустить анализ AI (ONNX)
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="ai-banner" id="ai-banner">
                <span>🤖</span>
                <span id="ai-text">Нейросеть определила категорию и цвет!</span>
            </div>

            <div class="form-group">
                <label>Название вещи (до 100 символов):*</label>
                <input type="text" id="new-title" placeholder="например, Голубая рубашка в полоску">
            </div>

            <div class="form-group">
                <label>Категория одежды:*</label>
                <select id="new-cat">
                    <option value="top">Верх (футболка, рубашка, свитер, худи)</option>
                    <option value="bottom">Брюки/юбка (джинсы, брюки, юбка, шорты)</option>
                    <option value="dress">Платье (сарафан, комбинезон)</option>
                    <option value="outerwear">Верхняя одежда (куртка, пальто, пуховик)</option>
                    <option value="shoes">Обувь (кроссовки, ботинки, туфли)</option>
                    <option value="accessory">Аксессуар (шарф, зонт, перчатки)</option>
                </select>
            </div>

            <div class="form-group">
                <label>Основной цвет:*</label>
                <select id="new-color">
                    <option value="Черный">Черный</option>
                    <option value="Белый">Белый</option>
                    <option value="Серый">Серый</option>
                    <option value="Синий">Синий</option>
                    <option value="Голубой">Голубой</option>
                    <option value="Красный">Красный</option>
                    <option value="Бежевый">Бежевый</option>
                    <option value="Коричневый">Коричневый</option>
                    <option value="Зеленый">Зеленый</option>
                    <option value="Желтый">Желтый</option>
                    <option value="Розовый">Розовый</option>
                    <option value="Фиолетовый">Фиолетовый</option>
                </select>
            </div>

            <div class="form-group">
                <label>Степень теплоизоляции:*</label>
                <select id="new-warmth">
                    <option value="light">Лёгкая (лето, тепло > 18°C)</option>
                    <option value="demi" selected>Демисезонная (весна/осень 8..18°C)</option>
                    <option value="warm">Тёплая (прохладно -2..8°C)</option>
                    <option value="winter">Зимняя (мороз < -2°C)</option>
                </select>
            </div>

            <div class="form-group">
                <label>Стилистическая направленность:*</label>
                <select id="new-style">
                    <option value="casual" selected>Повседневный (casual)</option>
                    <option value="formal">Деловой (formal / office)</option>
                    <option value="sport">Спортивный (sport)</option>
                </select>
            </div>

            <div class="form-group">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" id="new-water" style="width: auto;"> Пригодность для дождливой погоды (влагозащита)
                </label>
            </div>

            <div class="modal-actions">
                <button class="btn-cancel" onclick="closeAddModal()">Отмена</button>
                <button class="btn-add" onclick="submitNewItem()">✓ Сохранить в гардероб</button>
            </div>
        </div>
    </div>

    <script>
        let currentEvent = 'учёба';
        let currentWeather = null;
        let selectedPhotoBase64 = null;
        let selectedPhotoName = null;

        const catNames = { top: "Верх", bottom: "Брюки/юбка", dress: "Платье", outerwear: "Верх. одежда", shoes: "Обувь", accessory: "Аксессуар" };
        const warmthNames = { light: "Лёгкая", demi: "Демисезонная", warm: "Тёплая", winter: "Зимняя" };
        const styleNames = { casual: "Повседневный", formal: "Деловой", sport: "Спортивный" };

        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            if (tab === 'catalog') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('view-catalog').style.display = 'block';
                document.getElementById('view-recommendations').style.display = 'none';
                loadCatalog();
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('view-catalog').style.display = 'none';
                document.getElementById('view-recommendations').style.display = 'block';
                updateWeather();
            }
        }

        async function loadCatalog() {
            const cat = document.getElementById('sel-cat').value;
            const style = document.getElementById('sel-style').value;
            const warmth = document.getElementById('sel-warmth').value;
            const query = document.getElementById('inp-search').value.toLowerCase().trim();

            const res = await fetch(`/api/items?cat=${cat}&style=${style}&warmth=${warmth}`);
            let items = await res.json();
            if (query) {
                items = items.filter(it => it.title.toLowerCase().includes(query));
            }

            document.getElementById('items-count').innerText = `Всего вещей: ${items.length}`;
            const grid = document.getElementById('grid-container');
            grid.innerHTML = '';

            items.forEach(it => {
                const card = document.createElement('div');
                card.className = 'card';
                const imgTag = it.image_path ? `<img src="/images/${it.image_path.split('/').pop()}" alt="${it.title}">` : `<div style="color: #94a3b8; font-size: 28px;">📷</div>`;
                const waterBadge = it.is_waterproof ? `<span class="badge water">💧 Водостойкая</span>` : '';

                card.innerHTML = `
                    <div class="card-img-box">${imgTag}</div>
                    <div class="card-body">
                        <div class="card-title">${it.title}</div>
                        <div class="badges-row">
                            <span class="badge cat">${catNames[it.category_code] || it.category_code}</span>
                            <span class="badge">${it.color_tone}</span>
                            <span class="badge">${warmthNames[it.warmth_level] || it.warmth_level}</span>
                            <span class="badge">${styleNames[it.style_type] || it.style_type}</span>
                            ${waterBadge}
                        </div>
                        <div class="card-actions">
                            <button class="btn-del" onclick="deleteItem(${it.id})">✕ Удалить</button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
        }

        async function deleteItem(id) {
            if (confirm("Удалить вещь из гардероба?")) {
                await fetch(`/api/delete?id=${id}`, { method: 'POST' });
                loadCatalog();
            }
        }

        function openAddModal() {
            selectedPhotoBase64 = null;
            selectedPhotoName = null;
            document.getElementById('new-title').value = '';
            document.getElementById('upload-prompt').style.display = 'block';
            document.getElementById('preview-box').style.display = 'none';
            document.getElementById('ai-banner').style.display = 'none';
            document.getElementById('modal-add').classList.add('active');
        }
        function closeAddModal() { document.getElementById('modal-add').classList.remove('active'); }

        function onFileSelected(event) {
            const file = event.target.files[0];
            if (!file) return;
            selectedPhotoName = file.name;
            const reader = new FileReader();
            reader.onload = function(e) {
                selectedPhotoBase64 = e.target.result;
                document.getElementById('upload-prompt').style.display = 'none';
                document.getElementById('preview-box').style.display = 'flex';
                document.getElementById('preview-img').src = selectedPhotoBase64;
                document.getElementById('file-name-label').innerText = file.name;

                // Если название пустое, подставляем имя файла без расширения
                const titleInput = document.getElementById('new-title');
                if (!titleInput.value) {
                    titleInput.value = file.name.replace(/\\.[^/.]+$/, "");
                }
            };
            reader.readAsDataURL(file);
        }

        async function runAiAnalysis(event) {
            event.stopPropagation();
            if (!selectedPhotoBase64) {
                alert("Сначала выберите файл фотографии.");
                return;
            }
            const aiBanner = document.getElementById('ai-banner');
            const aiText = document.getElementById('ai-text');
            aiBanner.style.display = 'flex';
            aiText.innerText = "Нейросеть выполняет локальный анализ кадра...";

            try {
                const res = await fetch('/api/ai_analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ photo_base64: selectedPhotoBase64, photo_name: selectedPhotoName })
                });
                const pred = await res.json();
                
                // Автоподстановка в форму
                if (pred.category_code) {
                    document.getElementById('new-cat').value = pred.category_code;
                }
                if (pred.detected_color) {
                    document.getElementById('new-color').value = pred.detected_color;
                }

                aiText.innerHTML = `Нейросеть определила: <strong>${pred.category_name}</strong> (уверенность ${(pred.confidence*100).toFixed(0)}%), цвет: <strong>${pred.detected_color}</strong>. Значения подставлены в форму!`;
            } catch (err) {
                aiText.innerText = "Анализ завершен. Пожалуйста, проверьте выбранные категорию и цвет.";
            }
        }

        async function submitNewItem() {
            const title = document.getElementById('new-title').value.trim();
            if (!title) { alert("Укажите наименование вещи"); return; }
            const payload = {
                title,
                category_code: document.getElementById('new-cat').value,
                color_tone: document.getElementById('new-color').value,
                warmth_level: document.getElementById('new-warmth').value,
                style_type: document.getElementById('new-style').value,
                is_waterproof: document.getElementById('new-water').checked ? 1 : 0,
                photo_base64: selectedPhotoBase64,
                photo_name: selectedPhotoName
            };
            await fetch('/api/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            closeAddModal();
            loadCatalog();
        }

        function toggleManualWeather() {
            const manual = document.getElementById('chk-manual').checked;
            document.getElementById('manual-weather-inputs').style.display = manual ? 'flex' : 'none';
            updateWeather();
        }

        async function updateWeather() {
            const isManual = document.getElementById('chk-manual').checked;
            const city = document.getElementById('rec-city').value;
            const day = document.getElementById('rec-day').value;
            const hour = document.getElementById('rec-hour').value;

            let url = `/api/weather?city=${encodeURIComponent(city)}&day=${day}&hour=${hour}&manual=${isManual}`;
            if (isManual) {
                const t = document.getElementById('man-temp').value;
                const p = document.getElementById('man-precip').value;
                const w = document.getElementById('man-wind').value;
                url += `&t=${t}&p=${p}&w=${w}`;
            }

            const res = await fetch(url);
            currentWeather = await res.json();
            const banner = document.getElementById('weather-banner');
            banner.innerHTML = `🌤 <strong>${city}:</strong> Температура: ${currentWeather.temperature}°C (ощущается как <strong>${currentWeather.apparent_temperature}°C</strong>), Ветер: <strong>${currentWeather.wind_speed} м/с</strong>, Осадки: <strong>${currentWeather.precipitation_probability}%</strong> [${currentWeather.timezone}]`;
        }

        function selectEvent(ev, btn) {
            currentEvent = ev;
            document.querySelectorAll('.event-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        async function generateOutfits() {
            if (!currentWeather) await updateWeather();
            const res = await fetch(`/api/recommend`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ weather: currentWeather, event: currentEvent })
            });
            const data = await res.json();
            const container = document.getElementById('outfits-results');
            container.innerHTML = '';

            if (!data.success) {
                container.innerHTML = `
                    <div class="deficit-box">
                        ⚠️ <strong>ВНИМАНИЕ: ДЕФИЦИТ ВЕЩЕЙ В ГАРДЕРОБЕ</strong><br>
                        ${data.deficit_message}
                    </div>
                `;
                return;
            }

            data.outfits.forEach((out, idx) => {
                const card = document.createElement('div');
                card.className = 'outfit-card';
                let chipsHtml = '';
                out.items.forEach(it => {
                    const imgUrl = it.image_path ? `/images/${it.image_path.split('/').pop()}` : '';
                    chipsHtml += `
                        <div class="outfit-item-chip">
                            ${imgUrl ? `<img src="${imgUrl}" alt="">` : '<div style="font-size:24px;">📷</div>'}
                            <div>
                                <div style="font-weight: 700; font-size: 13px;">${it.title}</div>
                                <div style="font-size: 11px; color: var(--text-muted);">${catNames[it.category_code] || it.category_code} • ${it.color_tone}</div>
                            </div>
                        </div>
                    `;
                });

                card.innerHTML = `
                    <div class="outfit-header">Образ #${idx + 1} — ${out.type}</div>
                    <div class="outfit-items-flex">${chipsHtml}</div>
                    <div class="expl-box">
                        <strong>💡 Обоснование алгоритма:</strong><br>
                        ${out.explanation}
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // Загрузка каталога при старте
        loadCatalog();
    </script>
</body>
</html>
"""

class AppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif path.startswith("/images/"):
            img_name = os.path.basename(path)
            img_path = os.path.join(BASE_DIR, "images", img_name)
            if os.path.exists(img_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.end_headers()
                with open(img_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif path == "/api/items":
            cat = query.get("cat", [None])[0] or None
            style = query.get("style", [None])[0] or None
            warmth = query.get("warmth", [None])[0] or None
            items = repo.get_all_items(category_code=cat, style_type=style, warmth_level=warmth)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(items, ensure_ascii=False).encode("utf-8"))
        elif path == "/api/weather":
            city = query.get("city", ["Санкт-Петербург"])[0]
            day = int(query.get("day", [0])[0])
            hour = int(query.get("hour", [14])[0])
            is_manual = query.get("manual", ["false"])[0] == "true"
            if is_manual:
                t = float(query.get("t", [12])[0])
                p = int(query.get("p", [20])[0])
                w = float(query.get("w", [4.5])[0])
                data = weather_service.get_manual_weather(t, p, w, city_name=city)
            else:
                data = weather_service.get_weather(city, day, hour)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8') if length > 0 else ""

        if path == "/api/ai_analyze":
            data = json.loads(body)
            b64_str = data.get("photo_base64", "")
            temp_path = "/tmp/temp_ai_upload.png"
            if b64_str and "," in b64_str:
                _, b64_data = b64_str.split(",", 1)
                img_bytes = base64.b64decode(b64_data)
                img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                img.save(temp_path)
            
            # Предсказание нейросетью и определение цвета
            pred = classifier.predict(temp_path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(pred, ensure_ascii=False).encode('utf-8'))

        elif path == "/api/add":
            data = json.loads(body)
            img_path = None
            b64_str = data.get("photo_base64")
            
            if b64_str and "," in b64_str:
                try:
                    _, b64_data = b64_str.split(",", 1)
                    img_bytes = base64.b64decode(b64_data)
                    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                    
                    filename = f"user_{int(time.time()*1000)}.png"
                    img_path = os.path.join(BASE_DIR, "images", filename)
                    img.save(img_path)
                except Exception as e:
                    print(f"Error saving image: {e}")

            item_id = repo.add_item(
                data["title"],
                data["category_code"],
                data["color_tone"],
                data["warmth_level"],
                data["style_type"],
                bool(data.get("is_waterproof", False)),
                image_path=img_path
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "id": item_id}).encode('utf-8'))

        elif path.startswith("/api/delete"):
            query = urllib.parse.parse_qs(parsed.query)
            item_id = int(query.get("id", [0])[0])
            repo.delete_item(item_id)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": True}).encode('utf-8'))

        elif path == "/api/recommend":
            data = json.loads(body)
            weather = data["weather"]
            event = data["event"]
            res = engine.generate_recommendations(weather, event)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8080):
    # Если порт занят, пробуем 8081 или следующий
    server = None
    for p in range(port, port + 10):
        try:
            server = HTTPServer(('127.0.0.1', p), AppHandler)
            port = p
            break
        except OSError:
            continue
    
    if not server:
        print("Could not bind port.")
        return

    url = f"http://127.0.0.1:{port}"
    print(f"ClothesHelper Web Server started at {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run_server()
