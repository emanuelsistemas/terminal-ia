"""
Módulo de Agentes do NexusIA Bot

Este módulo contém os diferentes agentes especializados que compõem o bot.
Cada agente é responsável por uma funcionalidade específica e trabalha
em conjunto com os outros através do OrquestradorAgent.

Estrutura:
- analisador_agent.py: Analisa a intenção das mensagens
- conversa_agent.py: Gerencia conversas naturais
- diretorio_agent.py: Operações com diretórios
- orquestrador_agent.py: Coordena todos os outros agentes
"""

from .analisador_agent import AnalisadorAgent
from .conversa_agent import ConversaAgent
from .diretorio_agent import DiretorioAgent
from .orquestrador_agent import OrquestradorAgent

__all__ = [
    'AnalisadorAgent',
    'ConversaAgent',
    'DiretorioAgent',
    'OrquestradorAgent'
]
