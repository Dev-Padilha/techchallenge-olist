"""
================================================================================
 Tech Challenge Olist | Mockup de LAYOUT do dashboard (PNG)
--------------------------------------------------------------------------------
 Gera dashboard/layout_dashboard.png mostrando a organizacao completa:
   - barra de titulo
   - LINHA DE KPIs (6 cartoes) no topo
   - grade 2x2 com os 4 graficos da narrativa
 Serve como guia visual de onde posicionar cada elemento no Power BI.
================================================================================
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.gridspec import GridSpec

AZUL, LARANJA, VERDE, VERMELHO, CINZA = "#1F4E79", "#E07B39", "#2E8B57", "#C0392B", "#7F8C8D"
FUNDO = "#EEF1F5"

m   = pd.read_csv("data/bi/agg_mensal.csv")
uf  = pd.read_csv("data/bi/agg_estado.csv")
dr  = pd.read_csv("data/bi/tab_atraso_nota.csv")
sim = pd.read_csv("data/bi/tab_simulacao.csv")
kpi = pd.read_csv("data/bi/kpis.csv")
ordem = ["Adiantado >10d", "Adiantado 5-10d", "Adiantado 0-5d",
         "Atraso 0-5d", "Atraso 5-10d", "Atraso >10d"]
dr["faixa_atraso"] = pd.Categorical(dr["faixa_atraso"], categories=ordem, ordered=True)
dr = dr.sort_values("faixa_atraso")

def kv(n):
    return kpi.loc[kpi["indicador"].str.contains(n, case=False), "valor"].values[0]

fig = plt.figure(figsize=(13, 8.2), dpi=130)
fig.patch.set_facecolor(FUNDO)

gs = GridSpec(3, 4, figure=fig,
              height_ratios=[0.9, 2.4, 2.4], hspace=0.45, wspace=0.30,
              left=0.05, right=0.97, top=0.90, bottom=0.07)

# ----------------------------------------------------------- TITULO
fig.text(0.05, 0.955, "Olist — O paradoxo do crescimento",
         fontsize=20, fontweight="bold", color=AZUL)
fig.text(0.05, 0.925, "Relatório executivo  |  E-commerce Olist (2017–2018)",
         fontsize=11, color="#666")
# "slicer" ilustrativo
fig.text(0.78, 0.945, "  Filtro: UF  ▾     Ano  ▾  ", fontsize=10, color="#444",
         bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#ccc"))

# ----------------------------------------------------------- LINHA DE KPIs
kpis = [
    ("RECEITA", f"R$ {kv('Receita total')/1e6:.1f} mi", AZUL),
    ("PEDIDOS", f"{int(kv('Pedidos')):,}".replace(",", "."), AZUL),
    ("TICKET MÉDIO", f"R$ {kv('Ticket'):.0f}", AZUL),
    ("RECOMPRA", f"{kv('recompra'):.1f}%", VERMELHO),
    ("% ATRASO", f"{kv('atrasados'):.1f}%", LARANJA),
    ("NOTA: PRAZO→ATRASO", f"{kv('no prazo'):.1f} → {kv('atrasado'):.1f}", VERMELHO),
]
ax_k = fig.add_subplot(gs[0, :]); ax_k.axis("off")
ax_k.set_xlim(0, 6); ax_k.set_ylim(0, 1)
for i, (lab, val, cor) in enumerate(kpis):
    box = FancyBboxPatch((i + 0.06, 0.08), 0.88, 0.84,
                         boxstyle="round,pad=0.02,rounding_size=0.06",
                         fc="white", ec=cor, lw=0, mutation_aspect=0.5)
    ax_k.add_patch(box)
    # faixa superior colorida
    ax_k.add_patch(FancyBboxPatch((i + 0.06, 0.82), 0.88, 0.10,
                   boxstyle="round,pad=0.02,rounding_size=0.06",
                   fc=cor, ec="none", mutation_aspect=0.5))
    ax_k.text(i + 0.5, 0.55, val, ha="center", va="center",
              fontsize=15, fontweight="bold", color=cor)
    ax_k.text(i + 0.5, 0.25, lab, ha="center", va="center",
              fontsize=7.5, color="#666")

# ----------------------------------------------------------- (A) receita + nota
axA = fig.add_subplot(gs[1, 0:2])
axA.bar(m["ano_mes"], m["receita"], color=AZUL, alpha=.9)
axA.set_title("Crescimento da receita mensal", fontsize=11, fontweight="bold", color="#333")
axA.tick_params(axis="x", rotation=90, labelsize=6)
axA2 = axA.twinx()
axA2.plot(m["ano_mes"], m["nota_media"], color=LARANJA, lw=2.2, marker="o", ms=3)
axA2.set_ylim(3.5, 4.6); axA2.set_ylabel("Nota", color=LARANJA, fontsize=8)
axA.set_ylabel("Receita", fontsize=8)
for s in ["top"]:
    axA.spines[s].set_visible(False); axA2.spines[s].set_visible(False)

# ----------------------------------------------------------- (B) risco por estado
axB = fig.add_subplot(gs[1, 2:4])
sc = axB.scatter(uf["prazo_medio_dias"], uf["pct_atraso"],
                 s=(uf["pedidos"]**0.5)/1.2 + 25, c=uf["pct_atraso"], cmap="OrRd",
                 edgecolor="#333", lw=.5, alpha=.85)
for _, r in uf.iterrows():
    if r["pedidos"] > 1500:
        axB.annotate(r["uf"], (r["prazo_medio_dias"], r["pct_atraso"]),
                     fontsize=6, ha="center", va="center")
axB.set_title("Risco logístico por estado (cor = % atraso)", fontsize=11,
              fontweight="bold", color="#333")
axB.set_xlabel("Prazo médio (dias)", fontsize=8); axB.set_ylabel("% atraso", fontsize=8)
for s in ["top", "right"]:
    axB.spines[s].set_visible(False)

# ----------------------------------------------------------- (C) dose-resposta
axC = fig.add_subplot(gs[2, 0:2])
cores = [VERDE, VERDE, VERDE, LARANJA, VERMELHO, "#7B241C"]
b = axC.bar(dr["faixa_atraso"].astype(str), dr["nota_media"], color=cores)
axC.bar_label(b, fmt="%.2f", fontsize=8, padding=2)
axC.set_title("Quanto mais atrasa, pior a nota", fontsize=11, fontweight="bold", color="#333")
axC.set_ylim(1, 5); axC.tick_params(axis="x", labelsize=6.5, rotation=15)
axC.set_ylabel("Nota média", fontsize=8)
for s in ["top", "right"]:
    axC.spines[s].set_visible(False)

# ----------------------------------------------------------- (D) simulacao
axD = fig.add_subplot(gs[2, 2:4])
b = axD.bar(sim["cenario"].str.replace("Reduzir ", "−").str.replace(" dos atrasos", ""),
            sim["receita_protegida"], color=[CINZA, LARANJA, VERDE])
axD.bar_label(b, labels=[f"R$ {v/1e3:.0f} mil" for v in sim["receita_protegida"]],
              fontsize=8, padding=2)
axD.set_title("Receita protegida ao reduzir atrasos", fontsize=11,
              fontweight="bold", color="#333")
axD.set_ylabel("R$ protegidos", fontsize=8); axD.tick_params(axis="x", labelsize=7.5)
axD.margins(y=0.15)
for s in ["top", "right"]:
    axD.spines[s].set_visible(False)

fig.text(0.5, 0.025, "Logística não é custo — é a alavanca que protege o crescimento.",
         ha="center", fontsize=10, fontweight="bold", color=AZUL)

fig.savefig("dashboard/layout_dashboard.png", facecolor=FUNDO, bbox_inches="tight")
print("[OK] mockup salvo em dashboard/layout_dashboard.png")
