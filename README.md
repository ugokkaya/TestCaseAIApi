# TestCaseAIApi

FastAPI ile basit bir API; verilen gereksinim ve framework bilgisine gore test senaryosu ve otomasyon kodu uretir.

## Gereksinimler
- Python 3.10+ (onerilir)
- `pip`

## Kurulum
1. Sanal ortam olusturun ve aktif edin:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. Bagimliliklari yukleyin:
   ```bash
   pip install fastapi uvicorn pydantic requests
   ```

## Calistirma
```bash
uvicorn app:app --reload --port 8000
```

## API
### POST `/api/generate`
Istek ornegi:
```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirement": "Googlea git ve arama yap",
    "framework": "playwright",
    "model": "qwen"
  }'
```

Ornek cevap:
```json
{
  "model_used": "qwen2.5-coder:7b",
  "target_framework": "playwright",
  "result": {
    "test_case": {
      "title": "...",
      "steps": ["..."],
      "expected": "..."
    },
    "script_code": "...",
    "script": "playwright"
  }
}
```

## Notlar
- Model secimi: `model` alaninda `qwen`, `deepseek`, `llama` gibi anahtar kelimeler geciyorsa ilgili model secilir; bos ise varsayilan model kullanilir.
- LLM endpointi `app.py` icindeki `OLLAMA_URL` degiskeninden ayarlanir.
