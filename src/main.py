import os
from pathlib import Path
from dotenv import load_dotenv
from .chat import ChatAssistant, ChatError
from .logger import setup_logger

logger = setup_logger(__name__)

def print_header():
    print("╔══════════════════════════════════════╗")
    print("║ Bem-vindo ao Chat IA                 ║")
    print("╚══════════════════════════════════════╝\n")

def get_provider_choice() -> str:
    print("Escolha o provedor:\n")
    print("1. Groq")
    print("2. Deepseek\n")
    
    while True:
        try:
            choice = input("Opção (1-2): ")
            if choice == "1":
                return "groq"
            elif choice == "2":
                return "deepseek"
            else:
                print("\nOpção inválida. Por favor, escolha 1 ou 2.")
        except Exception as e:
            print(f"\nErro ao ler opção: {str(e)}")

def get_api_key(provider: str) -> str:
    """Obtém a chave da API do provedor escolhido"""
    if provider == "groq":
        return os.getenv("GROQ_API_KEY", "")
    elif provider == "deepseek":
        return os.getenv("DEEPSEEK_API_KEY", "")
    else:
        raise ValueError(f"Provedor {provider} não suportado")

def main():
    """Função principal que inicia o chat"""
    try:
        # Carrega variáveis de ambiente do arquivo .env no diretório do projeto
        env_path = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(env_path)
        
        # Mostra cabeçalho
        print_header()
        
        # Obtém escolha do provedor
        provider = get_provider_choice()
        
        # Obtém chave da API
        api_key = get_api_key(provider)
        if not api_key:
            print(f"\nErro: Chave da API do {provider} não encontrada no arquivo .env")
            return
        
        # Inicializa o chat
        chat = ChatAssistant(api_key=api_key, provider=provider)
        
        print("\nChat iniciado! Digite 'sair' para encerrar ou 'limpar' para limpar o histórico.\n")
        
        # Loop principal
        while True:
            try:
                # Obtém entrada do usuário
                user_input = input("Você: ").strip()
                
                # Verifica comandos especiais
                if user_input.lower() == "sair":
                    print("\nAté logo!")
                    break
                elif user_input.lower() == "limpar":
                    chat.clear_messages()
                    print("\nHistórico limpo!\n")
                    continue
                elif not user_input:
                    continue
                
                # Adiciona mensagem do usuário
                chat.add_message("user", user_input)
                
                # Obtém resposta do assistente
                print("\nAssistente: ", end="")
                response = chat.get_response()
                print(f"{response}\n")
                
            except ChatError as e:
                print(f"\nErro no chat: {str(e)}\n")
            except KeyboardInterrupt:
                print("\n\nChat encerrado pelo usuário.")
                break
            except Exception as e:
                print(f"\nErro inesperado: {str(e)}\n")
                logger.error(f"Erro inesperado: {str(e)}")
        
    except Exception as e:
        print(f"\nErro fatal: {str(e)}")
        logger.error(f"Erro fatal: {str(e)}")

if __name__ == "__main__":
    main()
