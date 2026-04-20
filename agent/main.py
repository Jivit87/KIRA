from fastapi import FastAPI
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
import ollama

load_dotenv()

app = FastAPI()

class Message(BaseModel):
    text: str
    sender: str

SYSTEM_PROMPT = """
You are a Mac automation assistant that talks via WhatsApp.
Keep responses:
- short
- clear
- conversational
- no markdown
"""

@app.post("/message")
async def handle_message(msg: Message):
    try:
        user_text = msg.text

        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ]
        )

        reply = response["message"]["content"]

        return {"reply": reply}

    except Exception as e:
        print(f"Error handling request: {e}")
        return {"reply": f"⚠️ Error processing request: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)