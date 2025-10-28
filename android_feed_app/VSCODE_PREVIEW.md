# 📱 Podgląd Android w VS Code - Instrukcja

## ✅ Co zostało zainstalowane

1. **scrcpy** - narzędzie do mirror'owania ekranu Android
2. **VS Code Extensions**:
   - `ihsanis.scrcpy` - Integracja scrcpy w VS Code
   - `gfrnr.docked-android-ios-emulator` - Wbudowany emulator w panelu
   - `jawa0919.adb-helper` - Zarządzanie urządzeniami ADB

---

## 🚀 Opcja 1: Docked Emulator (w panelu VS Code)

### Krok 1: Uruchom emulator Android

```powershell
# Lista dostępnych emulatorów
emulator -list-avds

# Uruchom emulator (zastąp nazwą swojego emulatora)
emulator -avd Pixel_5_API_34
```

### Krok 2: Otwórz w VS Code

1. Naciśnij `Ctrl + Shift + P`
2. Wpisz: **"Docked Emulator: Start"**
3. Wybierz urządzenie z listy
4. Emulator pojawi się w panelu bocznym! 🎉

---

## 🚀 Opcja 2: scrcpy (w osobnym oknie)

### Automatyczne uruchomienie:

1. Uruchom emulator Android
2. W VS Code: `Ctrl + Shift + P`
3. Wpisz: **"scrcpy: Start"**
4. Ekran telefonu pojawi się w osobnym oknie

### Ręczne uruchomienie (PowerShell):

```powershell
# Podstawowe użycie
scrcpy

# Z określonym rozmiarem okna
scrcpy --max-size=1024

# Zawsze na wierzchu
scrcpy --always-on-top

# Tylko do oglądania (bez kontroli)
scrcpy --no-control

# Zapis ekranu
scrcpy --record=recording.mp4
```

---

## 🚀 Opcja 3: ADB Helper (zarządzanie urządzeniami)

### Panel ADB Helper:

1. Kliknij ikonę **ADB** w bocznym pasku VS Code
2. Zobaczysz:
   - Listę podłączonych urządzeń
   - Zainstalowane aplikacje
   - System plików urządzenia
   - Opcje mirror'owania (scrcpy)

### Użycie:

- **Device**: Wybierz urządzenie z listy
- **Apps**: Zobacz zainstalowane aplikacje
- **FileSystem**: Przeglądaj pliki na telefonie
- **Scrcpy**: Kliknij aby uruchomić mirror

---

## 🎯 Kompletny workflow

### 1. Uruchom emulator

**W terminalu VS Code:**
```powershell
# Sprawdź dostępne emulatory
cd $env:ANDROID_HOME\emulator
.\emulator.exe -list-avds

# Uruchom emulator (w tle)
Start-Process emulator -ArgumentList "-avd","Pixel_5_API_34"
```

### 2. Poczekaj aż emulator się uruchomi

```powershell
# Sprawdź czy działa
adb devices
```

Powinieneś zobaczyć:
```
List of devices attached
emulator-5554   device
```

### 3. Uruchom aplikację

```powershell
cd d:\clickbait\android_feed_app
.\gradlew.bat installDebug
adb shell am start -n com.clickbait.feedreader/.MainActivity
```

### 4. Włącz podgląd w VS Code

**Metoda A - Docked Emulator:**
- `Ctrl + Shift + P` → "Docked Emulator: Start"

**Metoda B - scrcpy:**
- `Ctrl + Shift + P` → "scrcpy: Start"

**Metoda C - ADB Helper:**
- Kliknij ikonę ADB w sidebar → Wybierz device → Kliknij "Scrcpy"

### 5. Gotowe! 🎉

Teraz widzisz:
- **Po lewej**: Kod Kotlin/Java
- **Po prawej**: Działającą aplikację Android!

---

## 🎨 Opcje konfiguracji

### scrcpy - Dostosowanie

W VS Code Settings (`Ctrl + ,`), szukaj "scrcpy":

```json
{
  "scrcpy.executable": "scrcpy",
  "scrcpy.args": [
    "--max-size=1024",
    "--window-title=Clickbait App",
    "--always-on-top"
  ]
}
```

### Docked Emulator - Pozycja

- Możesz przeciągnąć panel emulatora do dowolnego miejsca
- Split view: kod + emulator obok siebie
- Full screen: emulator na cały ekran

---

## 💡 Przydatne skróty

### scrcpy:

| Akcja | Skrót |
|-------|-------|
| Fullscreen | `Ctrl + F` |
| Obrót ekranu | `Ctrl + R` |
| Home | `Ctrl + H` |
| Back | `Ctrl + B` |
| Power | `Ctrl + P` |
| Volume up | `Ctrl + ↑` |
| Volume down | `Ctrl + ↓` |

### Kopiowanie/Wklej:

- `Ctrl + C` na komputerze → Kopiuje do schowka telefonu
- `Ctrl + V` na komputerze → Wkleja ze schowka komputera
- `Ctrl + Shift + V` → Wkleja jako tekst (bez formatowania)

---

## 🔧 Troubleshooting

### scrcpy nie startuje

```powershell
# Restart adb
adb kill-server
adb start-server

# Sprawdź urządzenia
adb devices

# Uruchom scrcpy ręcznie
scrcpy
```

### "No devices found"

1. Uruchom emulator
2. Poczekaj 30-60s aż się załaduje
3. Sprawdź: `adb devices`
4. Jeśli pusty: `adb kill-server && adb start-server`

### Docked Emulator nie działa

1. Sprawdź czy emulator jest uruchomiony: `adb devices`
2. Restart VS Code
3. Użyj scrcpy jako alternatywy

### Czarny ekran w scrcpy

```powershell
# Odblokuj ekran emulatora
adb shell input keyevent 82  # Menu
adb shell input keyevent 26  # Power
```

### Lag/opóźnienia

Zmniejsz rozdzielczość:
```powershell
scrcpy --max-size=720
```

---

## 📊 Porównanie opcji

| Funkcja | Docked Emulator | scrcpy | ADB Helper |
|---------|----------------|--------|------------|
| Wbudowany w VS Code | ✅ | ❌ | ✅ |
| Panel boczny | ✅ | ❌ | ✅ |
| Osobne okno | ❌ | ✅ | ❌ |
| Kontrola dotyku | ✅ | ✅ | ✅ |
| Nagrywanie | ❌ | ✅ | ❌ |
| Zarządzanie plikami | ❌ | ❌ | ✅ |
| Instalacja APK | ❌ | ❌ | ✅ |

**Rekomendacja:**
- **Do development**: Docked Emulator (kod + preview obok)
- **Do prezentacji**: scrcpy (osobne okno, nagrywanie)
- **Do debugowania**: ADB Helper (zarządzanie plikami, logi)

---

## 🎯 Idealny setup

```
┌─────────────────────────────────────────────────────────┐
│                     VS CODE                             │
├──────────────────┬──────────────────┬───────────────────┤
│   File Explorer  │   Code Editor    │  Docked Emulator  │
│                  │                  │                   │
│   📁 src         │   MainActivity   │   ┌─────────────┐ │
│   📁 ui          │   .kt            │   │   🤖 📱    │ │
│   📁 data        │                  │   │             │ │
│   📄 README      │   fun onCreate   │   │  Clickbait  │ │
│                  │   ...            │   │    Feed     │ │
│                  │                  │   │   Reader    │ │
│                  │                  │   │             │ │
│                  │                  │   └─────────────┘ │
├──────────────────┴──────────────────┴───────────────────┤
│   Terminal: adb logcat | grep "ClickbaitFeedReader"     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Commands

**Pełny workflow w jednym:**

```powershell
# 1. Uruchom emulator w tle
Start-Process emulator -ArgumentList "-avd","Pixel_5_API_34"

# 2. Poczekaj 30s, potem:
cd d:\clickbait\android_feed_app

# 3. Build i install
.\gradlew.bat installDebug

# 4. Uruchom app
adb shell am start -n com.clickbait.feedreader/.MainActivity

# 5. W VS Code: Ctrl+Shift+P → "Docked Emulator: Start"
```

---

## 📚 Dodatkowe zasoby

- [scrcpy GitHub](https://github.com/Genymobile/scrcpy)
- [Docked Emulator Docs](https://marketplace.visualstudio.com/items?itemName=gfrnr.docked-android-ios-emulator)
- [ADB Commands](https://developer.android.com/studio/command-line/adb)

---

**Teraz masz pełny podgląd Android w VS Code! 🎉**

Pytania? Sprawdź sekcję Troubleshooting powyżej lub FAQ.md w projekcie.
