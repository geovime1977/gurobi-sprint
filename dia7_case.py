# DIA 7 — Case Completo para Entrevista Accenture
# ─────────────────────────────────────────────────────────────────
# PROBLEMA DE NEGÓCIO
# Cliente: BRAlimentos S.A. — rede de distribuição de alimentos no Brasil
# Desafio: a empresa opera 6 centros de distribuição (CDs) legados com
#          custos altos. Precisa decidir quais manter, quais fechar e
#          como redesenhar os fluxos para 10 regiões de varejo.
# Meta: reduzir custo total de distribuição em pelo menos 20%.
#
# ENTREGÁVEIS (formato Accenture):
#   1. Decisão ótima de quais CDs manter/fechar
#   2. Plano de fluxo (quem abastece quem)
#   3. Economia gerada vs situação atual
#   4. ROI do projeto de redesenho
#   5. Análise de sensibilidade (e se a demanda crescer 20%?)
# ─────────────────────────────────────────────────────────────────

import gurobipy as gp
from gurobipy import GRB

# ── DADOS ──────────────────────────────────────────────────────
cds     = list(range(6))
regioes = list(range(10))

nomes_cd = {
    0: "CD São Paulo",   1: "CD Rio de Janeiro", 2: "CD Belo Horizonte",
    3: "CD Curitiba",    4: "CD Salvador",        5: "CD Recife"
}
nomes_reg = {
    0: "SP Interior",  1: "RJ Norte",    2: "MG Sul",     3: "PR Costa",
    4: "BA Centro",    5: "PE Agreste",  6: "SP Capital",  7: "RJ Sul",
    8: "MG Triângulo", 9: "SC Norte"
}

# Custo fixo mensal de operação de cada CD (R$ mil)
custo_fixo = {0: 180, 1: 150, 2: 120, 3: 110, 4: 130, 5: 100}

# Capacidade mensal de cada CD (toneladas)
capacidade = {0: 800, 1: 700, 2: 600, 3: 500, 4: 550, 5: 450}

# Demanda mensal de cada região (toneladas)
demanda = {0: 200, 1: 150, 2: 180, 3: 130, 4: 160,
           5: 120, 6: 250, 7: 140, 8: 170, 9: 110}

# Custo de transporte por tonelada (R$/t) — CD para região
custo_t = {
    (0,0):8,  (0,1):12, (0,2):10, (0,3):9,  (0,4):18, (0,5):22, (0,6):5,  (0,7):14, (0,8):11, (0,9):13,
    (1,0):14, (1,1):6,  (1,2):11, (1,3):13, (1,4):16, (1,5):20, (1,6):12, (1,7):5,  (1,8):13, (1,9):16,
    (2,0):10, (2,1):11, (2,2):5,  (2,3):12, (2,4):14, (2,5):18, (2,6):11, (2,7):13, (2,8):6,  (2,9):14,
    (3,0):9,  (3,1):13, (3,2):12, (3,3):5,  (3,4):19, (3,5):23, (3,6):10, (3,7):15, (3,8):13, (3,9):7,
    (4,0):18, (4,1):16, (4,2):14, (4,3):19, (4,4):5,  (4,5):8,  (4,6):17, (4,7):17, (4,8):15, (4,9):21,
    (5,0):22, (5,1):20, (5,2):18, (5,3):23, (5,4):8,  (5,5):5,  (5,6):21, (5,7):21, (5,8):19, (5,9):25,
}

# Custo atual (situação AS-IS): todos os 6 CDs abertos, fluxo não otimizado
# Estimativa: cada região abastecida pelo CD mais próximo, sem otimização
custo_asis = sum(custo_fixo.values()) * 1000  # custo fixo total
# Fluxo atual: distribuição proporcional não otimizada (aprox. +35% no transporte)
custo_transp_asis = sum(
    min(custo_t[i, j] for i in cds) * demanda[j] * 1.35
    for j in regioes
)
custo_total_asis = custo_asis + custo_transp_asis

# ── MODELO ─────────────────────────────────────────────────────
def solve(demanda_override=None, label=""):
    dem = demanda_override or demanda
    m = gp.Model(f"bralimentos_{label}")
    m.setParam("OutputFlag", 0)
    m.setParam("MIPGap", 0.005)

    y = m.addVars(cds, vtype=GRB.BINARY, name="abre")
    x = m.addVars(cds, regioes, lb=0, name="fluxo")

    m.setObjective(
        gp.quicksum(custo_fixo[i] * 1000 * y[i] for i in cds) +
        gp.quicksum(custo_t[i, j] * x[i, j] for i in cds for j in regioes),
        GRB.MINIMIZE
    )

    for j in regioes:
        m.addConstr(gp.quicksum(x[i, j] for i in cds) == dem[j])

    for i in cds:
        m.addConstr(gp.quicksum(x[i, j] for j in regioes) <= capacidade[i] * y[i])

    m.optimize()
    return m, y, x

# ── CENÁRIO BASE ───────────────────────────────────────────────
m_base, y_base, x_base = solve(label="base")

# ── CENÁRIO +20% DEMANDA ───────────────────────────────────────
demanda_crescimento = {j: int(demanda[j] * 1.20) for j in regioes}
m_cresc, y_cresc, x_cresc = solve(demanda_crescimento, label="crescimento")

# ── OUTPUT EXECUTIVO ────────────────────────────────────────────
sep = "=" * 60

print(sep)
print("  BRALIMENTOS S.A. — REDESENHO DA REDE DE DISTRIBUIÇÃO")
print("  Análise de Otimização | Accenture Supply Chain")
print(sep)

print("\n1. SITUAÇÃO ATUAL (AS-IS)")
print("-" * 60)
print(f"   CDs operando:          6 de 6")
print(f"   Custo fixo mensal:     R$ {custo_asis/1000:,.0f} mil")
print(f"   Custo transporte:      R$ {custo_transp_asis/1000:,.0f} mil")
print(f"   CUSTO TOTAL MENSAL:    R$ {custo_total_asis/1000:,.0f} mil")

print("\n2. SOLUÇÃO ÓTIMA (TO-BE)")
print("-" * 60)
abertos = [i for i in cds if y_base[i].X > 0.5]
fechados = [i for i in cds if y_base[i].X < 0.5]
print(f"   CDs mantidos ({len(abertos)}):")
for i in abertos:
    uso = sum(x_base[i, j].X for j in regioes)
    print(f"     ✓ {nomes_cd[i]:<22} {uso:.0f}/{capacidade[i]}t ({uso/capacidade[i]*100:.0f}%)")
print(f"   CDs fechados ({len(fechados)}):")
for i in fechados:
    print(f"     ✗ {nomes_cd[i]}")

cf_otimo = sum(custo_fixo[i] * 1000 for i in abertos)
ct_otimo = sum(custo_t[i,j] * x_base[i,j].X for i in cds for j in regioes)
custo_total_otimo = cf_otimo + ct_otimo

print(f"\n   Custo fixo mensal:     R$ {cf_otimo/1000:,.0f} mil")
print(f"   Custo transporte:      R$ {ct_otimo/1000:,.0f} mil")
print(f"   CUSTO TOTAL MENSAL:    R$ {custo_total_otimo/1000:,.0f} mil")

print("\n3. PLANO DE FLUXO ÓTIMO")
print("-" * 60)
for i in abertos:
    print(f"\n   {nomes_cd[i]}:")
    for j in regioes:
        if x_base[i, j].X > 0.1:
            print(f"     → {nomes_reg[j]:<16} {x_base[i,j].X:>5.0f}t  "
                  f"@ R${custo_t[i,j]}/t")

print("\n4. IMPACTO FINANCEIRO")
print("-" * 60)
economia_mensal = custo_total_asis - custo_total_otimo
economia_anual  = economia_mensal * 12
reducao_pct     = economia_mensal / custo_total_asis * 100
custo_projeto   = 800_000   # estimativa custo de implementação

print(f"   Economia mensal:       R$ {economia_mensal/1000:,.0f} mil")
print(f"   Economia anual:        R$ {economia_anual/1000:,.0f} mil")
print(f"   Redução percentual:    {reducao_pct:.1f}%")
print(f"   Custo do projeto:      R$ {custo_projeto/1000:,.0f} mil")
print(f"   Payback:               {custo_projeto/economia_mensal:.1f} meses")
print(f"   ROI 12 meses:          {(economia_anual-custo_projeto)/custo_projeto*100:.0f}%")

print("\n5. ANÁLISE DE SENSIBILIDADE — Demanda +20%")
print("-" * 60)
abertos_c = [i for i in cds if y_cresc[i].X > 0.5]
ct_cresc   = sum(custo_t[i,j] * x_cresc[i,j].X for i in cds for j in regioes)
cf_cresc   = sum(custo_fixo[i] * 1000 for i in abertos_c)
custo_cresc = cf_cresc + ct_cresc

print(f"   CDs necessários:       {len(abertos_c)} ({[nomes_cd[i] for i in abertos_c]})")
print(f"   Custo total:           R$ {custo_cresc/1000:,.0f} mil/mês")
delta = custo_cresc - custo_total_otimo
print(f"   Impacto vs base:       +R$ {delta/1000:,.0f} mil/mês (+{delta/custo_total_otimo*100:.1f}%)")
print(f"   Conclusão: rede suporta crescimento {'sem abrir novos CDs' if len(abertos_c)==len(abertos) else 'abrindo '+str(len(abertos_c)-len(abertos))+' CD(s) adicional(is)'}")

print(f"\n{sep}")
print("  RECOMENDAÇÃO EXECUTIVA")
print(sep)
print(f"""
  Fechar {len(fechados)} CDs e otimizar fluxos gera economia de {reducao_pct:.0f}% no custo
  de distribuição — R$ {economia_anual/1e6:.1f}M ao ano. Payback do projeto em
  {custo_projeto/economia_mensal:.0f} meses com ROI de {(economia_anual-custo_projeto)/custo_projeto*100:.0f}% no primeiro ano.

  A rede redesenhada suporta crescimento de 20% na demanda
  {'sem necessidade de novos investimentos em infraestrutura.' if len(abertos_c)==len(abertos) else f'com abertura de {len(abertos_c)-len(abertos)} CD adicional.'}
""")
