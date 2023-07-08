from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from data import *

model3 = Block()

Y3=1
dt=0.083
NI=timelen
NJ=12
model3.I = RangeSet(1,NI)
model3.J = RangeSet(1,NJ)
model3.I2 = RangeSet(0,NI)
model3.J2 = RangeSet(0,NJ)
model3.Segment = RangeSet(1,8)

model3.G = Set(initialize=['AIR','GOX','LOX','GAN','LIN','LAR','GAR'])
model3.S = Set(initialize=['LOX','LIN','LAR'])
model3.C = Set(initialize=['AIRC','GOXC','MPNC','LPNC'])
model3.SP = Set(initialize=['GOX', 'LIN'])
# different T-i is different mode
model3.Mode = Set(initialize=['M1','M2','M3','M4','M5','M6','M7','M8'])

model3.y = Var(model3.I2,model3.Mode, within=Binary,bounds=(0,1),initialize=0)
model3.FSP = Var(model3.SP, model3.I2, within=Reals, bounds=(0,None), initialize=0)
model3.deltaFSP = Var(model3.SP, model3.I, within=Reals, initialize=0)
model3.deltaFSP1 = Var(model3.SP, model3.I,model3.Mode, within=Reals, initialize=0)

model3.F = Var(model3.G, model3.I2, model3.J, within=Reals, bounds=(0,None), initialize=0)
model3.deltaF = Var(model3.G, model3.I2, model3.J,model3.Mode, within=Reals, initialize=0)
# model3.y = Var(model3.I, model3.Segment, within=Binary, bounds=(0,1), initialize=0)
model3.Y_GAR = Var(model3.I, model3.J, within=Binary, bounds=(0,1), initialize=0)
model3.Q = Var(model3.C, model3.I, model3.J, within=Reals, bounds=(0,None), initialize=0)
#model3.T = Var(model3.I, within=Reals, bounds=(0,None), initialize=0)
#model3.T = Param(model3.I, initialize=18)
model3.W = Var(model3.G, model3.I, model3.J, model3.Segment, within=Reals, initialize=0)
model3.z = Var(model3.I, model3.J, within=Binary, bounds=(0,1), initialize=0)
model3.Z = Var(model3.Mode,model3.Mode, model3.I2,within=Binary, bounds=(0, 1), initialize=0)


gain1={}
gain1['GOX'] = 1
gain1['AIR'] = 4.384
gain1['LOX'] = 0.0395
gain1['GAN'] = 1.885
gain1['LIN'] = 0
gain1['LAR'] = 0.032

model3.Gain_GOX = Param(model3.G, initialize=gain1)

gain2={}
gain2['GOX'] = 0
gain2['AIR'] = -4.06
gain2['LOX'] = -0.92
gain2['GAN'] = -2.75
gain2['LIN'] = 1
gain2['LAR'] = -0.03

model3.Gain_LIN = Param(model3.G, initialize=gain2)
# init load
init1={}
init1['GOX'] = 20000
init1['AIR'] = 100000
init1['LOX'] = 1600
init1['GAN'] = 40000
init1['LIN'] = 600
init1['LAR'] = 900
model3.Init = Param(model3.G, initialize=init1)

# Time constant
time1={}
for i in range(1, 5):
    time1[i] = 0.3 - 0.075 * (i - 1)
for i in range(5, 9):
    time1[i] = 0.075 * (i - 4)
model3.Time = Param(model3.Segment, initialize=time1)

# init load
def _ASU_ini(m, g):
    if g!='GAR':
        return m.F[g, 1, 1] == m.Init[g] * Y3
    return Constraint.Skip
model3.ASU_ini = Constraint(model3.G, rule=_ASU_ini)

# steady state
def _ASU_ini2(m, g, i, r):
    if g!='GAR':
        return m.deltaF[g, i, 1, r] == 0
    return Constraint.Skip
model3.ASU_ini2 = Constraint(model3.G, model3.I,model3.Mode, rule=_ASU_ini2)

def _ASU_1(m, g, i, j, r):
    if g!='GAR':
        if j != NJ:
            if r == 'M1':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M1'] * (dt + 0.3) == (0.3) * m.deltaF[g,i,j,'M1'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M1'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M1']
                return m.deltaF[g,i,j+1,'M1'] * (dt + 0.3) == (0.3) * m.deltaF[g,i,j,'M1']
            if r == 'M2':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M2'] * (dt + 0.225) == (0.225) * m.deltaF[g,i,j,'M2'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M2'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M2']
                return m.deltaF[g,i,j+1,'M2'] * (dt + 0.225) == (0.225) * m.deltaF[g,i,j,'M2']
            if r == 'M3':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M3'] * (dt + 0.15) == (0.15) * m.deltaF[g,i,j,'M3'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M3'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M3']
                return m.deltaF[g,i,j+1,'M3'] * (dt + 0.15) == (0.15) * m.deltaF[g,i,j,'M3']
            if r == 'M4':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M4'] * (dt + 0.075) == (0.075) * m.deltaF[g,i,j,'M4'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M4'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M4']
                return m.deltaF[g,i,j+1,'M4'] * (dt + 0.075) == (0.075) * m.deltaF[g,i,j,'M4']
            if r == 'M8':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M8'] * (dt + 0.3) == (0.3) * m.deltaF[g,i,j,'M8'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M8'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M8']
                return m.deltaF[g,i,j+1,'M8'] * (dt + 0.3) == (0.3) * m.deltaF[g,i,j,'M8']
            if r == 'M7':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M7'] * (dt + 0.225) == (0.225) * m.deltaF[g,i,j,'M7'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M7'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M7']
                return m.deltaF[g,i,j+1,'M7'] * (dt + 0.225) == (0.225) * m.deltaF[g,i,j,'M7']
            if r == 'M6':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M6'] * (dt + 0.15) == (0.15) * m.deltaF[g,i,j,'M6'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M6'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M6']
                return m.deltaF[g,i,j+1,'M6'] * (dt + 0.15) == (0.15) * m.deltaF[g,i,j,'M6']
            if r == 'M5':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M5'] * (dt + 0.075) == (0.075) * m.deltaF[g,i,j,'M5'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M5'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M5']
                return m.deltaF[g,i,j+1,'M5'] * (dt + 0.075) == (0.075) * m.deltaF[g,i,j,'M5']
    return Constraint.Skip
model3.ASU_1 = Constraint(model3.G, model3.I, model3.J, model3.Mode, rule=_ASU_1)

def _ASU_2(m, g, i):
    return m.deltaFSP[g, i] == m.FSP[g, i] - m.F[g, i-1, NJ]
model3.ASU_2 = Constraint(model3.SP, model3.I, rule=_ASU_2)

def _ASU_2_1(m, g, i):
    return m.deltaFSP[g, i] == m.deltaFSP1[g, i, 'M1'] + m.deltaFSP1[g, i, 'M2'] + m.deltaFSP1[g, i, 'M3'] + m.deltaFSP1[g, i, 'M4'] + m.deltaFSP1[g, i, 'M5'] + m.deltaFSP1[g, i, 'M6']+ m.deltaFSP1[g, i, 'M7'] + + m.deltaFSP1[g, i, 'M8']
model3.ASU_2_1 = Constraint(model3.SP, model3.I, rule=_ASU_2_1)

def _ASU_3(m, g, i, j):
    if j!=NJ:
        if j == 1:
            if g != 'GAR':
                return m.F[g, i, j + 1] == m.F[g, i, j] + m.deltaF[g, i, j + 1, 'M1'] + m.deltaF[g, i, j + 1, 'M2'] + \
                       m.deltaF[g, i, j + 1, 'M3'] + m.deltaF[g, i, j + 1, 'M4'] + m.deltaF[g, i, j + 1, 'M5'] + \
                       m.deltaF[g, i, j + 1, 'M6'] + m.deltaF[g, i, j + 1, 'M7'] + + m.deltaF[g, i, j + 1, 'M8']
            return m.F[g, i, j+1] == m.F[g, i, j] + m.deltaF[g, i, j+1,'M1'] + m.deltaF[g, i, j+1,'M2'] + m.deltaF[g, i, j+1,'M3'] + m.deltaF[g, i, j+1,'M4'] + m.deltaF[g, i, j+1,'M5'] + m.deltaF[g, i, j+1,'M6'] + m.deltaF[g, i, j+1,'M7'] + + m.deltaF[g, i, j+1,'M8']
        return m.F[g, i, j+1] == m.F[g, i, j] + m.deltaF[g, i, j+1,'M1'] + m.deltaF[g, i, j+1,'M2'] + m.deltaF[g, i, j+1,'M3'] + m.deltaF[g, i, j+1,'M4'] + m.deltaF[g, i, j+1,'M5'] + m.deltaF[g, i, j+1,'M6'] + m.deltaF[g, i, j+1,'M7'] + + m.deltaF[g, i, j+1,'M8']
    return Constraint.Skip
model3.ASU_3 = Constraint(model3.G, model3.I, model3.J, rule=_ASU_3)

def _ASU_32(m,g,i,j,r):
    return m.deltaF[g,i,j,r] >= -40000 * m.y[i,r]
model3.ASU_32 = Constraint(model3.G,model3.I,model3.J,model3.Mode, rule=_ASU_32)

def _ASU_33(m,g,i,j,r):
    return m.deltaF[g,i,j,r] <= 40000 * m.y[i,r]
model3.ASU_33 = Constraint(model3.G,model3.I,model3.J,model3.Mode, rule=_ASU_33)

def _ASU_32_1(m,g,i,r):
    return m.deltaFSP1[g,i,r] >= -20000 * m.y[i,r]
model3.ASU_32_1 = Constraint(model3.SP,model3.I,model3.Mode, rule=_ASU_32_1)

def _ASU_33_1(m,g,i,r):
    return m.deltaFSP1[g,i,r] <= 20000 * m.y[i,r]
model3.ASU_33_1 = Constraint(model3.SP,model3.I,model3.Mode, rule=_ASU_33_1)


def _ASU_34(m,i):
    return m.y[i,'M1'] + m.y[i,'M2'] + m.y[i,'M3'] + m.y[i,'M4'] + m.y[i,'M5'] + m.y[i,'M6'] + m.y[i,'M7'] + m.y[i,'M8'] == 1
model3.ASU_34 = Constraint(model3.I,rule=_ASU_34)

leftEnd1={}
for i in range(1, 9):
    leftEnd1[i] = -8000 + 2000 * (i - 1)
model3.LeftEnd = Param(model3.Segment, initialize=leftEnd1)

rightEnd1={}
for i in range(1, 9):
    rightEnd1[i] = -6000 + 2000 * (i - 1)
model3.RightEnd = Param(model3.Segment, initialize=rightEnd1)

def _ASU_16(m, i):
    return m.deltaFSP['GOX', i] >= m.LeftEnd[1] * m.y[i, 'M1'] + m.LeftEnd[2] * m.y[i, 'M2'] + m.LeftEnd[3] * m.y[i, 'M3'] + m.LeftEnd[4] * m.y[i, 'M4'] + m.LeftEnd[5] * m.y[i, 'M5'] + m.LeftEnd[6] * m.y[i, 'M6'] + m.LeftEnd[7] * m.y[i, 'M7'] + m.LeftEnd[8] * m.y[i, 'M8'] + 1e-10
model3.ASU_16 = Constraint(model3.I, rule=_ASU_16)

def _ASU_17(m, i):
     return m.deltaFSP['GOX', i] <= m.RightEnd[1] * m.y[i, 'M1'] + m.RightEnd[2] * m.y[i, 'M2'] + m.RightEnd[3] * m.y[i, 'M3'] + m.RightEnd[4] * m.y[i, 'M4'] + m.RightEnd[5] * m.y[i, 'M5'] + m.RightEnd[6] * m.y[i, 'M6'] + m.RightEnd[7] * m.y[i, 'M7'] + m.RightEnd[8] * m.y[i, 'M8']
model3.ASU_17 = Constraint(model3.I, rule=_ASU_17)

def _ASU_4(m, g, i):
    return m.F[g, i, 1] == m.F[g, i-1, NJ]
model3.ASU_4 = Constraint(model3.G, model3.I, rule=_ASU_4)

def _FSPinitial1(m, i):
    return m.FSP['GOX', 0] == 20000 * Y3
model3.FSPinitial1 = Constraint(model3.I, rule=_FSPinitial1)

def _FSPinitial2(m, i):
    return m.FSP['LIN', 0] == 0 * Y3
model3.FSPinitial2 = Constraint(model3.I, rule=_FSPinitial2)

model3.y_lin = Var(model3.I, model3.J, within=Binary, bounds=(0,1), initialize=0)
def _firstStageMode2_8(m, i, j):
    return m.F['GOX', i, j] <= 20000 * (1-m.y_lin[i, j]) + 24000 * m.y_lin[i, j]
model3.firstStageMode2_8 = Constraint(model3.I, model3.J, rule=_firstStageMode2_8)

def _firstStageMode2_9(m, i, j):
    return m.F['GOX', i, j] >= 20000 * m.y_lin[i, j] + 1e-10
model3.firstStageMode2_9 = Constraint(model3.I, model3.J, rule=_firstStageMode2_9)

def _firstStageMode2_10(m, i, j):
    return m.F['LIN', i, j] <= 2400 * m.y_lin[i, j]
model3.firstStageMode2_10 = Constraint(model3.I, model3.J, rule=_firstStageMode2_10)

def _firstStageMode2_11(m, i, j):
    return m.y_lin[i, j] <= Y3
model3.firstStageMode2_11 = Constraint(model3.I, model3.J, rule=_firstStageMode2_11)

F_UB1={}
F_UB1['AIR'] = 120000
F_UB1['GOX'] = 24000
F_UB1['LOX'] = 2500
F_UB1['GAN'] = 50000
F_UB1['LIN'] = 2500
F_UB1['LAR'] = 1100
model3.F_UB = Param(model3.G, initialize=F_UB1)

F_LB1={}
F_LB1['AIR'] = 80000
F_LB1['GOX'] = 16000
F_LB1['LOX'] = 0
F_LB1['GAN'] = 30000
F_LB1['LIN'] = 0
F_LB1['LAR'] = 700
model3.F_LB = Param(model3.G, initialize=F_LB1)

def _ASU_5(m, g, i, j):
    if g!='GAR':
        return m.F[g, i, j]  >= m.F_LB[g] * Y3
    return Constraint.Skip
model3.ASU_5 = Constraint(model3.G, model3.I, model3.J, rule=_ASU_5)

def _ASU_6(m, g, i, j):
    if g!='GAR':
        return m.F[g, i, j] <= m.F_UB[g] * Y3
    return Constraint.Skip
model3.ASU_6 = Constraint(model3.G, model3.I, model3.J, rule=_ASU_6)

def _ASU_7(m, i, j):
    return m.Q['AIRC', i, j] == 0.455 * m.F['AIR', i, j]
model3.ASU_7 = Constraint(model3.I, model3.J, rule=_ASU_7)

def _ASU_8(m, i, j):
    return m.F['GAR', i, j] >= 500 * m.Y_GAR[i, j]
model3.ASU_8 = Constraint(model3.I, model3.J, rule=_ASU_8)

def _ASU_9(m, i, j):
    return m.F['GAR', i, j] <= 900 * m.Y_GAR[i, j]
model3.ASU_9 = Constraint(model3.I, model3.J, rule=_ASU_9)

def _ASU_10(m, i, j):
    return m.Y_GAR[i, j] <= Y3
model3.ASU_10 = Constraint(model3.I, model3.J, rule=_ASU_10)

def _ASU_11(m, i):
    return m.FSP['GOX', i] >= 16000 * Y3
model3.ASU_11 = Constraint(model3.I, rule=_ASU_11)

def _ASU_12(m, i):
    return m.FSP['GOX', i] <= 24000 * Y3
model3.ASU_12 = Constraint(model3.I, rule=_ASU_12)


def _ASU_13(m, i):
    return m.FSP['LIN', i] >= 0 * Y3
model3.ASU_13 = Constraint(model3.I, rule=_ASU_13)

def _ASU_14(m, i):
    return m.FSP['LIN', i] <= 2400 * Y3
model3.ASU_14 = Constraint(model3.I, rule=_ASU_14)

def _ASU_30(m, i, j):
    return m.Q['GOXC', i, j] == 0.120 * m.F['GOX', i, j]
model3.ASU_30 = Constraint(model3.I, model3.J, rule=_ASU_30)

#switch
def _Switch1(m, i, r):
    return sum(m.Z[s, r, i]for s in m.Mode) - sum(m.Z[r, k, i]for k in m.Mode) == m.y[i,r] - m.y[i-1,r]
model3.Switch1 = Constraint(model3.I, model3.Mode, rule= _Switch1)

# init
def _init1(m):
    return m.y[0,'M1'] == 0
model3.init1 = Constraint(rule=_init1)

def _init2(m):
    return m.y[0,'M2'] == 0
model3.init2 = Constraint(rule=_init2)

def _init3(m):
    return m.y[0,'M3'] == 0
model3.init3 = Constraint(rule=_init3)

def _init4(m):
    return m.y[0,'M4'] == 0
model3.init4 = Constraint(rule=_init4)

def _init5(m):
    return m.y[0,'M5'] == 1
model3.init5 = Constraint(rule=_init5)

def _init6(m):
    return m.y[0,'M6'] == 0
model3.init6 = Constraint(rule=_init6)

def _init7(m):
    return m.y[0,'M7'] == 0
model3.init7 = Constraint(rule=_init7)

def _init8(m):
    return m.y[0,'M8'] == 0
model3.init8 = Constraint(rule=_init8)

