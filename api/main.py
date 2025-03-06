import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.intents import load_intents, find_best_match
from api.response import generate_response
from dotenv import load_dotenv

app = FastAPI(title="Chatbot ERP Master")

INTENTS = load_intents()
load_dotenv()

class Message(BaseModel):
    question: str


@app.post("/chat")
async def chat(message: Message):
    try:
        intent, confidence = find_best_match(message.question, INTENTS)
        response_data = generate_response(intent, confidence, INTENTS)
        if not response_data:
            return {"status": "not_found",
                    "response": "Desculpe, não entendi sua pergunta. Pode reformular de outra forma?"}
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/intents")
async def list_intents():
    return {
        "status": "success",
        "intents": list(INTENTS.keys())
    }

@app.post("/reload")
async def reload_intents():
    try:
        global INTENTS
        INTENTS = load_intents()
        return {
            "status": "success",
            "message": "Intenções recarregadas com sucesso!",
            "intents_count": len(INTENTS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/intents")
async def list_intents():
    return {
        "status": "success",
        "intents": list(INTENTS.keys())
    }

@app.post("/reload")
async def reload_intents():
    try:
        load_intents()
        return {
            "status": "success",
            "message": "Intenções recarregadas com sucesso!",
            "intents_count": len(INTENTS)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n=== Iniciando Servidor do Chatbot ERP Master ===")
    print("Verificando configurações...")
    print(f"- Diretório de imagens: {os.getenv('IMAGES_PATH')}")
    print(f"- Arquivo de intents: intents.json")
    print("\nIniciando servidor...")
    uvicorn.run(app, host="0.0.0.0", port=8000)