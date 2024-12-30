from src.chat import ChatAssistant, ChatError
import asyncio

async def test_provider(provider: str, api_key: str):
    print(f"\nTestando {provider.capitalize()}...")
    try:
        chat = ChatAssistant(
            api_key=api_key,
            provider=provider
        )
        chat.add_message("system", "Você é um assistente útil e amigável.")
        chat.add_message("user", "Olá, tudo bem?")
        response = await chat.get_response()
        print(f"Resposta {provider.capitalize()}: {response}\n")
    except ChatError as e:
        print(f"Erro ao usar {provider.capitalize()}: {e.message}\n")
    except Exception as e:
        print(f"Erro inesperado com {provider.capitalize()}: {str(e)}\n")

async def main():
    # Configurar provedores e chaves
    providers = {
        "groq": "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",
        "deepseek": "sk-e56e6c97810f405684b72e676c05b231"
    }
    
    # Testar cada provedor
    for provider, api_key in providers.items():
        await test_provider(provider, api_key)

if __name__ == "__main__":
    asyncio.run(main())
