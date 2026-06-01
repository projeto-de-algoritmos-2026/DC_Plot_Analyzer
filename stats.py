import math
from collections import Counter
from count_inversions import count_inversions


def kendall_tau(y, x=None):
    """Kendall tau-b entre a sequência y (ordenada por x) e a ordem crescente.

    Quando x tem empates, pares com mesmo x não são concordantes nem
    discordantes — calculado em O(n²). Sem empates em x, usa a contagem
    de inversões D&C em O(n log n).
    """
    n = len(y)
    if n < 2:
        return 1.0

    n0 = n * (n - 1) // 2
    x_has_ties = x is not None and len(set(x)) < n

    if not x_has_ties:
        # Caminho rápido: T_x = 0, usa contagem D&C
        D = count_inversions(list(y))
        T_y = sum(c * (c - 1) // 2 for c in Counter(y).values())
        C = n0 - D - T_y
        T_x = 0
    else:
        # Caminho geral: O(n²) — necessário para empates em x
        C, D, T_x, T_y = 0, 0, 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                dx = (x[j] > x[i]) - (x[j] < x[i])
                dy = (y[j] > y[i]) - (y[j] < y[i])
                if dx == 0:
                    T_x += 1
                if dy == 0:
                    T_y += 1
                if dx != 0 and dy != 0:
                    if dx == dy:
                        C += 1
                    else:
                        D += 1

    denom_sq = (n0 - T_x) * (n0 - T_y)
    if denom_sq <= 0:
        return 1.0
    return (C - D) / math.sqrt(denom_sq)


def spearman_rho(y, x=None):
    """Correlação de Spearman entre os ranks de x (ou posições) e de y."""
    n = len(y)
    if n < 2:
        return 1.0

    def avg_ranks(arr):
        sorted_vals = sorted(arr)
        rank_of = {}
        i = 0
        while i < n:
            j = i
            while j < n and sorted_vals[j] == sorted_vals[i]:
                j += 1
            rank_of[sorted_vals[i]] = (i + j + 1) / 2
            i = j
        return [rank_of[v] for v in arr]

    x_ranks = avg_ranks(x) if x is not None else list(range(1, n + 1))
    y_ranks = avg_ranks(y)

    x_mean = sum(x_ranks) / n
    y_mean = sum(y_ranks) / n

    num = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x_ranks, y_ranks))
    den_x = sum((xi - x_mean) ** 2 for xi in x_ranks)
    den_y = sum((yi - y_mean) ** 2 for yi in y_ranks)

    if den_x == 0 or den_y == 0:
        return 1.0
    return num / math.sqrt(den_x * den_y)
