# -*- coding: utf-8 -*-
"""
Репозиторий локальной базы данных гардероба (WardrobeRepository) на SQLite.
Обеспечивает ACID-транзакции, валидацию и фильтрацию.
"""
import sqlite3
import time
import os

class WardrobeRepository:
    def __init__(self, db_path="wardrobe.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
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
                updated_at INTEGER NOT NULL
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clothing_cat_warmth ON clothing_items(category_code, warmth_level);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clothing_style ON clothing_items(style_type);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clothing_waterproof ON clothing_items(is_waterproof);")

    def add_item(self, title, category_code, color_tone, warmth_level, style_type, is_waterproof=False, image_path=None):
        if not title or len(title.strip()) == 0:
            raise ValueError("Название вещи не может быть пустым.")
        if len(title) > 100:
            raise ValueError("Название вещи не должно превышать 100 символов.")
        
        now = int(time.time() * 1000)
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO clothing_items (title, category_code, color_tone, warmth_level, style_type, is_waterproof, image_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title.strip(), category_code, color_tone, warmth_level, style_type, 1 if is_waterproof else 0, image_path, now, now))
            item_id = cur.lastrowid
            conn.commit()
            return item_id

    def update_item(self, item_id, title, category_code, color_tone, warmth_level, style_type, is_waterproof=False, image_path=None):
        now = int(time.time() * 1000)
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            UPDATE clothing_items 
            SET title = ?, category_code = ?, color_tone = ?, warmth_level = ?, style_type = ?, is_waterproof = ?, image_path = ?, updated_at = ?
            WHERE id = ?
            """, (title.strip(), category_code, color_tone, warmth_level, style_type, 1 if is_waterproof else 0, image_path, now, item_id))
            conn.commit()

    def delete_item(self, item_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM clothing_items WHERE id = ?", (item_id,))
            conn.commit()

    def get_all_items(self, category_code=None, style_type=None, warmth_level=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM clothing_items WHERE 1=1"
            params = []
            if category_code:
                query += " AND category_code = ?"
                params.append(category_code)
            if style_type:
                query += " AND style_type = ?"
                params.append(style_type)
            if warmth_level:
                query += " AND warmth_level = ?"
                params.append(warmth_level)
            query += " ORDER BY updated_at DESC"
            cur.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def get_item_by_id(self, item_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM clothing_items WHERE id = ?", (item_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_count(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM clothing_items")
            return cur.fetchone()[0]
