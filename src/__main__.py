import sys
from .assistant import main as assistant_main
from .log_viewer import main as log_viewer_main
import asyncio

def print_usage():
    print("Uso:")
    print("  chat-ia          - Inicia o chat")
    print("  chat-ia logs     - Monitora os logs em tempo real")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "logs":
            log_viewer_main()
            return
        else:
            print_usage()
            return
    
    asyncio.run(assistant_main())

if __name__ == "__main__":
    main()
