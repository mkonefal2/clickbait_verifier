# Instrukcje eksportu do PDF

## Markdown Preview Enhanced (rekomendowane)

### Krok 1: Otwórz preview
- `Ctrl+Shift+V` lub `Ctrl+K V`

### Krok 2: Export do PDF
- Prawy przycisk w preview → `Chrome (Puppeteer)` → `PDF`
- Lub prawy przyciek → `HTML` → `HTML (offline)` → następnie `Ctrl+P` w przeglądarce

### Krok 3: Konfiguracja (opcjonalna)
W preview kliknij ⚙️ (Settings) i dodaj CSS:

```css
@page {
  @top-center {
    content: "Clickbait Verifier - Propozycja Pracy Inżynierskiej";
    font-size: 9pt;
    color: #666;
  }
  @bottom-center {
    content: "Strona " counter(page);
    font-size: 10pt;
    color: #666;
  }
}
```

---

## Markdown PDF Extension (alternatywa)

### Krok 1: Instalacja
`Ctrl+Shift+X` → wyszukaj "Markdown PDF" (yzane.markdown-pdf)

### Krok 2: Konfiguracja
`Ctrl+Shift+P` → "Preferences: Open Settings (JSON)"

Dodaj:
```json
{
  "markdown-pdf.format": "A4",
  "markdown-pdf.displayHeaderFooter": true,
  "markdown-pdf.headerTemplate": "<div style='font-size:9px; width:100%; text-align:center; color:#666;'>Clickbait Verifier - Propozycja Pracy Inżynierskiej</div>",
  "markdown-pdf.footerTemplate": "<div style='font-size:10px; width:100%; text-align:center; color:#666;'>Strona <span class='pageNumber'></span> z <span class='totalPages'></span></div>",
  "markdown-pdf.styles": [
    "D:/Projekty/clickbait/markdown-pdf-styles.css"
  ],
  "markdown-pdf.margin": {
    "top": "2.5cm",
    "bottom": "2cm",
    "left": "2cm",
    "right": "2cm"
  }
}
```

### Krok 3: Export
- `Ctrl+Shift+P` → "Markdown PDF: Export (pdf)"
- PDF pojawi się w tym samym katalogu

---

## Pandoc (profesjonalne dokumenty)

### Instalacja Pandoc
https://pandoc.org/installing.html

### Eksport z metadanymi
```powershell
pandoc PRACA_INZYNIERSKA_PROMOTOR.md -o praca.pdf `
  --toc `
  --number-sections `
  --pdf-engine=xelatex `
  -V geometry:margin=2.5cm `
  -V fontsize=11pt `
  -V documentclass=article `
  -V lang=pl
```

### Z custom template (zaawansowane)
```powershell
pandoc PRACA_INZYNIERSKA_PROMOTOR.md -o praca.pdf `
  --template eisvogel `
  --toc `
  --number-sections `
  --listings
```

---

## Wynik

Po eksporcie otrzymasz PDF z:
- ✅ Custom nagłówkiem: "Clickbait Verifier - Propozycja Pracy Inżynierskiej"
- ✅ Numeracją stron: "Strona X z Y"
- ✅ Automatyczną numeracją rozdziałów (1., 1.1, 1.2, etc.)
- ✅ Podziałami stron przed głównymi rozdziałami
- ✅ Profesjonalnym układem (marginesy, fonty, kolory)
- ✅ Diagramami Mermaid (wyrenderowanymi)

---

## Troubleshooting

### Diagramy Mermaid się nie renderują
Użyj Markdown Preview Enhanced zamiast Markdown PDF

### Nie widzę custom nagłówka
Upewnij się że masz YAML front matter na początku pliku

### Chcę zmienić tekst nagłówka/stopki
Edytuj `markdown-pdf-styles.css` w sekcji `@page`
