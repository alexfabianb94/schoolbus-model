#/usr/bin/env python

import gurobipy as gp
from gurobipy import GRB
from helpers.data import Data
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import argparse

def create_graph(nodes, arcs, graph_file='graphs/sol.pdf'):
    graph = nx.Graph()
    nodes_graph = [(n1.id, {'pos': (n1.x, n1.y),\
                             'lab': n1.id if n1.p else 'c-'+str(n1.id)}) for n1 in nodes]
    graph.add_nodes_from(nodes_graph)
    graph.add_edges_from(arcs)
    pos = nx.get_node_attributes(graph, 'pos')
    n = max([node.id for node in nodes if node.p])
    color = [max(n1.p-n,0) if n1.p else max(n1.id-n,0) for n1 in nodes]
    shape = ['o' if n1.p else 's' for n1 in nodes]
    labels = nx.get_node_attributes(graph, 'lab')
    nx.draw(graph, pos,node_color=color, labels = labels, node_size=600)
    plt.savefig(graph_file)
    
def gen_path(arcs):
    dict_arcs = {arc[0]: arc[1] for arc in arcs}
    i = 0
    path = [i]
    for _ in arcs:
        i = dict_arcs[i]
        path.append(i)
    return path

def solver(instance, solution_file='solutions/solution.sol', fo='Z1', model_file='models/model.lp', time_limit=100):
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
            if (i,j) in edges.keys()), GRB.MINIMIZE)
        
    elif fo == 'Z6':
        m.setObjective(gp.quicksum((edges[i,j] + instance.nodes[j].s)*x[i,j] \
            for i in range(1, instance.n + instance.K + 1) \
            for j in range(1, instance.n + instance.K + 1) \
            if (i,j) in edges.keys()) - t[depot], GRB.MINIMIZE)
        
    elif fo == 'Z7':
        m.setObjective(gp.quicksum(t[instance.nodes[i].p] - t[i] \
            for i in range(1, instance.n + 1)), GRB.MINIMIZE)

    m.addConstr(gp.quicksum(x[depot, j] for j in range(1, instance.n + 1)) == 1, name='llegada')
    
    m.addConstrs((gp.quicksum(x[i,j] for i in range(0, instance.n + instance.K + 1) \
        if (i,j) in edges.keys()) == 1 \
        for j in range(1, instance.n + 1)), name='salida')

    m.addConstrs((gp.quicksum(x[i,j] for i in range(1, instance.n + instance.K + 1) \
        if (i,j) in edges.keys()) == 1 \
        for j in range(instance.n + 1, instance.n + instance.K + 1)), name='Rest3')
    
    m.addConstr(gp.quicksum(x[i, fdepot] for i in range(instance.n + 1, instance.n + instance.K + 1)) == 1, \
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
    
    m.setParam(GRB.Param.TimeLimit, time_limit)
    
    if os.path.exists(solution_file):
        m.update()
        m.read(solution_file)
    
    m.optimize()
    
    m.write(model_file)
    m.write(solution_file)

    values = m.getAttr("x", x)
    arcs = [(i,j) for i,j in values.keys() if values[i,j] > 0.9]
    path = gen_path(arcs)
    nsep = len(str(path)) + 10
    print("\n{}\nsolution: {}\n{}\n".format('-'*nsep, path, '-'*nsep))
    return arcs
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, default='data/data.dat',required=False, help='data file')
    parser.add_argument('-s', '--solution', type=str, default='solutions/solution.sol', required=False, help='solution file')
    parser.add_argument('-f', '--fo', type=str, default='Z1', required=False, help='objective function')
    parser.add_argument('-m', '--model-file', type=str, default='models/model.lp', required=False, help='model export file')
    parser.add_argument('-g', '--graph-file', type=str, default='graphs/sol.pdf', required=False, help='graph file')
    parser.add_argument('-t', '--time', required=False, type=int, default=100, help='time limit')
    parser.add_argument('-F', '--force', required=False, action='store_true', help='force data')
    args = parser.parse_args()
    
    if not args.force:
        assert os.path.exists(args.data)
        assert os.path.splitext(args.solution)[1] == '.sol'
        assert args.fo in ['Z1', 'Z2', 'Z3', 'Z4', 'Z5', 'Z6', 'Z7']
        assert os.path.splitext(args.model_file)[1] == '.lp'
        assert os.path.splitext(args.graph_file)[1] == '.pdf'
    
    data = args.data
    solution = args.solution
    fo = args.fo
    model_file = args.model_file
    graph_file = args.graph_file
    time = args.time
    
    
    print('Params\ndata: {}\nsolution: {}\nfo: {}\nmodel_file: {}\ngraph_file: {}\ntime: {}\n' \
        .format(data,solution,fo,model_file,graph_file,time))
    
    with open(data) as file:
        input_data = file.read()
    instance = Data(input_data)
    sol = solver(instance, solution, fo, model_file, time)
    nodes = instance.nodes[:]
    create_graph(nodes, sol, graph_file) 

if __name__ == '__main__':
    main()
