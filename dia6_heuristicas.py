# DIA 6 — Heurísticas + Warm Start + Callback com Gurobi
# Contexto: problema maior de Facility Location onde resolver do zero
# é lento. Usamos uma heurística gulosa para gerar solução inicial
# (warm start) e aceleramos o solver com MIP Gap e Callback.

# CONCEITOS DO DIA
# 1. Heurística Gulosa   — solução inicial rápida (não ótima)
# 2. Warm Start          — passa solução inicial ao Gurobi via .Start
# 3. MIP Gap             — para quando solução está dentro de X% do ótimo
# 4. Time Limit          — para após N segundos independente do gap
# 5. Callback            — monitora progresso em tempo real durante o solving

import gurobipy as gp
from gurobipy import GRB
import random
import time

random.seed(42)

# Problema maior: 8 depósitos candidatos, 12 clientes
n_dep = 8
n_cli = 12
depositos = list(range(n_dep))
clientes  = list(range(n_cli))

custo_fixo = {i: random.randint(800, 2000) for i in depositos}
capacidade = {i: random.randint(300, 600)  for i in depositos}
demanda    = {j: random.randint(50, 120)   for j in clientes}

custo_transp = {
    (i, j): random.randint(2, 15)
    for i in depositos for j in clientes
}

# ─────────────────────────────────────────────
# PARTE 1 — HEURÍSTICA GULOSA
# Abre o depósito mais barato até atender toda demanda
# ─────────────────────────────────────────────
print("=" * 55)
print("PARTE 1 — Heurística Gulosa (solução inicial rápida)")
print("=" * 55)

t0 = time.time()

demanda_restante = dict(demanda)
depositos_abertos = []
alocacao_gulosa = {(i, j): 0 for i in depositos for j in clientes}

# Ordena depósitos por custo fixo crescente
ordem = sorted(depositos, key=lambda i: custo_fixo[i])

cap_restante = dict(capacidade)
for i in ordem:
    if sum(demanda_restante.values()) <= 0:
        break
    depositos_abertos.append(i)
    for j in clientes:
        if demanda_restante[j] > 0 and cap_restante[i] > 0:
            envio = min(demanda_restante[j], cap_restante[i])
            alocacao_gulosa[i, j] = envio
            demanda_restante[j] -= envio
            cap_restante[i] -= envio

custo_guloso = (
    sum(custo_fixo[i] for i in depositos_abertos) +
    sum(custo_transp[i, j] * alocacao_gulosa[i, j]
        for i in depositos for j in clientes)
)

t_guloso = time.time() - t0
print(f"Depósitos abertos: {depositos_abertos}")
print(f"Custo heurístico:  R$ {custo_guloso:,.2f}")
print(f"Tempo:             {t_guloso*1000:.1f} ms")
print()

# ─────────────────────────────────────────────
# PARTE 2 — GUROBI SEM WARM START
# ─────────────────────────────────────────────
def build_model():
    m = gp.Model("facility_avancado")
    m.setParam("OutputFlag", 0)
    y = m.addVars(depositos, vtype=GRB.BINARY, name="abre")
    x = m.addVars(depositos, clientes, lb=0, name="fluxo")
    m.setObjective(
        gp.quicksum(custo_fixo[i] * y[i] for i in depositos) +
        gp.quicksum(custo_transp[i, j] * x[i, j]
                    for i in depositos for j in clientes),
        GRB.MINIMIZE
    )
    for j in clientes:
        m.addConstr(
            gp.quicksum(x[i, j] for i in depositos) == demanda[j]
        )
    for i in depositos:
        m.addConstr(
            gp.quicksum(x[i, j] for j in clientes) <= capacidade[i] * y[i]
        )
    return m, y, x

print("=" * 55)
print("PARTE 2 — Gurobi sem Warm Start")
print("=" * 55)
m1, y1, x1 = build_model()
m1.setParam("MIPGap", 0.01)   # para com gap <= 1%
m1.setParam("TimeLimit", 30)
t0 = time.time()
m1.optimize()
t_sem = time.time() - t0
print(f"Custo ótimo:  R$ {m1.ObjVal:,.2f}")
print(f"MIP Gap:      {m1.MIPGap*100:.2f}%")
print(f"Tempo:        {t_sem:.3f}s")
print(f"Nos B&B:      {int(m1.NodeCount)}")
print()

# ─────────────────────────────────────────────
# PARTE 3 — GUROBI COM WARM START
# ─────────────────────────────────────────────
print("=" * 55)
print("PARTE 3 — Gurobi com Warm Start (solução gulosa)")
print("=" * 55)

m2, y2, x2 = build_model()
m2.setParam("MIPGap", 0.01)
m2.setParam("TimeLimit", 30)

# Injeta solução gulosa como ponto de partida
for i in depositos:
    y2[i].Start = 1 if i in depositos_abertos else 0
for i in depositos:
    for j in clientes:
        x2[i, j].Start = alocacao_gulosa[i, j]

# Callback: imprime cada melhoria encontrada
historico = []
def callback(model, where):
    if where == GRB.Callback.MIPSOL:
        obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
        gap = model.cbGet(GRB.Callback.MIPSOL_OBJBND)
        historico.append((round(time.time() - t0, 3), round(obj, 2)))

t0 = time.time()
m2.optimize(callback)
t_com = time.time() - t0

print(f"Custo ótimo:  R$ {m2.ObjVal:,.2f}")
print(f"MIP Gap:      {m2.MIPGap*100:.2f}%")
print(f"Tempo:        {t_com:.3f}s")
print(f"Nos B&B:      {int(m2.NodeCount)}")
print()

print("Progresso de melhoria (Callback):")
for t, v in historico:
    print(f"  t={t:5.3f}s  →  R$ {v:,.2f}")

# ─────────────────────────────────────────────
# COMPARATIVO FINAL
# ─────────────────────────────────────────────
print()
print("=" * 55)
print("COMPARATIVO FINAL")
print("=" * 55)
print(f"{'Método':<25} {'Custo':>12} {'Tempo':>10} {'Nós B&B':>10}")
print("-" * 55)
print(f"{'Heurística Gulosa':<25} {'R$ '+f'{custo_guloso:,.0f}':>12} {t_guloso*1000:>8.1f}ms {'—':>10}")
print(f"{'Gurobi sem warm start':<25} {'R$ '+f'{m1.ObjVal:,.0f}':>12} {t_sem:>9.3f}s {int(m1.NodeCount):>10}")
print(f"{'Gurobi com warm start':<25} {'R$ '+f'{m2.ObjVal:,.0f}':>12} {t_com:>9.3f}s {int(m2.NodeCount):>10}")
melhoria = (custo_guloso - m2.ObjVal) / custo_guloso * 100
print()
print(f"Melhoria do ótimo sobre a heurística: {melhoria:.1f}%")
