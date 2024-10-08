import random
import itertools
from typing import List
from ..data import Insight

def sample(lst: List[Insight], n: int) -> List[List[Insight]]:
    valid_subsets = [list(subset) for i in range(2, len(lst)+1) for subset in itertools.combinations(lst, i)]
    if n > len(valid_subsets):
        raise ValueError(f"n cannot be greater than {len(valid_subsets)}")
    
    return random.sample(valid_subsets, n)
