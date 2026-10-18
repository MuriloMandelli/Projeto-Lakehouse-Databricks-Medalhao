"""Gera os dados fictícios da Loja Virtual (5 tabelas) em data/origem/*.csv.

Os dados são criados com a biblioteca Faker (pt_BR) e uma semente fixa, então
toda execução gera exatamente os mesmos registros (os mesmos do Trabalho 2).

Depois, a função ``sujar`` insere de propósito PROBLEMAS DE QUALIDADE — como
acontece em sistemas reais — para que a camada Silver do lakehouse tenha o que
corrigir. Cada problema está listado em PROBLEMAS e é tratado no notebook
003_silver.

Uso:
    uv run python scripts/gerar_dados.py
"""

import csv
import random
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from faker import Faker

SEMENTE = 2026
PASTA_SAIDA = Path(__file__).resolve().parents[1] / "data" / "origem"

QTD_CLIENTES = 1000
PRODUTOS_POR_CATEGORIA = 25
QTD_PEDIDOS = 3000

# categoria -> (descrição, [(produto base, preço da versão "Lite" em R$)])
CATEGORIAS = {
    "Eletrônicos": (
        "Celulares, áudio e acessórios",
        [
            ("Smartphone", 1200),
            ("Fone Bluetooth", 150),
            ("Smartwatch", 600),
            ("Caixa de Som", 250),
            ("Carregador Turbo", 80),
        ],
    ),
    "Informática": (
        "Computadores, periféricos e armazenamento",
        [
            ("Notebook", 3200),
            ("Mouse Sem Fio", 70),
            ("Teclado Mecânico", 250),
            ("Monitor 24 pol", 800),
            ("SSD 1TB", 400),
        ],
    ),
    "Casa e Cozinha": (
        "Eletroportáteis e utensílios",
        [
            ("Air Fryer", 350),
            ("Liquidificador", 150),
            ("Cafeteira", 200),
            ("Jogo de Panelas", 300),
            ("Aspirador", 450),
        ],
    ),
    "Esporte e Lazer": (
        "Equipamentos e artigos esportivos",
        [
            ("Bicicleta Aro 29", 1300),
            ("Tênis de Corrida", 300),
            ("Bola de Futebol", 90),
            ("Halteres", 120),
            ("Tapete de Yoga", 80),
        ],
    ),
    "Moda": (
        "Roupas, calçados e acessórios",
        [
            ("Camiseta Básica", 40),
            ("Calça Jeans", 130),
            ("Jaqueta Corta-Vento", 200),
            ("Mochila", 150),
            ("Boné", 50),
        ],
    ),
    "Livros": (
        "Livros técnicos, literatura e HQs",
        [
            ("Livro de Python", 90),
            ("Romance Nacional", 45),
            ("Ficção Científica", 55),
            ("HQ", 35),
            ("Guia de SQL", 80),
        ],
    ),
    "Beleza e Saúde": (
        "Cuidados pessoais e cosméticos",
        [
            ("Secador de Cabelo", 180),
            ("Perfume 100ml", 250),
            ("Kit Skincare", 120),
            ("Barbeador", 150),
            ("Protetor Solar", 45),
        ],
    ),
    "Brinquedos": (
        "Brinquedos e jogos",
        [
            ("Blocos de Montar", 200),
            ("Quebra-Cabeça", 60),
            ("Boneca", 90),
            ("Carrinho RC", 180),
            ("Jogo de Tabuleiro", 120),
        ],
    ),
}
# Cada produto base tem 5 linhas; quanto mais "alta" a linha, maior o preço
LINHAS = [("Lite", 1.0), ("Plus", 1.3), ("Pro", 1.7), ("Max", 2.2), ("Ultra", 2.8)]
STATUS_PEDIDO = ["ENTREGUE", "ENVIADO", "PAGO", "PENDENTE", "CANCELADO"]
PESOS_STATUS = [55, 15, 10, 10, 10]


def moeda(valor: float) -> Decimal:
    return Decimal(str(valor)).quantize(Decimal("0.01"))


def gravar(nome: str, colunas: list[str], linhas: list[list]) -> None:
    caminho = PASTA_SAIDA / f"{nome}.csv"
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(colunas)
        escritor.writerows(linhas)
    print(f"{nome:<12} {len(linhas):>6} linhas -> data/origem/{caminho.name}")


# Problemas de qualidade inseridos de propósito (código -> descrição)
PROBLEMAS = {
    "P01": "cliente: nome com espaços sobrando e letras minúsculas",
    "P02": "cliente: e-mail em MAIÚSCULAS e com espaços",
    "P03": "cliente: CPF com máscara (123.456.789-01)",
    "P04": "cliente: UF em minúsculas",
    "P05": "cliente: cidade vazia (NULL)",
    "P06": "cliente: cadastro duplicado (mesmo CPF, código novo)",
    "P07": "produto: preço negativo (erro de sinal)",
    "P08": "produto: estoque negativo",
    "P09": "pedido: status escrito de formas diferentes (entregue, Pago, ' ENVIADO ')",
    "P10": "item_pedido: quantidade zero",
    "P11": "categoria: descrição vazia (NULL)",
}


def sujar(categorias, clientes, produtos, pedidos, itens) -> None:
    """Altera os dados (no lugar) inserindo os problemas listados em PROBLEMAS."""
    rnd = random.Random(SEMENTE + 1)  # gerador separado: os dados limpos não mudam

    def escolher(lista, qtd):
        return rnd.sample(lista, qtd)

    for c in escolher(clientes, 40):  # P01
        c[1] = f"  {c[1].lower()}  "
    for c in escolher(clientes, 60):  # P02
        c[2] = f" {c[2].upper()} "
    for c in escolher(clientes, 50):  # P03
        d = c[3]
        c[3] = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
    for c in escolher(clientes, 30):  # P04
        c[5] = c[5].lower()
    for c in escolher(clientes, 20):  # P05
        c[4] = None
    originais = escolher(clientes[:QTD_CLIENTES], 15)  # P06
    for i, c in enumerate(originais, start=QTD_CLIENTES + 1):
        clientes.append([i, c[1].upper(), c[2], c[3], c[4], c[5], "2026-06-01"])
    for p in escolher(produtos, 6):  # P07
        p[3] = -p[3]
    for p in escolher(produtos, 8):  # P08
        p[4] = -rnd.randint(1, 20)
    variacoes = {
        "ENTREGUE": "entregue",
        "PAGO": "Pago",
        "ENVIADO": " ENVIADO ",
        "PENDENTE": "pendente ",
        "CANCELADO": "Cancelado",
    }
    for p in escolher(pedidos, 200):  # P09
        p[3] = variacoes[p[3]]
    for it in escolher(itens, 25):  # P10
        it[3] = 0
    categorias[-1][2] = None  # P11


def main() -> None:
    random.seed(SEMENTE)
    fake = Faker("pt_BR")
    Faker.seed(SEMENTE)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    # categoria
    categorias = []
    for id_categoria, (nome, (descricao, _)) in enumerate(CATEGORIAS.items(), start=1):
        categorias.append([id_categoria, nome, descricao])

    # cliente
    clientes = []
    for id_cliente in range(1, QTD_CLIENTES + 1):
        nome = fake.name()
        usuario = fake.unique.user_name()
        clientes.append(
            [
                id_cliente,
                nome,
                f"{usuario}@{fake.free_email_domain()}",
                fake.cpf().replace(".", "").replace("-", ""),
                fake.city(),
                fake.estado_sigla(),
                fake.date_between(date(2022, 1, 1), date(2025, 12, 31)).isoformat(),
            ]
        )

    # produto
    produtos = []
    id_produto = 0
    for id_categoria, (_, (_, bases)) in enumerate(CATEGORIAS.items(), start=1):
        for i in range(PRODUTOS_POR_CATEGORIA):
            id_produto += 1
            base, preco_base = bases[i % len(bases)]
            linha, fator = LINHAS[i // len(bases)]
            nome = f"{base} {linha}"
            preco = moeda(preco_base * fator * random.uniform(0.9, 1.1))
            estoque = random.randint(0, 500)
            ativo = 0 if random.random() < 0.05 else 1
            produtos.append([id_produto, id_categoria, nome, preco, estoque, ativo])
    preco_por_produto = {p[0]: p[3] for p in produtos}

    # pedido + item_pedido
    pedidos, itens = [], []
    id_item = 0
    inicio, fim = datetime(2024, 1, 1), datetime(2026, 9, 30, 23, 59, 59)
    for id_pedido in range(1, QTD_PEDIDOS + 1):
        id_cliente = random.randint(1, QTD_CLIENTES)
        dt_pedido = fake.date_time_between(inicio, fim).replace(microsecond=0)
        status = random.choices(STATUS_PEDIDO, PESOS_STATUS)[0]
        total = Decimal("0.00")
        for produto in random.sample(list(preco_por_produto), k=random.randint(1, 5)):
            id_item += 1
            quantidade = random.randint(1, 3)
            preco = preco_por_produto[produto]
            total += preco * quantidade
            itens.append([id_item, id_pedido, produto, quantidade, preco])
        pedidos.append(
            [id_pedido, id_cliente, dt_pedido.isoformat(sep=" "), status, moeda(float(total))]
        )

    sujar(categorias, clientes, produtos, pedidos, itens)

    gravar("categoria", ["id_categoria", "nome", "descricao"], categorias)
    gravar(
        "cliente",
        ["id_cliente", "nome", "email", "cpf", "cidade", "uf", "dt_cadastro"],
        clientes,
    )
    gravar(
        "produto",
        ["id_produto", "id_categoria", "nome", "preco", "estoque", "ativo"],
        produtos,
    )
    gravar("pedido", ["id_pedido", "id_cliente", "dt_pedido", "status", "valor_total"], pedidos)
    gravar(
        "item_pedido",
        ["id_item", "id_pedido", "id_produto", "quantidade", "preco_unitario"],
        itens,
    )


if __name__ == "__main__":
    main()
