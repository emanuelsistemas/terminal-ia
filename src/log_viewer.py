import os
import time
from datetime import datetime
from .config import COLORS

def get_current_log_file():
    log_dir = "logs"
    current_date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"{current_date}.log")

def colorize_log_line(line):
    # Adiciona cores baseado no nível do log
    if "ERROR" in line:
        return f"{COLORS.RED}{line}{COLORS.RESET}"
    elif "WARNING" in line:
        return f"{COLORS.YELLOW}{line}{COLORS.RESET}"
    elif "INFO" in line:
        return f"{COLORS.LIGHT_BLUE}{line}{COLORS.RESET}"
    else:
        return line

def follow_log():
    print(f"{COLORS.GREEN}=== Monitor de Logs ==={COLORS.RESET}")
    print(f"{COLORS.LIGHT_BLUE}Monitorando logs em tempo real...{COLORS.RESET}\n")
    
    current_file = get_current_log_file()
    
    # Espera o arquivo de log ser criado
    while not os.path.exists(current_file):
        print(f"{COLORS.YELLOW}Aguardando arquivo de log ser criado...{COLORS.RESET}")
        time.sleep(1)
    
    # Abre o arquivo e vai para o final
    with open(current_file, "r") as file:
        file.seek(0, 2)  # Vai para o final do arquivo
        while True:
            line = file.readline()
            if not line:
                # Verifica se mudou o dia e precisa trocar de arquivo
                new_file = get_current_log_file()
                if new_file != current_file:
                    print(f"{COLORS.YELLOW}Mudança de dia detectada, trocando arquivo de log...{COLORS.RESET}")
                    current_file = new_file
                    file.close()
                    # Espera o novo arquivo ser criado
                    while not os.path.exists(current_file):
                        time.sleep(1)
                    file = open(current_file, "r")
                else:
                    time.sleep(0.1)  # Pequena pausa para não sobrecarregar a CPU
                continue
            print(colorize_log_line(line.strip()))

def main():
    try:
        follow_log()
    except KeyboardInterrupt:
        print(f"\n{COLORS.YELLOW}Monitor de logs encerrado.{COLORS.RESET}")

if __name__ == "__main__":
    main()
