# DIA 1 — Programação Linear com Gurobi
# Contexto: cliente de manufatura quer maximizar lucro alocando produção
# entre dois produtos com restrições de capacidade de máquina e mão de obra.

# PROBLEMA
# Uma fábrica produz dois produtos: A e B.
#   - Produto A: lucro R$ 25/unidade, usa 2h de máquina e 1h de mão de obra
#   - Produto B: lucro R$ 30/unidade, usa 1h de máquina e 3h de mão de obra
# Capacidade disponível por semana:
#   - Máquina: 120 horas
#   - Mão de obra: 150 horas
# Pergunta: quantas unidades de A e B produzir para maximizar lucro?

# FORMULAÇÃO MATEMÁTICA
# Variáveis de decisão:
#   x_A = unidades de A produzidas
#   x_B = unidades de B produzidas
#
# Função objetivo (maximizar lucro):
#   max  25*x_A + 30*x_B
#
# Restrições:
#   2*x_A + 1*x_B <= 120   (máquina)
#   1*x_A + 3*x_B <= 150   (mão de obra)
#   x_A, x_B >= 0

import gurobipy as gp
from gurobipy import GRB

m = gp.Model("producao")
m.setParam("OutputFlag", 0)  # silencia log do solver

# Variáveis de decisão (contínuas, >= 0 por padrão)
x_A = m.addVar(name="x_A")
x_B = m.addVar(name="x_B")

# Função objetivo
m.setObjective(25 * x_A + 30 * x_B, GRB.MAXIMIZE)

# Restrições
m.addConstr(2 * x_A + x_B <= 120, "maquina")
m.addConstr(x_A + 3 * x_B <= 150, "mao_de_obra")

m.optimize()

# Resultados
print("=" * 40)
print("RESULTADO — Plano de Produção Ótimo")
print("=" * 40)
print(f"Produto A: {x_A.X:.1f} unidades")
print(f"Produto B: {x_B.X:.1f} unidades")
print(f"Lucro máximo: R$ {m.ObjVal:,.2f}")
print()

# Análise de folga (recursos usados vs disponíveis)
print("UTILIZAÇÃO DE RECURSOS")
print("-" * 40)
uso_maquina = 2 * x_A.X + x_B.X
uso_mao_obra = x_A.X + 3 * x_B.X
print(f"Máquina:     {uso_maquina:.1f}h / 120h ({uso_maquina/120*100:.1f}%)")
print(f"Mão de obra: {uso_mao_obra:.1f}h / 150h ({uso_mao_obra/150*100:.1f}%)")
print()

# Preços-sombra (quanto vale cada hora adicional de recurso)
print("PREÇOS-SOMBRA (valor de 1h extra de capacidade)")
print("-" * 40)
for c in m.getConstrs():
    print(f"{c.ConstrName}: R$ {c.Pi:.2f} por hora adicional")
