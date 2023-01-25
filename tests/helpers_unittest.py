"""Unit tests for the helpers.py module"""
import unittest
from classevy import helpers


class TestNextBest(unittest.TestCase):
    """Unit tests for module-level functions."""

    def test_next_best(self):
        """Test the next_best function."""
        options = [0, 1, 2, 4]
        self.assertEqual(helpers.next_best(options, 0), 0)
        self.assertEqual(helpers.next_best(options, 1), 1)
        self.assertEqual(helpers.next_best(options, 2), 2)
        self.assertEqual(helpers.next_best(options, 3), 4)
        self.assertEqual(helpers.next_best(options, 5), 0)


class TestPopAbsMax(unittest.TestCase):
    """For the pop_absmax function"""

    def test(self):
        a = [1, -2]
        absmax = helpers.pop_absmax(a)
        self.assertEqual(absmax, -2)
        self.assertEqual(a, [1])


class TestDivide(unittest.TestCase):
    """Unit tests for hypo spread, biggest_impact, divide_one_prop"""

    def test_hypo_spread(self):
        mean_stds = helpers.hypo_spread(1, [[-2, -2], [1, 1]])
        self.assertEqual(mean_stds, [1.0, 1.5])

    def test_biggest_impact(self):
        bi = helpers.biggest_impact([10, 1, 0], [[0], [0]])
        self.assertEqual(bi, 10)

        bi = helpers.biggest_impact([10, 1, 0], [[10], [10]])
        self.assertEqual(bi, 0)

    def test_divide_list(self):
        sets, means, spread = helpers.divide_list([1, 1, 1], 3)
        self.assertEqual(sets, [[1], [1], [1]])
        self.assertEqual(means, [1, 1, 1])
        self.assertEqual(spread, 0)

        # the algo will favor filling empty lists first:
        sets, means, spread = helpers.divide_list([-1, 1, 0], 3)
        self.assertEqual(sets, [[-1], [1], [0]])
        self.assertEqual(means, [-1, 1, 0])

        sets, means, spread = helpers.divide_list([-1, 1, 0], 2)
        self.assertEqual(sets, [[-1, 0], [1]])
        self.assertEqual(means, [-0.5, 1])
