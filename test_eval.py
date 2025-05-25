import unittest
import math

import main
import math_parser
from math_parser import Parser, Node  # Replace with the actual module name


class TestMathExpressionEval(unittest.TestCase):
    
    def _test_parser(self, expression, result):
        parser = Parser(expression)
        new_expression = parser.parse()
        env = Parser.FUNCTIONS
        a = eval(result, env)
        if isinstance(new_expression, Node):
            b = new_expression.eval(env)
        else:
            b = new_expression
        self.assertEqual(a, b, expression)

    def test_basic_operations(self):
        self._test_parser("2 + 3", "(2 + 3)")
        self._test_parser("4 - 1", "(4 - 1)")
        self._test_parser("-4 - 1", "(-4 - 1)")
        self._test_parser("-4 + 1", "(-4 + 1)")
        self._test_parser("5 * 6", "(5 * 6)")
        self._test_parser("8 / 2", "(8 / 2)")

    def test_operator_precedence(self):
        self._test_parser("34 - 77/2", "(34 - (77 / 2))")
        self._test_parser("2 + 3 * 4", "(2 + (3 * 4))")
        self._test_parser("(2 + 3) * 4", "((2 + 3) * 4)")
        self._test_parser("-(2 + 3) * 4", "(-(2 + 3) * 4)")
        self._test_parser("-(2 + 3) + 4", "(-(2 + 3) + 4)")
        self._test_parser("-(2 + 3) - (2 + 2)", "(-(2 + 3) - (2 + 2))")
        self._test_parser("234*1+12", "((234 * 1) + 12)")

    def test_exponentiation(self):
        self._test_parser("2 ^ 3", "(2**3)")
        self._test_parser("1+2**3", "(1 + (2**3))")
        self._test_parser("1+2**3+4", "(1 + (2**3) + 4)")

    def test_factorial(self):
        self._test_parser("5!", "factorial(5)")

    def test_custom_operator(self):
        self._test_parser("3 // 4", "(3*4/(4+3))")
        self._test_parser("3 // 4 // 5", "(3*4*5/(4*5+3*5+3*4))")

    def test_constants(self):
        self._test_parser("pi", str(float(math.pi)))
        self._test_parser("e", str(float(math.e)))

    def test_functions(self):
        self._test_parser("sin(30)", "sin(30)")
        self._test_parser("log(10, 2)", "log(10, 2)")

    def test_engineering_notation(self):
        self._test_parser("1k", "1000.0")
        self._test_parser("2.5M", "2500000.0")
        self.assertAlmostEqual(float(Parser("3.4n").parse()), 3.4e-09, 9)

    def test_complex_expression(self):
        expr = "sin(2 * pi * 4k)! + 3M + 5 // 6"
        parsed = str(Parser(expr).parse())
        expected = "(factorial(sin(2 * 3.141592653589793 * 4000.0)) + 3000000.0 + (5*6/(6+5)))"
        self.assertEqual(parsed, expected)
        self._test_parser("1+2*3+4/5+6^7+8%9+sin(10*pi)-8!",
                          "((1 + (2 * 3) + (4 / 5) + (6**7) + (8 % 9) + sin(10 * 3.141592653589793)) - factorial(8))")

    def test_parallels(self):
        self._test_parser("45//45", "(45*45/(45+45))")
        self._test_parser("45//34", "(45*34/(34+45))")
        self._test_parser("45//34//12", "(45*34*12/(34*12+45*12+45*34))")
        
    def test_complex(self):
        self._test_parser("4j", "4j")
        self._test_parser("2+3j", "(2 + 3j)")

    def test_percentages(self):
        self._test_parser("2%", "(2/100)")
        self._test_parser("11+2%", "(11 * (1 + (2/100)))")
        self._test_parser("11-2%", "(11 * (1 - (2/100)))")
        self._test_parser("11*2%", "(11 * (2/100))")
        self._test_parser("2%+3", "((2/100) + 3)")
        self._test_parser("2%-3", "((2/100) - 3)")
        self._test_parser("3+11+2%", "(3 + (11 * (1 + (2/100))))")
        self._test_parser("5-11*2%", "(5 - (11 * (2/100)))")

    def test_bitwise_operators(self):
        self._test_parser("5&1", "(5 & 1)")
        self._test_parser("5^^1", "(5 ^ 1)")
        self._test_parser("1+5&1", "(1 + (5 & 1))")


class TestCalculate(unittest.TestCase):

    def test_variables(self):
        vars = {'a': 5, 'b': 2}
        result, _ = math_parser.evaluate("a+b", vars)
        self.assertEqual(7, result)
        result, _ = math_parser.evaluate("a-b", vars)
        self.assertEqual(3, result)
        result, _ = math_parser.evaluate("a*b", vars)
        self.assertEqual(10, result)
        result, _ = math_parser.evaluate("b-a", vars)
        self.assertEqual(-3, result)


if __name__ == "__main__":
    unittest.main()