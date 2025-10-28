package com.clickbait.feedreader.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.ui.theme.*

/**
 * Karta artykułu w stylu Squid - elegancka i czytelna
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ArticleCard(
    article: Article,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            // Obrazek artykułu
            AsyncImage(
                model = article.imageUrl,
                contentDescription = "Obrazek artykułu: ${article.title}",
                modifier = Modifier
                    .fillMaxWidth()
                    .height(200.dp)
                    .clip(RoundedCornerShape(topStart = 12.dp, topEnd = 12.dp)),
                contentScale = ContentScale.Crop
            )
            
            // Treść karty
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                // Źródło i kategoria
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = article.source.uppercase(),
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    // Badge clickbait
                    article.analysis?.let { analysis ->
                        ClickbaitBadge(
                            score = analysis.clickbaitScore,
                            isClickbait = analysis.hasClickbait
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                // Sugerowany tytuł neutralny (główny nagłówek)
                val displayTitle = article.analysis?.suggestedTitle ?: article.title
                Text(
                    text = displayTitle,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                    maxLines = 3,
                    overflow = TextOverflow.Ellipsis,
                    color = MaterialTheme.colorScheme.onSurface
                )
                
                // Oryginalny tytuł (mniejszy, pod sugerowanym)
                if (article.analysis?.suggestedTitle != null) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Oryginalny: ${article.title}",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Normal,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Content preview
                if (!article.content.isNullOrEmpty()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = article.content,
                        style = MaterialTheme.typography.bodyMedium,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Źródło i data
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = article.source.uppercase(),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    article.publishedAt?.let { date ->
                        Text(
                            text = formatDate(date),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

/**
 * Badge pokazujący poziom clickbait
 */
@Composable
fun ClickbaitBadge(
    score: Double?,
    isClickbait: Boolean?,
    modifier: Modifier = Modifier
) {
    val (backgroundColor, textColor, text) = when {
        score == null -> Triple(ClickbaitNone, MaterialTheme.colorScheme.onSurface, "N/A")
        score >= 70 -> Triple(ClickbaitHigh, MaterialTheme.colorScheme.onError, "Wysoki")
        score >= 40 -> Triple(ClickbaitMedium, MaterialTheme.colorScheme.onTertiary, "Średni")
        else -> Triple(ClickbaitLow, MaterialTheme.colorScheme.onPrimary, "Niski")
    }
    
    Row(
        modifier = modifier
            .background(backgroundColor, RoundedCornerShape(12.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        if (isClickbait == true && score != null && score >= 0.5) {
            Icon(
                imageVector = Icons.Default.Warning,
                contentDescription = null,
                tint = textColor,
                modifier = Modifier.size(14.dp)
            )
        }
        Text(
            text = text,
            style = MaterialTheme.typography.labelSmall,
            color = textColor,
            fontWeight = FontWeight.Bold
        )
    }
}

/**
 * Formatuje datę do czytelnego formatu
 */
private fun formatDate(dateString: String): String {
    // Prosty format - możesz użyć biblioteki do formatowania dat
    return try {
        dateString.take(10)
    } catch (e: Exception) {
        dateString
    }
}
