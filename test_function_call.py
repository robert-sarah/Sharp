#!/usr/bin/env python3
"""Test why function definition doesn't show output."""

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

# Test case: Function definition without calling it
code1 = """def ie():
    let x = 10
    print('X')
"""

print("Test 1: Define function but don't call it")
print("=" * 50)
print("Code:")
print(code1)
print("\nOutput:")

lexer = Lexer(code1)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
result = interpreter.interpret(ast)

print("(nothing printed)")
print("^ This is correct - the function is defined but never called")

print("\n" + "=" * 50)

# Test case 2: Function definition with function call
code2 = """def ie():
    let x = 10
    print('X')

ie()
"""

print("\nTest 2: Define function AND call it")
print("=" * 50)
print("Code:")
print(code2)
print("\nOutput:")

lexer = Lexer(code2)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
interpreter = Interpreter()
result = interpreter.interpret(ast)

print("\n^ This shows output because we called ie()")
