import itertools
import random
from typing import List

from ..data import Idea


def sample_ideas(lst: List[Idea], n: int) -> List[List[Idea]]:
    valid_subsets = [
        list(subset)
        for i in range(2, len(lst) + 1)
        for subset in itertools.combinations(lst, i)
    ]
    if n > len(valid_subsets):
        raise ValueError(f'n cannot be greater than {len(valid_subsets)}')

    return random.sample(valid_subsets, n)
