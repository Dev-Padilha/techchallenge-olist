"""
================================================================================
 Tech Challenge Olist | Export para Power BI
--------------------------------------------------------------------------------
 Gera, em data/bi/, um modelo pronto para o Power BI:
   - fato_pedidos.csv      : tabela-fato (1 linha = 1 pedido), nomes amigaveis
   - agg_mensal.csv        : serie mensal (receita, pedidos, ticket, atraso, nota)
   - agg_estado.csv        : desempenho por UF (mapa/risco logistico)
   - agg_categoria.csv     : receita e nota por categoria
   - tab_atraso_nota.csv   : relacao atraso x nota (dose-resposta)
   - tab_simulacao.csv     : cenarios de receita protegida
   - kpis.csv              : indicadores-cabecalho (cartoes)
 Basta "Obter Dados > Pasta" apontando para data/bi/.
================================================================================
"""
import os
import pandas as pd
import numpy as np

OUT = "data/bi"
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv("data/processed/order_master.csv",
                 parse_dates=["order_purchase_timestamp"])

# ---------------------------------------------------------------- TABELA FATO
fato = pd.DataFrame({
    "id_pedido":        df["order_id"],
    "data_compra":      df["order_purchase_timestamp"].dt.date,
    "ano_mes":          df["ano_mes"],
    "ano":              df["ano"],
    "uf":               df["customer_state"],
    "cidade":           df["customer_city"],
    "categoria":        df["categoria_principal"],
    "status":           df["order_status"],
    "entregue":         (df["order_status"] == "delivered").astype(int),
    "receita_produto":  df["receita_produto"],
    "receita_frete":    df["receita_frete"],
    "valor_pago":       df["valor_pago"],
    "parcelas":         df["parcelas"],
    "tipo_pagamento":   df["tipo_pagamento"],
    "qtd_itens":        df["n_itens"],
    "prazo_entrega_dias": df["lead_time_total"].round(1),
    "tempo_aprovacao_dias": df["tempo_aprovacao"].round(1),
    "tempo_postagem_dias":  df["tempo_postagem"].round(1),
    "tempo_transporte_dias": df["tempo_transporte"].round(1),
    "atraso_dias":      df["atraso_dias"].round(1),
    "nota_avaliacao":   df["review_score"],
})
fato["entregue_atrasado"] = (fato["atraso_dias"] > 0).astype("Int64")
fato["detrator"] = (fato["nota_avaliacao"] <= 2).astype("Int64")
# Faixa de atraso (para o grafico dose-resposta)
bins = [-1e9, -10, -5, 0, 5, 10, 1e9]
labels = ["Adiantado >10d", "Adiantado 5-10d", "Adiantado 0-5d",
          "Atraso 0-5d", "Atraso 5-10d", "Atraso >10d"]
fato["faixa_atraso"] = pd.cut(fato["atraso_dias"], bins=bins, labels=labels)
# Situacao simples (para slicer)
fato["situacao_entrega"] = np.where(fato["atraso_dias"] > 0, "Atrasado",
                            np.where(fato["atraso_dias"].notna(), "No prazo", "Sem entrega"))
fato.to_csv(f"{OUT}/fato_pedidos.csv", index=False)

# Universo de analise (entregues, janela limpa) para agregados
JAN = (df["ano_mes"] >= "2017-01") & (df["ano_mes"] <= "2018-08")
ent = df[(df["order_status"] == "delivered")].dropna(subset=["lead_time_total", "atraso_dias"]).copy()
ent["late"] = ent["atraso_dias"] > 0
ent["detrator"] = ent["review_score"] <= 2

# ---------------------------------------------------------------- AGG MENSAL
agg_m = (df[JAN].groupby("ano_mes")
         .agg(pedidos=("order_id", "count"),
              receita=("receita_produto", "sum")).reset_index())
agg_m["ticket_medio"] = (agg_m["receita"] / agg_m["pedidos"]).round(2)
# atraso e nota mensal (so entregues, mesma janela limpa)
ent_jan = ent[(ent["ano_mes"] >= "2017-01") & (ent["ano_mes"] <= "2018-08")]
em = ent_jan.groupby("ano_mes").agg(
    pct_atraso=("late", "mean"), nota_media=("review_score", "mean")).reset_index()
agg_m = agg_m.merge(em, on="ano_mes", how="left")
agg_m["pct_atraso"] = (agg_m["pct_atraso"] * 100).round(1)
agg_m["nota_media"] = agg_m["nota_media"].round(2)
agg_m.to_csv(f"{OUT}/agg_mensal.csv", index=False)

# ---------------------------------------------------------------- AGG ESTADO
agg_uf = ent.groupby("customer_state").agg(
    pedidos=("order_id", "count"),
    receita=("receita_produto", "sum"),
    prazo_medio_dias=("lead_time_total", "mean"),
    pct_atraso=("late", "mean"),
    nota_media=("review_score", "mean")).reset_index()
agg_uf.columns = ["uf", "pedidos", "receita", "prazo_medio_dias", "pct_atraso", "nota_media"]
agg_uf["prazo_medio_dias"] = agg_uf["prazo_medio_dias"].round(1)
agg_uf["pct_atraso"] = (agg_uf["pct_atraso"] * 100).round(1)
agg_uf["nota_media"] = agg_uf["nota_media"].round(2)
agg_uf["receita"] = agg_uf["receita"].round(0)
agg_uf.to_csv(f"{OUT}/agg_estado.csv", index=False)

# ---------------------------------------------------------------- AGG CATEGORIA
agg_cat = (df[JAN].dropna(subset=["categoria_principal"])
           .groupby("categoria_principal")
           .agg(pedidos=("order_id", "count"),
                receita=("receita_produto", "sum")).reset_index())
agg_cat["ticket_medio"] = (agg_cat["receita"] / agg_cat["pedidos"]).round(2)
ec = ent.dropna(subset=["categoria_principal"]).groupby("categoria_principal").agg(
    nota_media=("review_score", "mean")).reset_index()
agg_cat = agg_cat.merge(ec, on="categoria_principal", how="left")
agg_cat.columns = ["categoria", "pedidos", "receita", "ticket_medio", "nota_media"]
agg_cat["nota_media"] = agg_cat["nota_media"].round(2)
agg_cat["receita"] = agg_cat["receita"].round(0)
agg_cat.sort_values("receita", ascending=False).to_csv(f"{OUT}/agg_categoria.csv", index=False)

# ---------------------------------------------------------------- DOSE-RESPOSTA
fr = ent.dropna(subset=["review_score"]).copy()
fr["faixa_atraso"] = pd.cut(fr["atraso_dias"], bins=bins, labels=labels)
tab_dr = fr.groupby("faixa_atraso", observed=True).agg(
    nota_media=("review_score", "mean"),
    pedidos=("order_id", "count")).reset_index()
tab_dr["nota_media"] = tab_dr["nota_media"].round(2)
tab_dr.to_csv(f"{OUT}/tab_atraso_nota.csv", index=False)

# ---------------------------------------------------------------- SIMULACAO
rev_late = ent.loc[ent["late"], "receita_produto"].sum()
n_late = int(ent["late"].sum())
detr_late = fr.loc[fr["atraso_dias"] > 0, "review_score"].le(2).mean()
detr_ontime = fr.loc[fr["atraso_dias"] <= 0, "review_score"].le(2).mean()
excesso = detr_late - detr_ontime
detr_extras = n_late * excesso
sim = []
for red in [0.25, 0.50, 0.75]:
    sim.append({"cenario": f"Reduzir {int(red*100)}% dos atrasos",
                "reducao_pct": int(red*100),
                "receita_protegida": round(rev_late * red, 0),
                "detratores_evitados": int(detr_extras * red)})
pd.DataFrame(sim).to_csv(f"{OUT}/tab_simulacao.csv", index=False)

# ---------------------------------------------------------------- KPIs (cartoes)
cli = df.groupby("customer_unique_id")["order_id"].count()
kpis = pd.DataFrame([
    {"indicador": "Receita total (jan17-ago18)", "valor": round(df[JAN]["receita_produto"].sum(), 0), "formato": "R$"},
    {"indicador": "Pedidos (jan17-ago18)", "valor": int(df[JAN]["order_id"].count()), "formato": "num"},
    {"indicador": "Ticket medio", "valor": round(df[JAN]["receita_produto"].mean(), 2), "formato": "R$"},
    {"indicador": "Taxa de recompra (%)", "valor": round((cli > 1).mean() * 100, 2), "formato": "%"},
    {"indicador": "Prazo medio de entrega (dias)", "valor": round(ent["lead_time_total"].mean(), 1), "formato": "num"},
    {"indicador": "Pedidos atrasados (%)", "valor": round(ent["late"].mean() * 100, 1), "formato": "%"},
    {"indicador": "Nota media no prazo", "valor": round(fr.loc[fr["atraso_dias"] <= 0, "review_score"].mean(), 2), "formato": "num"},
    {"indicador": "Nota media atrasado", "valor": round(fr.loc[fr["atraso_dias"] > 0, "review_score"].mean(), 2), "formato": "num"},
    {"indicador": "Receita exposta a atraso (R$)", "valor": round(rev_late, 0), "formato": "R$"},
])
kpis.to_csv(f"{OUT}/kpis.csv", index=False)

print("[OK] modelo BI exportado em data/bi/:")
for f in sorted(os.listdir(OUT)):
    print("   -", f, f"({len(pd.read_csv(os.path.join(OUT, f))):,} linhas)")
