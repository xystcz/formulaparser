from typing import Dict, Any, Callable
from formulaparser.func_manager import FunctionManager
from formulaparser.op_manager import OperatorManager
from formulaparser.lexer import Token, TokenType, Lexer
from formulaparser.ast_nodes import (
    ASTNode,
    NumberNode,
    StringNode,
    UnaryOpNode,
    BinaryOpNode,
    FunctionCallNode,
    VariableNode
)


class _Parser:
    """语法分析器"""

    def __init__(self, op_mgr: OperatorManager, func_mgr: FunctionManager, text: str):
        self.op_mgr = op_mgr
        self.func_mgr = func_mgr
        self.text = text
        self.tokens = Lexer(op_mgr, text).tokenize()
        self.position = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.variable_nodes = dict()

    def advance(self):
        """前进到下一个token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = Token(TokenType.EOF, None, -1)

    def parse(self) -> ASTNode:
        """解析表达式"""
        if self.current_token.type == TokenType.EOF:
            raise ValueError('表达式为空')

        result = self.parse_expression()

        if self.current_token.type != TokenType.EOF:
            raise ValueError(f'解析错误：意外的token {self.current_token}')

        return result

    def parse_expression(self, min_precedence: int = 0) -> ASTNode:
        """解析表达式（使用优先级爬升法）"""
        left = self.parse_unary()

        while self.current_token.type == TokenType.OPERATOR:
            operator = self.current_token.value
            if operator not in self.op_mgr.binary_ops:
                raise ValueError(f'Token无法解析为双目运算符：{self.current_token}')
            precedence = self.op_mgr.binary_precedences[operator]
            if precedence <= min_precedence:
                break
            self.advance()
            right = self.parse_expression(precedence)
            left = BinaryOpNode(operator, left, right)

        return left

    def parse_unary(self) -> ASTNode:
        """解析一元运算符"""
        if self.current_token.type == TokenType.OPERATOR:
            if self.current_token.value not in self.op_mgr.unary_ops:
                raise ValueError(f'Token无法解析为单目运算符：{self.current_token}')
            operator = self.current_token.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(operator, operand)

        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        """解析基本表达式"""
        token = self.current_token

        # 数字
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)

        # 字符串
        if token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value)

        # 括号表达式
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            if self.current_token.type != TokenType.RPAREN:
                raise ValueError(f'缺少右括号，位置：{self.current_token.position}')
            self.advance()
            return expr

        # 变量/函数调用
        if token.type == TokenType.IDENTIFIER:
            identifier = token.value
            self.advance()

            if self.current_token.type != TokenType.LPAREN:
                # 识别为变量，直接返回
                if identifier not in self.variable_nodes:
                    self.variable_nodes[identifier] = VariableNode(identifier)
                return self.variable_nodes[identifier]

            # 识别为函数
            if identifier not in self.func_mgr.functions:
                raise KeyError(f'函数"{identifier}"不存在')

            self.advance()  # 跳过左括号

            # 解析参数列表
            arguments = []
            if self.current_token.type != TokenType.RPAREN:
                arguments.append(self.parse_expression())

                while self.current_token.type == TokenType.COMMA:
                    self.advance()
                    arguments.append(self.parse_expression())

            if self.current_token.type != TokenType.RPAREN:
                raise ValueError(f'函数调用缺少右括号，位置：{self.current_token.position}')

            self.advance()  # 跳过右括号

            return FunctionCallNode(identifier, arguments)

        raise ValueError(f'意外的token：{token}')


class Parser:
    def __init__(self):
        self.op_mgr = OperatorManager()
        self.func_mgr = FunctionManager()

    def parse(self, text) -> ASTNode:
        _parser = _Parser(self.op_mgr, self.func_mgr, text)
        return _parser.parse()

    def register_function(self, name: str, func: Callable):
        self.func_mgr.register_func(name, func)

    def register_binary_op(self, op: str, func: Callable[[Any, Any], Any], precedence: int):
        self.op_mgr.register_binary_op(op, func, precedence)

    def register_unary_op(self, op: str, func: Callable[[Any], Any]):
        self.op_mgr.register_unary_op(op, func)

    def evaluate(self, node: ASTNode, context: Dict[str, Any]=None) -> Any:
        """求值AST节点"""
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, VariableNode):
            if context and node.name in context:
                return context[node.name]
            else:
                raise KeyError(f'变量不存在: {node.name}')
        elif isinstance(node, UnaryOpNode):
            return self.op_mgr.unary_funcs[node.operator](self.evaluate(node.operand, context))
        elif isinstance(node, BinaryOpNode):
            left = self.evaluate(node.left, context)
            right = self.evaluate(node.right, context)
            return self.op_mgr.binary_funcs[node.operator](left, right)
        elif isinstance(node, FunctionCallNode):
            return self.func_mgr.get_func(node.name)(*[self.evaluate(arg, context) for arg in node.arguments])
        else:
            raise ValueError(f'未知的节点类型：{type(node)}')
