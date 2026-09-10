import os
import asyncio
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="DEV AI Backend")

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

class ChatRequest(BaseModel):
    message: str
    mode: str = "Both AI"

async def ask_openai(message: str) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing")
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "input": [{"role": "user", "content": message}]
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("https://api.openai.com/v1/responses", headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("output_text", "No response")

async def ask_gemini(message: str) -> str:
    if not GEMINI_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": message}]}]}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

@app.get("/")
async def home():
    return {"status": "DEV AI backend running"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        if req.mode == "ChatGPT":
            return {"answer": await ask_openai(req.message)}

        if req.mode == "Gemini":
            return {"answer": await ask_gemini(req.message)}

        openai_answer, gemini_answer = await asyncio.gather(
            ask_openai(req.message),
            ask_gemini(req.message),
            return_exceptions=True
        )

        results = []
        if not isinstance(openai_answer, Exception):
            results.append(f"OpenAI answer:\n{openai_answer}")
        if not isinstance(gemini_answer, Exception):
            results.append(f"Gemini answer:\n{gemini_answer}")

        if not results:
            raise HTTPException(status_code=500, detail="Both AI services failed")

        if len(results) == 1:
            return {"answer": results[0]}

        combined_prompt = (
            "Create one clear, accurate answer for the user by combining these two AI answers. "
            "Do not mention the internal comparison unless useful. Answer in the user's language.\n\n"
            + "\n\n".join(results)
        )
        final_answer = await ask_openai(combined_prompt)
        return {"answer": final_answer}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
