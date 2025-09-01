# Monitor de Status Pages - MB Status Board

Automação para monitorar as status pages dos fornecedores e replicar incidentes automaticamente na nossa status page.

## �� Funcionalidades

- ✅ Detecta novos incidentes, atualizações e resoluções
- ✅ Replica automaticamente na nossa status page
- ✅ Filtra manutenções programadas
- ✅ Executa via GitHub Actions (gratuito)
- ✅ Logs detalhados de todas as operações

## ⚙️ Configuração

### 1. Variáveis de Ambiente no GitHub

Vá em Settings > Secrets and variables > Actions e adicione:

- `STATUSPAGE_API_KEY`: Sua chave da API da StatusPage.io
- `STATUSPAGE_PAGE_ID`: ID da sua página 

### 2. Execução

O monitor executa automaticamente a cada 5 minutos via GitHub Actions.

Para executar manualmente:
1. Vá em Actions no GitHub
2. Selecione "Monitor Status Pages"
3. Clique em "Run workflow"

## 🔧 Estrutura do Projeto

```
├── monitor.py              # Script principal
├── config.py               # Configurações
├── statuspage_client.py    # Cliente da StatusPage.io
├── providers/              # Módulos dos fornecedores
│   ├── __init__.py
│   ├── celcoin.py
│   └── starkbank.py
├── .github/workflows/      # GitHub Actions
│   └── monitor.yml
└── requirements.txt        # Dependências Python
```

## 📊 Monitoramento

- **Celcoin**: https://celcoin.statuspage.io/api/v2/incidents.json
- **Stark Bank**: https://status.starkbank.com/api/v2/incidents.json
- **Nossa Status Page**: https://mbstatusboard.statuspage.io/


## 🚨 Logs

Todos os logs são salvos em `monitor.log` e disponibilizados como artefato no GitHub Actions.

## ⚡ Como Funciona

1. **GitHub Action** executa a cada 5 minutos
2. **Script Python** consulta as APIs dos fornecedores
3. **Compara** com o último estado conhecido
4. **Detecta mudanças** e replica na nossa status page
5. **Atualiza componentes** automaticamente

## 🔒 Segurança

- APIs dos fornecedores são públicas (sem chave necessária)
- Sua chave de API fica protegida nas secrets do GitHub
- Código é público mas não expõe dados sensíveis

## 🚀 Instalação

1. Clone o repositório
2. Configure as secrets no GitHub:
   - `STATUSPAGE_API_KEY`
   - `STATUSPAGE_PAGE_ID`
3. O monitor começará a executar automaticamente

## 📝 Logs e Monitoramento

- Logs detalhados em `monitor.log`
- Estado dos incidentes salvo em `last_state.json`
- Artefatos disponíveis no GitHub Actions

## 🛠️ Desenvolvimento

Para testar localmente:

```bash
pip install -r requirements.txt
python monitor.py
```

## 📞 Suporte

Em caso de problemas, verifique:
1. Logs do GitHub Actions
2. Arquivo `monitor.log`
3. Configuração das secrets
