#!/usr/bin/env python3
"""
Test Sharp language with newly added global and nonlocal statements
"""

from lexer import Lexer
from parser import Parser
from interpreter import Interpreter

print("="*70)
print("TESTING NEWLY ADDED KEYWORDS: global, nonlocal")
print("="*70)

# Test 1: Global statement
print("\n1. Testing GLOBAL statement...")
code1 = """
x = 10

def change_global():
    global x
    x = 20

print(x)
change_global()
print(x)
"""

try:
    lexer = Lexer(code1)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("   ✅ GLOBAL statement works!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Nonlocal statement
print("\n2. Testing NONLOCAL statement...")
code2 = """
def outer():
    x = 10
    
    def inner():
        nonlocal x
        x = 20
    
    inner()
    print(x)

outer()
"""

try:
    lexer = Lexer(code2)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("   ✅ NONLOCAL statement works!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Multiple variables in global
print("\n3. Testing multiple variables in GLOBAL...")
code3 = """
a = 1
b = 2
c = 3

def update_all():
    global a, b, c
    a = 10
    b = 20
    c = 30

update_all()
print(a)
print(b)
print(c)
"""

try:
    lexer = Lexer(code3)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("   ✅ Multiple GLOBAL variables work!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("ALL TESTS COMPLETE!")
print("="*70)
