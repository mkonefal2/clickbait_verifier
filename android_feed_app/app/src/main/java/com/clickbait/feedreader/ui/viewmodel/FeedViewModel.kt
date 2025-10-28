package com.clickbait.feedreader.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.data.repository.ArticleRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Stan UI dla ekranu feedu
 */
sealed class FeedUiState {
    object Loading : FeedUiState()
    data class Success(val articles: List<Article>) : FeedUiState()
    data class Error(val message: String) : FeedUiState()
}

/**
 * ViewModel dla ekranu feedu
 */
class FeedViewModel : ViewModel() {
    
    private val repository = ArticleRepository()
    
    private val _uiState = MutableStateFlow<FeedUiState>(FeedUiState.Loading)
    val uiState: StateFlow<FeedUiState> = _uiState.asStateFlow()
    
    private val _selectedSource = MutableStateFlow<String?>(null)
    val selectedSource: StateFlow<String?> = _selectedSource.asStateFlow()
    
    // Pagination state
    private var currentOffset = 0
    private val pageSize = 20
    private var isLoadingMore = false
    private var endReached = false
    
    init {
        loadArticles()
    }
    
    /**
     * Ładuje artykuły z API
     */
    fun loadArticles(source: String? = null) {
        viewModelScope.launch {
            _uiState.value = FeedUiState.Loading
            currentOffset = 0
            endReached = false

            val result = if (source != null) {
                repository.getArticles(limit = pageSize, offset = currentOffset, source = source)
            } else {
                repository.getArticles(limit = pageSize, offset = currentOffset)
            }

            result.fold(
                onSuccess = { response ->
                    // if fewer items returned than pageSize, mark endReached
                    endReached = response.articles.size < pageSize
                    _uiState.value = FeedUiState.Success(response.articles)
                },
                onFailure = { exception ->
                    _uiState.value = FeedUiState.Error(
                        exception.message ?: "Nieznany błąd"
                    )
                }
            )
        }
    }

    /**
     * Load next page and append results
     */
    fun loadMore() {
        if (isLoadingMore || endReached) return
        isLoadingMore = true
        viewModelScope.launch {
            // show loading state only if we already have items
            val currentArticles = when (val s = _uiState.value) {
                is FeedUiState.Success -> s.articles
                else -> emptyList()
            }

            currentOffset += pageSize

            val result = if (_selectedSource.value != null) {
                repository.getArticles(limit = pageSize, offset = currentOffset, source = _selectedSource.value)
            } else {
                repository.getArticles(limit = pageSize, offset = currentOffset)
            }

            result.fold(
                onSuccess = { response ->
                    endReached = response.articles.size < pageSize
                    val combined = currentArticles + response.articles
                    _uiState.value = FeedUiState.Success(combined)
                },
                onFailure = { exception ->
                    // keep existing articles and show error state
                    _uiState.value = FeedUiState.Error(exception.message ?: "Nieznany błąd")
                }
            )

            isLoadingMore = false
        }
    }
    
    /**
     * Odświeża listę artykułów
     */
    fun refresh() {
        loadArticles(_selectedSource.value)
    }
    
    /**
     * Ustawia filtr źródła
     */
    fun selectSource(source: String?) {
        _selectedSource.value = source
        loadArticles(source)
    }
}
