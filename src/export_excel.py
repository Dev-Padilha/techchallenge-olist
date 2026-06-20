"""
export_excel.py — Gera o dashboard executivo em Excel (.xlsx) a partir de data/bi/.

Substitui o Power BI: um único arquivo `dashboard/dashboard_olist.xlsx` com uma página
"Dashboard" que conta a mesma história do relatorio (Crescimento -> Risco logistico ->
Atraso destroi reputacao -> Valor de agir), alimentada por abas de dados nativas do Excel.

Uso:
    python src/export_excel.py
Pre-requisito: data/bi/*.csv (gere com `python src/export_bi.py`).
"""
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.utils.dataframe import dataframe_to_rows

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "data" / "bi"
OUT = ROOT / "dashboard" / "dashboard_olist.xlsx"

# Paleta executiva (mesma das figuras/relatorio)
AZUL = "1F4E79"
VERMELHO = "C0392B"
VERDE = "2E8B57"
LARANJA = "E07B39"
CINZA = "7F8C8D"
CINZA_CLARO = "F2F4F5"
BRANCO = "FFFFFF"

thin = Side(style="thin", color="D9D9D9")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def load(name):
    return pd.read_csv(BI / f"{name}.csv")


def write_data_sheet(wb, df, title):
    """Cria uma aba de dados (fonte dos graficos)."""
    ws = wb.create_sheet(title)
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    # cabecalho em negrito
    for c in ws[1]:
        c.font = Font(bold=True, color=BRANCO)
        c.fill = PatternFill("solid", fgColor=AZUL)
    ws.sheet_state = "visible"
    return ws


def kpi_card(ws, anchor_col, row, titulo, valor, cor=AZUL):
    """Desenha um cartao de KPI ocupando 3 colunas x 3 linhas a partir de (row, anchor_col)."""
    c0 = anchor_col
    ws.merge_cells(start_row=row, start_column=c0, end_row=row, end_column=c0 + 2)
    ws.merge_cells(start_row=row + 1, start_column=c0, end_row=row + 2, end_column=c0 + 2)
    t = ws.cell(row=row, column=c0, value=titulo)
    t.font = Font(bold=True, size=10, color=BRANCO)
    t.alignment = Alignment(horizontal="center", vertical="center")
    v = ws.cell(row=row + 1, column=c0, value=valor)
    v.font = Font(bold=True, size=20, color=cor)
    v.alignment = Alignment(horizontal="center", vertical="center")
    for rr in range(row, row + 3):
        for cc in range(c0, c0 + 3):
            cell = ws.cell(row=rr, column=cc)
            cell.border = BORDER
            if rr == row:
                cell.fill = PatternFill("solid", fgColor=cor)
            else:
                cell.fill = PatternFill("solid", fgColor=CINZA_CLARO)


def main():
    kpis = load("kpis")
    mensal = load("agg_mensal")
    atraso = load("tab_atraso_nota")
    simul = load("tab_simulacao")
    categoria = load("agg_categoria").sort_values("receita", ascending=False).head(8)
    estado = load("agg_estado").sort_values("pedidos", ascending=False).head(12)

    wb = Workbook()
    dash = wb.active
    dash.title = "Dashboard"
    dash.sheet_view.showGridLines = False

    # ---- abas de dados ----
    ws_mensal = write_data_sheet(wb, mensal, "dados_mensal")
    ws_atraso = write_data_sheet(wb, atraso, "dados_atraso_nota")
    ws_simul = write_data_sheet(wb, simul, "dados_simulacao")
    ws_cat = write_data_sheet(wb, categoria, "dados_categoria")
    ws_est = write_data_sheet(wb, estado, "dados_estado")

    # ---- cabecalho ----
    dash.merge_cells("A1:R1")
    h = dash["A1"]
    h.value = "OLIST  —  O paradoxo do crescimento: vende mais, mas a entrega ameaca o futuro"
    h.font = Font(bold=True, size=18, color=AZUL)
    h.alignment = Alignment(horizontal="left", vertical="center")
    dash.row_dimensions[1].height = 30
    dash.merge_cells("A2:R2")
    s = dash["A2"]
    s.value = "Tech Challenge — Data Analytics | Brazilian E-Commerce Public Dataset by Olist (2017–2018) | Publico: investidores e diretoria"
    s.font = Font(italic=True, size=10, color=CINZA)

    # largura base das colunas
    for col in range(1, 19):
        dash.column_dimensions[get_column_letter(col)].width = 9

    # ---- linha de KPIs (5 cartoes) ----
    kv = {row["indicador"]: row for _, row in kpis.iterrows()}
    cards = [
        ("RECEITA TOTAL", "R$ 13,5 mi", AZUL),
        ("PEDIDOS", "99.092", AZUL),
        ("TICKET MEDIO", "R$ 137,68", AZUL),
        ("TAXA DE RECOMPRA", "3,1%", VERMELHO),
        ("PEDIDOS ATRASADOS", "8,1%", VERMELHO),
    ]
    start_row = 4
    for i, (titulo, valor, cor) in enumerate(cards):
        kpi_card(dash, anchor_col=1 + i * 3, row=start_row, titulo=titulo, valor=valor, cor=cor)

    # banda de contexto sob os KPIs
    dash.merge_cells("A7:R7")
    band = dash["A7"]
    band.value = ("Negocio movido a aquisicao (recompra 10x abaixo do mercado ~28%)  →  reputacao e o ativo critico  "
                  "→  atraso derruba a nota (4,29 → 2,57) e expoe R$ 1,2 mi de receita.")
    band.font = Font(size=9, italic=True, color=CINZA)
    band.alignment = Alignment(horizontal="left", vertical="center")

    # ============ GRAFICO A: Receita mensal + nota media (combo) ============
    n = len(mensal)
    bar = BarChart()
    bar.type = "col"
    bar.title = "Crescimento da receita ao longo do tempo (estabiliza em 2018)"
    bar.height = 7.5
    bar.width = 16
    data = Reference(ws_mensal, min_col=3, min_row=1, max_row=n + 1)  # receita
    cats = Reference(ws_mensal, min_col=1, min_row=2, max_row=n + 1)  # ano_mes
    bar.add_data(data, titles_from_data=True)
    bar.set_categories(cats)
    bar.y_axis.title = "Receita (R$)"
    bar.series[0].graphicalProperties.solidFill = AZUL

    line = LineChart()
    ldata = Reference(ws_mensal, min_col=6, min_row=1, max_row=n + 1)  # nota_media
    line.add_data(ldata, titles_from_data=True)
    line.y_axis.axId = 200
    line.y_axis.title = "Nota media"
    line.series[0].graphicalProperties.line.solidFill = LARANJA
    line.series[0].graphicalProperties.line.width = 28000
    bar.y_axis.crosses = "autoZero"
    line.y_axis.crosses = "max"
    bar += line
    bar.legend.position = "b"
    dash.add_chart(bar, "A9")

    # ============ GRAFICO B: Atraso x Nota (o "aha") ============
    b = BarChart()
    b.type = "col"
    b.title = "Quanto mais atrasa, pior a nota (dose-resposta)"
    b.height = 7.5
    b.width = 16
    bdata = Reference(ws_atraso, min_col=2, min_row=1, max_row=len(atraso) + 1)  # nota_media
    bcats = Reference(ws_atraso, min_col=1, min_row=2, max_row=len(atraso) + 1)
    b.add_data(bdata, titles_from_data=True)
    b.set_categories(bcats)
    b.series[0].graphicalProperties.solidFill = VERMELHO
    b.dataLabels = DataLabelList()
    b.dataLabels.showVal = True
    b.legend = None
    b.y_axis.title = "Nota media (1-5)"
    dash.add_chart(b, "J9")

    # ============ GRAFICO C: Simulacao (valor de agir) ============
    c = BarChart()
    c.type = "col"
    c.title = "Valor de agir: receita protegida ao reduzir atrasos (R$)"
    c.height = 7.5
    c.width = 16
    cdata = Reference(ws_simul, min_col=3, min_row=1, max_row=len(simul) + 1)  # receita_protegida
    ccats = Reference(ws_simul, min_col=1, min_row=2, max_row=len(simul) + 1)
    c.add_data(cdata, titles_from_data=True)
    c.set_categories(ccats)
    c.series[0].graphicalProperties.solidFill = VERDE
    c.dataLabels = DataLabelList()
    c.dataLabels.showVal = True
    c.legend = None
    dash.add_chart(c, "A25")

    # ============ GRAFICO D: Top categorias por receita ============
    d = BarChart()
    d.type = "bar"
    d.title = "Top categorias por receita (R$)"
    d.height = 7.5
    d.width = 16
    ddata = Reference(ws_cat, min_col=3, min_row=1, max_row=len(categoria) + 1)  # receita
    dcats = Reference(ws_cat, min_col=1, min_row=2, max_row=len(categoria) + 1)
    d.add_data(ddata, titles_from_data=True)
    d.set_categories(dcats)
    d.series[0].graphicalProperties.solidFill = AZUL
    d.legend = None
    dash.add_chart(d, "J25")

    # rodape sintese
    dash.merge_cells("A41:R41")
    foot = dash["A41"]
    foot.value = "Logistica nao e custo — e a alavanca que protege o crescimento. Reduzir atrasos em 50% protege ~R$ 579 mil e evita ~1.755 detratores."
    foot.font = Font(bold=True, size=10, color=AZUL)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"OK -> {OUT.relative_to(ROOT)}")
    print("Abas:", wb.sheetnames)


if __name__ == "__main__":
    main()
