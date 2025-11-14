from typing import Any, Callable
from formulaparser.func_manager import FunctionManager
from formulaparser.op_manager import OperatorManager
from formulaparser.lexer import Token, TokenType, Lexer
from formulaparser.ast_nodes import (
    ASTNode, NumberNode, StringNode, UnaryOpNode, BinaryOpNode, FunctionCallNode, IdentifierNode, SliceNode,
    AttributionNode, NoneNode, ItemNode, ArgsNode, KwargsNode
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
        self.identifier_nodes = dict()

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
            left = BinaryOpNode(self.op_mgr, operator, left, right)

        return left

    def parse_unary(self) -> ASTNode:
        """解析一元运算符"""
        if self.current_token.type == TokenType.OPERATOR:
            if self.current_token.value not in self.op_mgr.unary_ops:
                raise ValueError(f'Token无法解析为单目运算符：{self.current_token}')
            operator = self.current_token.value
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(self.op_mgr, operator, operand)

        return self.parse_primary()

    def parse_primary(self) -> ASTNode:
        """解析基本表达式"""
        token = self.current_token

        # 数字
        if token.type == TokenType.NUMBER:
            ret = NumberNode(token.value)
            self.advance()
        # 字符串
        elif token.type == TokenType.STRING:
            ret = StringNode(token.value)
            self.advance()
        # 变量/函数调用
        elif token.type == TokenType.IDENTIFIER:
            if token.value not in self.identifier_nodes:
                self.identifier_nodes[token.value] = IdentifierNode(self.func_mgr, token.value)
            ret = self.identifier_nodes[token.value]
            self.advance()
        # 圆括号表达式
        elif token.type == TokenType.LPAREN:
            ret = self.parse_parenthesis()
        # 方括号表达式
        elif token.type == TokenType.LSQUARE:
            ret = self.parse_square()
        else:
            raise ValueError(f'意外的token：{token}')

        while True:
            if self.current_token.type == TokenType.LPAREN:
                ret = self.parse_parenthesis(ret)
            elif self.current_token.type == TokenType.LSQUARE:
                ret = self.parse_square(ret)
            elif self.current_token.type == TokenType.ATTRIBUTION:
                ret = AttributionNode(ret, self.current_token.value[:])
                self.advance()
            elif self.current_token.type in (TokenType.STRING, TokenType.NUMBER, TokenType.IDENTIFIER):
                raise ValueError(f'意外的token：{self.current_token}')
            else:
                break
        return ret

    def parse_parenthesis(self, func: ASTNode=None) -> ASTNode:
        start_position = self.current_token.position
        self.advance()
        # 解析参数列表
        is_func = func is not None
        args, kwargs, extra_comma = ArgsNode([]), KwargsNode({}), False
        if self.current_token.type != TokenType.RPAREN:
            node = self.parse_expression()
            if is_func and isinstance(node, IdentifierNode) and self.current_token.type == TokenType.ASSIGNMENT:
                self.advance()
                kwargs.add(node.name, self.parse_expression())
            else:
                args.append(node)
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.RPAREN:
                    if len(args) + len(kwargs) == 0:
                        raise ValueError(f'意外的token：{self.current_token}')
                    extra_comma = True
                else:
                    node = self.parse_expression()
                    if is_func:
                        if self.current_token.type == TokenType.ASSIGNMENT:
                            if not isinstance(node, IdentifierNode):
                                raise ValueError(f'错误的赋值符号，位置: {self.current_token.position}')
                            self.advance()
                            kwargs.add(node.name, self.parse_expression())
                        else:
                            if kwargs:
                                raise ValueError(f'顺序参数必须在关键字参数前，位置：{self.current_token.position}')
                            args.append(node)
                    else:
                        args.append(node)
        if self.current_token.type != TokenType.RPAREN:
            raise ValueError(f'缺少右圆括号，位置：{start_position}')
        self.advance()
        if is_func:
            return FunctionCallNode(func, args, kwargs)
        else:
            if kwargs:
                raise KeyError(f'元组推导式不支持keyword，位置：{start_position}')
            if len(args) == 1 and not extra_comma:
                return args[0]
            else:
                return args.to_tuple()

    def parse_square(self, slice_obj: ASTNode=None) -> ASTNode:
        self.advance()
        # 解析参数列表
        is_slice = slice_obj is not None
        args, extra_comma = ArgsNode([]), False
        parse_func = self.parse_slice if is_slice else self.parse_expression
        if self.current_token.type != TokenType.RSQUARE:
            args.append(parse_func())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.RSQUARE:
                    if len(args) == 0:
                        raise ValueError(f'意外的token：{self.current_token}')
                    extra_comma = True
                else:
                    args.append(parse_func())
        if self.current_token.type != TokenType.RSQUARE:
            raise ValueError(f'缺少右圆括号，位置：{self.current_token.position}')
        self.advance()
        if is_slice:
            if len(args) == 1 and not extra_comma:
                return ItemNode(slice_obj, args[0])
            else:
                return ItemNode(slice_obj, args.to_tuple())
        else:
            return args.to_list()

    def parse_slice(self):
        cur_position = self.current_token.position
        args, is_slice, colon_cnt = [], False, 0
        while self.current_token.type not in (TokenType.COMMA, TokenType.RSQUARE):
            if self.current_token.type == TokenType.COLON:
                args.append(NoneNode())
                is_slice = True
                colon_cnt += 1
                self.advance()
            else:
                args.append(self.parse_expression())
                if self.current_token.type == TokenType.COLON:
                    is_slice = True
                    colon_cnt += 1
                    self.advance()
        if is_slice:
            if len(args) > 3:
                raise ValueError(f'切片参数个数大于3，位置：{cur_position}')
            if colon_cnt > 2:
                raise ValueError(f'冒号过多，位置：{cur_position}')
            start, end, stop = args + [NoneNode() for _ in range(3-len(args))]
            return SliceNode(start, end, stop)
        else:
            if len(args) != 1:
                raise ValueError(f'切片参数解析失败，位置：{cur_position}')
            return args[0]

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
