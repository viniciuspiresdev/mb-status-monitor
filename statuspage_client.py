"""
Cliente para interagir com a API da StatusPage.io
"""

import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StatusPageClient:
    """Cliente para a API da StatusPage.io"""
    
    def __init__(self, api_key: str, page_id: str):
        self.api_key = api_key
        self.page_id = page_id
        self.base_url = f"https://api.statuspage.io/v1/pages/{page_id}"
        self.headers = {
            'Authorization': f'OAuth {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_incidents(self) -> List[Dict]:
        """Busca todos os incidentes da página"""
        try:
            response = requests.get(
                f"{self.base_url}/incidents",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar incidentes: {e}")
            return []
    
    def create_incident(self, incident_data: Dict) -> Optional[Dict]:
        """Cria um novo incidente"""
        try:
            response = requests.post(
                f"{self.base_url}/incidents",
                headers=self.headers,
                json=incident_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao criar incidente: {e}")
            return None
    
    def update_incident(self, incident_id: str, update_data: Dict) -> Optional[Dict]:
        """Atualiza um incidente existente"""
        try:
            response = requests.patch(
                f"{self.base_url}/incidents/{incident_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao atualizar incidente: {e}")
            return None
    
    def resolve_incident(self, incident_id: str) -> Optional[Dict]:
        """Resolve um incidente"""
        try:
            update_data = {
                'status': 'resolved',
                'body': 'Este incidente foi resolvido automaticamente.'
            }
            return self.update_incident(incident_id, update_data)
        except Exception as e:
            logger.error(f"Erro ao resolver incidente: {e}")
            return None
    
    def update_component(self, component_id: str, status: str) -> Optional[Dict]:
        """Atualiza o status de um componente"""
        try:
            update_data = {
                'status': status
            }
            response = requests.patch(
                f"{self.base_url}/components/{component_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao atualizar componente: {e}")
            return None