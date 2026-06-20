# Tech Challenge — Olist | Relatório Executivo para Investidores

O paradoxo do crescimento: a Olist vende mais, mas a entrega ameaça o futuro.

Análise do *Brazilian E-Commerce Public Dataset by Olist* (2016–2018), transformando dados
transacionais numa tese de investimento. A ideia central é que a Olist é um negócio movido a
aquisição, cuja reputação (um ativo estratégico) está sendo corroída pelos atrasos de entrega.

## Principais achados (dados reais)
- Crescimento de 80% em pedidos (2018 vs 2017), receita de R$ 13,5 mi e ticket médio de R$ 137,68.
- Recompra de apenas 3,1% (contra cerca de 28% do e-commerce maduro), ou seja, negócio dependente de aquisição.
- Atraso derruba a avaliação: nota de 4,29 para 2,57; detratores de 9% para 54%.
- R$ 1,2 mi (8,8%) de receita exposta a má experiência de entrega.
- Reduzir atrasos pela metade protege cerca de R$ 579 mil e evita cerca de 1.755 detratores.

## Estrutura do repositório
```
techchallenge-olist/
├── data/                      # CSVs brutos do Olist (dados pesados não versionados)
│   └── processed/             # tabela analítica gerada (order_master.csv)
├── src/
│   ├── data_prep.py           # ETL: 9 tabelas -> tabela analítica por pedido
│   ├── analysis.py            # EDA, insights e simulação -> figuras + achados
│   ├── model.py               # modelo preditivo (risco de avaliação negativa)
│   ├── export_bi.py           # exporta o modelo em estrela (data/bi/), fonte do dashboard
│   ├── export_excel.py        # gera o dashboard executivo pronto em Excel (.xlsx)
│   └── dashboard.py           # dashboard interativo (HTML) estilo BI
├── figures/                   # 8 gráficos executivos (PNG)
├── dashboard/                 # dashboard_olist.xlsx (Excel, pronto) + .html + .png
├── report/relatorio_executivo.md
├── presentation/apresentacao.md
├── requirements.txt
└── README.md
```

## Como reproduzir
```bash
pip install -r requirements.txt
# coloque os CSVs do Olist em data/ (download no Kaggle)
python src/data_prep.py     # gera data/processed/order_master.csv
python src/analysis.py      # gera figures/ (01-07) e imprime os achados-chave
python src/model.py         # modelo preditivo -> figures/08 + ranking de fatores
python src/export_bi.py     # gera data/bi/ (modelo em estrela)
python src/export_excel.py  # gera dashboard/dashboard_olist.xlsx (Excel, pronto para abrir)
```

## Dashboard (Excel)
`dashboard/dashboard_olist.xlsx` é o painel executivo de uma página, já montado, com KPIs e
quatro gráficos. Ele conta a mesma história do relatório: crescimento, risco logístico, o
atraso destruindo reputação e o valor de agir. Abre em Excel, Google Sheets ou Numbers, sem
depender de Power BI ou Windows. Para regenerar: `python src/export_excel.py`.

## Decisões metodológicas
- Cliente real é `customer_unique_id`, não `customer_id`.
- Métricas de prazo e satisfação só em pedidos entregues.
- Janela mensal limpa de jan/2017 a ago/2018 (descarta as caudas de 2016 e set–out/2018).
- Nulos de entrega (cerca de 3%) excluídos das métricas de prazo e documentados.
- Dado externo: benchmark de recompra do e-commerce (cerca de 28%).

## Limitações
Dados de 2016 a 2018, sem custos ou margem reais (receita usada como proxy de valor), e
associação não é causalidade. Detalhes no relatório.

## Dataset
Brazilian E-Commerce Public Dataset by Olist (Kaggle).
