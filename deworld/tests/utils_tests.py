# coding: utf-8

from unittest import TestCase

from deworld.utils import E, prepair_to_approximation, resize2d

class UtilsTests(TestCase):

    def setUp(self):
        pass

    def test_prepair_to_approximation(self):
        powers = prepair_to_approximation([(1, 'a'), (3, 'b'), (10, 'c')])
        Q = 3.0/43
        self.assertEqual(['a', 'b', 'c'], [p[1] for p in powers])
        self.assertTrue(-E < powers[0][0] - Q*10 < E)
        self.assertTrue(-E < powers[1][0] - Q*10/3 < E)
        self.assertTrue(-E < powers[2][0] - Q < E)

    def test_prepair_to_approximation_with_0_distance(self):
        powers = prepair_to_approximation([(1, 'a'), (0, 'b'), (10, 'c')])
        self.assertEqual(powers, [(1, 'b')])

    def test_prepair_to_approximation_with_no_points(self):
        powers = prepair_to_approximation([], default='c')
        self.assertEqual(powers, [(1, 'c')])

    def test_resize2d_increase(self):
        array = [[1, 2 ,3],
                 [4, 5, 6]]
        self.assertEqual(resize2d(array, 5, 6), [[1, 2, 3, 3, 3],
                                                 [4, 5, 6, 6, 6],
                                                 [4, 5, 6, 6, 6],
                                                 [4, 5, 6, 6, 6],
                                                 [4, 5, 6, 6, 6],
                                                 [4, 5, 6, 6, 6]])

    def test_resize2d_when_x_not_chaged(self):
        array = [[1, 2 ,3],
                 [4, 5, 6]]
        self.assertEqual(resize2d(array, 3, 6), [[1, 2, 3],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6]])

    def test_resize2d_reduce(self):
        array = [[1, 2, 3, 3, 3],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6]]
        self.assertEqual(resize2d(array, 3, 2), [[1, 2 ,3],
                                                 [4, 5, 6]])

    def test_resize2d_when_y_not_changed(self):
        array = [[1, 2, 3, 3, 3],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6],
                 [4, 5, 6, 6, 6]]
        self.assertEqual(resize2d(array, 3, 6), [[1, 2, 3],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6],
                                                 [4, 5, 6]])
