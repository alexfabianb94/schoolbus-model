import numpy as np
from tqdm import tqdm
from utils.helpers import gen_path

def initial_solution(instance):
    s_total = 0
    path = [0]
    Nk = {i: [e for e in range(1,instance.n + 1) if instance.nodes[e].p == i] for i in range(instance.n + 1, instance.n + instance.K + 1)}
    for e in Nk:
        path += Nk[e] + [e]
    path.append(instance.N - 1)
    return path

def gen_arcs(path):
    arcs = []
    for i, node in enumerate(path[:-1]):
        arcs.append((path[i], path[i+1]))
    return arcs

def neigh_2opt(path):
    neigh = []
    n = len(path) - 1
    for i in range(1,n-1):
        for j in range(i+1,n):
            npath = path[:i] + path[j:i-1:-1] + path[j+1:]
            neigh.append(npath)
    return neigh

def neigh_mv(path):
    neigh = []
    cp_path = path[1:-1]
    for i, n1 in enumerate(cp_path):
        for j in range(len(cp_path[i+1:])+1):
            cand = [path[0]] + cp_path[:i] + cp_path[i+1:i+1+j] + [n1] + cp_path[i+1+j:] + [path[-1]]
            neigh.append(cand)
            #print(cand)
    return neigh

def is_factible(path, ins, edges):
    z, t, r = fo(path, ins, edges)
    for i, node in enumerate(path[1:]):
        if r[node] > ins.Q:
            print('r[{}] := {} </= {}'.format(node, r[node],ins.Q))
            return False
    for i in range(1, ins.n + 1):
        if t[i] > t[ins.nodes[i].p]:
            return False
    for i in range(ins.n +1, ins.n + ins.K +1):
        if t[i] > ins.nodes[i].TE:
            return False
    return True
    
    print(z,t,r)

def fo(path, ins, edges):
    t = {0: 0}
    r = {0: 0}
    total = 0
    for i, node in enumerate(path[1:]):
        t[node] = edges[path[i], node] + t[path[i]] + ins.nodes[node].s
        r[node] = r[path[i]] + ins.nodes[node].d if node <= ins.n else r[path[i]] - ins.nodes[node].d
        total += t[node] if ins.nodes[node].p not in t and r[node] <= ins.Q else 2*ins.M
    for i in range(ins.n +1, ins.n + ins.K +1):
        total += 0 if t[i] <= ins.nodes[i].TE else 2*ins.M
    return total, t, r

def ts(instance, s0 = None):
    dist = lambda n1, n2: round(np.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2))
    edges = { (n1.id, n2.id): dist(n1,n2) for n1 in instance.nodes \
        for n2 in instance.nodes if n1.id != n2.id}

    depot = 0
    fdepot = instance.N - 1
    
    path = gen_path(s0) if s0 else initial_solution(instance)
    print('Initial solution: {}'.format(path))
    sk = path
    fk = fo(sk, instance, edges)[0]
    s_glob = sk
    fo_glob = fk
    tabu = []
    tamaño = 20
    for it in tqdm(range(10*instance.N)):
        neigh = neigh_2opt(sk) + neigh_mv(sk)
        ski = neigh[0]
        fki = fo(ski, instance, edges)[0]
        if len(tabu) > tamaño:
            tabu.pop(0)
        for cand in neigh:
            if cand in tabu:
                continue
            f_cand = fo(cand, instance, edges)[0]
            if f_cand < fki:
                fki = f_cand
                ski = cand
            if f_cand < fo_glob:
                print('it {} => improve TS: from {} to {}, len {}'.format(it, fo_glob, f_cand, len(tabu)))
                fo_glob = f_cand
                s_glob = cand
        sk = ski
        fo(sk, instance, edges)[0]
        tabu.append(ski)
        
    arcs = gen_arcs(s_glob)
    nsep = len(str(s_glob)) + 13
    
    factible = is_factible(s_glob, instance, edges)
    print("\n{}\nLS solution: {}\nfo: {}, Factible : {}\n{}\n".format('-'*nsep, s_glob, fo_glob, factible, '-'*nsep))
    return arcs if factible else None
