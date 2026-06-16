# DIA 4 — Assignment Problem com Gurobi
# Contexto: consultoria precisa alocar 5 consultores para 5 projetos de clientes.
# Cada consultor tem um custo (ou tempo estimado) diferente para cada projeto.
# Regra: cada consultor em exatamente 1 projeto, cada projeto com exatamente 1 consultor.
# Objetivo: minimizar custo total de alocação.

# FORMULAÇÃO MATEMÁTICA
# Índices:
#   i ∈ {0..4} — consultores
#   j ∈ {0..4} — projetos
#
# Parâmetros:
#   c[i][j] = custo de alocar consultor i ao projeto j (dias de trabalho estimados)
#
# Variáveis:
#   x[i][j] ∈ {0,1} — 1 se consultor i é alocado ao projeto j
#
# Função objetivo:
#   min  Σ Σ c[i][j] * x[i][j]
#
# Restrições:
#   Σ_j x[i][j] == 1   para cada consultor i  (cada consultor em 1 projeto)
#   Σ_i x[i][j] == 1   para cada projeto j    (cada projeto com 1 consultor)
#   x[i][j] ∈ {0,1}

import gurobipy as gp
from gurobipy import GRB

consultores = list(range(5))
projetos    = list(range(5))

nomes_c = {0: "Ana",    1: "Bruno", 2: "Carla", 3: "Diego", 4: "Elena"}
nomes_p = {0: "Supply Chain", 1: "Finance", 2: "HR Tech",
           3: "Manufatura",   4: "Logística"}

# Custo em dias de trabalho para cada par consultor-projeto
# (habilidade de cada consultor em cada domínio)
custo = {
    (0, 0): 8,  (0, 1): 12, (0, 2): 15, (0, 3): 9,  (0, 4): 11,
    (1, 0): 10, (1, 1): 7,  (1, 2): 13, (1, 3): 14, (1, 4): 9,
    (2, 0): 14, (2, 1): 11, (2, 2): 6,  (2, 3): 10, (2, 4): 12,
    (3, 0): 9,  (3, 1): 13, (3, 2): 12, (3, 3): 7,  (3, 4): 8,
    (4, 0): 13, (4, 1): 10, (4, 2): 9,  (4, 3): 11, (4, 4): 6,
}

m = gp.Model("assignment")
m.setParam("OutputFlag", 0)

x = m.addVars(consultores, projetos, vtype=GRB.BINARY, name="aloca")

m.setObjective(
    gp.quicksum(custo[i, j] * x[i, j] for i in consultores for j in projetos),
    GRB.MINIMIZE
)

# Cada consultor em exatamente 1 projeto
for i in consultores:
    m.addConstr(gp.quicksum(x[i, j] for j in projetos) == 1, f"cons_{i}")

# Cada projeto com exatamente 1 consultor
for j in projetos:
    m.addConstr(gp.quicksum(x[i, j] for i in consultores) == 1, f"proj_{j}")

m.optimize()

# Resultados
print("=" * 50)
print("RESULTADO — Alocação Ótima de Consultores")
print("=" * 50)
print(f"Total de dias de trabalho: {m.ObjVal:.0f} dias")
print()

print("ALOCAÇÃO ÓTIMA")
print("-" * 50)
for i in consultores:
    for j in projetos:
        if x[i, j].X > 0.5:
            economia = min(custo[i, k] for k in projetos) - custo[i, j]
            print(f"  {nomes_c[i]:6} → {nomes_p[j]:15} ({custo[i,j]} dias)")

print()
print("COMPARATIVO: ótimo vs pior alocação possível")
print("-" * 50)
pior = sum(max(custo[i, j] for j in projetos) for i in consultores)
print(f"  Alocação ótima:  {m.ObjVal:.0f} dias")
print(f"  Pior alocação:   {pior} dias")
print(f"  Economia:        {pior - m.ObjVal:.0f} dias ({(pior-m.ObjVal)/pior*100:.1f}%)")

print()
print("MATRIZ DE CUSTO (dias) — ótimo marcado com *")
print("-" * 50)
header = f"{'':8}" + "".join(f"{nomes_p[j][:10]:>12}" for j in projetos)
print(header)
for i in consultores:
    row = f"{nomes_c[i]:8}"
    for j in projetos:
        val = f"{custo[i,j]}*" if x[i,j].X > 0.5 else str(custo[i,j])
        row += f"{val:>12}"
    print(row)
