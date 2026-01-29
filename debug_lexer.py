"""Debug lexer output"""
from lexer import Lexer

source = """def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

lexer = Lexer(source)
tokens = lexer.tokenize()

for token in tokens:
    print(token)
