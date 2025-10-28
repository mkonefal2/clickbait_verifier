# 🚀 Szybki Start - Android Feed App

## Najszybsza droga do uruchomienia

### 1️⃣ Otwórz w Android Studio (5 min)

1. Uruchom **Android Studio**
2. Kliknij **File → Open**
3. Wybierz folder: `d:\clickbait\android_feed_app`
4. Poczekaj na synchronizację Gradle (może potrwać 2-3 min przy pierwszym otwarciu)

### 2️⃣ Uruchom emulator lub podłącz telefon

**Opcja A - Emulator (jeśli masz):**
- W Android Studio: **Tools → Device Manager**
- Uruchom dowolny emulator (np. Pixel 5)

**Opcja B - Telefon fizyczny:**
- Włącz tryb dewelopera na telefonie
- Podłącz przez USB
- Zaakceptuj debugowanie USB

### 3️⃣ Uruchom aplikację

Kliknij zielony przycisk **▶️ Run** w Android Studio

🎉 **Gotowe!** Aplikacja uruchomi się z przykładowymi danymi.

---

## Połączenie z backendem (opcjonalnie)

Jeśli chcesz prawdziwe dane z backendu:

### 1. Uruchom backend
```powershell
# W folderze głównym clickbait
python -m streamlit run clickbait_verifier/streamlit_app.py
```

### 2. Zmień URL w aplikacji
Otwórz: `app/src/main/java/com/clickbait/feedreader/data/api/RetrofitInstance.kt`

Dla **emulatora**:
```kotlin
private const val BASE_URL = "http://10.0.2.2:8501/"
```

Dla **telefonu** (znajdź swoje IP przez `ipconfig`):
```kotlin
private const val BASE_URL = "http://192.168.1.XXX:8501/"
```

### 3. Przebuduj aplikację
Kliknij: **Build → Rebuild Project**

---

## VS Code (dla zaawansowanych)

Jeśli wolisz VS Code zamiast Android Studio:

1. Zainstaluj Android SDK i JDK 17
2. Ustaw zmienne środowiskowe (`ANDROID_HOME`, `JAVA_HOME`)
3. W terminalu:
```powershell
cd d:\clickbait\android_feed_app
.\gradlew.bat assembleDebug
.\gradlew.bat installDebug
adb shell am start -n com.clickbait.feedreader/.MainActivity
```

Zobacz: [`QUICKSTART_VSCODE.md`](QUICKSTART_VSCODE.md) dla szczegółów.

---

## Troubleshooting

**"SDK location not found"**
→ Utwórz `local.properties`:
```
sdk.dir=C\:\\Users\\TwojeImie\\AppData\\Local\\Android\\Sdk
```

**"Gradle sync failed"**
→ Sprawdź internet, poczekaj na pobranie zależności

**"No connected devices"**
→ Uruchom emulator lub podłącz telefon, sprawdź `adb devices`

**Aplikacja nie pokazuje danych**
→ Używaj przykładowych danych z `SampleData.kt` (domyślnie włączone)

---

## Co dalej?

- 📖 Przeczytaj: [`README.md`](README.md) - pełna dokumentacja
- 🔗 Zobacz: [`BACKEND_INTEGRATION.md`](BACKEND_INTEGRATION.md) - integracja z API
- 💻 Sprawdź: [`QUICKSTART_VSCODE.md`](QUICKSTART_VSCODE.md) - rozwój w VS Code

---

**Gotowy projekt do przeniesienia!**
Cały folder `android_feed_app` jest samodzielny i możesz go przenieść do osobnego repozytorium. 🎯
