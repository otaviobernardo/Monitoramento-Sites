import os
import time
import pandas as pd
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = webdriver.ChromeOptions()
#options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

sites = {
    "Google": {"url": "https://www.google.com", "check": "q"},
    "LinkedIn": {"url": "https://www.linkedin.com", "check": "session_key"},
    "Amazon": {"url": "https://www.amazon.com", "check": "nav-logo-sprites"},
    "Globo": {"url": "https://www.globo.com", "check": "header-menu"},
    "Teste 404": {"url": "https://httpstat.us/404", "check": ""},
    "Teste 500": {"url": "https://httpstat.us/500", "check": ""},
    "Teste 301": {"url": "http://github.com", "check": ""},
    "Teste 403": {"url": "https://httpstat.us/403", "check": ""},
}

arquivo = "monitorando_status.csv"
if os.path.exists(arquivo):
    df_historico = pd.read_csv(arquivo)
else:
    df_historico = pd.DataFrame(columns=["Site","Status","Tempo","Elemento_OK","Hora"])


def testar_site(nome, url, elemento_id):
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        inicio = time.time()
        resposta = requests.get(url, timeout=10)
        status = resposta.status_code
        tempo_resposta = time.time() - inicio

        elemento_ok = False
        if elemento_id:
            driver.get(url)
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, elemento_id)))
                elemento_ok = True
            except:
                elemento_ok = False

        print(f"[OK] {nome}: Status={status} | Tempo={tempo_resposta:.2f}s | Elemento={elemento_ok}")
        return [nome, status, tempo_resposta, elemento_ok, hora]
    except Exception as e:
        print(f"[ERRO] {nome}: {e}")
        return [nome, "Erro", None, False, hora]

# Loop de monitoramento
coletas = 100        # número de coletas
intervalo = 60      # intervalo em segundos

for i in range(coletas):
    print(f"\n--- Coleta {i+1}/{coletas} ---")
    dados = []
    for site, info in sites.items():
        resultado = testar_site(site, info["url"], info["check"])
        dados.append(resultado)

    df_novo = pd.DataFrame(dados, columns=["Site","Status","Tempo","Elemento_OK","Hora"])
    df_historico = pd.concat([df_historico, df_novo], ignore_index=True)
    df_historico.to_csv(arquivo, index=False)

    if i < coletas-1:
        print(f"[Aguardando {intervalo}s para próxima coleta...]")
        time.sleep(intervalo)

print("\n[INFO] Monitoramento finalizado.")
driver.quit()
