#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import time
from datetime import datetime

def get_bot_pid():
    try:
        with open("bot.pid", "r") as f:
            return int(f.read().strip())
    except:
        return None

def is_bot_running(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

def start_bot():
    pid = get_bot_pid()
    if is_bot_running(pid):
        print(f"❌ Bot já está rodando com PID {pid}")
        return
    
    print("🚀 Iniciando bot...")
    subprocess.run(["./run_telegram.sh"])
    time.sleep(2)
    
    pid = get_bot_pid()
    if is_bot_running(pid):
        print(f"✅ Bot iniciado com sucesso (PID: {pid})")
    else:
        print("❌ Falha ao iniciar bot")

def stop_bot():
    pid = get_bot_pid()
    if not is_bot_running(pid):
        print("❌ Bot não está rodando")
        return
    
    print(f"🛑 Parando bot (PID: {pid})...")
    try:
        subprocess.run(["pkill", "-f", "run_telegram.py"])
        time.sleep(2)
        if not is_bot_running(pid):
            print("✅ Bot parado com sucesso")
        else:
            print("❌ Falha ao parar bot")
    except:
        print("❌ Erro ao tentar parar bot")

def restart_bot():
    print("🔄 Reiniciando bot...")
    stop_bot()
    time.sleep(2)
    start_bot()

def status_bot():
    pid = get_bot_pid()
    if is_bot_running(pid):
        print(f"✅ Bot está rodando (PID: {pid})")
        # Mostra últimas linhas do log
        print("\n📝 Últimas 5 linhas do log:")
        subprocess.run(["tail", "-n", "5", "telegram.log"])
    else:
        print("❌ Bot não está rodando")

def view_logs(n=20, follow=False, error=False):
    log_file = "telegram.log"
    
    if error:
        print("🔍 Buscando erros no log...")
        subprocess.run(["grep", "-i", "error", log_file])
        return
    
    if follow:
        print(f"📝 Monitorando log em tempo real (Ctrl+C para sair)...")
        try:
            subprocess.run(["tail", "-f", log_file])
        except KeyboardInterrupt:
            print("\n✋ Monitoramento interrompido")
    else:
        print(f"📝 Últimas {n} linhas do log:")
        subprocess.run(["tail", "-n", str(n), log_file])

def main():
    parser = argparse.ArgumentParser(description="Gerenciador do Bot Telegram")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "logs"], help="Ação a ser executada")
    parser.add_argument("-n", "--lines", type=int, default=20, help="Número de linhas do log para mostrar")
    parser.add_argument("-f", "--follow", action="store_true", help="Monitora o log em tempo real")
    parser.add_argument("-e", "--error", action="store_true", help="Mostra apenas erros do log")
    
    args = parser.parse_args()
    
    if args.action == "start":
        start_bot()
    elif args.action == "stop":
        stop_bot()
    elif args.action == "restart":
        restart_bot()
    elif args.action == "status":
        status_bot()
    elif args.action == "logs":
        view_logs(args.lines, args.follow, args.error)

if __name__ == "__main__":
    main()
