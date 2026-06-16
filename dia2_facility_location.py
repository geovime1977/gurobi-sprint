# DIA 2 — MILP: Facility Location Problem com Gurobi
# Contexto: cliente de varejo precisa decidir quais depósitos abrir
# para atender lojas com custo total mínimo (fixo + transporte).

# PROBLEMA
# 3 depósitos candidatos (D1, D2, D3) e 4 lojas (L1, L2, L3, L4).
# Cada depósito tem custo fixo de abertura e capacidade máxima.
# Cada loja tem demanda conhecida.
# Custo de transporte por unidade entre cada depósito e loja é dado.
# Pergunta: quais depósitos abrir e quanto enviar de cada um para cada loja?

# FORMULAÇÃO MATEMÁTICA
# Índices:
#   i ∈ {0,1,2} — depósitos
#   j ∈ {0,1,2,3} — lojas
#
# Parâmetros:
#   f[i]     = custo fixo de abrir depósito i
#   c[i][j]  = custo de transporte por unidade de i para j
#   cap[i]   = capacidade do depósito i
#   dem[j]   = demanda da loja j
#
# Variáveis de decisão:
#   y[i]    ∈ {0,1}  — 1 se depósito i é aberto
#   x[i][j] ≥ 0      — unidades enviadas de i para j
#
# Função objetivo (minimizar custo total):
#   min  Σ f[i]*y[i] + Σ Σ c[i][j]*x[i][j]
#
# Restrições:
#   Σ_i x[i][j] = dem[j]          para cada loja j  (demanda atendida)
#   Σ_j x[i][j] <= cap[i]*y[i]    para cada depósito i  (capacidade + ligação binária)
#   y[i] ∈ {0,1},  x[i][j] >= 0

import gurobipy as gp
from gurobipy import GRB

# Dados do problema
depositos = [0, 1, 2]
lojas     = [0, 1, 2, 3]

custo_fixo = {0: 1000, 1: 1200, 2: 800}   # R$ para abrir cada depósito
capacidade = {0: 500,  1: 600,  2: 400}    # unidades/mês

demanda = {0: 150, 1: 200, 2: 180, 3: 120}  # demanda de cada loja

# Custo de transporte por unidade [depósito][loja]
custo_transp = {
    (0, 0): 4,  (0, 1): 6,  (0, 2): 9,  (0, 3): 5,
    (1, 0): 7,  (1, 1): 3,  (1, 2): 5,  (1, 3): 8,
    (2, 0): 5,  (2, 1): 8,  (2, 2): 4,  (2, 3): 3,
}

m = gp.Model("facility_location")
m.setParam("OutputFlag", 0)

# Variáveis
y = m.addVars(depositos, vtype=GRB.BINARY, name="abre")
x = m.addVars(depositos, lojas, lb=0, name="fluxo")

# Função objetivo
m.setObjective(
    gp.quicksum(custo_fixo[i] * y[i] for i in depositos) +
    gp.quicksum(custo_transp[i, j] * x[i, j] for i in depositos for j in lojas),
    GRB.MINIMIZE
)

# Restrições de demanda: cada loja deve ser totalmente atendida
for j in lojas:
    m.addConstr(gp.quicksum(x[i, j] for i in depositos) == demanda[j], f"dem_{j}")

# Restrições de capacidade + ligação binária
for i in depositos:
    m.addConstr(
        gp.quicksum(x[i, j] for j in lojas) <= capacidade[i] * y[i],
        f"cap_{i}"
    )

m.optimize()

# Resultados
print("=" * 45)
print("RESULTADO — Facility Location")
print("=" * 45)
print(f"Custo total mínimo: R$ {m.ObjVal:,.2f}")
print()

print("DECISÃO DE ABERTURA")
print("-" * 45)
nomes = {0: "Depósito Norte", 1: "Depósito Centro", 2: "Depósito Sul"}
for i in depositos:
    status = "ABERTO" if y[i].X > 0.5 else "fechado"
    print(f"  {nomes[i]}: {status}  (custo fixo: R$ {custo_fixo[i]:,})")

print()
print("PLANO DE DISTRIBUIÇÃO (unidades)")
print("-" * 45)
for i in depositos:
    if y[i].X > 0.5:
        for j in lojas:
            if x[i, j].X > 0.01:
                print(f"  {nomes[i]} → Loja {j+1}: {x[i,j].X:.0f} un "
                      f"(custo unit: R$ {custo_transp[i,j]})")

print()
custo_fixo_total = sum(custo_fixo[i] * y[i].X for i in depositos)
custo_transp_total = m.ObjVal - custo_fixo_total
print(f"Custo fixo total:       R$ {custo_fixo_total:,.2f}")
print(f"Custo de transporte:    R$ {custo_transp_total:,.2f}")
