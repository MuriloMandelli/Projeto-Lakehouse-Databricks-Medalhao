# Lakehouse com Databricks e arquitetura medalhão

![Databricks](https://img.shields.io/badge/Databricks-Free%20Edition-FF3621?logo=databricks&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-00ADD4)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2025-CC2927?logo=microsoftsqlserver&logoColor=white)
![Python](https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/gerenciador-uv-DE5FE9)

Trabalho 3 da disciplina de **Engenharia de Dados** (Engenharia de Software — SATC), complemento dos
[Trabalho 1](https://github.com/MuriloMandelli/Projeto-Apache-Spark---Delta-Lake-e-Apache-Iceberg) e
[Trabalho 2](https://github.com/MuriloMandelli/Projeto-Apache-Spark-MinIO-Delta).

Pipeline de dados da **Loja Virtual** no **Databricks Free Edition** (PaaS) com a **arquitetura
medalhão**, encadeado por uma **Job**:

```
SQL Server (LojaDB) ─▶ LANDING (CSV) ─▶ BRONZE (Delta) ─▶ SILVER (Data Quality) ─▶ GOLD (Kimball)
   [local: 00, 01]      [volume]          [002]              [003]                   [004]
                                    └───────────── Job no Databricks: 001 → 002 → 003 → 004 ─────────────┘
```

📘 **Documentação (MkDocs):** https://murilomandelli.github.io/Projeto-Lakehouse-Databricks-Medalhao/

👥 **Equipe:** Murilo Mandelli · Augusto Benedetti

---

## Sumário

- [Aviso](#aviso)
- [Pré-requisitos](#pré-requisitos)
- [Parte 1 — no computador (extração)](#parte-1--no-computador-extração)
- [Parte 2 — no Databricks (medalhão + Job)](#parte-2--no-databricks-medalhão--job)
- [Notebooks](#notebooks)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Testes](#testes)
- [Documentação (MkDocs)](#documentação-mkdocs)
- [Solução de problemas](#solução-de-problemas)
- [Referências](#referências)

## Aviso

> [!IMPORTANT]
> - O projeto tem **duas partes**: a **extração** roda no computador (WSL), porque o Databricks na
>   nuvem não acessa um banco em `localhost`; as camadas **bronze, silver e gold** rodam no
>   **Databricks**, encadeadas por uma **Job**.
> - As tabelas são **próprias** (Loja Virtual, 5 tabelas), diferentes das do material da aula.
> - Os dados de origem têm **problemas de qualidade inseridos de propósito** (ver `scripts/gerar_dados.py`),
>   corrigidos na camada silver.
> - **Nunca** suba o arquivo `.env` para o GitHub: ele pode conter o token do Databricks.

## Pré-requisitos

| Ferramenta | Versão testada | Para quê |
|---|---|---|
| Conta no [Databricks Free Edition](https://www.databricks.com/learn/free-edition) | — | Onde roda o lakehouse |
| Windows 11 + WSL 2 | Ubuntu 24.04 LTS | Extração local |
| Docker + Docker Compose | 29 / v2+ | SQL Server 2025 (container `lakehouse-sqlserver`, porta **1434**) |
| [uv](https://docs.astral.sh/uv/) | 0.12 | Ambiente Python 3.12 e dependências |
| ODBC Driver 18 for SQL Server | 18 | Conexão do `pyodbc` |
| Java 17 *(opcional)* | 17 | Só para `uv run task simular` (testa os notebooks do Databricks com Spark local) |

Bibliotecas (`pyproject.toml` / `uv.lock`): `pandas`, `pyodbc`, `python-dotenv`, `databricks-sdk`,
`jupyterlab`, `ipykernel`; desenvolvimento: `faker`, `mkdocs-material`, `pytest`, `ruff`,
`taskipy`, `pyspark 3.5.9` e `delta-spark 3.3.3` (simulação local).

## Parte 1 — no computador (extração)

Terminal do **Ubuntu (WSL)**. A instalação do Docker e do ODBC Driver 18 é a mesma do
[Trabalho 2](https://github.com/MuriloMandelli/Projeto-Apache-Spark-MinIO-Delta#instalação-passo-a-passo).

### 1. Clonar e instalar

```bash
git clone https://github.com/MuriloMandelli/Projeto-Lakehouse-Databricks-Medalhao.git
cd Projeto-Lakehouse-Databricks-Medalhao
```

```bash
uv sync
```

```bash
cp .env.example .env
```

### 2. (Opcional) Token do Databricks para enviar os CSV automaticamente

No Databricks: **foto do perfil ▸ Settings ▸ Developer ▸ Access tokens ▸ Generate new token**.
Edite o `.env` e preencha `DATABRICKS_HOST` (o endereço do seu workspace, ex.
`https://dbc-xxxx.cloud.databricks.com`) e `DATABRICKS_TOKEN`. Sem token, o upload é manual (passo 5
da Parte 2).

### 3. Subir o SQL Server e extrair

```bash
uv run task up
```

```bash
uv run task extrair
```

O `extrair` executa os notebooks `notebooks/local/00` (cria o banco `LojaDB` com as 5 tabelas) e
`01` (extrai **todas** as tabelas para `data/landing/*.csv` e, com token, envia para
`/Volumes/workspace/landing/dados`).

## Parte 2 — no Databricks (medalhão + Job)

### 4. Trazer os notebooks para o workspace

**Workspace ▸ Create ▸ Git folder**, cole `https://github.com/MuriloMandelli/Projeto-Lakehouse-Databricks-Medalhao`
e confirme. Os notebooks ficam em `notebooks/databricks/`.
*(Alternativa: **Workspace ▸ Import** e selecione os `.ipynb` da pasta `notebooks/databricks/`.)*

### 5. Criar o ambiente e colocar os CSV na landing

Abra **`001_preparar_ambiente`** e clique em **Run all** (cria `landing`, `bronze`, `silver`, `gold`
e o volume `landing.dados`).

Se você **não** usou token: **Catalog ▸ workspace ▸ landing ▸ dados ▸ Upload to this volume** e envie os
5 arquivos de `data/landing/`.

### 6. Criar a Job

**Jobs & Pipelines ▸ Create ▸ Job**, nome `lakehouse_loja_medalhao`, e adicione 4 tarefas do tipo
**Notebook** (compute **Serverless**), cada uma dependendo da anterior:

| Tarefa | Notebook | Depende de |
|---|---|---|
| `t1_preparar_ambiente` | `001_preparar_ambiente` | — |
| `t2_bronze` | `002_bronze` | `t1_preparar_ambiente` |
| `t3_silver` | `003_silver` | `t2_bronze` |
| `t4_gold` | `004_gold` | `t3_silver` |

A definição equivalente em JSON está em [`jobs/job_lakehouse_loja.json`](jobs/job_lakehouse_loja.json)
(troque `SEU_EMAIL` pelo seu usuário).

### 7. Executar

Clique em **Run now**. Em **Runs** aparece o grafo das 4 tarefas, executadas em sequência.

## Notebooks

| Onde | Notebook | O que faz |
|---|---|---|
| Local | `00_setup_sqlserver` | Cria o banco `LojaDB` (5 tabelas) com os dados de `data/origem/` |
| Local | `01_extracao_sqlserver_para_landing` | Extrai **todas** as tabelas para CSV e envia para o volume `landing/dados` |
| Databricks | `001_preparar_ambiente` | Schemas `landing`, `bronze`, `silver`, `gold` e volume `landing.dados` |
| Databricks | `002_bronze` | CSV → tabelas Delta na `bronze` + metadados (`data_hora_bronze`, `nome_arquivo`) |
| Databricks | `003_silver` | **Data Quality** (11 regras) + padronização de nomes de colunas + relatório |
| Databricks | `004_gold` | Modelo dimensional: `dim_cliente`, `dim_produto`, `dim_tempo`, `fato_vendas` |
| Databricks | `005_destruir_ambiente` | Apaga todos os schemas (fora da Job, uso manual) |

## Estrutura do projeto

```text
Projeto-Lakehouse-Databricks-Medalhao/
├── README.md                    ← instalação e uso
├── docker-compose.yml           ← SQL Server 2025 (porta 1434)
├── .env.example                 ← modelo das variáveis (SQL Server + Databricks)
├── pyproject.toml / uv.lock     ← dependências e atalhos (taskipy)
├── mkdocs.yml + docs/           ← site de documentação
├── assets/                      ← diagramas (ER da origem e estrela da gold)
├── data/origem/*.csv            ← dados que populam o SQL Server (com problemas de qualidade)
├── data/landing/*.csv           ← CSV extraídos do SQL Server (os que vão para o Databricks)
├── jobs/job_lakehouse_loja.json ← definição da Job
├── notebooks/local/             ← 00 e 01 (rodam no WSL)
├── notebooks/databricks/        ← 001 a 005 (rodam no Databricks)
├── scripts/gerar_dados.py       ← gera os dados com Faker e insere os problemas de qualidade
├── src/lakehouse_databricks/    ← conexão com o SQL Server e com o Databricks (SDK)
└── tests/                       ← testes dos dados e simulação local dos notebooks do Databricks
```

## Testes

```bash
uv run task test
```

```bash
uv run task simular
```

O `simular` executa os notebooks `001` a `004` num **Spark local**, com pequenas adaptações (sem
catálogo `workspace`, sem volume, sem `IDENTITY`), para validar a lógica antes de rodar no Databricks.

## Documentação (MkDocs)

```bash
uv run task docs
```

```bash
uv run task deploy
```

## Solução de problemas

<details>
<summary><b>Porta 1434 ocupada / conflito com o SQL Server do Trabalho 2</b></summary>

Este projeto usa a porta 1434 justamente para não conflitar. Se ainda assim houver erro, derrube o
outro container: `docker compose down` na pasta do Trabalho 2.

</details>

<details>
<summary><b><code>002_bronze</code> encontra 0 arquivos</b></summary>

Os CSV não estão no volume. Rode o notebook local `01` com token ou faça o upload manual em
**Catalog ▸ workspace ▸ landing ▸ dados**.

</details>

<details>
<summary><b>Erro de autenticação no envio pelo SDK</b></summary>

Confira `DATABRICKS_HOST` (sem barra no final) e `DATABRICKS_TOKEN` no `.env`. Se o token expirou,
gere outro.

</details>

<details>
<summary><b>Recomeçar do zero no Databricks</b></summary>

Rode `005_destruir_ambiente`, depois `001`, envie os CSV de novo e execute a Job.

</details>

## Referências

**Documentação oficial**

- [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition)
- [Arquitetura medalhão (Databricks)](https://www.databricks.com/br/glossary/medallion-architecture)
- [Unity Catalog — catálogos, schemas e volumes](https://docs.databricks.com/aws/en/volumes/)
- [Lakeflow Jobs (Jobs & Pipelines)](https://docs.databricks.com/aws/en/jobs/)
- [Git folders no Databricks](https://docs.databricks.com/aws/en/repos/)
- [Delta Lake — MERGE INTO](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into) · [Identity columns](https://docs.databricks.com/aws/en/delta/generated-columns#identity-columns)
- [Databricks SDK for Python — Files API](https://databricks-sdk-py.readthedocs.io/)
- [SQL Server em container Linux](https://learn.microsoft.com/pt-br/sql/linux/quickstart-install-connect-docker) · [pyodbc](https://github.com/mkleehammer/pyodbc/wiki) · [Faker](https://faker.readthedocs.io/)

**Modelagem dimensional**

- KIMBALL, Ralph; ROSS, Margy. *The Data Warehouse Toolkit*. 3. ed. Wiley, 2013.
- [Kimball Group — Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)

**Material da disciplina**

- *Ciclo de vida e pipeline de dados — Arquitetura Medalhão* (slides e enunciado do Trabalho 3)
- Notebooks da aula: *001 Preparando ambiente*, *002 Bronze*, *003 Silver*, *004 Gold*, *005 Destruindo ambiente*
- Trabalhos anteriores: [Trabalho 1](https://github.com/MuriloMandelli/Projeto-Apache-Spark---Delta-Lake-e-Apache-Iceberg) · [Trabalho 2](https://github.com/MuriloMandelli/Projeto-Apache-Spark-MinIO-Delta)

**Ferramentas:** [uv](https://docs.astral.sh/uv/) · [Docker Compose](https://docs.docker.com/compose/) · [MkDocs](https://www.mkdocs.org/) · [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

---

Projeto acadêmico — SATC · Engenharia de Dados · Prof. Jorge Luiz da Silva
