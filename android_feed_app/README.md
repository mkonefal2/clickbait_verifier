# Clickbait Feed Reader - Android App

Aplikacja Android do przeglądania feedu artykułów z analizą poziomu clickbait, inspirowana aplikacją Squid.

## 🚀 Funkcje

- 📱 Nowoczesny interfejs w Jetpack Compose
- 🎨 Material Design 3
- 📰 Przeglądanie feedu artykułów z różnych źródeł
- 🔍 Analiza poziomu clickbait dla każdego artykułu
- 🎯 Filtrowanie po źródłach (Onet, RMF24, Focus, Nauka w Polsce)
- 📖 Szczegółowy widok artykułu z pełną treścią
- 🔄 Odświeżanie listy artykułów

## 🛠️ Technologie

- **Kotlin** - język programowania
- **Jetpack Compose** - nowoczesny UI framework
- **Material 3** - system projektowania
- **Retrofit** - komunikacja z API
- **Coil** - ładowanie obrazków
- **Coroutines** - programowanie asynchroniczne
- **ViewModel** - architektura MVVM
- **Navigation Compose** - nawigacja między ekranami

## 📋 Wymagania

- Android Studio Hedgehog (2023.1.1) lub nowsze
- JDK 17
- Android SDK 34
- Gradle 8.2
- Minimalna wersja Android: 7.0 (API 24)
- Docelowa wersja Android: 14 (API 34)

## 🔧 Instalacja

### 1. Otwórz projekt w Android Studio

```bash
# Otwórz Android Studio i wybierz:
File -> Open -> [ścieżka do android_feed_app]
```

### 2. Synchronizuj Gradle

Android Studio automatycznie zsynchronizuje zależności Gradle. Jeśli nie, kliknij:
```
File -> Sync Project with Gradle Files
```

### 3. Konfiguracja API

Edytuj plik `app/src/main/java/com/clickbait/feedreader/data/api/RetrofitInstance.kt` i zmień `BASE_URL`:

```kotlin
// Dla emulatora Android (localhost):
private const val BASE_URL = "http://10.0.2.2:8501/"

// Dla fizycznego urządzenia (zastąp IP adresem swojego komputera):
private const val BASE_URL = "http://192.168.1.XXX:8501/"
```

### 4. Uruchom aplikację

- Podłącz urządzenie Android lub uruchom emulator
- Kliknij przycisk "Run" (zielona strzałka) w Android Studio
- Lub użyj skrótu: `Shift + F10`

## 📱 Struktura projektu

```
android_feed_app/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/clickbait/feedreader/
│   │       │   ├── data/
│   │       │   │   ├── api/           # API service i Retrofit
│   │       │   │   ├── model/         # Modele danych
│   │       │   │   └── repository/    # Repository layer
│   │       │   ├── ui/
│   │       │   │   ├── components/    # Komponenty UI
│   │       │   │   ├── screens/       # Ekrany aplikacji
│   │       │   │   ├── theme/         # Kolory, typografia, theme
│   │       │   │   └── viewmodel/     # ViewModele
│   │       │   └── MainActivity.kt    # Główna aktywność
│   │       ├── res/                   # Zasoby (strings, themes, etc.)
│   │       └── AndroidManifest.xml
│   └── build.gradle.kts              # Konfiguracja modułu
├── gradle/                            # Gradle wrapper
├── build.gradle.kts                   # Konfiguracja projektu
└── settings.gradle.kts                # Ustawienia projektu
```

## 🎨 Interfejs użytkownika

### Ekran główny (Feed)
- Lista artykułów w formie kart
- Miniaturki obrazków
- Badge z poziomem clickbait
- Informacje o źródle i autorze
- Filtr po źródłach
- Przycisk odświeżania

### Ekran szczegółów
- Pełny obraz artykułu
- Kompletny tytuł i treść
- Szczegółowa analiza clickbait:
  - Wynik procentowy
  - Wizualna reprezentacja (progress bar)
  - Uzasadnienie oceny
  - Lista wskaźników clickbait
- Link do oryginalnego artykułu

## 🔄 API Backend

Aplikacja wymaga uruchomionego backendu Clickbait Verifier. Upewnij się, że:

1. Backend jest uruchomiony na porcie 8501
2. Endpoint API jest dostępny
3. CORS jest skonfigurowany (jeśli potrzebne)

Przykładowe endpointy:
- `GET /api/articles` - lista artykułów
- `GET /api/articles/{id}` - szczegóły artykułu
- `GET /api/sources/{source}/articles` - artykuły z danego źródła

## 🐛 Debugowanie

### Sprawdzanie logów

```bash
# W Android Studio:
View -> Tool Windows -> Logcat

# Lub w terminalu:
adb logcat -s "ClickbaitFeedReader"
```

### Częste problemy

1. **Błąd połączenia z API**
   - Sprawdź czy backend jest uruchomiony
   - Zweryfikuj adres IP w `RetrofitInstance.kt`
   - Dla emulatora użyj `10.0.2.2` zamiast `localhost`

2. **Gradle sync failed**
   - Sprawdź połączenie z internetem
   - Wyczyść cache: `Build -> Clean Project`
   - Invalidate caches: `File -> Invalidate Caches / Restart`

3. **Brak obrazków**
   - Sprawdź uprawnienia INTERNET w AndroidManifest
   - Zweryfikuj URL obrazków w API

## 📦 Build & Release

### Debug build

```bash
./gradlew assembleDebug
```

### Release build

```bash
./gradlew assembleRelease
```

APK będzie w: `app/build/outputs/apk/`

## 🚀 Dalszy rozwój

Możliwe rozszerzenia:
- [ ] Cachowanie artykułów (Room Database)
- [ ] Tryb offline
- [ ] Zapisywanie ulubionych artykułów
- [ ] Udostępnianie artykułów
- [ ] Powiadomienia o nowych artykułach
- [ ] Dark mode
- [ ] Personalizacja feedu
- [ ] Wyszukiwarka artykułów

## 📄 Licencja

Projekt do użytku osobistego i edukacyjnego.

## 👨‍💻 Autor

Clickbait Verifier Team
