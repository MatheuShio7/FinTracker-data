import csv
import os
from supabase import create_client, Client
from typing import List, Dict


# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Usando service_role key


def create_supabase_client() -> Client:
    """Cria e retorna o cliente do Supabase com permissões administrativas"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError("SUPABASE_URL e SUPABASE_SERVICE_KEY devem estar definidas nas variáveis de ambiente")
    
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


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
                print(f"✅ {stock['ticker']} inserido com sucesso")
            except Exception as individual_error:
                error_count += 1
                print(f"❌ Erro ao inserir {stock['ticker']}: {individual_error}")
        
        print(f"Resultado da inserção individual: {success_count} sucessos, {error_count} erros")
        return success_count > 0


def check_existing_data(supabase: Client) -> int:
    """Verifica quantas ações já existem na tabela"""
    try:
        response = supabase.table('stock').select('ticker', count='exact').execute()
        count = response.count if hasattr(response, 'count') else len(response.data)
        print(f"📊 Atualmente existem {count} ações na tabela 'stock'")
        return count
    except Exception as e:
        print(f"⚠️ Erro ao verificar dados existentes: {e}")
        return 0


def main():
    """Função principal que coordena todo o processo"""
    # Nome do arquivo CSV (assumindo que está no mesmo diretório do script)
    csv_file_path = "infomoney_b3.csv"
    
    print("🚀 Iniciando processo de inserção de ações no Supabase...")
    print("🔐 Usando SERVICE ROLE KEY para bypass de RLS")
    
    # 1. Criar cliente do Supabase com permissões administrativas
    try:
        supabase = create_supabase_client()
        print("✅ Cliente Supabase ADMIN criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar cliente Supabase: {e}")
        print("💡 Verifique se SUPABASE_URL e SUPABASE_SERVICE_KEY estão definidas no .env")
        return
    
    # 2. Verificar dados existentes
    existing_count = check_existing_data(supabase)
    
    # 3. Ler dados do CSV
    print(f"📖 Lendo dados do arquivo: {csv_file_path}")
    stocks_data = read_csv_file(csv_file_path)
    
    if not stocks_data:
        print("❌ Nenhum dado válido encontrado no arquivo CSV")
        return
    
    print(f"✅ {len(stocks_data)} ações encontradas no arquivo CSV")
    
    # 4. Exibir algumas amostras dos dados
    print("\n📊 Amostra dos dados que serão inseridos:")
    for i, stock in enumerate(stocks_data[:5]):  # Mostra apenas as primeiras 5
        print(f"  {i+1}. Ticker: {stock['ticker']}, Company: {stock['company']}, Country: {stock['country']}")
    
    if len(stocks_data) > 5:
        print(f"  ... e mais {len(stocks_data) - 5} ações")
    
    # 5. Confirmar inserção
    print(f"\n⚠️ ATENÇÃO: Você está usando a SERVICE ROLE KEY")
    print(f"📈 Dados existentes na tabela: {existing_count}")
    print(f"📥 Novos dados para inserir: {len(stocks_data)}")
    
    user_input = input(f"\n❓ Deseja inserir {len(stocks_data)} ações na tabela 'stock'? (s/n): ").lower().strip()
    
    if user_input != 's':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # 6. Inserir dados no Supabase
    print("\n💾 Inserindo dados no Supabase...")
    success = insert_stocks_to_supabase(supabase, stocks_data)
    
    if success:
        print("🎉 Processo concluído com sucesso!")
        # Verificar dados após inserção
        final_count = check_existing_data(supabase)
        print(f"📊 Total de ações na tabela após inserção: {final_count}")
    else:
        print("❌ Processo concluído com erros")


def setup_environment():
    """Carrega as variáveis de ambiente do arquivo .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Arquivo .env carregado")
    except ImportError:
        print("⚠️ python-dotenv não está instalado. Instale com: pip install python-dotenv")
        print("⚠️ Certifique-se de que as variáveis de ambiente estão definidas no sistema")


def verify_environment():
    """Verifica se as variáveis de ambiente necessárias estão definidas"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    
    print("\n🔍 Verificando variáveis de ambiente:")
    print(f"  SUPABASE_URL: {'✅ Definida' if url else '❌ Não definida'}")
    print(f"  SUPABASE_SERVICE_KEY: {'✅ Definida' if key else '❌ Não definida'}")
    
    if not url or not key:
        print("\n❌ Variáveis de ambiente faltando!")
        print("📝 Crie um arquivo .env com:")
        print("   SUPABASE_URL=https://seu-projeto.supabase.co")
        print("   SUPABASE_SERVICE_KEY=sua_service_role_key_aqui")
        return False
    
    return True


if __name__ == "__main__":
    # Configurar variáveis de ambiente
    setup_environment()
    
    # Verificar se as variáveis estão definidas
    if not verify_environment():
        exit(1)
    
    # Executar o processo principal
    main()