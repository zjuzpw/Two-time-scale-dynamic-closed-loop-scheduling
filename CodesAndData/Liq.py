from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from data import *

model5 = Block()
NI=timelen
NJ=12
model5.I = RangeSet(1,NI)
model5.J = RangeSet(1,NJ)
model5.Q = RangeSet(1,2)
model5.L = Set(initialize=['LGOX','LGAN'])
model5.V = Set(initialize=['VLOX','VLIN'])

model5.F_L = Var(model5.L, model5.I, model5.J, within=Reals, bounds=(0,None), initialize=0)
model5.F = Var(model5.L, model5.Q, model5.I, model5.J, within=Reals, bounds=(0,None), initialize=0)
model5.Y = Var(model5.L, model5.Q, model5.I, model5.J, within=Binary, bounds=(0,1), initialize=0)
model5.Z = Var(model5.I, model5.J, within=Binary, bounds=(0,1), initialize=0)
model5.cost = Var(within=Reals, bounds=(0,None), initialize=0)
model5.ToLIQ = Var(model5.I, model5.J, within=Reals, bounds=(0,None), initialize=0)

def _Liq_1(m, q, i, j):
    return m.F['LGOX', q, i, j] == 2400 * m.Y['LGOX', q, i, j]
model5.Liq_1 = Constraint(model5.Q, model5.I, model5.J, rule=_Liq_1)

def _Liq_2(m, q, i, j):
    return m.F['LGAN', q, i, j] == 2200 * m.Y['LGAN', q, i, j]
model5.Liq_2 = Constraint(model5.Q, model5.I, model5.J, rule=_Liq_2)

def _Liq_3(m, q, i, j):
    return sum(m.Y['LGAN', k, i, j] for k in model5.Q) <= 2 * (1 - m.Y['LGOX', q, i, j])
model5.Liq_3 = Constraint(model5.Q, model5.I, model5.J, rule=_Liq_3)

def _Liq_4(m, i, j):
    return m.F_L['LGOX', i, j] == sum(m.F['LGOX', q, i, j] for q in m.Q)
model5.Liq_4 = Constraint(model5.I, model5.J, rule=_Liq_4)

def _Liq_5(m, i, j):
    return m.F_L['LGAN', i, j] == sum(m.F['LGAN', q, i, j] for q in m.Q)
model5.Liq_5 = Constraint(model5.I, model5.J, rule=_Liq_5)

#def _Liq_6(m, j):
#    return m.ToLIQ[j] == 11000 * (sum(m.Y['LGOX', i, j] + m.Y['LGAN', i, j]) for i in m.Q)
#model5.Liq_6 = Constraint(model5.T, rule=_Liq_6)

def _Liq_6(m, i, j):
    return m.ToLIQ[i, j] == 11000 * sum(m.Y['LGOX', q, i, j] for q in m.Q) + 11000 * sum(m.Y['LGAN', q, i, j] for q in m.Q)
model5.Liq_6 = Constraint(model5.I, model5.J, rule=_Liq_6)

def _Liq_7(m, l, q, i):
    return m.Y[l, q, i, 1] == 0
model5.Liq_7 = Constraint(model5.L, model5.Q, model5.I, rule=_Liq_7)

def _pingjun1(m, i, j):
    return m.Y['LGOX', 1, i, j] >= m.Y['LGOX', 2, i, j]
model5.pingjun1 = Constraint(model5.I, model5.J, rule=_pingjun1)

def _pingjun2(m, i, j):
    return m.Y['LGAN', 1, i, j] >= m.Y['LGAN', 2, i, j]
model5.pingjun2 = Constraint(model5.I, model5.J, rule=_pingjun2)


