import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
np.random.seed(SEED)
random.seed(SEED)
fake = Faker("pt_BR")
Faker.seed(SEED)
fake.seed_instance(SEED)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATE_START = pd.Timestamp("2022-01-01")
DATE_END = pd.Timestamp("2025-12-31")

N_LOJAS = 15
N_FORNECEDORES = 40
N_PRODUTOS = 500
N_CLIENTES = 10_000
N_FUNCIONARIOS = 150
N_VENDAS_ITENS = 220_000
MAX_ROWS_PER_SHEET = 1_000_000
N_ESTOQUE = 105_000
N_COMPRAS = 5_000
N_ATENDIMENTOS = 20_000

REGIAO_MAP = {
    "SP": "Sudeste",
    "RJ": "Sudeste",
    "MG": "Sudeste",
    "ES": "Sudeste",
    "PR": "Sul",
    "SC": "Sul",
    "RS": "Sul",
    "BA": "Nordeste",
    "PE": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "GO": "Centro-Oeste",
}

CATEGORIAS = {
    "Whey Protein": ["Concentrado", "Isolado", "Hidrolisado", "Blend"],
    "Creatina": ["Monohidratada", "Micronizada", "Creapure"],
    "BCAA": ["2:1:1", "4:1:1", "Tabletes"],
    "Pré-treino": ["Estimulante", "Sem cafeína", "Pump"],
    "Hipercalórico": ["Mass Gainer", "Alto Carbo", "Proteico"],
    "Termogênico": ["Cafeína", "Capsulas", "Natural"],
    "Vitaminas": ["Vitamina C", "Vitamina D", "Complexo B"],
    "Multivitamínico": ["Masculino", "Feminino", "Sênior"],
    "Ômega 3": ["EPA/DHA", "Ultra Concentrado", "TG"],
    "Colágeno": ["Hidrolisado", "Tipo II", "Com Vitamina C"],
    "Barras Proteicas": ["Low Carb", "Alta Proteína", "Vegan"],
    "Pasta de Amendoim": ["Integral", "Com Whey", "Com Chocolate"],
    "Acessórios": ["Luva", "Cinto", "Faixa"],
    "Roupas": ["Camiseta", "Regata", "Legging"],
    "Coqueteleiras": ["600ml", "700ml", "Com mola"],
}

MARCAS = [
    "Growth",
    "Max Titanium",
    "Integralmédica",
    "Probiótica",
    "Optimum Nutrition",
    "Black Skull",
    "Dux Nutrition",
    "Athletica",
    "Dark Lab",
    "Universal",
]

SABORES = [
    "Chocolate",
    "Baunilha",
    "Morango",
    "Cookies",
    "Doce de Leite",
    "Sem Sabor",
    "Banana",
    "Cappuccino",
]

FORMAS_PAGAMENTO = ["Dinheiro", "Pix", "Cartão Débito", "Cartão Crédito", "Boleto"]
CANAIS_VENDA = ["Loja Física", "E-commerce", "WhatsApp", "Marketplace"]
CARGOS = [
    "Vendedor",
    "Caixa",
    "Gerente",
    "Subgerente",
    "Repositor",
    "Auxiliar de Limpeza",
    "Segurança",
    "Estoquista",
    "Nutricionista",
]

SALARIO_BASE_CARGO = {
    "Vendedor": (1700, 2200),
    "Caixa": (1800, 2400),
    "Gerente": (4600, 6200),
    "Subgerente": (3200, 4500),
    "Repositor": (1700, 2200),
    "Auxiliar de Limpeza": (1450, 1800),
    "Segurança": (1700, 2600),
    "Estoquista": (1900, 2600),
    "Nutricionista": (3200, 5000),
}

FERIADOS_FIXOS = {
    "01-01": "Confraternização Universal",
    "04-21": "Tiradentes",
    "05-01": "Dia do Trabalhador",
    "09-07": "Independência do Brasil",
    "10-12": "Nossa Senhora Aparecida",
    "11-02": "Finados",
    "11-15": "Proclamação da República",
    "12-25": "Natal",
}


def _rand_from_range(start: pd.Timestamp, end: pd.Timestamp, n: int) -> pd.Series:
    delta = (end - start).days
    return pd.to_datetime(np.random.randint(0, delta + 1, n), unit="D", origin=start)


def _generate_dim_fornecedores() -> pd.DataFrame:
    estados = list(REGIAO_MAP.keys())
    categorias = list(CATEGORIAS.keys())
    data = []
    for i in range(1, N_FORNECEDORES + 1):
        estado = random.choice(estados)
        data.append(
            {
                "id_fornecedor": i,
                "razao_social": fake.company() + " LTDA",
                "nome_fantasia": fake.company(),
                "cnpj": fake.cnpj(),
                "inscricao_estadual": str(np.random.randint(10**8, 10**9 - 1)),
                "endereco": fake.street_address(),
                "cidade": fake.city(),
                "estado": estado,
                "pais": "Brasil",
                "contato_nome": fake.name(),
                "contato_email": fake.company_email(),
                "contato_telefone": fake.phone_number(),
                "prazo_entrega_dias": int(np.random.randint(3, 21)),
                "condicao_pagamento": random.choice(
                    ["14 dias", "21 dias", "28 dias", "30 dias", "45 dias"]
                ),
                "avaliacao": int(np.random.randint(1, 6)),
                "data_inicio_parceria": _rand_from_range(
                    pd.Timestamp("2018-01-01"), DATE_END, 1
                )[0].date(),
                "categoria_principal": random.choice(categorias),
            }
        )
    return pd.DataFrame(data)


def _generate_dim_produtos(df_fornecedores: pd.DataFrame) -> pd.DataFrame:
    data = []
    fornecedores_ids = df_fornecedores["id_fornecedor"].to_numpy()
    categorias = list(CATEGORIAS.keys())

    for i in range(1, N_PRODUTOS + 1):
        categoria = random.choice(categorias)
        subcategoria = random.choice(CATEGORIAS[categoria])
        marca = random.choice(MARCAS)

        if categoria == "Whey Protein":
            peso = random.choice([900, 1000, 1800, 2000])
            preco_venda = round(np.random.uniform(90, 250), 2)
        elif categoria == "Creatina":
            peso = random.choice([150, 300, 500])
            preco_venda = round(np.random.uniform(70, 180), 2)
        elif categoria in {"Barras Proteicas", "Pasta de Amendoim"}:
            peso = random.choice([35, 60, 450, 600, 1000])
            preco_venda = round(np.random.uniform(8, 65), 2)
        elif categoria in {"Coqueteleiras", "Acessórios", "Roupas"}:
            peso = np.nan
            preco_venda = round(np.random.uniform(25, 220), 2)
        else:
            peso = random.choice([60, 120, 300, 500, 900])
            preco_venda = round(np.random.uniform(35, 210), 2)

        margem = round(np.random.uniform(0.2, 0.55), 4)
        preco_custo = round(preco_venda * (1 - margem), 2)

        data.append(
            {
                "id_produto": i,
                "sku": f"SKU-{i:06d}",
                "codigo_barras_ean": str(np.random.randint(10**12, 10**13 - 1)),
                "nome_produto": f"{categoria} {marca} {subcategoria}",
                "categoria": categoria,
                "subcategoria": subcategoria,
                "marca": marca,
                "sabor": random.choice(SABORES)
                if categoria not in {"Acessórios", "Roupas", "Coqueteleiras"}
                else "N/A",
                "peso_gramas": peso,
                "volume_ml": random.choice([300, 500, 600, 700])
                if categoria == "Coqueteleiras"
                else np.nan,
                "tipo_embalagem": random.choice(
                    ["Pote", "Sachê", "Caixa", "Refil", "Unidade"]
                ),
                "id_fornecedor": int(np.random.choice(fornecedores_ids)),
                "preco_custo": preco_custo,
                "preco_venda": preco_venda,
                "margem_percentual": round(
                    (preco_venda - preco_custo) / preco_venda * 100, 2
                ),
                "tributacao_ncm": str(np.random.randint(10**8, 10**9 - 1)),
                "aliquota_icms": random.choice([7.0, 12.0, 18.0]),
                "data_cadastro": _rand_from_range(
                    pd.Timestamp("2019-01-01"), DATE_END, 1
                )[0].date(),
                "ativo": random.choices([True, False], weights=[0.93, 0.07], k=1)[0],
                "controlado_anvisa": random.choices(
                    [True, False], weights=[0.08, 0.92], k=1
                )[0],
                "validade_meses": int(np.random.randint(6, 37)),
            }
        )

    return pd.DataFrame(data)


def _generate_dim_lojas() -> pd.DataFrame:
    cidades = [
        ("São Paulo", "SP"),
        ("Campinas", "SP"),
        ("Rio de Janeiro", "RJ"),
        ("Belo Horizonte", "MG"),
        ("Vitória", "ES"),
        ("Curitiba", "PR"),
        ("Florianópolis", "SC"),
        ("Porto Alegre", "RS"),
        ("Salvador", "BA"),
        ("Recife", "PE"),
        ("Fortaleza", "CE"),
        ("Brasília", "DF"),
        ("Goiânia", "GO"),
        ("São José dos Campos", "SP"),
        ("Niterói", "RJ"),
    ]

    data = []
    for i in range(1, N_LOJAS + 1):
        cidade, estado = cidades[i - 1]
        data.append(
            {
                "id_loja": i,
                "nome_loja": f"Sety Suplementos {cidade}",
                "codigo_loja": f"LJ-{i:03d}",
                "cnpj": fake.cnpj(),
                "endereco": fake.street_address(),
                "bairro": fake.bairro(),
                "cidade": cidade,
                "estado": estado,
                "regiao": REGIAO_MAP[estado],
                "cep": fake.postcode(),
                "telefone": fake.phone_number(),
                "data_abertura": _rand_from_range(
                    pd.Timestamp("2014-01-01"), pd.Timestamp("2025-01-01"), 1
                )[0].date(),
                "area_m2": int(np.random.randint(25, 280)),
                "tipo_loja": random.choices(
                    ["Rua", "Shopping", "Quiosque", "Online"],
                    weights=[0.5, 0.3, 0.1, 0.1],
                    k=1,
                )[0],
                "gerente_responsavel_id": np.nan,
                "latitude": round(float(np.random.uniform(-30.0, 1.0)), 6),
                "longitude": round(float(np.random.uniform(-73.0, -34.0)), 6),
                "status": random.choices(
                    ["Ativa", "Inativa", "Reforma"], weights=[0.86, 0.08, 0.06], k=1
                )[0],
            }
        )
    return pd.DataFrame(data)


def _generate_dim_clientes(df_lojas: pd.DataFrame) -> pd.DataFrame:
    lojas_ids = df_lojas["id_loja"].to_numpy()
    objetivos = ["Hipertrofia", "Emagrecimento", "Performance", "Saúde", "Definição"]
    niveis = ["Iniciante", "Intermediário", "Avançado"]
    data = []
    for i in range(1, N_CLIENTES + 1):
        data_nascimento = _rand_from_range(
            pd.Timestamp("1955-01-01"), pd.Timestamp("2008-12-31"), 1
        )[0]
        data_cadastro = _rand_from_range(pd.Timestamp("2020-01-01"), DATE_END, 1)[0]
        data.append(
            {
                "id_cliente": i,
                "nome": fake.name(),
                "cpf": fake.cpf(),
                "data_nascimento": data_nascimento.date(),
                "genero": random.choice(["Masculino", "Feminino", "Outro"]),
                "email": fake.email(),
                "telefone": fake.phone_number(),
                "cep": fake.postcode(),
                "endereco": fake.street_address(),
                "cidade": fake.city(),
                "estado": random.choice(list(REGIAO_MAP.keys())),
                "data_cadastro": data_cadastro.date(),
                "loja_origem_id": int(np.random.choice(lojas_ids)),
                "aceita_marketing": random.choices(
                    [True, False], weights=[0.75, 0.25], k=1
                )[0],
                "programa_fidelidade": random.choices(
                    ["Bronze", "Prata", "Ouro", "Diamante", "Sem"],
                    weights=[0.3, 0.25, 0.2, 0.08, 0.17],
                    k=1,
                )[0],
                "pontos_acumulados": int(np.random.randint(0, 25000)),
                "objetivo_treino": random.choice(objetivos),
                "nivel_atividade": random.choice(niveis),
                "frequencia_compra_estimada_dias": int(np.random.randint(7, 95)),
            }
        )
    return pd.DataFrame(data)


def _generate_dim_funcionarios(df_lojas: pd.DataFrame):
    lojas_ids = df_lojas["id_loja"].to_numpy()
    cargo_choices = np.random.choice(
        CARGOS,
        size=N_FUNCIONARIOS,
        p=[0.42, 0.12, 0.10, 0.08, 0.08, 0.07, 0.05, 0.06, 0.02],
    )

    data = []
    for i in range(1, N_FUNCIONARIOS + 1):
        cargo = str(cargo_choices[i - 1])
        salario_min, salario_max = SALARIO_BASE_CARGO[cargo]
        admissao = _rand_from_range(pd.Timestamp("2018-01-01"), DATE_END, 1)[0]
        demitido = random.choices([True, False], weights=[0.15, 0.85], k=1)[0]
        data_demissao = (
            _rand_from_range(
                max(admissao + pd.Timedelta(days=90), pd.Timestamp("2019-01-01")),
                DATE_END,
                1,
            )[0]
            if demitido and admissao < DATE_END - pd.Timedelta(days=90)
            else pd.NaT
        )
        if pd.notna(data_demissao) and data_demissao < admissao:
            data_demissao = pd.NaT

        percentual = 0.0
        if cargo == "Vendedor":
            percentual = round(float(np.random.uniform(0.01, 0.04)), 4)
        elif cargo == "Gerente":
            percentual = round(float(np.random.uniform(0.005, 0.02)), 4)

        data.append(
            {
                "id_funcionario": i,
                "nome": fake.name(),
                "cpf": fake.cpf(),
                "rg": str(np.random.randint(10**7, 10**9 - 1)),
                "data_nascimento": _rand_from_range(
                    pd.Timestamp("1965-01-01"), pd.Timestamp("2004-12-31"), 1
                )[0].date(),
                "genero": random.choice(["Masculino", "Feminino", "Outro"]),
                "email": fake.email(),
                "telefone": fake.phone_number(),
                "cargo": cargo,
                "departamento": random.choice(
                    ["Vendas", "Operações", "Administrativo", "Atendimento"]
                ),
                "id_loja": int(np.random.choice(lojas_ids)),
                "data_admissao": admissao.date(),
                "data_demissao": data_demissao.date() if pd.notna(data_demissao) else pd.NaT,
                "salario_base": round(float(np.random.uniform(salario_min, salario_max)), 2),
                "percentual_comissao": percentual,
                "meta_mensal_vendas": round(float(np.random.uniform(25_000, 160_000)), 2)
                if cargo in {"Vendedor", "Gerente"}
                else 0.0,
                "tipo_contrato": random.choice(["CLT", "PJ", "Temporário"]),
                "carga_horaria_semanal": random.choice([30, 36, 40, 44]),
                "status": "Inativo" if pd.notna(data_demissao) else "Ativo",
            }
        )

    df = pd.DataFrame(data)
    for loja_id in df_lojas["id_loja"]:
        gerentes = df[
            (df["id_loja"] == loja_id)
            & (df["cargo"] == "Gerente")
            & (df["status"] == "Ativo")
        ]
        if gerentes.empty:
            idx = df[(df["id_loja"] == loja_id)].sample(1, random_state=SEED).index[0]
            df.loc[idx, "cargo"] = "Gerente"
            df.loc[idx, "percentual_comissao"] = round(
                float(np.random.uniform(0.005, 0.02)), 4
            )
            df.loc[idx, "meta_mensal_vendas"] = round(
                float(np.random.uniform(45_000, 180_000)), 2
            )
            df.loc[idx, "salario_base"] = round(float(np.random.uniform(4600, 6200)), 2)
            df.loc[idx, "status"] = "Ativo"
            df.loc[idx, "data_demissao"] = pd.NaT
            gerente_id = int(df.loc[idx, "id_funcionario"])
        else:
            gerente_id = int(gerentes.sample(1, random_state=SEED).iloc[0]["id_funcionario"])
        df_lojas.loc[df_lojas["id_loja"] == loja_id, "gerente_responsavel_id"] = gerente_id

    return df, df_lojas


def _generate_dim_calendario() -> pd.DataFrame:
    meses_pt = {
        1: "janeiro",
        2: "fevereiro",
        3: "março",
        4: "abril",
        5: "maio",
        6: "junho",
        7: "julho",
        8: "agosto",
        9: "setembro",
        10: "outubro",
        11: "novembro",
        12: "dezembro",
    }
    dias_pt = {
        0: "segunda-feira",
        1: "terça-feira",
        2: "quarta-feira",
        3: "quinta-feira",
        4: "sexta-feira",
        5: "sábado",
        6: "domingo",
    }
    calendar = pd.DataFrame({"data": pd.date_range(DATE_START, DATE_END, freq="D")})
    calendar["ano"] = calendar["data"].dt.year
    calendar["trimestre"] = calendar["data"].dt.quarter
    calendar["mes"] = calendar["data"].dt.month
    calendar["nome_mes"] = calendar["mes"].map(meses_pt)
    calendar["semana_ano"] = calendar["data"].dt.isocalendar().week.astype(int)
    calendar["dia"] = calendar["data"].dt.day
    calendar["dia_semana"] = calendar["data"].dt.weekday + 1
    calendar["nome_dia_semana"] = calendar["data"].dt.weekday.map(dias_pt)
    calendar["eh_fim_semana"] = calendar["data"].dt.weekday >= 5
    calendar["eh_feriado"] = calendar["data"].dt.strftime("%m-%d").isin(FERIADOS_FIXOS.keys())
    calendar["nome_feriado"] = np.where(
        calendar["eh_feriado"], calendar["data"].dt.strftime("%m-%d").map(FERIADOS_FIXOS), ""
    )
    calendar["bimestre"] = ((calendar["mes"] - 1) // 2) + 1
    calendar["semestre"] = np.where(calendar["mes"] <= 6, 1, 2)
    return calendar


def _generate_sales_dates(n_sales: int) -> np.ndarray:
    dates = pd.date_range(DATE_START, DATE_END, freq="D")
    month_factor = {
        1: 1.30,
        2: 1.00,
        3: 1.05,
        4: 1.00,
        5: 0.80,
        6: 0.78,
        7: 0.95,
        8: 1.00,
        9: 1.20,
        10: 1.25,
        11: 1.10,
        12: 1.05,
    }
    weekday_factor = {0: 0.95, 1: 0.98, 2: 1.0, 3: 1.07, 4: 1.20, 5: 1.25, 6: 0.80}
    probs = np.array([month_factor[d.month] * weekday_factor[d.weekday()] for d in dates], dtype=float)
    probs = probs / probs.sum()
    return np.random.choice(dates.to_numpy(), size=n_sales, p=probs)


def _generate_sales_hours(n_sales: int) -> np.ndarray:
    hours = np.arange(9, 23)
    weights = np.array([0.5, 0.6, 0.9, 1.3, 1.35, 1.0, 0.9, 0.95, 1.05, 1.3, 1.35, 1.25, 0.95, 0.7])
    weights = weights / weights.sum()
    selected_hours = np.random.choice(hours, size=n_sales, p=weights)
    minutes = np.random.randint(0, 60, size=n_sales)
    seconds = np.random.randint(0, 60, size=n_sales)
    return np.array([f"{h:02d}:{m:02d}:{s:02d}" for h, m, s in zip(selected_hours, minutes, seconds)])


def _generate_fato_vendas(df_lojas, df_clientes, df_funcionarios, df_produtos) -> pd.DataFrame:
    n_sales = 92_000
    item_counts = np.random.choice([1, 2, 3, 4, 5], size=n_sales, p=[0.42, 0.30, 0.17, 0.08, 0.03])
    diff = N_VENDAS_ITENS - item_counts.sum()
    while diff != 0:
        idx = np.random.randint(0, n_sales)
        if diff > 0 and item_counts[idx] < 5:
            item_counts[idx] += 1
            diff -= 1
        elif diff < 0 and item_counts[idx] > 1:
            item_counts[idx] -= 1
            diff += 1

    sale_ids = np.repeat(np.arange(1, n_sales + 1), item_counts)
    n_items = len(sale_ids)
    dates_sale = _generate_sales_dates(n_sales)
    sale_hours = _generate_sales_hours(n_sales)

    vendedores = df_funcionarios[df_funcionarios["cargo"].isin(["Vendedor", "Gerente"])][
        ["id_funcionario", "percentual_comissao", "id_loja"]
    ]
    sale_store = np.random.choice(df_lojas["id_loja"], size=n_sales)
    sale_client = np.where(
        np.random.rand(n_sales) < 0.18,
        np.nan,
        np.random.choice(df_clientes["id_cliente"], size=n_sales),
    )

    vendedores_by_store = {
        loja_id: grp["id_funcionario"].to_numpy() for loja_id, grp in vendedores.groupby("id_loja")
    }
    any_vendedores = vendedores["id_funcionario"].to_numpy()
    sale_vendedor = []
    for loja_id in sale_store:
        options = vendedores_by_store.get(loja_id)
        sale_vendedor.append(int(np.random.choice(options if options is not None and len(options) else any_vendedores)))
    sale_vendedor = np.array(sale_vendedor)

    sale_df = pd.DataFrame(
        {
            "id_venda": np.arange(1, n_sales + 1),
            "data_venda": pd.to_datetime(dates_sale).date,
            "hora_venda": sale_hours,
            "id_loja": sale_store,
            "id_cliente": sale_client,
            "id_vendedor": sale_vendedor,
            "forma_pagamento": np.random.choice(FORMAS_PAGAMENTO, size=n_sales, p=[0.05, 0.35, 0.22, 0.35, 0.03]),
            "parcelas": np.random.choice([1, 1, 1, 2, 3, 4, 6], size=n_sales),
            "cupom_promocional": np.where(
                np.random.rand(n_sales) < 0.28,
                np.random.choice(
                    ["JANFIT", "PROTEINA10", "CREATINA15", "SEMANAWHEY", "QUEIMA5"],
                    size=n_sales,
                ),
                "",
            ),
            "canal_venda": np.random.choice(CANAIS_VENDA, size=n_sales, p=[0.62, 0.23, 0.1, 0.05]),
        }
    )

    item_df = pd.DataFrame({"id_venda": sale_ids})
    item_df["id_venda_item"] = np.arange(1, n_items + 1)
    item_df = item_df.merge(sale_df, on="id_venda", how="left")
    item_df["id_produto"] = np.random.choice(df_produtos["id_produto"], size=n_items)
    item_df["quantidade"] = np.random.choice([1, 2, 3, 4], size=n_items, p=[0.73, 0.2, 0.06, 0.01])

    prod_info = df_produtos[["id_produto", "preco_venda", "preco_custo"]].set_index("id_produto")
    item_df["preco_unitario"] = (
        prod_info.loc[item_df["id_produto"], "preco_venda"].to_numpy() * np.random.uniform(0.95, 1.05, n_items)
    ).round(2)
    item_df["desconto_percentual"] = np.where(
        item_df["cupom_promocional"] != "",
        np.random.uniform(0.03, 0.18, n_items),
        np.random.uniform(0, 0.08, n_items),
    ).round(4)
    item_df["valor_bruto"] = (item_df["quantidade"] * item_df["preco_unitario"]).round(2)
    item_df["desconto_valor"] = (item_df["valor_bruto"] * item_df["desconto_percentual"]).round(2)
    item_df["valor_liquido"] = (item_df["valor_bruto"] - item_df["desconto_valor"]).round(2)
    item_df["custo_unitario"] = (
        prod_info.loc[item_df["id_produto"], "preco_custo"].to_numpy() * np.random.uniform(0.97, 1.03, n_items)
    ).round(2)

    comissao_map = df_funcionarios.set_index("id_funcionario")["percentual_comissao"].to_dict()
    item_df["comissao_calculada"] = (
        item_df["valor_liquido"] * item_df["id_vendedor"].map(comissao_map).fillna(0.0)
    ).round(2)
    item_df["margem_bruta_item"] = (
        item_df["valor_liquido"] - (item_df["custo_unitario"] * item_df["quantidade"])
    ).round(2)
    item_df["id_cliente"] = item_df["id_cliente"].astype("Int64")

    return item_df[
        [
            "id_venda_item",
            "id_venda",
            "data_venda",
            "hora_venda",
            "id_loja",
            "id_cliente",
            "id_vendedor",
            "id_produto",
            "quantidade",
            "preco_unitario",
            "desconto_percentual",
            "desconto_valor",
            "valor_bruto",
            "valor_liquido",
            "forma_pagamento",
            "parcelas",
            "cupom_promocional",
            "canal_venda",
            "comissao_calculada",
            "custo_unitario",
            "margem_bruta_item",
        ]
    ]


def _generate_fato_estoque(df_lojas, df_produtos):
    snapshot_dates = pd.to_datetime(
        np.unique(np.linspace(0, len(pd.date_range(DATE_START, DATE_END)) - 1, 14, dtype=int)),
        unit="D",
        origin=DATE_START,
    )
    combos = pd.MultiIndex.from_product(
        [snapshot_dates.date, df_lojas["id_loja"], df_produtos["id_produto"]],
        names=["data_snapshot", "id_loja", "id_produto"],
    ).to_frame(index=False)
    if len(combos) > N_ESTOQUE:
        combos = combos.sample(N_ESTOQUE, random_state=SEED).reset_index(drop=True)

    min_qtd = np.random.randint(5, 26, len(combos))
    max_qtd = min_qtd + np.random.randint(25, 220, len(combos))
    qtd = np.random.randint(0, max_qtd + 1)
    status = np.where(
        qtd == 0,
        "Ruptura",
        np.where(qtd < min_qtd, "Baixo", np.where(qtd > max_qtd * 0.9, "Excesso", "OK")),
    )

    custo_map = df_produtos.set_index("id_produto")["preco_custo"]
    combos["quantidade_em_estoque"] = qtd
    combos["quantidade_minima"] = min_qtd
    combos["quantidade_maxima"] = max_qtd
    combos["status_estoque"] = status
    combos["valor_estoque_custo"] = (combos["id_produto"].map(custo_map).fillna(0) * qtd).round(2)
    combos["dias_cobertura_estimados"] = np.where(qtd == 0, 0, np.random.randint(3, 120, len(combos)))
    return combos


def _generate_fato_compras(df_lojas, df_fornecedores, df_produtos):
    data_pedido = _rand_from_range(DATE_START, DATE_END, N_COMPRAS)
    lead_time = np.random.randint(3, 25, N_COMPRAS)
    atraso = np.random.randint(-2, 8, N_COMPRAS)
    data_prevista = data_pedido + pd.to_timedelta(lead_time, unit="D")
    data_real = data_prevista + pd.to_timedelta(atraso, unit="D")

    produtos = np.random.choice(df_produtos["id_produto"], size=N_COMPRAS)
    custo_prod = df_produtos.set_index("id_produto")["preco_custo"]
    qtd = np.random.randint(20, 600, N_COMPRAS)
    custo = (custo_prod.loc[produtos].to_numpy() * np.random.uniform(0.9, 1.05, N_COMPRAS)).round(2)

    return pd.DataFrame(
        {
            "id_compra": np.arange(1, N_COMPRAS + 1),
            "id_fornecedor": np.random.choice(df_fornecedores["id_fornecedor"], size=N_COMPRAS),
            "id_loja_destino": np.random.choice(df_lojas["id_loja"], size=N_COMPRAS),
            "id_produto": produtos,
            "data_pedido": data_pedido.date,
            "data_entrega_prevista": data_prevista.date,
            "data_entrega_real": data_real.date,
            "quantidade": qtd,
            "preco_custo_unitario": custo,
            "valor_total": (qtd * custo).round(2),
            "status": np.where(
                data_real <= data_prevista,
                "Entregue",
                np.where(data_real > data_prevista + pd.Timedelta(days=4), "Atrasado", "Parcial"),
            ),
            "numero_nota_fiscal": [f"NF-{x:08d}" for x in np.random.randint(1, 9_999_999, N_COMPRAS)],
        }
    )


def _generate_fato_metas(df_funcionarios, df_vendas):
    meses = pd.period_range(DATE_START, DATE_END, freq="M")
    vendedores = df_funcionarios[df_funcionarios["cargo"].isin(["Vendedor", "Gerente"])].copy()
    realizado = (
        df_vendas.groupby(["id_vendedor", pd.to_datetime(df_vendas["data_venda"]).dt.to_period("M")])["valor_liquido"]
        .sum()
        .rename("realizado_valor")
        .reset_index()
    )

    rows = []
    for _, func in vendedores.iterrows():
        meta_base = func["meta_mensal_vendas"] if func["meta_mensal_vendas"] > 0 else np.random.uniform(30_000, 100_000)
        for mes in meses:
            meta = round(float(meta_base * np.random.uniform(0.85, 1.2)), 2)
            real_match = realizado[
                (realizado["id_vendedor"] == func["id_funcionario"]) & (realizado["data_venda"] == mes)
            ]
            real = float(real_match["realizado_valor"].iloc[0]) if not real_match.empty else 0.0
            pct = round((real / meta) * 100, 2) if meta > 0 else 0.0
            comissao = round(real * func["percentual_comissao"], 2)
            bonus = round(real * 0.01, 2) if func["cargo"] == "Gerente" and pct >= 100 else 0.0
            rows.append(
                {
                    "id_funcionario": int(func["id_funcionario"]),
                    "id_loja": int(func["id_loja"]),
                    "ano": int(mes.year),
                    "mes": int(mes.month),
                    "meta_valor": meta,
                    "realizado_valor": round(real, 2),
                    "percentual_atingido": pct,
                    "comissao_paga": comissao,
                    "bonus_extra": bonus,
                }
            )
    return pd.DataFrame(rows)


def _generate_fato_folha(df_funcionarios, df_metas):
    meses = pd.period_range(DATE_START, DATE_END, freq="M")
    metas_lookup = df_metas.set_index(["id_funcionario", "ano", "mes"])
    rows = []
    for _, func in df_funcionarios.iterrows():
        adm = pd.Timestamp(func["data_admissao"])
        dem = pd.Timestamp(func["data_demissao"]) if pd.notna(func["data_demissao"]) else DATE_END
        for m in meses:
            periodo_inicio = pd.Timestamp(m.start_time.date())
            periodo_fim = pd.Timestamp(m.end_time.date())
            if periodo_fim < adm or periodo_inicio > dem:
                continue

            salario_base = float(func["salario_base"])
            comissao = 0.0
            bonus = 0.0
            if (int(func["id_funcionario"]), m.year, m.month) in metas_lookup.index:
                linha_meta = metas_lookup.loc[(int(func["id_funcionario"]), m.year, m.month)]
                comissao = float(linha_meta["comissao_paga"])
                bonus = float(linha_meta["bonus_extra"])

            horas_extras = round(float(np.random.uniform(0, salario_base * 0.08)), 2)
            vt = round(float(np.random.uniform(80, 280)), 2)
            vr = round(float(np.random.uniform(220, 650)), 2)
            bruto = salario_base + comissao + bonus + horas_extras + vt + vr
            inss = round(bruto * 0.08, 2)
            irrf = round(max((bruto - 2600) * 0.075, 0), 2)
            fgts = round(salario_base * 0.08, 2)
            salario_liquido = round(bruto - inss - irrf, 2)
            custo_empresa = round(bruto + fgts, 2)

            rows.append(
                {
                    "id_funcionario": int(func["id_funcionario"]),
                    "id_loja": int(func["id_loja"]),
                    "ano": int(m.year),
                    "mes": int(m.month),
                    "salario_base": round(salario_base, 2),
                    "comissao": round(comissao, 2),
                    "bonus": round(bonus, 2),
                    "horas_extras_valor": horas_extras,
                    "vale_transporte": vt,
                    "vale_refeicao": vr,
                    "inss": inss,
                    "irrf": irrf,
                    "fgts": fgts,
                    "salario_liquido": salario_liquido,
                    "custo_total_empresa": custo_empresa,
                }
            )
    return pd.DataFrame(rows)


def _generate_fato_atendimento(df_clientes, df_lojas, df_funcionarios):
    atendentes = df_funcionarios[df_funcionarios["status"] == "Ativo"]["id_funcionario"]
    return pd.DataFrame(
        {
            "id_atendimento": np.arange(1, N_ATENDIMENTOS + 1),
            "id_cliente": np.random.choice(df_clientes["id_cliente"], size=N_ATENDIMENTOS),
            "id_loja": np.random.choice(df_lojas["id_loja"], size=N_ATENDIMENTOS),
            "id_funcionario": np.random.choice(atendentes, size=N_ATENDIMENTOS),
            "data": _rand_from_range(DATE_START, DATE_END, N_ATENDIMENTOS).date,
            "canal": np.random.choice(
                ["WhatsApp", "Telefone", "Balcão", "E-mail", "Instagram"],
                size=N_ATENDIMENTOS,
                p=[0.28, 0.18, 0.34, 0.1, 0.1],
            ),
            "motivo": np.random.choice(
                [
                    "Dúvida de produto",
                    "Troca",
                    "Reclamação",
                    "Pedido atrasado",
                    "Programa fidelidade",
                    "Suporte nutricional",
                ],
                size=N_ATENDIMENTOS,
            ),
            "nps": np.random.choice(
                np.arange(0, 11),
                size=N_ATENDIMENTOS,
                p=[0.02, 0.02, 0.03, 0.04, 0.04, 0.08, 0.12, 0.17, 0.19, 0.17, 0.12],
            ),
            "tempo_atendimento_min": np.random.randint(2, 61, size=N_ATENDIMENTOS),
            "resolvido": np.random.choice([True, False], size=N_ATENDIMENTOS, p=[0.88, 0.12]),
        }
    )


def _validate_integridade(references):
    for nome, (fact_df, fact_col, dim_df, dim_col, nullable) in references.items():
        serie = fact_df[fact_col]
        if nullable:
            serie = serie.dropna()
        missing = set(pd.Series(serie).astype(int).unique()) - set(dim_df[dim_col].astype(int).unique())
        if missing:
            raise ValueError(f"Integridade referencial falhou em {nome}: {len(missing)} IDs inválidos")


def _save_excel(df: pd.DataFrame, path: Path, split_by_year: bool = False, date_col: str = "data_venda"):
    if split_by_year and len(df) > MAX_ROWS_PER_SHEET:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for year, part in df.groupby(pd.to_datetime(df[date_col]).dt.year):
                part.to_excel(writer, index=False, sheet_name=f"{year}")
    else:
        df.to_excel(path, index=False, engine="openpyxl")


def main():
    df_fornecedores = _generate_dim_fornecedores()
    df_produtos = _generate_dim_produtos(df_fornecedores)
    df_lojas = _generate_dim_lojas()
    df_clientes = _generate_dim_clientes(df_lojas)
    df_funcionarios, df_lojas = _generate_dim_funcionarios(df_lojas)
    df_calendario = _generate_dim_calendario()

    df_vendas = _generate_fato_vendas(df_lojas, df_clientes, df_funcionarios, df_produtos)
    df_estoque = _generate_fato_estoque(df_lojas, df_produtos)
    df_compras = _generate_fato_compras(df_lojas, df_fornecedores, df_produtos)
    df_metas = _generate_fato_metas(df_funcionarios, df_vendas)
    df_folha = _generate_fato_folha(df_funcionarios, df_metas)
    df_atendimento = _generate_fato_atendimento(df_clientes, df_lojas, df_funcionarios)

    _validate_integridade(
        {
            "vendas_loja": (df_vendas, "id_loja", df_lojas, "id_loja", False),
            "vendas_cliente": (df_vendas, "id_cliente", df_clientes, "id_cliente", True),
            "vendas_vendedor": (df_vendas, "id_vendedor", df_funcionarios, "id_funcionario", False),
            "vendas_produto": (df_vendas, "id_produto", df_produtos, "id_produto", False),
            "estoque_loja": (df_estoque, "id_loja", df_lojas, "id_loja", False),
            "estoque_produto": (df_estoque, "id_produto", df_produtos, "id_produto", False),
            "compras_fornecedor": (
                df_compras,
                "id_fornecedor",
                df_fornecedores,
                "id_fornecedor",
                False,
            ),
            "compras_loja": (df_compras, "id_loja_destino", df_lojas, "id_loja", False),
            "compras_produto": (df_compras, "id_produto", df_produtos, "id_produto", False),
            "metas_funcionario": (
                df_metas,
                "id_funcionario",
                df_funcionarios,
                "id_funcionario",
                False,
            ),
            "folha_funcionario": (
                df_folha,
                "id_funcionario",
                df_funcionarios,
                "id_funcionario",
                False,
            ),
            "atendimento_cliente": (
                df_atendimento,
                "id_cliente",
                df_clientes,
                "id_cliente",
                False,
            ),
            "atendimento_funcionario": (
                df_atendimento,
                "id_funcionario",
                df_funcionarios,
                "id_funcionario",
                False,
            ),
        }
    )

    files = {
        "dim_lojas.xlsx": df_lojas,
        "dim_produtos.xlsx": df_produtos,
        "dim_fornecedores.xlsx": df_fornecedores,
        "dim_clientes.xlsx": df_clientes,
        "dim_funcionarios.xlsx": df_funcionarios,
        "dim_calendario.xlsx": df_calendario,
        "fato_estoque.xlsx": df_estoque,
        "fato_compras.xlsx": df_compras,
        "fato_metas.xlsx": df_metas,
        "fato_folha_pagamento.xlsx": df_folha,
        "fato_atendimento_clientes.xlsx": df_atendimento,
    }
    for file_name, df in files.items():
        _save_excel(df, DATA_DIR / file_name)
    _save_excel(df_vendas, DATA_DIR / "fato_vendas.xlsx", split_by_year=True)

    print("Resumo de geração:")
    print(f"- dim_lojas: {len(df_lojas):,}")
    print(f"- dim_produtos: {len(df_produtos):,}")
    print(f"- dim_fornecedores: {len(df_fornecedores):,}")
    print(f"- dim_clientes: {len(df_clientes):,}")
    print(f"- dim_funcionarios: {len(df_funcionarios):,}")
    print(f"- dim_calendario: {len(df_calendario):,}")
    print(f"- fato_vendas: {len(df_vendas):,}")
    print(f"- fato_estoque: {len(df_estoque):,}")
    print(f"- fato_compras: {len(df_compras):,}")
    print(f"- fato_metas: {len(df_metas):,}")
    print(f"- fato_folha_pagamento: {len(df_folha):,}")
    print(f"- fato_atendimento_clientes: {len(df_atendimento):,}")


if __name__ == "__main__":
    main()
