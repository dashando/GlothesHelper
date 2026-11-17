package com.guap.clotheshelper.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.guap.clotheshelper.data.ClothingEntity

/**
 * Экран «Цифровой шкаф» (Каталог одежды).
 * Реализует п. 4.1.1 (подсистема 2).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WardrobeCatalogScreen(
    items: List<ClothingEntity>,
    onAddItemClick: () -> Unit,
    onItemClick: (ClothingEntity) -> Unit,
    onNavigateToOutfitGeneration: () -> Unit
) {
    var searchQuery by remember { mutableStateOf("") }
    var selectedCategory by remember { mutableStateOf<String?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Умный гардероб — Цифровой шкаф") },
                actions = {
                    Button(onClick = onNavigateToOutfitGeneration) {
                        Text("Подобрать образ")
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onAddItemClick) {
                Icon(Icons.Default.Add, contentDescription = "Добавить вещь")
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp)
        ) {
            // Поисковая строка и фильтры
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("Поиск вещей в гардеробе...") },
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) },
                singleLine = true
            )

            Spacer(modifier = Modifier.height(12.dp))

            // Фильтры категорий
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                FilterChip(
                    selected = selectedCategory == null,
                    onClick = { selectedCategory = null },
                    label = { Text("Все (${items.size})") }
                )
                FilterChip(
                    selected = selectedCategory == "top",
                    onClick = { selectedCategory = "top" },
                    label = { Text("Верх") }
                )
                FilterChip(
                    selected = selectedCategory == "bottom",
                    onClick = { selectedCategory = "bottom" },
                    label = { Text("Низ") }
                )
                FilterChip(
                    selected = selectedCategory == "outerwear",
                    onClick = { selectedCategory = "outerwear" },
                    label = { Text("Верхняя одежда") }
                )
                FilterChip(
                    selected = selectedCategory == "shoes",
                    onClick = { selectedCategory = "shoes" },
                    label = { Text("Обувь") }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Сетка карточек
            val filteredItems = items.filter { item ->
                (selectedCategory == null || item.categoryCode == selectedCategory) &&
                (searchQuery.isBlank() || item.title.contains(searchQuery, ignoreCase = true))
            }

            LazyVerticalGrid(
                columns = GridCells.Adaptive(minSize = 200.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                items(filteredItems) { clothingItem ->
                    ElevatedCard(
                        onClick = { onItemClick(clothingItem) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Text(
                                text = clothingItem.title,
                                style = MaterialTheme.typography.titleMedium
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = "Цвет: ${clothingItem.colorTone} • ${clothingItem.warmthLevel}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.secondary
                            )
                        }
                    }
                }
            }
        }
    }
}
