package com.clickbait.feedreader.data.repository

import com.clickbait.feedreader.data.api.RetrofitInstance
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.data.model.FeedResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Repository do zarządzania danymi artykułów
 */
class ArticleRepository {
    
    private val api = RetrofitInstance.api
    
    /**
     * Pobiera listę artykułów
     */
    suspend fun getArticles(limit: Int = 50, offset: Int = 0, source: String? = null): Result<FeedResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.getArticles(limit, offset, source)
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    /**
     * Pobiera artykuły z konkretnego źródła
     */
    suspend fun getArticlesBySource(source: String, limit: Int = 50, offset: Int = 0): Result<FeedResponse> {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.getArticlesBySource(source, limit)
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    /**
     * Pobiera szczegóły pojedynczego artykułu
     */
    suspend fun getArticleById(id: String): Result<Article> {
        return withContext(Dispatchers.IO) {
            try {
                val response = api.getArticleById(id)
                Result.success(response)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
