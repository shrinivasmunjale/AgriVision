# Temporary: try several candidate Gemini models and report which work.
# pyrefly: ignore [missing-import]
import httpx, os

key = os.environ.get("K", "").strip()
models = [
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-pro",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-2.0",
]

for m in models:
    try:
        r = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
            params={"key": key},
            json={"contents": [{"parts": [{"text": "Reply with exactly: ok"}]}]},
            timeout=30,
        )
        if r.status_code == 200:
            try:
                reply = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                reply = "<parse?>" + r.text[:60]
            print(f"OK   {m}  -> {reply[:40]}")
        else:
            print(f"FAIL {m}  -> {r.status_code}")
    except Exception as e:
        print(f"EXC  {m}  -> {type(e).__name__}")