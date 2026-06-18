"""
================================================================================
 Tech Challenge Olist | ETAPAS 4-6 - EDA, Insights e Simulacao
--------------------------------------------------------------------------------
 Le a tabela master e produz:
   (1) Graficos executivos -> figures/
   (2) Numeros-chave (FINDINGS) impressos no console -> alimentam o relatorio
 Narrativa: Crescimento -> Gargalo logistico -> Elo causal (atraso x nota)
            -> Custo invisivel (insatisfacao x recompra) -> Simulacao financeira
================================================================================
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ---------------------------------------------------------------- estilo exec.
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.figsize": (10, 5.5), "figure.dpi": 110,
    "axes.titlesize": 14, "axes.titleweight": "bold",
    "axes.labelsize": 11, "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
})
AZUL, LARANJA, VERDE, VERMELHO, CINZA = "#1f4e79", "#e07b39", "#2e8b57", "#c0392b", "#7f8c8d"
FIG = "figures"

def brl(x, _=None):
    return f"R$ {x/1e6:.1f} mi" if abs(x) >= 1e6 else f"R$ {x/1e3:.0f} mil"

# --------------------------------------------------------------------- dados
df = pd.read_csv("data/processed/order_master.csv",
                 parse_dates=["order_purchase_timestamp"])
# Universo de analise de SLA/satisfacao: pedidos efetivamente entregues
ent = df[(df["order_status"] == "delivered") &
         (df["order_delivered_customer_date"].notna() if "order_delivered_customer_date" in df else True)].copy()
ent = df[df["order_status"] == "delivered"].dropna(subset=["lead_time_total", "atraso_dias"]).copy()

# Janela mensal limpa (meses completos)
JANELA = (df["ano_mes"] >= "2017-01") & (df["ano_mes"] <= "2018-08")

FIND = {}  # dicionario de achados para o relatorio

# ======================================================================
# CAP 1 - CRESCIMENTO COMERCIAL  (+ projecao)
# ======================================================================
mensal = (df[JANELA].groupby("ano_mes")
          .agg(pedidos=("order_id", "count"),
               receita=("receita_produto", "sum")).reset_index())
mensal["ticket_medio"] = mensal["receita"] / mensal["pedidos"]
mensal["t"] = np.arange(len(mensal))

# Projecao linear simples (minimos quadrados) de receita p/ +3 meses
coef = np.polyfit(mensal["t"], mensal["receita"], 1)
tendencia = np.poly1d(coef)
fut_t = np.arange(len(mensal), len(mensal) + 3)
proj = tendencia(fut_t)

FIND["receita_total"] = df[JANELA]["receita_produto"].sum()
FIND["pedidos_total"] = int(df[JANELA]["order_id"].count())
FIND["ticket_medio_geral"] = df[JANELA]["receita_produto"].mean()
FIND["cresc_pedidos_2017x2018"] = (
    mensal[mensal.ano_mes.str.startswith("2018")].pedidos.mean() /
    mensal[mensal.ano_mes.str.startswith("2017")].pedidos.mean() - 1) * 100
FIND["proj_receita_3m"] = proj.sum()

fig, ax1 = plt.subplots()
ax1.bar(mensal["ano_mes"], mensal["receita"], color=AZUL, alpha=.85, label="Receita realizada")
ax1.plot(list(fut_t_lbl := ["2018-09", "2018-10", "2018-11"]), proj,
         "o--", color=LARANJA, lw=2, label="Projeção (tendência)")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(brl))
ax1.set_title("Crescimento da receita mensal (2017-2018) e projeção")
ax1.set_ylabel("Receita de produtos")
ax1.tick_params(axis="x", rotation=90)
ax1.annotate("Black Friday\n2017", xy=("2017-11", mensal.loc[mensal.ano_mes=="2017-11","receita"].values[0]),
             xytext=(2, 1.05e6), color=VERMELHO, fontsize=9,
             arrowprops=dict(arrowstyle="->", color=VERMELHO))
ax1.legend()
plt.tight_layout(); plt.savefig(f"{FIG}/01_crescimento_receita.png"); plt.close()

# ======================================================================
# CAP 2 - GARGALO LOGISTICO (decomposicao do lead time + % atraso)
# ======================================================================
FIND["lead_time_medio"] = ent["lead_time_total"].mean()
FIND["lead_time_mediano"] = ent["lead_time_total"].median()
FIND["pct_atrasado"] = ent["entregue_atrasado"].mean() * 100
etapas = {
    "Aprovação\n(compra→pagto)": ent["tempo_aprovacao"].median(),
    "Postagem\n(aprov.→transp.)": ent["tempo_postagem"].median(),
    "Transporte\n(transp.→cliente)": ent["tempo_transporte"].median(),
}
FIND["etapas"] = etapas

fig, ax = plt.subplots()
bars = ax.barh(list(etapas.keys()), list(etapas.values()),
               color=[VERDE, LARANJA, AZUL])
ax.bar_label(bars, fmt="%.1f dias", padding=4)
ax.set_title("Onde o tempo se perde: decomposição do prazo de entrega (mediana)")
ax.set_xlabel("Dias")
plt.tight_layout(); plt.savefig(f"{FIG}/02_lead_time_decomposicao.png"); plt.close()

# ======================================================================
# CAP 3 - ELO CAUSAL: atraso derruba a nota
# ======================================================================
rev = ent.dropna(subset=["review_score"]).copy()
rev["situacao"] = np.where(rev["atraso_dias"] > 0, "Entregue ATRASADO", "Entregue no prazo")
nota_por_sit = rev.groupby("situacao")["review_score"].mean()
FIND["nota_no_prazo"] = nota_por_sit.get("Entregue no prazo")
FIND["nota_atrasado"] = nota_por_sit.get("Entregue ATRASADO")
# % de notas 1-2 (detratores) em cada situacao
rev["detrator"] = rev["review_score"] <= 2
detr = rev.groupby("situacao")["detrator"].mean() * 100
FIND["detr_no_prazo"] = detr.get("Entregue no prazo")
FIND["detr_atrasado"] = detr.get("Entregue ATRASADO")

# Faixas de atraso x nota media (mostra a dose-resposta)
bins = [-1e9, -10, -5, 0, 5, 10, 1e9]
labels = ["Adiantado\n>10d", "Adiantado\n5-10d", "Adiantado\n0-5d",
          "Atraso\n0-5d", "Atraso\n5-10d", "Atraso\n>10d"]
rev["faixa"] = pd.cut(rev["atraso_dias"], bins=bins, labels=labels)
faixa_nota = rev.groupby("faixa", observed=True)["review_score"].mean()

fig, ax = plt.subplots()
cores = [VERDE]*3 + [LARANJA, VERMELHO, "#7b241c"]
bars = ax.bar(faixa_nota.index.astype(str), faixa_nota.values, color=cores)
ax.bar_label(bars, fmt="%.2f", padding=3)
ax.axhline(rev["review_score"].mean(), ls="--", color=CINZA,
           label=f"Média geral {rev['review_score'].mean():.2f}")
ax.set_ylim(1, 5); ax.set_title("Quanto mais atrasa, pior a nota (relação dose-resposta)")
ax.set_ylabel("Nota média de avaliação (1-5)"); ax.legend()
plt.tight_layout(); plt.savefig(f"{FIG}/03_atraso_x_nota.png"); plt.close()

# ======================================================================
# CAP 4 - O MODELO E DE AQUISICAO, NAO DE RETENCAO
# ----------------------------------------------------------------------
# Achado honesto: recompra ~3% e NAO e explicada pela satisfacao -> o
# negocio depende de atrair clientes novos. Logo o ativo estrategico e a
# REPUTACAO (avaliacoes publicas que alimentam a aquisicao).
# Dado externo (Dica 1 do enunciado): e-commerce maduro tem taxa de
# clientes recorrentes tipicamente entre 20% e 30% (benchmark de mercado).
# ======================================================================
cli = df.groupby("customer_unique_id").agg(
    n_pedidos=("order_id", "count")).reset_index()
FIND["pct_recompra"] = (cli["n_pedidos"] > 1).mean() * 100
BENCH_RECOMPRA = 28.0  # benchmark externo de e-commerce maduro (%)
FIND["bench_recompra"] = BENCH_RECOMPRA

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(["Olist (real)", "E-commerce maduro\n(benchmark de mercado)"],
              [FIND["pct_recompra"], BENCH_RECOMPRA], color=[VERMELHO, CINZA])
ax.bar_label(bars, fmt="%.1f%%", padding=3)
ax.set_title("Negócio movido a AQUISIÇÃO: recompra muito abaixo do mercado")
ax.set_ylabel("% de clientes que voltam a comprar")
ax.annotate("Quase todo cliente compra\numa única vez", xy=(0, FIND["pct_recompra"]),
            xytext=(0.15, 15), color=VERMELHO, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=VERMELHO))
plt.tight_layout(); plt.savefig(f"{FIG}/04_recompra_benchmark.png"); plt.close()

# ======================================================================
# CAP 5 - O CUSTO INVISIVEL: atraso envenena a reputacao + SIMULACAO
# ----------------------------------------------------------------------
# Como a aquisicao depende de reputacao, o atraso e caro: converte
# clientes em DETRATORES (nota 1-2) e expoe receita a uma ma experiencia.
# ======================================================================
ent["late"] = ent["atraso_dias"] > 0
rev_late_rev = ent.loc[ent["late"], "receita_produto"].sum()       # receita exposta
rev_tot_ent = ent["receita_produto"].sum()
n_atrasados = int(ent["late"].sum())
# excesso de detratores causado pelo atraso (p.p.)
excesso_detr = (FIND["detr_atrasado"] - FIND["detr_no_prazo"]) / 100
detr_extras = n_atrasados * excesso_detr
FIND["receita_exposta"] = rev_late_rev
FIND["receita_exposta_pct"] = rev_late_rev / rev_tot_ent * 100
FIND["detr_extras"] = detr_extras

# Simulacao: reduzir X% dos atrasos protege X% da receita exposta e evita
# X% dos detratores excedentes (relacao direta, sem premissas ocultas).
cenarios = {}
cenarios_detr = {}
for red in [0.25, 0.50, 0.75]:
    cenarios[f"Reduzir {int(red*100)}%\ndos atrasos"] = rev_late_rev * red
    cenarios_detr[f"Reduzir {int(red*100)}%\ndos atrasos"] = detr_extras * red
FIND["cenarios"] = cenarios
FIND["cenarios_detr"] = cenarios_detr

fig, ax = plt.subplots()
bars = ax.bar(list(cenarios.keys()), list(cenarios.values()),
              color=[CINZA, LARANJA, VERDE])
ax.bar_label(bars, labels=[f"{brl(v)}\n(-{int(d):,} detratores)".replace(",", ".")
                           for v, d in zip(cenarios.values(), cenarios_detr.values())],
             padding=3, fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(brl))
ax.set_title("Receita protegida e detratores evitados ao reduzir atrasos")
ax.set_ylabel("Receita protegida de má experiência")
ax.margins(y=0.18)
plt.tight_layout(); plt.savefig(f"{FIG}/05_simulacao_financeira.png"); plt.close()

# ======================================================================
# (apoio) Mapa de desempenho por estado: volume x atraso
# ======================================================================
uf = ent.groupby("customer_state").agg(
    pedidos=("order_id", "count"),
    atraso_pct=("entregue_atrasado", "mean"),
    lead=("lead_time_total", "mean")).reset_index()
uf = uf[uf["pedidos"] >= 200]
FIND["top_uf_volume"] = uf.sort_values("pedidos", ascending=False).head(5)[["customer_state","pedidos"]].values.tolist()
FIND["pior_uf_lead"] = uf.sort_values("lead", ascending=False).head(5)[["customer_state","lead"]].values.tolist()

fig, ax = plt.subplots()
sc = ax.scatter(uf["lead"], uf["atraso_pct"]*100, s=uf["pedidos"]/30,
                c=uf["atraso_pct"]*100, cmap="OrRd", edgecolor="k", alpha=.8)
for _, r in uf.iterrows():
    ax.annotate(r["customer_state"], (r["lead"], r["atraso_pct"]*100),
                fontsize=8, ha="center", va="center")
ax.set_title("Mapa de risco logístico por estado (tamanho = volume)")
ax.set_xlabel("Prazo médio de entrega (dias)")
ax.set_ylabel("% de pedidos entregues com atraso")
plt.tight_layout(); plt.savefig(f"{FIG}/06_mapa_estados.png"); plt.close()

# ======================================================================
# (apoio) Categorias top por receita
# ======================================================================
cat_rev = (df[JANELA].groupby("categoria_principal")["receita_produto"]
           .sum().sort_values(ascending=False).head(10))
FIND["top_categorias"] = cat_rev.head(5).to_dict()
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_rev.index[::-1], cat_rev.values[::-1], color=AZUL)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(brl))
ax.set_title("Top 10 categorias por receita")
plt.tight_layout(); plt.savefig(f"{FIG}/07_top_categorias.png"); plt.close()

# ======================================================================
# DUMP DOS ACHADOS
# ======================================================================
print("\n" + "#"*70 + "\n ACHADOS-CHAVE (numeros reais p/ o relatorio)\n" + "#"*70)
def p(k, v):
    print(f"  {k:32s}: {v}")
p("Receita total (jan17-ago18)", brl(FIND['receita_total']))
p("Pedidos (jan17-ago18)", f"{FIND['pedidos_total']:,}")
p("Ticket medio", f"R$ {FIND['ticket_medio_geral']:.2f}")
p("Crescimento medio 2018 vs 2017", f"{FIND['cresc_pedidos_2017x2018']:.0f}%")
p("Projecao receita +3 meses", brl(FIND['proj_receita_3m']))
p("Lead time medio entrega", f"{FIND['lead_time_medio']:.1f} dias (mediana {FIND['lead_time_mediano']:.1f})")
_transp = list(etapas.values())[2]
p("Etapa transporte (mediana)", f"{_transp:.1f} dias")
p("% pedidos entregues atrasados", f"{FIND['pct_atrasado']:.1f}%")
p("Nota media no prazo", f"{FIND['nota_no_prazo']:.2f}")
p("Nota media atrasado", f"{FIND['nota_atrasado']:.2f}")
p("Detratores (1-2) no prazo", f"{FIND['detr_no_prazo']:.1f}%")
p("Detratores (1-2) atrasado", f"{FIND['detr_atrasado']:.1f}%")
p("Taxa de recompra Olist", f"{FIND['pct_recompra']:.2f}% (benchmark mercado ~{FIND['bench_recompra']:.0f}%)")
p("Receita exposta a atraso", f"{brl(FIND['receita_exposta'])} ({FIND['receita_exposta_pct']:.1f}% da receita entregue)")
p("Detratores extras p/ atraso", f"{FIND['detr_extras']:,.0f} clientes no periodo")
print("  Cenarios (receita protegida | detratores evitados):")
for k in FIND["cenarios"]:
    print(f"      {k.replace(chr(10),' '):26s}: {brl(FIND['cenarios'][k])} | -{FIND['cenarios_detr'][k]:,.0f}")
print("  Top 5 categorias por receita:")
for k, v in FIND["top_categorias"].items():
    print(f"      {k:28s}: {brl(v)}")
print("\n[OK] 7 figuras salvas em figures/")
