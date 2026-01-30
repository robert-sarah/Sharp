"""
Lexer for Sharp Programming Language.
Tokenizes Sharp source code into a stream of tokens.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any

class TokenType(Enum):
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()

    # Identifiers & Keywords
    IDENTIFIER = auto()
    DEF = auto()
    LET = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    MATCH = auto()
    CASE = auto()
    LAMBDA = auto()
    TYPE = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    CLASS = auto()
    PASS = auto()
    GLOBAL = auto()
    NONLOCAL = auto()
    ASYNC = auto()
    AWAIT = auto()
    YIELD = auto()
    TRY = auto()
    EXCEPT = auto()
    FINALLY = auto()
    WITH = auto()
    RAISE = auto()
    SELF = auto()
    SUPER = auto()
    INIT = auto()
    STATICMETHOD = auto()
    CLASSMETHOD = auto()
    PROPERTY = auto()
    AT = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    POWER = auto()
    ASSIGN = auto()
    PLUS_ASSIGN = auto()
    MINUS_ASSIGN = auto()
    STAR_ASSIGN = auto()
    SLASH_ASSIGN = auto()

    # Comparison
    EQ = auto()
    NE = auto()
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()

    # Logical
    AND = auto()
    OR = auto()
    NOT = auto()

    # Bitwise
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    LSHIFT = auto()
    RSHIFT = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()
    PIPE = auto()
    QUESTION = auto()

    # Special
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    EOF = auto()
    ERROR = auto()

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}, {self.column})"

class Lexer:
    """Tokenizes Sharp source code."""

    KEYWORDS = {
        'def': TokenType.DEF,
        'let': TokenType.LET,
        'if': TokenType.IF,
        'elif': TokenType.ELIF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'return': TokenType.RETURN,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'match': TokenType.MATCH,
        'case': TokenType.CASE,
        'lambda': TokenType.LAMBDA,
        'type': TokenType.TYPE,
        'import': TokenType.IMPORT,
        'from': TokenType.FROM,
        'as': TokenType.AS,
        'class': TokenType.CLASS,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'nil': TokenType.NIL,
        'pass': TokenType.PASS,
        'global': TokenType.GLOBAL,
        'nonlocal': TokenType.NONLOCAL,
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.NOT,
        'async': TokenType.ASYNC,
        'await': TokenType.AWAIT,
        'yield': TokenType.YIELD,
        'try': TokenType.TRY,
        'except': TokenType.EXCEPT,
        'finally': TokenType.FINALLY,
        'with': TokenType.WITH,
        'raise': TokenType.RAISE,
        'self': TokenType.SELF,
        'super': TokenType.SUPER,
        '__init__': TokenType.INIT,
        'staticmethod': TokenType.STATICMETHOD,
        'classmethod': TokenType.CLASSMETHOD,
        'property': TokenType.PROPERTY,
    }

    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]

    def error(self, message: str):
        token = Token(TokenType.ERROR, message, self.line, self.column)
        self.tokens.append(token)

    def current_char(self) -> Optional[str]:
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek_char(self, offset: int = 1) -> Optional[str]:
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def advance(self) -> Optional[str]:
        char = self.current_char()
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
        return char

    def skip_whitespace(self) -> int:
        """Skip spaces and tabs, return indentation level."""
        indent = 0
        while self.current_char() in ' \t':
            if self.current_char() == ' ':
                indent += 1
            else:  # tab
                indent += 4
            self.advance()
        return indent

    def skip_comment(self):
        """Skip comments."""
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()

    def read_string(self, quote: str) -> str:
        """Read a string literal."""
        value = ""
        self.advance()  # Skip opening quote
        
        while self.current_char() and self.current_char() != quote:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    value += '\n'
                elif escape_char == 't':
                    value += '\t'
                elif escape_char == 'r':
                    value += '\r'
                elif escape_char == '\\':
                    value += '\\'
                elif escape_char == quote:
                    value += quote
                else:
                    value += escape_char
                self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if self.current_char() == quote:
            self.advance()  # Skip closing quote
        else:
            self.error(f"Unterminated string at line {self.line}")
        
        return value

    def read_number(self) -> Token:
        """Read a number (integer or float)."""
        start_line = self.line
        start_column = self.column
        num_str = ""
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            num_str += self.current_char()
            self.advance()
        
        # Handle scientific notation
        if self.current_char() in 'eE':
            num_str += self.current_char()
            self.advance()
            if self.current_char() in '+-':
                num_str += self.current_char()
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()
        
        if '.' in num_str or 'e' in num_str.lower():
            return Token(TokenType.FLOAT, float(num_str), start_line, start_column)
        else:
            return Token(TokenType.INTEGER, int(num_str), start_line, start_column)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_line = self.line
        start_column = self.column
        identifier = ""
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() in '_'):
            identifier += self.current_char()
            self.advance()
        
        token_type = self.KEYWORDS.get(identifier, TokenType.IDENTIFIER)
        value = True if token_type == TokenType.TRUE else (
            False if token_type == TokenType.FALSE else (
                None if token_type == TokenType.NIL else identifier
            )
        )
        
        return Token(token_type, value, start_line, start_column)

    def tokenize(self) -> List[Token]:
        """Tokenize the source code."""
        # First pass: tokenize without indentation tracking
        lines = self.source.split('\n')
        indent_stack = [0]
        
        for line_num, line in enumerate(lines, 1):
            # Count leading spaces
            indent = len(line) - len(line.lstrip(' \t'))
            indent_chars = line[:indent]
            for ch in indent_chars:
                if ch == '\t':
                    indent = indent - 1 + 4  # Convert tabs to 4 spaces
            
            # Skip empty and comment-only lines
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Process indentation
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                self.tokens.append(Token(TokenType.INDENT, None, line_num, indent + 1))
            elif indent < indent_stack[-1]:
                while indent_stack and indent < indent_stack[-1]:
                    indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, None, line_num, 1))
            
            # Tokenize line content
            pos = 0
            while pos < len(line):
                # Skip whitespace
                while pos < len(line) and line[pos] in ' \t':
                    pos += 1
                
                if pos >= len(line):
                    break
                
                # Comment
                if line[pos] == '#':
                    break
                
                # String
                if line[pos] in '"\'':
                    quote = line[pos]
                    pos += 1
                    start_pos = pos
                    string_val = ""
                    while pos < len(line):
                        if line[pos] == '\\':
                            pos += 1
                            if pos < len(line):
                                escape_char = line[pos]
                                if escape_char == 'n':
                                    string_val += '\n'
                                elif escape_char == 't':
                                    string_val += '\t'
                                elif escape_char == '\\':
                                    string_val += '\\'
                                elif escape_char == quote:
                                    string_val += quote
                                else:
                                    string_val += escape_char
                                pos += 1
                        elif line[pos] == quote:
                            pos += 1
                            break
                        else:
                            string_val += line[pos]
                            pos += 1
                    self.tokens.append(Token(TokenType.STRING, string_val, line_num, start_pos))
                    continue
                
                # Number
                if line[pos].isdigit():
                    start_pos = pos
                    num_str = ""
                    while pos < len(line) and (line[pos].isdigit() or line[pos] == '.'):
                        num_str += line[pos]
                        pos += 1
                    if '.' in num_str:
                        self.tokens.append(Token(TokenType.FLOAT, float(num_str), line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.INTEGER, int(num_str), line_num, start_pos))
                    continue
                
                # Identifier or keyword
                if line[pos].isalpha() or line[pos] == '_':
                    start_pos = pos
                    ident = ""
                    while pos < len(line) and (line[pos].isalnum() or line[pos] == '_'):
                        ident += line[pos]
                        pos += 1
                    
                    if ident in self.KEYWORDS:
                        token_type = self.KEYWORDS[ident]
                        if token_type == TokenType.TRUE:
                            self.tokens.append(Token(token_type, True, line_num, start_pos))
                        elif token_type == TokenType.FALSE:
                            self.tokens.append(Token(token_type, False, line_num, start_pos))
                        elif token_type == TokenType.NIL:
                            self.tokens.append(Token(token_type, None, line_num, start_pos))
                        else:
                            self.tokens.append(Token(token_type, ident, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.IDENTIFIER, ident, line_num, start_pos))
                    continue
                
                # Operators and delimiters
                start_pos = pos
                ch = line[pos]
                
                if ch == '+':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.PLUS_ASSIGN, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.PLUS, None, line_num, start_pos))
                elif ch == '-':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.MINUS_ASSIGN, None, line_num, start_pos))
                    elif pos < len(line) and line[pos] == '>':
                        pos += 1
                        self.tokens.append(Token(TokenType.ARROW, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.MINUS, None, line_num, start_pos))
                elif ch == '*':
                    pos += 1
                    if pos < len(line) and line[pos] == '*':
                        pos += 1
                        self.tokens.append(Token(TokenType.POWER, None, line_num, start_pos))
                    elif pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.STAR_ASSIGN, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.STAR, None, line_num, start_pos))
                elif ch == '/':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.SLASH_ASSIGN, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.SLASH, None, line_num, start_pos))
                elif ch == '%':
                    pos += 1
                    self.tokens.append(Token(TokenType.PERCENT, None, line_num, start_pos))
                elif ch == '=':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.EQ, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.ASSIGN, None, line_num, start_pos))
                elif ch == '!':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.NE, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.NOT, None, line_num, start_pos))
                elif ch == '<':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.LE, None, line_num, start_pos))
                    elif pos < len(line) and line[pos] == '<':
                        pos += 1
                        self.tokens.append(Token(TokenType.LSHIFT, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.LT, None, line_num, start_pos))
                elif ch == '>':
                    pos += 1
                    if pos < len(line) and line[pos] == '=':
                        pos += 1
                        self.tokens.append(Token(TokenType.GE, None, line_num, start_pos))
                    elif pos < len(line) and line[pos] == '>':
                        pos += 1
                        self.tokens.append(Token(TokenType.RSHIFT, None, line_num, start_pos))
                    else:
                        self.tokens.append(Token(TokenType.GT, None, line_num, start_pos))
                elif ch == '(':
                    pos += 1
                    self.tokens.append(Token(TokenType.LPAREN, None, line_num, start_pos))
                elif ch == ')':
                    pos += 1
                    self.tokens.append(Token(TokenType.RPAREN, None, line_num, start_pos))
                elif ch == '[':
                    pos += 1
                    self.tokens.append(Token(TokenType.LBRACKET, None, line_num, start_pos))
                elif ch == ']':
                    pos += 1
                    self.tokens.append(Token(TokenType.RBRACKET, None, line_num, start_pos))
                elif ch == '{':
                    pos += 1
                    self.tokens.append(Token(TokenType.LBRACE, None, line_num, start_pos))
                elif ch == '}':
                    pos += 1
                    self.tokens.append(Token(TokenType.RBRACE, None, line_num, start_pos))
                elif ch == ',':
                    pos += 1
                    self.tokens.append(Token(TokenType.COMMA, None, line_num, start_pos))
                elif ch == '.':
                    pos += 1
                    self.tokens.append(Token(TokenType.DOT, None, line_num, start_pos))
                elif ch == ':':
                    pos += 1
                    self.tokens.append(Token(TokenType.COLON, None, line_num, start_pos))
                elif ch == ';':
                    pos += 1
                    self.tokens.append(Token(TokenType.SEMICOLON, None, line_num, start_pos))
                elif ch == '|':
                    pos += 1
                    self.tokens.append(Token(TokenType.PIPE, None, line_num, start_pos))
                elif ch == '&':
                    pos += 1
                    self.tokens.append(Token(TokenType.BIT_AND, None, line_num, start_pos))
                elif ch == '^':
                    pos += 1
                    self.tokens.append(Token(TokenType.BIT_XOR, None, line_num, start_pos))
                elif ch == '~':
                    pos += 1
                    self.tokens.append(Token(TokenType.BIT_NOT, None, line_num, start_pos))
                elif ch == '?':
                    pos += 1
                    self.tokens.append(Token(TokenType.QUESTION, None, line_num, start_pos))
                elif ch == '@':
                    pos += 1
                    self.tokens.append(Token(TokenType.AT, None, line_num, start_pos))
                else:
                    self.error(f"Unexpected character '{ch}' at line {line_num}")
                    pos += 1
            
            # Add newline after line (if not last line)
            if line_num < len(lines) and self.tokens and self.tokens[-1].type not in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
                self.tokens.append(Token(TokenType.NEWLINE, None, line_num, len(line)))
        
        # Add final dedents
        while len(indent_stack) > 1:
            indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, None, len(lines), 1))
        
        self.tokens.append(Token(TokenType.EOF, None, len(lines), 1))
        return self.tokens
