#!/usr/bin/env python3
"""
Monitor de Status Pages - Automação MB Status Board
Monitora Celcoin e Stark Bank, replica incidentes automaticamente
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import requests
from providers.celcoin import CelcoinProvider
from providers.starkbank import StarkBankProvider
from statuspage_client import StatusPageClient
from config import Config

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StatusMonitor:
    def __init__(self):
        self.config = Config()
        self.statuspage_client = StatusPageClient(
            api_key=self.config.STATUSPAGE_API_KEY,
            page_id=self.config.STATUSPAGE_PAGE_ID
        )
        self.providers = {
            'celcoin': CelcoinProvider(),
            'starkbank': StarkBankProvider()
        }
        self.last_incidents = self._load_last_state()
        
        # Mapeamento dos componentes
        self.component_mapping = {
            'celcoin': 'kqwgjnyxjlgd',  # Celcoin - Parceiro Corebank
            'starkbank': '4nb00rg5gjvl'  # Stark Bank - Parceiro Corebank
        }
    
    def _load_last_state(self) -> Dict:
        """Carrega o último estado conhecido dos incidentes"""
        try:
            with open('last_state.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_last_state(self, state: Dict):
        """Salva o estado atual dos incidentes"""
        with open('last_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    
    def _should_replicate_incident(self, incident: Dict) -> bool:
        """Determina se um incidente deve ser replicado"""
        # Replica TODOS os incidentes, incluindo manutenções programadas
        # Não replica apenas incidentes resolvidos há mais de 1 hora
        if incident.get('status') == 'resolved':
            resolved_at = incident.get('resolved_at')
            if resolved_at:
                try:
                    resolved_time = datetime.fromisoformat(resolved_at.replace('Z', '+00:00'))
                    if (datetime.now(timezone.utc) - resolved_time).total_seconds() > 3600:
                        return False
                except:
                    pass
        
        return True
    
    def _map_impact(self, impact: str) -> str:
        """Mapeia o impacto do fornecedor para nossa terminologia"""
        mapping = {
            'minor': 'minor',
            'major': 'major', 
            'critical': 'critical'
        }
        return mapping.get(impact, 'major')
    
    def _map_status(self, status: str) -> str:
        """Mapeia o status do fornecedor para nossa terminologia"""
        mapping = {
            'investigating': 'investigating',
            'identified': 'identified',
            'monitoring': 'monitoring',
            'resolved': 'resolved'
        }
        return mapping.get(status, 'investigating')
    
    def monitor_providers(self):
        """Monitora todos os fornecedores e replica incidentes"""
        logger.info("Iniciando monitoramento dos fornecedores...")
        
        current_incidents = {}
        changes_detected = False
        
        for provider_name, provider in self.providers.items():
            logger.info(f"Monitorando {provider_name}...")
            
            try:
                incidents = provider.get_incidents()
                current_incidents[provider_name] = incidents
                
                # Verifica mudanças
                last_incidents = self.last_incidents.get(provider_name, [])
                
                for incident in incidents:
                    if self._should_replicate_incident(incident):
                        incident_id = incident.get('id')
                        
                        # Verifica se é um incidente novo ou atualizado
                        last_incident = next(
                            (i for i in last_incidents if i.get('id') == incident_id), 
                            None
                        )
                        
                        if not last_incident:
                            # Novo incidente
                            logger.info(f"Novo incidente detectado: {incident.get('name')}")
                            self._create_incident(incident, provider_name)
                            changes_detected = True
                        
                        elif last_incident.get('updated_at') != incident.get('updated_at'):
                            # Incidente atualizado
                            logger.info(f"Incidente atualizado: {incident.get('name')}")
                            self._update_incident(incident, provider_name)
                            changes_detected = True
                
            except Exception as e:
                logger.error(f"Erro ao monitorar {provider_name}: {e}")
        
        # Salva o estado atual
        self._save_last_state(current_incidents)
        
        if changes_detected:
            logger.info("Mudanças detectadas e processadas!")
        else:
            logger.info("Nenhuma mudança detectada.")
    
    def _create_incident(self, incident: Dict, provider_name: str):
        """Cria um novo incidente na nossa status page"""
        try:
            # Prepara os dados do incidente
            incident_data = {
                'name': f"{provider_name.upper()} - {incident.get('name', 'Incidente')}",
                'status': self._map_status(incident.get('status', 'investigating')),
                'impact': self._map_impact(incident.get('impact', 'major')),
                'body': self._format_incident_body(incident, provider_name),
                'components': [self.component_mapping[provider_name]]
            }
            
            # Cria o incidente
            result = self.statuspage_client.create_incident(incident_data)
            logger.info(f"Incidente criado com sucesso: {result.get('id')}")
            
        except Exception as e:
            logger.error(f"Erro ao criar incidente: {e}")
    
    def _update_incident(self, incident: Dict, provider_name: str):
        """Atualiza um incidente existente na nossa status page"""
        try:
            # Busca o incidente correspondente na nossa status page
            our_incident = self._find_our_incident(incident, provider_name)
            
            if our_incident:
                # Prepara a atualização
                update_data = {
                    'status': self._map_status(incident.get('status', 'investigating')),
                    'body': self._format_incident_body(incident, provider_name)
                }
                
                # Atualiza o incidente
                self.statuspage_client.update_incident(our_incident['id'], update_data)
                logger.info(f"Incidente atualizado: {our_incident['id']}")
                
                # Se foi resolvido, atualiza o componente
                if incident.get('status') == 'resolved':
                    self.statuspage_client.update_component(
                        self.component_mapping[provider_name], 
                        'operational'
                    )
                    logger.info(f"Componente {provider_name} marcado como operational")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar incidente: {e}")
    
    def _find_our_incident(self, provider_incident: Dict, provider_name: str) -> Optional[Dict]:
        """Encontra o incidente correspondente na nossa status page"""
        try:
            our_incidents = self.statuspage_client.get_incidents()
            
            for incident in our_incidents:
                if (provider_name.upper() in incident.get('name', '') and 
                    incident.get('status') != 'resolved'):
                    return incident
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar incidente: {e}")
            return None
    
    def _format_incident_body(self, incident: Dict, provider_name: str) -> str:
        """Formata o corpo do incidente"""
        body = f"**Fonte:** {provider_name.upper()}\n\n"
        
        # Adiciona a descrição mais recente
        updates = incident.get('incident_updates', [])
        if updates:
            latest_update = updates[0]
            body += f"**Status:** {latest_update.get('status', '').title()}\n\n"
            body += f"**Descrição:**\n{latest_update.get('body', '')}\n\n"
        
        # Adiciona informações do fornecedor
        body += f"**Link original:** {incident.get('shortlink', '')}\n"
        body += f"**Atualizado em:** {incident.get('updated_at', '')}"
        
        return body

def main():
    """Função principal"""
    monitor = StatusMonitor()
    monitor.monitor_providers()

if __name__ == "__main__":
    main()