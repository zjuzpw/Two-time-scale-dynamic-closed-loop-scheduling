from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
# from Tkinter import *
from ASU1 import model1
from ASU2 import model2
from ASU3 import model3
from ASU4 import model4
from Liq import model5
from Vap import model6
from data import *

import sys
import xlrd
import xlwt
import math


m = ConcreteModel()

m.add_component('m1',model1)
m.add_component('m2',model2)
m.add_component('m3',model3)
m.add_component('m4',model4)
m.add_component('m5',model5)
m.add_component('m6',model6)

NI=timelen
NJ=12
m.I = RangeSet(1,NI)
m.J = RangeSet(1,NJ)
m.I2 = RangeSet(0,NI)
m.J2 = RangeSet(0,NJ)

m.T5 = RangeSet(1,5)

m.G = Set(initialize=['GOX','MPGN','LPGN','GAR'])
m.G_GAN = Set(initialize=['MPGN','LPGN','SLT'])
m.S = Set(initialize=['LOX','LIN','LAR'])

m.F = Var(m.G, m.I2, m.J, within=Reals, bounds=(0,None), initialize=0)
m.F_GAN = Var(m.G_GAN, m.T5, m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.Y_GAN = Var(m.G_GAN, m.T5, m.I, m.J, within=Binary, bounds=(0,1), initialize=0)
m.Q_GAN1 = Var(m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.Q_GAN2 = Var(m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.D = Var(m.G, m.I2, m.J, within=Reals, bounds=(0,None), initialize=0)
m.P = Var(m.G, m.I2, m.J, within=Reals, bounds=(0,None), initialize=0)
m.Vent = Var(m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.Tank = Var(m.S, m.I2, m.J, within=Reals, bounds=(0,None), initialize=0)
m.F_L = Var(m.S, m.I2, m.J, within=Reals, bounds=(0,None), initialize=0)
m.ToLP = Var(m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.punish_pipe = Var(within=Reals, bounds=(0,None), initialize=0)


a={}
def read_excel():
    workbook = xlrd.open_workbook('demand.xlsx')
    worksheets = workbook.sheet_names()
    worksheet1 = workbook.sheet_by_name(u'Sheet2')
    for i in m.I:
        for j in m.J:
            a['GOX', i, j] = 100000#worksheet1.cell_value(i, 1)
            # print(worksheet1.cell_value(i, 1))
            a['MPGN', i, j] = 80000
            a['LPGN', i, j] = 20000
            a['GAR', i, j] = 1600
read_excel()


m.Demand = Param(m.G, m.I, m.J, initialize=a)
#m.d2 = Param(m.T1, m.S, initialize=b)
#m.Demand = Var(m.G, m.I, m.J, within=Reals, bounds=(0,None), initialize=0)
m.Sale = Var(m.S, m.I, m.J, within=Reals, bounds=(0,None), initialize=0)

m.dT = Param(initialize=0.083)

m.rev_liq = Var(within=Reals, bounds=(0,None), initialize=0)
m.rev_gas = Var(within=Reals, bounds=(0,None), initialize=0)
m.rev_pipe1 = Var(within=Reals, bounds=(0,None), initialize=0)
m.rev_pipe2 = Var(within=Reals, bounds=(0,None), initialize=0)
m.pro_liq = Var(within=Reals, bounds=(0,None), initialize=0)
m.pro_vap = Var(within=Reals, bounds=(0,None), initialize=0)
m.cost1 = Var(within=Reals, bounds=(0,None), initialize=0)
m.cost2 = Var(within=Reals, bounds=(0,None), initialize=0)
m.cost3 = Var(within=Reals, bounds=(0,None), initialize=0)
m.cost4 = Var(within=Reals, bounds=(0,None), initialize=0)
m.profit = Var(within=Reals, initialize=0)
m.price = Param(initialize=1)


def _B1(m, i, j):
    return m.Sale['LOX', i, j] <= 5000
m.B1 = Constraint(m.I, m.J, rule=_B1)

def _B2(m, i, j):
    return m.Sale['LIN', i, j] <= 5000
m.B2 = Constraint(m.I, m.J, rule=_B2)

def _B3(m, i, j):
    return m.Sale['LAR', i, j] <= 5000
m.B3 = Constraint(m.I, m.J,  rule=_B3)

def _P_ini1(m):
    return m.P['GOX', 1, 1] == 2100000
m.P_ini1 = Constraint(rule=_P_ini1)

def _P_ini2(m):
    return m.P['MPGN', 1, 1] == 1900000
m.P_ini2 = Constraint(rule=_P_ini2)

def _D_ini1(m):
    return m.D['GOX', 1, 1] == 3000
m.D_ini1 = Constraint(rule=_D_ini1)

def _D_ini2(m):
    return m.D['MPGN', 1, 1] == 3000
m.D_ini2 = Constraint(rule=_D_ini2)

def _Tank_ini1(m):
    return m.Tank['LOX', 1, 1] == 3883.5 * 804
m.Tank_ini1 = Constraint(rule=_Tank_ini1)

def _Tank_ini2(m):
    return m.Tank['LIN', 1, 1] == 1334.5 * 646
m.Tank_ini2 = Constraint(rule=_Tank_ini2)

def _Tank_ini3(m):
    return m.Tank['LAR', 1, 1] == 1555 * 785
m.Tank_ini3 = Constraint(rule=_Tank_ini3)

#########################

def _GOX_GW1(m, i, j):
    return m.F['GOX', i, j] == m.m1.F['GOX', i, j] + m.m2.F['GOX', i, j] + m.m3.F['GOX', i, j] + m.m4.F['GOX', i, j]
m.GOX_GW1 = Constraint(m.I, m.J, rule=_GOX_GW1)

def _GOX_GW2(m, i, j):
    if j!=1:
        return m.D['GOX', i, j] - m.D['GOX', i, j-1] == (m.F['GOX', i, j]  + m.m6.F_V['VLOX', i, j] - m.m5.F_L['LGOX', i, j]  - m.Demand['GOX', i, j] - m.Vent[i, j]) * m.dT
    return Constraint.Skip
m.GOX_GW2 = Constraint(m.I, m.J, rule=_GOX_GW2)

def _GOX_GW3(m, i, j):
    if j!=1:
        return m.D['GOX', i, j] - m.D['GOX', i, j-1] == (m.P['GOX', i, j] - m.P['GOX', i, j-1]) * 7000 * 22.4 * 0.001 / (8.314 * 273.15)
    return Constraint.Skip
m.GOX_GW3 = Constraint(m.I, m.J, rule=_GOX_GW3)

def _GOX_GW4(m, i, j):
    return m.P['GOX', i, j] >= 1600000
m.GOX_GW4 = Constraint(m.I, m.J, rule=_GOX_GW4)

def _GOX_GW5(m, i, j):
    return m.P['GOX', i, j] <= 2600000
m.GOX_GW5 = Constraint(m.I, m.J, rule=_GOX_GW5)

def _GOX_GW6(m, i):
   return m.D['GOX', i, 1] == m.D['GOX', i-1, NJ]
m.GOX_GW6 = Constraint(m.I, rule=_GOX_GW6)

def _GOX_GW7(m, i):
   return m.P['GOX', i, 1] == m.P['GOX', i-1, NJ]
m.GOX_GW7 = Constraint(m.I, rule=_GOX_GW7)

def _Vent_1(m,i,j):
    return m.Vent[i,j] <= 2000
m.Vent_1 = Constraint(m.I,m.J, rule=_Vent_1)

'''
def _GOX_GW8(m):
   return m.D['GOX', NI, NJ] >= m.D['GOX', 1, 1]
m.GOX_GW8 = Constraint(rule=_GOX_GW8)
'''

m.pipe = Var(m.I, m.J, within=Reals, bounds=(0, None), initialize=0)

def _pipePunish1(m, i, j):
    return m.P['GOX', i, j] >= 2050000 - m.pipe[i, j]
m.pipePunish1 = Constraint(m.I, m.J, rule=_pipePunish1)

def _pipePunish2(m, i, j):
    return m.P['GOX', i, j] <= 2150000 + m.pipe[i, j]
m.pipePunish2 = Constraint(m.I, m.J, rule=_pipePunish2)

###################

def _GOX_CC1(m, i, j):
    return m.F_L['LOX', i, j] == m.m1.F['LOX', i, j] + m.m2.F['LOX', i, j] + m.m3.F['LOX', i, j] + m.m4.F['LOX', i, j] 
m.GOX_CC1 = Constraint(m.I, m.J, rule=_GOX_CC1)

def _GOX_CC2(m, i, j):
    if j!=1:
        return m.Tank['LOX', i, j] - m.Tank['LOX', i, j-1] == (m.F_L['LOX', i, j]  + m.m5.F_L['LGOX', i, j] - m.m6.F_V['VLOX', i, j] - m.Sale['LOX', i, j]) * m.dT
    return Constraint.Skip
m.GOX_CC2 = Constraint(m.I, m.J, rule=_GOX_CC2)

def _GOX_CC3(m, i, j):
    return m.Tank['LOX', i, j] >= 2834 * 804
m.GOX_CC3 = Constraint(m.I, m.J, rule=_GOX_CC3)

def _GOX_CC4(m, i, j):
    return m.Tank['LOX', i, j] <= 4933 * 804
m.GOX_CC4 = Constraint(m.I, m.J, rule=_GOX_CC4)

def _GOX_CC5(m, i):
    return m.Tank['LOX', i, 1] == m.Tank['LOX', i-1, NJ]
m.GOX_CC5 = Constraint(m.I, rule=_GOX_CC5)

#####################

def _yiqu_1(m, i, j):
    return m.m1.F['GAN', i, j] + m.m4.F['GAN', i, j] +  m.m5.ToLIQ[i, j] == m.F_GAN['MPGN', 1, i, j]  + m.F_GAN['MPGN', 4, i, j] + m.F_GAN['MPGN', 5, i, j]  + m.F_GAN['LPGN', 1, i, j] + m.F_GAN['SLT', 1, i, j]
m.yiqu_1 = Constraint(m.I, m.J, rule=_yiqu_1)

def _yiqu_2(m, i, j):
    return m.Q_GAN1[i, j] == 0.2 * m.F_GAN['MPGN', 1, i, j]  + 0.161 * (m.F_GAN['MPGN', 4, i, j] + m.F_GAN['MPGN', 5, i, j] ) + 0.108 * m.F_GAN['LPGN', 1, i, j] 
m.yiqu_2 = Constraint(m.I, m.J, rule=_yiqu_2)

def _yiqu_3(m, q, i, j):
    return m.F_GAN['MPGN', q, i, j] >= 16000 * m.Y_GAN['MPGN', q, i, j]
m.yiqu_3 = Constraint(m.T5, m.I, m.J, rule=_yiqu_3)

def _yiqu_4(m, q, i, j):
    return m.F_GAN['MPGN', q, i, j] <= 20000 * m.Y_GAN['MPGN', q, i, j]
m.yiqu_4 = Constraint(m.T5, m.I, m.J, rule=_yiqu_4)

def _yiqu_5(m, q, i, j):
    return m.F_GAN['LPGN', q, i, j] >= 8000 * m.Y_GAN['LPGN', q, i, j]
m.yiqu_5 = Constraint(m.T5, m.I, m.J, rule=_yiqu_5)

def _yiqu_6(m, q, i, j):
    return m.F_GAN['LPGN', q, i, j] <= 10000 * m.Y_GAN['LPGN', q, i, j]
m.yiqu_6 = Constraint(m.T5, m.I, m.J, rule=_yiqu_6)

def _yiqu_7(m, i, j):
    return m.Y_GAN['MPGN', 4, i, j] >=  m.Y_GAN['MPGN', 1, i, j]
m.yiqu_7 = Constraint(m.I, m.J, rule=_yiqu_7)

def _yiqu_8(m, i, j):
    return m.Y_GAN['MPGN', 5, i, j] >=  m.Y_GAN['MPGN', 1, i, j]
m.yiqu_8 = Constraint(m.I, m.J, rule=_yiqu_8)



def _erqu_1(m, i, j):
    return m.m2.F['GAN', i, j] + m.m3.F['GAN', i, j]  == m.F_GAN['MPGN', 2, i, j] + m.F_GAN['MPGN', 3, i, j]  + m.F_GAN['LPGN', 2, i, j]  + m.F_GAN['LPGN', 3, i, j]  + m.F_GAN['SLT', 2, i, j]
m.erqu_1 = Constraint(m.I, m.J, rule=_erqu_1)

def _erqu_2(m, i, j):
    return m.Q_GAN2[i, j] == 0.178 * m.F_GAN['MPGN', 2, i, j]  + 0.161 * m.F_GAN['MPGN', 3, i, j]  + 0.111 * m.F_GAN['LPGN', 2, i, j]  + 0.107 * m.F_GAN['LPGN', 3, i, j] 
m.erqu_2 = Constraint(m.I, m.J, rule=_erqu_2)

def _erqu_3(m, i, j):
    return m.Y_GAN['MPGN', 3, i, j] >= m.F_GAN['MPGN', 2, i, j]
m.erqu_3 = Constraint(m.I, m.J, rule=_erqu_3)

def _erqu_4(m, i, j):
    return m.Y_GAN['LPGN', 3, i, j] >= m.F_GAN['LPGN', 2, i, j]
m.erqu_4 = Constraint(m.I, m.J, rule=_erqu_4)



#####################

def _GAN_GW1(m, i, j):
    if j!=1:
        return m.D['MPGN', i, j] - m.D['MPGN', i, j-1] == (sum(m.F_GAN['MPGN', q, i, j] for q in m.T5)  + m.m6.F_V['VLIN', i, j] - m.m5.F_L['LGAN', i, j] - m.ToLP[i, j] - m.m5.ToLIQ[i, j] - m.Demand['MPGN', i, j]) * m.dT
    return Constraint.Skip
m.GAN_GW1 = Constraint(m.I, m.J, rule=_GAN_GW1)

def _GAN_GW2(m, i, j):
    if j!=1:
        return m.D['MPGN', i, j] - m.D['MPGN', i, j-1] == (m.P['MPGN', i, j] - m.P['MPGN', i, j-1]) * 2072 * 22.4 * 0.001 / (8.314 * 273.15)
    return Constraint.Skip
m.GAN_GW2 = Constraint(m.I, m.J, rule=_GAN_GW2)

def _GAN_GW3(m, i, j):
    return m.P['MPGN', i, j] >= 1600000
m.GAN_GW3 = Constraint(m.I, m.J, rule=_GAN_GW3)

def _GAN_GW4(m, i, j):
    return m.P['MPGN', i, j] <= 2300000
m.GAN_GW4 = Constraint(m.I, m.J, rule=_GAN_GW4)


def _GAN_GW5(m, i, j):
    return (m.F_GAN['LPGN', 1, i, j] + m.F_GAN['LPGN', 2, i, j] + m.F_GAN['LPGN', 3, i, j] + m.ToLP[i, j]) * m.dT == m.Demand['LPGN', i, j] * m.dT
m.GAN_GW5 = Constraint(m.I, m.J, rule=_GAN_GW5)

def _GAN_GW6(m, i):
    return m.D['MPGN', i, 1] == m.D['MPGN', i-1, NJ]
m.GAN_GW6 = Constraint(m.I, rule=_GAN_GW6)

def _GAN_GW7(m, i):
    return m.P['MPGN', i, 1] == m.P['MPGN', i-1, NJ]
m.GAN_GW7 = Constraint(m.I, rule=_GAN_GW7)


##########################

def _GAN_CC1(m, i, j):
    return m.F_L['LIN', i, j] == m.m1.F['LIN', i, j] + m.m2.F['LIN', i, j] + m.m3.F['LIN', i, j] + m.m4.F['LIN', i, j] 
m.GAN_CC1 = Constraint(m.I, m.J, rule=_GAN_CC1)

def _GAN_CC2(m, i, j):
    if j!=1:
        return m.Tank['LIN', i, j] - m.Tank['LIN', i, j-1] == (m.F_L['LIN', i, j]  + m.m5.F_L['LGAN', i, j] - m.m6.F_V['VLIN', i, j] - m.Sale['LIN', i, j]) * m.dT
    return Constraint.Skip
m.GAN_CC2 = Constraint(m.I, m.J, rule=_GAN_CC2)

def _GAN_CC3(m, i, j):
    return m.Tank['LIN', i, j] >= 942 * 646
m.GAN_CC3 = Constraint(m.I, m.J, rule=_GAN_CC3)

def _GAN_CC4(m, i, j):
    return m.Tank['LIN', i, j] <= 1727 * 646
m.GAN_CC4 = Constraint(m.I, m.J, rule=_GAN_CC4)

def _GAN_CC5(m, i):
    return m.Tank['LIN', i, 1] == m.Tank['LIN', i-1, NJ]
m.GAN_CC5 = Constraint(m.I, rule=_GAN_CC5)

##############################


def _GAR_GW1(m, i, j):
    return m.F['GAR', i, j]  == m.m1.F['GAR', i, j] + m.m2.F['GAR', i, j] + m.m3.F['GAR', i, j] + m.m4.F['GAR', i, j]
m.GAR_GW1 = Constraint(m.I, m.J, rule=_GAR_GW1)

def _GAR_GW2(m, i, j):
    return m.F['GAR', i, j] * m.dT == m.Demand['GAR', i, j] * m.dT
m.GAR_GW2 = Constraint(m.I, m.J, rule=_GAR_GW2)


def _GAR_CC1(m, i, j):
    return m.F_L['LAR', i, j] == m.m1.F['LAR', i, j] + m.m2.F['LAR', i, j] + m.m3.F['LAR', i, j] + m.m4.F['LAR', i, j]
m.GAR_CC1 = Constraint(m.I, m.J, rule=_GAR_CC1)

def _GAR_CC2(m, i, j):
    if j!=1:
        return m.Tank['LAR', i, j] - m.Tank['LAR', i, j-1] == (m.F_L['LAR', i, j] - m.F['GAR', i, j] - m.Sale['LAR', i, j]) * m.dT
    return Constraint.Skip
m.GAR_CC2 = Constraint(m.I, m.J, rule=_GAR_CC2)

def _GAR_CC3(m, i, j):
    return m.Tank['LAR', i, j] >= 785 * 785
m.GAR_CC3 = Constraint(m.I, m.J, rule=_GAR_CC3)

def _GAR_CC4(m, i, j):
    return m.Tank['LAR', i, j] <= 2325 * 785
m.GAR_CC4 = Constraint(m.I, m.J, rule=_GAR_CC4)

def _GAR_CC5(m, i):
    return m.Tank['LAR', i, 1] == m.Tank['LAR', i-1, NJ]
m.GAR_CC5 = Constraint(m.I, rule=_GAR_CC5)

##################################
'''
def _PipeConstraint(m, g):
    return m.D[g, NI, NJ] >= m.D[g, 1, 1]
m.PipeConstraint = Constraint(m.G, rule=_PipeConstraint)
'''

# def _OBJ1(m):
#     return m.rev_liq == sum(m.F_L['LOX', i, j] * m.dT for i in m.I for j in m.J) / 804 * 1.143 * 1400 + sum(m.F_L['LIN', i, j] * m.dT for i in m.I for j in m.J) / 646 * 0.8083 * 1100 + sum((m.F_L['LAR', i, j] - m.F['GAR', i, j]) * m.dT for i in m.I for j in m.J) / 785 * 1.4 * 2000
# m.OBJ1 = Constraint(rule=_OBJ1)
def _OBJ1(m):
    return m.rev_liq == (m.Tank['LOX', NI, NJ] - m.Tank['LOX', 1, 1]) / 804 * 1.143 * 1400 + (m.Tank['LIN', NI, NJ] - m.Tank['LIN', 1, 1]) / 646 * 0.8083 * 1100 + (m.Tank['LAR', NI, NJ] - m.Tank['LAR', 1, 1]) / 785 * 1.4 * 2000
    + sum(Sale['LOX', i, j] * m.dT for i in m.I for j in m.J) / 804 * 1.143 * 1400 + sum(Sale['LIN', i, j] * m.dT for i in m.I for j in m.J) / 646 * 0.8083 * 1100 + sum(Sale['LAR', i, j] * m.dT for i in m.I for j in m.J) / 785 * 1.4 * 2000
m.OBJ1 = Constraint(rule=_OBJ1)

def _OBJ2(m):
    return m.rev_gas == sum((m.Demand['GOX', i, j] * 0.4499 + (m.Demand['MPGN', i, j] + m.Demand['LPGN', i, j]) * 0.1 + m.Demand['GAR', i, j] * 1.2) for i in m.I for j in m.J) * m.dT
m.OBJ2 = Constraint(rule=_OBJ2)

def _OBJ3(m):
    return m.rev_pipe1 == (m.D['GOX', NI, NJ] - m.D['GOX', 1, 1]) * 0.4499  #+ (m.D['MPGN', NI, NJ] - m.D['MPGN', 1, 1]) * 0.1
m.OBJ3 = Constraint(rule=_OBJ3)

def _OBJ3_2(m):
    return m.rev_pipe2 == (m.D['MPGN', NI, NJ] - m.D['MPGN', 1, 1]) * 0.1
m.OBJ3_2 = Constraint(rule=_OBJ3_2)
#
# def _OBJ4(m):
#     return m.pro_liq == sum(m.m5.F_L['LGOX', i, j] * m.dT for i in m.I for j in m.J) / 804 * 1.143 * 1400 + sum(m.m5.F_L['LGAN', i, j] * m.dT for i in m.I for j in m.J) / 646 * 0.8083 * 1100
# m.OBJ4 = Constraint(rule=_OBJ4)
#
# def _OBJ5(m):
#     return m.pro_vap == -sum(m.m6.F_V['VLOX', i, j] * m.dT for i in m.I for j in m.J) / 804 * 1.143 * 1400 - sum(m.m6.F_V['VLIN', i, j] * m.dT for i in m.I for j in m.J) / 646 * 0.8083 * 1100
# m.OBJ5 = Constraint(rule=_OBJ5)

def _OBJ6(m):
    return m.cost1 == sum((m.m1.Q['AIRC', i, j] + m.m2.Q['AIRC', i, j] + m.m3.Q['AIRC', i, j] + m.m4.Q['AIRC', i, j]) * m.dT for i in m.I for j in m.J) * m.price 
m.OBJ6 = Constraint(rule=_OBJ6)

def _OBJ7(m):
    return m.cost2 == sum((m.m1.Q['GOXC', i, j] + m.m2.Q['GOXC', i, j] +m.m3.Q['GOXC', i, j] + m.m4.Q['GOXC', i, j]) * m.dT for i in m.I for j in m.J) * m.price
m.OBJ7 = Constraint(rule=_OBJ7)

def _OBJ8(m):
    return m.cost3 == sum((m.Q_GAN1[i, j] + m.Q_GAN2[i, j]) for i in m.I for j in m.J) * m.dT * m.price
m.OBJ8 = Constraint(rule=_OBJ8)

def _pipePunish3(m):
    return m.punish_pipe == sum(m.pipe[i, j] for i in m.I for j in m.J) * 1000
m.pipePunish3 = Constraint(rule=_pipePunish3)

m.obj = Objective(expr= m.rev_liq + m.rev_gas + m.rev_pipe1 + m.rev_pipe2 - m.cost1 - m.cost2 - m.cost3 - m.punish_pipe , sense=maximize) # + m.pro_vap + m.pro_liq

# solvername='baron'
# solverpath_folder='C:\\baron'
# solverpath_exe='C:\\baron\\baron'
# sys.path.append(solverpath_folder)
# solver=SolverFactory(solvername,executable=solverpath_exe)
# solver.options["LPSol"] = 3
# solver.solve(m,tee=True, keepfiles=True)
ss = SolverFactory('cplex')
ss.options['mipgap'] = 0.0001
ss.solve(m, tee=True, keepfiles=True)

def write_excel():
    workbook = xlwt.Workbook()
    sheet1 = workbook.add_sheet('GOX', cell_overwrite_ok=True)
    sheet2 = workbook.add_sheet('Pipe', cell_overwrite_ok=True)
    sheet3 = workbook.add_sheet('LIN', cell_overwrite_ok=True)
    sheet4 = workbook.add_sheet('LIQVAP', cell_overwrite_ok=True)
    for i in range(1, NI+1):
        sheet1.write(i, 0, m.m2.FSP['GOX', i].value)
        sheet1.write(i, 1, m.m3.FSP['GOX', i].value)
        sheet1.write(i, 2, m.m4.FSP['GOX', i].value)
        for j in range(1, NJ+1):
            sheet1.write(j + (i - 1) * NJ, 3, m.m1.F['GOX', i, j].value)
            sheet1.write(j+(i-1)*NJ, 4, m.m2.F['GOX', i, j].value)
            sheet1.write(j+(i-1)*NJ, 5, m.m3.F['GOX', i, j].value)
            sheet1.write(j+(i-1)*NJ, 6, m.m4.F['GOX', i, j].value)

    for i in range(1, NI+1):
        for j in range(1, NJ+1):
            sheet2.write(j+(i-1)*NJ, 0, m.D['GOX', i, j].value)
            sheet2.write(j+(i-1)*NJ, 1, m.P['GOX', i, j].value)
            sheet2.write(j+(i-1)*NJ, 3, m.Vent[i, j].value)

    for i in range(1, NI+1):
        sheet3.write(i, 0, m.m2.FSP['LIN', i].value)
        sheet3.write(i, 1, m.m3.FSP['LIN', i].value)
        sheet3.write(i, 2, m.m4.FSP['LIN', i].value)
        for j in range(1, NJ + 1):
            sheet3.write(j+(i-1)*NJ, 4, m.m2.F['LIN', i, j].value)
            sheet3.write(j+(i-1)*NJ, 5, m.m3.F['LIN', i, j].value)
            sheet3.write(j+(i-1)*NJ, 6, m.m4.F['LIN', i, j].value)

            sheet4.write(j+(i-1)*NJ, 0 , m.m5.F_L['LGOX', i, j].value)
            sheet4.write(j+(i-1)*NJ, 1, m.m5.F_L['LGAN', i, j].value)
            sheet4.write(j+(i-1)*NJ, 2, m.m6.F_V['VLOX', i, j].value)
            sheet4.write(j+(i-1)*NJ, 3, m.m6.F_V['VLIN', i, j].value)
    workbook.save('example2.xls')
write_excel()


