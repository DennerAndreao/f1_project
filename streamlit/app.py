import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Configuração do banco
DB_USER = "f1_user"
DB_PASS = "f1_pass"
DB_HOST = "postgres"
DB_PORT = "5432"
DB_NAME = "f1_db"

# Criando engine para conexão
engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Título
st.title("🏎️ Dashboard Fórmula 1 2025")

# Consulta para ler os dados
@st.cache_data
def load_data():
    query = "SELECT * FROM f1_results"
    df = pd.read_sql(query, engine)
    return df

#DF recebe os dados
df = load_data()

# Garantir que pontos sejam numéricos
df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)

# Criar coluna "driver"
df["driver"] = df["driver.name"].astype(str) + " " + df["driver.surname"].astype(str)

# Garantir coluna de equipe sem nulos
df["team"] = df["team.teamName"].fillna("Desconhecida")

# Sidebar de filtros
st.sidebar.header("Filtros")
anos = sorted(df["season"].dropna().unique())
ano_sel = st.sidebar.selectbox("Selecione o ano", anos)

corridas = ["Todas"] + sorted(df.loc[df["season"] == ano_sel, "raceName"].dropna().unique().tolist())
corrida_sel = st.sidebar.selectbox("Selecione a corrida", corridas)

# Filtrar DataFrame
if corrida_sel == "Todas":
    df_filtered = df[df["season"] == ano_sel]
else:
    df_filtered = df[(df["season"] == ano_sel) & (df["raceName"] == corrida_sel)]

st.subheader(f"📊 Resultados - {corrida_sel} ({ano_sel})")

# Cards
st.markdown("---")

# Criar colunas para os cards
col1, col2, col3, col4 = st.columns(4)

# Calcular estatísticas
total_corridas = len(df_filtered['raceName'].unique())
corridas_race = len(df_filtered[df_filtered['id'] == 'race']['raceName'].unique())
corridas_sprint = len(df_filtered[df_filtered['id'] == 'sprint']['raceName'].unique())

# Card 1: Total de Corridas
with col1:
    st.metric(
        label="🏁 Total de Eventos",
        value=total_corridas,
        help="Total de eventos"
    )

# Card 2: Corridas Principais
with col2:
    st.metric(
        label="🎯 Corridas Principais",
        value=corridas_race,
        help="Total de corridas principais"
    )

# Card 3: Corridas Sprint
with col3:
    st.metric(
        label="⚡ Corridas Sprint",
        value=corridas_sprint,
        help="Total de corridas sprint"
    )

# Card 3: Pilotos
with col4:
    pilotos_ativos = df_filtered['driver'].nunique()
    st.metric(
        label="👥 Pilotos", 
        value=pilotos_ativos,
        help='Total de pilotos'
    )

# Cards 2
col5, col6, col7, col8 = st.columns(4)

# Card 5: Equipes
with col5:
    equipes_ativas = df_filtered['team'].nunique()
    st.metric(
        label="🏎️ Equipes", 
        value=equipes_ativas,
        help="Total de equipes"
    )

# Card 6: Pontos
with col6:
    pontos_totais = df_filtered['points'].sum()
    st.metric(
        label="⭐ Pontos Totais", 
        value=int(pontos_totais),
        help="Total de pontos"
    )

# Card 7: Calcular abandonos totais
with col7:
    abandonos_totais = len(df_filtered[df_filtered['position'].isin(['NC'])])
    st.metric(
        label="🚨 Abandonos",
        value=abandonos_totais,
        help="Total de abandonos"
    )

# Card 8: Calcular desqualificações totais
with col8:
    desquali_totais = len(df_filtered[df_filtered['position'].isin(['-'])])
    st.metric(
        label="🚨 Desqualificações",
        value=desquali_totais,
        help="Total de desqualifieds"
    )

st.markdown("### 🏁 Pontos por Piloto")
points_by_driver = (
                df_filtered.groupby("driver")["points"]
                .sum()
                .sort_values(ascending=False)
            )

st.bar_chart(points_by_driver)

# Pontos por equipe
points_by_team = (
    df_filtered.groupby("team")["points"]
    .sum()
    .sort_values(ascending=False)
)

st.markdown("### 🏎️ Pontos por Equipe")
st.bar_chart(points_by_team)

# Poles por piloto
poles = df_filtered[df_filtered['grid'] == '1']
poles_por_piloto = (
                poles.groupby('driver')
                .size()
                .sort_values(ascending=False)
            )


poles_por_equipe = (
                poles.groupby('team')
                .size()
                .sort_values(ascending=False)
            )

# NOVAS MÉTRICAS
col9, col10 = st.columns(2)

with col9:
    st.markdown("#### 🚦 Poles por Piloto")
    st.dataframe(poles_por_piloto)

with col10:
    st.markdown("#### 🚦 Poles por Equipe")
    st.dataframe(poles_por_equipe)

# Mostrar tabela bruta
st.markdown("### 📋 Dados Brutos")
st.dataframe(df_filtered)
