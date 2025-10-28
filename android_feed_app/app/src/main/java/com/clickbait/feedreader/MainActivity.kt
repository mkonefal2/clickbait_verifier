package com.clickbait.feedreader

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.ui.screens.ArticleDetailScreen
import com.clickbait.feedreader.ui.screens.FeedScreen
import com.clickbait.feedreader.ui.theme.ClickbaitFeedReaderTheme

/**
 * Główna aktywność aplikacji
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ClickbaitFeedReaderTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ClickbaitFeedApp()
                }
            }
        }
    }
}

/**
 * Główna funkcja kompozycyjna aplikacji z nawigacją
 */
@Composable
fun ClickbaitFeedApp() {
    val navController = rememberNavController()
    // Przechowywanie wybranego artykułu w pamięci zamiast przekazywać przez URL
    var selectedArticle by remember { mutableStateOf<Article?>(null) }
    
    NavHost(
        navController = navController,
        startDestination = "feed"
    ) {
        // Ekran feedu
        composable("feed") {
            FeedScreen(
                onArticleClick = { article ->
                    // Zapisz artykuł i nawiguj
                    selectedArticle = article
                    navController.navigate("article_detail")
                }
            )
        }
        
        // Ekran szczegółów artykułu
        composable("article_detail") {
            selectedArticle?.let { article ->
                ArticleDetailScreen(
                    article = article,
                    onBackClick = { navController.navigateUp() }
                )
            }
        }
    }
}
