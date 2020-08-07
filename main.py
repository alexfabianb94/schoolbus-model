#/usr/bin/python3

from utils.data import Data
from utils.exmeth.solver import solver
from utils.sheur.ts import ts
from utils.helpers import create_graph
import os
import argparse
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, default='data/data.dat',required=False, help='Data file')
    parser.add_argument('-s', '--solution', type=str, default='solutions/solution.sol', required=False, help='Solution file')
    parser.add_argument('-f', '--fo', type=str, default='Z3', required=False, help='Objective function')
    parser.add_argument('-m', '--model-file', type=str, default='models/model.lp', required=False, help='Model export file')
    parser.add_argument('-g', '--graph-file', type=str, default='graphs/solution.pdf', required=False, help='Graph file')
    parser.add_argument('-t', '--time', required=False, type=int, default=100, help='Time limit')
    parser.add_argument('-F', '--force', required=False, action='store_true', help='Force data')
    parser.add_argument('-T', '--tabu', required=False, action='store_true', help='Apply Tabu Search')
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
    tabu = args.tabu
    
    print('Params\ndata: {}\nsolution: {}\nfo: {}\nmodel_file: {}\ngraph_file: {}\ntime: {}\n' \
        .format(data,solution,fo,model_file,graph_file,time))
    
    with open(data) as file:
        input_data = file.read()
    instance = Data(input_data)
    ts_soluiton = ts(instance) if tabu else None
    sol = solver(instance, solution, fo, model_file, time, ts_soluiton)
    nodes = instance.nodes[:]
    create_graph(nodes, sol, graph_file) 

if __name__ == '__main__':
    main()
