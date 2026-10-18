"""Configurações do projeto lidas do arquivo .env (com valores padrão do docker-compose)."""

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_PROJETO / ".env", override=True)

# SQL Server (banco de origem)
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "1434")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SqlServer@2025!")
DB_DATABASE = os.getenv("DB_DATABASE", "LojaDB")

# Databricks
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST", "").strip()
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "").strip()
CATALOGO = os.getenv("DATABRICKS_CATALOGO", "workspace")
SCHEMA_LANDING = "landing"
VOLUME_LANDING = "dados"
CAMINHO_VOLUME = f"/Volumes/{CATALOGO}/{SCHEMA_LANDING}/{VOLUME_LANDING}"

# Pastas locais
PASTA_ORIGEM = RAIZ_PROJETO / "data" / "origem"  # CSV usados para popular o SQL Server
PASTA_LANDING = RAIZ_PROJETO / "data" / "landing"  # CSV extraídos do SQL Server

# As 5 tabelas da loja, na ordem de carga (respeita as chaves estrangeiras)
TABELAS: tuple[str, ...] = ("categoria", "cliente", "produto", "pedido", "item_pedido")
