package com.clickbait.feedreader.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.OpenInNew
import androidx.compose.material.icons.filled.Share
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.clickbait.feedreader.data.model.Article
import com.clickbait.feedreader.ui.components.ClickbaitBadge
import com.clickbait.feedreader.ui.theme.ClickbaitHigh
import com.clickbait.feedreader.ui.theme.ClickbaitLow
import com.clickbait.feedreader.ui.theme.ClickbaitMedium

/**
 * Ekran szczegółów artykułu
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ArticleDetailScreen(
    article: Article,
    onBackClick: () -> Unit
) {
    val context = LocalContext.current
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Szczegóły artykułu") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "Wstecz"
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { /* Share functionality */ }) {
                        Icon(
                            imageVector = Icons.Default.Share,
                            contentDescription = "Udostępnij"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .background(MaterialTheme.colorScheme.background)
                .verticalScroll(rememberScrollState())
        ) {
            // Obrazek artykułu
            if (!article.imageUrl.isNullOrEmpty()) {
                AsyncImage(
                    model = article.imageUrl,
                    contentDescription = null,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(250.dp),
                    contentScale = ContentScale.Crop
                )
            }
            
            // Treść artykułu
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Źródło i badge clickbait
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = article.source.uppercase(),
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    article.analysis?.let { analysis ->
                        ClickbaitBadge(
                            score = analysis.clickbaitScore,
                            isClickbait = analysis.hasClickbait
                        )
                    }
                }
                
                // Sugerowany tytuł neutralny (główny nagłówek)
                val displayTitle = article.analysis?.suggestedTitle ?: article.title
                Text(
                    text = displayTitle,
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onBackground
                )
                
                // Oryginalny tytuł (jeśli jest sugerowany)
                if (article.analysis?.suggestedTitle != null) {
                    Text(
                        text = "Oryginalny: ${article.title}",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Normal,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontStyle = FontStyle.Italic
                    )
                }
                
                // Źródło i data
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Źródło: ${article.source.uppercase()}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    article.publishedAt?.let { date ->
                        Text(
                            text = date.take(10),
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                
                Divider()
                
                // Krótkie streszczenie artykułu jako zwykły tekst
                article.analysis?.summary?.let { summary ->
                    Column(
                        modifier = Modifier.fillMaxWidth(),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Streszczenie:",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = summary,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onBackground
                        )
                    }
                }
                
                // Link do oryginału
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(article.url))
                            context.startActivity(intent)
                        },
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "🔗 Przeczytaj oryginalny artykuł",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = article.url,
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f),
                                maxLines = 2
                            )
                        }
                        Icon(
                            imageVector = Icons.Default.OpenInNew,
                            contentDescription = "Otwórz",
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }
                
                // Treść artykułu
                if (!article.content.isNullOrEmpty()) {
                    Text(
                        text = article.content,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }
                
                // Analiza clickbait
                article.analysis?.let { analysis ->
                    Divider()
                    
                    AnalysisSection(
                        clickbaitScore = analysis.clickbaitScore,
                        isClickbait = analysis.hasClickbait,
                        reasoning = analysis.reasoning,
                        emotionalTone = analysis.emotionalTone,
                        sensationalism = analysis.sensationalism,
                        manipulationTechniques = analysis.manipulationTechniques
                    )
                }
            }
        }
    }
}

/**
 * Sekcja z analizą clickbait
*/
@Composable
fun AnalysisSection(
    clickbaitScore: Double?,
    isClickbait: Boolean?,
    reasoning: String?,
    emotionalTone: String?,
    sensationalism: String?,
    manipulationTechniques: List<String>?
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(12.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "📊 Analiza Clickbait",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            
            // Wynik - karta ze wskaźnikiem jak w Streamlit
            clickbaitScore?.let { score ->
                val scoreInt = score.toInt()
                val color = when {
                    score >= 70 -> ClickbaitHigh
                    score >= 40 -> ClickbaitMedium
                    else -> ClickbaitLow
                }
                
                val label = when {
                    score >= 70 -> "Wysoki"
                    score >= 40 -> "Średni"
                    else -> "Niski"
                }
                
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surface
                    ),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Wynik (score)",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        
                        Text(
                            text = scoreInt.toString(),
                            style = MaterialTheme.typography.displayLarge,
                            fontWeight = FontWeight.Bold,
                            color = color
                        )
                        
                        Text(
                            text = "Etykieta: $label",
                            style = MaterialTheme.typography.bodyMedium,
                            color = color,
                            fontWeight = FontWeight.Medium
                        )
                        
                        // Progress bar
                        Spacer(modifier = Modifier.height(4.dp))
                        LinearProgressIndicator(
                            progress = { (score.toFloat() / 100f).coerceIn(0f, 1f) },
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(8.dp)
                                .clip(RoundedCornerShape(4.dp)),
                            color = color,
                        )
                    }
                }
            }
            
            // Uzasadnienie
            reasoning?.let {
                Text(
                    text = "🔍 Uzasadnienie:",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Charakterystyka artykułu - bardziej meaningful labels
            if (emotionalTone != null || sensationalism != null) {
                Divider(
                    modifier = Modifier.padding(vertical = 8.dp),
                    color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                )
                
                Text(
                    text = "🎭 Charakterystyka artykułu",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    emotionalTone?.let {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Emocje:",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = translateEmotionalTone(it),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                    
                    sensationalism?.let {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                text = "Wydźwięk:",
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.primary
                            )
                            Text(
                                text = translateSensationalism(it),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
            
            // Techniki manipulacji
            manipulationTechniques?.takeIf { it.isNotEmpty() }?.let { list ->
                Divider(
                    modifier = Modifier.padding(vertical = 8.dp),
                    color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                )
                
                Text(
                    text = "⚠️ Wykryte techniki:",
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = FontWeight.Bold
                )
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    list.forEach { technique ->
                        Row(
                            verticalAlignment = Alignment.Top,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Box(
                                modifier = Modifier
                                    .padding(top = 6.dp)
                                    .size(6.dp)
                                    .background(
                                        MaterialTheme.colorScheme.error,
                                        RoundedCornerShape(3.dp)
                                    )
                            )
                            Text(
                                text = translateTechnique(technique),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }
            }
            
            // editor notes removed from public UI
        }
    }
}

/**
 * Tłumaczy ton emocjonalny na polski
 */
private fun translateEmotionalTone(tone: String): String {
    return when (tone.lowercase()) {
        "neutral" -> "Neutralny"
        "positive" -> "Pozytywny"
        "negative" -> "Negatywny"
        "alarmist" -> "Alarmujący"
        "sensational" -> "Sensacyjny"
        else -> tone.capitalize()
    }
}

/**
 * Tłumaczy poziom sensacjonalizmu na polski
 */
private fun translateSensationalism(level: String): String {
    return when (level.lowercase()) {
        "not_clickbait" -> "Neutralny"
        "mild" -> "Umiarkowany"
        "strong" -> "Silny"
        "low" -> "Niski"
        "medium" -> "Średni"
        "high" -> "Wysoki"
        else -> level.capitalize()
    }
}

/**
 * Tłumaczy technikę manipulacji na bardziej zrozumiały polski
 */
private fun translateTechnique(technique: String): String {
    return when {
        technique.contains("curiosity_gap", ignoreCase = true) -> "Luka ciekawości (budzi pytania bez odpowiedzi)"
        technique.contains("sensational_phrases", ignoreCase = true) -> "Sensacyjne sformułowania"
        technique.contains("alarming", ignoreCase = true) -> "Alarmujący język"
        technique.contains("clickbait", ignoreCase = true) -> "Typowy clickbait"
        technique.contains("exaggeration", ignoreCase = true) -> "Przesada i wyolbrzymienie"
        technique.contains("emotional", ignoreCase = true) -> "Manipulacja emocjami"
        technique.contains("misleading", ignoreCase = true) -> "Wprowadzanie w błąd"
        technique.contains("question", ignoreCase = true) -> "Pytanie prowokujące"
        technique.contains("number", ignoreCase = true) -> "Wykorzystanie liczb"
        technique.contains("urgency", ignoreCase = true) -> "Wywoływanie poczucia pilności"
        else -> technique
    }
}

private fun String.capitalize(): String {
    return this.replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
}
