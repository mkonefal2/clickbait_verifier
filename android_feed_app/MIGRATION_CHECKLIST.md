# ✅ Checklist - Przeniesienie projektu Android

## Gotowy do przeniesienia

Folder `android_feed_app` jest w pełni samodzielny i może być przeniesiony do odrębnego repozytorium Git.

---

## 📋 Krok po kroku - Przeniesienie

### 1. Przygotowanie nowego repozytorium

- [ ] Stwórz nowe repozytorium na GitHub (np. `clickbait-android-app`)
- [ ] Sklonuj puste repo lokalnie:
  ```powershell
  git clone https://github.com/twoja-nazwa/clickbait-android-app.git
  ```

### 2. Kopiowanie plików

- [ ] Skopiuj całą zawartość folderu `android_feed_app` do nowego repo:
  ```powershell
  Copy-Item -Path "d:\clickbait\android_feed_app\*" -Destination "d:\clickbait-android-app\" -Recurse
  ```

### 3. Aktualizacja konfiguracji

- [ ] Sprawdź `.gitignore` - jest już gotowy
- [ ] Zaktualizuj `README.md` - usuń odniesienia do parent project
- [ ] Zmień namespace w `settings.gradle.kts` jeśli chcesz:
  ```kotlin
  rootProject.name = "ClickbaitAndroidApp"
  ```

### 4. Commit i push

- [ ] Inicjalizuj Git (jeśli nie było):
  ```powershell
  cd d:\clickbait-android-app
  git init
  ```
  
- [ ] Dodaj wszystkie pliki:
  ```powershell
  git add .
  git commit -m "Initial commit: Android Feed Reader app"
  ```
  
- [ ] Push do GitHub:
  ```powershell
  git branch -M main
  git remote add origin https://github.com/twoja-nazwa/clickbait-android-app.git
  git push -u origin main
  ```

### 5. Weryfikacja

- [ ] Sklonuj repo na nowej maszynie/folderze i sprawdź czy działa:
  ```powershell
  git clone https://github.com/twoja-nazwa/clickbait-android-app.git
  cd clickbait-android-app
  # Otwórz w Android Studio
  ```

---

## 🔧 Opcjonalne dostosowania po przeniesieniu

### Zmiana package name

Jeśli chcesz zmienić `com.clickbait.feedreader` na coś innego:

1. **W Android Studio**:
   - Kliknij prawym na package → Refactor → Rename
   - Wybierz "Rename package"
   - Wpisz nową nazwę (np. `com.twojanazwa.feedreader`)

2. **Ręcznie**:
   - Zmień w `AndroidManifest.xml`:
     ```xml
     <manifest xmlns:android="..." package="com.twojanazwa.feedreader">
     ```
   - Zmień w `build.gradle.kts`:
     ```kotlin
     namespace = "com.twojanazwa.feedreader"
     applicationId = "com.twojanazwa.feedreader"
     ```
   - Przenieś pliki Kotlin do nowej struktury folderów

### Zmiana nazwy aplikacji

W `app/src/main/res/values/strings.xml`:
```xml
<string name="app_name">Twoja Nazwa Aplikacji</string>
```

### Dodanie ikony aplikacji

1. Wygeneruj ikonę: [Android Asset Studio](https://romannurik.github.io/AndroidAssetStudio/)
2. Zastąp pliki w `app/src/main/res/mipmap-*/`
3. Zaktualizuj `ic_launcher_background.xml` i `ic_launcher_foreground.xml`

### Konfiguracja CI/CD

Przykład GitHub Actions (`.github/workflows/android.yml`):

```yaml
name: Android CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up JDK 17
      uses: actions/setup-java@v3
      with:
        java-version: '17'
        distribution: 'temurin'
    - name: Build with Gradle
      run: ./gradlew build
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-debug
        path: app/build/outputs/apk/debug/app-debug.apk
```

---

## 📦 Struktura po przeniesieniu

```
clickbait-android-app/          (nowe repo)
├── .github/
│   └── workflows/
│       └── android.yml         (CI/CD)
├── .gitignore                  ✅ Gotowy
├── README.md                   ✅ Gotowy
├── START.md                    ✅ Gotowy
├── QUICKSTART_VSCODE.md        ✅ Gotowy
├── BACKEND_INTEGRATION.md      ✅ Gotowy
├── ARCHITECTURE.md             ✅ Gotowy
├── LICENSE                     (dodaj jeśli chcesz)
├── app/                        ✅ Gotowe
│   ├── src/
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── gradle/                     ✅ Gotowe
├── build.gradle.kts            ✅ Gotowy
├── settings.gradle.kts         ✅ Gotowy
├── gradle.properties           ✅ Gotowy
├── gradlew                     ✅ Gotowy
└── gradlew.bat                 ✅ Gotowy
```

---

## 🔐 Przed publikacją (jeśli publiczne repo)

### Bezpieczeństwo

- [ ] Usuń hardcoded URL-e do API (użyj BuildConfig)
- [ ] Dodaj `local.properties` do `.gitignore` (już jest)
- [ ] Nie commituj keystorów produkcyjnych
- [ ] Przejrzyj kod pod kątem danych wrażliwych

### BuildConfig dla URL

W `app/build.gradle.kts`:
```kotlin
android {
    defaultConfig {
        buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8501/\"")
    }
    buildTypes {
        release {
            buildConfigField("String", "API_BASE_URL", "\"https://api.example.com/\"")
        }
    }
}
```

W `RetrofitInstance.kt`:
```kotlin
private const val BASE_URL = BuildConfig.API_BASE_URL
```

### Licencja

Dodaj plik `LICENSE` (np. MIT, Apache 2.0):
```
MIT License

Copyright (c) 2024 Twoje Imię

Permission is hereby granted, free of charge...
```

---

## 📱 Testowanie po przeniesieniu

### Checklist testów:

- [ ] Gradle sync działa bez błędów
- [ ] Aplikacja się buduje (`./gradlew assembleDebug`)
- [ ] Aplikacja się instaluje na emulatorze
- [ ] UI wyświetla się poprawnie
- [ ] Nawigacja działa (Feed → Detail → Back)
- [ ] Filtrowanie źródeł działa
- [ ] Pull-to-refresh działa
- [ ] Przykładowe dane się wyświetlają
- [ ] (Opcjonalnie) Połączenie z API działa

---

## 🚀 Release build (produkcja)

### Generowanie keystore:

```powershell
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

### Konfiguracja signing:

W `app/build.gradle.kts`:
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("../my-release-key.jks")
            storePassword = "hasło"
            keyAlias = "my-key-alias"
            keyPassword = "hasło"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(...)
        }
    }
}
```

### Build release:

```powershell
./gradlew assembleRelease
# APK w: app/build/outputs/apk/release/app-release.apk
```

---

## 📊 Metryki po przeniesieniu

Sprawdź:
- [ ] Rozmiar APK (powinien być < 10 MB dla debug)
- [ ] Liczba metod (limit: 64k, możesz sprawdzić w Android Studio)
- [ ] Build time (powinien być < 2 min)

---

## 🎯 Co dalej?

Po przeniesieniu możesz:

1. **Publikacja**:
   - Google Play Store (wymaga konta dewelopera - $25)
   - F-Droid (darmowy, open source)
   - GitHub Releases (APK do pobrania)

2. **Development**:
   - Dodaj testy jednostkowe (JUnit, Mockito)
   - Dodaj testy UI (Espresso, Compose Testing)
   - Implementuj Room Database dla offline
   - Dodaj WorkManager dla sync w tle

3. **Marketing**:
   - Stwórz screenshoty dla Google Play
   - Napisz opis aplikacji
   - Dodaj demo wideo

---

**Powodzenia! 🎉**

Masz pytania? Sprawdź dokumentację:
- [README.md](README.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [Android Developers](https://developer.android.com/)
