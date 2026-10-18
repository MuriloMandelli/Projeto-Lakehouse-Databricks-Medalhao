# Landing e Bronze

## Landing

Os 5 CSV extraídos do SQL Server ficam no volume **`workspace.landing.dados`**, exatamente como
saíram da origem (inclusive com os problemas de qualidade).

```python
display(dbutils.fs.ls('/Volumes/workspace/landing/dados/'))
```

## Bronze — `002_bronze`

Lê **todos** os CSV do volume e grava cada um como tabela **Delta gerenciada** no schema `bronze`.
Nenhum dado é corrigido: a bronze é uma **cópia fiel** da landing. São acrescentadas duas colunas de
**metadados de ingestão**, como no notebook da aula:

| Coluna | Conteúdo |
|---|---|
| `data_hora_bronze` | Quando o registro foi processado |
| `nome_arquivo` | Arquivo da landing de onde ele veio |

```python
for arquivo in arquivos:                      # categoria.csv, cliente.csv, ...
    tabela = arquivo.removesuffix(".csv")
    df = (spark.read.option("header", "true").option("inferSchema", "true")
                    .csv(f"{CAMINHO_LANDING}/{arquivo}")
                    .withColumn("data_hora_bronze", current_timestamp())
                    .withColumn("nome_arquivo", lit(arquivo)))
    df.write.format("delta").mode("overwrite").saveAsTable(f"bronze.{tabela}")
```

| Tabela | Registros |
|---|---:|
| `bronze.categoria` | 8 |
| `bronze.cliente` | 1.015 |
| `bronze.produto` | 200 |
| `bronze.pedido` | 3.000 |
| `bronze.item_pedido` | 8.971 |

Os problemas continuam lá — é o papel da bronze guardar o dado bruto:

```text
id_cliente | nome                  | email                     | cpf            | cidade
6          | Beatriz Macedo        | marcela26@live.com        | 147.209.358-50 | Borges
28         | Maria Luísa Fernandes | rochamaya@icloud.com      | 83625701995    | NULL
37         | Dr. Lucas Sá          |  CASTROMILENA@UOL.COM.BR  | 16897542300    | Freitas
```
