# Relatório Executivo — Olist
### O paradoxo do crescimento: a Olist vende mais, mas a entrega ameaça o futuro

*Tech Challenge — Pós-Tech Data Analytics | Brazilian E-Commerce Public Dataset by Olist (2016–2018)*
*Público-alvo: investidores, acionistas e diretoria executiva*

---

## 1. Resumo Executivo

Entre 2017 e 2018, a Olist cresceu rápido. O volume médio mensal de pedidos foi 80% maior em 2018 do que em 2017, a receita de produtos somou R$ 13,5 milhões no período e o ticket médio ficou em R$ 137,68.

Por trás desse crescimento há um risco que passa despercebido. A taxa de recompra é de apenas 3,1%, quase dez vezes abaixo do que se vê em e-commerce maduro (cerca de 28%). Na prática, o negócio é movido por aquisição de clientes novos, e não por fidelização. Num modelo assim, o ativo mais valioso é a reputação: são as avaliações públicas que atraem o próximo cliente.

E é justamente essa reputação que a logística vem corroendo. Pedidos entregues com atraso recebem nota média 2,57, contra 4,29 dos entregues no prazo. Entre os atrasados, 54% viram detratores (nota 1 ou 2), contra 9% nos pedidos pontuais. No período analisado, isso representa R$ 1,2 milhão em receita (8,8%) exposta a uma experiência ruim, e cerca de 3,5 mil clientes transformados desnecessariamente em detratores.

Nossa recomendação central é tratar a pontualidade de entrega como prioridade estratégica de crescimento, não como custo operacional. Reduzir os atrasos pela metade protege cerca de R$ 579 mil de receita e evita aproximadamente 1.755 detratores, preservando o motor de aquisição que sustenta a expansão.

---

## 2. Introdução

A Olist conecta pequenos e médios vendedores aos grandes marketplaces brasileiros. O conjunto de dados analisado cobre cerca de 99 mil pedidos entre setembro de 2016 e outubro de 2018, com informações de clientes, itens, pagamentos, avaliações, vendedores e geolocalização.

A pergunta que orienta este relatório é a de um investidor: a Olist está construindo um negócio que se sustenta no longo prazo, ou está crescendo sobre uma base frágil? Para responder, conectamos três dimensões numa única narrativa: crescimento comercial, eficiência logística e satisfação (que define o valor futuro do cliente).

---

## 3. Metodologia

Fonte: 9 tabelas do Brazilian E-Commerce Public Dataset by Olist (Kaggle).

A preparação dos dados está detalhada e reprodutível em `src/data_prep.py`. Consolidamos as 9 tabelas numa tabela analítica única no grão de pedido (`order_master`). O cliente foi identificado por `customer_unique_id`, e não por `customer_id` (que é reemitido a cada pedido); essa distinção é indispensável para medir recompra corretamente. Também calculamos os tempos de ciclo (compra, aprovação, postagem, entrega) e o atraso frente ao prazo prometido ao cliente.

Sobre qualidade e tratamentos: as análises de prazo e satisfação ficaram restritas aos pedidos efetivamente entregues (96,5 mil). Os registros sem data de entrega (cerca de 3%) foram excluídos das métricas de prazo, com o impacto documentado. Para as séries mensais, usamos uma janela temporal limpa (jan/2017 a ago/2018), descartando os meses-cauda de 2016 e de set–out/2018, que têm volume residual e distorceriam a tendência.

Como dado externo de enriquecimento, usamos um benchmark de mercado para a taxa de recompra do e-commerce (algo entre 20% e 30%), que serve de referência para contextualizar o número da Olist.

Limitações: os dados são de 2016 a 2018; não há custos nem margem reais, então usamos receita como proxy de valor; e correlação não é causalidade. Apontamos associação e risco, não prova causal experimental.

---

## 4. Análise dos Dados

### 4.1 Crescimento acelerado, com sinais de estabilização
A receita mensal saltou de algo entre R$ 100 mil e R$ 400 mil no início de 2017 para cerca de R$ 1 milhão por mês em 2018, com pico na Black Friday de novembro de 2017. A projeção por tendência aponta continuidade do crescimento, mas os dados de 2018 já mostram estabilização em torno de R$ 850 mil a R$ 1 milhão por mês. É o sinal de que a fase de hipercrescimento começa a dar lugar à maturidade. *(Figura 01)*

### 4.2 Onde o tempo se perde
O prazo médio de entrega é de 12,6 dias (mediana de 10,2). A decomposição mostra que a maior parcela está no transporte até o cliente, com mediana de cerca de 7 dias. É a última milha, não o processamento interno. Dos pedidos, 8,1% chegam atrasados em relação ao prazo prometido. *(Figura 02)*

### 4.3 O elo entre atraso e avaliação
Há uma relação dose-resposta clara: quanto maior o atraso, pior a nota. Pedidos no prazo ou adiantados mantêm nota entre 4,2 e 4,3; com atraso de 0 a 5 dias a nota cai para 3,46; e acima de 10 dias de atraso ela despenca para 1,70. A média vai de 2,57 (atrasados) para 4,29 (no prazo). *(Figura 03)*

### 4.4 Um modelo de aquisição, não de retenção
Apenas 3,1% dos clientes compram de novo, bem abaixo do benchmark de mercado (cerca de 28%). A Olist depende de conquistar clientes novos o tempo todo. Isso coloca a reputação pública, ou seja, as avaliações, na condição de ativo estratégico: é ela que alimenta a aquisição. *(Figura 04)*

### 4.5 O custo invisível e a simulação
Como a reputação é o motor da aquisição, o atraso sai caro. No período, R$ 1,2 milhão de receita (8,8%) esteve associada a pedidos com má experiência de entrega, gerando cerca de 3,5 mil detratores excedentes. A simulação mostra o tamanho do ganho ao agir: reduzir os atrasos em 25%, 50% ou 75% protege, respectivamente, R$ 290 mil, R$ 579 mil e R$ 869 mil, e evita 878, 1.755 e 2.633 detratores. *(Figura 05)*

### 4.6 É possível antecipar a insatisfação
Construímos um modelo para estimar a probabilidade de avaliação negativa (nota 1 ou 2) a partir de fatores logísticos. O modelo discrimina bem o risco, com capacidade de acerto de 0,73 (em que 0,5 seria sorte e 1,0 seria perfeito). Mais importante do que prever é explicar: o fator que mais aumenta o risco de nota baixa é o prazo total de entrega, acima até do atraso frente ao prometido. Ou seja, entrega lenta gera insatisfação mesmo quando cumpre o prazo combinado. Isso reforça que a alavanca é encurtar o tempo absoluto de entrega, e não apenas "bater a meta". *(Figura 08)*

### 4.7 Mapas de apoio
O risco logístico se concentra em estados distantes dos centros vendedores, com maior prazo e maior taxa de atraso, enquanto São Paulo concentra o volume com o melhor desempenho *(Figura 06)*. A receita é liderada por saúde e beleza, relógios e presentes, e cama, mesa e banho *(Figura 07)*.

---

## 5. Principais Insights

| # | Insight | Evidência | Impacto no negócio |
|---|---|---|---|
| 1 | Crescimento forte, mas estabilizando | +80% pedidos 2018 vs 2017; platô em 2018 | Fase de maturidade exige eficiência, não só expansão |
| 2 | Negócio movido a aquisição | Recompra 3,1% vs 28% do mercado | Reputação é o ativo crítico |
| 3 | Atraso destrói reputação | Nota 4,29 → 2,57; detratores 9% → 54% | Logística vira alavanca de crescimento |
| 4 | Última milha é o gargalo | Transporte ~7 dias (maior etapa) | Foco de investimento claro |
| 5 | Há valor mensurável em jogo | R$ 1,2 mi exposto; até R$ 869 mil protegíveis | Caso de negócio para investir em logística |

---

## 6. Recomendações

| Prioridade | Recomendação | Benefício esperado | Custo/Esforço | Risco |
|---|---|---|---|---|
| Alta | Atacar atrasos na última milha (transportadoras, prazos realistas, regiões críticas) | Protege até R$ 869 mil e a reputação | Médio | Baixo |
| Alta | Recalibrar prazos prometidos por região (não prometer o que não se cumpre) | Reduz frustração sem mudar operação | Baixo | Baixo |
| Média | Programa de recompra/CRM após entrega bem-sucedida | Elevar recompra acima de 3% destrava muito valor | Médio | Médio |
| Média | Priorizar sellers com alto NPS e entrega rápida | Melhora a reputação média da plataforma | Baixo | Baixo |
| Baixa | Cross-sell nas categorias líderes | Aumenta o ticket médio | Baixo | Baixo |

Sobre previsões e cenários: mantida a tendência, a receita projetada para o trimestre seguinte é de cerca de R$ 3,5 milhões. O ganho das recomendações logísticas (até R$ 869 mil protegidos) é adicional a essa trajetória e, principalmente, protege a reputação que sustenta a aquisição.

---

## 7. Conclusão

A Olist montou um motor de crescimento impressionante, mas que depende de atrair clientes novos e, portanto, de manter uma reputação impecável. Os dados mostram que a logística de última milha é o principal ponto de fricção: cada atraso converte um possível promotor em detrator, com impacto direto e mensurável sobre o ativo mais importante do negócio.

A boa notícia para o investidor é que o problema é localizado, quantificável e acionável. Tratar a pontualidade como prioridade estratégica não é despesa; é a forma mais eficiente de proteger o crescimento já conquistado e viabilizar a próxima fase de expansão.

---

*Reprodutibilidade: todo o pipeline (`src/data_prep.py`, `src/analysis.py`) e as figuras estão versionados no repositório. Resultados regeneráveis com `python src/data_prep.py && python src/analysis.py`.*
