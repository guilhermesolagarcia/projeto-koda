from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from persona import KODA_SYSTEM_PROMPT
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

class ChatRequest(BaseModel):
    mensagem: str
    historico: list = []

@app.get("/")
def root():
    return {"status": "KODA online"}

@app.post("/chat")
def chat(request: ChatRequest):
    historico = [{"role": "system", "content": KODA_SYSTEM_PROMPT}]
    historico += request.historico
    historico.append({"role": "user", "content": request.mensagem})

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=historico
    )

    resposta = response.choices[0].message.content

    historico_atualizado = request.historico + [
        {"role": "user", "content": request.mensagem},
        {"role": "assistant", "content": resposta}
    ]

    return {
        "resposta": resposta,
        "historico": historico_atualizado
    }