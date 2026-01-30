#!/usr/bin/env python3
"""Test parser error messages."""

from lexer import Lexer
from parser import Parser

# Test case 1: Incomplete function definition
code1 = """def ie
let x = 10
print('X')
"""

print("Test 1: Incomplete function definition 'def ie'")
print("=" * 50)
try:
    lexer = Lexer(code1)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("ERROR: Should have failed!")
except Exception as e:
    print(f"✓ Got expected error:\n  {e}")

print("\n" + "=" * 50)

# Test case 2: Correct function definition
code2 = """def ie():
    let x = 10
    print(x)
"""

print("\nTest 2: Correct function definition")
print("=" * 50)
try:
    lexer = Lexer(code2)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("✓ Parse successful!")
except Exception as e:
    print(f"ERROR: {e}")

# Test case 3: Function with parameters
code3 = """def add(a, b):
    return a + b
"""

print("\nTest 3: Function with parameters")
print("=" * 50)
try:
    lexer = Lexer(code3)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("✓ Parse successful!")
except Exception as e:
    print(f"ERROR: {e}")

# Test case 4: Missing colon
code4 = """def test()
    let x = 5
"""

print("\nTest 4: Missing colon after function definition")
print("=" * 50)
try:
    lexer = Lexer(code4)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    print("ERROR: Should have failed!")
except Exception as e:
    print(f"✓ Got expected error:\n  {e}")
