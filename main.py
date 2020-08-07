#/usr/bin/env python

from utils.data import Data
from utils.solver import solver
from utils.helpers import create_graph
import os
import argparse
    
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
