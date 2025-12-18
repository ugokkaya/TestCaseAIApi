import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

OLLAMA_URL = "https://yyzx6tvepstx5b-11434.proxy.runpod.net/api/generate"
AVAILABLE_MODELS = {
    "qwen": "qwen2.5-coder:7b",
    "deepseek": "deepseek-coder:6.7b",
    "llama": "llama3.1:8b",
}
DEFAULT_MODEL = "qwen2.5-coder:7b"

app = FastAPI()

class Req(BaseModel):
    requirement: str
    framework: str = "playwright"
    model: str | None = None

FRAMEWORK_EXAMPLES = {
    "playwright": {
        "code": "await page.goto('https://google.com'); await page.fill('input[name=q]', 'test'); await page.press('input[name=q]', 'Enter');",
        "desc": "Playwright (Async/Python)"
    },
    "selenium": {
        "code": "driver.get('https://google.com'); driver.find_element(By.NAME, 'q').send_keys('test', Keys.RETURN);",
        "desc": "Selenium (Python)"
    },
    "cypress": {
        "code": "cy.visit('https://google.com'); cy.get('input[name=q]').type('test{enter}');",
        "desc": "Cypress (JS)"
    }
}

# --- PROMPT TEMPLATE ---
PROMPT_TMPL = """
Sen uzman bir QA Otomasyon Mühendisisin.
GÖREV: Aşağıdaki gereksinim için **{fw_name}** kütüphanesini kullanarak test otomasyon kodu yaz.

KURALLAR:
1. Yanıtın SADECE geçerli bir JSON objesi olmalıdır.
2. "test_case" içeriği (title, steps, expected) TAMAMEN TÜRKÇE olmalıdır.
3. "script_code" alanı BOŞ KALAMAZ.
4. **ÖNEMLİ:** Aşağıdaki örneği kopyalama! Sadece formatı örnek al, kodu verilen gereksinime ({req}) göre sıfırdan yaz.

ÖRNEK GİRDİ (Formatı anlaman için):
Gereksinim: Google'a git ve arama yap.
Çıktı Formatı:
{{
  "test_case": {{
    "title": "Google Arama Testi",
    "steps": ["Google anasayfasına git", "...", "..."],
    "expected": "..."
  }},
  "script_code": "{example_code}", 
  "script": "{fw_slug}"
}}

---------------------------------------------------
ŞİMDİ GERÇEK SENARYOYU YAZ:

Gereksinim: {req}
Framework: {fw_name}
"""

@app.post("/api/generate")
def generate(data: Req):
    key_model = data.model.lower() if data.model else "default"
    model_name = next((v for k, v in AVAILABLE_MODELS.items() if k in key_model), DEFAULT_MODEL)

    fw_slug = data.framework.lower()
    fw_context = FRAMEWORK_EXAMPLES.get(fw_slug, FRAMEWORK_EXAMPLES["playwright"])

    prompt = PROMPT_TMPL.format(
        fw_name=fw_slug.capitalize(),
        req=data.requirement,
        example_code=fw_context["code"],
        fw_slug=fw_slug
    )

    payload = {
        "model": model_name,
        "prompt": prompt,
        "format": "json",
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 1200
        },
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=90)
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    raw = resp.json().get("response", "")


    match = re.search(r"\{.*\}", raw, re.DOTALL)

    if match:
        clean = match.group(0)
        try:
            parsed = json.loads(clean)
        except json.JSONDecodeError:
            parsed = {"error": "JSON valid değil", "raw_snippet": clean[:100] + "..."}
    else:
        parsed = {"error": "JSON bloğu bulunamadı", "raw": raw}

    return {
        "model_used": model_name,
        "target_framework": fw_slug,
        "result": parsed
    }