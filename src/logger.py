import logging
import sys

def setup_logger(name):
    """Configura um logger básico que escreve no stdout"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Cria um handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Formata a mensagem
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Adiciona o handler ao logger
    logger.addHandler(handler)
    
    return logger
