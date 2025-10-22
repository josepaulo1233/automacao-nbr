"""
Pacote de Gerenciamento MITSID Dash
Módulos para gestão de dados do sistema
"""

__version__ = "1.0.0"
__author__ = "MITSID Team"
__description__ = "Sistema de gerenciamento de dados para análise térmica"

# Importações principais
from .gerenciar_materiais import *
from .gerenciar_vidros import *
from .gerenciar_cores import *
from .gerenciar_projetos import *
from .gerenciar_usuarios import *

__all__ = [
    'gerenciar_materiais',
    'gerenciar_vidros', 
    'gerenciar_cores',
    'gerenciar_projetos',
    'gerenciar_usuarios',
    'gerenciador_principal'
]