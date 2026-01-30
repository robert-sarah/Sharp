"""
Interpreter extension methods for Sharp language.
This file contains evaluation methods for:
- Classes & OOP
- Decorators
- Exception handling
- Generators
- Async/await
- Context managers
"""

from ast_nodes import (
    ClassDef, DecoratedFunction, DecoratedClass,
    TryStmt, RaiseStmt, WithStmt, YieldStmt,
    AsyncFunctionDef, AwaitExpr, AsyncForLoop, AsyncWithStmt,
    FunctionDef, VarDecl
)

def eval_class_def(self, node: ClassDef) -> 'SharpClass':
    """Evaluate class definition."""
    # Resolve base classes
    bases = []
    for base_name in node.bases:
        base_cls = env.get(base_name)
        if not isinstance(base_cls, SharpClass):
            raise SharpRuntimeError(f"Base '{base_name}' is not a class")
        bases.append(base_cls)
    
    # Create new environment for class
    class_env = Environment(env)
    
    # Evaluate class body
    methods = {}
    attributes = {}
    
    for stmt in node.body:
        if isinstance(stmt, FunctionDef):
            # Methods
            func = self.eval_function_def(stmt, class_env)
            methods[stmt.name] = func
        elif isinstance(stmt, VarDecl):
            # Class attributes
            value = self.eval(stmt.value, class_env)
            attributes[stmt.name] = value
        else:
            self.eval(stmt, class_env)
    
    # Create and register class
    sharp_class = SharpClass(node.name, bases, methods, attributes)
    env.define(node.name, sharp_class)
    
    return sharp_class

def eval_decorated_function(self, node: DecoratedFunction, env: Environment):
    """Evaluate decorated function."""
    func = self.eval(node.func, env)
    
    # Apply decorators from bottom to top
    for decorator in reversed(node.decorators):
        dec_func = env.get(decorator.name)
        if callable(dec_func):
            if decorator.args:
                args = [self.eval(arg, env) for arg in decorator.args]
                func = dec_func(*args)(func)
            else:
                func = dec_func(func)
    
    return func

def eval_decorated_class(self, node: DecoratedClass, env: Environment):
    """Evaluate decorated class."""
    cls = self.eval(node.cls, env)
    
    # Apply decorators from bottom to top
    for decorator in reversed(node.decorators):
        dec_func = env.get(decorator.name)
        if callable(dec_func):
            if decorator.args:
                args = [self.eval(arg, env) for arg in decorator.args]
                cls = dec_func(*args)(cls)
            else:
                cls = dec_func(cls)
    
    return cls

def eval_try_stmt(self, node: TryStmt, env: Environment):
    """Evaluate try/except/finally statement."""
    result = None
    exception_caught = False
    
    try:
        # Try to execute try block
        for stmt in node.body:
            result = self.eval(stmt, env)
    
    except SharpException as e:
        # Handle exceptions
        for handler in node.except_handlers:
            if handler.exception_type is None or isinstance(e, type(e)):
                # Catch-all or matching exception type
                if handler.var_name:
                    env.define(handler.var_name, e)
                
                for stmt in handler.body:
                    result = self.eval(stmt, env)
                exception_caught = True
                break
    
    # Execute else block if no exception
    if not exception_caught and node.else_body:
        for stmt in node.else_body:
            result = self.eval(stmt, env)
    
    finally:
        # Always execute finally block
        if node.finally_body:
            for stmt in node.finally_body:
                result = self.eval(stmt, env)
    
    return result

def eval_raise_stmt(self, node: RaiseStmt, env: Environment):
    """Evaluate raise statement."""
    if node.exception is None:
        raise SharpRuntimeError("No exception to raise")
    
    exception_value = self.eval(node.exception, env)
    raise SharpException(str(exception_value))

def eval_with_stmt(self, node: WithStmt, env: Environment):
    """Evaluate with statement (context manager)."""
    context = self.eval(node.context_expr, env)
    
    result = None
    # Call __enter__
    if hasattr(context, '__enter__'):
        result = context.__enter__()
        if node.context_var:
            env.define(node.context_var, result)
    
    try:
        # Execute body
        for stmt in node.body:
            result = self.eval(stmt, env)
    finally:
        # Call __exit__
        if hasattr(context, '__exit__'):
            context.__exit__(None, None, None)
    
    return result

def eval_yield_stmt(self, node: YieldStmt, env: Environment):
    """Evaluate yield statement (generator)."""
    if node.value:
        return self.eval(node.value, env)
    return None

def eval_async_function_def(self, node: AsyncFunctionDef, env: Environment):
    """Evaluate async function definition."""
    # For now, treat async functions like regular functions
    # Full async support would require asyncio integration
    return SharpFunction(node.name, node.params, node.defaults, node.body, env)

def eval_await_expr(self, node: AwaitExpr, env: Environment):
    """Evaluate await expression."""
    # For now, just evaluate the expression
    # Full async support would require asyncio integration
    return self.eval(node.value, env)

def eval_async_for_loop(self, node: AsyncForLoop, env: Environment):
    """Evaluate async for loop."""
    # For now, treat like regular for loop
    iterable = self.eval(node.iterable, env)
    
    result = None
    for item in iterable:
        loop_env = Environment(env)
        loop_env.define(node.target, item)
        
        try:
            for stmt in node.body:
                result = self.eval(stmt, loop_env)
        except BreakException:
            break
        except ContinueException:
            continue
    
    return result

def eval_async_with_stmt(self, node: AsyncWithStmt, env: Environment):
    """Evaluate async with statement."""
    # For now, treat like regular with statement
    context = self.eval(node.context_expr, env)
    
    if hasattr(context, '__aenter__'):
        result = context.__aenter__()
        if node.context_var:
            env.define(node.context_var, result)
    
    try:
        for stmt in node.body:
            self.eval(stmt, env)
    finally:
        if hasattr(context, '__aexit__'):
            context.__aexit__(None, None, None)
    
    return None

def eval_function_call_with_self(self, func: Any, args: List[Any], kwargs: Dict[str, Any], env: Environment):
    """Evaluate function call with self binding for methods."""
    if isinstance(func, SharpFunction):
        # Create call environment
        call_env = Environment(func.closure)
        
        # Bind parameters
        for i, param in enumerate(func.params):
            if i < len(args):
                call_env.define(param, args[i])
            elif param in kwargs:
                call_env.define(param, kwargs[param])
            elif i < len(func.params) - len(func.defaults):
                # Required parameter not provided
                raise SharpRuntimeError(f"Missing required parameter: {param}")
            elif func.defaults[i] is not None:
                default_val = self.eval(func.defaults[i], func.closure)
                call_env.define(param, default_val)
        
        # Execute function body
        try:
            result = None
            for stmt in func.body:
                result = self.eval(stmt, call_env)
        except ReturnValue as ret:
            return ret.value
        
        return result
    elif callable(func):
        return func(*args, **kwargs)
    else:
        raise SharpRuntimeError(f"'{func}' is not callable")

# This function is called by interpreter.py to register all extension methods
def register_interpreter_extensions(interpreter_class):
    """Register all extension methods to the Interpreter class."""
    interpreter_class.eval_class_def = eval_class_def
    interpreter_class.eval_decorated_function = eval_decorated_function
    interpreter_class.eval_decorated_class = eval_decorated_class
    interpreter_class.eval_try_stmt = eval_try_stmt
    interpreter_class.eval_raise_stmt = eval_raise_stmt
    interpreter_class.eval_with_stmt = eval_with_stmt
    interpreter_class.eval_yield_stmt = eval_yield_stmt
    interpreter_class.eval_async_function_def = eval_async_function_def
    interpreter_class.eval_await_expr = eval_await_expr
    interpreter_class.eval_async_for_loop = eval_async_for_loop
    interpreter_class.eval_async_with_stmt = eval_async_with_stmt