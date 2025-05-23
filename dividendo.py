# Últimos 10 Proventos 

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Configurar o Chrome em modo headless
options = Options()
options.add_argument("--headless")  # Executar sem interface gráfica
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)  # Certifique-se de ter o chromedriver correto

try:
    # 2. Acessar a página de proventos da PETR4
    url = "https://www.infomoney.com.br/cotacoes/b3/acao/petrobras-petr4/proventos/"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # 3. Aguardar o carregamento inicial da tabela de proventos
    wait.until(EC.presence_of_element_located((By.XPATH, "//tbody/tr")))
    
    # 4. Coletar apenas os primeiros 10 registros disponíveis (sem clicar em "Carregar mais")
    rows = driver.find_elements(By.XPATH, "//tbody/tr")[:10]

    # 5. Extrair campos VALOR e PAGAMENTO
    proventos = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 7:
            valor = cells[1].text.strip().replace("R$", "").replace(",", ".")
            try:
                valor_float = float(valor)
                valor_formatado = f"{valor_float:.2f}".replace(".", ",")
            except ValueError:
                valor_formatado = cells[1].text.strip()
            pagamento = cells[6].text.strip()   # Coluna "PAGAMENTO"
            proventos.append({"VALOR": valor_formatado, "PAGAMENTO": pagamento})

    # 6. Exibir os resultados coletados
    for idx, prov in enumerate(proventos, start=1):
        print(f"Data: {prov['PAGAMENTO']}, Valor: R${prov['VALOR']}")

finally:
    driver.quit()
