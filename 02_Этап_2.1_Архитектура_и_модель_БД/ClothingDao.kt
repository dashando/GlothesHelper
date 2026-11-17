package com.guap.clotheshelper.data

import androidx.room.*
import kotlinx.coroutines.flow.Flow

/**
 * Интерфейс доступа к данным (DAO) для SQLite / Room.
 */
@Dao
interface ClothingDao {
    @Query("SELECT * FROM clothing_items ORDER BY updated_at DESC")
    fun getAllItems(): Flow<List<ClothingEntity>>

    @Query("SELECT * FROM clothing_items WHERE category_code = :categoryCode")
    suspend fun getItemsByCategory(categoryCode: String): List<ClothingEntity>

    @Query("SELECT * FROM clothing_items WHERE id = :id")
    suspend fun getItemById(id: Long): ClothingEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertItem(item: ClothingEntity): Long

    @Update
    suspend fun updateItem(item: ClothingEntity)

    @Delete
    suspend fun deleteItem(item: ClothingEntity)

    @Query("DELETE FROM clothing_items WHERE id = :id")
    suspend fun deleteById(id: Long)

    @Query("SELECT COUNT(*) FROM clothing_items")
    suspend fun getCount(): Int
}
