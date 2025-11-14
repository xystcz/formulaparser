"""抽象语法树（AST）节点类定义"""
from dataclasses import dataclass
from typing import List, Union


# AST节点基类
class ASTNode:
    """抽象语法树节点基类"""

    def render(self):
        text = []
        q = [(self, '', '')]
        while q:
            node, cur_prefix, leaf_prefix = q.pop()
            if isinstance(node, (NumberNode, StringNode, VariableNode)):
                text.append(f'{cur_prefix}{node}')
                leaf_nodes = []
            else:
                if isinstance(node, BinaryOpNode):
                    text.append(f'{cur_prefix}BinaryOp({node.operator})')
                    leaf_nodes = [node.left, node.right]
                elif isinstance(node, UnaryOpNode):
                    text.append(f'{cur_prefix}UnaryOp({node.operator})')
                    leaf_nodes = [node.operand]
                elif isinstance(node, FunctionCallNode):
                    text.append(f'{cur_prefix}FunctionCall({node.name})')
                    leaf_nodes = node.arguments[:]
                else:
                    raise TypeError(f'不支持的Node类型：{type(node)}')
            for i, l_node in enumerate(leaf_nodes[::-1]):
                if i == 0:
                    next_cur_prefix, next_leaf_prefix = f'{leaf_prefix}└───', f'{leaf_prefix}    '
                else:
                    next_cur_prefix, next_leaf_prefix = f'{leaf_prefix}├───', f'{leaf_prefix}│   '
                q.append((l_node, next_cur_prefix, next_leaf_prefix))
        return '\n'.join(text)


@dataclass
class NumberNode(ASTNode):
    """数字节点"""
    value: Union[float, int]

    def __repr__(self):
        return f'Number({self.value})'


@dataclass
class StringNode(ASTNode):
    """字符串节点"""
    value: str

    def __repr__(self):
        return f'String("{self.value}")'


@dataclass
class VariableNode(ASTNode):
    """变量节点"""
    name: str

    def __repr__(self):
        return f'Variable({self.name})'


@dataclass
class BinaryOpNode(ASTNode):
    """二元运算符节点"""
    operator: str
    left: ASTNode
    right: ASTNode

    def __repr__(self):
        return f'BinaryOp({self.operator}, {self.left}, {self.right})'


@dataclass
class UnaryOpNode(ASTNode):
    """一元运算符节点"""
    operator: str
    operand: ASTNode

    def __repr__(self):
        return f'UnaryOp({self.operator}, {self.operand})'


@dataclass
class FunctionCallNode(ASTNode):
    """函数调用节点"""
    name: str
    arguments: List[ASTNode]

    def __repr__(self):
        args_str = ', '.join(str(arg) for arg in self.arguments)
        return f'FunctionCall({self.name}, [{args_str}])'
