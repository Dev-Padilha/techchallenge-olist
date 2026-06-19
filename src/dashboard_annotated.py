"""
================================================================================
 Tech Challenge Olist | Mockup ANOTADO do dashboard (guia de montagem visual)
--------------------------------------------------------------------------------
 Gera dashboard/layout_dashboard_anotado.png : um esquema que mostra, em cada
 area, QUAL visual do Power BI usar, QUAL tabela e QUAIS campos arrastar.
================================================================================
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AZUL, LARANJA, VERDE, VERMELHO, CINZA = "#1F4E79", "#E07B39", "#2E8B57", "#C0392B", "#7F8C8D"
FUNDO = "#EEF1F5"

fig, ax = plt.subplots(figsize=(13, 8.6), dpi=130)
fig.patch.set_facecolor(FUNDO)
ax.set_xlim(0, 12); ax.set_ylim(0, 12); ax.axis("off")
ax.set_facecolor(FUNDO)

def caixa(x, y, w, h, fc="white", ec=AZUL, lw=1.5, r=0.10):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                 boxstyle=f"round,pad=0.02,rounding_size={r}",
                 fc=fc, ec=ec, lw=lw))

def txt(x, y, s, size=9, color="#222", weight="normal", ha="center", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va)

def badge(x, y, s, cor):
    ax.text(x, y, s, fontsize=7.5, color="white", fontweight="bold", ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc=cor, ec="none"))

# ============================================================ TITULO
caixa(0.3, 10.9, 11.4, 0.9, fc="white", ec="#ccc", lw=1)
txt(0.6, 11.35, "Olist — O paradoxo do crescimento", size=15, color=AZUL,
    weight="bold", ha="left")
txt(9.0, 11.35, "Filtro: UF ▾   Ano ▾", size=9, color="#444", ha="left")
badge(9.0, 11.0, "Segmentação de Dados (slicer) → fato_pedidos[uf], [ano]", CINZA)

# ============================================================ KPIs
txt(0.3, 10.55, "① LINHA DE KPIs (topo) — 6 visuais  ‹Cartão›  →  tabela  kpis  /  medidas DAX",
    size=10, color=VERMELHO, weight="bold", ha="left")
labels = [("RECEITA", "R$ 13,5 mi", AZUL), ("PEDIDOS", "99.092", AZUL),
          ("TICKET", "R$ 138", AZUL), ("RECOMPRA", "3,1%", VERMELHO),
          ("% ATRASO", "8,1%", LARANJA), ("NOTA P→A", "4,3→2,6", VERMELHO)]
w = 1.83
for i, (lab, val, cor) in enumerate(labels):
    x = 0.3 + i * (w + 0.05)
    caixa(x, 9.55, w, 0.85, fc="white", ec=cor, lw=2)
    ax.add_patch(plt.Rectangle((x, 10.30), w, 0.10, color=cor))
    txt(x + w/2, 10.05, val, size=11, color=cor, weight="bold")
    txt(x + w/2, 9.75, lab, size=7, color="#666")

# ============================================================ GRAFICOS (2x2)
def painel(x, y, w, h, n, titulo, visual, tabela, campos, cor):
    caixa(x, y, w, h, fc="white", ec="#ccc", lw=1)
    txt(x + 0.25, y + h - 0.32, f"{n} {titulo}", size=10.5, color="#222",
        weight="bold", ha="left")
    badge(x + 0.25, y + h - 0.75, f"Visual: {visual}", cor)
    txt(x + 0.25, y + h - 1.15, f"Tabela:  {tabela}", size=8.5, color="#333", ha="left")
    for j, c in enumerate(campos):
        txt(x + 0.35, y + h - 1.55 - j*0.36, f"•  {c}", size=8.2, color="#444", ha="left")

W, H = 5.6, 3.9
painel(0.3, 5.3, W, H, "②", "Crescimento da receita mensal",
       "Gráfico de Colunas e Linhas", "agg_mensal",
       ["Eixo X:  ano_mes", "Colunas:  receita", "Linha (eixo 2º):  nota_media",
        "Análises → Linha de tendência"], AZUL)

painel(6.1, 5.3, W, H, "③", "Risco logístico por estado",
       "Gráfico de Dispersão (ou Mapa)", "agg_estado",
       ["X:  prazo_medio_dias", "Y:  pct_atraso", "Tamanho:  pedidos",
        "Legenda/Cor:  uf"], LARANJA)

painel(0.3, 1.0, W, H, "④", "Quanto mais atrasa, pior a nota",
       "Gráfico de Colunas Agrupadas", "tab_atraso_nota",
       ["Eixo X:  faixa_atraso (ordenar!)", "Valor:  nota_media",
        "Cor condicional: verde→vermelho", "★ Gráfico-chave: destaque"], VERMELHO)

painel(6.1, 1.0, W, H, "⑤", "Receita protegida (simulação)",
       "Gráfico de Colunas", "tab_simulacao",
       ["Eixo X:  cenario", "Valor:  receita_protegida",
        "Dica (tooltip):  detratores_evitados"], VERDE)

txt(6.0, 0.5, "Logística não é custo — é a alavanca que protege o crescimento.",
    size=10, color=AZUL, weight="bold")

fig.savefig("dashboard/layout_dashboard_anotado.png", facecolor=FUNDO, bbox_inches="tight")
print("[OK] mockup anotado salvo em dashboard/layout_dashboard_anotado.png")
