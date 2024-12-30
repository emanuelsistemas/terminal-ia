import groq
import asyncio

async def main():
    print("Iniciando teste...")
    client = groq.AsyncGroq(
        api_key="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"
    )
    
    print("Enviando mensagem...")
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente amigável e prestativo."
            },
            {
                "role": "user",
                "content": "Olá, tudo bem?"
            }
        ],
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_tokens=1024
    )
    
    print(f"\nResposta: {chat_completion.choices[0].message.content}")

if __name__ == "__main__":
    asyncio.run(main())
