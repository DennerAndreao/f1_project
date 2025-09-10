# 🏎️ Projeto F1 Data Pipeline

Este projeto constrói um **pipeline de dados da Fórmula 1** usando **Airflow, PostgreSQL e Streamlit**, containerizados com **Docker Compose**.  
A ideia é extrair dados da API pública da Fórmula 1, carregar no banco de dados e disponibilizar um **dashboard interativo**.

---

## ⚙️ Tecnologias Utilizadas

- **Docker & Docker Compose**
- **PostgreSQL** – armazenamento dos dados
- **Airflow** – orquestração do ETL
- **Streamlit** – dashboard interativo
- **Adminer** – interface de administração para PostgreSQL
- **Python (pandas, sqlalchemy, psycopg2, plotly)**

---

## 📂 Estrutura do Projeto

```
f1_project/
│── docker-compose.yml          # Orquestração dos containers
├── airflow/                    
│   └── dags/
│       └── f1_pipeline_dag.py  # DAG
│── streamlit/
│   └── app.py                  # Dashboard
├── README.md                   # Readme
└── requirements.txt            # Dependências
```

---

## 🚀 Como Rodar

### 1. Clonar o projeto
```bash
git clone https://github.com/seu-usuario/f1_project.git
cd f1_project
```

### 2. Subir os containers
```bash
docker-compose up -d --build
```

### 3. Acessar os serviços

- **Airflow Web UI** → [http://localhost:8081](http://localhost:8081)  
  - Login: `admin` | Senha: `admin`
- **Adminer (Postgres GUI)** → [http://localhost:8082](http://localhost:8082)  
  - Server: `postgres`  
  - User: `f1_user`  
  - Password: `f1_pass`  
  - Database: `f1_db`
- **Streamlit Dashboard** → [http://localhost:8501](http://localhost:8501)

---

## 📊 Pipeline de Dados

1. **Extração** → DAG no Airflow consome dados da API da Fórmula 1  
2. **Transformação** → Normalização dos dados (pandas)  
3. **Carga** → Dados inseridos no PostgreSQL (tabela `f1_results`)  
4. **Visualização** → Dashboard em Streamlit mostrando ranking de pilotos e equipes  

---

## 🛠️ Comandos Úteis

- Ver logs do Airflow:
```bash
docker-compose logs -f airflow
```

- Acessar container do Streamlit:
```bash
docker exec -it f1_project-streamlit-1 bash
```

- Derrubar containers:
```bash
docker-compose down
```

---