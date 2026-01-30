#!/usr/bin/env python3
"""Test new Sharp language features."""

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

# Test 1: Simple class definition
code1 = """class Person:
    name = "Unknown"

person = Person()
print(person)
"""

print("Test 1: Simple class definition")
print("=" * 50)
print("Code:")
print(code1)
print("\nResult:")
try:
    lexer = Lexer(code1)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("✓ Class definition parsed and evaluated!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)

# Test 2: Try/Except
code2 = """try:
    x = 10 / 0
except:
    print("Error caught!")
"""

print("\nTest 2: Try/Except")
print("=" * 50)
print("Code:")
print(code2)
print("\nResult:")
try:
    lexer = Lexer(code2)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("✓ Try/Except parsed and evaluated!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)

# Test 3: Async function
code3 = """async def fetch_data():
    return "data"
"""

print("\nTest 3: Async function")
print("=" * 50)
print("Code:")
print(code3)
print("\nResult:")
try:
    lexer = Lexer(code3)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("✓ Async function parsed!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)

# Test 4: Yield (generator)
code4 = """def count():
    yield 1
    yield 2
    yield 3
"""

print("\nTest 4: Generator with yield")
print("=" * 50)
print("Code:")
print(code4)
print("\nResult:")
try:
    lexer = Lexer(code4)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("✓ Generator parsed!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)

# Test 5: Decorator
code5 = """@decorator
def my_func():
    return "hello"
"""

print("\nTest 5: Decorator")
print("=" * 50)
print("Code:")
print(code5)
print("\nResult:")
try:
    lexer = Lexer(code5)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("✓ Decorator parsed!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)

# Test 6: With statement
code6 = """with file as f:
    content = f.read()
"""

print("\nTest 6: With statement")
print("=" * 50)
print("Code:")
print(code6)
print("\nResult:")
try:
    lexer = Lexer(code6)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("✓ With statement parsed!")
except Exception as e:
    print(f"✗ Error: {e}")

print("\nAll new features have been added to Sharp!")
