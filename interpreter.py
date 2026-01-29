"""
Interpreter for Sharp Programming Language.
Evaluates AST and executes Sharp programs.
"""

import math
import os
from typing import Any, Dict, Optional, List
from ast_nodes import *
from stdlib import (
    SharpValue, SharpFunction, SharpBuiltin, SharpType, SharpVariant, SharpNil, SharpModule,
    ReturnValue, BreakException, ContinueException, STDLIB
)

class Environment:
    """Environment for variable scope."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
    
    def define(self, name: str, value: Any):
        """Define variable in current scope."""
        self.variables[name] = value
    
    def get(self, name: str) -> Any:
        """Get variable value."""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"name '{name}' is not defined")
    
    def set(self, name: str, value: Any):
        """Set variable value."""
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            # If not found, create in current scope
            self.variables[name] = value

class Interpreter:
    """Interprets and executes Sharp AST."""
    
    def __init__(self):
        self.global_env = Environment()
        # Load standard library
        for name, value in STDLIB.items():
            self.global_env.define(name, value)
        self.current_env = self.global_env
        self.loaded_modules = {}  # Cache for loaded modules
    
    def load_module(self, module_name: str) -> Dict[str, Any]:
        """Load a Sharp or Python module and return its exports."""
        # Check cache
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        # Try to load as Sharp module first
        module_path = self._find_module(module_name)
        
        if module_path and module_path.endswith('.sharp'):
            # Load Sharp module
            try:
                with open(module_path, 'r') as f:
                    source = f.read()
            except FileNotFoundError:
                raise ImportError(f"Module '{module_name}' not found at {module_path}")
            
            # Parse and interpret module
            from lexer import Lexer
            from parser import Parser
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Create module environment
            module_env = Environment(self.global_env)
            old_env = self.current_env
            self.current_env = module_env
            
            try:
                self.interpret(ast)
            finally:
                self.current_env = old_env
            
            # Extract module exports
            exports = {}
            for name, value in module_env.variables.items():
                exports[name] = value
            
            # Cache the module
            self.loaded_modules[module_name] = exports
            return exports
        
        # Try to load as Python module
        try:
            import importlib
            py_module = importlib.import_module(f"modules.{module_name}")
            
            # Extract all public attributes
            exports = {}
            for name in dir(py_module):
                if not name.startswith('_'):
                    exports[name] = getattr(py_module, name)
            
            self.loaded_modules[module_name] = exports
            return exports
        except (ImportError, ModuleNotFoundError):
            pass
        
        # If not found anywhere
        raise ImportError(f"No module named '{module_name}'")
    
    def _find_module(self, module_name: str) -> Optional[str]:
        """Find module file in standard locations."""
        # Try built-in modules first
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try modules/ directory
        module_paths = [
            os.path.join(current_dir, 'modules', f'{module_name}.sharp'),
            os.path.join(current_dir, f'{module_name}.sharp'),
            os.path.join('.', 'modules', f'{module_name}.sharp'),
            os.path.join('.', f'{module_name}.sharp'),
        ]
        
        for path in module_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def interpret(self, program: Program) -> Any:
        """Interpret a program."""
        result = None
        for statement in program.statements:
            result = self.evaluate(statement)
        return result
    
    def evaluate(self, node: ASTNode) -> Any:
        """Evaluate AST node."""
        if isinstance(node, IntLiteral):
            return node.value
        
        elif isinstance(node, FloatLiteral):
            return node.value
        
        elif isinstance(node, StringLiteral):
            return node.value
        
        elif isinstance(node, BoolLiteral):
            return node.value
        
        elif isinstance(node, NilLiteral):
            return SharpNil()
        
        elif isinstance(node, ListLiteral):
            return [self.evaluate(elem) for elem in node.elements]
        
        elif isinstance(node, DictLiteral):
            return {self.evaluate(k): self.evaluate(v) for k, v in node.pairs}
        
        elif isinstance(node, TupleLiteral):
            return tuple(self.evaluate(elem) for elem in node.elements)
        
        elif isinstance(node, Identifier):
            return self.current_env.get(node.name)
        
        elif isinstance(node, VarDecl):
            value = self.evaluate(node.value)
            self.current_env.define(node.name, value)
            return value
        
        elif isinstance(node, BinaryOp):
            return self.eval_binary_op(node)
        
        elif isinstance(node, UnaryOp):
            return self.eval_unary_op(node)
        
        elif isinstance(node, Assignment):
            value = self.evaluate(node.value)
            self.current_env.set(node.target, value)
            return value
        
        elif isinstance(node, AugmentedAssignment):
            current = self.current_env.get(node.target)
            value = self.evaluate(node.value)
            result = self.apply_binary_op(current, node.op, value)
            self.current_env.set(node.target, result)
            return result
        
        elif isinstance(node, FunctionDef):
            func = SharpFunction(node.name, node.params, node.defaults, node.body, self.current_env)
            self.current_env.define(node.name, func)
            return SharpNil()
        
        elif isinstance(node, FunctionCall):
            return self.eval_function_call(node)
        
        elif isinstance(node, Lambda):
            return SharpFunction('<lambda>', node.params, [], node.body, self.current_env)
        
        elif isinstance(node, IfExpr):
            return self.eval_if(node)
        
        elif isinstance(node, WhileLoop):
            return self.eval_while(node)
        
        elif isinstance(node, ForLoop):
            return self.eval_for(node)
        
        elif isinstance(node, MatchExpr):
            return self.eval_match(node)
        
        elif isinstance(node, ReturnStmt):
            value = self.evaluate(node.value) if node.value else SharpNil()
            raise ReturnValue(value)
        
        elif isinstance(node, BreakStmt):
            raise BreakException()
        
        elif isinstance(node, ContinueStmt):
            raise ContinueException()
        
        elif isinstance(node, IndexAccess):
            obj = self.evaluate(node.obj)
            index = self.evaluate(node.index)
            return obj[index]
        
        elif isinstance(node, SliceAccess):
            obj = self.evaluate(node.obj)
            start = self.evaluate(node.start) if node.start else None
            end = self.evaluate(node.end) if node.end else None
            step = self.evaluate(node.step) if node.step else None
            return obj[start:end:step]
        
        elif isinstance(node, AttributeAccess):
            obj = self.evaluate(node.obj)
            # Handle SharpModule specially
            if isinstance(obj, SharpModule):
                exports = obj.exports
                if node.attr in exports:
                    return exports[node.attr]
                raise AttributeError(f"Module '{obj.name}' has no attribute '{node.attr}'")
            return getattr(obj, node.attr)
        
        elif isinstance(node, ListComprehension):
            return self.eval_list_comprehension(node)
        
        elif isinstance(node, DictComprehension):
            return self.eval_dict_comprehension(node)
        
        elif isinstance(node, TypeDef):
            return self.eval_type_def(node)
        
        elif isinstance(node, ImportStmt):
            # Load module and optionally alias it
            module_exports = self.load_module(node.module)
            
            # Create module object
            module_obj = SharpModule(node.module, module_exports)
            
            # Define module in current environment
            if node.alias:
                self.current_env.define(node.alias, module_obj)
            else:
                self.current_env.define(node.module, module_obj)
            
            return SharpNil()
        
        elif isinstance(node, FromImportStmt):
            # Load module and import specific items
            module_exports = self.load_module(node.module)
            
            # Import requested items
            for item_name, alias in node.items:
                if item_name == '*':
                    # Import all
                    for name, value in module_exports.items():
                        self.current_env.define(name, value)
                else:
                    # Import specific item
                    if item_name not in module_exports:
                        raise ImportError(f"Cannot import name '{item_name}' from '{node.module}'")
                    
                    # Use alias if provided, otherwise use original name
                    import_as = alias if alias else item_name
                    self.current_env.define(import_as, module_exports[item_name])
            
            return SharpNil()
        
        elif isinstance(node, PassStmt):
            return SharpNil()
        
        elif isinstance(node, Program):
            return self.interpret(node)
        
        else:
            raise RuntimeError(f"Unknown AST node type: {type(node).__name__}")
    
    def eval_binary_op(self, node: BinaryOp) -> Any:
        """Evaluate binary operation."""
        # Short-circuit evaluation for logical operators
        if node.op == 'and':
            left = self.evaluate(node.left)
            if not self.is_truthy(left):
                return left
            return self.evaluate(node.right)
        
        elif node.op == 'or':
            left = self.evaluate(node.left)
            if self.is_truthy(left):
                return left
            return self.evaluate(node.right)
        
        # Regular binary operations
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        return self.apply_binary_op(left, node.op, right)
    
    def apply_binary_op(self, left: Any, op: str, right: Any) -> Any:
        """Apply binary operator."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if isinstance(left, int) and isinstance(right, int):
                return left // right  # Integer division
            return left / right
        elif op == '%':
            return left % right
        elif op == '**':
            return left ** right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '<=':
            return left <= right
        elif op == '>':
            return left > right
        elif op == '>=':
            return left >= right
        elif op == '&':
            return left & right
        elif op == '|':
            return left | right
        elif op == '^':
            return left ^ right
        elif op == '<<':
            return left << right
        elif op == '>>':
            return left >> right
        elif op == 'in':
            # Membership test operator
            return left in right
        else:
            raise RuntimeError(f"Unknown binary operator: {op}")
    
    def eval_unary_op(self, node: UnaryOp) -> Any:
        """Evaluate unary operation."""
        operand = self.evaluate(node.operand)
        
        if node.op == '-':
            return -operand
        elif node.op == '+':
            return +operand
        elif node.op == 'not':
            return not self.is_truthy(operand)
        elif node.op == '~':
            return ~operand
        else:
            raise RuntimeError(f"Unknown unary operator: {node.op}")
    
    def eval_function_call(self, node: FunctionCall) -> Any:
        """Evaluate function call."""
        func = self.evaluate(node.func)
        args = [self.evaluate(arg) for arg in node.args]
        kwargs = {k: self.evaluate(v) for k, v in node.kwargs.items()}
        
        return self.call_function(func, args, kwargs)
    
    def call_function(self, func: Any, args: List[Any], kwargs: dict) -> Any:
        """Call a function (Sharp, builtin, or Python)."""
        
        if isinstance(func, SharpBuiltin):
            # Special handling for higher-order functions that take callables
            if func.name in ('map', 'filter'):
                if func.name == 'map':
                    func_arg = args[0]
                    iterables = args[1:]
                    results = []
                    for items in zip(*iterables):
                        if len(iterables) == 1:
                            item = items[0]
                        else:
                            item = items
                        # Call function (Sharp or builtin)
                        result = self.call_function(func_arg, [item], {})
                        results.append(result)
                    return results
                elif func.name == 'filter':
                    func_arg = args[0]
                    iterable = args[1]
                    results = []
                    for item in iterable:
                        if func_arg is None:
                            if self.is_truthy(item):
                                results.append(item)
                        else:
                            result = self.call_function(func_arg, [item], {})
                            if self.is_truthy(result):
                                results.append(item)
                    return results
            return func.func(*args, **kwargs)
        
        elif isinstance(func, SharpFunction):
            # Create new environment for function
            func_env = Environment(func.closure)
            
            # Bind parameters
            for i, param in enumerate(func.params):
                if i < len(args):
                    func_env.define(param, args[i])
                elif param in kwargs:
                    func_env.define(param, kwargs[param])
                elif i < len(func.defaults) and func.defaults[i] is not None:
                    func_env.define(param, self.evaluate(func.defaults[i]))
                else:
                    raise TypeError(f"missing required argument: '{param}'")
            
            # Execute function body
            prev_env = self.current_env
            self.current_env = func_env
            try:
                result = SharpNil()
                # Handle both statement lists and single expressions (lambdas)
                if isinstance(func.body, list):
                    for stmt in func.body:
                        result = self.evaluate(stmt)
                else:
                    # Single expression (lambda)
                    result = self.evaluate(func.body)
                return result
            except ReturnValue as ret:
                return ret.value
            finally:
                self.current_env = prev_env
        
        elif callable(func):
            return func(*args, **kwargs)
        
        else:
            raise TypeError(f"'{type(func).__name__}' object is not callable")
    
    def eval_if(self, node: IfExpr) -> Any:
        """Evaluate if expression."""
        condition = self.evaluate(node.condition)
        
        if self.is_truthy(condition):
            result = SharpNil()
            for stmt in node.then_body:
                result = self.evaluate(stmt)
            return result
        
        # Check elif conditions
        for elif_cond, elif_body in node.elif_parts:
            elif_condition = self.evaluate(elif_cond)
            if self.is_truthy(elif_condition):
                result = SharpNil()
                for stmt in elif_body:
                    result = self.evaluate(stmt)
                return result
        
        # Execute else body
        if node.else_body:
            result = SharpNil()
            for stmt in node.else_body:
                result = self.evaluate(stmt)
            return result
        
        return SharpNil()
    
    def eval_while(self, node: WhileLoop) -> Any:
        """Evaluate while loop."""
        result = SharpNil()
        
        while self.is_truthy(self.evaluate(node.condition)):
            try:
                for stmt in node.body:
                    result = self.evaluate(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def eval_for(self, node: ForLoop) -> Any:
        """Evaluate for loop."""
        iterable = self.evaluate(node.iterable)
        result = SharpNil()
        
        for item in iterable:
            self.current_env.set(node.target, item)
            try:
                for stmt in node.body:
                    result = self.evaluate(stmt)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def eval_match(self, node: MatchExpr) -> Any:
        """Evaluate match expression."""
        value = self.evaluate(node.value)
        
        for pattern, body in node.cases:
            pattern_value = self.evaluate(pattern)
            
            # Simple pattern matching: check equality
            if value == pattern_value:
                result = SharpNil()
                for stmt in body:
                    result = self.evaluate(stmt)
                return result
        
        return SharpNil()
    
    def eval_list_comprehension(self, node: ListComprehension) -> List:
        """Evaluate list comprehension."""
        iterable = self.evaluate(node.iterable)
        result = []
        
        for item in iterable:
            self.current_env.set(node.target, item)
            
            # Check condition if present
            if node.condition:
                condition = self.evaluate(node.condition)
                if not self.is_truthy(condition):
                    continue
            
            value = self.evaluate(node.expr)
            result.append(value)
        
        return result
    
    def eval_dict_comprehension(self, node: DictComprehension) -> Dict:
        """Evaluate dict comprehension."""
        iterable = self.evaluate(node.iterable)
        result = {}
        
        for item in iterable:
            self.current_env.set(node.target, item)
            
            # Check condition if present
            if node.condition:
                condition = self.evaluate(node.condition)
                if not self.is_truthy(condition):
                    continue
            
            key = self.evaluate(node.key)
            value = self.evaluate(node.value)
            result[key] = value
        
        return result
    
    def eval_type_def(self, node: TypeDef) -> Any:
        """Evaluate type definition."""
        variants = {}
        for variant_name, fields in node.variants:
            variants[variant_name] = fields
        
        type_obj = SharpType(node.name, variants)
        self.current_env.define(node.name, type_obj)
        return SharpNil()
    
    def is_truthy(self, value: Any) -> bool:
        """Check if value is truthy."""
        if isinstance(value, SharpNil):
            return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return len(value) > 0
        elif isinstance(value, (list, dict, tuple)):
            return len(value) > 0
        else:
            return True
