import sys
from datetime import datetime
import pytz
from .config import COLORS

class Terminal:
    def get_input(self, prompt="Você: "):
        sys.stdout.write(COLORS.LIGHT_BLUE)
        sys.stdout.flush()
        try:
            text = input(prompt)
            return text
        finally:
            sys.stdout.write(COLORS.RESET)
            sys.stdout.flush()
    
    def print_message(self, message, color=COLORS.RESET):
        print(f"{color}{message}{COLORS.RESET}")
    
    def get_current_time(self):
        sp_tz = pytz.timezone("America/Sao_Paulo")
        now = datetime.now(sp_tz)
        return now.strftime("%H:%M:%S - %d/%m/%Y")
