from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from data import *

model1 = Block()

Y1=1
NI=timelen
NJ=12
model1.I = RangeSet(1,NI)
model1.J = RangeSet(1,NJ)

model1.G = Set(initialize=['AIR','GOX','LOX','GAN','LIN','LAR','SLT','GAR'])
model1.S = Set(initialize=['LOX','LIN','LAR'])
model1.C = Set(initialize=['AIRC','GOXC','MPNC','LPNC'])
model1.GN = Set(initialize=['MPGN','LPGN'])
model1.L = Set(initialize=['LGOX','LGAN'])
model1.V = Set(initialize=['VLOX','VLIN'])

model1.F = Var(model1.G, model1.I, model1.J, within=Reals, bounds=(0,None), initialize=0)
#model1.Y = Var(model1.I, model1.J, within=Binary, bounds=(0,1), initialize=0)
model1.Y_GAR = Var(model1.I, model1.J, within=Binary, bounds=(0,1), initialize=0)
model1.Q = Var(model1.C, model1.I, model1.J, within=Reals, bounds=(0,None), initialize=0)

def _ASU1_1(m, i, j):
    return m.F['AIR',i, j] == 112000 * Y1
model1.ASU1_1 = Constraint(model1.I, model1.J, rule=_ASU1_1)

def _ASU1_2(m, i, j):
    return m.F['GOX',i, j] == 20000 * Y1
model1.ASU1_2 = Constraint(model1.I, model1.J, rule=_ASU1_2)

def _ASU1_3(m, i, j):
    return m.F['GAN',i, j] == 45000 * Y1
model1.ASU1_3 = Constraint(model1.I, model1.J, rule=_ASU1_3)

def _ASU1_4(m, i, j):
    return m.F['LOX',i, j] == 500 * Y1
model1.ASU1_4 = Constraint(model1.I, model1.J, rule=_ASU1_4)

def _ASU1_5(m, i, j):
    return m.F['LIN',i, j] == 0 * Y1
model1.ASU1_5 = Constraint(model1.I, model1.J, rule=_ASU1_5)

#def _ASU1_6(m, i):
#    return m.F['LIN', i] >= 0 * m.Y[i]
#model1.ASU1_6 = Constraint(model1.T, rule=_ASU1_6)

def _ASU1_7(m, i, j):
    return m.F['LAR', i, j] + m.F['GAR', i, j] == 600 * Y1
model1.ASU1_7 = Constraint(model1.I, model1.J, rule=_ASU1_7)

def _ASU1_8(m, i, j):
    return m.Q['AIRC', i, j] == 0.437 * m.F['AIR', i, j]
model1.ASU1_8 = Constraint(model1.I, model1.J, rule=_ASU1_8)

def _ASU1_9(m, i, j):
    return m.Q['GOXC', i, j] == 0.187 * m.F['GOX', i, j]
model1.ASU1_9 = Constraint(model1.I, model1.J, rule=_ASU1_9)

def _ASU1_10(m, i, j):
    return m.F['GAR', i, j] >= 300 * m.Y_GAR[i, j]
model1.ASU1_10 = Constraint(model1.I, model1.J, rule=_ASU1_10)

def _ASU1_11(m, i, j):
    return m.F['GAR', i, j] <= 400 * m.Y_GAR[i, j]
model1.ASU1_11 = Constraint(model1.I, model1.J, rule=_ASU1_11)

def _ASU1_19(m, i, j):
    return m.Y_GAR[i, j] <= Y1
model1.ASU1_19 = Constraint(model1.I, model1.J, rule=_ASU1_19)









