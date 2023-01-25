import numpy as np
from typing import Union, List

Numeric = Union[int, float, complex, np.number]


# some general functions
def next_best(options: List[int], choice: int) -> int:
    """find the option that equals choice, or the next item or if there is no
    next item, the first item

    Args:
        options: List of options to choose from.
        choice: preferred option.

    Returns:
        choice or next item in the options or first item.
    """
    checks = [op >= choice for op in options]
    idx = np.argmax(np.array(checks))
    return options[idx]


def hypo_spread(num: Numeric, sets: List[List[Numeric]]) -> List[Numeric]:
    """Hypothetically assigning this num to one class or the other would result in
    which new spreads?
    We want to assign it to the option which causes the smallest new spread.

    Args:
        num: Input number to check.
        sets: The list of sets versus which to check the num

    Returns:
        A list of hypothetical std across sets, for each set, if the num, were added to
        that set.
    """
    sets = [k if len(k) else [0] for k in sets]
    mean_stds = []  # will contain all possible std when the num is added to a class
    for c in sets:
        sets_no_c = sets.copy()
        sets_no_c.remove(c)
        mean_stds.append(
            np.array(
                [np.array(c0).mean() for c0 in sets_no_c] + [np.array(c + [num]).mean()]
            ).std()
        )
    return mean_stds


def biggest_impact(num_list: List[Numeric], sets: List[List[Numeric]]) -> Numeric:
    """Which num in num_list has the biggest impact on the spread?
    Pop it from the num_list.

    Args:
        num_list: List to pick the number from
        sets: The list of sets versus which to check the num

    Returns:
        The value with the biggest impact on the spread of means of sets.
    """
    max_stds = []
    for num in num_list:
        mean_stds = hypo_spread(num, sets)
        max_stds.append(np.max(np.array(mean_stds)))
    index = np.argmax(np.array(max_stds))
    return num_list.pop(index)


def pop_absmax(lst: List[Numeric]) -> Numeric:
    """Find the maximum absolute value in a list and pop it from the list.

    Args:
        lst: input list

    Returns:
        popped value
    """
    absmax = np.max(np.array([abs(i) for i in lst]))
    if absmax in lst:
        m = absmax
    elif -absmax in lst:
        m = -absmax

    index = lst.index(m)
    return lst.pop(index)


def divide_list(
    num_list: List[Numeric], n_sets: int
) -> tuple[List[List[Numeric]], List[Numeric], Numeric]:
    sets: list = [[] for _ in range(n_sets)]
    """Divide a list of numbers into a number of sets trying to minimize the spread
    over the mean values of each set.

    Args:
        num_list: numbers to divide
        n_sets: number of sets over which to divide

    Returns:
        sets: the numbers divided into sets
        means: the mean of each set
        spread: the spread of the means of sets
    """
    for i in range(len(num_list)):
        # pick the number with the highest potential impact:
        num = biggest_impact(num_list, sets)
        # if any of the classes is still empty, add it there:
        if not all([len(c) for c in sets]):
            for c in sets:
                if len(c) == 0:
                    c.append(num)
                    break
        else:
            mean_stds = hypo_spread(num, sets)
            # now add the num to the class that results in the smallest std:
            index = np.argmin(np.array(mean_stds))
            sets[index].append(num)
    means = [np.array(c).mean() if len(c) else 0 for c in sets]
    spread = np.array(means).std()
    return sets, means, spread


def divide_num(num: Numeric, n_sets: int) -> List[int]:
    """Divide a number num into n_sets equal integer parts, as best as possible.
    For example, dividing 14 into 3 groups should yield [5, 5, 4]
    
    Args:
        num: the number to divide
        n_sets: how many groups to divide it in
        
    Returns:
        sets: list of numbers divided
    """
    base: int = np.floor(num/n_sets)
    rest = np.mod(num, n_sets)
    sets = [base]*n_sets
    for i in range(rest):
        sets[i] += 1

    return sets
