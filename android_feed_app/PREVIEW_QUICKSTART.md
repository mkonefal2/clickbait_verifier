# 🚀 Szybki Start - Podgląd Android w VS Code

## ⚡ Super Szybki Setup (5 minut)

### Krok 1: Zainstaluj Android Studio
Jeśli nie masz jeszcze Android Studio:

1. Pobierz: https://developer.android.com/studio
2. Zainstaluj (wybierz wszystkie komponenty)
3. Podczas pierwszego uruchomienia zainstaluje się Android SDK

### Krok 2: Dodaj Android SDK do PATH

**Otwórz PowerShell jako Administrator i uruchom:**

```powershell
# Znajdź ścieżkę do Android SDK (zwykle):
$androidSdk = "$env:LOCALAPPDATA\Android\Sdk"

# Dodaj do PATH (tymczasowo dla tej sesji)
$env:PATH += ";$androidSdk\platform-tools;$androidSdk\emulator;$androidSdk\cmdline-tools\latest\bin"

# Sprawdź czy działa
adb version
```

**Aby dodać permanentnie:**

1. Naciśnij `Win + X` → "System"
2. "Advanced system settings" → "Environment Variables"
3. W "System variables" znajdź `Path` → "Edit"
4. Dodaj:
   ```
   C:\Users\TwojeImie\AppData\Local\Android\Sdk\platform-tools
   C:\Users\TwojeImie\AppData\Local\Android\Sdk\emulator
   ```
5. OK → Restart PowerShell

### Krok 3: Uruchom emulator

**Opcja A - Przez Android Studio (najłatwiej):**
1. Otwórz Android Studio
2. Tools → Device Manager
3. Kliknij ▶️ przy jednym z emulatorów
4. Poczekaj aż się uruchomi (~30s)

**Opcja B - Przez terminal:**
```powershell
# Lista emulatorów
emulator -list-avds

# Uruchom (zastąp nazwą swojego emulatora)
emulator -avd Pixel_5_API_34
```

### Krok 4: Włącz podgląd w VS Code

Masz 3 opcje - wybierz najlepszą dla Ciebie:

#### 🎯 Opcja 1: Docked Emulator (ZALECANE)
**Wbudowany panel w VS Code - kod obok emulatora**

1. `Ctrl + Shift + P`
2. Wpisz: `Docked Emulator: Start`
3. Wybierz urządzenie
4. Gotowe! 🎉

#### 🎯 Opcja 2: scrcpy (Osobne okno)
**Świetne do prezentacji i nagrywania**

1. `Ctrl + Shift + P`
2. Wpisz: `scrcpy: Start`
3. Pojawi się osobne okno z ekranem telefonu

Lub w terminalu:
```powershell
scrcpy
```

#### 🎯 Opcja 3: ADB Helper (Panel zarządzania)
**Najlepsze do debugowania**

1. Kliknij ikonę "ADB" w lewym pasku VS Code
2. Zobaczysz podłączone urządzenia
3. Kliknij urządzenie → "Start Scrcpy"

---

## 🎮 Testuj aplikację

### 1. Build i install:

```powershell
cd d:\clickbait\android_feed_app
.\gradlew.bat installDebug
```

### 2. Uruchom aplikację:

```powershell
adb shell am start -n com.clickbait.feedreader/.MainActivity
```

### 3. Zobacz w podglądzie!

Aplikacja pojawi się w emulatorze, który widzisz w VS Code! 🎉

---

## 🔥 Wszystko w jednej komendzie

Kopiuj i wklej:

```powershell
# KROK 1: Uruchom emulator w tle (potrzebne Android Studio)
Start-Process -FilePath "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -ArgumentList "-avd","Pixel_5_API_34" -WindowStyle Hidden

# KROK 2: Poczekaj 30s aż emulator się uruchomi
Start-Sleep -Seconds 30

# KROK 3: Build i install aplikację
cd d:\clickbait\android_feed_app
.\gradlew.bat installDebug

# KROK 4: Uruchom aplikację
Start-Sleep -Seconds 3
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" shell am start -n com.clickbait.feedreader/.MainActivity

# KROK 5: W VS Code: Ctrl+Shift+P → "Docked Emulator: Start"
Write-Host "✅ Gotowe! Teraz w VS Code naciśnij Ctrl+Shift+P i wybierz 'Docked Emulator: Start'" -ForegroundColor Green
```

---

## 💡 Nie masz Android Studio?

### Plan B: Użyj tylko ADB i scrcpy (bez emulatora)

Jeśli masz fizyczny telefon Android:

1. **Włącz USB Debugging na telefonie:**
   - Settings → About Phone
   - Tap "Build Number" 7 razy
   - Settings → Developer Options
   - Włącz "USB Debugging"

2. **Podłącz telefon przez USB**

3. **W terminalu:**
   ```powershell
   scrcpy
   ```

4. **Gotowe!** Widzisz ekran telefonu w VS Code

---

## 🎨 Layout w VS Code

Po uruchomieniu masz:

```
┌───────────────────────────────────────────────┐
│          VS CODE WINDOW                       │
├──────────┬──────────────┬─────────────────────┤
│ Explorer │ Code Editor  │  Docked Emulator    │
│          │              │                     │
│ 📁 src   │ MainActivity │  ┌───────────────┐  │
│ 📁 ui    │              │  │  📱 Android   │  │
│ 📁 data  │ @Composable  │  │               │  │
│          │ fun Feed()   │  │  Clickbait    │  │
│          │              │  │  Feed Reader  │  │
│          │              │  │               │  │
│          │              │  └───────────────┘  │
├──────────┴──────────────┴─────────────────────┤
│ Terminal: adb logcat                          │
└───────────────────────────────────────────────┘
```

Możesz:
- Pisać kod po lewej
- Widzieć zmiany po prawej
- Debugować w terminalu na dole

---

## 🆘 Problem? Szybkie rozwiązania

### "adb not found"
```powershell
# Ustaw PATH tymczasowo
$env:PATH += ";$env:LOCALAPPDATA\Android\Sdk\platform-tools"
adb version
```

### "No devices found"
```powershell
# Sprawdź czy emulator działa
adb devices

# Jeśli pusty, restart:
adb kill-server
adb start-server
```

### Emulator nie uruchamia się
1. Otwórz Android Studio
2. Tools → Device Manager
3. Jeśli nie ma emulatorów: "Create Device"
4. Wybierz Pixel 5, API 34, Finish

### scrcpy czarny ekran
```powershell
# Odblokuj ekran
adb shell input keyevent 82
```

---

## 📱 Hot Reload (aktualizacja na żywo)

Po zmianach w kodzie:

```powershell
# Quick reinstall
.\gradlew.bat installDebug
adb shell am start -n com.clickbait.feedreader/.MainActivity
```

Lub użyj Android Studio dla prawdziwego hot reload!

---

## ✅ Checklist

- [ ] Zainstalowane Android Studio
- [ ] Dodane ścieżki do PATH
- [ ] Uruchomiony emulator
- [ ] Zainstalowane rozszerzenia VS Code (✅ już są!)
- [ ] Zainstalowane scrcpy (✅ już jest!)
- [ ] Otwarte Docked Emulator w VS Code

---

## 🎯 Najlepszy workflow

1. **Lewy monitor**: VS Code z kodem
2. **Prawy monitor**: Android Studio z Device Manager
3. **W VS Code**: Docked Emulator w panelu bocznym
4. **Terminal**: adb logcat dla logów

Albo wszystko w VS Code:
- Split view: kod | emulator
- Terminal na dole z logami

---

## 🚀 Następne kroki

Po uruchomieniu podglądu:

1. Eksperymentuj z kodem
2. Zobacz zmiany od razu na emulatorze
3. Debuguj przez logi: `adb logcat | Select-String "ClickbaitFeedReader"`
4. Testuj różne scenariusze

---

**Potrzebujesz pomocy?**
- Zobacz pełny przewodnik: `VSCODE_PREVIEW.md`
- FAQ: `FAQ.md`
- Troubleshooting: sekcja powyżej

**Powodzenia! 🎉**
