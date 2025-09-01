"""
Configurações do Monitor de Status Pages
"""

import os
from typing import Optional

class Config:
    """Configurações da aplicação"""
    
    # Sua Status Page - APENAS variáveis de ambiente
    STATUSPAGE_API_KEY: str = os.getenv('STATUSPAGE_API_KEY', '')
    STATUSPAGE_PAGE_ID: str = os.getenv('STATUSPAGE_PAGE_ID', '8bkqmcmyhrmd')
    
    # URLs das APIs dos fornecedores
    CELCOIN_API_URL: str = "https://celcoin.statuspage.io/api/v2/incidents.json"
    STARKBANK_API_URL: str = "https://status.starkbank.com/api/v2/incidents.json"
    
    # Configurações de monitoramento
    CHECK_INTERVAL: int = 300  # 5 minutos em segundos
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Configurações de filtro
    IGNORE_MAINTENANCE: bool = False
    IGNORE_RESOLVED_OLDER_THAN_HOURS: int = 1
    
    # Mapeamento dos componentes
    COMPONENT_MAPPING = {
        'celcoin': 'kqwgjnyxjlgd',      # Celcoin - Parceiro Corebank
        'starkbank': '4nb00rg5gjvl'     # Stark Bank - Parceiro Corebank
    }
    
    @classmethod
    def get_from_env(cls) -> 'Config':
        """Carrega configurações das variáveis de ambiente"""
        config = cls()
        
        # Sobrescreve com variáveis de ambiente se existirem
        config.STATUSPAGE_API_KEY = os.getenv('STATUSPAGE_API_KEY', config.STATUSPAGE_API_KEY)
        config.STATUSPAGE_PAGE_ID = os.getenv('STATUSPAGE_PAGE_ID', config.STATUSPAGE_PAGE_ID)
        
        return config