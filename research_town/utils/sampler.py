import random
from typing import List, Tuple

from ..data import Idea


def sample_ideas(lst: List[Idea], n: int) -> List[List[Idea]]:
    total_subsets = 2 ** len(lst) - (len(lst) + 1)
    if len(lst) == 1:
        return lst
    if n > total_subsets:
        print(f'n cannot be greater than {total_subsets}')
        n = total_subsets

    sampled_subsets: set[Tuple[int, ...]] = set()
    lst_len = len(lst)
    lst_indices = list(range(lst_len))

    while len(sampled_subsets) < n:
        bits = random.getrandbits(lst_len)
        if bits == 0:
            continue  # Skip empty set
        indices = [i for i in lst_indices if bits & (1 << i)]
        if len(indices) < 2:
            continue  # Skip subsets of size 1

        indices_tuple = tuple(sorted(indices))
        sampled_subsets.add(indices_tuple)

    # Map indices back to lst elements
    result = []
    for indices_tuple in sampled_subsets:
        subset = [lst[i] for i in indices_tuple]
        result.append(subset)

    return result
