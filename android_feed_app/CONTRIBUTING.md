# Contributing to Clickbait Feed Reader Android

Dziękujemy za zainteresowanie projektem! 🎉

## 🚀 Quick Start dla developerów

1. **Fork** repozytorium
2. **Clone** swojego forka:
   ```powershell
   git clone https://github.com/twoja-nazwa/clickbait-android-app.git
   ```
3. **Otwórz** w Android Studio
4. **Stwórz branch** na feature:
   ```powershell
   git checkout -b feature/nazwa-feature
   ```
5. **Commituj** zmiany:
   ```powershell
   git commit -m "Add: opis zmian"
   ```
6. **Push** i otwórz Pull Request

---

## 📝 Konwencje kodu

### Kotlin Style Guide

Stosujemy [oficjalny Kotlin Style Guide](https://kotlinlang.org/docs/coding-conventions.html):

```kotlin
// ✅ Dobre
fun loadArticles(limit: Int = 50) {
    viewModelScope.launch {
        repository.getArticles(limit)
    }
}

// ❌ Złe
fun loadArticles(limit:Int=50){
    viewModelScope.launch{
        repository.getArticles(limit)
    }
}
```

### Nazewnictwo

- **Classes**: PascalCase → `ArticleRepository`
- **Functions**: camelCase → `loadArticles()`
- **Constants**: UPPER_SNAKE_CASE → `BASE_URL`
- **Variables**: camelCase → `articleList`

### Composables

```kotlin
// ✅ Dobre - nazwane jak funkcje, PascalCase
@Composable
fun ArticleCard(
    article: Article,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) { ... }

// ❌ Złe
@Composable
fun articleCard(...) { ... }
```

### Package Structure

```
com.clickbait.feedreader
├── data
│   ├── api         # Network layer
│   ├── model       # Data models
│   └── repository  # Repository pattern
├── ui
│   ├── components  # Reusable UI
│   ├── screens     # Full screens
│   ├── theme       # Theme, colors, typography
│   └── viewmodel   # ViewModels
└── MainActivity.kt
```

---

## 🧪 Testing

### Unit Tests

```kotlin
// Przykład testu ViewModel
class FeedViewModelTest {
    @Test
    fun `loadArticles should update uiState to Success`() = runTest {
        // Given
        val mockRepository = mockk<ArticleRepository>()
        val viewModel = FeedViewModel(mockRepository)
        
        // When
        coEvery { mockRepository.getArticles() } returns Result.success(mockResponse)
        viewModel.loadArticles()
        
        // Then
        assertTrue(viewModel.uiState.value is FeedUiState.Success)
    }
}
```

Uruchom testy:
```powershell
./gradlew test
```

### UI Tests (Compose)

```kotlin
@Test
fun articleCard_displaysCorrectInformation() {
    composeTestRule.setContent {
        ArticleCard(
            article = sampleArticle,
            onClick = {}
        )
    }
    
    composeTestRule.onNodeWithText("Tytuł artykułu").assertIsDisplayed()
}
```

---

## 📦 Pull Request Guidelines

### Checklist przed PR:

- [ ] Kod działa lokalnie bez błędów
- [ ] Gradle build przechodzi (`./gradlew build`)
- [ ] Nie ma konfliktów z `main` branch
- [ ] Dodano testy dla nowej funkcjonalności
- [ ] Zaktualizowano dokumentację (jeśli potrzebne)
- [ ] Commit messages są jasne i opisowe

### Format PR:

**Tytuł**: `[Feature/Fix/Docs] Krótki opis`

**Opis**:
```markdown
## Zmiany
- Co zostało dodane/zmienione
- Dlaczego była potrzebna ta zmiana

## Jak przetestować
1. Krok po kroku
2. Co powinno się stać

## Screenshots (jeśli dotyczy UI)
[Dodaj screenshoty]

## Related Issues
Fixes #123
```

---

## 🐛 Zgłaszanie bugów

### Template Issue:

**Tytuł**: Krótki opis problemu

**Opis**:
```markdown
## Opis błędu
Co się dzieje vs. co powinno się dziać

## Kroki do reprodukcji
1. Otwórz aplikację
2. Kliknij X
3. Zobacz błąd

## Oczekiwane zachowanie
Co powinno się stać

## Aktualne zachowanie
Co się dzieje teraz

## Środowisko
- Android wersja: 14
- Urządzenie: Pixel 5 Emulator
- App wersja: 1.0.0

## Logi
```
Wklej logi z logcat
```

## Screenshots
[Dodaj jeśli możliwe]
```

---

## ✨ Feature Requests

Chcesz zaproponować nową funkcję?

1. Sprawdź czy ktoś już nie zaproponował (Issues)
2. Otwórz Issue z tagiem `enhancement`
3. Opisz:
   - **Problem**: Jaki problem rozwiązuje
   - **Rozwiązanie**: Jak widzisz implementację
   - **Alternatywy**: Inne rozważane opcje
   - **Dodatkowy kontekst**: Screenshots, mockupy, etc.

---

## 🎨 UI/UX Guidelines

### Material Design 3

Stosujemy Material Design 3 guidelines:
- [Material 3 Design](https://m3.material.io/)
- Używaj komponentów z `androidx.compose.material3`
- Kolory definiowane w `ui/theme/Color.kt`

### Accessibility

- Dodawaj `contentDescription` do ikon:
  ```kotlin
  Icon(
      imageVector = Icons.Default.Refresh,
      contentDescription = "Odśwież listę"
  )
  ```
- Używaj semantycznych kolorów z theme
- Testuj z TalkBack (screen reader)

### Responsive Design

- Używaj `fillMaxWidth()`, `weight()` zamiast hardcoded sizes
- Testuj na różnych rozmiarach ekranów
- Supportuj landscape orientation

---

## 🔧 Development Setup

### Wymagania

- Android Studio Hedgehog+
- JDK 17
- Android SDK 34
- Git

### Narzędzia

**Zalecane pluginy Android Studio:**
- Kotlin
- Android
- Compose UI Preview

**Linters:**
```kotlin
// Włącz w Android Studio:
// File → Settings → Editor → Inspections
// ✅ Kotlin → Style issues
// ✅ Kotlin → Probable bugs
```

---

## 📚 Resources

### Dokumentacja

- [Kotlin Docs](https://kotlinlang.org/docs/home.html)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Android Architecture](https://developer.android.com/topic/architecture)
- [Material 3](https://m3.material.io/)

### Tutoriale

- [Compose Basics](https://developer.android.com/courses/jetpack-compose/course)
- [MVVM Pattern](https://developer.android.com/topic/architecture/ui-layer)
- [Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-guide.html)

---

## 🤝 Code of Conduct

### Zasady

- ✅ Bądź uprzejmy i szanuj innych
- ✅ Konstruktywna krytyka jest mile widziana
- ✅ Pytaj jeśli czegoś nie rozumiesz
- ❌ Nie tolerujemy mowy nienawiści ani dyskryminacji

---

## 💬 Komunikacja

**Pytania?** Otwórz Discussion na GitHub

**Bug report?** Otwórz Issue

**Feature request?** Otwórz Issue z tagiem `enhancement`

---

## 🎯 Roadmap

Sprawdź [Issues](https://github.com/twoja-nazwa/clickbait-android-app/issues) z tagiem `good first issue` dla łatwych zadań na początek!

---

**Dziękujemy za wkład w projekt! 🙏**
