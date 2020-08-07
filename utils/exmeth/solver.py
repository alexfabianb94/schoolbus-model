import gurobipy as gp
from gurobipy import GRB
from utils.helpers import gen_path
import os
import numpy as np

def solver(instance, solution_file='solutions/solution.sol', fo='Z1', model_file='models/model.lp', time_limit=100, initial_sol = None):
    m = gp.Model("school")
        
    dist = lambda n1, n2: round(np.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2))
    edges = { (n1.id, n2.id): dist(n1,n2) for n1 in instance.nodes \
        for n2 in instance.nodes if n1.id != n2.id}

    depot = 0
    fdepot = instance.N - 1

    x = m.addVars(edges.keys() , vtype=GRB.BINARY, name='x')
    t = m.addVars(range(instance.N), vtype=GRB.CONTINUOUS, name='t')
    r = m.addVars(range(instance.N), vtype=GRB.CONTINUOUS, name='r')

    if fo == 'Z1':
        m.setObjective(gp.quicksum(t[e] for e in range(instance.n + 1, instance.n + instance.K + 1)), GRB.MINIMIZE)
        
    elif fo == 'Z2':
        m.setObjective(t[0] + gp.quicksum(0.01*t[e] for e in range(instance.n + 1, instance.n + instance.K + 1)), \
            GRB.MAXIMIZE)
        
    elif fo == 'Z3':
        m.setObjective(gp.quicksum(t[i] for i in range(1, instance.n + instance.K + 1)), GRB.MAXIMIZE)
        
    elif fo == 'Z4':
        m.setObjective(t[0] ,GRB.MAXIMIZE)
        
    elif fo == 'Z5':
        m.setObjective(gp.quicksum((edges[i,j] + instance.nodes[j].s)*x[i,j] \
            for i in range(1, instance.n + instance.K + 1) \
            for j in range(1, instance.n + instance.K + 1) \
            if (i,j) in edges), GRB.MINIMIZE)
        
    elif fo == 'Z6':
        m.setObjective(gp.quicksum((edges[i,j] + instance.nodes[j].s)*x[i,j] \
            for i in range(1, instance.n + instance.K + 1) \
            for j in range(1, instance.n + instance.K + 1) \
            if (i,j) in edges) - t[depot], GRB.MINIMIZE)
        
    elif fo == 'Z7':
        m.setObjective(gp.quicksum(t[instance.nodes[i].p] - t[i] \
            for i in range(1, instance.n + 1)), GRB.MINIMIZE)

    m.addConstr(gp.quicksum(x[depot, j] for j in range(1, instance.n + 1)) == 1, name='llegada')
    
    m.addConstrs((gp.quicksum(x[i,j] for i in range(0, instance.n + instance.K + 1) \
        if (i,j) in edges) == 1 \
        for j in range(1, instance.n + 1)), name='salida')

    m.addConstrs((gp.quicksum(x[i,j] for i in range(1, instance.n + instance.K + 1) \
        if (i,j) in edges) == 1 \
        for j in range(instance.n + 1, instance.n + instance.K + 1)), name='Rest3')
    
    m.addConstr(gp.quicksum(x[i, fdepot] for i in range(instance.n + 1, instance.n + instance.K + 1)) == 1, \
        name='Rest4')
    
    m.addConstrs((gp.quicksum(x[i,j] for j in range(1, instance.n + instance.K + 1) \
        if (i,j) in edges) == 1 \
        for i in range(1, instance.n + 1)), name='Rest5')

    m.addConstrs((gp.quicksum(x[i,j] for j in range(1, fdepot + 1) \
        if (i,j) in edges) == 1 \
        for i in range(instance.n + 1, instance.n + instance.K +1)), name='Rest6')

    m.addConstrs((t[j] >= t[i] + (edges[i,j] + instance.nodes[j].s)* x[i,j] -instance.M*(1-x[i,j]) \
        for i in range(1, instance.n + instance.K +1) \
        for j in range(1, instance.n + instance.K +1) \
        if (i,j) in edges), name='MTZ1')

    m.addConstrs((t[i] <= t[instance.nodes[i].p] for i in range(1, instance.n + 1)), name='MTZ2')

    m.addConstrs((r[j] >= r[i] + instance.nodes[j].d* x[i,j] - instance.Q*(1-x[i,j]) \
        for i in range(1, instance.n + instance.K +1) \
        for j in range(1, instance.n +1) \
        if (i,j) in edges), name='MTZ3')

    m.addConstrs((r[j] >= r[i] - instance.nodes[j].d* x[i,j] - instance.Q*(1-x[i,j]) \
        for i in range(1, instance.n + instance.K +1) \
        for j in range(instance.n +1, instance.n + instance.K +1) \
        if (i,j) in edges), name='MTZ4')

    m.addConstr(r[depot] == 0, name='MTZ5')
    
    # m.addConstr(t[depot] == 0, name='MTZ6')
    
    m.addConstr(r[fdepot] == 0, name='MTZ7')

    m.addConstrs((r[e] <= instance.Q for e in range(instance.n + 1, instance.n + instance.K + 1)), name='MTZ8')
    
    m.addConstrs((t[e] <= instance.nodes[e].TE for e in range(instance.n + 1, instance.n + instance.K + 1)), \
        name='MTZ9')
    
    m.addConstrs((t[j] >= t[depot] - instance.M*(1 - x[depot,j]) for j in range(1, instance.n + 1)), name='MTZ10')
    
    m.addConstrs((r[j] >= r[depot] + instance.nodes[j].d*x[depot,j] for j in range(1, instance.n + 1)), name='MTZ11')
    
    m.setParam(GRB.Param.TimeLimit, time_limit)
    
    m.update()
    
    if initial_sol:
        for arc in edges:
            x[arc[0], arc[1]].start = 1 if (arc[0], arc[1]) in initial_sol else 0
    elif os.path.exists(solution_file):
        m.read(solution_file)
    
    m.optimize()
    
    m.write(model_file)
    m.write(solution_file)

    values = m.getAttr("x", x)
    times = m.getAttr("x", t)
    arcs = [(i,j) for i,j in values.keys() if values[i,j] > 0.9]
    #print(times)
    path = gen_path(arcs)
    nsep = len(str(path)) + 10
    print("\n{}\nsolution: {}\n{}\n".format('-'*nsep, path, '-'*nsep))
    return arcs
