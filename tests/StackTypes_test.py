import unittest

from tolstack.StackTypes import *


class TestGetDistFromCode(unittest.TestCase):

    def test_uniform(self):
        self.assertEqual(get_dist_from_code("U"), DistType.UNIFORM)

    def test_normal_1s(self):
        self.assertEqual(get_dist_from_code("1S"), DistType.NORMAL_1S)

    def test_normal_2s(self):
        self.assertEqual(get_dist_from_code("2S"), DistType.NORMAL_2S)

    def test_normal_3s(self):
        self.assertEqual(get_dist_from_code("3S"), DistType.NORMAL_3S)

    def test_constant(self):
        self.assertEqual(get_dist_from_code("C"), DistType.CONSTANT)

    def test_derived(self):
        self.assertEqual(get_dist_from_code("D"), DistType.DERIVED)

    def test_unknown_code(self):
        self.assertIsNone(get_dist_from_code("X"))

    def test_lowercase_input(self):
        self.assertEqual(get_dist_from_code("u"), DistType.UNIFORM)
        self.assertEqual(get_dist_from_code("1s"), DistType.NORMAL_1S)
        self.assertEqual(get_dist_from_code("2s"), DistType.NORMAL_2S)
        self.assertEqual(get_dist_from_code("3s"), DistType.NORMAL_3S)
        self.assertEqual(get_dist_from_code("c"), DistType.CONSTANT)
        self.assertEqual(get_dist_from_code("d"), DistType.DERIVED)

    def test_code_with_spaces(self):
        self.assertEqual(get_dist_from_code(" U "), DistType.UNIFORM)
        self.assertEqual(get_dist_from_code(" 1S "), DistType.NORMAL_1S)
        self.assertEqual(get_dist_from_code(" 2S "), DistType.NORMAL_2S)
        self.assertEqual(get_dist_from_code(" 3S "), DistType.NORMAL_3S)
        self.assertEqual(get_dist_from_code(" C "), DistType.CONSTANT)
        self.assertEqual(get_dist_from_code(" D "), DistType.DERIVED)


class TestGetCodeFromDist(unittest.TestCase):
    def test_uniform(self):
        self.assertEqual(get_code_from_dist(DistType.UNIFORM), "U")

    def test_normal_1s(self):
        self.assertEqual(get_code_from_dist(DistType.NORMAL_1S), "1S")

    def test_normal_2s(self):
        self.assertEqual(get_code_from_dist(DistType.NORMAL_2S), "2S")

    def test_normal_3s(self):
        self.assertEqual(get_code_from_dist(DistType.NORMAL_3S), "3S")

    def test_constant(self):
        self.assertEqual(get_code_from_dist(DistType.CONSTANT), "C")

    def test_derived(self):
        self.assertEqual(get_code_from_dist(DistType.DERIVED), "D")


class TestGetEvalFromCode(unittest.TestCase):

    def test_worst_case(self):
        self.assertEqual(get_eval_from_code("W"), EvalType.WORSTCASE)

    def test_statistical_1s(self):
        self.assertEqual(get_eval_from_code("1S"), EvalType.STATISTICAL_1S)

    def test_statistical_2s(self):
        self.assertEqual(get_eval_from_code("2S"), EvalType.STATISTICAL_2S)

    def test_statistical_3s(self):
        self.assertEqual(get_eval_from_code("3S"), EvalType.STATISTICAL_3S)

    def test_unknown_code(self):
        self.assertEqual(get_eval_from_code("X"), EvalType.UNKNOWN)

    def test_lowercase_input(self):
        self.assertEqual(get_eval_from_code("w"), EvalType.WORSTCASE)
        self.assertEqual(get_eval_from_code("1s"), EvalType.STATISTICAL_1S)
        self.assertEqual(get_eval_from_code("2s"), EvalType.STATISTICAL_2S)
        self.assertEqual(get_eval_from_code("3s"), EvalType.STATISTICAL_3S)

    def test_code_with_spaces(self):
        self.assertEqual(get_eval_from_code(" W "), EvalType.WORSTCASE)
        self.assertEqual(get_eval_from_code(" 1S "), EvalType.STATISTICAL_1S)
        self.assertEqual(get_eval_from_code(" 2S "), EvalType.STATISTICAL_2S)
        self.assertEqual(get_eval_from_code(" 3S "), EvalType.STATISTICAL_3S)


class TestEvalType(unittest.TestCase):
    def test_worstcase_str(self):
        self.assertEqual(str(EvalType.WORSTCASE), "Worst Case")

    def test_statistical_1s_str(self):
        self.assertEqual(str(EvalType.STATISTICAL_1S), "Statistical ±1σ")

    def test_statistical_2s_str(self):
        self.assertEqual(str(EvalType.STATISTICAL_2S), "Statistical ±2σ")

    def test_statistical_3s_str(self):
        self.assertEqual(str(EvalType.STATISTICAL_3S), "Statistical ±3σ")

    def test_unknown_str(self):
        self.assertEqual(str(EvalType.UNKNOWN), "Unknown")
