"""词法分析器"""
import re
from enum import Enum
from typing import List, Any
from dataclasses import dataclass
from formulaparser.op_manager import OperatorManager


# Token类型枚举
class TokenType(Enum):
    """Token类型枚举"""
    NUMBER = 'NUMBER'           # 数字
    STRING = 'STRING'           # 字符串
    OPERATOR = 'OPERATOR'       # 运算符
    IDENTIFIER = 'IDENTIFIER'   # 标识符（变量名或函数名）
    LPAREN = 'LPAREN'           # 左圆括号
    RPAREN = 'RPAREN'           # 右圆括号
    LSQUARE = 'LSQUARE'         # 左方括号
    RSQUARE = 'RSQUARE'         # 右方括号
    ATTRIBUTION = 'ATTRIBUTION' # 属性
    ASSIGNMENT = 'ASSIGNMENT'   # keyword参数
    COLON = 'COLON'             # 切片
    COMMA = 'COMMA'             # 逗号
    EOF = 'EOF'                 # 结束符


@dataclass
class Token:
    """Token数据类"""
    type: TokenType
    value: Any
    position: int


class Lexer:
    """词法分析器"""

    def __init__(self, op_mgr: OperatorManager, text: str):
        self.text = text
        self.op_mgr = op_mgr
        self.position = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        """前进一个字符"""
        self.position += 1
        if self.position < len(self.text):
            self.current_char = self.text[self.position]
        else:
            self.current_char = None

    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char and self.current_char == ' ':
            self.advance()

    def read_number(self) -> Token:
        """读取数字"""
        start_pos = self.position

        chars = re.match(r'^((\d+(\.\d+)?[eE][+\-]?\d+)|(\d+(\.\d+)?))', self.text[self.position:]).group(0)
        if re.match(r'^\d+$', chars):
            value = int(chars)
        else:
            value = float(chars)

        for _ in chars:
            self.advance()

        return Token(TokenType.NUMBER, value, start_pos)

    def read_string(self) -> Token:
        """读取字符串（双引号包围）"""
        start_pos = self.position
        self.advance()  # 跳过开始的引号

        string_value = ""
        while self.current_char and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    string_value += '\n'
                elif self.current_char == 't':
                    string_value += '\t'
                elif self.current_char == '"':
                    string_value += '"'
                elif self.current_char == '\\':
                    string_value += '\\'
                else:
                    raise ValueError(f'不支持的转义符"\\{self.current_char}"，位置：{self.position-1}')
            else:
                string_value += self.current_char
            self.advance()

        if self.current_char == '"':
            self.advance()  # 跳过结束的引号
        else:
            raise ValueError(f'未闭合的字符串，位置：{start_pos}')

        return Token(TokenType.STRING, string_value, start_pos)

    def read_operator(self) -> Token:
        start_pos = self.position
        for op in sorted(self.op_mgr.binary_ops | self.op_mgr.unary_ops, reverse=True):
            if op == self.text[self.position:self.position+len(op)]:
                for _ in range(len(op)):
                    self.advance()
                return Token(TokenType.OPERATOR, op, start_pos)
        if self.current_char == '=':
            self.advance()
            return Token(TokenType.ASSIGNMENT, '=', start_pos)
        raise ValueError(f'不支持的运算符，位置：{start_pos}')

    def read_identifier(self) -> Token:
        """读取标识符（变量名或函数名）

        标识符由字母、数字、下划线组成，必须以字母或下划线开头
        """
        start_pos = self.position

        identifier = re.match('^[a-zA-Z_]([a-zA-Z0-9_]+)?', self.text[start_pos:]).group(0)

        for _ in identifier:
            self.advance()

        return Token(TokenType.IDENTIFIER, identifier, start_pos)

    def read_attribution(self) -> Token:
        start_pos = self.position

        attributions = re.match(r'^(\.[a-zA-Z_]([a-zA-Z0-9_]+)?)+', self.text[start_pos:]).group(0)

        for _ in attributions:
            self.advance()

        return Token(TokenType.ATTRIBUTION, attributions.split('.')[1:], start_pos)


    def tokenize(self) -> List[Token]:
        """将文本转换为token列表"""
        tokens = []

        while self.current_char:
            # 跳过空白
            if self.current_char == ' ':
                self.skip_whitespace()
                continue

            # 数字
            if re.match(r'\d', self.current_char):
                tokens.append(self.read_number())
                continue

            # 字符串
            if self.current_char == '"':
                tokens.append(self.read_string())
                continue

            # 标识符（变量名或函数名）
            if re.match(r'[a-zA-Z_]', self.current_char):
                tokens.append(self.read_identifier())
                continue

            # 属性
            if self.current_char == '.':
                tokens.append(self.read_attribution())
                continue

            # 运算符
            if self.current_char in self.op_mgr.AVAILABLE_CHARS:
                tokens.append(self.read_operator())
                continue

            # 括号
            if self.current_char == '(':
                tokens.append(Token(TokenType.LPAREN, '(', self.position))
                self.advance()
                continue

            if self.current_char == ')':
                tokens.append(Token(TokenType.RPAREN, ')', self.position))
                self.advance()
                continue

            if self.current_char == '[':
                tokens.append(Token(TokenType.LSQUARE, '[', self.position))
                self.advance()
                continue

            if self.current_char == ']':
                tokens.append(Token(TokenType.RSQUARE, ']', self.position))
                self.advance()
                continue

            # 逗号
            if self.current_char == ',':
                tokens.append(Token(TokenType.COMMA, ',', self.position))
                self.advance()
                continue

            if self.current_char == ':':
                tokens.append(Token(TokenType.COLON, ':', self.position))
                self.advance()
                continue

            raise ValueError(f'未知字符："{self.current_char}"，位置：{self.position}')

        tokens.append(Token(TokenType.EOF, None, self.position))
        return tokens
