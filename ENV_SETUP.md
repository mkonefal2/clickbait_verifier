# 📄 Konfiguracja klucza API w pliku .env

## ✅ **Gotowe!** Plik `.env` został utworzony.

### 🔧 **Jak skonfigurować:**

1. **Otwórz plik `.env`** w głównym katalogu projektu
2. **Zamień** `sk-your-actual-api-key-here` na prawdziwy klucz OpenAI
3. **Zapisz plik**

### 📝 **Przykład pliku `.env`:**
```
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-abc123def456ghi789...

# Opcjonalne ustawienia:
# OPENAI_MODEL=gpt-4o-mini
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### 🔑 **Jak uzyskać klucz API:**

1. Idź na https://platform.openai.com/api-keys
2. Zaloguj się lub załóż konto
3. Kliknij **"Create new secret key"**
4. Skopiuj klucz (zaczyna się od `sk-`)
5. Wklej do pliku `.env`

### ✨ **Korzyści pliku `.env`:**

- ✅ Klucz automatycznie ładowany przy starcie
- ✅ Bezpieczne (plik w `.gitignore`)
- ✅ Łatwe do zarządzania
- ✅ Działa ze wszystkimi narzędziami

### 🚀 **Test konfiguracji:**

```bash
# Test czy klucz się ładuje
.venv\Scripts\python.exe -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENAI_API_KEY')))"

# Uruchom analizę (użyje klucz z .env)
.venv\Scripts\python.exe -m clickbait_verifier.main --analyze-all --limit 3
```

### 🔒 **Bezpieczeństwo:**

- ❌ **NIE** commituj pliku `.env` do git
- ✅ Plik `.env` jest już w `.gitignore` 
- ✅ Używaj różnych kluczy dla dev/prod
- ✅ Regularnie regeneruj klucze API

---

**Po skonfigurowaniu klucza w `.env` system będzie automatycznie go używał!** 🎉