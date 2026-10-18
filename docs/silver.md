# Silver: Data Quality — `003_silver`

Lê as tabelas da **bronze**, aplica regras de **qualidade de dados** e grava no schema **`silver`**.

## Regras e resultado

| Código | Tabela | Regra | Registros afetados |
|---|---|---|---:|
| P01 | cliente | Nome: `trim`, espaços duplos removidos, `initcap` (só se estava todo em minúsculo/maiúsculo) | 55 |
| P02 | cliente | E-mail: `lower(trim(email))` | 62 |
| P03 | cliente | CPF: só dígitos; inválido vira `NULL` | 51 |
| P04 | cliente | UF: `upper(trim(uf))` | 30 |
| P05 | cliente | Cidade vazia → `NAO INFORMADO` | 21 |
| P06 | cliente | Mesmo CPF mais de uma vez → fica o cadastro mais antigo | **15 removidos** |
| P07 | produto | Preço negativo → valor absoluto | 6 |
| P08 | produto | Estoque negativo → 0 | 8 |
| P09 | pedido | Status: `upper(trim(status))` | 200 |
| P10 | item_pedido | Quantidade ≤ 0 → registro descartado | **25 removidos** |
| P11 | categoria | Descrição vazia → `SEM DESCRICAO` | 1 |
| — | todas | Linhas repetidas → `dropDuplicates()` | 0 |

Esses números ficam gravados na tabela **`silver.relatorio_data_quality`**, para auditoria.

```python
# P06 — mesmo CPF cadastrado mais de uma vez: fica o menor código (cadastro mais antigo)
ordem = Window.partitionBy("cpf").orderBy("id_cliente")
cliente = cliente.withColumn("_n", F.row_number().over(ordem)).filter("_n = 1").drop("_n")

# P10 — item com quantidade zero não é uma venda válida
item_pedido = item_pedido.filter("quantidade > 0")
```

## Padronização dos nomes das colunas

Mesmo padrão do notebook da aula: tudo em **MAIÚSCULAS** e siglas por extenso.

| Bronze | Silver |
|---|---|
| `id_cliente` | `CODIGO_CLIENTE` |
| `dt_pedido` | `DATA_PEDIDO` |
| `uf` | `UNIDADE_FEDERATIVA` |
| `data_hora_bronze`, `nome_arquivo` | *(removidas)* |
| — | `NOME_TABELA_BRONZE`, `DATA_HORA_SILVER` (auditoria) |

## Antes e depois

=== "Bronze"

    ```text
    6  | Beatriz Macedo        | marcela26@live.com        | 147.209.358-50 | Borges  | AC
    37 | Dr. Lucas Sá          |  CASTROMILENA@UOL.COM.BR  | 16897542300    | Freitas | CE
    28 | Maria Luísa Fernandes | rochamaya@icloud.com      | 83625701995    | NULL    | PI
    ```

=== "Silver"

    ```text
    6  | Beatriz Macedo        | marcela26@live.com        | 14720935850 | Borges        | AC
    37 | Dr. Lucas Sá          | castromilena@uol.com.br   | 16897542300 | Freitas       | CE
    28 | Maria Luísa Fernandes | rochamaya@icloud.com      | 83625701995 | NAO INFORMADO | PI
    ```

| Tabela | Bronze | Silver |
|---|---:|---:|
| cliente | 1.015 | **1.000** |
| item_pedido | 8.971 | **8.946** |
| pedido · STATUS distintos | 10 grafias | **5** (`CANCELADO`, `ENTREGUE`, `ENVIADO`, `PAGO`, `PENDENTE`) |
