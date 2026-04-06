import os
from openai import OpenAI
from dotenv import load_dotenv
from persona import KODA_SYSTEM_PROMPT
from crisis import CrisisManager

# Carrega as chaves do seu arquivo .env [cite: 2]
load_dotenv()

# Configura o cliente para o OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

crisis_manager = CrisisManager() # Inicializa o gestor de crises
historico = [{"role": "system", "content": KODA_SYSTEM_PROMPT}] # Define a persona

print("--- 🌿 KODA: Terminal Mode ---")
print("Digite 'sair' para encerrar a conversa.\n")

while True:
    user_input = input("Você: ")
    
    if user_input.lower() in ["sair", "exit", "quit"]:
        print("KODA: Até logo. Se precisar, estarei aqui. 🫂")
        break

    # 1. Verifica se há crise antes de chamar a IA
    state = crisis_manager.analyze_input(user_input)
    
    if state.is_crisis and state.severity == 'critical':
        print(f"\nKODA: {crisis_manager.get_crisis_protocol(state)}\n")
        continue

    # 2. Adiciona a fala do usuário ao histórico
    historico.append({"role": "user", "content": user_input})

    try:
        # 3. Chama o modelo gratuito que definimos
        response = client.chat.completions.create(
            model="google/gemini-2.0-flash-exp:free",
            messages=historico
        )
        resposta = response.choices[0].message.content
        
        # 4. Exibe a resposta e salva no histórico para manter o contexto
        print(f"\nKODA: {resposta}\n")
        historico.append({"role": "assistant", "content": resposta})

    except Exception as e:
        print(f"\n🚨 Erro de conexão: {e}\n")