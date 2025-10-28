# Uruchomienie projektu Android w VS Code

## Wymagania wstępne

### 1. Zainstaluj Android Studio
- Pobierz z: https://developer.android.com/studio
- Zainstaluj Android SDK, Android SDK Platform-Tools, Android SDK Build-Tools
- Zainstaluj Android Emulator (opcjonalnie)

### 2. Ustaw zmienne środowiskowe

Dodaj do zmiennych środowiskowych (System Properties -> Environment Variables):

```
ANDROID_HOME = C:\Users\TwojeImie\AppData\Local\Android\Sdk
JAVA_HOME = C:\Program Files\Java\jdk-17 (lub inna lokalizacja JDK 17)
```

Dodaj do PATH:
```
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\tools
%ANDROID_HOME%\cmdline-tools\latest\bin
%JAVA_HOME%\bin
```

### 3. Sprawdź instalację

Otwórz PowerShell i uruchom:

```powershell
# Sprawdź Java
java -version
# Powinno wyświetlić: openjdk version "17" lub nowszy

# Sprawdź Android SDK
adb version
# Powinno wyświetlić wersję Android Debug Bridge

# Sprawdź Gradle (jeśli zainstalowany globalnie)
gradle -version
```

## Uruchomienie w VS Code

### Opcja 1: Build i Install przez Gradle Wrapper

1. Otwórz terminal w VS Code (Ctrl + `)
2. Przejdź do folderu projektu:
   ```powershell
   cd android_feed_app
   ```

3. Build Debug APK:
   ```powershell
   .\gradlew.bat assembleDebug
   ```

4. Uruchom emulator Android lub podłącz urządzenie

5. Zainstaluj APK:
   ```powershell
   .\gradlew.bat installDebug
   ```

6. Uruchom aplikację:
   ```powershell
   adb shell am start -n com.clickbait.feedreader/.MainActivity
   ```

### Opcja 2: Używając zadań VS Code

1. Naciśnij `Ctrl + Shift + P`
2. Wpisz: `Tasks: Run Task`
3. Wybierz: `Build Debug APK`
4. Po zakończeniu wybierz: `Install Debug APK`
5. Wybierz: `Run on Emulator`

### Opcja 3: Android Studio (zalecane dla debugowania)

1. Otwórz Android Studio
2. File -> Open -> wybierz folder `android_feed_app`
3. Poczekaj na synchronizację Gradle
4. Kliknij przycisk "Run" (zielona strzałka)

## Podgląd w VS Code

### Przeglądanie kodu
- Otwórz folder `android_feed_app` w VS Code
- Kod Kotlin znajduje się w: `app/src/main/java/com/clickbait/feedreader/`
- Zainstalowane rozszerzenia zapewnią:
  - Podświetlanie składni Kotlin
  - Podstawowe auto-uzupełnianie
  - Przeglądanie struktury projektu

### Logowanie
- Otwórz terminal
- Uruchom:
  ```powershell
  adb logcat | Select-String "ClickbaitFeedReader"
  ```

## Emulator Android

### Uruchomienie emulatora

1. Lista dostępnych emulatorów:
   ```powershell
   emulator -list-avds
   ```

2. Uruchom emulator:
   ```powershell
   emulator -avd Pixel_5_API_34
   ```
   (zastąp `Pixel_5_API_34` nazwą swojego emulatora)

### Tworzenie nowego emulatora

1. Uruchom Android Studio
2. Tools -> Device Manager
3. Create Device
4. Wybierz urządzenie (np. Pixel 5)
5. Wybierz system (np. API 34 - Android 14)
6. Finish

## Testowanie połączenia z backendem

### Uruchom backend
1. Wróć do głównego folderu clickbait:
   ```powershell
   cd ..
   python -m streamlit run clickbait_verifier/streamlit_app.py
   ```

2. Backend powinien być dostępny na: http://localhost:8501

### Konfiguracja aplikacji Android

#### Dla emulatora:
- URL w aplikacji: `http://10.0.2.2:8501/`
- (10.0.2.2 to specjalny adres dla localhost w emulatorze)

#### Dla fizycznego urządzenia:
1. Sprawdź IP komputera:
   ```powershell
   ipconfig
   ```
   Szukaj: `IPv4 Address` w sekcji WiFi/Ethernet

2. Zmień w pliku `app/src/main/java/com/clickbait/feedreader/data/api/RetrofitInstance.kt`:
   ```kotlin
   private const val BASE_URL = "http://192.168.1.XXX:8501/"
   ```
   (zastąp XXX swoim IP)

3. Upewnij się, że telefon i komputer są w tej samej sieci WiFi

## Rozwiązywanie problemów

### Błąd: "SDK location not found"
- Utwórz plik `local.properties` w folderze `android_feed_app`:
  ```
  sdk.dir=C\:\\Users\\TwojeImie\\AppData\\Local\\Android\\Sdk
  ```

### Błąd: "Gradle sync failed"
- Otwórz projekt w Android Studio i pozwól na automatyczną synchronizację
- Lub uruchom w terminalu: `.\gradlew.bat --refresh-dependencies`

### Błąd: "No connected devices"
- Uruchom emulator lub podłącz telefon
- Sprawdź: `adb devices`
- Jeśli puste, restart adb: `adb kill-server` i `adb start-server`

### Aplikacja nie łączy się z API
- Sprawdź czy backend działa
- Sprawdź URL w `RetrofitInstance.kt`
- Sprawdź logi: `adb logcat | Select-String "Retrofit"`
- Upewnij się, że firewall nie blokuje połączenia

## Struktura projektu dla VS Code

```
android_feed_app/
├── .vscode/
│   ├── launch.json       # Konfiguracja debugowania
│   ├── settings.json     # Ustawienia projektu
│   └── tasks.json        # Zadania build/run
├── app/
│   └── src/main/java/com/clickbait/feedreader/
│       ├── data/         # Warstwa danych (API, modele, repository)
│       ├── ui/           # Warstwa UI (ekrany, komponenty, ViewModele)
│       └── MainActivity.kt
├── README.md             # Dokumentacja projektu
├── QUICKSTART_VSCODE.md  # Ten plik
└── build.gradle.kts      # Konfiguracja Gradle
```

## Przydatne komendy

```powershell
# Build
.\gradlew.bat assembleDebug
.\gradlew.bat assembleRelease

# Install
.\gradlew.bat installDebug
.\gradlew.bat installRelease

# Clean
.\gradlew.bat clean

# Wyświetl zależności
.\gradlew.bat dependencies

# Lista zadań
.\gradlew.bat tasks

# ADB
adb devices                           # Lista urządzeń
adb install app-debug.apk             # Instalacja APK
adb uninstall com.clickbait.feedreader # Odinstalowanie
adb logcat                            # Logi
adb shell am start -n com.clickbait.feedreader/.MainActivity  # Uruchom app
```

## Następne kroki

1. Zmodyfikuj UI w plikach Compose
2. Dodaj nowe funkcje (np. cache, zapisywanie ulubionych)
3. Dostosuj kolory w `ui/theme/Color.kt`
4. Dodaj więcej źródeł wiadomości
5. Zaimplementuj offline mode

## Zasoby

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [Jetpack Compose](https://developer.android.com/jetpack/compose)
- [Material Design 3](https://m3.material.io/)
- [Android Developers](https://developer.android.com/)
