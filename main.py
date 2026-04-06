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

MODELOS_FALLBACK = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "google/gemma-3-27b-it:free",
    "openrouter/auto",
]

def chamar_api(historico):
    for modelo in MODELOS_FALLBACK:
        try:
            response = client.chat.completions.create(
                model=modelo,
                messages=historico
            )
            print(f"✅ Modelo usado: {modelo}")
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ {modelo} falhou: {e}")
            continue
    return "Desculpe, tô com instabilidade agora. Pode tentar de novo?"

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

    resposta = chamar_api(historico)

    historico_atualizado = request.historico + [
        {"role": "user", "content": request.mensagem},
        {"role": "assistant", "content": resposta}
    ]

    return {
        "resposta": resposta,
        "historico": historico_atualizado
    }

# ==============================================================
# IMPORTANTE: Esta linha DEVE ser sempre a última do arquivo!
# ==============================================================
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")