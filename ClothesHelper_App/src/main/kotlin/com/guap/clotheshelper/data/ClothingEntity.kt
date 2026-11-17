package com.guap.clotheshelper.data

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.ColumnInfo
import androidx.room.Index
import kotlinx.serialization.Serializable

/**
 * Сущность предмета гардероба в реляционной базе данных Room/SQLite.
 * Соответствует требованиям п. 4.1.1 ТЗ.
 */
@Serializable
@Entity(
    tableName = "clothing_items",
    indices = [
        Index(value = ["category_code", "warmth_level"]),
        Index(value = ["style_type"]),
        Index(value = ["is_waterproof"])
    ]
)
data class ClothingEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "title")
    val title: String,

    @ColumnInfo(name = "category_code")
    val categoryCode: String,

    @ColumnInfo(name = "color_tone")
    val colorTone: String,

    @ColumnInfo(name = "warmth_level")
    val warmthLevel: String, // light, demi, warm, winter

    @ColumnInfo(name = "style_type")
    val styleType: String,   // casual, formal, sport

    @ColumnInfo(name = "is_waterproof")
    val isWaterproof: Boolean = false,

    @ColumnInfo(name = "image_path")
    val imagePath: String? = null,

    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis(),

    @ColumnInfo(name = "updated_at")
    val updatedAt: Long = System.currentTimeMillis()
)
