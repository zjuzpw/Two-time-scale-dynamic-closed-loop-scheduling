from pyomo.environ import *

m = ConcreteModel()
m.z = Var()
m.x = Var(bounds=(0,1))
def conrule(m):
    return m.z <= pow(m.x,2)
m.c1 = Constraint(rule=conrule)

m.obj = Objective(expr=m.z,sense=maximize)

opt = SolverFactory('baron')
opt.solve(m,tee=True)