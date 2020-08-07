#/usr/bin/env python

import networkx as nx
import matplotlib.pyplot as plt

def create_graph(nodes, arcs, graph_file='graphs/sol.pdf'):
    graph = nx.Graph()
    nodes_graph = [(n1.id, {'pos': (n1.x, n1.y),\
                             'lab': n1.id if n1.p else 'c-'+str(n1.id)}) for n1 in nodes]
    graph.add_nodes_from(nodes_graph)
    graph.add_edges_from(arcs)
    pos = nx.get_node_attributes(graph, 'pos')
    n = max(node.id for node in nodes if node.p)
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
