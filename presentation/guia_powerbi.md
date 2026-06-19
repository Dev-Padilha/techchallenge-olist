# Guia de Montagem — Dashboard Power BI (Olist)
### "Do CSV ao dashboard executivo em ~30 minutos"

Este guia transforma os arquivos de `data/bi/` em um dashboard de **1 página** que conta a
mesma história do relatório: **Crescimento → Risco logístico → Atraso destrói reputação → Valor de agir.**

> ⚠️ Regra de ouro: o dashboard deve **contar uma história**, não ser um amontoado de gráficos.
> Siga a ordem de leitura (cima→baixo, esquerda→direita) sugerida no layout.

---

## 0. Pré-requisitos
- **Power BI Desktop** (Windows) — gratuito na Microsoft Store. No Mac: usar VM Windows ou Power BI Service (web).
- Os 7 arquivos da pasta `data/bi/` (gerados por `python src/export_bi.py`).

---

## 1. Importar os dados (5 min)
1. `Página Inicial > Obter Dados > Pasta` → aponte para `data/bi/`. (Ou `Texto/CSV` arquivo a arquivo.)
2. Importe as 7 tabelas: **fato_pedidos, agg_mensal, agg_estado, agg_categoria, tab_atraso_nota, tab_simulacao, kpis**.
3. Em cada tabela, confira os tipos: valores monetários como **Número Decimal**, `ano_mes` como **Texto**, `data_compra` como **Data**.

## 2. Modelo (relacionamentos) (3 min)
Para um dashboard simples, as tabelas `agg_*` são **autossuficientes** (já agregadas) — você
pode usá-las direto, sem relacionamento. Opcional (avançado): criar uma `dim_calendario` e
ligar a `fato_pedidos[data_compra]` para análises temporais ricas.

> 👉 Caminho rápido recomendado: use `kpis` e `agg_*` para os visuais. Use `fato_pedidos` só
> se quiser slicers interativos (UF, categoria, situação de entrega).

## 3. Medidas DAX (copie e cole) (5 min)
`Modelagem > Nova Medida`. Estas usam a `fato_pedidos` (permite slicers dinâmicos):

```DAX
Receita = SUM(fato_pedidos[receita_produto])

Pedidos = DISTINCTCOUNT(fato_pedidos[id_pedido])

Ticket Medio = DIVIDE([Receita], [Pedidos])

% Atraso =
DIVIDE(
    CALCULATE([Pedidos], fato_pedidos[entregue_atrasado] = 1),
    CALCULATE([Pedidos], fato_pedidos[entregue] = 1)
)

Nota Media = AVERAGE(fato_pedidos[nota_avaliacao])

% Detratores =
DIVIDE(
    CALCULATE([Pedidos], fato_pedidos[detrator] = 1),
    CALCULATE([Pedidos], NOT(ISBLANK(fato_pedidos[nota_avaliacao])))
)

Receita Exposta a Atraso =
CALCULATE([Receita], fato_pedidos[entregue_atrasado] = 1)
```

## 4. Tema de cores (1 min)
`Exibição > Temas > Personalizar tema atual`. Paleta executiva (mesma das figuras):
| Uso | Hex |
|---|---|
| Primária (azul) | `#1F4E79` |
| Alerta (vermelho) | `#C0392B` |
| Positivo (verde) | `#2E8B57` |
| Destaque (laranja) | `#E07B39` |
| Neutro (cinza) | `#7F8C8D` |

---

## 5. Layout da página (a narrativa) (10 min)

```
┌──────────────────────────────────────────────────────────────────────┐
│  TÍTULO:  Olist — O paradoxo do crescimento        [slicer: UF] [Ano]  │
├───────────┬───────────┬───────────┬───────────┬──────────────────────┤
│  CARTÃO   │  CARTÃO   │  CARTÃO   │  CARTÃO   │   CARTÃO              │  ← Linha de KPIs
│ Receita   │ Pedidos   │ Ticket    │ Recompra  │  % Atraso            │
│ R$ 13,5mi │  99 mil   │ R$ 137,68 │   3,1%    │   8,1%               │
├───────────┴───────────┴───────────┼───────────┴──────────────────────┤
│  (A) Receita mensal + tendência    │  (B) Mapa de risco por estado     │
│      [Gráfico de colunas/linha]    │      [Mapa ou dispersão]          │
├────────────────────────────────────┼──────────────────────────────────┤
│  (C) Atraso × Nota (dose-resposta) │  (D) Simulação: receita protegida │
│      [Colunas, eixo faixa_atraso]  │      [Colunas, eixo cenário]      │
└────────────────────────────────────┴──────────────────────────────────┘
```

### Visual por visual

**Linha de KPIs (cartões):** 5 visuais "Cartão". Use as medidas `[Receita]`, `[Pedidos]`,
`[Ticket Medio]`, recompra (do `kpis.csv`, valor fixo 3,12%), `[% Atraso]`.
Formate Receita como R$ e use separador de milhar.

**(A) Receita mensal + tendência** — visual *Gráfico de colunas e linhas*:
- Eixo X: `agg_mensal[ano_mes]` · Colunas: `agg_mensal[receita]` · Linha: `agg_mensal[nota_media]` (eixo secundário).
- Título: "Crescimento da receita e satisfação ao longo do tempo".
- Ative *Linha de tendência* nas Análises. Mensagem: cresce, mas estabiliza.

**(B) Mapa de risco por estado** — visual *Mapa* (ou *Dispersão* se mapa não carregar):
- Localização: `agg_estado[uf]` · Tamanho da bolha: `agg_estado[pedidos]` · Cor: `agg_estado[pct_atraso]` (vermelho = pior).
- Alternativa dispersão: X = `prazo_medio_dias`, Y = `pct_atraso`, tamanho = `pedidos`.
- Título: "Onde o atraso se concentra".

**(C) Atraso × Nota (o gráfico-chave)** — visual *Gráfico de colunas*:
- Eixo X: `tab_atraso_nota[faixa_atraso]` (ordene: Adiantado>10d → Atraso>10d) · Valor: `nota_media`.
- Formatação condicional da cor: verde nas faixas "no prazo/adiantado", vermelho nas "atraso".
- Título: "Quanto mais atrasa, pior a nota". **Este é o momento 'aha' — destaque-o.**

**(D) Simulação** — visual *Gráfico de colunas*:
- Eixo X: `tab_simulacao[cenario]` · Valor: `receita_protegida`.
- Dica: adicione `detratores_evitados` como rótulo/tooltip.
- Título: "Quanto a Olist protege ao reduzir atrasos".

**Slicers (topo direito):** `fato_pedidos[uf]` e `fato_pedidos[ano]` — deixam o diretor explorar.

---

## 6. Acabamento profissional (5 min)
- **Título da página** em caixa de texto, fonte 20+, negrito, cor `#1F4E79`.
- Uma **frase-síntese** no rodapé: *"Logística não é custo — é a alavanca que protege o crescimento."*
- Alinhe os visuais (use *Formatar > Alinhar*). Mesma fonte em todos os títulos.
- Remova bordas poluídas; fundo branco/cinza claro.
- **Exporte como imagem/PDF** (`Arquivo > Exportar`) para usar nos slides e no vídeo.

---

## 7. O que dizer ao apresentar o dashboard (15 segundos)
> "Este painel resume a tese: no topo, o tamanho do negócio. À esquerda, o crescimento que
> estabiliza. No centro, a prova de que o atraso derruba a nota. E à direita, quanto a empresa
> ganha ao agir. Tudo filtrável por estado e ano."

---

## Mapa arquivo → visual (referência rápida)
| Arquivo | Alimenta |
|---|---|
| `kpis.csv` | Cartões de KPI |
| `agg_mensal.csv` | Visual (A) receita/tendência |
| `agg_estado.csv` | Visual (B) mapa de risco |
| `tab_atraso_nota.csv` | Visual (C) dose-resposta |
| `tab_simulacao.csv` | Visual (D) simulação |
| `agg_categoria.csv` | (extra) top categorias, se quiser 2ª página |
| `fato_pedidos.csv` | Slicers + medidas DAX |
