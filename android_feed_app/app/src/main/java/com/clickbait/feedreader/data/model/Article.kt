package com.clickbait.feedreader.data.model

import com.google.gson.annotations.SerializedName

/**
 * Model reprezentujący artykuł z feedu
 */
data class Article(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("url")
    val url: String,
    
    @SerializedName("title")
    val title: String,
    
    @SerializedName("source")
    val source: String,
    
    @SerializedName("publishedAt")
    val publishedAt: String? = null,
    
    @SerializedName("imageUrl")
    val imageUrl: String? = null,
    
    @SerializedName("content")
    val content: String? = null,
    
    @SerializedName("analysis")
    val analysis: Analysis? = null
)

/**
 * Model reprezentujący analizę clickbait
 */
data class Analysis(
    @SerializedName("clickbaitScore")
    val clickbaitScore: Double? = null,
    
    @SerializedName("hasClickbait")
    val hasClickbait: Boolean? = null,
    
    @SerializedName("reasoning")
    val reasoning: String? = null,
    
    @SerializedName("summary")
    val summary: String? = null,
    
    @SerializedName("emotionalTone")
    val emotionalTone: String? = null,
    
    @SerializedName("sensationalism")
    val sensationalism: String? = null,
    
    @SerializedName("manipulationTechniques")
    val manipulationTechniques: List<String>? = null,
    
    @SerializedName("factualBasis")
    val factualBasis: String? = null,
    
    @SerializedName("suggestedTitle")
    val suggestedTitle: String? = null,
    
    @SerializedName("editorNotes")
    val editorNotes: String? = null
)

/**
 * Model odpowiedzi API z listą artykułów
 */
data class FeedResponse(
    @SerializedName("articles")
    val articles: List<Article>,
    
    @SerializedName("total")
    val total: Int,
    
    @SerializedName("source")
    val source: String? = null
)
