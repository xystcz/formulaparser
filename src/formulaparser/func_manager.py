import math
import operator
from typing import Callable

class FunctionManager:

    PREDEFINE_FUNCTIONS = {
        'add':         operator.add,          # 加法: a + b,
        'concat':      operator.concat,       # 字符串拼接: seq1 + seq2,
        'contains':    operator.contains,     # 包含测试: obj in seq,
        'truediv':     operator.truediv,      # 除法: a / b,
        'floordiv':    operator.floordiv,     # 除法: a // b,
        'and_':        operator.and_,         # 按位与: a & b,
        'xor':         operator.xor,          # 按位异或: a ^ b,
        'invert':      operator.invert,       # 按位取反: ~ a,
        'or_':         operator.or_,          # 按位或: a | b,
        'pow':         operator.pow,          # 取幂: a ** b,
        'is_':         operator.is_,          # 标识: a is b,
        'is_not':      operator.is_not,       # 标识: a is not b,
        'setitem':     operator.setitem,      # 索引赋值: obj[k] = v,
        'delitem':     operator.delitem,      # 索引删除: del obj[k],
        'getitem':     operator.getitem,      # 索引取值: obj[k],
        'lshift':      operator.lshift,       # 左移: a << b,
        'mod':         operator.mod,          # 取模: a % b,
        'mul':         operator.mul,          # 乘法: a * b,
        'matmul':      operator.matmul,       # 矩阵乘法: a @ b,
        'neg':         operator.neg,          # 取反（算术）: - a,
        'not_':        operator.not_,         # 取反（逻辑）: not a,
        'pos':         operator.pos,          # 正数: + a,
        'rshift':      operator.rshift,       # 右移: a >> b,
        'mod':         operator.mod,          # 字符串格式化: s % obj,
        'sub':         operator.sub,          # 减法: a - b,
        'truth':       operator.truth,        # 真值测试: obj,
        'lt':          operator.lt,           # 比较: a < b,
        'le':          operator.le,           # 比较: a <= b,
        'eq':          operator.eq,           # 相等: a == b,
        'ne':          operator.ne,           # 不等: a != b,
        'ge':          operator.ge,           # 比较: a >= b,
        'gt':          operator.gt,           # 比较: a > b,

        'slice':       slice,                 # 切片

        'abs':         abs,
        'max':         max,
        'min':         min,
        'sum':         sum,

        'sin':         math.sin,
        'cos':         math.cos,
        'tan':         math.tan,
        'log':         math.log,
        'exp':         math.exp,
        'sqrt':        math.sqrt,

    }


    def __init__(self):
        self.functions = {}

        for name, func in self.PREDEFINE_FUNCTIONS.items():
            self.register_func(name, func)

    def register_func(self, name: str, func: Callable):
        if name in self.functions:
            raise ValueError(f'函数"{name}"已存在')
        self.functions[name] = func

    def get_func(self, name: str) -> Callable:
        if name in self.functions:
            return self.functions[name]
        else:
            raise KeyError(f'函数不存在"{name}"')
