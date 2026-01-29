"""
Extended Standard Library for Sharp Programming Language.
Includes GUI, networking, file I/O, math, strings, and more.
Complete implementation with all required functions.
"""

import sys
import os
import json
import math
import random
import time
import socket
import threading
from typing import Any, List, Dict, Callable
from datetime import datetime, timedelta

# ==================== Core Value Types ====================

class SharpValue:
    """Base class for Sharp runtime values."""
    pass

class SharpModule(SharpValue):
    """Sharp module object."""
    def __init__(self, name: str, exports: Dict[str, Any]):
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'exports', exports)
    
    def __getattr__(self, name: str):
        exports = object.__getattribute__(self, 'exports')
        module_name = object.__getattribute__(self, 'name')
        if name in exports:
            return exports[name]
        raise AttributeError(f"Module '{module_name}' has no attribute '{name}'")
    
    def __repr__(self):
        name = object.__getattribute__(self, 'name')
        return f"<module '{name}'"

class SharpFunction(SharpValue):
    """Sharp user-defined function."""
    def __init__(self, name: str, params: List[str], defaults: List, body, closure):
        self.name = name
        self.params = params
        self.defaults = defaults
        self.body = body
        self.closure = closure
    
    def __repr__(self):
        return f"<function {self.name}>"

class SharpBuiltin(SharpValue):
    """Built-in Sharp function."""
    def __init__(self, name: str, func: Callable):
        self.name = name
        self.func = func
    
    def __repr__(self):
        return f"<builtin {self.name}>"

class SharpType(SharpValue):
    """Sharp type (algebraic data type)."""
    def __init__(self, name: str, variants: Dict):
        self.name = name
        self.variants = variants
    
    def __repr__(self):
        return f"<type {self.name}>"

class SharpVariant(SharpValue):
    """Instance of a variant type."""
    def __init__(self, name: str, fields: Dict):
        self.name = name
        self.fields = fields
    
    def __repr__(self):
        if self.fields:
            fields_str = ", ".join(f"{k}={v}" for k, v in self.fields.items())
            return f"{self.name}({fields_str})"
        return self.name

class SharpNil(SharpValue):
    """Sharp nil/null value."""
    def __repr__(self):
        return "nil"

class SharpModule(SharpValue):
    """Sharp module object."""
    def __init__(self, name: str, exports: Dict):
        self.name = name
        self.exports = exports
    
    def __repr__(self):
        return f"<module {self.name}>"

# ==================== Exceptions ====================

class ReturnValue(Exception):
    """Exception to signal return from function."""
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    """Exception to signal break from loop."""
    pass

class ContinueException(Exception):
    """Exception to signal continue in loop."""
    pass

# ==================== I/O Functions ====================

def builtin_print(*args):
    """Print function."""
    print(" ".join(str(arg) for arg in args))
    return SharpNil()

def builtin_input(prompt=""):
    """Read input from user."""
    try:
        return input(str(prompt))
    except EOFError:
        return ""

def builtin_open(filename, mode="r"):
    """Open file. Returns file object."""
    return open(filename, mode)

def builtin_read(file_obj):
    """Read file content."""
    if hasattr(file_obj, 'read'):
        return file_obj.read()
    raise TypeError("Expected file object")

def builtin_write(file_obj, content):
    """Write to file."""
    if hasattr(file_obj, 'write'):
        file_obj.write(str(content))
        return len(str(content))
    raise TypeError("Expected file object")

def builtin_close(file_obj):
    """Close file."""
    if hasattr(file_obj, 'close'):
        file_obj.close()
    return SharpNil()

def builtin_exists(path):
    """Check if file/directory exists."""
    return os.path.exists(path)

def builtin_mkdir(path):
    """Create directory."""
    os.makedirs(path, exist_ok=True)
    return SharpNil()

def builtin_listdir(path="."):
    """List files in directory."""
    return os.listdir(path)

def builtin_remove(path):
    """Delete file."""
    os.remove(path)
    return SharpNil()

def builtin_rmdir(path):
    """Remove directory."""
    os.rmdir(path)
    return SharpNil()

def builtin_getcwd():
    """Get current working directory."""
    return os.getcwd()

def builtin_chdir(path):
    """Change directory."""
    os.chdir(path)
    return SharpNil()

# ==================== Type Conversion & Core Functions ====================

def builtin_len(obj):
    """Length function."""
    if isinstance(obj, (list, str, dict, tuple)):
        return len(obj)
    raise TypeError(f"object of type '{type(obj).__name__}' has no len()")

def builtin_str(obj):
    """Convert to string."""
    if isinstance(obj, SharpNil):
        return "nil"
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, SharpValue):
        return repr(obj)
    return str(obj)

def builtin_int(obj):
    """Convert to integer."""
    if isinstance(obj, int):
        return obj
    elif isinstance(obj, float):
        return int(obj)
    elif isinstance(obj, str):
        return int(obj)
    elif isinstance(obj, bool):
        return 1 if obj else 0
    else:
        raise TypeError(f"int() argument must be a string or a number")

def builtin_float(obj):
    """Convert to float."""
    if isinstance(obj, float):
        return obj
    elif isinstance(obj, int):
        return float(obj)
    elif isinstance(obj, str):
        return float(obj)
    else:
        raise TypeError(f"float() argument must be a string or a number")

def builtin_bool(obj):
    """Convert to boolean."""
    if isinstance(obj, SharpNil):
        return False
    elif isinstance(obj, bool):
        return obj
    elif isinstance(obj, (int, float)):
        return obj != 0
    elif isinstance(obj, str):
        return len(obj) > 0
    elif isinstance(obj, (list, dict, tuple)):
        return len(obj) > 0
    else:
        return True

def builtin_list(obj=None):
    """Convert to list."""
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj[:]
    elif isinstance(obj, str):
        return list(obj)
    elif isinstance(obj, dict):
        return list(obj.values())
    else:
        return list(obj)

def builtin_dict(*args, **kwargs):
    """Create dictionary."""
    if args:
        return dict(args[0])
    return kwargs or {}

def builtin_type(obj):
    """Get type of object."""
    if isinstance(obj, SharpNil):
        return "nil"
    elif isinstance(obj, bool):
        return "bool"
    elif isinstance(obj, int):
        return "int"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, str):
        return "str"
    elif isinstance(obj, list):
        return "list"
    elif isinstance(obj, dict):
        return "dict"
    elif isinstance(obj, tuple):
        return "tuple"
    elif isinstance(obj, SharpFunction):
        return "function"
    else:
        return type(obj).__name__

def builtin_isinstance(obj, classinfo):
    """Check if object is instance of class."""
    return isinstance(obj, classinfo)

def builtin_exit(code=0):
    """Exit program."""
    sys.exit(code)

# ==================== String Functions ====================

def builtin_upper(s):
    """Convert string to uppercase."""
    return str(s).upper()

def builtin_lower(s):
    """Convert string to lowercase."""
    return str(s).lower()

def builtin_strip(s):
    """Strip whitespace from string."""
    return str(s).strip()

def builtin_split(s, sep=None):
    """Split string."""
    return str(s).split(sep)

def builtin_join(sep, iterable):
    """Join iterable with separator."""
    return str(sep).join(str(x) for x in iterable)

def builtin_replace(s, old, new):
    """Replace substring."""
    return str(s).replace(old, new)

def builtin_find(s, substring):
    """Find substring index."""
    return str(s).find(substring)

def builtin_startswith(s, prefix):
    """Check if string starts with prefix."""
    return str(s).startswith(prefix)

def builtin_endswith(s, suffix):
    """Check if string ends with suffix."""
    return str(s).endswith(suffix)

def builtin_contains(obj, item):
    """Check if item in collection."""
    return item in obj

def builtin_format(format_str, *args):
    """Format string."""
    return format_str % args if args else format_str

def builtin_ord(char):
    """Get character code."""
    return ord(str(char)[0])

def builtin_chr(code):
    """Get character from code."""
    return chr(int(code))

# ==================== Collection Functions ====================

def builtin_range(*args):
    """Range function."""
    if len(args) == 1:
        return list(range(int(args[0])))
    elif len(args) == 2:
        return list(range(int(args[0]), int(args[1])))
    elif len(args) == 3:
        return list(range(int(args[0]), int(args[1]), int(args[2])))
    else:
        raise TypeError(f"range expected 1-3 arguments")

def builtin_enumerate(iterable, start=0):
    """Enumerate iterable."""
    return list(enumerate(iterable, start))

def builtin_zip(*iterables):
    """Zip iterables."""
    return list(zip(*iterables))

def builtin_sorted(iterable, reverse=False):
    """Sorted list."""
    return sorted(iterable, reverse=reverse)

def builtin_reversed(iterable):
    """Reversed list."""
    return list(reversed(iterable))

def builtin_min(*args):
    """Minimum value."""
    if not args:
        raise ValueError("min expected at least 1 argument")
    return min(args)

def builtin_max(*args):
    """Maximum value."""
    if not args:
        raise ValueError("max expected at least 1 argument")
    return max(args)

def builtin_sum(iterable, start=0):
    """Sum of iterable."""
    return sum(iterable, start)

def builtin_any(iterable):
    """Check if any element is true."""
    return any(iterable)

def builtin_all(iterable):
    """Check if all elements are true."""
    return all(iterable)

def builtin_filter(func, iterable):
    """Filter iterable."""
    if func is None:
        return [x for x in iterable if x]
    return [x for x in iterable if func(x)]

def builtin_map(func, *iterables):
    """Map function over iterables."""
    if not iterables:
        raise TypeError("map() must have at least two arguments.")
    return list(map(func, *iterables))

# ==================== Math Functions ====================

def builtin_abs(x):
    """Absolute value."""
    return abs(x)

def builtin_round(number, ndigits=0):
    """Round number."""
    return round(number, ndigits)

def builtin_pow(x, y, z=None):
    """Power function."""
    if z is None:
        return x ** y
    return pow(x, y, z)

def builtin_sqrt(x):
    """Square root."""
    return math.sqrt(x)

def builtin_sin(x):
    """Sine (radians)."""
    return math.sin(x)

def builtin_cos(x):
    """Cosine (radians)."""
    return math.cos(x)

def builtin_tan(x):
    """Tangent (radians)."""
    return math.tan(x)

def builtin_log(x, base=math.e):
    """Logarithm."""
    return math.log(x, base)

def builtin_log10(x):
    """Base-10 logarithm."""
    return math.log10(x)

def builtin_exp(x):
    """Exponential."""
    return math.exp(x)

def builtin_floor(x):
    """Floor function."""
    return math.floor(x)

def builtin_ceil(x):
    """Ceiling function."""
    return math.ceil(x)

def builtin_degrees(x):
    """Convert radians to degrees."""
    return math.degrees(x)

def builtin_radians(x):
    """Convert degrees to radians."""
    return math.radians(x)

# ==================== Random Functions ====================

def builtin_random():
    """Random float between 0 and 1."""
    return random.random()

def builtin_randint(a, b):
    """Random integer between a and b (inclusive)."""
    return random.randint(a, b)

def builtin_choice(seq):
    """Random choice from sequence."""
    return random.choice(seq)

def builtin_shuffle(lst):
    """Shuffle list in place."""
    random.shuffle(lst)
    return SharpNil()

def builtin_sample(population, k):
    """Random sample from population."""
    return random.sample(population, k)

# ==================== JSON Functions ====================

def builtin_json_dumps(obj):
    """Serialize to JSON string."""
    def convert(o):
        if isinstance(o, SharpNil):
            return None
        elif isinstance(o, bool):
            return o
        elif isinstance(o, (int, float, str)):
            return o
        elif isinstance(o, list):
            return [convert(x) for x in o]
        elif isinstance(o, dict):
            return {k: convert(v) for k, v in o.items()}
        else:
            return str(o)
    
    return json.dumps(convert(obj))

def builtin_json_loads(s):
    """Deserialize from JSON string."""
    data = json.loads(s)
    
    def convert_none(o):
        if o is None:
            return SharpNil()
        elif isinstance(o, bool):
            return o
        elif isinstance(o, (int, float, str)):
            return o
        elif isinstance(o, list):
            return [convert_none(x) for x in o]
        elif isinstance(o, dict):
            return {k: convert_none(v) for k, v in o.items()}
        else:
            return o
    
    return convert_none(data)

# ==================== Time Functions ====================

def builtin_time():
    """Current Unix timestamp."""
    return time.time()

def builtin_sleep(seconds):
    """Sleep for seconds."""
    time.sleep(seconds)
    return SharpNil()

def builtin_now():
    """Current datetime as string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def builtin_date(year, month, day):
    """Create date object as string."""
    return datetime(year, month, day).strftime("%Y-%m-%d")

# ==================== Networking Functions ====================

def builtin_http_get(url):
    """Simple HTTP GET request."""
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"HTTP GET failed: {e}")

def builtin_http_post(url, data):
    """Simple HTTP POST request."""
    try:
        import urllib.request
        req_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"HTTP POST failed: {e}")

# ==================== GUI Functions ====================

def builtin_gui_window(title="Sharp App", width=800, height=600):
    """Create GUI window."""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title(title)
        root.geometry(f"{width}x{height}")
        return root
    except Exception as e:
        raise RuntimeError(f"GUI creation failed: {e}")

def builtin_gui_label(parent, text="Label"):
    """Create label widget."""
    try:
        import tkinter as tk
        label = tk.Label(parent, text=text, font=("Arial", 12))
        label.pack(pady=10)
        return label
    except Exception as e:
        raise RuntimeError(f"Label creation failed: {e}")

def builtin_gui_button(parent, text="Button", onclick=None):
    """Create button widget."""
    try:
        import tkinter as tk
        def btn_callback():
            if onclick and callable(onclick):
                onclick()
        
        button = tk.Button(parent, text=text, command=btn_callback, font=("Arial", 12))
        button.pack(pady=10)
        return button
    except Exception as e:
        raise RuntimeError(f"Button creation failed: {e}")

def builtin_gui_textbox(parent, placeholder=""):
    """Create text entry widget."""
    try:
        import tkinter as tk
        textbox = tk.Entry(parent, font=("Arial", 12), width=40)
        if placeholder:
            textbox.insert(0, placeholder)
        textbox.pack(pady=10)
        return textbox
    except Exception as e:
        raise RuntimeError(f"Textbox creation failed: {e}")

def builtin_gui_textarea(parent, height=5, width=40):
    """Create text area widget."""
    try:
        import tkinter as tk
        textarea = tk.Text(parent, font=("Arial", 10), height=height, width=width)
        textarea.pack(pady=10)
        return textarea
    except Exception as e:
        raise RuntimeError(f"Textarea creation failed: {e}")

def builtin_gui_show(window):
    """Display window and start event loop."""
    try:
        window.mainloop()
        return SharpNil()
    except Exception as e:
        raise RuntimeError(f"Window display failed: {e}")

def builtin_gui_close(window):
    """Close window."""
    try:
        window.destroy()
        return SharpNil()
    except Exception as e:
        raise RuntimeError(f"Window close failed: {e}")

def builtin_widget_set_text(widget, text):
    """Set widget text."""
    try:
        if hasattr(widget, 'config'):
            widget.config(text=text)
        elif hasattr(widget, 'delete') and hasattr(widget, 'insert'):
            widget.delete(0, 'end')
            widget.insert(0, text)
        return SharpNil()
    except Exception as e:
        raise RuntimeError(f"Widget set text failed: {e}")

def builtin_widget_get_text(widget):
    """Get widget text."""
    try:
        if hasattr(widget, 'get'):
            return widget.get()
        return ""
    except Exception as e:
        raise RuntimeError(f"Widget get text failed: {e}")

# ==================== Utility Functions ====================

def builtin_assert(condition, message=""):
    """Assert condition."""
    if not condition:
        raise AssertionError(message)
    return SharpNil()

def builtin_help(obj=None):
    """Get help on object."""
    if obj is None:
        return """Sharp Programming Language - Help
Type help(function_name) for specific function help."""
    return f"Help: {obj}"

def builtin_id(obj):
    """Get object identity (memory address)."""
    return id(obj)

def builtin_hash(obj):
    """Get hash of object."""
    try:
        return hash(obj)
    except TypeError:
        return id(obj)

def builtin_bin(x):
    """Convert to binary string."""
    return bin(x)

def builtin_hex(x):
    """Convert to hexadecimal string."""
    return hex(x)

def builtin_oct(x):
    """Convert to octal string."""
    return oct(x)

# ==================== Timer Functions ====================

class SharpTimer(SharpValue):
    """Sharp timer object."""
    def __init__(self):
        self.start_time = None
        self.elapsed = 0
        self.is_running = False
    
    def start(self):
        """Start the timer."""
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True
        return SharpNil()
    
    def stop(self):
        """Stop the timer."""
        if self.is_running:
            self.elapsed += time.time() - self.start_time
            self.is_running = False
        return self.elapsed
    
    def reset(self):
        """Reset the timer."""
        self.elapsed = 0
        self.is_running = False
        return SharpNil()
    
    def get_elapsed(self):
        """Get elapsed time in seconds."""
        if self.is_running:
            return self.elapsed + (time.time() - self.start_time)
        return self.elapsed
    
    def __repr__(self):
        return f"<timer {self.get_elapsed():.2f}s>"

def builtin_timer():
    """Create a new timer object."""
    return SharpTimer()

def builtin_timer_start(timer):
    """Start a timer."""
    if isinstance(timer, SharpTimer):
        return timer.start()
    raise TypeError("Expected timer object")

def builtin_timer_stop(timer):
    """Stop a timer."""
    if isinstance(timer, SharpTimer):
        return timer.stop()
    raise TypeError("Expected timer object")

def builtin_timer_reset(timer):
    """Reset a timer."""
    if isinstance(timer, SharpTimer):
        return timer.reset()
    raise TypeError("Expected timer object")

def builtin_timer_elapsed(timer):
    """Get elapsed time from timer."""
    if isinstance(timer, SharpTimer):
        return timer.get_elapsed()
    raise TypeError("Expected timer object")

# ==================== Additional Python Functions ====================

def builtin_tuple(*args):
    """Create tuple from arguments."""
    return tuple(args)

def builtin_set(iterable=None):
    """Create set from iterable."""
    if iterable is None:
        return set()
    return set(iterable)

def builtin_frozenset(iterable):
    """Create frozenset."""
    return frozenset(iterable)

def builtin_slice(start, stop, step=1):
    """Create slice object."""
    return slice(start, stop, step)

def builtin_enumerate_custom(iterable, start=0):
    """Enumerate with custom index."""
    return list(enumerate(iterable, start))

def builtin_map_custom(func, *iterables):
    """Map function over iterables."""
    if not iterables:
        raise TypeError("map() must have at least two arguments.")
    return list(map(func, *iterables))

def builtin_zip_custom(*iterables):
    """Zip iterables together."""
    return list(zip(*iterables))

def builtin_reversed_custom(iterable):
    """Reverse iterable."""
    return list(reversed(iterable))

def builtin_sorted_custom(iterable, reverse=False, key=None):
    """Sort iterable."""
    return sorted(iterable, reverse=reverse)

def builtin_eval_expr(expr_str):
    """Evaluate a Simple expression."""
    try:
        return eval(expr_str, {"__builtins__": {}})
    except:
        raise RuntimeError(f"Cannot evaluate: {expr_str}")

def builtin_getattr_custom(obj, name, default=None):
    """Get attribute from object."""
    try:
        return getattr(obj, name)
    except AttributeError:
        return default

def builtin_setattr_custom(obj, name, value):
    """Set attribute on object."""
    try:
        setattr(obj, name, value)
        return SharpNil()
    except:
        raise RuntimeError(f"Cannot set attribute {name}")

def builtin_hasattr_custom(obj, name):
    """Check if object has attribute."""
    return hasattr(obj, name)

def builtin_callable_check(obj):
    """Check if object is callable."""
    return callable(obj)

def builtin_issubclass_check(cls1, cls2):
    """Check if class1 is subclass of class2."""
    try:
        return issubclass(cls1, cls2)
    except:
        return False

def builtin_isinstance_check(obj, classinfo):
    """Enhanced isinstance check."""
    return isinstance(obj, classinfo)

def builtin_abs_value(x):
    """Get absolute value."""
    return abs(x)

def builtin_divmod_custom(a, b):
    """Divmod function."""
    return divmod(a, b)

def builtin_ascii_val(obj):
    """Get ASCII representation."""
    return ascii(obj)

def builtin_repr_val(obj):
    """Get representation string."""
    if isinstance(obj, SharpNil):
        return "nil"
    return repr(obj)

def builtin_vars_dict(obj=None):
    """Get object's variables."""
    if obj is None:
        return {}
    try:
        return dict(vars(obj))
    except:
        return {}

def builtin_dir_list(obj=None):
    """List object's attributes."""
    if obj is None:
        return []
    return dir(obj)

def builtin_globals_dict():
    """Get global variables dictionary."""
    return {}  # Return empty for safety

def builtin_locals_dict():
    """Get local variables dictionary."""
    return {}  # Return empty for safety

def builtin_compile_code(source, filename="<sharp>", mode="exec"):
    """Compile code (basic implementation)."""
    return source  # Return source as-is

def builtin_next_item(iterator):
    """Get next item from iterator."""
    try:
        return next(iterator)
    except StopIteration:
        raise RuntimeError("StopIteration")

def builtin_iter_from(iterable):
    """Create iterator from iterable."""
    return iter(iterable)

def builtin_complex_num(real, imag=0):
    """Create complex number."""
    return complex(real, imag)

def builtin_memoryview_obj(obj):
    """Create memoryview (simplified)."""
    return memoryview(obj)

def builtin_bytes_obj(source):
    """Create bytes object."""
    if isinstance(source, str):
        return source.encode('utf-8')
    return bytes(source)

def builtin_bytearray_obj(source):
    """Create bytearray."""
    if isinstance(source, str):
        return bytearray(source, 'utf-8')
    return bytearray(source)

# ==================== Standard Library Dictionary ====================

STDLIB = {
    # I/O
    'print': SharpBuiltin('print', builtin_print),
    'input': SharpBuiltin('input', builtin_input),
    'open': SharpBuiltin('open', builtin_open),
    'read': SharpBuiltin('read', builtin_read),
    'write': SharpBuiltin('write', builtin_write),
    'close': SharpBuiltin('close', builtin_close),
    
    # File System
    'exists': SharpBuiltin('exists', builtin_exists),
    'mkdir': SharpBuiltin('mkdir', builtin_mkdir),
    'listdir': SharpBuiltin('listdir', builtin_listdir),
    'remove': SharpBuiltin('remove', builtin_remove),
    'rmdir': SharpBuiltin('rmdir', builtin_rmdir),
    'getcwd': SharpBuiltin('getcwd', builtin_getcwd),
    'chdir': SharpBuiltin('chdir', builtin_chdir),
    
    # Type Conversion & Inspection
    'len': SharpBuiltin('len', builtin_len),
    'str': SharpBuiltin('str', builtin_str),
    'int': SharpBuiltin('int', builtin_int),
    'float': SharpBuiltin('float', builtin_float),
    'bool': SharpBuiltin('bool', builtin_bool),
    'list': SharpBuiltin('list', builtin_list),
    'dict': SharpBuiltin('dict', builtin_dict),
    'type': SharpBuiltin('type', builtin_type),
    'isinstance': SharpBuiltin('isinstance', builtin_isinstance),
    'id': SharpBuiltin('id', builtin_id),
    'hash': SharpBuiltin('hash', builtin_hash),
    
    # String Functions
    'upper': SharpBuiltin('upper', builtin_upper),
    'lower': SharpBuiltin('lower', builtin_lower),
    'strip': SharpBuiltin('strip', builtin_strip),
    'split': SharpBuiltin('split', builtin_split),
    'join': SharpBuiltin('join', builtin_join),
    'replace': SharpBuiltin('replace', builtin_replace),
    'find': SharpBuiltin('find', builtin_find),
    'startswith': SharpBuiltin('startswith', builtin_startswith),
    'endswith': SharpBuiltin('endswith', builtin_endswith),
    'contains': SharpBuiltin('contains', builtin_contains),
    'format': SharpBuiltin('format', builtin_format),
    'ord': SharpBuiltin('ord', builtin_ord),
    'chr': SharpBuiltin('chr', builtin_chr),
    
    # Collection Functions
    'range': SharpBuiltin('range', builtin_range),
    'enumerate': SharpBuiltin('enumerate', builtin_enumerate),
    'zip': SharpBuiltin('zip', builtin_zip),
    'sorted': SharpBuiltin('sorted', builtin_sorted),
    'reversed': SharpBuiltin('reversed', builtin_reversed),
    'min': SharpBuiltin('min', builtin_min),
    'max': SharpBuiltin('max', builtin_max),
    'sum': SharpBuiltin('sum', builtin_sum),
    'any': SharpBuiltin('any', builtin_any),
    'all': SharpBuiltin('all', builtin_all),
    'filter': SharpBuiltin('filter', builtin_filter),
    'map': SharpBuiltin('map', builtin_map),
    
    # Math
    'abs': SharpBuiltin('abs', builtin_abs),
    'round': SharpBuiltin('round', builtin_round),
    'pow': SharpBuiltin('pow', builtin_pow),
    'sqrt': SharpBuiltin('sqrt', builtin_sqrt),
    'sin': SharpBuiltin('sin', builtin_sin),
    'cos': SharpBuiltin('cos', builtin_cos),
    'tan': SharpBuiltin('tan', builtin_tan),
    'log': SharpBuiltin('log', builtin_log),
    'log10': SharpBuiltin('log10', builtin_log10),
    'exp': SharpBuiltin('exp', builtin_exp),
    'floor': SharpBuiltin('floor', builtin_floor),
    'ceil': SharpBuiltin('ceil', builtin_ceil),
    'degrees': SharpBuiltin('degrees', builtin_degrees),
    'radians': SharpBuiltin('radians', builtin_radians),
    
    # Random
    'random': SharpBuiltin('random', builtin_random),
    'randint': SharpBuiltin('randint', builtin_randint),
    'choice': SharpBuiltin('choice', builtin_choice),
    'shuffle': SharpBuiltin('shuffle', builtin_shuffle),
    'sample': SharpBuiltin('sample', builtin_sample),
    
    # JSON
    'json_dumps': SharpBuiltin('json_dumps', builtin_json_dumps),
    'json_loads': SharpBuiltin('json_loads', builtin_json_loads),
    
    # Time
    'time': SharpBuiltin('time', builtin_time),
    'sleep': SharpBuiltin('sleep', builtin_sleep),
    'now': SharpBuiltin('now', builtin_now),
    'date': SharpBuiltin('date', builtin_date),
    
    # Timer Functions
    'timer': SharpBuiltin('timer', builtin_timer),
    'timer_start': SharpBuiltin('timer_start', builtin_timer_start),
    'timer_stop': SharpBuiltin('timer_stop', builtin_timer_stop),
    'timer_reset': SharpBuiltin('timer_reset', builtin_timer_reset),
    'timer_elapsed': SharpBuiltin('timer_elapsed', builtin_timer_elapsed),
    
    # Networking
    'http_get': SharpBuiltin('http_get', builtin_http_get),
    'http_post': SharpBuiltin('http_post', builtin_http_post),
    
    # GUI
    'gui_window': SharpBuiltin('gui_window', builtin_gui_window),
    'gui_label': SharpBuiltin('gui_label', builtin_gui_label),
    'gui_button': SharpBuiltin('gui_button', builtin_gui_button),
    'gui_textbox': SharpBuiltin('gui_textbox', builtin_gui_textbox),
    'gui_textarea': SharpBuiltin('gui_textarea', builtin_gui_textarea),
    'gui_show': SharpBuiltin('gui_show', builtin_gui_show),
    'gui_close': SharpBuiltin('gui_close', builtin_gui_close),
    'widget_set_text': SharpBuiltin('widget_set_text', builtin_widget_set_text),
    'widget_get_text': SharpBuiltin('widget_get_text', builtin_widget_get_text),
    
    # Utility
    'assert': SharpBuiltin('assert', builtin_assert),
    'exit': SharpBuiltin('exit', builtin_exit),
    'help': SharpBuiltin('help', builtin_help),
    'bin': SharpBuiltin('bin', builtin_bin),
    'hex': SharpBuiltin('hex', builtin_hex),
    'oct': SharpBuiltin('oct', builtin_oct),
    
    # Additional Python Functions
    'tuple': SharpBuiltin('tuple', builtin_tuple),
    'set': SharpBuiltin('set', builtin_set),
    'frozenset': SharpBuiltin('frozenset', builtin_frozenset),
    'slice': SharpBuiltin('slice', builtin_slice),
    'callable': SharpBuiltin('callable', builtin_callable_check),
    'repr': SharpBuiltin('repr', builtin_repr_val),
    'ascii': SharpBuiltin('ascii', builtin_ascii_val),
    'vars': SharpBuiltin('vars', builtin_vars_dict),
    'dir': SharpBuiltin('dir', builtin_dir_list),
    'divmod': SharpBuiltin('divmod', builtin_divmod_custom),
    'next': SharpBuiltin('next', builtin_next_item),
    'iter': SharpBuiltin('iter', builtin_iter_from),
    'complex': SharpBuiltin('complex', builtin_complex_num),
    'bytes': SharpBuiltin('bytes', builtin_bytes_obj),
    'bytearray': SharpBuiltin('bytearray', builtin_bytearray_obj),
    
    # Constants
    'true': True,
    'false': False,
    'nil': SharpNil(),
    'pi': math.pi,
    'e': math.e,
}
