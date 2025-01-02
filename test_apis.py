import asyncio
from groq import Groq
from openai import OpenAI

# Configurações
GROQ_API_KEY = "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"
DEEPSEEK_API_KEY = "sk-e56e6c97810f405684b72e676c05b231"

def test_groq():
    print("\nTestando Groq...")
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": "Olá, tudo bem?"}]
        )
        print("Resposta Groq:", response.choices[0].message.content)
        print("✅ Teste Groq bem sucedido!")
    except Exception as e:
        print("❌ Erro no teste Groq:", str(e))

def test_deepseek():
    print("\nTestando Deepseek...")
    try:
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Olá, tudo bem?"}]
        )
        print("Resposta Deepseek:", response.choices[0].message.content)
        print("✅ Teste Deepseek bem sucedido!")
    except Exception as e:
        print("❌ Erro no teste Deepseek:", str(e))

if __name__ == "__main__":
    print("Iniciando testes das APIs...")
    test_groq()
    test_deepseek()
    print("\nTestes concluídos!")
