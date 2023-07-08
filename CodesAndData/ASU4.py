from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from data import *

model4 = Block()

Y3=1
dt=0.083
NI=timelen
NJ=12
model4.I = RangeSet(1,NI)
model4.J = RangeSet(1,NJ)
model4.I2 = RangeSet(0,NI)
model4.J2 = RangeSet(0,NJ)
model4.Segment = RangeSet(1,8)

model4.G = Set(initialize=['AIR','GOX','LOX','GAN','LIN','LAR','GAR'])
model4.S = Set(initialize=['LOX','LIN','LAR'])
model4.C = Set(initialize=['AIRC','GOXC','MPNC','LPNC'])
model4.SP = Set(initialize=['GOX', 'LIN'])
# different T-i is different mode
model4.Mode = Set(initialize=['M1','M2','M3','M4','M5','M6','M7','M8'])

model4.y = Var(model4.I2,model4.Mode, within=Binary,bounds=(0,1),initialize=0)
model4.FSP = Var(model4.SP, model4.I2, within=Reals, bounds=(0,None), initialize=0)
model4.deltaFSP = Var(model4.SP, model4.I, within=Reals, initialize=0)
model4.deltaFSP1 = Var(model4.SP, model4.I,model4.Mode, within=Reals, initialize=0)

model4.F = Var(model4.G, model4.I2, model4.J, within=Reals, bounds=(0,None), initialize=0)
model4.deltaF = Var(model4.G, model4.I2, model4.J,model4.Mode, within=Reals, initialize=0)
# model4.y = Var(model4.I, model4.Segment, within=Binary, bounds=(0,1), initialize=0)
model4.Y_GAR = Var(model4.I, model4.J, within=Binary, bounds=(0,1), initialize=0)
model4.Q = Var(model4.C, model4.I, model4.J, within=Reals, bounds=(0,None), initialize=0)
#model4.T = Var(model4.I, within=Reals, bounds=(0,None), initialize=0)
#model4.T = Param(model4.I, initialize=18)
model4.W = Var(model4.G, model4.I, model4.J, model4.Segment, within=Reals, initialize=0)
model4.z = Var(model4.I, model4.J, within=Binary, bounds=(0,1), initialize=0)
model4.Z = Var(model4.Mode,model4.Mode, model4.I2,within=Binary, bounds=(0, 1), initialize=0)


gain3={}
gain3['GOX'] = 1
gain3['AIR'] = 4.22
gain3['LOX'] = 0.0266
gain3['GAN'] = 2.532
gain3['LIN'] = 0
gain3['LAR'] = 0.04

model4.Gain_GOX = Param(model4.G, initialize=gain3)

gain4={}
gain4['GOX'] = 0
gain4['AIR'] = -3.9
gain4['LOX'] = -1.09
gain4['GAN'] = -2.34
gain4['LIN'] = 1
gain4['LAR'] = -0.5

model4.Gain_LIN = Param(model4.G, initialize=gain4)
# init load
init2={}
init2['GOX'] = 30000
init2['AIR'] = 150000
init2['LOX'] = 1300
init2['GAN'] = 90000
init2['LIN'] = 200
init2['LAR'] = 1700
model4.Init = Param(model4.G, initialize=init2)

# Time constant
time1={}
for i in range(1, 5):
    time1[i] = 0.125 - 0.03 * (i - 1)
for i in range(5, 9):
    time1[i] = 0.03 * (i - 4)
model4.Time = Param(model4.Segment, initialize=time1)

# init load
def _ASU_ini(m, g):
    if g!='GAR':
        return m.F[g, 1, 1] == m.Init[g] * Y3
    return Constraint.Skip
model4.ASU_ini = Constraint(model4.G, rule=_ASU_ini)

# steady state
def _ASU_ini2(m, g, i, r):
    if g!='GAR':
        return m.deltaF[g, i, 1, r] == 0
    return Constraint.Skip
model4.ASU_ini2 = Constraint(model4.G, model4.I,model4.Mode, rule=_ASU_ini2)

def _ASU_1(m, g, i, j, r):
    if g!='GAR':
        if j != NJ:
            if r == 'M1':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M1'] * (dt + 0.125) == (0.125) * m.deltaF[g,i,j,'M1'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M1'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M1']
                return m.deltaF[g,i,j+1,'M1'] * (dt + 0.125) == (0.125) * m.deltaF[g,i,j,'M1']
            if r == 'M2':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M2'] * (dt + 0.095) == (0.095) * m.deltaF[g,i,j,'M2'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M2'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M2']
                return m.deltaF[g,i,j+1,'M2'] * (dt + 0.095) == (0.095) * m.deltaF[g,i,j,'M2']
            if r == 'M3':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M3'] * (dt + 0.065) == (0.065) * m.deltaF[g,i,j,'M3'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M3'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M3']
                return m.deltaF[g,i,j+1,'M3'] * (dt + 0.065) == (0.065) * m.deltaF[g,i,j,'M3']
            if r == 'M4':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M4'] * (dt + 0.035) == (0.035) * m.deltaF[g,i,j,'M4'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M4'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M4']
                return m.deltaF[g,i,j+1,'M4'] * (dt + 0.035) == (0.035) * m.deltaF[g,i,j,'M4']
            if r == 'M8':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M8'] * (dt + 0.12) == (0.12) * m.deltaF[g,i,j,'M8'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M8'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M8']
                return m.deltaF[g,i,j+1,'M8'] * (dt + 0.12) == (0.12) * m.deltaF[g,i,j,'M8']
            if r == 'M7':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M7'] * (dt + 0.09) == (0.09) * m.deltaF[g,i,j,'M7'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M7'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M7']
                return m.deltaF[g,i,j+1,'M7'] * (dt + 0.09) == (0.09) * m.deltaF[g,i,j,'M7']
            if r == 'M6':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M6'] * (dt + 0.06) == (0.06) * m.deltaF[g,i,j,'M6'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M6'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M6']
                return m.deltaF[g,i,j+1,'M6'] * (dt + 0.06) == (0.06) * m.deltaF[g,i,j,'M6']
            if r == 'M5':
                if j == 1:
                    return m.deltaF[g,i,j+1,'M5'] * (dt + 0.03) == (0.03) * m.deltaF[g,i,j,'M5'] + + m.Gain_GOX[g] * dt * m.deltaFSP1['GOX', i,'M5'] + m.Gain_LIN[g] * dt * m.deltaFSP1['LIN', i,'M5']
                return m.deltaF[g,i,j+1,'M5'] * (dt + 0.03) == (0.03) * m.deltaF[g,i,j,'M5']
    return Constraint.Skip
model4.ASU_1 = Constraint(model4.G, model4.I, model4.J, model4.Mode, rule=_ASU_1)

def _ASU_2(m, g, i):
    return m.deltaFSP[g, i] == m.FSP[g, i] - m.F[g, i-1, NJ]
model4.ASU_2 = Constraint(model4.SP, model4.I, rule=_ASU_2)

def _ASU_2_1(m, g, i):
    return m.deltaFSP[g, i] == m.deltaFSP1[g, i, 'M1'] + m.deltaFSP1[g, i, 'M2'] + m.deltaFSP1[g, i, 'M3'] + m.deltaFSP1[g, i, 'M4'] + m.deltaFSP1[g, i, 'M5'] + m.deltaFSP1[g, i, 'M6']+ m.deltaFSP1[g, i, 'M7'] + + m.deltaFSP1[g, i, 'M8']
model4.ASU_2_1 = Constraint(model4.SP, model4.I, rule=_ASU_2_1)

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
model4.ASU_3 = Constraint(model4.G, model4.I, model4.J, rule=_ASU_3)

def _ASU_32(m,g,i,j,r):
    return m.deltaF[g,i,j,r] >= -40000 * m.y[i,r]
model4.ASU_32 = Constraint(model4.G,model4.I,model4.J,model4.Mode, rule=_ASU_32)

def _ASU_33(m,g,i,j,r):
    return m.deltaF[g,i,j,r] <= 40000 * m.y[i,r]
model4.ASU_33 = Constraint(model4.G,model4.I,model4.J,model4.Mode, rule=_ASU_33)

def _ASU_32_1(m,g,i,r):
    return m.deltaFSP1[g,i,r] >= -20000 * m.y[i,r]
model4.ASU_32_1 = Constraint(model4.SP,model4.I,model4.Mode, rule=_ASU_32_1)

def _ASU_33_1(m,g,i,r):
    return m.deltaFSP1[g,i,r] <= 20000 * m.y[i,r]
model4.ASU_33_1 = Constraint(model4.SP,model4.I,model4.Mode, rule=_ASU_33_1)


def _ASU_34(m,i):
    return m.y[i,'M1'] + m.y[i,'M2'] + m.y[i,'M3'] + m.y[i,'M4'] + m.y[i,'M5'] + m.y[i,'M6'] + m.y[i,'M7'] + m.y[i,'M8'] == 1
model4.ASU_34 = Constraint(model4.I,rule=_ASU_34)

leftEnd1={}
for i in range(1, 9):
    leftEnd1[i] = -7000 + 1750 * (i - 1)
model4.LeftEnd = Param(model4.Segment, initialize=leftEnd1)

rightEnd1={}
for i in range(1, 9):
    rightEnd1[i] = -5250 + 1750 * (i - 1)
model4.RightEnd = Param(model4.Segment, initialize=rightEnd1)

def _ASU_16(m, i):
    return m.deltaFSP['GOX', i] >= m.LeftEnd[1] * m.y[i, 'M1'] + m.LeftEnd[2] * m.y[i, 'M2'] + m.LeftEnd[3] * m.y[i, 'M3'] + m.LeftEnd[4] * m.y[i, 'M4'] + m.LeftEnd[5] * m.y[i, 'M5'] + m.LeftEnd[6] * m.y[i, 'M6'] + m.LeftEnd[7] * m.y[i, 'M7'] + m.LeftEnd[8] * m.y[i, 'M8'] + 1e-10
model4.ASU_16 = Constraint(model4.I, rule=_ASU_16)

def _ASU_17(m, i):
     return m.deltaFSP['GOX', i] <= m.RightEnd[1] * m.y[i, 'M1'] + m.RightEnd[2] * m.y[i, 'M2'] + m.RightEnd[3] * m.y[i, 'M3'] + m.RightEnd[4] * m.y[i, 'M4'] + m.RightEnd[5] * m.y[i, 'M5'] + m.RightEnd[6] * m.y[i, 'M6'] + m.RightEnd[7] * m.y[i, 'M7'] + m.RightEnd[8] * m.y[i, 'M8']
model4.ASU_17 = Constraint(model4.I, rule=_ASU_17)

def _ASU_4(m, g, i):
    return m.F[g, i, 1] == m.F[g, i-1, NJ]
model4.ASU_4 = Constraint(model4.G, model4.I, rule=_ASU_4)

def _FSPinitial1(m, i):
    return m.FSP['GOX', 0] == 30000 * Y3
model4.FSPinitial1 = Constraint(model4.I, rule=_FSPinitial1)

def _FSPinitial2(m, i):
    return m.FSP['LIN', 0] == 0 * Y3
model4.FSPinitial2 = Constraint(model4.I, rule=_FSPinitial2)

model4.y_lin = Var(model4.I, model4.J, within=Binary, bounds=(0,1), initialize=0)
def _firstStageMode2_8(m, i, j):
    return m.F['GOX', i, j] <= 30000 * (1-m.y_lin[i, j]) + 33000 * m.y_lin[i, j]
model4.firstStageMode2_8 = Constraint(model4.I, model4.J, rule=_firstStageMode2_8)

def _firstStageMode2_9(m, i, j):
    return m.F['GOX', i, j] >= 30000 * m.y_lin[i, j] + 1e-10
model4.firstStageMode2_9 = Constraint(model4.I, model4.J, rule=_firstStageMode2_9)

def _firstStageMode2_10(m, i, j):
    return m.F['LIN', i, j] <= 1300 * m.y_lin[i, j]
model4.firstStageMode2_10 = Constraint(model4.I, model4.J, rule=_firstStageMode2_10)

def _firstStageMode2_11(m, i, j):
    return m.y_lin[i, j] <= Y3
model4.firstStageMode2_11 = Constraint(model4.I, model4.J, rule=_firstStageMode2_11)

F_UB2={}
F_UB2['AIR'] = 170000
F_UB2['GOX'] = 33000
F_UB2['LOX'] = 1500
F_UB2['GAN'] = 100000
F_UB2['LIN'] = 1300
F_UB2['LAR'] = 1900
model4.F_UB = Param(model4.G, initialize=F_UB2)

F_LB2={}
F_LB2['AIR'] = 130000
F_LB2['GOX'] = 26000
F_LB2['LOX'] = 0
F_LB2['GAN'] = 70000
F_LB2['LIN'] = 0
F_LB2['LAR'] = 1500
model4.F_LB = Param(model4.G, initialize=F_LB2)

def _ASU_5(m, g, i, j):
    if g!='GAR':
        return m.F[g, i, j]  >= m.F_LB[g] * Y3
    return Constraint.Skip
model4.ASU_5 = Constraint(model4.G, model4.I, model4.J, rule=_ASU_5)

def _ASU_6(m, g, i, j):
    if g!='GAR':
        return m.F[g, i, j] <= m.F_UB[g] * Y3
    return Constraint.Skip
model4.ASU_6 = Constraint(model4.G, model4.I, model4.J, rule=_ASU_6)

def _ASU_7(m, i, j):
    return m.Q['AIRC', i, j] == 0.377 * m.F['AIR', i, j]
model4.ASU_7 = Constraint(model4.I, model4.J, rule=_ASU_7)

def _ASU_8(m, i, j):
    return m.F['GAR', i, j] >= 500 * m.Y_GAR[i, j]
model4.ASU_8 = Constraint(model4.I, model4.J, rule=_ASU_8)

def _ASU_9(m, i, j):
    return m.F['GAR', i, j] <= 900 * m.Y_GAR[i, j]
model4.ASU_9 = Constraint(model4.I, model4.J, rule=_ASU_9)

def _ASU_10(m, i, j):
    return m.Y_GAR[i, j] <= Y3
model4.ASU_10 = Constraint(model4.I, model4.J, rule=_ASU_10)

def _ASU_11(m, i):
    return m.FSP['GOX', i] >= 26000 * Y3
model4.ASU_11 = Constraint(model4.I, rule=_ASU_11)

def _ASU_12(m, i):
    return m.FSP['GOX', i] <= 33000 * Y3
model4.ASU_12 = Constraint(model4.I, rule=_ASU_12)


def _ASU_13(m, i):
    return m.FSP['LIN', i] >= 0 * Y3
model4.ASU_13 = Constraint(model4.I, rule=_ASU_13)

def _ASU_14(m, i):
    return m.FSP['LIN', i] <= 1300 * Y3
model4.ASU_14 = Constraint(model4.I, rule=_ASU_14)

def _ASU_30(m, i, j):
    return m.Q['GOXC', i, j] == 0.175 * m.F['GOX', i, j]
model4.ASU_30 = Constraint(model4.I, model4.J, rule=_ASU_30)

#switch
def _Switch1(m, i, r):
    return sum(m.Z[s, r, i]for s in m.Mode) - sum(m.Z[r, k, i]for k in m.Mode) == m.y[i,r] - m.y[i-1,r]
model4.Switch1 = Constraint(model4.I, model4.Mode, rule= _Switch1)

# init
def _init1(m):
    return m.y[0,'M1'] == 0
model4.init1 = Constraint(rule=_init1)

def _init2(m):
    return m.y[0,'M2'] == 0
model4.init2 = Constraint(rule=_init2)

def _init3(m):
    return m.y[0,'M3'] == 0
model4.init3 = Constraint(rule=_init3)

def _init4(m):
    return m.y[0,'M4'] == 0
model4.init4 = Constraint(rule=_init4)

def _init5(m):
    return m.y[0,'M5'] == 1
model4.init5 = Constraint(rule=_init5)

def _init6(m):
    return m.y[0,'M6'] == 0
model4.init6 = Constraint(rule=_init6)

def _init7(m):
    return m.y[0,'M7'] == 0
model4.init7 = Constraint(rule=_init7)

def _init8(m):
    return m.y[0,'M8'] == 0
model4.init8 = Constraint(rule=_init8)

