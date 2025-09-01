"""
Provider para monitorar a Status Page da Stark Bank
"""

import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class StarkBankProvider:
    """Provider para a Status Page da Stark Bank"""
    
    def __init__(self):
        self.api_url = "https://status.starkbank.com/api/v2/incidents.json"
    
    def get_incidents(self) -> List[Dict]:
        """Busca todos os incidentes da Stark Bank"""
        try:
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('incidents', [])
        except Exception as e:
            logger.error(f"Erro ao buscar incidentes da Stark Bank: {e}")
            return []
    
    def get_active_incidents(self) -> List[Dict]:
        """Busca apenas incidentes ativos (não resolvidos)"""
        incidents = self.get_incidents()
        return [incident for incident in incidents if incident.get('status') != 'resolved']
