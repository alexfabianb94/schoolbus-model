#/usr/bin/env python

import re

def clean_data(data):
    cpdata = data[:]
    patterns = [r'[ \t]+', r'#[\w\d áéíóú]+\n', r'(\/\*)[\w\n\d\s:=;]+(\*\/)']
    for pat in patterns:
        cpdata = re.sub(pat, ' ', cpdata)
    return cpdata.strip()

class Node:
    def __init__(self, idn):
        self.id = idn
        self.x = None
        self.y = None
        self.d = None
        self.s = None
        self.p = None
        self.TE = None
        
exp_data = {
        'N': r'set nodos *:= *([ \d\n]+) *;',
        'NumCole': r'param NumCole *:=[ \n]*([ \d\n]+)[ \n]*;',
        'NumUsua': r'param NumUsua *:=[ \n]*([ \d\n]+)[ \n]*;',
        'Q': r'param *Q *:=[ \n]*([ \d\n]+)[ \n]*;',
        'M': r'param *M *:=[ \n]*([ \d\n]+)[ \n]*;',
        'coords': r'param: xcoord ycoord *:=[ \n]*([ \d\n]+)[ \n]*;',
        'D': r'param D *:=[ \n]*([ \d\n]+)[ \n]*;',
        'S': r'param S *:=[ \n]*([ \d\n]+)[ \n]*;',
        'P': r'param P *:=[ \n]*([ \d\n]+)[ \n]*;',
        'TE': r'param TE *:=[ \n]*([ \d\n]+)[ \n]*;'
    }

class Data:
    def __init__(self, input_data):
        data = clean_data(input_data)
        self.N = max(map(int, re.findall(exp_data['N'], data)[0].split())) + 1
        self.nodes = [Node(i) for i in range(self.N)]
        self.K = int(re.findall(exp_data['NumCole'], data)[0])
        self.n = int(re.findall(exp_data['NumUsua'], data)[0])
        self.Q = int(re.findall(exp_data['Q'], data)[0])
        self.M = int(re.findall(exp_data['M'], data)[0])
        
        coords = map(str.split, re.findall(exp_data['coords'], data)[0].strip().split('\n'))
        for coord in coords:
            [node, x, y] = map(int, coord)
            self.nodes[node].x, self.nodes[node].y = x, y
            
        D_nodes = map(str.split, re.findall(exp_data['D'], data)[0].strip().split('\n'))
        for node_D in D_nodes:
            [node, d] = map(int, node_D)
            self.nodes[node].d = d
            
        S_nodes = map(str.split, re.findall(exp_data['S'], data)[0].strip().split('\n'))
        for node_S in S_nodes:
            [node, s] = map(int, node_S)
            self.nodes[node].s = s
            
        P_nodes = map(str.split, re.findall(exp_data['P'], data)[0].strip().split('\n'))
        for node_P in P_nodes:
            [node, p] = map(int, node_P)
            self.nodes[node].p = p

        TE_nodes = map(str.split, re.findall(exp_data['TE'], data)[0].strip().split('\n'))
        for node_TE in TE_nodes:
            [node, TE] = map(int, node_TE)
            self.nodes[node].TE = TE
