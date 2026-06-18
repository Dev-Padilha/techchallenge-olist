"""
================================================================================
 Tech Challenge Olist  |  ETAPA 3 - Engenharia e Preparacao dos Dados
--------------------------------------------------------------------------------
 Objetivo: a partir das 9 tabelas brutas do Olist, construir UMA tabela
 analitica no grao de PEDIDO ("order_master"), pronta para responder as
 perguntas de negocio do relatorio executivo.

 Decisoes de modelagem (documentadas para governanca/reprodutibilidade):
  - Grao final = 1 linha por pedido (order_id).
  - Foco analitico em pedidos ENTREGUES (order_status == 'delivered'),
    pois SLA, satisfacao e receita realizada so fazem sentido em pedidos
    de fato concluidos. Pedidos cancelados/indisponiveis sao quantificados
    a parte (taxa de cancelamento), mas nao entram nas analises de prazo.
  - Cliente real = customer_unique_id (NAO customer_id). customer_id e
    re-emitido a cada pedido; usa-lo infla artificialmente a base de clientes.
================================================================================
"""

import os
import pandas as pd
import numpy as np

RAW = "data"
OUT = "data/processed"
os.makedirs(OUT, exist_ok=True)


def carregar_brutos():
    """Le os CSVs brutos. Datas sao parseadas onde aplicavel."""
    orders = pd.read_csv(
        f"{RAW}/olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    items = pd.read_csv(f"{RAW}/olist_order_items_dataset.csv")
    payments = pd.read_csv(f"{RAW}/olist_order_payments_dataset.csv")
    reviews = pd.read_csv(f"{RAW}/olist_order_reviews_dataset.csv")
    customers = pd.read_csv(f"{RAW}/olist_customers_dataset.csv")
    products = pd.read_csv(f"{RAW}/olist_products_dataset.csv")
    sellers = pd.read_csv(f"{RAW}/olist_sellers_dataset.csv")
    cat = pd.read_csv(f"{RAW}/product_category_name_translation.csv")
    return orders, items, payments, reviews, customers, products, sellers, cat


def agregar_itens(items, products, cat):
    """
    order_items esta no grao de ITEM. Agregamos para o grao de PEDIDO:
      - receita_produto = soma dos precos dos itens
      - receita_frete   = soma dos fretes
      - n_itens         = qtd de itens
      - categoria_principal = categoria do item mais caro do pedido (proxy
        simples e robusta para classificar o pedido por categoria).
    """
    # Traduz categoria PT -> EN (lookup); mantem PT quando nao houver traducao.
    products = products.merge(cat, on="product_category_name", how="left")
    products["categoria"] = products["product_category_name_english"].fillna(
        products["product_category_name"]
    ).fillna("desconhecida")

    it = items.merge(products[["product_id", "categoria"]], on="product_id", how="left")

    # Agregados financeiros por pedido
    agg = it.groupby("order_id").agg(
        receita_produto=("price", "sum"),
        receita_frete=("freight_value", "sum"),
        n_itens=("order_item_id", "count"),
        n_sellers=("seller_id", "nunique"),
    ).reset_index()

    # Categoria principal = categoria do item de maior preco no pedido
    idx = it.groupby("order_id")["price"].idxmax()
    cat_principal = it.loc[idx, ["order_id", "categoria"]].rename(
        columns={"categoria": "categoria_principal"}
    )
    agg = agg.merge(cat_principal, on="order_id", how="left")
    return agg


def agregar_pagamentos(payments):
    """payments pode ter varias linhas por pedido (parcelamentos/vouchers).
    Consolidamos: valor total pago, tipo predominante e maximo de parcelas."""
    pay = payments.groupby("order_id").agg(
        valor_pago=("payment_value", "sum"),
        parcelas=("payment_installments", "max"),
    ).reset_index()
    # Tipo de pagamento predominante (o de maior valor no pedido)
    idx = payments.groupby("order_id")["payment_value"].idxmax()
    tipo = payments.loc[idx, ["order_id", "payment_type"]].rename(
        columns={"payment_type": "tipo_pagamento"}
    )
    pay = pay.merge(tipo, on="order_id", how="left")
    return pay


def agregar_reviews(reviews):
    """Alguns pedidos tem mais de uma avaliacao. Usamos a nota MEDIA por
    pedido (decisao conservadora) e a data da 1a avaliacao."""
    rv = reviews.groupby("order_id").agg(
        review_score=("review_score", "mean"),
    ).reset_index()
    rv["review_score"] = rv["review_score"].round(0).astype("Int64")
    return rv


def construir_master():
    orders, items, payments, reviews, customers, products, sellers, cat = carregar_brutos()

    # --- Enriquecimentos ---
    itens_agg = agregar_itens(items, products, cat)
    pay_agg = agregar_pagamentos(payments)
    rev_agg = agregar_reviews(reviews)

    # customer_unique_id (cliente real) + geografia
    cli = customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]]

    df = (
        orders
        .merge(cli, on="customer_id", how="left")
        .merge(itens_agg, on="order_id", how="left")
        .merge(pay_agg, on="order_id", how="left")
        .merge(rev_agg, on="order_id", how="left")
    )

    # --- Variaveis de TEMPO / SLA (em dias) ---
    df["lead_time_total"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["tempo_aprovacao"] = (
        df["order_approved_at"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400
    df["tempo_postagem"] = (
        df["order_delivered_carrier_date"] - df["order_approved_at"]
    ).dt.total_seconds() / 86400
    df["tempo_transporte"] = (
        df["order_delivered_customer_date"] - df["order_delivered_carrier_date"]
    ).dt.total_seconds() / 86400
    # Atraso vs prazo PROMETIDO ao cliente (positivo = entregou atrasado)
    df["atraso_dias"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400
    df["entregue_atrasado"] = df["atraso_dias"] > 0

    # --- Dimensoes de tempo para series mensais ---
    df["ano_mes"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["ano"] = df["order_purchase_timestamp"].dt.year

    return df


def relatorio_qualidade(df):
    """Imprime um diagnostico de qualidade (governanca)."""
    print("\n" + "=" * 70)
    print("DIAGNOSTICO DE QUALIDADE - tabela master")
    print("=" * 70)
    print(f"Linhas (pedidos): {len(df):,}")
    print(f"Periodo: {df['order_purchase_timestamp'].min()} -> {df['order_purchase_timestamp'].max()}")
    print("\nStatus dos pedidos:")
    print(df["order_status"].value_counts().to_string())
    print("\n% de nulos em colunas-chave:")
    cols = ["order_delivered_customer_date", "review_score", "receita_produto",
            "valor_pago", "atraso_dias", "lead_time_total"]
    print((df[cols].isna().mean() * 100).round(2).to_string())


if __name__ == "__main__":
    df = construir_master()
    relatorio_qualidade(df)
    df.to_csv(f"{OUT}/order_master.csv", index=False)
    print(f"\n[OK] tabela master salva em {OUT}/order_master.csv  ({df.shape})")
