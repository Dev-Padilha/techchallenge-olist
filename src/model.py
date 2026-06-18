"""
================================================================================
 Tech Challenge Olist | ETAPA 6 (bonus) - Modelo Preditivo
--------------------------------------------------------------------------------
 Pergunta de negocio: e POSSIVEL prever, no momento da entrega, se o cliente
 vai dar uma avaliacao NEGATIVA (nota 1-2)? E qual fator mais contribui?

 Tecnica: Regressao Logistica (modelo simples e INTERPRETAVEL - de proposito,
 pois o objetivo executivo e explicar QUAIS alavancas importam, nao so prever).

 Saida executiva: ranking de fatores de risco + grafico de importancia.
================================================================================
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, confusion_matrix

sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 110, "axes.titleweight": "bold",
                     "axes.spines.top": False, "axes.spines.right": False})
AZUL, VERMELHO, VERDE = "#1f4e79", "#c0392b", "#2e8b57"

df = pd.read_csv("data/processed/order_master.csv")
ent = df[df["order_status"] == "delivered"].copy()

# ----------------------------------------------------------- variaveis (X) e alvo (y)
ent = ent.dropna(subset=["review_score", "atraso_dias", "lead_time_total",
                         "receita_frete", "receita_produto"])
ent["alvo_nota_baixa"] = (ent["review_score"] <= 2).astype(int)   # 1 = detrator

feat = {
    "atraso_dias":      "Atraso na entrega (dias)",
    "lead_time_total":  "Prazo total de entrega (dias)",
    "receita_frete":    "Valor do frete (R$)",
    "receita_produto":  "Valor do produto (R$)",
    "n_itens":          "Qtd. de itens",
    "parcelas":         "Nº de parcelas",
}
ent["n_itens"] = ent["n_itens"].fillna(1)
ent["parcelas"] = ent["parcelas"].fillna(1)
X = ent[list(feat.keys())].astype(float)
y = ent["alvo_nota_baixa"]

# --------------------------------------------------------------------- treino/teste
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
sc = StandardScaler().fit(Xtr)
Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

modelo = LogisticRegression(max_iter=1000, class_weight="balanced")
modelo.fit(Xtr_s, ytr)

prob = modelo.predict_proba(Xte_s)[:, 1]
auc = roc_auc_score(yte, prob)

# Importancia = coeficientes padronizados (mesma escala -> comparaveis)
coef = pd.Series(modelo.coef_[0], index=[feat[c] for c in feat.keys()])
coef = coef.sort_values()

# --------------------------------------------------------------------- grafico
fig, ax = plt.subplots(figsize=(9, 5))
cores = [VERMELHO if v > 0 else VERDE for v in coef.values]
bars = ax.barh(coef.index, coef.values, color=cores)
ax.axvline(0, color="k", lw=.8)
ax.set_title(f"O que mais prevê uma avaliação negativa (poder do modelo: AUC {auc:.2f})")
ax.set_xlabel("← reduz risco        Peso no risco de nota baixa        aumenta risco →")
plt.tight_layout(); plt.savefig("figures/08_modelo_fatores_risco.png"); plt.close()

# --------------------------------------------------------------------- achados
print("\n" + "#"*70 + "\n MODELO PREDITIVO - risco de avaliacao negativa\n" + "#"*70)
print(f"  Base: {len(ent):,} pedidos entregues com avaliacao")
print(f"  Taxa real de detratores (nota 1-2): {y.mean()*100:.1f}%")
print(f"  Poder de discriminacao do modelo (AUC): {auc:.3f}")
print("  Ranking de fatores (coef. padronizado; + aumenta risco):")
for nome, v in coef.sort_values(ascending=False).items():
    print(f"      {nome:32s}: {v:+.3f}")
print("\n[OK] figura salva em figures/08_modelo_fatores_risco.png")
