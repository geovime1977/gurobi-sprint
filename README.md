# Gurobi Sprint — Preparação Técnica em Otimização

Sprint de 7 dias cobrindo Pesquisa Operacional aplicada com **Gurobi Optimizer** em Python. Desenvolvida para preparação técnica em entrevistas de consultoria de otimização (Supply Chain, Manufacturing, Workforce, Finance).

## Por que Gurobi

O Gurobi é o solver comercial de referência do mercado — usado por Accenture, McKinsey, IBM e grandes empresas de logística e finanças. Diferencia-se do PuLP/OR-Tools por oferecer MIP Gap nativo, Warm Start, preços-sombra automáticos e performance superior em problemas de grande escala.

## Estrutura

| Arquivo | Tema | Conceitos |
|---------|------|-----------|
| `dia1_lp_basico.py` | Programação Linear | variáveis contínuas, função objetivo, restrições, preços-sombra |
| `dia2_facility_location.py` | MILP — Facility Location | variáveis binárias, abertura de instalações, custo fixo + variável |
| `dia3_transporte.py` | Transportation Problem | fluxo em rede, oferta/demanda, custo mínimo |
| `dia4_assignment.py` | Assignment / Scheduling | matching ótimo, alocação 1-para-1 |
| `dia5_cvrp.py` | CVRP — Roteirização | Vehicle Routing, capacidade, subtour elimination |
| `dia6_heuristicas.py` | Heurísticas + Warm Start | MIP Gap, time limit, callbacks, warm start |
| `dia7_case.py` | Case completo | problema real → modelo → código → resultado → ROI |

## Setup

```bash
git clone https://github.com/geovime1977/gurobi-sprint.git
cd gurobi-sprint
uv venv && uv pip install gurobipy
```

Licença necessária: conta gratuita em [gurobi.com](https://gurobi.com) → Academic / Online Course License.

## Rodar um modelo

```bash
source .venv/bin/activate
python dia1_lp_basico.py
```

## Exemplo de output (Dia 1 — LP)

```
========================================
RESULTADO — Plano de Produção Ótimo
========================================
Produto A: 42.0 unidades
Produto B: 36.0 unidades
Lucro máximo: R$ 2,130.00

UTILIZAÇÃO DE RECURSOS
----------------------------------------
Máquina:     120.0h / 120h (100.0%)
Mão de obra: 150.0h / 150h (100.0%)

PREÇOS-SOMBRA (valor de 1h extra de capacidade)
----------------------------------------
maquina: R$ 9.00 por hora adicional
mao_de_obra: R$ 7.00 por hora adicional
```

## Stack

- Python 3.13+
- gurobipy 13.0.2
- uv (gerenciador de ambiente)

## Autor

**Geovane Virmecati** — Consultor PO/Analytics, Fundador da Eixo Estratégico
[GitHub](https://github.com/geovime1977) · [LinkedIn](https://linkedin.com/in/geovanevirmecati)
