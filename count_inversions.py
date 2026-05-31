import random

class _Return_object:
    def __init__(self, arr, inv):
        self.arr = arr
        self.inv = inv

# Método público, retorna o total de inversoes no vetor
def count_inversions(arr) -> int:
    return _count_inversions(arr).inv

# Método recursivo com base em merge sort
def _count_inversions(arr) -> _Return_object:
    if len(arr) == 1:
        return _Return_object(arr, 0)
    
    lro = _count_inversions(arr[:int(len(arr)/2)])
    rro = _count_inversions(arr[int(len(arr)/2):])

    return _sort_and_count(lro, rro)


# Merge + contagem de inversões, 
def _sort_and_count(lro, rro) -> _Return_object:
    li = 0
    ri = 0

    new_arr = []
    inv = lro.inv + rro.inv
         
    while li < len(lro.arr) and ri < len(rro.arr):
        if rro.arr[ri] < lro.arr[li]:
            new_arr.append(rro.arr[ri])
            inv += len(lro.arr) - li
            ri += 1
        else:
            new_arr.append(lro.arr[li])
            li += 1
    while li < len(lro.arr):
        new_arr.append(lro.arr[li])
        li += 1
    while ri < len(rro.arr):
        new_arr.append(rro.arr[ri])
        ri += 1
    
    if __name__ == "__main__":
        print(f'{inv}: {lro.arr} - {rro.arr}')

    return _Return_object(new_arr, inv)


# Teste
if __name__ == "__main__":
    arr = []
    for i in range(10):
        arr.append(random.randrange(30))

    print(f'-=-=-=-=-=-TESTING INVERSION COUNTER-=-=-=-=-=-')
    print(f'array: {arr}')
    print(f'inversions: {count_inversions(arr)}')