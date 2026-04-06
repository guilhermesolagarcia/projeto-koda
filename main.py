from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from persona import KODA_SYSTEM_PROMPT
from crisis import CrisisManager
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

crisis_manager = CrisisManager()

class ChatRequest(BaseModel):
    mensagem: str
    historico: list = []


@app.post("/chat")
def chat(request: ChatRequest):
    state = crisis_manager.analyze_input(request.mensagem)
    
    if state.is_crisis and state.severity == 'critical':
        resposta_crise = crisis_manager.get_crisis_protocol(state)
        return {
            "resposta": resposta_crise,
            "historico": request.historico
        }

    historico = [{"role": "system", "content": KODA_SYSTEM_PROMPT}]
    historico += request.historico
    historico.append({"role": "user", "content": request.mensagem})

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini", 
            messages=historico
        )
        resposta = response.choices[0].message.content
    except Exception as e:
        resposta = "Desculpe, a minha conexão vacilou por um segundo. Pode tentar me mandar de novo?"

    historico_atualizado = request.historico + [
        {"role": "user", "content": request.mensagem},
        {"role": "assistant", "content": resposta}
    ]

    return {
        "resposta": resposta,
        "historico": historico_atualizado
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")