"""Valida os CSV de origem (com os problemas de qualidade propositais) e os extraídos."""

import csv

import pytest

from lakehouse_databricks.config import PASTA_LANDING, PASTA_ORIGEM, TABELAS


def ler(pasta, tabela: str) -> list[dict]:
    with (pasta / f"{tabela}.csv").open(encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def test_sao_cinco_tabelas():
    assert TABELAS == ("categoria", "cliente", "produto", "pedido", "item_pedido")


@pytest.mark.parametrize("tabela", TABELAS)
def test_origem_existe(tabela):
    assert ler(PASTA_ORIGEM, tabela), f"{tabela}.csv vazio — rode `uv run task dados`"


@pytest.mark.parametrize(
    "filha, coluna, pai, chave",
    [
        ("produto", "id_categoria", "categoria", "id_categoria"),
        ("pedido", "id_cliente", "cliente", "id_cliente"),
        ("item_pedido", "id_pedido", "pedido", "id_pedido"),
        ("item_pedido", "id_produto", "produto", "id_produto"),
    ],
)
def test_chaves_estrangeiras_existem(filha, coluna, pai, chave):
    existentes = {linha[chave] for linha in ler(PASTA_ORIGEM, pai)}
    assert not {linha[coluna] for linha in ler(PASTA_ORIGEM, filha)} - existentes


def test_origem_tem_os_problemas_de_qualidade_esperados():
    clientes = ler(PASTA_ORIGEM, "cliente")
    produtos = ler(PASTA_ORIGEM, "produto")
    itens = ler(PASTA_ORIGEM, "item_pedido")
    status = {p["status"] for p in ler(PASTA_ORIGEM, "pedido")}

    assert any("." in c["cpf"] for c in clientes)  # P03
    assert any(c["email"] != c["email"].strip().lower() for c in clientes)  # P02
    assert (
        len(clientes) - len({c["cpf"].replace(".", "").replace("-", "") for c in clientes}) == 15
    )  # P06
    assert any(float(p["preco"]) < 0 for p in produtos)  # P07
    assert sum(int(i["quantidade"]) == 0 for i in itens) == 25  # P10
    assert "entregue" in status and "ENTREGUE" in status  # P09


@pytest.mark.parametrize("tabela", TABELAS)
def test_landing_tem_o_mesmo_numero_de_linhas_da_origem(tabela):
    if not (PASTA_LANDING / f"{tabela}.csv").exists():
        pytest.skip("rode o notebook local 01 para gerar data/landing")
    assert len(ler(PASTA_LANDING, tabela)) == len(ler(PASTA_ORIGEM, tabela))
