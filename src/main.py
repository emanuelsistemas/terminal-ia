import os
import asyncio
from dotenv import load_dotenv
from .chat import ChatAssistant, ChatError
from .logger import setup_logger

logger = setup_logger(__name__)

def print_header():
    print("╔══════════════════════════════════════╗")
    print("║ Bem-vindo ao Chat IA                 ║")
    print("╚══════════════════════════════════════╝")

def get_provider_choice() -> str:
    while True:
        print("\nEscolha o provedor:\n")
        print("1. Groq")
        print("2. Deepseek")
        
        try:
            choice = input("\nOpção (1-2): ").strip()
            if choice == "1":
                return "groq"
            elif choice == "2":
                return "deepseek"
            else:
                print("\nOpção inválida! Escolha 1 ou 2.")
        except Exception as e:
            print(f"\nErro ao ler opção: {str(e)}")

def get_api_key(provider: str) -> str:
    # Tenta carregar do .env primeiro
    load_dotenv()
    
    if provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        env_var = "GROQ_API_KEY"
    else:  # deepseek
        key = os.getenv("DEEPSEEK_API_KEY")
        env_var = "DEEPSEEK_API_KEY"
    
    if not key:
        print(f"\nAPI Key não encontrada no arquivo .env")
        key = input(f"Digite sua {provider.upper()} API Key: ").strip()
        
        # Salva no .env para próximo uso
        with open(".env", "a") as f:
            f.write(f"\n{env_var}={key}")
    
    return key

async def chat_loop(assistant: ChatAssistant):
    print("\nChat iniciado! Digite 'sair' para encerrar ou 'limpar' para limpar o histórico.")
    
    while True:
        try:
            # Lê mensagem do usuário
            message = input("\nVocê: ").strip()
            
            # Verifica comandos especiais
            if message.lower() == "sair":
                print("\nAté logo! 👋")
                break
            elif message.lower() == "limpar":
                await assistant.clear_messages()
                print("\nHistórico limpo!")
                continue
            elif not message:
                continue
            
            # Adiciona mensagem ao histórico
            assistant.add_message("user", message)
            
            # Obtém e exibe resposta
            print("\nAssistente: ", end="", flush=True)
            response = await assistant.get_response()
            print(response)
            
        except ChatError as e:
            print(f"\nErro: {str(e)}")
        except KeyboardInterrupt:
            print("\n\nAté logo! 👋")
            break
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            print(f"\nOcorreu um erro inesperado: {str(e)}")

async def main_async():
    try:
        # Exibe cabeçalho
        print_header()
        
        # Obtém configurações do usuário
        provider = get_provider_choice()
        api_key = get_api_key(provider)
        
        # Inicializa o assistente
        assistant = ChatAssistant(api_key=api_key, provider=provider)
        await assistant.initialize()
        
        # Inicia o loop de chat
        await chat_loop(assistant)
        
    except Exception as e:
        print(f"\nErro: {str(e)}")

def main():
    """Ponto de entrada principal"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\nAté logo! 👋")
    except Exception as e:
        print(f"\nErro fatal: {str(e)}")

if __name__ == "__main__":
    main()
