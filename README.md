# Tech Challenge — Olist | Relatório Executivo para Investidores

> **O paradoxo do crescimento: a Olist vende mais, mas a entrega ameaça o futuro.**

Análise do *Brazilian E-Commerce Public Dataset by Olist* (2016–2018) transformando dados
transacionais em uma tese de investimento: **a Olist é um negócio movido a aquisição, cuja
reputação — ativo estratégico — está sendo corroída por atrasos de entrega.**

## 📊 Principais achados (dados reais)
- Crescimento de **+80%** em pedidos (2018 vs 2017); receita de **R$ 13,5 mi**; ticket médio **R$ 137,68**.
- Recompra de apenas **3,1%** (vs ~28% do e-commerce maduro) → negócio dependente de aquisição.
- Atraso derruba a avaliação: nota **4,29 → 2,57**; detratores **9% → 54%**.
- **R$ 1,2 mi (8,8%) de receita exposta** a má experiência de entrega.
- Reduzir atrasos em 50% protege **~R$ 579 mil** e evita **~1.755 detratores**.

## 🗂 Estrutura do repositório
```
techchallenge-olist/
├── data/                      # CSVs brutos do Olist (não versionar dados pesados)
│   └── processed/             # tabela analítica gerada (order_master.csv)
├── src/
│   ├── data_prep.py           # ETL: 9 tabelas -> tabela analítica por pedido
│   ├── analysis.py            # EDA, insights e simulação -> figuras + achados
│   ├── model.py               # modelo preditivo (risco de avaliação negativa)
│   └── export_bi.py           # exporta modelo em estrela para Power BI (data/bi/)
├── figures/                   # 8 gráficos executivos (PNG)
├── report/relatorio_executivo.md
├── presentation/apresentacao.md
├── requirements.txt
└── README.md
```

## ▶️ Como reproduzir
```bash
pip install -r requirements.txt
# coloque os CSVs do Olist em data/ (download no Kaggle)
python src/data_prep.py     # gera data/processed/order_master.csv
python src/analysis.py      # gera figures/ (01-07) e imprime os achados-chave
python src/model.py         # modelo preditivo -> figures/08 + ranking de fatores
python src/export_bi.py     # gera data/bi/ (modelo p/ Power BI) — ver presentation/guia_powerbi.md
```

## 🔎 Decisões metodológicas (governança)
- Cliente real = `customer_unique_id` (não `customer_id`).
- Métricas de prazo/satisfação só em pedidos **entregues**.
- Janela mensal limpa **jan/2017–ago/2018** (descarta caudas de 2016 e set–out/2018).
- Nulos de entrega (~3%) excluídos das métricas de prazo e documentados.
- Dado externo: benchmark de recompra de e-commerce (~28%).

## ⚠️ Limitações
Dados de 2016–2018; sem custos/margem reais (receita como proxy de valor);
associação ≠ causalidade. Detalhes no relatório.

## 📦 Dataset
Brazilian E-Commerce Public Dataset by Olist — Kaggle.
