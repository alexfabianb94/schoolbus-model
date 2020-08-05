#/usr/bin/env python

import gurobipy as gp
from gurobipy import GRB
import numpy as np
from helpers.data import Data


def solver(instance):
    m = gp.Model("school")
        
    dist = lambda n1, n2: round(np.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2))
    edges = { (n1.id, n2.id): dist(n1,n2) for n1 in instance.nodes \
                                        for n2 in instance.nodes if n1.id != n2.id}

    depot = 0
    fdepot = 24

    x = m.addVars(edges.keys() , vtype=GRB.BINARY, name='x')
    t = m.addVars(range(instance.N), vtype=GRB.CONTINUOUS, name='t')
    r = m.addVars(range(instance.N), vtype=GRB.CONTINUOUS, name='r')


    m.setObjective(gp.quicksum(t[e] for e in range(instance.n + 1, instance.n + instance.K + 1)), GRB.MINIMIZE)
    #m.setObjective(t[0] + gp.quicksum(0.01*t[e] for e in range(instance.n + 1, instance.n + instance.K + 1)),\
    #                                                                                               GRB.MAXIMIZE)

    #m.setObjective(t[0] ,GRB.MAXIMIZE)

    m.addConstr(gp.quicksum(x[depot, j] for j in range(1, instance.n + 1)) == 1, name='llegada')
    m.addConstrs((gp.quicksum(x[i,j] for i in range(0, instance.n + instance.K + 1) \
                            if (i,j) in edges.keys()) == 1 \
                                    for j in range(1, instance.n + 1)), name='salida')

    m.addConstrs((gp.quicksum(x[i,j] for i in range(1, instance.n + instance.K + 1) \
                            if (i,j) in edges.keys()) == 1 \
                                    for j in range(instance.n + 1, instance.n + instance.K + 1)), name='Rest3')
    m.addConstr(gp.quicksum(x[i, fdepot] for i in range(instance.n + 1, instance.n + instance.K + 1)) == 1,\
                                                                                            name='Rest4')
    m.addConstrs((gp.quicksum(x[i,j] for j in range(1, instance.n + instance.K + 1) \
                            if (i,j) in edges.keys()) == 1 \
                                    for i in range(1, instance.n + 1)), name='Rest5')

    m.addConstrs((gp.quicksum(x[i,j] for j in range(1, fdepot + 1) \
                            if (i,j) in edges.keys()) == 1 \
                                    for i in range(instance.n + 1, instance.n + instance.K +1)), name='Rest6')

    m.addConstrs((t[j] >= t[i] + (edges[i,j] + instance.nodes[j].s)* x[i,j] -instance.M*(1-x[i,j]) \
                                        for i in range(1, instance.n + instance.K +1) \
                                        for j in range(1, instance.n + instance.K +1) \
                                            if (i,j) in edges.keys()), name='MTZ1')

    m.addConstrs((t[i] <= t[instance.nodes[i].p] for i in range(1, instance.n + 1)), name='MTZ2')

    m.addConstrs((r[j] >= r[i] + instance.nodes[j].d* x[i,j] - instance.Q*(1-x[i,j]) \
                                        for i in range(1, instance.n + instance.K +1) \
                                        for j in range(1, instance.n +1) \
                                            if (i,j) in edges.keys()), name='MTZ3')

    m.addConstrs((r[j] >= r[i] - instance.nodes[j].d* x[i,j] - instance.Q*(1-x[i,j]) \
                                        for i in range(1, instance.n + instance.K +1) \
                                        for j in range(instance.n +1, instance.n + instance.K +1) \
                                            if (i,j) in edges.keys()), name='MTZ4')

    m.addConstr(r[depot] == 0, name='MTZ5')
    # m.addConstr(t[depot] == 0, name='MTZ6')
    m.addConstr(r[fdepot] == 0, name='MTZ7')

    m.addConstrs((r[e] <= instance.Q for e in range(instance.n + 1, instance.n + instance.K + 1)), name='MTZ8')
    m.addConstrs((t[e] <= instance.nodes[e].TE for e in range(instance.n + 1, instance.n + instance.K + 1)), \
                                                                                                name='MTZ9')
    m.addConstrs((t[j] >= t[depot] - instance.M*(1 - x[depot,j]) for j in range(1, instance.n + 1)), name='MTZ10')
    m.addConstrs((r[j] >= r[depot] + instance.nodes[j].d*x[depot,j] for j in range(1, instance.n + 1)), name='MTZ11')

    m.setParam(GRB.Param.TimeLimit, 100.0)
    
    m.optimize()
    m.write('models/model.lp')

    values = m.getAttr("x", x)
    arcs = [(i,j) for i,j in values.keys() if values[i,j] > 0.9]
    print(arcs)
    
if __name__ == '__main__':
    with open('data/data.dat') as file:
        input_data = file.read()
    instance = Data(input_data)
    solver(instance)

