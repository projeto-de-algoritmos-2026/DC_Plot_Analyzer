import point
import re

# retorna uma lista de pontos ordenada com base no valor de X
def parse_file(filepath) -> list[Point]:
    plot = []
    with open(filepath, 'r') as file:
        i = 1
        for line in file:
            x = 0
            y = 0
            
            line = line.strip()
            split = re.split(r', |,| ', line)
            if len(split) != 2:
                raise ValueError(f'Formatação do arquivo de entrada incorreto:\n{i}:{line}')

            try:
                x = float(split[0])
            except ValueError as e:
                raise ValueError(f'Valor de X não pode ser convertido em float:\n{i}:{line}\n{' ' * (len(str(i)) + 1)}{'^' * len(split[0])}\n{e}')

            try:
                y = float(split[1])
            except ValueError as e:
                raise ValueError(f'Valor de Y não pode ser convertido em float:\n{i}:{line}\n{' ' * (len(str(i)) + 1)}{' ' * (len(line) - len(split[1]))}{'^' * len(split[1])}\n{e}')

            plot.append(point.Point(x, y))
            
            i += 1
    
    return sorted(plot, key= lambda e: e.x)