package com.clickbait.feedreader.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.ui.components.ArticleCard
import com.clickbait.feedreader.ui.viewmodel.FeedUiState
import com.clickbait.feedreader.ui.viewmodel.FeedViewModel

/**
 * Ekran główny z feedem artykułów
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedScreen(
    onArticleClick: (Article) -> Unit,
    viewModel: FeedViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val selectedSource by viewModel.selectedSource.collectAsState()
    
    Scaffold(
        topBar = {
            FeedTopBar(
                onRefresh = { viewModel.refresh() },
                selectedSource = selectedSource,
                onSourceChange = { viewModel.selectSource(it) }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(MaterialTheme.colorScheme.background)
        ) {
            when (val state = uiState) {
                is FeedUiState.Loading -> {
                    LoadingView()
                }
                is FeedUiState.Success -> {
                    ArticleList(
                        articles = state.articles,
                        onArticleClick = onArticleClick,
                        onLoadMore = { viewModel.loadMore() }
                    )
                }
                is FeedUiState.Error -> {
                    ErrorView(
                        message = state.message,
                        onRetry = { viewModel.refresh() }
                    )
                }
            }
        }
    }
}

/**
 * Top bar z tytułem i akcjami
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FeedTopBar(
    onRefresh: () -> Unit,
    selectedSource: String?,
    onSourceChange: (String?) -> Unit
) {
    var showSourceMenu by remember { mutableStateOf(false) }
    val sources = listOf("Wszystkie", "onet", "rmf24", "focuspl", "naukawpolsce")
    
    TopAppBar(
        title = {
            Text(
                text = "Aktualności",
                fontWeight = FontWeight.Bold
            )
        },
        actions = {
            // Filter button
            TextButton(onClick = { showSourceMenu = true }) {
                Text(
                    text = selectedSource ?: "Wszystkie",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            
            // Dropdown menu for source selection
            DropdownMenu(
                expanded = showSourceMenu,
                onDismissRequest = { showSourceMenu = false }
            ) {
                sources.forEach { source ->
                    DropdownMenuItem(
                        text = { Text(source) },
                        onClick = {
                            onSourceChange(if (source == "Wszystkie") null else source)
                            showSourceMenu = false
                        }
                    )
                }
            }
            
            IconButton(onClick = onRefresh) {
                Icon(
                    imageVector = Icons.Default.Refresh,
                    contentDescription = "Odśwież"
                )
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primary,
            titleContentColor = MaterialTheme.colorScheme.onPrimary,
            actionIconContentColor = MaterialTheme.colorScheme.onPrimary
        )
    )
}

/**
 * Lista artykułów
 */
@Composable
fun ArticleList(
    articles: List<Article>,
    onArticleClick: (Article) -> Unit,
    onLoadMore: () -> Unit
) {
    if (articles.isEmpty()) {
        EmptyView()
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(vertical = 8.dp)
        ) {
            items(articles) { article ->
                ArticleCard(
                    article = article,
                    onClick = { onArticleClick(article) }
                )
            }
            item {
                // Load more button at end
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Button(onClick = onLoadMore) {
                        Text(text = "Pokaż więcej")
                    }
                }
            }
        }
    }
}

/**
 * Widok ładowania
 */
@Composable
fun LoadingView() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            CircularProgressIndicator()
            Text(
                text = "Ładowanie...",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}

/**
 * Widok błędu
 */
@Composable
fun ErrorView(
    message: String,
    onRetry: () -> Unit
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
            modifier = Modifier.padding(32.dp)
        ) {
            Text(
                text = "Wystąpił błąd",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.error
            )
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onBackground
            )
            Button(onClick = onRetry) {
                Text("Spróbuj ponownie")
            }
        }
    }
}

/**
 * Widok pustej listy
 */
@Composable
fun EmptyView() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Brak artykułów",
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onBackground
        )
    }
}
