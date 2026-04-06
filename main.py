from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Inicializa o cliente da API
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Inicializa o Escudo de Crise
crisis_manager = CrisisManager()

class ChatRequest(BaseModel):
    mensagem: str
    historico: list = []

@app.get("/")
def root():
    return {"status": "KODA online"}

@app.post("/chat")
def chat(request: ChatRequest):
    # 1. VERIFICAÇÃO DE CRISE (Rodando localmente, ultra rápido)
    state = crisis_manager.analyze_input(request.mensagem)
    
    # Se for crise crítica, bloqueia a IA e responde com o protocolo de segurança
    if state.is_crisis and state.severity == 'critical':
        resposta_crise = crisis_manager.get_crisis_protocol(state)
        historico_atualizado = request.historico + [
            {"role": "user", "content": request.mensagem},
            {"role": "assistant", "content": resposta_crise}
        ]
        return {
            "resposta": resposta_crise,
            "historico": historico_atualizado
        }

    # 2. FLUXO NORMAL (Se não for crise, chama a IA)
    historico = [{"role": "system", "content": KODA_SYSTEM_PROMPT}]
    historico += request.historico
    historico.append({"role": "user", "content": request.mensagem})

    try:
        response = client.chat.completions.create(
            model="openrouter/auto", # Se o sotaque de Portugal continuar, mude para "google/gemini-2.5-flash"
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