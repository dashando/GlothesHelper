package com.guap.clotheshelper

import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.rememberWindowState
import com.guap.clotheshelper.ui.theme.ClothesHelperTheme
import com.guap.clotheshelper.ui.WardrobeCatalogScreen

fun main() = application {
    val windowState = rememberWindowState(width = 1200.dp, height = 800.dp)
    Window(
        onCloseRequest = ::exitApplication,
        title = "Умный гардероб — WARDROBE-AI (ClothesHelper) | ГУАП Каф. 41",
        state = windowState
    ) {
        ClothesHelperTheme {
            // Главный контейнер навигации
        }
    }
}
