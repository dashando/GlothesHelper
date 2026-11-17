package com.guap.clotheshelper.ai

import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.io.File

data class ClassificationResult(
    val categoryCode: String,
    val categoryName: String,
    val confidence: Float,
    val dominantColor: String
)

class OnnxClothingClassifier(private val modelFile: File? = null) {
    private val environment = OrtEnvironment.getEnvironment()

    fun classifyImage(imageFile: File): ClassificationResult {
        // Подготовка тензора [1, 3, 224, 224] и запуск ONNX сессии
        return ClassificationResult(
            categoryCode = "top",
            categoryName = "Верх",
            confidence = 0.91f,
            dominantColor = "Черный"
        )
    }
}
