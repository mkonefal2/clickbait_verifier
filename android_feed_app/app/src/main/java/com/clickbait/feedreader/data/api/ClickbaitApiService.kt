package com.clickbait.feedreader.data.api

import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.data.model.FeedResponse
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * API service dla komunikacji z backendem clickbait verifier
 */
interface ClickbaitApiService {
    
    /**
     * Pobiera listę artykułów ze wszystkich źródeł
     */
    @GET("api/articles")
    suspend fun getArticles(
        @Query("limit") limit: Int = 50,
        @Query("offset") offset: Int = 0,
        @Query("source") source: String? = null
    ): FeedResponse
    
    /**
     * Pobiera szczegóły pojedynczego artykułu
     */
    @GET("api/articles/{id}")
    suspend fun getArticleById(
        @Path("id") id: String
    ): Article
    
    /**
     * Pobiera listę artykułów z konkretnego źródła
     */
    @GET("api/sources/{source}/articles")
    suspend fun getArticlesBySource(
        @Path("source") source: String,
        @Query("limit") limit: Int = 50
    ): FeedResponse
}
