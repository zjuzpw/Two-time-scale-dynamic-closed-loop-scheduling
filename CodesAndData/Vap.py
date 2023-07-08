from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from data import *

model6 = Block()
NI=timelen
NJ=12
model6.I = RangeSet(1,NI)
model6.J = RangeSet(1,NJ)
model6.Q = RangeSet(1,3)
model6.L = Set(initialize=['LGOX','LGAN'])
model6.V = Set(initialize=['VLOX','VLIN'])

model6.F_V = Var(model6.V, model6.I, model6.J, within=Reals, bounds=(0,None), initialize=0)
model6.F = Var(model6.V, model6.Q, model6.I, model6.J, within=Reals, bounds=(0,None), initialize=0)
model6.Y = Var(model6.V, model6.Q, model6.I, model6.J, within=Binary, bounds=(0,1), initialize=0)
model6.Z = Var(model6.I, model6.J, within=Binary, bounds=(0,1), initialize=0)

model6.cost = Var(within=Reals, bounds=(0,None), initialize=0)

def _Vap_1(m, i, j):
    return m.F['VLOX', 1 , i, j] == 30000 * m.Y['VLOX', 1 , i, j]
model6.Vap_1 = Constraint(model6.I, model6.J, rule=_Vap_1)

def _Vap_2(m, i, j):
    return m.F['VLOX', 2, i, j] == 20000 * m.Y['VLOX', 2, i, j]
model6.Vap_2 = Constraint(model6.I, model6.J, rule=_Vap_2)

def _Vap_3(m, i, j):
    return m.F['VLOX', 3, i, j] == 20000 * m.Y['VLOX', 3, i, j]
model6.Vap_3 = Constraint(model6.I, model6.J, rule=_Vap_3)

def _Vap_4(m, i, j):
    return m.F['VLIN', 1, i, j] == 30000 * m.Y['VLIN', 1, i, j]
model6.Vap_4 = Constraint(model6.I, model6.J, rule=_Vap_4)

def _Vap_5(m, i, j):
    return m.F['VLIN', 2, i, j] == 20000 * m.Y['VLIN', 2, i, j]
model6.Vap_5 = Constraint(model6.I, model6.J, rule=_Vap_5)

def _Vap_6(m, i, j):
    return m.F['VLIN', 3, i, j] == 0
model6.Vap_6 = Constraint(model6.I, model6.J, rule=_Vap_6)

def _Vap_7(m, i, j):
    return m.F_V['VLOX', i, j] == sum(m.F['VLOX', q, i, j] for q in model6.Q)
model6.Vap_7 = Constraint(model6.I, model6.J, rule=_Vap_7)

def _Vap_8(m, i, j):
    return m.F_V['VLIN', i, j] == sum(m.F['VLIN', q, i, j] for q in model6.Q)
model6.Vap_8 = Constraint(model6.I, model6.J, rule=_Vap_8)

def _Vap_9(m, i, j):
    return m.Y['VLIN', 3, i, j] == 0
model6.Vap_9 = Constraint(model6.I, model6.J, rule=_Vap_9)
