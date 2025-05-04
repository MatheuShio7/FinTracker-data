import requests
import json
from datetime import datetime, timedelta
from tabulate import tabulate
import random
import time

# Definindo a lista de User-Agents para rotacionar
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.5; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'
]

def obter_cotacao_atual(ticker):
    """Obtém a cotação atual da ação usando a API do Yahoo Finance"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA"
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        requisicao = requests.get(url, headers=headers)
        
        if requisicao.status_code != 200:
            print(f"Erro na requisição: código {requisicao.status_code}")
            return None
        
        dados = json.loads(requisicao.text)
        
        if 'chart' in dados and 'result' in dados['chart'] and dados['chart']['result']:
            resultado = dados['chart']['result'][0]
            meta = resultado.get('meta', {})
            
            preco_atual = meta.get('regularMarketPrice')
            nome_empresa = meta.get('shortName')
            volume = meta.get('regularMarketVolume')
            variacao = meta.get('regularMarketChangePercent')
            
            return {
                'preco': preco_atual,
                'nome': nome_empresa,
                'volume': volume,
                'variacao': variacao
            }
        else:
            print("Dados não encontrados na resposta da API.")
            return None
    
    except Exception as e:
        print(f"Erro ao obter cotação atual: {e}")
        return None

def obter_precos_historicos(ticker, dias=30):
    """Obtém preços históricos dos últimos dias usando o Yahoo Finance API"""
    # Calcula o período - 90 dias atrás para garantir dias suficientes de negociação
    data_final = int(datetime.now().timestamp())
    data_inicial = int((datetime.now() - timedelta(days=90)).timestamp())
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA?period1={data_inicial}&period2={data_final}&interval=1d"
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        requisicao = requests.get(url, headers=headers)
        
        if requisicao.status_code != 200:
            print(f"Erro na requisição: código {requisicao.status_code}")
            return []
        
        dados = json.loads(requisicao.text)
        
        if 'chart' in dados and 'result' in dados['chart'] and dados['chart']['result']:
            resultado = dados['chart']['result'][0]
            timestamps = resultado.get('timestamp', [])
            quotes = resultado.get('indicators', {}).get('quote', [{}])[0]
            
            # Extraindo preços de fechamento e ajustando para dados disponíveis
            precos = []
            for i in range(len(timestamps)):
                if 'close' in quotes and i < len(quotes['close']) and quotes['close'][i] is not None:
                    data = datetime.fromtimestamp(timestamps[i]).strftime('%d/%m/%Y')
                    preco = round(quotes['close'][i], 2)
                    precos.append({'Data': data, 'Preço (R$)': preco})
            
            # Aumentando o período de busca se necessário para garantir 30 dias
            if len(precos) < dias:
                print(f"Aviso: Foram encontrados apenas {len(precos)} dias de negociação.")
            
            # Ordenando por data (mais recente primeiro) e pegando os últimos 'dias'
            precos.sort(key=lambda x: datetime.strptime(x['Data'], '%d/%m/%Y'), reverse=True)
            return precos[:dias]
        else:
            print("Dados históricos não encontrados na resposta da API.")
            return []
    
    except Exception as e:
        print(f"Erro ao obter dados históricos: {e}")
        import traceback
        traceback.print_exc()
        return []

def obter_proventos(ticker):
    """Obtém os dividendos usando o Yahoo Finance API"""
    # Tempo maior para garantir que tenhamos dividendos suficientes
    data_final = int(datetime.now().timestamp())
    data_inicial = int((datetime.now() - timedelta(days=1825)).timestamp())  # ~5 anos
    
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}.SA?period1={data_inicial}&period2={data_final}&interval=1d&events=div"
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        # Adiciona delay para evitar bloqueio por muitas requisições
        time.sleep(1)
        requisicao = requests.get(url, headers=headers)
        
        if requisicao.status_code != 200:
            print(f"Erro na requisição de proventos: código {requisicao.status_code}")
            return []
        
        dados = json.loads(requisicao.text)
        
        if 'chart' in dados and 'result' in dados['chart'] and dados['chart']['result']:
            resultado = dados['chart']['result'][0]
            eventos = resultado.get('events', {})
            
            if 'dividends' in eventos:
                dividendos = eventos['dividends']
                
                # Convertendo para lista e ordenando
                proventos_list = []
                for timestamp, provento in dividendos.items():
                    data = datetime.fromtimestamp(int(timestamp)).strftime('%d/%m/%Y')
                    valor = round(provento.get('amount', 0), 4)
                    proventos_list.append({
                        'Data': data,
                        'Valor (R$)': valor,
                        'Tipo': 'Dividendo'  # Yahoo não diferencia tipos de proventos
                    })
                
                # Ordenando por data (mais recente primeiro)
                proventos_list.sort(key=lambda x: datetime.strptime(x['Data'], '%d/%m/%Y'), reverse=True)
                return proventos_list[:12]  # Retorna os 12 mais recentes
            else:
                print("Não foram encontrados dados de proventos.")
                return []
        else:
            print("Dados de proventos não encontrados na resposta da API.")
            return []
    
    except Exception as e:
        print(f"Erro ao obter proventos: {e}")
        import traceback
        traceback.print_exc()
        return []

def formatar_variacao(variacao):
    """Formata a variação percentual com cor e sinal"""
    if variacao is None:
        return "N/A"
    
    if variacao > 0:
        return f"+{variacao:.2f}%"
    else:
        return f"{variacao:.2f}%"

def mostrar_resultados(ticker):
    """Mostra os resultados formatados"""
    try:
        print(f"\nConsultando informações para {ticker}...")
        
        # Obtém dados atuais
        dados_atuais = obter_cotacao_atual(ticker)
        
        if not dados_atuais:
            print(f"Não foi possível obter informações para o ticker {ticker}.")
            return
        
        nome_empresa = dados_atuais.get('nome', ticker)
        preco_atual = dados_atuais.get('preco', 'N/A')
        variacao = dados_atuais.get('variacao', None)
        variacao_formatada = formatar_variacao(variacao)
        
        print(f"\n{'=' * 60}")
        print(f"{'ANÁLISE DA AÇÃO ' + ticker + ' - ' + nome_empresa:^60}")
        print(f"{'=' * 60}")
        print(f"Preço Atual: R$ {preco_atual:.2f} ({variacao_formatada})")
        print(f"{'=' * 60}\n")
        
        # Obtém e mostra os preços históricos
        print(f"PREÇOS DOS ÚLTIMOS 30 DIAS DE NEGOCIAÇÃO:")
        precos = obter_precos_historicos(ticker)
        if precos:
            # Usando tabulate para formatar os dados
            headers = precos[0].keys()
            data = [item.values() for item in precos]
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("Não foram encontrados dados de preços para esta ação.\n")
        
        print("\n")
        
        # Obtém e mostra os proventos
        print(f"ÚLTIMOS 12 PROVENTOS DISTRIBUÍDOS:")
        proventos = obter_proventos(ticker)
        if proventos:
            # Usando tabulate para formatar os dados
            headers = proventos[0].keys()
            data = [item.values() for item in proventos]
            print(tabulate(data, headers=headers, tablefmt="pretty"))
        else:
            print("Não foram encontrados dados de proventos para esta ação.")
        
        print(f"\n{'=' * 60}")
    
    except Exception as e:
        print(f"Erro ao processar resultados: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("\nConsulta de dados de ações brasileiras")
    print("--------------------------------------")
    print("\nUtilizando a API do Yahoo Finance para consulta de dados financeiros")
    
    while True:
        ticker = input("\nDigite o ticker da ação (ex: PETR4) ou 'sair' para encerrar: ").strip().upper()
        
        if ticker.lower() == 'sair':
            print("\nEncerrando o programa...")
            break
        
        if not ticker:
            print("Por favor, digite um ticker válido.")
            continue
        
        mostrar_resultados(ticker)

if __name__ == "__main__":
    main()