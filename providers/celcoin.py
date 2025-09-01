"""
Provider para monitorar a Status Page da Celcoin
"""

import requests
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class CelcoinProvider:
    """Provider para a Status Page da Celcoin"""
    
    def __init__(self):
        self.api_url = "https://celcoin.statuspage.io/api/v2/incidents.json"
    
    def get_incidents(self) -> List[Dict]:
        """Busca todos os incidentes da Celcoin"""
        try:
            response = requests.get(self.api_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('incidents', [])
        except Exception as e:
            logger.error(f"Erro ao buscar incidentes da Celcoin: {e}")
            return []
    
    def get_active_incidents(self) -> List[Dict]:
        """Busca apenas incidentes ativos (não resolvidos)"""
        incidents = self.get_incidents()
        return [incident for incident in incidents if incident.get('status') != 'resolved']