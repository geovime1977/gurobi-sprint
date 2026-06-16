# DIA 5 — CVRP: Capacitated Vehicle Routing Problem com Gurobi
# Contexto: distribuidora precisa roteirizar 3 veículos para atender
# 6 clientes partindo e retornando ao depósito central.
# Cada veículo tem capacidade máxima de carga.
# Objetivo: minimizar distância total percorrida.

# FORMULAÇÃO (MTZ — Miller-Tucker-Zemlin)
# Índices:
#   0        = depósito
#   1..6     = clientes
#   k ∈ K    = veículos
#
# Parâmetros:
#   d[i][j]  = distância entre nós i e j
#   q[i]     = demanda do cliente i
#   Q        = capacidade máxima por veículo
#
# Variáveis:
#   x[i][j][k] ∈ {0,1} — veículo k percorre arco (i→j)
#   u[i][k]    >= 0     — carga acumulada ao chegar em i com veículo k (MTZ)
#
# Função objetivo:
#   min  Σ Σ Σ d[i][j] * x[i][j][k]
#
# Restrições:
#   Cada cliente visitado exatamente 1 vez
#   Cada veículo sai e volta ao depósito
#   Capacidade respeitada por veículo
#   Eliminação de subtours via MTZ

import gurobipy as gp
from gurobipy import GRB
import math

# Coordenadas dos nós (depósito + 6 clientes)
coords = {
    0: (0, 0),    # depósito
    1: (2, 4),    2: (5, 2),    3: (8, 5),
    4: (6, 8),    5: (1, 7),    6: (9, 2),
}
clientes  = list(range(1, 7))
nos       = list(range(7))
veiculos  = [0, 1, 2]

demanda  = {1: 20, 2: 30, 3: 25, 4: 15, 5: 20, 6: 30}
capacidade = 70  # por veículo

def dist(i, j):
    xi, yi = coords[i]
    xj, yj = coords[j]
    return round(math.sqrt((xi-xj)**2 + (yi-yj)**2), 2)

d = {(i, j): dist(i, j) for i in nos for j in nos if i != j}

m = gp.Model("cvrp")
m.setParam("OutputFlag", 0)
m.setParam("TimeLimit", 60)

# Variáveis
x = m.addVars(nos, nos, veiculos, vtype=GRB.BINARY, name="x")
u = m.addVars(nos, veiculos, lb=0, name="u")

# Função objetivo
m.setObjective(
    gp.quicksum(d[i, j] * x[i, j, k]
                for i in nos for j in nos for k in veiculos if i != j),
    GRB.MINIMIZE
)

# Cada cliente visitado exatamente 1 vez
for j in clientes:
    m.addConstr(
        gp.quicksum(x[i, j, k] for i in nos for k in veiculos if i != j) == 1,
        f"visita_{j}"
    )

# Cada veículo sai do depósito no máximo 1 vez
for k in veiculos:
    m.addConstr(
        gp.quicksum(x[0, j, k] for j in clientes) <= 1,
        f"saida_{k}"
    )

# Conservação de fluxo: quem entra, sai
for k in veiculos:
    for h in clientes:
        m.addConstr(
            gp.quicksum(x[i, h, k] for i in nos if i != h) ==
            gp.quicksum(x[h, j, k] for j in nos if j != h),
            f"fluxo_{h}_{k}"
        )

# Retorno ao depósito
for k in veiculos:
    m.addConstr(
        gp.quicksum(x[i, 0, k] for i in clientes) ==
        gp.quicksum(x[0, j, k] for j in clientes),
        f"retorno_{k}"
    )

# Capacidade + eliminação de subtours (MTZ)
for k in veiculos:
    for i in clientes:
        m.addConstr(u[i, k] >= demanda[i], f"carga_min_{i}_{k}")
        m.addConstr(u[i, k] <= capacidade, f"carga_max_{i}_{k}")

for k in veiculos:
    for i in clientes:
        for j in clientes:
            if i != j:
                m.addConstr(
                    u[j, k] >= u[i, k] + demanda[j] - capacidade * (1 - x[i, j, k]),
                    f"mtz_{i}_{j}_{k}"
                )

m.optimize()

# Resultados
print("=" * 50)
print("RESULTADO — CVRP (Roteirização com Capacidade)")
print("=" * 50)
print(f"Distância total: {m.ObjVal:.2f} km")
print()

nomes = {0: "Depósito", 1: "Cliente A", 2: "Cliente B",
         3: "Cliente C", 4: "Cliente D", 5: "Cliente E", 6: "Cliente F"}

for k in veiculos:
    # Reconstrói rota do veículo k
    rota = [0]
    atual = 0
    carga = 0
    visitados = set()
    while True:
        proximo = None
        for j in nos:
            if j != atual and j not in visitados and x[atual, j, k].X > 0.5:
                proximo = j
                break
        if proximo is None or proximo == 0:
            rota.append(0)
            break
        rota.append(proximo)
        visitados.add(proximo)
        if proximo in clientes:
            carga += demanda[proximo]
        atual = proximo

    if len(rota) > 2:
        dist_rota = sum(d[rota[i], rota[i+1]] for i in range(len(rota)-1))
        carga_rota = sum(demanda[n] for n in rota if n in clientes)
        print(f"Veículo {k+1} ({carga_rota}/{capacidade} unidades, {dist_rota:.2f} km)")
        rota_str = " → ".join(nomes[n] for n in rota)
        print(f"  {rota_str}")
        print()

print("DEMANDAS ATENDIDAS")
print("-" * 50)
for c in clientes:
    print(f"  {nomes[c]}: {demanda[c]} unidades ✓")
