import os
import csv
import random
import string
from datetime import datetime
import configparser  # Para ler o arquivo INI

def load_folder_path_from_ini(ini_file_path):
    # Criar um objeto configparser para ler o arquivo INI
    config = configparser.ConfigParser()
    
    # Ler o arquivo INI
    config.read(ini_file_path)
    
    # Obter o valor de folder_path da seção [Settings]
    folder_path = config.get('Settings', 'folder_path')
    
    return folder_path

def combine_csv_files(folder_path):
    # Gerar um nome aleatório para o arquivo de saída
    random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    current_month_year = datetime.now().strftime("%b_%Y")  # Mês e ano atual (exemplo: Mar_2025)
    output_filename = f"{random_name}_{current_month_year}.csv"
    output_filepath = os.path.join(folder_path, output_filename)
    
    all_rows = []  # Lista para armazenar todas as linhas combinadas
    header = ['Keyword', 'Value Before', 'Value After', 'Date', 'Playing Time', 'Start Time', 'Duration']  # Cabeçalho fixo
    
    # Processar os arquivos CSV na pasta
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            csv_filepath = os.path.join(folder_path, filename)
            
            # Abrir cada arquivo CSV na pasta
            with open(csv_filepath, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                # Ler o cabeçalho
                next(reader)  # Ignorar o cabeçalho do arquivo atual
                
                # Adicionar os dados do arquivo CSV na lista
                for row in reader:
                    all_rows.append(row)
    
    # Ordenar as linhas pela coluna "Keyword" (índice 1)
    all_rows_sorted = sorted(all_rows, key=lambda x: x[0])  # Ordena pela primeira coluna, que é "Keyword"

    # Escrever os dados no arquivo CSV final
    with open(output_filepath, mode='w', newline='', encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        
        # Escrever o cabeçalho fixo
        writer.writerow(header)
        
        # Escrever todas as linhas ordenadas no arquivo CSV
        writer.writerows(all_rows_sorted)

    print(f"Arquivo CSV combinado e ordenado gerado: {output_filepath}")
    return output_filepath


if __name__ == "__main__":
    # Caminho do arquivo INI com a configuração
    ini_file_path = 'config.ini'  # Substitua pelo caminho do seu arquivo INI

    # Obter o caminho da pasta a partir do arquivo INI
    folder_path = load_folder_path_from_ini(ini_file_path)

    # Processar todos os CSVs na pasta
    combine_csv_files(folder_path)
