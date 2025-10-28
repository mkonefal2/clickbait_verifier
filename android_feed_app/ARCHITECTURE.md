# Architektura aplikacji Android

## Wzorzec MVVM (Model-View-ViewModel)

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI LAYER (View)                         │
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │   FeedScreen     │              │ ArticleDetailScreen│       │
│  │  - LazyColumn    │              │  - ScrollColumn   │       │
│  │  - ArticleCard   │              │  - AnalysisSection│       │
│  └────────┬─────────┘              └────────┬──────────┘       │
└───────────┼──────────────────────────────────┼──────────────────┘
            │                                  │
            │ observes StateFlow               │
            ▼                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIEWMODEL LAYER                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              FeedViewModel                           │      │
│  │  - _uiState: MutableStateFlow<FeedUiState>          │      │
│  │  - uiState: StateFlow<FeedUiState> (public)         │      │
│  │  + loadArticles()                                    │      │
│  │  + refresh()                                         │      │
│  │  + selectSource(source)                              │      │
│  └────────────────────┬─────────────────────────────────┘      │
└───────────────────────┼──────────────────────────────────────────┘
                        │ calls repository
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REPOSITORY LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │           ArticleRepository                          │      │
│  │  + getArticles(): Result<FeedResponse>              │      │
│  │  + getArticlesBySource(): Result<FeedResponse>      │      │
│  │  + getArticleById(): Result<Article>                │      │
│  └────────────────────┬─────────────────────────────────┘      │
└───────────────────────┼──────────────────────────────────────────┘
                        │ uses API service
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│                                                                 │
│  ┌──────────────────┐     ┌──────────────────────────────┐    │
│  │ RetrofitInstance │────▶│  ClickbaitApiService         │    │
│  │  - BASE_URL      │     │  + getArticles()             │    │
│  │  - okHttpClient  │     │  + getArticleById()          │    │
│  │  - retrofit      │     │  + getArticlesBySource()     │    │
│  └──────────────────┘     └────────────┬─────────────────┘    │
│                                         │                       │
│  ┌──────────────────┐                  │                       │
│  │  Data Models     │                  │ HTTP/REST             │
│  │  - Article       │◀─────────────────┘                       │
│  │  - Analysis      │                                          │
│  │  - FeedResponse  │                                          │
│  └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                        │
                        │ HTTP Request
                        ▼
        ┌───────────────────────────────┐
        │  Backend API (Streamlit/FastAPI)│
        │  http://10.0.2.2:8501         │
        └───────────────────────────────┘
```

## Przepływ danych (Data Flow)

### Ładowanie listy artykułów:

```
User Action (Pull to Refresh / App Launch)
    │
    ▼
FeedScreen → calls viewModel.refresh()
    │
    ▼
FeedViewModel.refresh()
    │
    ├─ Sets: _uiState = Loading
    │
    ├─ Calls: repository.getArticles()
    │       │
    │       ▼
    │   ArticleRepository.getArticles()
    │       │
    │       ├─ withContext(Dispatchers.IO) { ... }
    │       │
    │       ├─ Calls: api.getArticles(limit, source)
    │       │       │
    │       │       ▼
    │       │   Retrofit → HTTP GET /api/articles
    │       │       │
    │       │       ▼
    │       │   Backend API responds with JSON
    │       │       │
    │       │       ▼
    │       │   Gson parses JSON → FeedResponse
    │       │
    │       └─ Returns: Result.success(response)
    │               or Result.failure(exception)
    │
    └─ Sets: _uiState = Success(articles)
            or _uiState = Error(message)
    │
    ▼
FeedScreen observes uiState change
    │
    ├─ If Success → Display ArticleList
    ├─ If Loading → Display LoadingView
    └─ If Error → Display ErrorView
```

## Komponenty UI

### Struktura ekranu Feed:

```
Scaffold
├─ TopAppBar
│  ├─ Title: "Aktualności"
│  ├─ Filter Button (Dropdown)
│  │  └─ Sources: Wszystkie, onet, rmf24, focuspl...
│  └─ Refresh Button (IconButton)
│
└─ Content: LazyColumn
   └─ items(articles) { article ->
       ArticleCard(article) {
          ├─ Image (AsyncImage from Coil)
          ├─ Source Badge
          ├─ Clickbait Badge (colored)
          ├─ Title (bold, 3 lines max)
          ├─ Snippet (2 lines max)
          └─ Author + Date
       }
   }
```

### Nawigacja:

```
MainActivity
    │
    └─ ClickbaitFeedApp()
        │
        └─ NavHost
            │
            ├─ Route: "feed"
            │   └─ FeedScreen
            │       │ onClick: article →
            │       └─ Navigate to "article_detail/{json}"
            │
            └─ Route: "article_detail/{articleJson}"
                └─ ArticleDetailScreen
                    │ onBackClick →
                    └─ navigateUp()
```

## Stany UI (State Management)

### FeedUiState (sealed class):

```kotlin
sealed class FeedUiState {
    object Loading : FeedUiState()
    data class Success(val articles: List<Article>) : FeedUiState()
    data class Error(val message: String) : FeedUiState()
}
```

### Diagram stanów:

```
        ┌─────────┐
        │ Loading │
        └────┬────┘
             │
    ┌────────┼────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ Success │      │  Error  │
└────┬────┘      └────┬────┘
     │                │
     └────────┬───────┘
              │
              ▼
         (User Action)
              │
              ▼
        ┌─────────┐
        │ Loading │ (cycle repeats)
        └─────────┘
```

## Threading Model

```
Main Thread (UI Thread)
    │
    ├─ Compose Recomposition
    ├─ User Interactions
    └─ StateFlow observations
    
ViewModelScope (Coroutine Scope)
    │
    ├─ Launches coroutines for background work
    └─ Lifecycle-aware (cancelled when ViewModel cleared)
    
Dispatchers.IO (IO Thread Pool)
    │
    ├─ Network calls (Retrofit)
    ├─ File operations
    └─ Heavy computations
    
    Flow:
    [Main Thread] User clicks refresh
         │
         ▼
    [ViewModelScope] Launch coroutine
         │
         ▼
    [Dispatchers.IO] Network call
         │
         ▼
    [Main Thread] Update UI state
         │
         ▼
    [Compose] Recompose UI
```

## Zależności (Dependencies)

```
app
├── Jetpack Compose
│   ├── compose-bom (Bill of Materials)
│   ├── ui
│   ├── material3
│   └── navigation-compose
│
├── AndroidX Core
│   ├── activity-compose
│   ├── lifecycle (ViewModel, Runtime)
│   └── core-ktx
│
├── Networking
│   ├── retrofit2
│   ├── converter-gson
│   └── okhttp3 (logging-interceptor)
│
├── Image Loading
│   └── coil-compose
│
└── Asynchronous
    └── kotlinx-coroutines-android
```

## Build Process

```
Gradle Build Flow:

settings.gradle.kts
    │ (defines project structure)
    ▼
build.gradle.kts (root)
    │ (applies plugins, versions)
    ▼
app/build.gradle.kts
    │ (app config, dependencies)
    ▼
Gradle Sync
    │ (downloads dependencies)
    ▼
Compilation
    │ (Kotlin → JVM bytecode)
    ▼
Resource Processing
    │ (XML, images, strings)
    ▼
DEX Conversion
    │ (JVM bytecode → Dalvik bytecode)
    ▼
APK Packaging
    │ (combines DEX + resources + manifest)
    ▼
Signing
    │ (debug or release keystore)
    ▼
app-debug.apk or app-release.apk
```

## Clickbait Score Color Coding

```kotlin
score >= 0.7  → ClickbaitHigh   (Red #E53935)
score >= 0.4  → ClickbaitMedium (Orange #FB8C00)
score < 0.4   → ClickbaitLow    (Green #43A047)
score == null → ClickbaitNone   (Gray #757575)

Badge Example:
┌──────────────┐
│ 🔴 Wysoki   │  (score: 0.85)
└──────────────┘
┌──────────────┐
│ 🟠 Średni   │  (score: 0.55)
└──────────────┘
┌──────────────┐
│ 🟢 Niski    │  (score: 0.25)
└──────────────┘
```

## Error Handling Flow

```
Try-Catch in Repository:
    try {
        val response = api.getArticles()
        Result.success(response)
    } catch (e: Exception) {
        Result.failure(e)
    }

In ViewModel:
    result.fold(
        onSuccess = { response ->
            _uiState.value = Success(response.articles)
        },
        onFailure = { exception ->
            _uiState.value = Error(exception.message ?: "Unknown error")
        }
    )

In UI:
    when (uiState) {
        is Error -> ErrorView(message, onRetry)
        ...
    }
```

---

**Legenda symboli:**
- `│` - Połączenie/zależność
- `▼` - Kierunek przepływu
- `→` - Wywołanie/transformacja
- `├─` - Rozgałęzienie
- `└─` - Koniec gałęzi
