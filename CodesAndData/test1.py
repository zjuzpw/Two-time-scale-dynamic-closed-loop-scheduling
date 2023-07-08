from pyomo.environ import *
from pyomo.opt import SolverFactory, SolverStatus, TerminationCondition, ProblemFormat
from Tkinter import *
import math

m = ConcreteModel()

list1={}
list2={}
for i in range(1,31):
    list1[i] = i*math.pi/15
    list2[i] = 85000+5000*sin(list1[i])
    print list2[i]

