"""
================================================================================
 Tech Challenge Olist | Dashboard interativo (estilo Power BI) em HTML
--------------------------------------------------------------------------------
 Gera dashboard/dashboard_olist.html - arquivo unico, abre em qualquer
 navegador (Mac/Windows). Cartoes de KPI + 4 graficos da narrativa.
 Substitui/antecipa o Power BI: mesma historia, mesmos numeros.
================================================================================
"""
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

os.makedirs("dashboard", exist_ok=True)

AZUL, LARANJA, VERDE, VERMELHO, CINZA = "#1F4E79", "#E07B39", "#2E8B57", "#C0392B", "#7F8C8D"

# ----------------------------------------------------------------- dados (BI)
m   = pd.read_csv("data/bi/agg_mensal.csv")
uf  = pd.read_csv("data/bi/agg_estado.csv")
dr  = pd.read_csv("data/bi/tab_atraso_nota.csv")
sim = pd.read_csv("data/bi/tab_simulacao.csv")
kpi = pd.read_csv("data/bi/kpis.csv")

ordem = ["Adiantado >10d", "Adiantado 5-10d", "Adiantado 0-5d",
         "Atraso 0-5d", "Atraso 5-10d", "Atraso >10d"]
dr["faixa_atraso"] = pd.Categorical(dr["faixa_atraso"], categories=ordem, ordered=True)
dr = dr.sort_values("faixa_atraso")

def kv(nome):
    return kpi.loc[kpi["indicador"].str.contains(nome, case=False), "valor"].values[0]

# ----------------------------------------------------------------- KPI cards (HTML)
def card(titulo, valor, cor=AZUL):
    return f"""
    <div style="flex:1;min-width:150px;background:#fff;border-radius:10px;
                padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,.12);
                border-top:4px solid {cor};margin:6px;">
      <div style="font-size:12px;color:#666;text-transform:uppercase;
                  letter-spacing:.5px;">{titulo}</div>
      <div style="font-size:26px;font-weight:700;color:{cor};margin-top:4px;">{valor}</div>
    </div>"""

cards = (
    card("Receita (jan17-ago18)", f"R$ {kv('Receita total')/1e6:.1f} mi", AZUL) +
    card("Pedidos", f"{int(kv('Pedidos')):,}".replace(",", "."), AZUL) +
    card("Ticket medio", f"R$ {kv('Ticket'):.0f}", AZUL) +
    card("Recompra", f"{kv('recompra'):.1f}%", VERMELHO) +
    card("Pedidos atrasados", f"{kv('atrasados'):.1f}%", LARANJA) +
    card("Nota: prazo vs atraso", f"{kv('no prazo'):.1f} -> {kv('atrasado'):.1f}", VERMELHO)
)

# ----------------------------------------------------------------- figura 2x2
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "<b>Crescimento da receita mensal</b>",
        "<b>Risco logistico por estado (cor = % atraso)</b>",
        "<b>Quanto mais atrasa, pior a nota</b>",
        "<b>Receita protegida ao reduzir atrasos</b>",
    ),
    specs=[[{"secondary_y": True}, {}], [{}, {}]],
    vertical_spacing=0.14, horizontal_spacing=0.10,
)

# (A) receita + nota
fig.add_trace(go.Bar(x=m["ano_mes"], y=m["receita"], name="Receita",
                     marker_color=AZUL, hovertemplate="%{x}<br>R$ %{y:,.0f}<extra></extra>"),
              row=1, col=1, secondary_y=False)
fig.add_trace(go.Scatter(x=m["ano_mes"], y=m["nota_media"], name="Nota media",
                         mode="lines+markers", line=dict(color=LARANJA, width=3)),
              row=1, col=1, secondary_y=True)

# (B) risco por estado (dispersao volume x atraso)
fig.add_trace(go.Scatter(
    x=uf["prazo_medio_dias"], y=uf["pct_atraso"], mode="markers+text",
    text=uf["uf"], textposition="middle center", textfont=dict(size=8, color="white"),
    marker=dict(size=(uf["pedidos"]**0.5)/4+7, color=uf["pct_atraso"], colorscale="OrRd",
                showscale=False, line=dict(width=1, color="#333")),
    name="Estados",
    hovertemplate="%{text}<br>Prazo %{x:.1f}d<br>Atraso %{y:.1f}%<extra></extra>"),
    row=1, col=2)

# (C) dose-resposta
cores_dr = [VERDE, VERDE, VERDE, LARANJA, VERMELHO, "#7B241C"]
fig.add_trace(go.Bar(x=dr["faixa_atraso"].astype(str), y=dr["nota_media"],
                     marker_color=cores_dr, text=dr["nota_media"], textposition="outside",
                     name="Nota", showlegend=False), row=2, col=1)

# (D) simulacao
fig.add_trace(go.Bar(x=sim["cenario"], y=sim["receita_protegida"],
                     marker_color=[CINZA, LARANJA, VERDE],
                     text=[f"R$ {v/1e3:.0f} mil<br>-{d:,} detratores".replace(",", ".")
                           for v, d in zip(sim["receita_protegida"], sim["detratores_evitados"])],
                     textposition="outside", name="Receita protegida", showlegend=False),
              row=2, col=2)

fig.update_yaxes(title_text="Receita (R$)", row=1, col=1, secondary_y=False)
fig.update_yaxes(title_text="Nota", range=[3.5, 4.6], row=1, col=1, secondary_y=True)
fig.update_yaxes(title_text="% atraso", row=1, col=2)
fig.update_xaxes(title_text="Prazo medio (dias)", row=1, col=2)
fig.update_yaxes(title_text="Nota media", range=[1, 5], row=2, col=1)
fig.update_yaxes(title_text="R$ protegidos", row=2, col=2)
fig.update_layout(height=720, template="plotly_white",
                  legend=dict(orientation="h", y=1.07, x=0.0),
                  margin=dict(t=70, l=60, r=30, b=40), font=dict(size=12))

corpo = pio.to_html(fig, include_plotlyjs="cdn", full_html=False)

# ----------------------------------------------------------------- pagina
html = f"""<!DOCTYPE html><html lang="pt-br"><head><meta charset="utf-8">
<title>Dashboard Olist</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;background:#eef1f5;margin:0;padding:20px;}}
h1{{color:{AZUL};margin:0 0 2px;}} .sub{{color:#666;margin:0 0 14px;}}
.kpis{{display:flex;flex-wrap:wrap;margin-bottom:8px;}}
.foot{{color:{AZUL};font-weight:600;margin-top:10px;text-align:center;}}
.wrap{{max-width:1180px;margin:auto;}}</style></head>
<body><div class="wrap">
<h1>Olist — O paradoxo do crescimento</h1>
<p class="sub">Relatorio executivo | Brazilian E-Commerce Dataset (2017-2018)</p>
<div class="kpis">{cards}</div>
{corpo}
<p class="foot">Logistica nao e custo — e a alavanca que protege o crescimento.</p>
</div></body></html>"""

out = "dashboard/dashboard_olist.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"[OK] dashboard interativo salvo em {out}")

# Snapshot estatico (para slides/verificacao); requer kaleido
try:
    fig.update_layout(title=dict(text="<b>Olist — O paradoxo do crescimento</b>",
                                 x=0.5, font=dict(size=20, color=AZUL)))
    fig.write_image("dashboard/dashboard_olist.png", width=1180, height=760, scale=2)
    print("[OK] snapshot salvo em dashboard/dashboard_olist.png")
except Exception as e:
    print("[aviso] PNG nao gerado (opcional):", e)
