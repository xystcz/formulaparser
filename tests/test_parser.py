import unittest
import operator

from formulaparser import Parser


class TestParser(unittest.TestCase):

    def test_exception(self):
        parser = Parser()

        self.assertRaises(ValueError, parser.parse, '测试')
        self.assertRaises(ValueError, parser.parse, 'a @%@ b')

        ast = parser.parse('a + b')
        self.assertRaises(KeyError, ast.evaluate, context=dict(a=1, c=3))

    def test_parser(self):
        parser = Parser()
        context = dict(abc=5, bcd=9)
        cases = [
            ("2 + 3", 5),
            ("2 + 3 * 4", 14),
            ("(2 + 3) * 4", 20),
            ("10 / 2 - 3", 2),
            ("-5 + 3", -2),
            ('"hello"', 'hello'),
            ('"hello " + "world"', 'hello world'),
            ('max(1, 2, 3)', 3),
            ('sqrt(16)', 4),
            ('pow(2, 3)', 8),
            ('sqrt(16) + pow(2, 3)', 12),
            ('max(1, 2 * 3, sqrt(25))', 6),
            ('3 * sqrt(9) + 2', 11),
            ('-sqrt(4) + 10', 8),
            ('-sqrt(4) + 10 - 2 * (1 + (3 + 5) * (7 * (1 + 2)))', -330),
            ('max(1, 2, 3) + abc - bcd', -1),
        ]
        for formula, ans in cases:
            ast = parser.parse(formula)
            self.assertEqual(ast.evaluate(context), ans)

    def test_number(self):
        parser = Parser()
        context = dict(abc=5, bcd=9)

        cases = [
            ('abc + 2e3 - bcd', 1996),
            ('abc + 2.0e3 * bcd', 18005),
        ]
        for formula, ans in cases:
            ast = parser.parse(formula)
            self.assertEqual(ast.evaluate(context), ans)

        cases = [
            ('abc + 2.1e11 - bcd', context['abc'] + 2.1e11 - context['bcd']),
            ('abc + 2.0e-3 * bcd', context['abc'] + 2.0e-3 * context['bcd']),
            ('-2.0e-3 * bcd', -2.0e-3 * context['bcd']),
        ]
        for formula, ans in cases:
            ast = parser.parse(formula)
            self.assertAlmostEqual(ast.evaluate(context), ans, 10)

    def test_variable_node(self):
        parser = Parser()
        formula = '1 + abc - cef * abc'
        ast = parser.parse(formula)
        self.assertIs(ast.left.right, ast.right.right)

    def test_func(self):
        parser = Parser()

        def ratio_sum(ratio, *args):
            return sum(args) * ratio
        parser.register_function('ratio_sum', ratio_sum)

        def neg_sum(*args):
            return -sum(args)
        parser.register_function('neg_sum', neg_sum)

        context = dict(abc=5, bcd=9)

        formula = 'abc * neg_sum(abc, 3, bcd, 8) + ratio_sum(bcd, 1, 3, 6) + 9'
        ast = parser.parse(formula)
        self.assertEqual(ast.evaluate(context), -26)

        self.assertRaises(ValueError, parser.register_function, 'sum', sum)

    def test_operator(self):
        parser = Parser()
        parser.register_unary_op('&*', lambda x: x ** 3)
        parser.register_binary_op('$%', lambda x, y: (x + y) * 2, 16500)
        formula = '&*3 + 2000 $% 30 / 6 + max(1, 2, 23)'
        ast = parser.parse(formula)
        self.assertEqual(ast.evaluate(), 4060)

        self.assertRaises(ValueError, parser.register_unary_op, '.*', lambda x: x)
        self.assertRaises(ValueError, parser.register_unary_op, '+', lambda x: x)

        self.assertRaises(ValueError, parser.register_binary_op, '.*', lambda x, y: x+y, 20)
        self.assertRaises(ValueError, parser.register_binary_op, '*=', lambda x, y: x+y, -1)
        self.assertRaises(ValueError, parser.register_binary_op, '+', lambda x, y: x+y, 20)

    def test_iterator(self):
        parser = Parser()
        context = dict(abc=5, bcd=9, operator=operator)

        ast = parser.parse('[1, 2, abc, 66, 55][::2]')
        ans = ast.evaluate(context)
        self.assertIsInstance(ans, list)
        self.assertEqual(ans, [1, 5, 55])

        ast = parser.parse('(1, 2, abc, 66, 55, 99)[1:4:2]')
        ans = ast.evaluate(context)
        self.assertIsInstance(ans, tuple)
        self.assertEqual(ans, (2, 66))

    def test_function(self):
        parser = Parser()
        context = dict(abc=5, bcd=9)
        cases = [
            ('sum([1, 2, 9, abc])', 17),
            ('sum([1, 2, 9, abc], start=2)', 19),
            ('sum([1, 2, 9, abc][1:], start=0)', 16),
            ('sum((1, 2, 9, abc)[1:], start=0)', 16),
        ]
        for formula, ans in cases:
            ast = parser.parse(formula)
            self.assertEqual(ast.evaluate(context), ans)

    def test_property(self):
        parser = Parser()
        context = dict(abc=5, bcd=9, operator=operator)

        ast = parser.parse('operator.add(abc, bcd)')
        ans = ast.evaluate(context)
        self.assertEqual(ans, 14)

    def test_pythonic(self):
        parser = Parser()
        context = dict(abc=5, bcd=9, operator=operator)

        ast = parser.parse('sum([1,2,3], start=bcd) + max((4 ,5 ,7)) * operator.add(abc, bcd) + sum([1, 2, 3, 4, 5, 6][2::3])')
        self.assertEqual(ast.evaluate(context), 122)

    def test_repr(self):
        parser = Parser()
        ast = parser.parse('sum([1,2,3], start=bcd) + max((4 ,5 ,7)) * operator.add(abc, bcd) + sum([5, 6][::3])')
        self.assertEqual(f'{ast!r}', 'BinaryOpNode(+, BinaryOpNode(+, FunctionCallNode(IdentifierNode(sum), ArgsNode(ListNode[NumberNode(1), NumberNode(2), NumberNode(3)]), KwargsNode(start=IdentifierNode(bcd))), BinaryOpNode(*, FunctionCallNode(IdentifierNode(max), ArgsNode(TupleNode(NumberNode(4), NumberNode(5), NumberNode(7))), KwargsNode()), FunctionCallNode(AttributionNode(IdentifierNode(operator).add), ArgsNode(IdentifierNode(abc), IdentifierNode(bcd)), KwargsNode()))), FunctionCallNode(IdentifierNode(sum), ArgsNode(ItemNode(ListNode[NumberNode(5), NumberNode(6)], SliceNode(NoneNode:NoneNode:NumberNode(3)))), KwargsNode()))')
