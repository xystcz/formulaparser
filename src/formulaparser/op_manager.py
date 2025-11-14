import operator
from typing import Set, Dict, Callable, Any


class OperatorManager:
    AVAILABLE_CHARS = '+-*/<>=`~!@#$%^&|?'

    PREDEFINE_BINARY_OPERATORS = {
        # 比较运算
        '<':  (operator.lt,       11000),
        '<=': (operator.le,       11000),
        '==': (operator.eq,       11000),
        '!=': (operator.ne,       11000),
        '>=': (operator.ge,       11000),
        '>':  (operator.gt,       11000),
        # 按位或
        '|':  (operator.or_,      12000),
        # 按位异或
        '^':  (operator.xor,      13000),
        # 按位与
        '&':  (operator.and_,     14000),
        # 移位
        '<<': (operator.lshift,   15000),
        '>>': (operator.rshift,   15000),
        # 加和减
        '+':  (operator.add,      16000),
        '-':  (operator.sub,      16000),
        # 乘，除，整除，取余，矩阵乘
        '*':  (operator.mul,      17000),
        '/':  (operator.truediv,  17000),
        '//': (operator.floordiv, 17000),
        '%':  (operator.mod,      17000),
        '@':  (operator.matmul,   17000),
    }
    PREDEFINE_UNARY_OPERATORS = {
        '+': operator.pos,
        '-': operator.neg,
        '~': operator.invert,
    }

    def __init__(self):
        self.binary_ops: Set[str] = set()
        self.binary_funcs: Dict[str, Callable[[Any, Any], Any]] = dict()
        self.binary_precedences: Dict[str, int] = dict()

        self.unary_ops: Set[str] = set()
        self.unary_funcs: Dict[str, Callable[[Any], Any]] = dict()

        for op, (func, precedence) in self.PREDEFINE_BINARY_OPERATORS.items():
            self.register_binary_op(op, func, precedence)

        for op, func in self.PREDEFINE_UNARY_OPERATORS.items():
            self.register_unary_op(op, func)

    def is_operator_legal(self, op: str) -> bool:
        return all(c in self.AVAILABLE_CHARS for c in op)

    def register_binary_op(self, op: str, func: Callable[[Any, Any], Any], precedence: int):
        if not self.is_operator_legal(op):
            raise ValueError(f'不合法的运算符："{op}", 运算符仅能包含字符："{self.AVAILABLE_CHARS}"')
        if precedence <= 0:
            raise ValueError(f'运算符"{op}"优先级必须大于0')
        if op in self.binary_ops:
            raise ValueError(f'双目运算符"{op}"已存在')
        self.binary_ops.add(op)
        self.binary_funcs[op] = func
        self.binary_precedences[op] = precedence

    def register_unary_op(self, op: str, func: Callable[[Any], Any]):
        if not self.is_operator_legal(op):
            raise ValueError(f'不合法的运算符："{op}", 运算符仅能包含字符："{self.AVAILABLE_CHARS}"')
        if op in self.unary_ops:
            raise ValueError(f'单目运算符"{op}"已存在')
        self.unary_ops.add(op)
        self.unary_funcs[op] = func

