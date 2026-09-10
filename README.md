# DEV AI Backend

Secure backend for the DEV AI Android app.

## 1. Install
```bash
pip install -r requirements.txt
```

## 2. Configure keys
Copy `.env.example` to `.env` and add your API keys.

Never upload `.env` to GitHub.

## 3. Run
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Test:
http://localhost:8000/

## 4. Connect Android app
After deployment, replace the placeholder backend URL in:
MainActivity.kt

Example:
https://your-domain.com/chat

## API
POST /chat

JSON:
{
  "message": "Hello",
  "mode": "Both AI"
}

Modes:
- ChatGPT
- Gemini
- Both AI
