import point
import parser
from count_inversions import *
from sys import argv
import os
import stats
from interp_text import interp_text

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
    if len(plot) < 30:
        for i in range(len(plot)):
            print(f'({plot[i].x}, {plot[i].y})', end='')
            if i != len(plot) - 1:
                print(end=', ')
        print()
    else:
        print('large input file, skipping print...')

    yarr = [point.y for point in plot]   # array dos valores de y
    xarr = [point.x for point in plot]   # array dos valores de x

    inv = count_inversions(yarr)
    size = len(plot)
    print(f'inversions: {inv} out of a maximum of {size * (size - 1) / 2:.0f}')
    tau = stats.kendall_tau(yarr)
    print(f'kendall tau (τ): {tau:.4f}')
    print(f'spearman rho (ρ): {stats.spearman_rho(yarr):.4f}')
    print(interp_text(tau))


if __name__ == "__main__":
    main()
