# Przykład użycia pola `summary` - wersja 1.2.3

## Jak LLM powinien generować streszczenie

### ✅ DOBRE przykłady:

#### Przykład 1: Artykuł naukowy
**Tytuł:** "Naukowcy dokonali przełomowego odkrycia! To zmieni wszystko"
**Treść:** "Badacze z Uniwersytetu Warszawskiego odkryli nowy mechanizm komunikacji między komórkami nerwowymi..."

```json
{
  "summary": "Badacze z Uniwersytetu Warszawskiego odkryli nowy mechanizm komunikacji między komórkami nerwowymi. Odkrycie może pomóc w leczeniu chorób neurodegeneracyjnych. Wyniki opublikowano w czasopiśmie Nature Neuroscience."
}
```

#### Przykład 2: Artykuł polityczny
**Tytuł:** "Polityk ATAKUJE rząd! Zobacz co powiedział"
**Treść:** "Poseł Jan Kowalski podczas konferencji prasowej skrytykował rządową propozycję zmian w budżecie..."

```json
{
  "summary": "Poseł Jan Kowalski podczas konferencji prasowej skrytykował rządową propozycję zmian w budżecie. Według niego zmiany są niekorzystne dla samorządów. Rząd zapowiedział odpowiedź na zarzuty."
}
```

#### Przykład 3: Artykuł o wypadku
**Tytuł:** "Tragedia na drodze! Nie żyje jedna osoba"
**Treść:** "Do wypadku doszło w czwartek rano na drodze S7 w pobliżu Krakowa. Zderzyły się dwa samochody osobowe..."

```json
{
  "summary": "Do wypadku doszło w czwartek rano na drodze S7 w pobliżu Krakowa. Zderzyły się dwa samochody osobowe. Jedna osoba zginęła, dwie zostały ranne."
}
```

---

## ❌ ZŁE przykłady (czego UNIKAĆ):

#### Przykład 1: Opisywanie analizy zamiast treści
```json
{
  "summary": "Artykuł z clickbaitowym tytułem zawiera sensacyjne frazy. Treść nie wspiera obietnic z nagłówka. Ocena: 45 punktów."
}
```
**Dlaczego źle:** Opisuje analizę clickbaitowości, nie treść artykułu!

#### Przykład 2: Cytowanie tylko tytułu
```json
{
  "summary": "Naukowcy dokonali przełomowego odkrycia! To zmieni wszystko. Artykuł opisuje badania naukowe."
}
```
**Dlaczego źle:** Nie mówi O CZYM są badania, tylko powtarza clickbaitowy tytuł!

#### Przykład 3: Zbyt ogólne
```json
{
  "summary": "Artykuł dotyczy polityki. Opisuje wypowiedzi polityków i ich reakcje na różne wydarzenia."
}
```
**Dlaczego źle:** Brak konkretów - kto, co, kiedy, dlaczego?

#### Przykład 4: Zbyt długie (>400 znaków)
```json
{
  "summary": "Badacze z Uniwersytetu Warszawskiego, we współpracy z międzynarodowym zespołem naukowców z pięciu krajów, w tym USA, Wielkiej Brytanii i Japonii, po trzech latach intensywnych badań i analiz, dokonali przełomowego odkrycia nowego mechanizmu komunikacji między komórkami nerwowymi, które może potencjalnie zmienić podejście do leczenia wielu chorób neurodegeneracyjnych, w tym choroby Alzheimera i Parkinsona, oraz innych zaburzeń neurologicznych."
}
```
**Dlaczego źle:** 447 znaków (limit: 400)! Zbyt wiele szczegółów.

---

## 📋 Checklist dla LLM:

Przed zwróceniem `summary`, upewnij się że:
- [ ] Ma 2-4 zdania
- [ ] Ma maksymalnie 400 znaków
- [ ] Opisuje TREŚĆ artykułu, nie analizę
- [ ] Jest obiektywne i neutralne
- [ ] Zawiera kluczowe fakty: kto, co, kiedy, gdzie
- [ ] NIE cytuje clickbaitowych fraz z tytułu
- [ ] NIE zawiera słów o scoringu/ocenie clickbaitu
- [ ] Jest zrozumiałe bez czytania artykułu

---

## 🔧 Implementacja w kodzie

### Python (z OpenAI API):
```python
from openai import OpenAI

client = OpenAI()

system_prompt = """
Wygeneruj obiektywne streszczenie artykułu:
- 2-4 zdania, max 400 znaków
- Opisz główny temat i kluczowe fakty
- Styl neutralny, jak w kronice prasowej
- NIE opisuj analizy clickbaitowej
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Tytuł: {title}\n\nTreść: {content}"}
    ],
    max_tokens=150
)

summary = response.choices[0].message.content
```

### Python (heurystyczny, bez LLM):
```python
import re

def generate_summary(title: str, content: str, max_chars: int = 400) -> str:
    """Generuje proste streszczenie z pierwszych zdań artykułu."""
    # Usuń HTML i znormalizuj
    clean = re.sub(r'<[^>]+>', '', content)
    sentences = re.split(r'[.!?]+\s+', clean.strip())
    
    # Filtruj elementy UI
    skip_patterns = ['udostępnij', 'facebook', 'kopiuj link', 'zobacz także']
    
    summary_parts = []
    total_len = 0
    
    for sent in sentences[:8]:
        sent = sent.strip()
        if len(sent) < 20:
            continue
        if any(p in sent.lower() for p in skip_patterns):
            continue
            
        if total_len + len(sent) > max_chars:
            break
            
        summary_parts.append(sent)
        total_len += len(sent)
        
        if len(summary_parts) >= 4:
            break
    
    result = '. '.join(summary_parts)
    if result and not result.endswith('.'):
        result += '.'
    
    return result or f"Artykuł dotyczy: {title[:300]}"
```

---

## 🧪 Testowanie

```powershell
# Test pojedynczego przypadku
.\.venv\Scripts\python.exe -c "
from scripts.analyze_batch_job_auto import _generate_summary

title = 'Szokujące odkrycie naukowców!'
content = '''
Naukowcy z MIT odkryli nowy sposób produkcji energii.
Metoda wykorzystuje bakterie morskie.
Efektywność jest 3 razy wyższa niż w tradycyjnych ogniwach.
'''

summary = _generate_summary(title, content, 30)
print('Summary:', summary)
print('Length:', len(summary))
"

# Test na prawdziwych danych
.\.venv\Scripts\python.exe scripts\analyze_batch_job_auto.py
Get-Content "reports\analysis\analysis_*.json" | 
    Select-Object -First 1 | 
    ConvertFrom-Json | 
    Select-Object title, summary
```

---

## 📚 Dokumentacja API

### Pole `summary` w JSON output:

| Właściwość | Typ | Wymagane | Opis |
|-----------|-----|----------|------|
| `summary` | `string` | ✅ Tak | Streszczenie treści artykułu (2-4 zdania, max 400 znaków) |

### Przykład pełnego outputu:
```json
{
  "id": 1761321350141,
  "source": "rmf24",
  "url": "https://example.com/article",
  "title": "Polityk ATAKUJE rząd! Zobacz co powiedział",
  "score": 26,
  "label": "mild",
  "summary": "Poseł Jan Kowalski podczas konferencji prasowej skrytykował rządową propozycję zmian w budżecie. Według niego zmiany są niekorzystne dla samorządów. Rząd zapowiedział odpowiedź na zarzuty.",
  "rationale": [...],
  "rationale_user_friendly": [...],
  "signals": {...},
  "suggestions": {...},
  "diagnostics": {...}
}
```

---

**Utworzono:** 2025-10-28  
**Wersja spec:** 1.2.3  
**Powiązany plik:** `clickbait_agent_spec_v1.1.yaml`
