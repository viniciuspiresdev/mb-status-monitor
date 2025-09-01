name: Monitor Status Pages

on:
  schedule:
    - cron: '*/5 * * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout código
      uses: actions/checkout@v4
    
    - name: Configurar Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Instalar dependências
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Executar monitoramento
      env:
        STATUSPAGE_API_KEY: ${{ secrets.STATUSPAGE_API_KEY }}
        STATUSPAGE_PAGE_ID: ${{ secrets.STATUSPAGE_PAGE_ID }}
      run: |
        python monitor.py
    
    - name: Upload logs
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: monitor-logs
        path: |
          monitor.log
          last_state.json
