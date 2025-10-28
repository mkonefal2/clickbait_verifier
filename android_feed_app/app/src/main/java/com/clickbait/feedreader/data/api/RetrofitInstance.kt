package com.clickbait.feedreader.data.api

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Singleton do konfiguracji Retrofit
 */
object RetrofitInstance {
    
    // Zmień na adres swojego backendu
    // 10.0.2.2 dla emulatora, lokalny IP dla prawdziwego telefonu
    private const val BASE_URL = "http://192.168.0.178:8001/" // FastAPI server na porcie 8001
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    val api: ClickbaitApiService by lazy {
        retrofit.create(ClickbaitApiService::class.java)
    }
}
