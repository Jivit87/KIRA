import os 
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from pydantic import BaseModel
from fastapi import FastAPI
from memory.mem0_client import add_memory, search_memory
from intent.classifier import classify_intent

app = FastAPI()
groq_client = Groq() 

class Message(BaseModel):
    text: str
    sender: str

SYSTEM_PROMPT = """
You are a smart personal assistant on WhatsApp.
Use past context if relevant.
Keep replies short and natural.
"""

@app.post("/message")
async def handle_message(msg: Message):
    try:
        user_text = msg.text

        # classify intent
        intent = classify_intent(user_text)["intent"]
        print("Intent:", intent)

        # retrieve memory safely
        memory_result = search_memory(user_text)
        
        # You’re converting stored memory objects into a clean text context for the AI to use.
        if isinstance(memory_result, dict):
            mem_list = memory_result.get("results", [])
        elif isinstance(memory_result, list):
            mem_list = memory_result
        else:
            mem_list = []

        memory_context = "\n".join(
            str(m.get("memory", ""))
            for m in mem_list
            if isinstance(m, dict) and "memory" in m
        )  

        if intent == "chat":    
            response = groq_client.chat.completions.create(
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
            
                    {"role": "user", "content": f"Context:\n{memory_context}\n\nUser: {user_text}"}
                ]
            )

            reply = response.choices[0].message.content

        elif intent == "action":
            reply = "Got it, will perform action soon"

        elif intent == "plan":
            reply = "Got it, will plan and execute soon"  

        else:
            reply = "I'm not sure what you mean, can you rephrase?"      
            

        # save memory
        add_memory(user_text, reply)

        return {"reply": reply}

    except Exception as e:
        print(f"Error handling request: {e}")
        return {"reply": f"⚠️ Error processing request: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8765)