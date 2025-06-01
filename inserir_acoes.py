import csv
import os
from supabase import create_client, Client
from typing import List, Dict


# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


def create_supabase_client() -> Client:
    """Cria e retorna o cliente do Supabase"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL e SUPABASE_ANON_KEY devem estar definidas nas variáveis de ambiente")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def read_csv_file(file_path: str) -> List[Dict[str, str]]:
    """Lê o arquivo CSV e retorna uma lista de dicionários com os dados das ações"""
    stocks_data = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Usando DictReader para ler o CSV com headers
            csv_reader = csv.DictReader(file)
            
            # Processa cada linha do CSV
            for row in csv_reader:
                # Extrai apenas ticker e nome, ignora outras colunas
                ticker = row.get('Ticker', '').strip()
                company = row.get('Nome', '').strip()
                
                # Verifica se os campos obrigatórios estão preenchidos
                if ticker and company:
                    stock_data = {
                        'ticker': ticker,
                        'company': company,
                        'country': 'br'  # Sempre "br" para todas as ações
                    }
                    stocks_data.append(stock_data)
                else:
                    print(f"Aviso: Linha ignorada - Ticker: '{ticker}', Company: '{company}'")
    
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
        return []
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return []
    
    return stocks_data


def insert_stocks_to_supabase(supabase: Client, stocks_data: List[Dict[str, str]]) -> bool:
    """Insere os dados das ações na tabela stock do Supabase"""
    try:
        # Insere todos os dados de uma vez (batch insert)
        response = supabase.table('stock').insert(stocks_data).execute()
        
        if response.data:
            print(f"✅ Sucesso: {len(response.data)} ações inseridas na tabela 'stock'")
            return True
        else:
            print("❌ Erro: Nenhum dado foi inserido")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao inserir dados no Supabase: {e}")
        
        # Tenta inserção individual em caso de erro (para identificar duplicatas)
        print("Tentando inserção individual para identificar problemas...")
        success_count = 0
        error_count = 0
        
        for stock in stocks_data:
            try:
                supabase.table('stock').insert(stock).execute()
                success_count += 1
            except Exception as individual_error:
                error_count += 1
                print(f"Erro ao inserir {stock['ticker']}: {individual_error}")
        
        print(f"Resultado da inserção individual: {success_count} sucessos, {error_count} erros")
        return success_count > 0


def main():
    """Função principal que coordena todo o processo"""
    # Nome do arquivo CSV (assumindo que está no mesmo diretório do script)
    csv_file_path = "infomoney_b3.csv"
    
    print("🚀 Iniciando processo de inserção de ações no Supabase...")
    
    # 1. Criar cliente do Supabase
    try:
        supabase = create_supabase_client()
        print("✅ Cliente Supabase criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar cliente Supabase: {e}")
        return
    
    # 2. Ler dados do CSV
    print(f"📖 Lendo dados do arquivo: {csv_file_path}")
    stocks_data = read_csv_file(csv_file_path)
    
    if not stocks_data:
        print("❌ Nenhum dado válido encontrado no arquivo CSV")
        return
    
    print(f"✅ {len(stocks_data)} ações encontradas no arquivo CSV")
    
    # 3. Exibir algumas amostras dos dados
    print("\n📊 Amostra dos dados que serão inseridos:")
    for i, stock in enumerate(stocks_data[:5]):  # Mostra apenas as primeiras 5
        print(f"  {i+1}. Ticker: {stock['ticker']}, Company: {stock['company']}, Country: {stock['country']}")
    
    if len(stocks_data) > 5:
        print(f"  ... e mais {len(stocks_data) - 5} ações")
    
    # 4. Confirmar inserção
    user_input = input(f"\n❓ Deseja inserir {len(stocks_data)} ações na tabela 'stock'? (s/n): ").lower().strip()
    
    if user_input != 's':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # 5. Inserir dados no Supabase
    print("\n💾 Inserindo dados no Supabase...")
    success = insert_stocks_to_supabase(supabase, stocks_data)
    
    if success:
        print("🎉 Processo concluído com sucesso!")
    else:
        print("❌ Processo concluído com erros")


def setup_environment():
    """Carrega as variáveis de ambiente do arquivo .env"""
    from dotenv import load_dotenv
    load_dotenv()


if __name__ == "__main__":
    # Configurar variáveis de ambiente se necessário
    setup_environment()
    
    # Executar o processo principal
    main()