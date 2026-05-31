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

    plot = parser.parse_file(filepath)

    # print do conjunto de pontos
    for i in range(len(plot)):
        print(f'({plot[i].x}, {plot[i].y})', end='')
        if i != len(plot) - 1:
            print(end=', ')
    print()

    arr = [point.y for point in plot]   # array dos valores de y

    print(f'inversions: {count_inversions(arr)}')

if __name__ == "__main__":
    main()