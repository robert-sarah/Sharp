# Sharp Programming Language

A modern, Python-like programming language with **advanced features**: pattern matching, algebraic data types, classes & OOP, decorators, async/await, generators, and more.

---

## 🚀 What's New (2026 - MAJOR UPDATE)

### 🔥 **New Language Features**
- **Classes & Object-Oriented Programming**: Full OOP support with inheritance, methods, constructors
- **Decorators**: Function and class decorators with chaining
- **Complete Exception Handling**: try/except/else/finally with exception chaining
- **Generators**: `yield` for lazy evaluation
- **Async/Await**: Asynchronous programming with `async`/`await`
- **Context Managers**: `with` statements for resource management
- **Type Annotations**: Optional type hints (syntax ready, validation coming)
- **Raise Statements**: Custom exception throwing

### 🎨 **IDE Improvements**
- **Multi-tab Editor**: Edit multiple files simultaneously
- **Line Numbers**: Professional margin with synchronized scrolling
- **File Explorer**: Browse and open project files
- **Code Outline**: View function/variable structure
- **Output Panel**: Console, errors, and warnings tabs
- **Find & Replace**: Ctrl+F and Ctrl+H shortcuts
- **Intelligent Autocompletion**: Context-aware like Python/VSCode
- **Sharp Logo**: Professional branding (SVG gradient design)
- **Dark Theme**: PyCharm-like styling

### 📚 **Core Features**
- **Simple Syntax**: Indentation-based, clean and readable like Python
- **Pattern Matching**: Powerful `match` expressions
- **First-class Functions**: Lambdas, closures, higher-order functions
- **Standard Library**: 140+ built-in functions
- **Module System**: 40+ modules (math, string, collections, file, network, PyQt5, etc.)
- **GUI Support**: PyQt5 and wxPython wrappers
- **REPL**: Interactive shell

---

## 📊 Feature Comparison

| Feature | Sharp | Python | JavaScript |
|---------|-------|--------|------------|
| Classes | ✅ | ✅ | ✅ |
| Decorators | ✅ | ✅ | ✅ |
| Generators | ✅ | ✅ | ✅ |
| Async/Await | ✅ | ✅ | ✅ |
| Pattern Matching | ✅ | ✅ | ❌ |
| Simple Syntax | ✅ | ✅ | ❌ |
| Type Hints | ⚠️  | ✅ | ✅ |
| GUI (built-in) | ✅ | ❌ | ❌ |

---

## Quick Start

```bash
python gui.py   # Launch the Sharp IDE (recommended)
# or
python repl.py  # Command-line REPL
```

### Example: Hello World
```sharp
print("Hello, Sharp!")
```

### Example: Classes
```sharp
class Person:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return "Hello, " + self.name

alice = Person("Alice")
print(alice.greet())  # Hello, Alice
```

### Example: Exception Handling
```sharp
try:
    result = 10 / 0
except:
    print("Error caught!")
finally:
    print("Done!")
```

### Example: Generators
```sharp
def count_up(n):
    for i in range(n):
        yield i

for num in count_up(5):
    print(num)  # 0, 1, 2, 3, 4
```

### Example: PyQt5 GUI
```sharp
import pyqt5_wrapper as gui
````
win = gui.SharpWindow("Hello GUI")
win.add_label("Welcome to Sharp GUI!")
win.show()
```

If you see a message about PyQt5 missing, install it with:
```bash
pip install PyQt5
```

---

## Project Structure

```
sharp/
├── lexer.py          # Tokenization
├── parser.py         # AST generation
├── interpreter.py    # Evaluation engine
├── stdlib.py         # Built-in functions and types
├── gui.py            # Full-featured IDE (Tkinter)
├── repl.py           # Interactive shell
├── modules/          # 40+ modules (math, string, gui, ...)
├── examples/         # Example programs
│   ├── hello.sharp
│   ├── gui_demo.sharp
│   └── ...
└── README.md
```

---

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

---

## Installation

```bash
# Clone or download Sharp
# No dependencies required (pure Python, except for GUI: PyQt5/wxPython if you want GUI apps)

# Run IDE
python gui.py

# Run REPL
python repl.py

# Run a script
python interpreter.py hello.sharp
```

---

## Contributing

Contributions welcome! Areas of focus:
- Standard library expansion
- Optimization & performance
- Documentation
- Test coverage
- Language features (async, FFI, etc.)

## License

MIT
