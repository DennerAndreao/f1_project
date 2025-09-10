from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import requests

# -----------------------------
# Configurações
# -----------------------------
POSTGRES_CONN = "postgresql+psycopg2://f1_user:f1_pass@postgres:5432/f1_db"
YEAR = 2025
ROUND_NUM = 24

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# -----------------------------
# Funções
# -----------------------------
def get_f1_race_data(year, round_num, race_type='race'):

    # Definindo a URL base da API
    base_url = 'https://f1connectapi.vercel.app/api'

    # Construindo a URL completa
    if race_type == 'race':
        url = f'{base_url}/{year}/{round_num}/race'
    elif race_type == 'sprint':
        url = f'{base_url}/{year}/{round_num}/sprint/race'
    else:
        raise ValueError("race_type deve ser 'race' ou 'sprint'")
    
    try:
        # Fazendo a requisição GET
        response = requests.get(url)

        # Tratando o caso de round inexistente
        if response.status_code == 404:
            return pd.DataFrame()
        
        # Verificando a requisição e extraindo os dados
        response.raise_for_status()
        data = response.json()

    # Tratando erros de requisição
    except requests.exceptions.RequestException as e:
        print(f"Erro: {e}")
        return pd.DataFrame()
    
    if race_type == 'race':
        # Normalizando os dados
        df = pd.json_normalize(data['races']['results'])
        # Corrigindo erro de digitação na chave 'firstAppareance'
        df = df.rename(columns={'team.firstAppareance': 'team.firstAppeareance'})
        # Criando coluna de tipo de corrida
        df['id'] = 'race'

    else:
        # Normalizando os dados
        df = pd.json_normalize(data['races']['sprintRaceResults'])
        # Corrigindo erro de digitação nas chaves
        df = df.rename(columns={'team.teamNationality': 'team.nationality', 'gridPosition': 'grid'})
        # Criando coluna de tipo de corrida
        df['id'] = 'sprint'
    
    # Setando informações da corrida
    info = {
        "season" : data['season'],
        "round" : data['races']['round'],
        "date" : data['races']['date'],
        "raceName" : data['races']['raceName'],
        "circuitId" : data['races']['circuit']['circuitId'],
        "circuitName" : data['races']['circuit']['circuitName'],
        "country" : data['races']['circuit']['country'],
        "city" : data['races']['circuit']['city']
    }
    
    # Adicionando as informações ao DataFrame
    for key, value in info.items():
        df[key] = value
    
    return df

def extract_and_load():

    # Criando DataFrame final
    df_final = pd.DataFrame()
    
    # Extraindo dados por round de todas as corridas e sprints
    for i in range(1, ROUND_NUM + 1):
        # Extraindo dados da corrida
        df_race = get_f1_race_data(YEAR, i, 'race')

        # Extraindo dados da sprint
        df_sprint = get_f1_race_data(YEAR, i, 'sprint')

        # Concatenando os DataFrames se não estiverem vazios
        dfs_to_concat = [df for df in [df_race, df_sprint] if not df.empty]

        if dfs_to_concat:
            # Concatenando os DataFrames do round atual
            current_round_df = pd.concat(dfs_to_concat, ignore_index=True)

            # Adicionando ao DataFrame final
            df_final = pd.concat([df_final, current_round_df], ignore_index=True)
    
    if not df_final.empty:
        # Conexão com o Postgres via SQLAlchemy
        engine = create_engine(POSTGRES_CONN)

        # Carregando os dados no Postgres
        df_final.to_sql('f1_results', engine, if_exists='replace', index=False)
        print(f"{len(df_final)} registros inseridos no Postgres")
    else:
        print("Nenhum dado para inserir")

# -----------------------------
# DAG
# -----------------------------
with DAG(
    "f1_pipeline",
    default_args=default_args,
    description="Pipeline diário de dados da F1",
    schedule_interval="@daily",
    start_date=datetime(2025, 9, 9),
    catchup=False,
    tags=["f1", "api", "postgres"],
) as dag:

    task_extract_load = PythonOperator(
        task_id="extract_and_load",
        python_callable=extract_and_load
    )

    task_extract_load
