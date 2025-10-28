# 📱 Przewodnik Mobile - Clickbait Verifier Feed

## Responsywność interfejsu

Interfejs feeda został zoptymalizowany dla urządzeń mobilnych z następującymi funkcjami:

### 🎯 Automatyczne dostosowania

#### Breakpointy:
- **Desktop**: > 900px - Pełna funkcjonalność, dwie kolumny
- **Tablet**: 600px - 900px - Średnie dostosowania, jedna kolumna
- **Mobile**: < 600px - Maksymalne uproszczenie

### 📐 Zmiany układu na mobile

#### 1. **Statystyki** (< 900px)
- Grid automatycznie się przełącza na 2x2 lub 4x1
- Mniejsze fonty (36px → 28px na < 600px)
- Kompaktowy padding (28px → 12px)

#### 2. **Filtry i kontrolki**
- Wszystkie kontrolki układają się pionowo
- Pełna szerokość przycisków (lepsze targety dla dotyku)
- Minimum 44px wysokości (iOS guidelines)
- Większe fonty dla lepszej czytelności

#### 3. **Karty artykułów**
- **Desktop**: 2 kolumny obok siebie
- **Mobile**: 1 kolumna, pełna szerokość
- Automatyczne zmniejszanie fontów:
  - Sugerowany tytuł: 22px → 16px
  - Oryginalny tytuł: 16px → 13px
  - Wynik: 56px → 36px
  
#### 4. **Obrazki**
- Maksymalna wysokość: 280px (desktop) → 200px (mobile)
- Zawsze zachowują proporcje (object-fit: cover)
- Efekty hover wyłączone na touch devices

#### 5. **Paginacja**
- Przyciski pełnej szerokości na mobile
- Większe obszary klikalne
- Centrowane numerowanie stron

### 🎨 Optymalizacje wizualne

```css
/* Przykład zastosowanych media queries */
@media (max-width: 900px) {
  - Ukryty sidebar
  - Zmniejszone marginesy (padding: 0.5rem)
  - Fonty: 95% bazowego rozmiaru
  - Grid → flex-direction: column
}

@media (max-width: 600px) {
  - Jeszcze bardziej kompaktowy
  - Minimalne marginesy (padding: 0.25rem)
  - Maksymalna wysokość obrazu: 200px
  - Najmniejsze fonty dla UI
}
```

### 🧪 Testowanie mobile

#### Streamlit Browser (zalecane):
1. Uruchom aplikację:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run clickbait_verifier/streamlit_feed_app.py
   ```

2. Otwórz w przeglądarce (domyślnie `http://localhost:8501`)

3. **Chrome DevTools**:
   - F12 → Toggle device toolbar (Ctrl+Shift+M)
   - Wybierz urządzenie: iPhone 12 Pro, Galaxy S21, iPad Air
   - Testuj różne orientacje (portrait/landscape)

4. **Firefox Responsive Design Mode**:
   - Ctrl+Shift+M
   - Dostosuj rozdzielczość manualnie

#### Rzeczywiste urządzenie:
1. Uruchom serwer z dostępem sieciowym:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run clickbait_verifier/streamlit_feed_app.py --server.address 0.0.0.0
   ```

2. Znajdź IP komputera:
   ```powershell
   Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
   ```

3. Na telefonie otwórz: `http://[IP_KOMPUTERA]:8501`

### 💡 Wskazówki użytkowania mobile

#### Tryby widoku:
- **"Jedna kolumna"**: ✅ Zalecane dla mobile (domyślnie wymuszane)
- **"Dwie kolumny"**: Na mobile automatycznie przełącza się na jedną
- **"Kompaktowy"**: Minimalistyczny, lepszy dla małych ekranów

#### Filtry:
- Na mobile filtry układają się pionowo
- Użyj multiselect dla wielu źródeł/etykiet
- Sortowanie działa tak samo jak na desktop

#### Nawigacja:
- Przyciski ◀ / ▶ są duże i łatwe do kliknięcia
- "Przejdź do strony" - wpisz numer dla szybkiego dostępu
- Swipe nie jest wspierany (ograniczenie Streamlit)

### 🚀 Wydajność mobile

#### Optymalizacje:
- ✅ Lazy loading obrazków (przez Streamlit)
- ✅ Paginacja - tylko widoczne artykuły są renderowane
- ✅ CSS inline dla szybszego ładowania
- ✅ Minimalne zewnętrzne zależności

#### Zalecenia:
- **10 artykułów/strona** dla szybszego ładowania na 3G/4G
- Używaj filtrów zamiast "Wszystkie" na wolnych połączeniach
- Obrazy mogą ładować się wolniej - są pobierane z oryginalnych źródeł

### 🐛 Znane ograniczenia

#### Streamlit:
1. **Brak natywnych gestów**: Swipe, pinch-to-zoom nie działają
2. **Sidebar**: Całkowicie ukryty na mobile (< 900px)
3. **Reload przy każdej interakcji**: Standard Streamlit
4. **Brak offline mode**: Wymaga połączenia z serwerem

#### Workaround:
- Używaj przycisków zamiast gestów
- Wszystkie kontrolki dostępne w głównym widoku
- Session state zachowuje ustawienia między reload'ami

### 📊 Podsumowanie kompatybilności

| Funkcja | Desktop | Tablet | Mobile |
|---------|---------|--------|--------|
| Kolumny | 2 | 1-2 | 1 |
| Filtry | Poziomo | Poziomo | Pionowo |
| Statystyki | 4x1 | 2x2 | 4x1 lub 2x2 |
| Obrazy | 280px | 280px | 200px |
| Sidebar | ✅ | ✅ | ❌ |
| Touch | ➖ | ✅ | ✅ |
| Hover efekty | ✅ | ➖ | ❌ |

### 🔧 Dalsze usprawnienia (TODO)

- [ ] PWA support dla instalacji jako app
- [ ] Service worker dla offline cache
- [ ] Lazy loading obrazków z placeholder
- [ ] Infinite scroll zamiast paginacji
- [ ] Gesture support (wymaga custom JS)
- [ ] Dark mode toggle
- [ ] Zmiana orientacji: landscape optimizations

---

**Ostatnia aktualizacja**: 2025-10-28
