package com.guap.clotheshelper.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val PrimaryIndigo = Color(0xFF2A52BE)
val SecondaryTeal = Color(0xFF008080)
val BackgroundLight = Color(0xFFF8F9FA)
val SurfaceCard = Color(0xFFFFFFFF)
val TextDark = Color(0xFF1C1B1F)
val AccentOrange = Color(0xFFFF6F00)

private val LightColorScheme = lightColorScheme(
    primary = PrimaryIndigo,
    secondary = SecondaryTeal,
    background = BackgroundLight,
    surface = SurfaceCard,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = TextDark,
    onSurface = TextDark
)

@Composable
fun ClothesHelperTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = LightColorScheme,
        typography = Typography(),
        content = content
    )
}
