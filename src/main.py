import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from .chat import ChatAssistant, ChatError
from .logger import setup_logger

logger = setup_logger(__name__)

def print_flush(msg, end="\n"):
    print(msg, end=end, flush=True)
    sys.stdout.flush()

def print_header():
    print_flush("╔══════════════════════════════════════╗")
    print_flush("║ Bem-vindo ao Chat IA                 ║")
    print_flush("╚══════════════════════════════════════╝\n")

def get_provider_choice() -> str:
    print_flush("Escolha o provedor:\n")
    print_flush("1. Groq")
    print_flush("2. Deepseek\n")
    
    while True:
        try:
            choice = input("Opção (1-2): ").strip()
            if choice == "1":
                return "groq"
            elif choice == "2":
                return "deepseek"
            else:
                print_flush("\nOpção inválida. Por favor, escolha 1 ou 2.")
        except Exception as e:
            print_flush(f"\nErro ao ler opção: {str(e)}")

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
            print_flush(f"\nErro: Chave da API do {provider} não encontrada no arquivo .env")
            return
        
        # Inicializa o chat
        chat = ChatAssistant(api_key=api_key, provider=provider)
        
        print_flush("\nChat iniciado! Digite 'sair' para encerrar ou 'limpar' para limpar o histórico.\n")
        
        # Loop principal
        while True:
            try:
                # Obtém entrada do usuário
                user_input = input("Você: ").strip()
                
                # Verifica comandos especiais
                if user_input.lower() == "sair":
                    print_flush("\nAté logo!")
                    break
                elif user_input.lower() == "limpar":
                    chat.clear_messages()
                    print_flush("\nHistórico limpo!\n")
                    continue
                elif not user_input:
                    continue
                
                # Adiciona mensagem do usuário
                chat.add_message("user", user_input)
                
                # Obtém resposta do assistente
                print_flush("\nAssistente: ", end="")
                response = chat.get_response()
                print_flush(f"{response}\n")
                
            except ChatError as e:
                print_flush(f"\nErro no chat: {str(e)}\n")
            except KeyboardInterrupt:
                print_flush("\n\nChat encerrado pelo usuário.")
                break
            except Exception as e:
                print_flush(f"\nErro inesperado: {str(e)}\n")
                logger.error(f"Erro inesperado: {str(e)}")
        
    except Exception as e:
        print_flush(f"\nErro fatal: {str(e)}")
        logger.error(f"Erro fatal: {str(e)}")

if __name__ == "__main__":
    main()
