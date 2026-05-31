import point
import parser
from count_inversions import *
from sys import argv
import os

def main():
    argc = len(argv)
    if argc == 3:
        raise Exception(f'Unrecognized argument: {argv[2]}')
    if argc > 3:
        raise Exception(f'Unrecognized arguments: {argv[2:]}')

    if argc < 2:
        print('Filepath not provided, defaulting to "entrada.txt"')
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)) ,'entradas', 'entrada.txt')
    else:
        filepath = os.path.realpath(argv[1])

    graph = parser.parse_file(filepath)
    for i in range(len(graph)):
        print(f'({graph[i].x}, {graph[i].y})', end='')
        if i != len(graph) - 1:
            print(end=', ')
    print()

    arr = [p.y for p in graph]

    print(f'inversions: {count_inversions(arr)}')

if __name__ == "__main__":
    main()