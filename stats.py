import math
from collections import Counter
from count_inversions import count_inversions


def kendall_tau(arr):
    """Kendall's tau-b entre arr e sua versão ordenada."""
    n = len(arr)
    if n < 2:
        return 1.0

    inversions = count_inversions(list(arr))
    n0 = n * (n - 1) // 2
    ties_y = sum(c * (c - 1) // 2 for c in Counter(arr).values())

    concordant = n0 - inversions - ties_y
    discordant = inversions

    denom_sq = (concordant + discordant + ties_y) * (concordant + discordant)
    if denom_sq <= 0:
        return 1.0
    return (concordant - discordant) / math.sqrt(denom_sq)


def spearman_rho(arr):
    """Correlação de Spearman entre ranks posicionais e ranks de valor."""
    n = len(arr)
    if n < 2:
        return 1.0

    # Rank médio para empates
    sorted_vals = sorted(arr)
    rank_of = {}
    i = 0
    while i < n:
        j = i
        while j < n and sorted_vals[j] == sorted_vals[i]:
            j += 1
        rank_of[sorted_vals[i]] = (i + j + 1) / 2  # 1-indexado
        i = j

    x_mean = (n + 1) / 2
    y_ranks = [rank_of[v] for v in arr]
    y_mean = sum(y_ranks) / n

    num = sum((k + 1 - x_mean) * (y - y_mean) for k, y in enumerate(y_ranks))
    den_x = sum((k + 1 - x_mean) ** 2 for k in range(n))
    den_y = sum((y - y_mean) ** 2 for y in y_ranks)

    if den_x == 0 or den_y == 0:
        return 1.0
    return num / math.sqrt(den_x * den_y)
