# 🔗 Integracja z backendem Clickbait Verifier

Ten dokument opisuje jak połączyć aplikację Android z backendem.

## Backend API Endpoints (do zaimplementowania)

Aplikacja Android oczekuje następujących endpointów REST API:

### 1. Pobierz listę artykułów
```
GET /api/articles?limit=50&source=onet
```

**Response:**
```json
{
  "articles": [
    {
      "url": "https://...",
      "title": "Tytuł artykułu",
      "source": "onet",
      "scraped_at": "2024-01-15T10:30:00",
      "image_url": "https://...",
      "snippet": "Krótki opis...",
      "author": "Jan Kowalski",
      "category": "News",
      "full_content": "Pełna treść artykułu...",
      "analysis": {
        "clickbait_score": 0.85,
        "is_clickbait": true,
        "reasoning": "Uzasadnienie...",
        "indicators": ["Wskaźnik 1", "Wskaźnik 2"],
        "analyzed_at": "2024-01-15T10:31:00"
      }
    }
  ],
  "total": 150,
  "source": "onet"
}
```

### 2. Pobierz artykuły z konkretnego źródła
```
GET /api/sources/{source}/articles?limit=50
```

### 3. Pobierz szczegóły artykułu (opcjonalne)
```
GET /api/articles/{id}
```

## Dodanie endpointów do backendu Streamlit

Streamlit nie jest idealnym narzędziem do REST API. Zalecamy dodanie FastAPI:

### Opcja A: FastAPI obok Streamlit

Stwórz `clickbait_verifier/api_server.py`:

```python
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

app = FastAPI()

# CORS dla aplikacji mobilnej
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/articles")
async def get_articles(
    limit: int = Query(50, ge=1, le=200),
    source: str = Query(None)
):
    """Pobierz listę artykułów"""
    # Załaduj z plików JSON w reports/scraped/
    scraped_dir = Path("reports/scraped")
    analysis_dir = Path("reports/analysis")
    
    articles = []
    
    # Implementuj logikę ładowania
    # ... (kod do dodania)
    
    return {
        "articles": articles,
        "total": len(articles),
        "source": source
    }

@app.get("/api/sources/{source}/articles")
async def get_articles_by_source(
    source: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Pobierz artykuły z konkretnego źródła"""
    return await get_articles(limit=limit, source=source)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Uruchom API:
```powershell
pip install fastapi uvicorn
python clickbait_verifier/api_server.py
```

Zmień w aplikacji Android:
```kotlin
// RetrofitInstance.kt
private const val BASE_URL = "http://10.0.2.2:8000/"  // Port 8000 dla FastAPI
```

### Opcja B: Streamlit API (prostsze, ale ograniczone)

Możesz użyć st.experimental_get_query_params() ale to nie jest pełne REST API.

### Opcja C: Użyj danych testowych

W `FeedViewModel.kt` zmień:

```kotlin
init {
    // Zamiast ładować z API, użyj przykładowych danych
    _uiState.value = FeedUiState.Success(SampleData.sampleArticles)
}
```

## Struktura danych w aplikacji

Model `Article.kt` oczekuje:

```kotlin
data class Article(
    val url: String,                    // WYMAGANE
    val title: String,                  // WYMAGANE
    val source: String,                 // WYMAGANE
    val scrapedAt: String?,             // ISO 8601 format
    val imageUrl: String?,              // URL do obrazka
    val snippet: String?,               // Krótki opis
    val author: String?,                // Autor
    val category: String?,              // Kategoria
    val fullContent: String?,           // Pełna treść
    val analysis: Analysis?             // Analiza clickbait
)

data class Analysis(
    val clickbaitScore: Double?,        // 0.0 - 1.0
    val isClickbait: Boolean?,          // true/false
    val reasoning: String?,             // Uzasadnienie
    val indicators: List<String>?,      // Lista wskaźników
    val analyzedAt: String?             // ISO 8601 format
)
```

## Konfiguracja adresów

### Dla emulatora Android:
```kotlin
private const val BASE_URL = "http://10.0.2.2:8501/"
```
`10.0.2.2` to specjalny adres dla localhost w emulatorze Android.

### Dla fizycznego urządzenia:
1. Sprawdź IP komputera: `ipconfig` (Windows) lub `ifconfig` (Mac/Linux)
2. Zmień na:
```kotlin
private const val BASE_URL = "http://192.168.1.XXX:8501/"
```
3. Urządzenie musi być w tej samej sieci WiFi co komputer

### Dla środowiska produkcyjnego:
```kotlin
private const val BASE_URL = "https://twoja-domena.com/"
```

## Testowanie połączenia

### Test 1: Sprawdź dostępność API
```powershell
# Z komputera
curl http://localhost:8501/api/articles

# Z emulatora (przez adb)
adb shell curl http://10.0.2.2:8501/api/articles
```

### Test 2: Logi w aplikacji
Sprawdź logi Retrofit:
```powershell
adb logcat | Select-String "OkHttp"
```

### Test 3: Przykładowe dane
Użyj `SampleData.kt` do testowania bez backendu:

```kotlin
// W FeedViewModel.kt
private fun loadArticlesFromSampleData() {
    _uiState.value = FeedUiState.Success(SampleData.sampleArticles)
}
```

## Bezpieczeństwo

### Dla rozwoju:
- ✅ HTTP jest OK
- ✅ `usesCleartextTraffic="true"` w AndroidManifest

### Dla produkcji:
- ❌ Usuń `usesCleartextTraffic`
- ✅ Użyj HTTPS
- ✅ Dodaj Network Security Config
- ✅ Implementuj SSL pinning

## Rozwiązywanie problemów

### Błąd: "Failed to connect"
1. Sprawdź czy backend działa: `curl http://localhost:8501`
2. Sprawdź firewall Windows
3. Sprawdź czy port jest otwarty: `netstat -an | Select-String "8501"`

### Błąd: "Unable to resolve host"
1. Sprawdź połączenie internetowe emulatora
2. Spróbuj: `adb shell ping 8.8.8.8`
3. Restart emulatora

### Błąd: "Connection timeout"
1. Zwiększ timeout w `RetrofitInstance.kt`:
```kotlin
.connectTimeout(60, TimeUnit.SECONDS)
.readTimeout(60, TimeUnit.SECONDS)
```

### Błąd: JSON parsing
1. Sprawdź format odpowiedzi backendu
2. Porównaj z modelem `Article.kt`
3. Sprawdź logi: `adb logcat | Select-String "Gson"`

## Przykład pełnej implementacji FastAPI

Zobacz `examples/fastapi_backend_example.py` w tym folderze dla pełnego przykładu.

## Dalsze kroki

1. ✅ Uruchom backend (Streamlit lub FastAPI)
2. ✅ Skonfiguruj BASE_URL w aplikacji
3. ✅ Zbuduj i zainstaluj APK
4. ✅ Przetestuj połączenie
5. ✅ Sprawdź logi w przypadku problemów

Powodzenia! 🚀
