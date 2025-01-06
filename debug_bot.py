#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def check_processes():
    log("Verificando processos...")
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    processes = [line for line in result.stdout.split('\n') if 'python' in line and ('bot.py' in line or 'telegram.py' in line)]
    
    if processes:
        log("Processos encontrados:")
        for proc in processes:
            print(proc)
    else:
        log("Nenhum processo do bot encontrado")
    return processes

def check_files():
    log("Verificando arquivos...")
    files_to_check = [
        'run_telegram.py',
        'run_telegram.sh',
        'src/telegram_bot.py',
        'bot.pid',
        '/tmp/telegram.pid'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            stat = os.stat(file)
            perms = oct(stat.st_mode)[-3:]
            size = stat.st_size
            log(f"✓ {file}: permissões={perms}, tamanho={size} bytes")
        else:
            log(f"✗ {file} não encontrado")

def check_logs():
    log("Verificando logs...")
    log_files = ['telegram.log', 'bot.log']
    
    for log_file in log_files:
        if os.path.exists(log_file):
            log(f"Últimas linhas de {log_file}:")
            subprocess.run(['tail', '-n', '5', log_file])
            
            # Procura por erros
            log(f"Procurando erros em {log_file}:")
            subprocess.run(['grep', '-i', 'error', log_file], capture_output=True, text=True)
        else:
            log(f"✗ {log_file} não encontrado")

def kill_processes():
    log("Matando processos existentes...")
    subprocess.run(['pkill', '-9', '-f', 'python.*bot.py'])
    subprocess.run(['pkill', '-9', '-f', 'python.*telegram.py'])
    time.sleep(2)

def clean_pid_files():
    log("Limpando arquivos PID...")
    pid_files = ['bot.pid', '/tmp/telegram.pid']
    for pid_file in pid_files:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            log(f"✓ {pid_file} removido")

def fix_permissions():
    log("Corrigindo permissões...")
    files_to_fix = [
        'run_telegram.py',
        'run_telegram.sh',
        'manage_bot.py',
        'debug_bot.py'
    ]
    
    for file in files_to_fix:
        if os.path.exists(file):
            os.chmod(file, 0o755)
            log(f"✓ Permissões corrigidas para {file}")

def main():
    if len(sys.argv) < 2:
        print("Uso: ./debug_bot.py [check|clean|fix|all]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action in ['check', 'all']:
        check_processes()
        check_files()
        check_logs()
    
    if action in ['clean', 'all']:
        kill_processes()
        clean_pid_files()
    
    if action in ['fix', 'all']:
        fix_permissions()

if __name__ == "__main__":
    main()
