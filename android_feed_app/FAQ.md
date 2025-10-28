# ❓ FAQ - Często zadawane pytania

## 🚀 Uruchomienie

### Q: Jak najszybciej uruchomić aplikację?
**A:** Otwórz folder w Android Studio i kliknij Run (▶️). Aplikacja działa z przykładowymi danymi bez konfiguracji backendu.

### Q: Czy potrzebuję uruchomionego backendu?
**A:** Nie! Aplikacja zawiera `SampleData.kt` z przykładowymi artykułami. Backend jest opcjonalny.

### Q: Gdzie znajdę Android Studio?
**A:** Pobierz z [developer.android.com/studio](https://developer.android.com/studio)

### Q: Jak zainstalować JDK 17?
**A:** Pobierz OpenJDK 17 z [adoptium.net](https://adoptium.net/) lub użyj JDK wbudowanego w Android Studio.

---

## 🔧 Konfiguracja

### Q: Co to znaczy `10.0.2.2`?
**A:** To specjalny adres IP dla emulatora Android, który przekierowuje na `localhost` komputera hosta.

### Q: Jak znaleźć moje IP dla telefonu fizycznego?
**A:** 
```powershell
# Windows
ipconfig
# Szukaj "IPv4 Address" w sekcji WiFi/Ethernet

# Mac/Linux
ifconfig
```

### Q: Aplikacja nie łączy się z backendem. Co robić?
**A:** 
1. Sprawdź czy backend działa: `curl http://localhost:8501`
2. Sprawdź URL w `RetrofitInstance.kt`
3. Sprawdź firewall
4. Dla telefonu: upewnij się że jest w tej samej sieci WiFi

### Q: Gdzie zmienić URL backendu?
**A:** `app/src/main/java/com/clickbait/feedreader/data/api/RetrofitInstance.kt`
```kotlin
private const val BASE_URL = "http://twoj-adres:8501/"
```

---

## 📱 Emulator i urządzenia

### Q: Nie mam emulatora. Jak go stworzyć?
**A:** 
1. Android Studio → Tools → Device Manager
2. Create Device
3. Wybierz Pixel 5
4. Wybierz system image (np. API 34)
5. Finish

### Q: Jak podłączyć fizyczny telefon?
**A:**
1. Włącz "Opcje dla deweloperów" na telefonie
   - Settings → About Phone → tap "Build number" 7 razy
2. Włącz "USB debugging"
3. Podłącz USB
4. Zaakceptuj dialog na telefonie

### Q: `adb devices` pokazuje puste. Co robić?
**A:**
```powershell
adb kill-server
adb start-server
adb devices
```

---

## 🐛 Błędy

### Q: "SDK location not found"
**A:** Stwórz plik `local.properties`:
```
sdk.dir=C\:\\Users\\TwojeImie\\AppData\\Local\\Android\\Sdk
```

### Q: "Gradle sync failed"
**A:**
1. Sprawdź internet
2. File → Invalidate Caches / Restart
3. Build → Clean Project
4. Poczekaj na pobranie zależności

### Q: "Cannot resolve symbol R"
**A:**
1. Build → Clean Project
2. Build → Rebuild Project
3. File → Invalidate Caches / Restart

### Q: Aplikacja crashuje przy starcie
**A:**
1. Sprawdź logi: `adb logcat`
2. Sprawdź czy wszystkie pliki zostały skopiowane
3. Rebuild project
4. Uninstall and reinstall app

### Q: Brak obrazków w aplikacji
**A:**
1. Sprawdź uprawnienia INTERNET w AndroidManifest (✓ już są)
2. Sprawdź URL obrazków w przykładowych danych
3. Sprawdź logi Coil: `adb logcat | Select-String "Coil"`

---

## 💻 VS Code

### Q: Czy mogę używać VS Code zamiast Android Studio?
**A:** Tak! Zobacz `QUICKSTART_VSCODE.md`. Ale Android Studio jest zalecane dla Android development.

### Q: Jak zbudować APK w VS Code?
**A:**
```powershell
.\gradlew.bat assembleDebug
```

### Q: VS Code nie rozpoznaje Kotlin
**A:** Zainstaluj rozszerzenie: `mathiasfrohlich.kotlin`

---

## 🎨 Dostosowanie

### Q: Jak zmienić kolory aplikacji?
**A:** Edytuj `app/src/main/java/com/clickbait/feedreader/ui/theme/Color.kt`

### Q: Jak zmienić nazwę aplikacji?
**A:** `app/src/main/res/values/strings.xml`
```xml
<string name="app_name">Twoja Nazwa</string>
```

### Q: Jak zmienić ikonę aplikacji?
**A:** 
1. Wygeneruj na [Android Asset Studio](https://romannurik.github.io/AndroidAssetStudio/)
2. Zastąp pliki w `app/src/main/res/mipmap-*/`

### Q: Jak dodać nowe źródła wiadomości?
**A:** W `FeedScreen.kt`:
```kotlin
val sources = listOf("Wszystkie", "onet", "rmf24", "twoje-zrodlo")
```

---

## 🔐 Bezpieczeństwo

### Q: Czy mogę opublikować tę aplikację?
**A:** Tak, ale:
1. Zmień package name
2. Dodaj własny keystore dla release
3. Nie hardcoduj URL-i (użyj BuildConfig)
4. Dodaj ProGuard rules

### Q: Jak wygenerować keystore?
**A:**
```powershell
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias
```

### Q: Czy dane są bezpieczne?
**A:** App nie przechowuje danych użytkownika. Wszystkie artykuły są publiczne.

---

## 📦 Build & Deployment

### Q: Jak zrobić release build?
**A:**
```powershell
.\gradlew.bat assembleRelease
```
APK będzie w: `app/build/outputs/apk/release/`

### Q: Jak opublikować w Google Play?
**A:**
1. Stwórz konto dewelopera ($25)
2. Przygotuj screenshoty i opis
3. Wygeneruj signed release APK/AAB
4. Upload w Google Play Console

### Q: Co to jest AAB?
**A:** Android App Bundle - nowy format, zalecany przez Google Play. Generuj przez:
```powershell
.\gradlew.bat bundleRelease
```

---

## 🧪 Testing

### Q: Jak przetestować bez backendu?
**A:** App już używa `SampleData.kt` domyślnie - działa bez backendu!

### Q: Jak dodać własne przykładowe dane?
**A:** Edytuj `data/model/SampleData.kt` i dodaj nowe artykuły do listy.

### Q: Jak uruchomić testy?
**A:**
```powershell
.\gradlew.bat test
```

---

## 📊 Performance

### Q: Aplikacja działa wolno. Co robić?
**A:**
1. Użyj release build zamiast debug
2. Sprawdź ilość danych ładowanych z API
3. Włącz ProGuard (automatycznie w release)

### Q: Jak zmniejszyć rozmiar APK?
**A:**
1. Włącz ProGuard (minification)
2. Usuń nieużywane resources
3. Użyj WebP zamiast PNG dla obrazków
4. Bundle zamiast APK

### Q: Ile pamięci zajmuje app?
**A:** Debug build: ~10-15 MB, Release build: ~5-8 MB (z ProGuard)

---

## 🔄 Updates & Maintenance

### Q: Jak zaktualizować zależności?
**A:** Zmień wersje w `app/build.gradle.kts`:
```kotlin
implementation("androidx.compose.material3:material3:1.x.x")
```

### Q: Jak sprawdzić aktualizacje zależności?
**A:**
```powershell
.\gradlew.bat dependencyUpdates
```

### Q: Jak migrować do nowej wersji Compose?
**A:** Sprawdź [release notes](https://developer.android.com/jetpack/androidx/releases/compose) i zaktualizuj BOM version.

---

## 📚 Nauka

### Q: Jestem nowy w Android. Od czego zacząć?
**A:**
1. Przeczytaj `ARCHITECTURE.md` - zrozumiesz strukturę
2. Zobacz `MainActivity.kt` - prosty entry point
3. Eksperymentuj z kolorami w `Color.kt`
4. Zmień teksty w `strings.xml`

### Q: Gdzie nauczyć się Kotlin?
**A:**
- [Kotlin Koans](https://play.kotlinlang.org/koans)
- [Android Basics in Kotlin](https://developer.android.com/courses)
- [Kotlin by Example](https://play.kotlinlang.org/byExample)

### Q: Gdzie nauczyć się Compose?
**A:**
- [Jetpack Compose Tutorial](https://developer.android.com/jetpack/compose/tutorial)
- [Compose Pathway](https://developer.android.com/courses/pathways/compose)

---

## 🚀 Przeniesienie projektu

### Q: Jak przenieść do osobnego repo?
**A:** Zobacz szczegółową instrukcję w `MIGRATION_CHECKLIST.md`

### Q: Czy muszę coś zmieniać po przeniesieniu?
**A:** Opcjonalnie:
- Zmień package name
- Zaktualizuj README
- Dodaj własną ikonę
- Zmień nazwę aplikacji

### Q: Czy projekt jest samodzielny?
**A:** Tak! Cały folder `android_feed_app` zawiera wszystko co potrzebne.

---

## 🆘 Pomoc

### Q: Gdzie szukać pomocy?
**A:**
1. Dokumentacja w tym projekcie (START.md, README.md, etc.)
2. [Stack Overflow - Android](https://stackoverflow.com/questions/tagged/android)
3. [Android Developers Community](https://developer.android.com/community)
4. [r/androiddev](https://reddit.com/r/androiddev)

### Q: Znalazłem bug. Co robić?
**A:** Otwórz Issue w głównym projekcie lub w swoim fork.

### Q: Chcę coś dodać. Jak zacząć?
**A:** Zobacz `CONTRIBUTING.md` dla guidelines.

---

## 🎯 Roadmap

### Q: Jakie funkcje można dodać?
**A:**
- Room Database (offline storage)
- WorkManager (background sync)
- Favorite articles
- Share functionality
- Dark mode
- Push notifications
- Search
- Filters
- Settings screen

### Q: Czy planujecie iOS version?
**A:** To zależy od kontrybutorów! Można zrobić w React Native, Flutter lub Swift.

---

**Nie znalazłeś odpowiedzi?**
Sprawdź pełną dokumentację lub otwórz Issue! 💬
