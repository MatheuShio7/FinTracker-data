# Últimos 10 Proventos - VALE3

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Configuração do Chrome headless
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Acessar a URL de proventos
url = 'https://www.infomoney.com.br/cotacoes/b3/acao/vale-vale3/proventos/'
driver.get(url)

# Aguardar carregamento
time.sleep(5)

# Capturar o HTML renderizado
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Procurar por tabelas
tables = soup.find_all('table')

for table in tables:
    tbody = table.find('tbody')
    if tbody:
        rows = tbody.find_all('tr')
        if rows:
            proventos_encontrados = 0
            
            for row in rows[:10]:  # Primeiros 10
                cols = row.find_all('td')
                if len(cols) >= 2:
                    valor_texto = ""
                    data_texto = ""
                    
                    # Procurar por valor monetário e data nas colunas
                    for col in cols:
                        col_text = col.text.strip()
                        if 'R$' in col_text or (',' in col_text and any(c.isdigit() for c in col_text)):
                            valor_texto = col_text
                        if '/' in col_text and len(col_text) >= 8:  # Formato de data
                            data_texto = col_text
                    
                    if valor_texto and data_texto:
                        # Limpar e formatar valor
                        valor_limpo = valor_texto.replace("R$", "").strip()
                        
                        # Converter para float e formatar
                        try:
                            valor_limpo = valor_limpo.replace(",", ".")
                            valor_float = float(valor_limpo)
                            valor_formatado = f"R${valor_float:.2f}".replace(".", ",")
                        except ValueError:
                            valor_formatado = f"R${valor_limpo}"
                        
                        print(f"Data: {data_texto}, Valor: {valor_formatado}")
                        proventos_encontrados += 1
            
            if proventos_encontrados > 0:
                break  # Sair se encontrou dados

driver.quit()