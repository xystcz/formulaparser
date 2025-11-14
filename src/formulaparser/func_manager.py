import math
from typing import Callable

class FunctionManager:
    def __init__(self):
        self.functions = {}

        self.register_func('abs', abs)
        self.register_func('max', max)
        self.register_func('min', min)
        self.register_func('sum', sum)
        self.register_func('pow', pow)
        self.register_func('sin', math.sin)
        self.register_func('cos', math.cos)
        self.register_func('tan', math.tan)
        self.register_func('log', math.log)
        self.register_func('exp', math.exp)
        self.register_func('sqrt', math.sqrt)

    def register_func(self, name: str, func: Callable):
        if name in self.functions:
            raise ValueError(f'函数"{name}"已存在')
        self.functions[name] = func

    def get_func(self, name: str) -> Callable:
        if name in self.functions:
            return self.functions[name]
        else:
            raise KeyError(f'函数不存在"{name}"')
