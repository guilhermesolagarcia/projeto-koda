from openai import OpenAI
from dotenv import load_dotenv
from persona import KODA_SYSTEM_PROMPT
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

print("KODA: Oi! Eu sou o KODA. Como você tá hoje?")
print("(Digite 'sair' para encerrar)\n")

historico = [
    {"role": "system", "content": KODA_SYSTEM_PROMPT}
]

while True:
    usuario = input("Você: ")
    
    if usuario.lower() == "sair":
        print("KODA: Tá bem. Estarei aqui quando precisar.")
        break

    historico.append({"role": "user", "content": usuario})

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=historico
    )

    resposta = response.choices[0].message.content
    historico.append({"role": "assistant", "content": resposta})

    print(f"\nKODA: {resposta}\n")