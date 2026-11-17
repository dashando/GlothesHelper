package com.guap.clotheshelper.data

import kotlinx.coroutines.flow.Flow

/**
 * Репозиторий доступа к локальному реестру гардероба.
 */
class WardrobeRepository(private val dao: ClothingDao) {
    fun getAllItems(): Flow<List<ClothingEntity>> = dao.getAllItems()

    suspend fun getItemsByCategory(categoryCode: String): List<ClothingEntity> =
        dao.getItemsByCategory(categoryCode)

    suspend fun getItemById(id: Long): ClothingEntity? = dao.getItemById(id)

    suspend fun addItem(
        title: String,
        categoryCode: String,
        colorTone: String,
        warmthLevel: String,
        styleType: String,
        isWaterproof: Boolean = false,
        imagePath: String? = null
    ): Long {
        require(title.isNotBlank()) { "Название вещи не может быть пустым." }
        require(title.length <= 100) { "Название вещи не должно превышать 100 символов." }

        val entity = ClothingEntity(
            title = title.trim(),
            categoryCode = categoryCode,
            colorTone = colorTone,
            warmthLevel = warmthLevel,
            styleType = styleType,
            isWaterproof = isWaterproof,
            imagePath = imagePath
        )
        return dao.insertItem(entity)
    }

    suspend fun updateItem(item: ClothingEntity) = dao.updateItem(item)

    suspend fun deleteItem(item: ClothingEntity) = dao.deleteItem(item)

    suspend fun deleteById(id: Long) = dao.deleteById(id)

    suspend fun getCount(): Int = dao.getCount()
}
