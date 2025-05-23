# Últimos 30 Cotações

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

# Acessar a URL
url = 'https://www.infomoney.com.br/cotacoes/b3/acao/petrobras-petr4/historico/'
driver.get(url)

# Aguardar a tabela carregar (ajuste se necessário)
time.sleep(5)

# Capturar o HTML renderizado
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Encontrar os valores da tabela
table = soup.find('table', id='quotes_history')
if table:
    rows = table.find('tbody').find_all('tr')
    for i, row in enumerate(rows):
        if i >= 30:
            break  # Para após 30 registros
        cols = row.find_all('td')
        if len(cols) >= 3:
            data = cols[0].text.strip()
            valor_desejado = cols[2].text.strip()
            print(f'Data: {data}, Valor: {valor_desejado}')
else:
    print('Tabela não encontrada.')

driver.quit()
