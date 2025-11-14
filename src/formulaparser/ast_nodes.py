"""抽象语法树（AST）节点类定义"""
from operator import getitem
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Self, Any, List, Tuple, Dict, Union
from formulaparser.func_manager import FunctionManager
from formulaparser.op_manager import OperatorManager

# AST节点基类
class ASTNode(ABC):
    """抽象语法树节点基类"""

    def render(self):
        text = []
        q = [(self, '', '')]
        while q:
            node, cur_prefix, leaf_prefix = q.pop()
            head, leafs = node._render_info()
            text.append(f'{cur_prefix}{head}')
            if isinstance(leafs, list):
                leafs = [('', v) for v in leafs]
            else:
                leafs = [(f'{k}=', v) for k, v in leafs.items()]
            for i, (p_info, l_node) in enumerate(leafs[::-1]):
                if i == 0:
                    next_cur_prefix, next_leaf_prefix = f'{leaf_prefix}└───{p_info}', f'{leaf_prefix}    '
                else:
                    next_cur_prefix, next_leaf_prefix = f'{leaf_prefix}├───{p_info}', f'{leaf_prefix}│   '
                q.append((l_node, next_cur_prefix, next_leaf_prefix))
        return '\n'.join(text)

    @abstractmethod
    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        ...

    @abstractmethod
    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        ...


@dataclass
class NumberNode(ASTNode):
    """数字节点"""
    value: Union[float, int]

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'{self.value!r}', []

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return self.value


@dataclass
class StringNode(ASTNode):
    """字符串节点"""
    value: str

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'{self.value!r}', []

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return self.value


@dataclass
class NoneNode(ASTNode):
    def __repr__(self):
        return f'{self.__class__.__name__}'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'None', []

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return None


@dataclass
class BinaryOpNode(ASTNode):
    """二元运算符节点"""
    op_mgr: OperatorManager
    operator: str
    left: ASTNode
    right: ASTNode

    def __repr__(self):
        return f'{self.__class__.__name__}({self.operator}, {self.left!r}, {self.right!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'BinaryOp({self.operator})', [self.left, self.right]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        func = self.op_mgr.binary_funcs[self.operator]
        return func(self.left.evaluate(context), self.right.evaluate(context))


@dataclass
class UnaryOpNode(ASTNode):
    """一元运算符节点"""
    op_mgr: OperatorManager
    operator: str
    operand: ASTNode

    def __repr__(self):
        return f'{self.__class__.__name__}({self.operator}, {self.operand!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'UnaryOp({self.operator})', [self.operand]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        func = self.op_mgr.unary_funcs[self.operator]
        return func(self.operand.evaluate(context))


@dataclass
class IdentifierNode(ASTNode):
    func_mgr: FunctionManager
    name: str

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'ID({self.name})', []

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        if context and self.name in context:
            return context[self.name]
        elif self.func_mgr.has_func(self.name):
            return self.func_mgr.get_func(self.name)
        else:
            raise KeyError(f'{self.name} not found')


@dataclass
class SliceNode(ASTNode):
    start: ASTNode
    stop: ASTNode
    step: ASTNode

    def __repr__(self):
        return f'{self.__class__.__name__}({self.start!r}:{self.stop!r}:{self.step!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Slice', [self.start, self.stop, self.step]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return slice(self.start.evaluate(context), self.stop.evaluate(context), self.step.evaluate(context))


@dataclass
class AttributionNode(ASTNode):
    obj: ASTNode
    properties: List[str]

    def __repr__(self):
        return f'{self.__class__.__name__}({self.obj!r}.{".".join(self.properties)})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return f'Attr({".".join(self.properties)})', [self.obj]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        ans = self.obj.evaluate(context)
        for p in self.properties:
            ans = getattr(ans, p)
        return ans


@dataclass
class TupleNode(ASTNode):
    args: List[ASTNode]

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join([f'{arg!r}' for arg in self.args])})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Tuple', self.args[:]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return tuple(arg.evaluate(context) for arg in self.args)


@dataclass
class ListNode(ASTNode):
    args: List[ASTNode]

    def __repr__(self):
        return f'{self.__class__.__name__}[{", ".join([f'{arg!r}' for arg in self.args])}]'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'List', self.args[:]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return list(arg.evaluate(context) for arg in self.args)


@dataclass
class ItemNode(ASTNode):
    obj: ASTNode
    slice_obj: ASTNode
    def __repr__(self):
        return f'{self.__class__.__name__}({self.obj!r}, {self.slice_obj!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Item', [self.obj, self.slice_obj]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return getitem(self.obj.evaluate(context), self.slice_obj.evaluate(context))


@dataclass
class ArgsNode(ASTNode):
    args: List[ASTNode]

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(f'{arg!r}' for arg in self.args)})'

    def __len__(self):
        return len(self.args)

    def __getitem__(self, item):
        return self.args[item]

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Args', self.args[:]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return [arg.evaluate(context) for arg in self.args]

    def append(self, arg: ASTNode):
        self.args.append(arg)

    def to_tuple(self):
        return TupleNode(self.args[:])

    def to_list(self):
        return ListNode(self.args[:])


@dataclass
class KwargsNode(ASTNode):
    kwargs: Dict[str, ASTNode]

    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(f'{k}={v!r}' for k, v in self.kwargs.items())})'

    def __len__(self):
        return len(self.kwargs)

    def __getitem__(self, item):
        return self.kwargs[item]

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Kwargs', dict(**self.kwargs)

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        return {k: v.evaluate(context) for k, v in self.kwargs.items()}

    def add(self, k: str, v: ASTNode):
        if k in self.kwargs:
            raise KeyError(f'{k} already exists')
        self.kwargs[k] = v


@dataclass
class FunctionCallNode(ASTNode):
    """函数调用节点"""
    func: ASTNode
    args: ArgsNode
    kwargs: KwargsNode

    def __repr__(self):
        return f'{self.__class__.__name__}({self.func!r}, {self.args!r}, {self.kwargs!r})'

    def _render_info(self) -> Tuple[str, Union[List[Self], Dict[str, Self]]]:
        return 'Function', [self.func, self.args, self.kwargs]

    def evaluate(self, context: Union[Dict[str, Any], None]=None) -> Any:
        func = self.func.evaluate(context)
        return func(*self.args.evaluate(context), **self.kwargs.evaluate(context))