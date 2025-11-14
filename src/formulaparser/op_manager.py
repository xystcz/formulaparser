import operator
from typing import Set, Dict, Callable, Any


class OperatorManager:
    AVAILABLE_CHARS = '+-*/<>=`~!@#$%^&|?'

    def __init__(self):
        self.binary_ops: Set[str] = set()
        self.binary_funcs: Dict[str, Callable[[Any, Any], Any]] = dict()
        self.binary_precedences: Dict[str, int] = dict()

        self.unary_ops: Set[str] = set()
        self.unary_funcs: Dict[str, Callable[[Any], Any]] = dict()

        self.register_binary_op('+', operator.add, 5000)
        self.register_binary_op('-', operator.sub, 5000)
        self.register_binary_op('*', operator.mul, 6000)
        self.register_binary_op('/', operator.truediv, 6000)

        self.register_unary_op('+', operator.pos)
        self.register_unary_op('-', operator.neg)

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

