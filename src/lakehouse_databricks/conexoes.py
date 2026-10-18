"""Conexão com o SQL Server local e com o Databricks (para enviar os CSV ao volume)."""

import pyodbc

from lakehouse_databricks import config


def conectar_sqlserver(database: str | None = None) -> pyodbc.Connection:
    """Abre uma conexão ODBC com o SQL Server (``master`` quando ``database`` é None)."""
    banco = f"DATABASE={database};" if database else ""
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={config.DB_SERVER},{config.DB_PORT};{banco}"
        f"UID={config.DB_USER};PWD={config.DB_PASSWORD};"
        "TrustServerCertificate=yes;",
        autocommit=True,
    )


def databricks_configurado() -> bool:
    """True quando o .env tem endereço e token do Databricks."""
    return bool(config.DATABRICKS_HOST and config.DATABRICKS_TOKEN)


def cliente_databricks():
    """Cliente do Databricks SDK usando o endereço e o token do .env."""
    from databricks.sdk import WorkspaceClient

    return WorkspaceClient(host=config.DATABRICKS_HOST, token=config.DATABRICKS_TOKEN)


def garantir_volume_landing(w) -> None:
    """Cria o schema ``landing`` e o volume ``dados`` no Databricks, se não existirem."""
    from databricks.sdk.errors import NotFound
    from databricks.sdk.service.catalog import VolumeType

    try:
        w.schemas.get(f"{config.CATALOGO}.{config.SCHEMA_LANDING}")
    except NotFound:
        w.schemas.create(name=config.SCHEMA_LANDING, catalog_name=config.CATALOGO)
    try:
        w.volumes.read(f"{config.CATALOGO}.{config.SCHEMA_LANDING}.{config.VOLUME_LANDING}")
    except NotFound:
        w.volumes.create(
            catalog_name=config.CATALOGO,
            schema_name=config.SCHEMA_LANDING,
            name=config.VOLUME_LANDING,
            volume_type=VolumeType.MANAGED,
        )
