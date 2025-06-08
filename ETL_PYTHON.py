import requests
import pandas as pd
from dotenv import load_dotenv
import os
import time
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DECIMAL, DATETIME, inspect
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import json

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define a URL da API e a chave de autenticação
url = "https://myfin-financial-management.bubbleapps.io/api/1.1/obj/transactions"
token = os.getenv("API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

# Função para chamar a API e obter todos os dados das transações em páginas.
def chamar_api_myfinance(url, constraints=None):
    lista_dados_todas_paginas = []
    cursor = 0
    params = {"cursor": cursor}
    if constraints:
        params["constraints"] = json.dumps(constraints)

    while True:
        response = requests.get(url, headers=headers, params=params)
        response_ajustado_json = response.json()
        dados_response = response_ajustado_json.get("response", None)
        
        if dados_response is not None:
            results = dados_response.get('results', [])
            remaining = dados_response.get('remaining', 0)
            lista_dados_todas_paginas.extend(results)

            if remaining <= 0:
                break
        else:
            break
        
        cursor += 100
        params["cursor"] = cursor
        time.sleep(1)

    return lista_dados_todas_paginas

# Função para atualizar os dados dos últimos dois dias
def atualizar_dados_ultimos_dois_dias():
    dois_dias_atras = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    constraints = [{"key": "estimated_date", "constraint_type": "greater than", "value": dois_dias_atras}]
    lista_dados_todas_paginas = chamar_api_myfinance(url, constraints)
    df = pd.DataFrame(lista_dados_todas_paginas)
    return df

# Converta as colunas de data para o formato aceito pelo SQL Server
data_columns = ['Modified Date', 'Created Date', 'estimated_date', 'payment_date']

# Classe para gerenciar a conexão com o banco de dados SQL Server
class ConnectionHandler:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        
        driver = "ODBC Driver 17 for SQL Server"
        connection_string = f'DRIVER={driver};SERVER={self.host};PORT=1433;DATABASE={self.db};UID={self.user};PWD={self.password};&autocommit=true'
        connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
        self.engine = create_engine(connection_url, use_setinputsizes=False, echo=False)
        self.db_connection = self.engine.connect()
    
    def insert_data(self, df, tablename):
        inseridos_com_sucesso = 0
        for index, row in df.iterrows():
            try:
                row.to_frame().T.to_sql(tablename, if_exists='append', index=False, con=self.db_connection, dtype={
                    'Modified Date': DATETIME,
                    'Created Date': DATETIME,
                    'Created By': String(255),
                    'estimated_date': DATETIME,
                    'recipient_ref': String(255),
                    'status': String(255),
                    'amount': DECIMAL(10, 2),
                    'year_ref': Integer,
                    'payment_date': DATETIME,
                    'OS_type-transaction': String(255),
                    'user_ref': String(255),
                    'cod_ref': String(255),
                    'month_ref': Integer,
                    'OS_frequency-type': String(255),
                    '_id': String(255)
                })
                inseridos_com_sucesso += 1
            except IntegrityError:
                continue  # Ignora o erro de integridade e não mostra

        return inseridos_com_sucesso

    def __del__(self):
        try:
            self.db_connection.close()
        except:
            pass

# Carrega as credenciais do banco de dados do arquivo .env
db_user = os.getenv("DB_USER_SQLSERVER")
db_password = os.getenv("DB_PASSWORD_SQLSERVER")
db_host = os.getenv("DB_HOST_SQLSERVER")
db_name = os.getenv("DB_NAME_SQLSERVER")

# Cria a conexão com o banco de dados
CH = ConnectionHandler(db_host, db_user, db_password, db_name)

metadata = MetaData()

# Cria a tabela com todas as colunas necessárias e define a chave primária
transactions_table = Table('transactions', metadata,
    Column('Modified Date', DATETIME),
    Column('Created Date', DATETIME),
    Column('Created By', String(255)),
    Column('estimated_date', DATETIME),
    Column('recipient_ref', String(255)),
    Column('status', String(255)),
    Column('amount', DECIMAL(10, 2)),
    Column('year_ref', Integer),
    Column('payment_date', DATETIME),
    Column('OS_type-transaction', String(255)),
    Column('user_ref', String(255)),
    Column('cod_ref', String(255)),
    Column('month_ref', Integer),
    Column('OS_frequency-type', String(255)),
    Column('_id', String(255), primary_key=True)
)

metadata.create_all(CH.engine)  # Cria a tabela no banco de dados

# Usar o inspetor para verificar se a tabela existe
inspector = inspect(CH.engine)
if 'transactions' in inspector.get_table_names():
    df_incremental = atualizar_dados_ultimos_dois_dias()
    if not df_incremental.empty:
        for col in data_columns:
            if col in df_incremental.columns:
                df_incremental[col] = pd.to_datetime(df_incremental[col], errors='coerce')
        inseridos_com_sucesso = CH.insert_data(df_incremental, 'transactions')
        print(f"Total de registros inseridos: {inseridos_com_sucesso}")
    else:
        print("Nenhum dado novo para atualizar. Total de registros inseridos: 0")
else:
    df_inicial = chamar_api_myfinance(url)
    df = pd.DataFrame(df_inicial)
    for col in data_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    inseridos_com_sucesso = CH.insert_data(df, 'transactions')
    print(f"Total de registros inseridos na carga inicial: {inseridos_com_sucesso}")

# Fechando a conexão explicitamente
del CH
