"""
Interactive REPL (Read-Eval-Print-Loop) for Sharp Programming Language.
"""

import sys
import traceback
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from stdlib import SharpNil

def format_value(value):
    """Format value for display."""
    if isinstance(value, SharpNil):
        return "nil"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        return repr(value)
    elif isinstance(value, float):
        # Format float nicely
        if value == int(value):
            return str(int(value)) + ".0"
        return str(value)
    elif isinstance(value, list):
        return "[" + ", ".join(format_value(v) for v in value) + "]"
    elif isinstance(value, dict):
        items = ", ".join(f"{format_value(k)}: {format_value(v)}" for k, v in value.items())
        return "{" + items + "}"
    elif isinstance(value, tuple):
        if len(value) == 1:
            return "(" + format_value(value[0]) + ",)"
        return "(" + ", ".join(format_value(v) for v in value) + ")"
    else:
        return repr(value)

def run_repl():
    """Run the REPL."""
    print("Sharp Programming Language - Interactive REPL")
    print('Type "exit()" or press Ctrl+D to quit')
    print()
    
    interpreter = Interpreter()
    
    while True:
        try:
            # Read
            prompt = ">>> "
            line = input(prompt)
            
            # Handle multiline input
            while line.endswith("\\"):
                line = line[:-1] + input("... ")
            
            # Empty line
            if not line.strip():
                continue
            
            # Exit
            if line.strip() in ("exit()", "quit()"):
                break
            
            # Lex
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            # Check for errors
            if any(t.type.name == 'ERROR' for t in tokens):
                for token in tokens:
                    if token.type.name == 'ERROR':
                        print(f"Lexer error: {token.value}")
                continue
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Evaluate
            result = interpreter.interpret(ast)
            
            # Print (if not nil)
            if not isinstance(result, SharpNil):
                print(format_value(result))
        
        except KeyboardInterrupt:
            print()
            print("KeyboardInterrupt")
        except EOFError:
            print()
            break
        except SyntaxError as e:
            print(f"SyntaxError: {e}")
        except NameError as e:
            print(f"NameError: {e}")
        except TypeError as e:
            print(f"TypeError: {e}")
        except ZeroDivisionError:
            print("ZeroDivisionError: division by zero")
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
            # Uncomment for full traceback:
            # traceback.print_exc()

def run_file(filename: str):
    """Run a Sharp program file."""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        
        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Check for errors
        for token in tokens:
            if token.type.name == 'ERROR':
                print(f"Lexer error at line {token.line}: {token.value}")
                sys.exit(1)
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.interpret(ast)
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run file
        run_file(sys.argv[1])
    else:
        # Run REPL
        run_repl()
