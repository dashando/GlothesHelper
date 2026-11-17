# -*- coding: utf-8 -*-
"""
=============================================================================
ПРОГРАММНЫЙ ПРОДУКТ «СИСТЕМА ИНТЕЛЛЕКТУАЛЬНОГО ПОДБОРА ОДЕЖДЫ “УМНЫЙ ГАРДЕРОБ”»
Шифр разработки: WARDROBE-AI (ClothesHelper)
Кафедра программной инженерии и вычислительной техники (№ 41) ГУАП, 2026
Исполнители: студентки гр. 4618 Соколова Д. А., Мингазова Э. Р.
Руководитель: доцент, канд. техн. наук Чернышев С. А.
=============================================================================
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Подавление предупреждений macOS Tk
os.environ['TK_SILENCE_DEPRECATION'] = '1'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STEP2_DIR = os.path.join(os.path.dirname(BASE_DIR), "03_Этап_2.2_Хранилище_гардероба_и_ONNX")
STEP3_DIR = os.path.join(os.path.dirname(BASE_DIR), "04_Этап_2.3_Метеоданные_и_алгоритм_подбора")

sys.path.append(STEP2_DIR)
sys.path.append(STEP3_DIR)

from wardrobe_repo import WardrobeRepository
from onnx_classifier import OnnxClothingClassifier
from weather_service import WeatherService
from recommendation_engine import OutfitRecommendationEngine

CATEGORIES_MAP = {
    "top": "Верх",
    "bottom": "Брюки/юбка",
    "dress": "Платье",
    "outerwear": "Верхняя одежда",
    "shoes": "Обувь",
    "accessory": "Аксессуар"
}
REVERSE_CAT_MAP = {v: k for k, v in CATEGORIES_MAP.items()}

WARMTH_MAP = {
    "light": "Лёгкая",
    "demi": "Демисезонная",
    "warm": "Тёплая",
    "winter": "Зимняя"
}
REVERSE_WARMTH_MAP = {v: k for k, v in WARMTH_MAP.items()}

STYLE_MAP = {
    "casual": "Повседневный",
    "formal": "Деловой",
    "sport": "Спортивный"
}
REVERSE_STYLE_MAP = {v: k for k, v in STYLE_MAP.items()}

COLORS_LIST = [
    "Черный", "Белый", "Серый", "Синий", "Голубой", "Красный",
    "Бежевый", "Коричневый", "Зеленый", "Желтый", "Розовый", "Фиолетовый"
]

class ClothesHelperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Умный гардероб (ClothesHelper) — WARDROBE-AI | ГУАП Каф. 41")
        self.geometry("1160x840")
        self.minsize(980, 720)
        self.configure(bg="#F1F5F9")

        # Инициализация сервисов и БД
        self.db_path = os.path.join(BASE_DIR, "wardrobe.db")
        self.repo = WardrobeRepository(self.db_path)
        self.classifier = OnnxClothingClassifier()
        self.weather_service = WeatherService()
        self.engine = OutfitRecommendationEngine(self.repo)

        # Кэш картинок для Tkinter
        self.image_cache = []

        self._check_and_prepopulate_wardrobe()
        self._create_header_and_nav()
        
        # Контейнер для экранов
        self.main_container = tk.Frame(self, bg="#F1F5F9")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.catalog_frame = tk.Frame(self.main_container, bg="#F1F5F9")
        self.rec_frame = tk.Frame(self.main_container, bg="#F1F5F9")

        self._build_catalog_screen()
        self._build_recommendations_screen()

        # По умолчанию показываем каталог
        self.show_catalog()

    def _check_and_prepopulate_wardrobe(self):
        if self.repo.get_count() == 0:
            img_dir = os.path.join(BASE_DIR, "images")
            samples = [
                ("Белая рубашка Oxford", "top", "Белый", "light", "formal", False, os.path.join(img_dir, "white_shirt.png")),
                ("Синий шерстяной свитер", "top", "Синий", "warm", "casual", False, os.path.join(img_dir, "blue_sweater.png")),
                ("Серое оверсайз худи", "top", "Серый", "warm", "sport", False, os.path.join(img_dir, "grey_hoodie.png")),
                ("Классические черные брюки", "bottom", "Черный", "demi", "formal", False, os.path.join(img_dir, "black_trousers.png")),
                ("Синие джинсы Slim Fit", "bottom", "Синий", "demi", "casual", False, os.path.join(img_dir, "blue_jeans.png")),
                ("Спортивные джоггеры", "bottom", "Черный", "warm", "sport", False, os.path.join(img_dir, "sport_pants.png")),
                ("Красное вечернее платье", "dress", "Красный", "demi", "formal", False, os.path.join(img_dir, "red_dress.png")),
                ("Черное шерстяное пальто", "outerwear", "Черный", "demi", "formal", True, os.path.join(img_dir, "black_coat.png")),
                ("Теплый зимний пуховик", "outerwear", "Красный", "winter", "casual", True, os.path.join(img_dir, "winter_jacket.png")),
                ("Кожаные осенние ботинки", "shoes", "Коричневый", "demi", "formal", True, os.path.join(img_dir, "brown_boots.png")),
                ("Белые кожаные кроссовки", "shoes", "Белый", "light", "casual", False, os.path.join(img_dir, "white_sneakers.png")),
                ("Классические туфли Derby", "shoes", "Черный", "light", "formal", False, os.path.join(img_dir, "leather_shoes.png")),
                ("Ветрозащитный зонт-трость", "accessory", "Синий", "light", "casual", True, os.path.join(img_dir, "umbrella.png")),
                ("Шерстяной вязаный шарф", "accessory", "Бежевый", "winter", "casual", False, os.path.join(img_dir, "wool_scarf.png"))
            ]
            for s in samples:
                self.repo.add_item(*s)

    def _create_header_and_nav(self):
        # 1. Верхний информационный заголовок
        header = tk.Frame(self, bg="#0F172A", padx=20, pady=12)
        header.pack(fill=tk.X)

        lbl_title = tk.Label(header, text="👗 ClothesHelper — Умный гардероб", 
                             font=("Helvetica", 16, "bold"), fg="#FFFFFF", bg="#0F172A")
        lbl_title.pack(side=tk.LEFT)

        lbl_sub = tk.Label(header, text="Кафедра № 41 ГУАП | Д.А. Соколова, Э.Р. Мингазова | Рук.: доц. С.А. Чернышев",
                           font=("Helvetica", 11), fg="#94A3B8", bg="#0F172A")
        lbl_sub.pack(side=tk.RIGHT)

        # 2. Навигационная панель переключения экранов
        nav = tk.Frame(self, bg="#E2E8F0", padx=16, pady=8)
        nav.pack(fill=tk.X)

        self.btn_nav_catalog = tk.Button(nav, text="📁  Цифровой шкаф (Каталог)", font=("Helvetica", 11, "bold"),
                                         padx=14, pady=6, command=self.show_catalog)
        self.btn_nav_catalog.pack(side=tk.LEFT, padx=6)

        self.btn_nav_rec = tk.Button(nav, text="✨  Подбор образов (AI Рекомендации)", font=("Helvetica", 11),
                                     padx=14, pady=6, command=self.show_recommendations)
        self.btn_nav_rec.pack(side=tk.LEFT, padx=6)

        btn_add = tk.Button(nav, text="➕  Добавить вещь в шкаф", font=("Helvetica", 11, "bold"),
                            padx=14, pady=6, command=self._open_add_dialog)
        btn_add.pack(side=tk.RIGHT, padx=6)

    def show_catalog(self):
        self.rec_frame.pack_forget()
        self.catalog_frame.pack(fill=tk.BOTH, expand=True)
        self.btn_nav_catalog.config(relief="sunken")
        self.btn_nav_rec.config(relief="raised")
        self._refresh_catalog()

    def show_recommendations(self):
        self.catalog_frame.pack_forget()
        self.rec_frame.pack(fill=tk.BOTH, expand=True)
        self.btn_nav_rec.config(relief="sunken")
        self.btn_nav_catalog.config(relief="raised")
        self._fetch_current_weather()

    # -------------------------------------------------------------------------
    # ЭКРАН 1: ЦИФРОВОЙ ШКАФ
    # -------------------------------------------------------------------------
    def _build_catalog_screen(self):
        # Панель фильтров
        filter_box = tk.LabelFrame(self.catalog_frame, text=" Фильтры каталога ", font=("Helvetica", 10, "bold"),
                                   bg="#FFFFFF", padx=12, pady=8)
        filter_box.pack(fill=tk.X, padx=16, pady=8)

        # Категория
        tk.Label(filter_box, text="Категория:", font=("Helvetica", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=4)
        self.cat_filter_var = tk.StringVar(value="Все")
        cb_cat = ttk.Combobox(filter_box, textvariable=self.cat_filter_var, 
                              values=["Все"] + list(CATEGORIES_MAP.values()), state="readonly", width=14)
        cb_cat.pack(side=tk.LEFT, padx=4)
        cb_cat.bind("<<ComboboxSelected>>", lambda e: self._refresh_catalog())

        # Стиль
        tk.Label(filter_box, text="Стиль:", font=("Helvetica", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=6)
        self.style_filter_var = tk.StringVar(value="Все")
        cb_style = ttk.Combobox(filter_box, textvariable=self.style_filter_var,
                                values=["Все"] + list(STYLE_MAP.values()), state="readonly", width=13)
        cb_style.pack(side=tk.LEFT, padx=4)
        cb_style.bind("<<ComboboxSelected>>", lambda e: self._refresh_catalog())

        # Теплота
        tk.Label(filter_box, text="Теплота:", font=("Helvetica", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=6)
        self.warmth_filter_var = tk.StringVar(value="Все")
        cb_warmth = ttk.Combobox(filter_box, textvariable=self.warmth_filter_var,
                                 values=["Все"] + list(WARMTH_MAP.values()), state="readonly", width=13)
        cb_warmth.pack(side=tk.LEFT, padx=4)
        cb_warmth.bind("<<ComboboxSelected>>", lambda e: self._refresh_catalog())

        # Поиск
        tk.Label(filter_box, text="Поиск:", font=("Helvetica", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=8)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_catalog())
        ent_search = ttk.Entry(filter_box, textvariable=self.search_var, width=16)
        ent_search.pack(side=tk.LEFT, padx=4)

        self.lbl_count = tk.Label(filter_box, text="Всего: 0", font=("Helvetica", 10, "bold"), fg="#2563EB", bg="#FFFFFF")
        self.lbl_count.pack(side=tk.RIGHT, padx=12)

        # Скроллируемая область карточек
        container = tk.Frame(self.catalog_frame, bg="#F1F5F9")
        container.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.cat_canvas = tk.Canvas(container, bg="#F1F5F9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.cat_canvas.yview)
        self.cards_grid = tk.Frame(self.cat_canvas, bg="#F1F5F9")

        self.cards_grid.bind("<Configure>", lambda e: self.cat_canvas.configure(scrollregion=self.cat_canvas.bbox("all")))
        self.grid_window_id = self.cat_canvas.create_window((0, 0), window=self.cards_grid, anchor="nw")
        self.cat_canvas.configure(yscrollcommand=scrollbar.set)

        self.cat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.cat_canvas.bind('<Configure>', lambda e: self.cat_canvas.itemconfig(self.grid_window_id, width=e.width))

    def _refresh_catalog(self):
        for w in self.cards_grid.winfo_children():
            w.destroy()
        self.image_cache.clear()

        cat_val = self.cat_filter_var.get()
        cat_code = REVERSE_CAT_MAP.get(cat_val) if cat_val != "Все" else None

        style_val = self.style_filter_var.get()
        style_code = REVERSE_STYLE_MAP.get(style_val) if style_val != "Все" else None

        warmth_val = self.warmth_filter_var.get()
        warmth_code = REVERSE_WARMTH_MAP.get(warmth_val) if warmth_val != "Все" else None

        items = self.repo.get_all_items(category_code=cat_code, style_type=style_code, warmth_level=warmth_code)
        
        q = self.search_var.get().lower().strip()
        if q:
            items = [it for it in items if q in it["title"].lower()]

        self.lbl_count.config(text=f"Вещей в шкафу: {len(items)}")

        if not items:
            lbl = tk.Label(self.cards_grid, text="Нет вещей, соответствующих выбранным фильтрам.", 
                           font=("Helvetica", 13), fg="#64748B", bg="#F1F5F9")
            lbl.pack(pady=40)
            return

        # Сетка 4 колонки
        cols = 4
        for idx, item in enumerate(items):
            r = idx // cols
            c = idx % cols
            self._render_card(self.cards_grid, item, r, c)

    def _render_card(self, parent, item, row, col):
        card = tk.Frame(parent, bg="#FFFFFF", padx=10, pady=10, relief="solid", bd=1)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        # 1. Фото через Canvas (фиксированный размер 110x110 пикселей)
        canvas = tk.Canvas(card, width=110, height=110, bg="#F8FAFC", highlightthickness=1, highlightbackground="#CBD5E1")
        canvas.pack(pady=4)

        img_path = item.get("image_path")
        loaded = False
        if img_path and os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path).resize((106, 106))
                tk_img = ImageTk.PhotoImage(pil_img)
                self.image_cache.append(tk_img)
                canvas.create_image(55, 55, image=tk_img)
                loaded = True
            except Exception:
                pass
        
        if not loaded:
            canvas.create_text(55, 55, text="📷 Фото", font=("Helvetica", 11), fill="#64748B")

        # 2. Название вещи
        lbl_title = tk.Label(card, text=item["title"], font=("Helvetica", 11, "bold"), 
                             fg="#0F172A", bg="#FFFFFF", wraplength=210, justify="center")
        lbl_title.pack(pady=2)

        # 3. Теги
        cat_text = CATEGORIES_MAP.get(item["category_code"], item["category_code"])
        warmth_text = WARMTH_MAP.get(item["warmth_level"], item["warmth_level"])
        style_text = STYLE_MAP.get(item["style_type"], item["style_type"])
        water_text = " • 💧 Водостойкая" if item["is_waterproof"] else ""

        tags = f"🏷 {cat_text} • {item['color_tone']}\n🌡 {warmth_text} • {style_text}{water_text}"
        lbl_tags = tk.Label(card, text=tags, font=("Helvetica", 9), fg="#475569", bg="#FFFFFF", justify="center")
        lbl_tags.pack(pady=4)

        # 4. Кнопки
        btn_row = tk.Frame(card, bg="#FFFFFF")
        btn_row.pack(fill=tk.X, pady=4)

        btn_e = tk.Button(btn_row, text="✎ Редактировать", font=("Helvetica", 9),
                          command=lambda itm=item: self._open_edit_dialog(itm))
        btn_e.pack(side=tk.LEFT, padx=2)

        btn_d = tk.Button(btn_row, text="✕ Удалить", font=("Helvetica", 9),
                          command=lambda itm=item: self._delete_item(itm))
        btn_d.pack(side=tk.RIGHT, padx=2)

    def _delete_item(self, item):
        if messagebox.askyesno("Удаление", f"Удалить «{item['title']}» из гардероба?"):
            self.repo.delete_item(item["id"])
            self._refresh_catalog()

    # -------------------------------------------------------------------------
    # ДИАЛОГ ДОБАВЛЕНИЯ / РЕДАКТИРОВАНИЯ ВЕЩИ
    # -------------------------------------------------------------------------
    def _open_add_dialog(self):
        self._open_form_dialog("Добавление вещи в гардероб")

    def _open_edit_dialog(self, item):
        self._open_form_dialog("Редактирование вещи", item=item)

    def _open_form_dialog(self, title_text, item=None):
        dlg = tk.Toplevel(self)
        dlg.title(title_text)
        dlg.geometry("520x640")
        dlg.configure(bg="#FFFFFF")
        dlg.grab_set()

        tk.Label(dlg, text=title_text, font=("Helvetica", 14, "bold"), fg="#0F172A", bg="#FFFFFF").pack(pady=12)

        form = tk.Frame(dlg, bg="#FFFFFF", padx=24)
        form.pack(fill=tk.BOTH, expand=True)

        # Название
        tk.Label(form, text="Название вещи (до 100 символов):*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=2)
        var_title = tk.StringVar(value=item["title"] if item else "")
        ent_title = ttk.Entry(form, textvariable=var_title, width=42)
        ent_title.pack(fill=tk.X, pady=4)

        # Блок фото и AI
        frame_photo = tk.LabelFrame(form, text=" Фотография и нейросетевой анализ ", font=("Helvetica", 9, "bold"),
                                    bg="#FFFFFF", padx=10, pady=8)
        frame_photo.pack(fill=tk.X, pady=8)

        var_img_path = tk.StringVar(value=item["image_path"] if item and item["image_path"] else "")
        
        cv_prev = tk.Canvas(frame_photo, width=80, height=80, bg="#F1F5F9", highlightthickness=1)
        cv_prev.pack(side=tk.LEFT, padx=6)

        def update_cv(p):
            if p and os.path.exists(p):
                try:
                    p_img = Image.open(p).resize((76, 76))
                    tk_p = ImageTk.PhotoImage(p_img)
                    cv_prev.create_image(40, 40, image=tk_p)
                    cv_prev.img = tk_p
                except Exception:
                    pass

        if var_img_path.get():
            update_cv(var_img_path.get())
        else:
            cv_prev.create_text(40, 40, text="Нет фото", fill="#64748B", font=("Helvetica", 9))

        btns_p = tk.Frame(frame_photo, bg="#FFFFFF")
        btns_p.pack(side=tk.LEFT, padx=10)

        def pick_file():
            path = filedialog.askopenfilename(title="Выберите фото вещи", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
            if path:
                var_img_path.set(path)
                update_cv(path)

        tk.Button(btns_p, text="📁 Выбрать фото...", command=pick_file).pack(anchor="w", pady=3)

        def run_ai():
            p = var_img_path.get()
            if not p or not os.path.exists(p):
                messagebox.showwarning("Внимание", "Сначала выберите файл фотографии вещи.")
                return
            res = self.classifier.predict(p)
            var_cat.set(res["category_name"])
            var_color.set(res["detected_color"])
            messagebox.showinfo("ONNX Анализ завершен", 
                                f"🤖 Нейросеть определила:\nКатегория: {res['category_name']} (уверенность {res['confidence']:.0%})\n"
                                f"Доминирующий цвет: {res['detected_color']}\n\nЗначения подставлены в форму!")

        tk.Button(btns_p, text="✨ Анализ AI (ONNX)", font=("Helvetica", 9, "bold"), command=run_ai).pack(anchor="w", pady=3)

        # Категория
        tk.Label(form, text="Категория одежды:*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=2)
        initial_cat = CATEGORIES_MAP.get(item["category_code"]) if item else "Верх"
        var_cat = tk.StringVar(value=initial_cat)
        cb_cat = ttk.Combobox(form, textvariable=var_cat, values=list(CATEGORIES_MAP.values()), state="readonly")
        cb_cat.pack(fill=tk.X, pady=4)

        # Цвет
        tk.Label(form, text="Основной цвет:*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=2)
        initial_color = item["color_tone"] if item else "Черный"
        var_color = tk.StringVar(value=initial_color)
        cb_color = ttk.Combobox(form, textvariable=var_color, values=COLORS_LIST, state="readonly")
        cb_color.pack(fill=tk.X, pady=4)

        # Теплота
        tk.Label(form, text="Уровень теплоизоляции:*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=2)
        initial_warmth = WARMTH_MAP.get(item["warmth_level"]) if item else "Демисезонная"
        var_warmth = tk.StringVar(value=initial_warmth)
        cb_warmth = ttk.Combobox(form, textvariable=var_warmth, values=list(WARMTH_MAP.values()), state="readonly")
        cb_warmth.pack(fill=tk.X, pady=4)

        # Стиль
        tk.Label(form, text="Стилистическая направленность:*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(anchor="w", pady=2)
        initial_style = STYLE_MAP.get(item["style_type"]) if item else "Повседневный"
        var_style = tk.StringVar(value=initial_style)
        cb_style = ttk.Combobox(form, textvariable=var_style, values=list(STYLE_MAP.values()), state="readonly")
        cb_style.pack(fill=tk.X, pady=4)

        # Влагозащита
        var_water = tk.BooleanVar(value=bool(item["is_waterproof"]) if item else False)
        chk_water = tk.Checkbutton(form, text="Пригодность для дождливой погоды (влагозащитные свойства)",
                                   variable=var_water, bg="#FFFFFF", font=("Helvetica", 10))
        chk_water.pack(anchor="w", pady=6)

        # Кнопки сохранения
        box_b = tk.Frame(dlg, bg="#FFFFFF", pady=12)
        box_b.pack(fill=tk.X, padx=20)

        def save():
            title_val = var_title.get().strip()
            if not title_val:
                messagebox.showerror("Ошибка", "Наименование вещи не может быть пустым.")
                return
            if len(title_val) > 100:
                messagebox.showerror("Ошибка", "Наименование вещи не должно превышать 100 символов.")
                return

            c_code = REVERSE_CAT_MAP[var_cat.get()]
            w_code = REVERSE_WARMTH_MAP[var_warmth.get()]
            s_code = REVERSE_STYLE_MAP[var_style.get()]
            col_val = var_color.get()
            is_w = var_water.get()
            img_p = var_img_path.get() if var_img_path.get() else None

            if item:
                self.repo.update_item(item["id"], title_val, c_code, col_val, w_code, s_code, is_w, img_p)
            else:
                self.repo.add_item(title_val, c_code, col_val, w_code, s_code, is_w, img_p)

            dlg.destroy()
            self._refresh_catalog()

        tk.Button(box_b, text="✓ Сохранить вещь", font=("Helvetica", 11, "bold"), padx=14, pady=6, command=save).pack(side=tk.RIGHT, padx=6)
        tk.Button(box_b, text="Отмена", font=("Helvetica", 10), padx=10, pady=6, command=dlg.destroy).pack(side=tk.RIGHT, padx=6)

    # -------------------------------------------------------------------------
    # ЭКРАН 2: ПОДБОР ОБРАЗОВ (РЕКОМЕНДАЦИИ)
    # -------------------------------------------------------------------------
    def _build_recommendations_screen(self):
        panel = tk.LabelFrame(self.rec_frame, text=" Условия подбора комплекта ", font=("Helvetica", 10, "bold"),
                              bg="#FFFFFF", padx=16, pady=10)
        panel.pack(fill=tk.X, padx=16, pady=8)

        # Строка 1: Город, день, время
        r1 = tk.Frame(panel, bg="#FFFFFF")
        r1.pack(fill=tk.X, pady=4)

        tk.Label(r1, text="Город:", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=4)
        self.city_var = tk.StringVar(value="Санкт-Петербург")
        cities = ["Санкт-Петербург", "Москва", "Новосибирск", "Екатеринбург", "Казань"]
        cb_city = ttk.Combobox(r1, textvariable=self.city_var, values=cities, state="readonly", width=16)
        cb_city.pack(side=tk.LEFT, padx=4)

        tk.Label(r1, text="День:", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=8)
        self.day_var = tk.StringVar(value="Сегодня")
        cb_day = ttk.Combobox(r1, textvariable=self.day_var, values=["Сегодня", "Завтра"], state="readonly", width=9)
        cb_day.pack(side=tk.LEFT, padx=4)

        tk.Label(r1, text="Время:", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=8)
        self.hour_var = tk.StringVar(value="14:00")
        hours = [f"{h:02d}:00" for h in range(24)]
        cb_hour = ttk.Combobox(r1, textvariable=self.hour_var, values=hours, state="readonly", width=7)
        cb_hour.pack(side=tk.LEFT, padx=4)

        tk.Button(r1, text="🔄 Обновить прогноз", font=("Helvetica", 9), command=self._fetch_current_weather).pack(side=tk.LEFT, padx=12)

        self.manual_toggle_var = tk.BooleanVar(value=False)
        chk_manual = tk.Checkbutton(r1, text="Ручной ввод погоды (офлайн)", variable=self.manual_toggle_var,
                                    bg="#FFFFFF", font=("Helvetica", 9, "bold"), command=self._toggle_manual_inputs)
        chk_manual.pack(side=tk.LEFT, padx=10)

        # Строка 2: Ручные поля
        self.manual_frame = tk.Frame(panel, bg="#F8FAFC", padx=10, pady=4)
        self.manual_frame.pack(fill=tk.X, pady=4)

        tk.Label(self.manual_frame, text="Температура (°C):", bg="#F8FAFC").pack(side=tk.LEFT, padx=4)
        self.man_t = tk.StringVar(value="12.0")
        ttk.Entry(self.manual_frame, textvariable=self.man_t, width=6).pack(side=tk.LEFT, padx=2)

        tk.Label(self.manual_frame, text="Вероятность осадков (%):", bg="#F8FAFC").pack(side=tk.LEFT, padx=8)
        self.man_p = tk.StringVar(value="25")
        ttk.Entry(self.manual_frame, textvariable=self.man_p, width=6).pack(side=tk.LEFT, padx=2)

        tk.Label(self.manual_frame, text="Скорость ветра (м/с):", bg="#F8FAFC").pack(side=tk.LEFT, padx=8)
        self.man_w = tk.StringVar(value="4.5")
        ttk.Entry(self.manual_frame, textvariable=self.man_w, width=6).pack(side=tk.LEFT, padx=2)

        self.manual_frame.pack_forget()

        # Строка 3: Информационная карточка погоды
        self.lbl_weather_info = tk.Label(panel, text="Погода: получение актуальных данных...", 
                                         font=("Helvetica", 10), fg="#2563EB", bg="#FFFFFF")
        self.lbl_weather_info.pack(anchor="w", pady=6)

        # Строка 4: Выбор события и кнопка генерации
        r4 = tk.Frame(panel, bg="#FFFFFF")
        r4.pack(fill=tk.X, pady=4)

        tk.Label(r4, text="Формат мероприятия:*", font=("Helvetica", 10, "bold"), bg="#FFFFFF").pack(side=tk.LEFT, padx=4)
        self.event_var = tk.StringVar(value="учёба")
        for ev in ["учёба", "работа", "свидание", "прогулка", "спортзал"]:
            tk.Radiobutton(r4, text=ev.capitalize(), value=ev, variable=self.event_var,
                           bg="#FFFFFF", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=6)

        btn_run = tk.Button(r4, text="✨  Сгенерировать комплекты", font=("Helvetica", 11, "bold"),
                            padx=14, pady=6, command=self._generate_outfits)
        btn_run.pack(side=tk.RIGHT, padx=6)

        # Скролл результатов
        rec_cont = tk.Frame(self.rec_frame, bg="#F1F5F9")
        rec_cont.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        self.rec_canvas = tk.Canvas(rec_cont, bg="#F1F5F9", highlightthickness=0)
        rec_scroll = ttk.Scrollbar(rec_cont, orient="vertical", command=self.rec_canvas.yview)
        self.rec_list = tk.Frame(self.rec_canvas, bg="#F1F5F9")

        self.rec_list.bind("<Configure>", lambda e: self.rec_canvas.configure(scrollregion=self.rec_canvas.bbox("all")))
        self.rec_win_id = self.rec_canvas.create_window((0, 0), window=self.rec_list, anchor="nw")
        self.rec_canvas.configure(yscrollcommand=rec_scroll.set)

        self.rec_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rec_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.rec_canvas.bind('<Configure>', lambda e: self.rec_canvas.itemconfig(self.rec_win_id, width=e.width))

    def _toggle_manual_inputs(self):
        if self.manual_toggle_var.get():
            self.manual_frame.pack(fill=tk.X, pady=4)
            self._update_manual_weather()
        else:
            self.manual_frame.pack_forget()
            self._fetch_current_weather()

    def _fetch_current_weather(self):
        city = self.city_var.get()
        day_offset = 0 if self.day_var.get() == "Сегодня" else 1
        h_str = self.hour_var.get().split(":")[0]
        hour = int(h_str) if h_str.isdigit() else 14

        self.current_weather = self.weather_service.get_weather(city, day_offset, hour)
        t = self.current_weather['temperature']
        t_app = self.current_weather['apparent_temperature']
        w = self.current_weather['wind_speed']
        p = self.current_weather['precipitation_probability']
        tz = self.current_weather['timezone']

        msg = f"🌤 Погода в г. {city}: {t}°C (ощущается как {t_app}°C), ветер {w} м/с, осадки: {p}% [{tz}]"
        self.lbl_weather_info.config(text=msg, fg="#0F172A")

    def _update_manual_weather(self):
        try:
            t = float(self.man_t.get())
            p = int(self.man_p.get())
            w = float(self.man_w.get())
            self.current_weather = self.weather_service.get_manual_weather(t, p, w, city_name=self.city_var.get())
            msg = f"⚙️ Автономный ручной режим: {t}°C (ощущается как {self.current_weather['apparent_temperature']}°C), ветер {w} м/с, осадки: {p}%"
            self.lbl_weather_info.config(text=msg, fg="#B45309")
        except Exception:
            self.lbl_weather_info.config(text="Ошибка: проверьте числовой формат полей погоды", fg="#DC2626")

    def _generate_outfits(self):
        if self.manual_toggle_var.get():
            self._update_manual_weather()

        for w in self.rec_list.winfo_children():
            w.destroy()

        ev = self.event_var.get()
        res = self.engine.generate_recommendations(self.current_weather, ev)

        if not res["success"]:
            # Баннер дефицита
            def_box = tk.Frame(self.rec_list, bg="#FEF2F2", padx=20, pady=16, relief="solid", bd=1)
            def_box.pack(fill=tk.X, padx=12, pady=16)

            tk.Label(def_box, text="⚠️  ДЕФИЦИТ ВЕЩЕЙ В ГАРДЕРОБЕ", font=("Helvetica", 12, "bold"),
                     bg="#FEF2F2", fg="#B91C1C").pack(anchor="w")
            tk.Label(def_box, text=res["deficit_message"], font=("Helvetica", 11),
                     bg="#FEF2F2", fg="#7F1D1D", wraplength=900, justify="left").pack(anchor="w", pady=6)
            return

        outfits = res["outfits"]
        lbl_head = tk.Label(self.rec_list, 
                            text=f"Сформировано {len(outfits)} варианта образов под мероприятие «{ev.capitalize()}»:",
                            font=("Helvetica", 12, "bold"), fg="#0F172A", bg="#F1F5F9")
        lbl_head.pack(anchor="w", padx=10, pady=8)

        for idx, out in enumerate(outfits, 1):
            self._render_outfit_card(self.rec_list, out, idx)

    def _render_outfit_card(self, parent, outfit, index):
        box = tk.Frame(parent, bg="#FFFFFF", padx=16, pady=14, relief="solid", bd=1)
        box.pack(fill=tk.X, padx=10, pady=10)

        # Заголовок
        lbl_v = tk.Label(box, text=f"Образ #{index} — {outfit['type']}", 
                         font=("Helvetica", 13, "bold"), fg="#2563EB", bg="#FFFFFF")
        lbl_v.pack(anchor="w")

        # Ряд вещей с фото
        row_items = tk.Frame(box, bg="#FFFFFF", pady=10)
        row_items.pack(fill=tk.X)

        for it in outfit["items"]:
            ibox = tk.Frame(row_items, bg="#F8FAFC", padx=8, pady=8, relief="groove", bd=1)
            ibox.pack(side=tk.LEFT, padx=6)

            cv = tk.Canvas(ibox, width=80, height=80, bg="#FFFFFF", highlightthickness=1)
            cv.pack()

            p = it.get("image_path")
            loaded = False
            if p and os.path.exists(p):
                try:
                    p_img = Image.open(p).resize((76, 76))
                    tk_p = ImageTk.PhotoImage(p_img)
                    self.image_cache.append(tk_p)
                    cv.create_image(40, 40, image=tk_p)
                    loaded = True
                except Exception:
                    pass
            if not loaded:
                cv.create_text(40, 40, text="📷", font=("Helvetica", 14), fill="#64748B")

            tk.Label(ibox, text=it["title"], font=("Helvetica", 9, "bold"), bg="#F8FAFC", wraplength=110, justify="center").pack(pady=2)
            c_name = CATEGORIES_MAP.get(it["category_code"], it["category_code"])
            tk.Label(ibox, text=f"{c_name} • {it['color_tone']}", font=("Helvetica", 8), bg="#F8FAFC", fg="#64748B").pack()

        # Разделитель
        sep = tk.Frame(box, height=1, bg="#E2E8F0")
        sep.pack(fill=tk.X, pady=8)

        # Текстовое обоснование выбора
        expl_box = tk.Frame(box, bg="#F0FDF4", padx=12, pady=8)
        expl_box.pack(fill=tk.X)

        tk.Label(expl_box, text="💡 Обоснование алгоритма подбора:", font=("Helvetica", 10, "bold"),
                 bg="#F0FDF4", fg="#166534").pack(anchor="w")
        tk.Label(expl_box, text=outfit["explanation"], font=("Helvetica", 10),
                 bg="#F0FDF4", fg="#14532D", wraplength=950, justify="left").pack(anchor="w", pady=2)


if __name__ == "__main__":
    app = ClothesHelperApp()
    app.mainloop()
