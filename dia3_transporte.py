# DIA 3 — Transportation Problem com Gurobi
# Contexto: distribuidora precisa enviar produtos de 3 fábricas para 4 centros
# de distribuição minimizando custo total de frete.

# PROBLEMA
# 3 fábricas (F1, F2, F3) com oferta limitada.
# 4 centros de distribuição (C1, C2, C3, C4) com demanda conhecida.
# Custo de frete por unidade entre cada fábrica e centro é dado.
# Restrição: oferta total = demanda total (problema balanceado).
#
# FORMULAÇÃO MATEMÁTICA
# Índices:
#   i ∈ {0,1,2}    — fábricas
#   j ∈ {0,1,2,3}  — centros de distribuição
#
# Parâmetros:
#   oferta[i]   = capacidade de produção da fábrica i
#   demanda[j]  = demanda do centro j
#   c[i][j]     = custo de frete por unidade de i para j
#
# Variáveis:
#   x[i][j] >= 0 — unidades enviadas de fábrica i para centro j
#
# Função objetivo:
#   min  Σ Σ c[i][j] * x[i][j]
#
# Restrições:
#   Σ_j x[i][j] <= oferta[i]   para cada fábrica i
#   Σ_i x[i][j] == demanda[j]  para cada centro j
#   x[i][j] >= 0

import gurobipy as gp
from gurobipy import GRB

fabricas = [0, 1, 2]
centros  = [0, 1, 2, 3]

oferta  = {0: 300, 1: 400, 2: 350}   # unidades disponíveis por fábrica
demanda = {0: 200, 1: 250, 2: 300, 3: 200}  # demanda de cada centro

# Custo de frete por unidade [fábrica][centro]
custo = {
    (0, 0): 8,  (0, 1): 6,  (0, 2): 10, (0, 3): 9,
    (1, 0): 9,  (1, 1): 4,  (1, 2): 7,  (1, 3): 3,
    (2, 0): 5,  (2, 1): 8,  (2, 2): 6,  (2, 3): 7,
}

m = gp.Model("transporte")
m.setParam("OutputFlag", 0)

x = m.addVars(fabricas, centros, lb=0, name="x")

m.setObjective(
    gp.quicksum(custo[i, j] * x[i, j] for i in fabricas for j in centros),
    GRB.MINIMIZE
)

# Restrições de oferta
for i in fabricas:
    m.addConstr(gp.quicksum(x[i, j] for j in centros) <= oferta[i], f"oferta_{i}")

# Restrições de demanda
for j in centros:
    m.addConstr(gp.quicksum(x[i, j] for i in fabricas) == demanda[j], f"demanda_{j}")

m.optimize()

# Resultados
nomes_f = {0: "Fábrica SP", 1: "Fábrica RJ", 2: "Fábrica MG"}
nomes_c = {0: "Centro Norte", 1: "Centro Sul", 2: "Centro Leste", 3: "Centro Oeste"}

print("=" * 50)
print("RESULTADO — Transportation Problem")
print("=" * 50)
print(f"Custo total mínimo de frete: R$ {m.ObjVal:,.2f}")
print()

print("PLANO DE DISTRIBUIÇÃO")
print("-" * 50)
for i in fabricas:
    enviado = sum(x[i, j].X for j in centros)
    print(f"\n{nomes_f[i]} (oferta: {oferta[i]}u, enviado: {enviado:.0f}u)")
    for j in centros:
        if x[i, j].X > 0.01:
            subtotal = custo[i, j] * x[i, j].X
            print(f"  → {nomes_c[j]}: {x[i,j].X:.0f}u "
                  f"× R${custo[i,j]} = R${subtotal:,.0f}")

print()
print("UTILIZAÇÃO DE CAPACIDADE")
print("-" * 50)
for i in fabricas:
    usado = sum(x[i, j].X for j in centros)
    print(f"  {nomes_f[i]}: {usado:.0f}/{oferta[i]} ({usado/oferta[i]*100:.0f}%)")

print()
print("ATENDIMENTO DE DEMANDA")
print("-" * 50)
for j in centros:
    recebido = sum(x[i, j].X for i in fabricas)
    print(f"  {nomes_c[j]}: {recebido:.0f}/{demanda[j]} ✓")
