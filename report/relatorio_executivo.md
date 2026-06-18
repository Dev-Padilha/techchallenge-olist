# Relatório Executivo — Olist
### O paradoxo do crescimento: a Olist vende mais, mas a entrega ameaça o futuro

*Tech Challenge — Pós-Tech Data Analytics | Brazilian E-Commerce Public Dataset by Olist (2016–2018)*
*Público-alvo: investidores, acionistas e diretoria executiva*

---

## 1. Resumo Executivo

Entre 2017 e 2018, a Olist apresentou **crescimento expressivo**: o volume médio mensal de pedidos foi **80% maior em 2018 do que em 2017**, com receita de produtos de **R$ 13,5 milhões** no período e ticket médio de **R$ 137,68**.

Por trás desse crescimento, porém, há um risco silencioso. **A recompra é de apenas 3,1%** — quase dez vezes abaixo do padrão de e-commerce maduro (~28%). Ou seja, **o negócio é movido por aquisição de clientes novos, não por fidelização.** Nesse modelo, o ativo mais valioso é a **reputação**: as avaliações públicas que atraem o próximo cliente.

E é exatamente essa reputação que a logística está corroendo. **Pedidos entregues com atraso recebem nota média 2,57, contra 4,29 dos entregues no prazo.** Entre os pedidos atrasados, **54% viram detratores** (nota 1–2), contra 9% nos pedidos pontuais. No período analisado, isso representa **R$ 1,2 milhão em receita (8,8%) exposta a uma experiência ruim** e cerca de **3,5 mil clientes transformados desnecessariamente em detratores.**

**Recomendação central:** tratar a pontualidade de entrega como prioridade estratégica de crescimento — não como custo operacional. Reduzir os atrasos em 50% protege **~R$ 579 mil** de receita da má experiência e evita **~1.755 detratores**, preservando o motor de aquisição que sustenta a expansão.

---

## 2. Introdução

A Olist conecta pequenos e médios vendedores aos grandes marketplaces brasileiros. O conjunto de dados analisado cobre **~99 mil pedidos entre setembro de 2016 e outubro de 2018**, com informações de clientes, itens, pagamentos, avaliações, vendedores e geolocalização.

Este relatório responde a uma pergunta de investidor: **a Olist está construindo um negócio que se sustenta no longo prazo, ou está crescendo sobre uma base frágil?** Para isso, conectamos três dimensões em uma única narrativa: **crescimento comercial → eficiência logística → satisfação e valor futuro do cliente.**

---

## 3. Metodologia

**Fonte:** 9 tabelas do Brazilian E-Commerce Public Dataset by Olist (Kaggle).

**Preparação dos dados** (detalhada e reprodutível em `src/data_prep.py`):
- Consolidação das 9 tabelas em uma **tabela analítica única no grão de pedido** (`order_master`).
- **Cliente identificado por `customer_unique_id`** (e não `customer_id`, que é reemitido a cada pedido) — premissa indispensável para medir recompra corretamente.
- Cálculo de tempos de ciclo (compra → aprovação → postagem → entrega) e do **atraso frente ao prazo prometido ao cliente**.

**Tratamentos e qualidade:**
- Análises de prazo e satisfação restritas a **pedidos efetivamente entregues** (96,5 mil).
- Registros sem data de entrega (~3%) excluídos das métricas de prazo, e o impacto documentado.
- **Janela temporal limpa (jan/2017 a ago/2018)** para séries mensais, descartando os meses-cauda de 2016 e set–out/2018 (volume residual que distorceria tendências).

**Dado externo (enriquecimento):** benchmark de mercado de taxa de recompra do e-commerce (~20–30%), usado como referência para contextualizar a recompra da Olist.

**Limitações:** dados de 2016–2018; ausência de custos/margem reais (usamos receita como proxy de valor); correlação não implica causalidade — apontamos associação e risco, não prova causal experimental.

---

## 4. Análise dos Dados

### 4.1 Crescimento comercial acelerado — mas com sinais de estabilização
A receita mensal saltou de patamares de R$ 100–400 mil no início de 2017 para cerca de **R$ 1 milhão/mês** em 2018, com pico na **Black Friday de novembro/2017**. A projeção por tendência aponta continuidade do crescimento, mas os dados de 2018 já mostram **estabilização em torno de R$ 850 mil–1 mi/mês** — sinal de que a fase de hipercrescimento dá lugar à maturidade. *(Figura 01)*

### 4.2 Onde o tempo se perde
O prazo médio de entrega é de **12,6 dias** (mediana 10,2). A decomposição revela que a maior parcela está no **transporte até o cliente (~7 dias de mediana)** — etapa logística de última milha, não no processamento interno. **8,1% dos pedidos chegam atrasados** em relação ao prazo prometido. *(Figura 02)*

### 4.3 O elo causal: atraso destrói a avaliação
Existe uma clara **relação dose-resposta**: quanto maior o atraso, pior a nota. Pedidos entregues no prazo ou adiantados mantêm nota ~4,2–4,3; com atraso de 0–5 dias a nota cai para 3,46; e **acima de 10 dias de atraso despenca para 1,70**. A nota média salta de **2,57 (atrasados) para 4,29 (no prazo)**. *(Figura 03)*

### 4.4 O modelo é de aquisição, não de retenção
Apenas **3,1% dos clientes compram novamente** — muito abaixo do benchmark de mercado (~28%). A Olist depende de **conquistar clientes novos continuamente**. Isso eleva a reputação pública (avaliações) à condição de **ativo estratégico**: é ela que alimenta a aquisição. *(Figura 04)*

### 4.5 O custo invisível e a simulação
Como a reputação é o motor da aquisição, o atraso é caro. No período, **R$ 1,2 milhão de receita (8,8%) esteve associada a pedidos com má experiência de entrega**, gerando **~3,5 mil detratores excedentes**. A simulação mostra o valor de agir: reduzir os atrasos em 25%/50%/75% protege, respectivamente, **R$ 290 mil / R$ 579 mil / R$ 869 mil** e evita **878 / 1.755 / 2.633 detratores**. *(Figura 05)*

### 4.6 Modelo preditivo: é possível antecipar a insatisfação
Construímos um modelo para estimar a **probabilidade de avaliação negativa (nota 1–2)** a partir de fatores logísticos. O modelo discrimina bem o risco (capacidade de acerto medida em **0,73**, onde 0,5 seria sorte e 1,0 perfeito). Mais importante que prever é **explicar**: o fator que mais aumenta o risco de uma nota baixa é o **prazo total de entrega** — acima até do atraso frente ao prometido. Em outras palavras, **entrega lenta gera insatisfação mesmo quando cumpre o prazo combinado**. Isso reforça que a alavanca é encurtar o tempo absoluto de entrega, não apenas "bater a meta". *(Figura 08)*

### 4.7 Mapas de apoio
O **risco logístico se concentra em estados distantes dos centros vendedores** (maior prazo e maior taxa de atraso), enquanto SP concentra o volume com melhor desempenho *(Figura 06)*. A receita é liderada por **saúde & beleza, relógios & presentes e cama, mesa & banho** *(Figura 07)*.

---

## 5. Principais Insights

| # | Insight | Evidência | Impacto no negócio |
|---|---|---|---|
| 1 | Crescimento forte, mas estabilizando | +80% pedidos 2018 vs 2017; platô em 2018 | Fase de maturidade exige eficiência, não só expansão |
| 2 | Negócio movido a aquisição | Recompra 3,1% vs 28% do mercado | Reputação é o ativo crítico |
| 3 | Atraso destrói reputação | Nota 4,29→2,57; detratores 9%→54% | Logística vira alavanca de crescimento |
| 4 | Última milha é o gargalo | Transporte ~7 dias (maior etapa) | Foco de investimento claro |
| 5 | Há valor mensurável em jogo | R$ 1,2 mi exposto; até R$ 869 mil protegíveis | Caso de negócio para investir em logística |

---

## 6. Recomendações

| Prioridade | Recomendação | Benefício esperado | Custo/Esforço | Risco |
|---|---|---|---|---|
| 🔴 Alta | Atacar atrasos na última milha (transportadoras, prazos realistas, regiões críticas) | Protege até R$ 869 mil e a reputação | Médio | Baixo |
| 🔴 Alta | Recalibrar prazos prometidos por região (não prometer o que não se cumpre) | Reduz frustração sem mudar operação | Baixo | Baixo |
| 🟠 Média | Programa de recompra/CRM pós-entrega bem-sucedida | Elevar recompra acima de 3% destrava enorme valor | Médio | Médio |
| 🟠 Média | Priorizar sellers com alto NPS e entrega rápida | Melhora reputação média da plataforma | Baixo | Baixo |
| 🟡 Baixa | Cross-sell nas categorias líderes | Aumenta ticket médio | Baixo | Baixo |

**Previsões/cenários:** mantida a tendência, a receita projetada para o trimestre seguinte é de **~R$ 3,5 milhões**. O ganho incremental das recomendações logísticas (até R$ 869 mil protegidos) é **adicional** a essa trajetória e, sobretudo, **protege a reputação que sustenta a aquisição**.

---

## 7. Conclusão

A Olist construiu um motor de crescimento impressionante, mas que depende de **atrair clientes novos** — e, portanto, de **manter uma reputação impecável**. Os dados mostram que a **logística de última milha é o principal ponto de fricção**: cada atraso converte um potencial promotor em detrator, com impacto direto e mensurável sobre o ativo mais importante do negócio.

A boa notícia para o investidor: **o problema é localizado, quantificável e acionável.** Tratar a pontualidade como prioridade estratégica não é despesa — é a forma mais eficiente de proteger o crescimento já conquistado e viabilizar a próxima fase de expansão.

---

*Reprodutibilidade: todo o pipeline (`src/data_prep.py`, `src/analysis.py`) e as figuras estão versionados no repositório. Resultados regeneráveis com `python src/data_prep.py && python src/analysis.py`.*
