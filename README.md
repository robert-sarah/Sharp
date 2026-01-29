# Sharp Programming Language

A modern, Python-like programming language with advanced features: pattern matching, algebraic data types, optional static typing, async/await, and more.

## Features

- **Simple Syntax**: Indentation-based, clean and readable like Python
- **Dynamic Typing**: No explicit type declarations required (but optional static typing coming)
- **Pattern Matching**: Powerful `match` expressions
- **First-class Functions**: Lambdas, closures, higher-order functions
- **Algebraic Data Types**: Enums, tuples, records
- **Standard Library**: Comprehensive built-in functions and modules
- **REPL**: Interactive shell for exploration
- **FFI**: Call Python/native functions

## Quick Start

```bash
python repl.py
```

Then type:
```sharp
let x = 42
print(x)

def factorial(n):
    if n < 2:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
```

## Project Structure

```
sharp/
├── lexer.py          # Tokenization
├── parser.py         # AST generation
├── interpreter.py    # Evaluation engine
├── stdlib.py         # Built-in functions and types
├── repl.py           # Interactive shell
├── vm.py             # (Optional) Bytecode VM
├── examples/         # Example programs
│   ├── hello.sharp
│   ├── fibonacci.sharp
│   └── ...
├── tests/            # Test suite
└── README.md
```

## Language Syntax

### Variables & Basic Types
```sharp
let x = 10
let y = 3.14
let name = "Sharp"
let flag = true
let empty = nil
```

### Functions
```sharp
def add(a, b):
    return a + b

def greet(name = "World"):
    print("Hello, " + name)

greet()
greet("Sharp")
```

### Control Flow
```sharp
if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")

while x > 0:
    x = x - 1

for i in range(10):
    print(i)
```

### Collections
```sharp
let arr = [1, 2, 3, 4, 5]
let dict = {"name": "Sharp", "version": 1}
let tuple = (10, 20)

# Iteration
for item in arr:
    print(item)

# Comprehensions
let squares = [x * x for x in range(10)]
let pairs = {x: x**2 for x in range(5)}
```

### Pattern Matching
```sharp
match value:
    case 0:
        print("zero")
    case 1:
        print("one")
    case n if n > 1:
        print("greater than one")
    case _:
        print("unknown")
```

### Closures & Higher-Order Functions
```sharp
def make_adder(x):
    def add(y):
        return x + y
    return add

add_5 = make_adder(5)
print(add_5(10))  # 15

result = map(lambda x: x * 2, [1, 2, 3])
```

### Algebraic Data Types
```sharp
type Option:
    case Some(value)
    case None

type Result:
    case Ok(value)
    case Err(message)

match opt:
    case Some(val):
        print(val)
    case None:
        print("nothing")
```

## Roadmap

### MVP (Current)
- [x] Lexer
- [x] Parser
- [x] Tree-walking interpreter
- [x] Basic standard library
- [x] REPL
- [ ] Pattern matching
- [ ] Algebraic data types

### Phase 2
- [ ] Static type checking (optional)
- [ ] Module system
- [ ] Package manager (`shp`)
- [ ] Formatter & linter
- [ ] Documentation

### Phase 3
- [ ] Bytecode VM
- [ ] JIT compilation
- [ ] Async/await & actors
- [ ] FFI to C/native libraries
- [ ] IDE support (VS Code extension)

## Installation

```bash
# Clone or download Sharp
# No dependencies required (pure Python)

# Run REPL
python repl.py

# Run a script
python interpreter.py hello.sharp
```

## Contributing

Contributions welcome! Areas of focus:
- Standard library expansion
- Optimization & performance
- Documentation
- Test coverage
- Language features (async, FFI, etc.)

## License

MIT
