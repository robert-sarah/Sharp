# New parser methods for Sharp language extensions
# This file contains all the new parsing methods for:
# - Classes & OOP
# - Decorators
# - Type annotations
# - Exception handling (try/except/finally)
# - Generators (yield)
# - Async/await
# - With statements
# - Raise statements

from lexer import TokenType
from ast_nodes import (
    ClassDef, DecoratedFunction, DecoratedClass, Decorator,
    TryStmt, ExceptHandler, RaiseStmt, WithStmt, YieldStmt,
    AsyncFunctionDef, AsyncForLoop, AsyncWithStmt,
    ASTNode
)

def parse_class(self) -> ClassDef:
    """Parse class definition."""
    self.expect(TokenType.CLASS)
    name_token = self.expect(TokenType.IDENTIFIER)
    
    bases = []
    if self.current_token and self.current_token.type == TokenType.LPAREN:
        self.advance()
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            base_token = self.expect(TokenType.IDENTIFIER)
            bases.append(base_token.value)
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
    
    self.expect(TokenType.COLON)
    self.skip_newlines()
    body = self.parse_block()
    
    return ClassDef(name_token.value, bases, body)

def parse_async(self) -> ASTNode:
    """Parse async function or for loop."""
    self.expect(TokenType.ASYNC)
    
    if self.current_token and self.current_token.type == TokenType.DEF:
        self.advance()
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)
        
        params = []
        defaults = []
        
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            param_token = self.expect(TokenType.IDENTIFIER)
            params.append(param_token.value)
            
            if self.current_token and self.current_token.type == TokenType.ASSIGN:
                self.advance()
                defaults.append(self.parse_expression())
            else:
                defaults.append(None)
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = self.parse_block()
        
        return AsyncFunctionDef(name_token.value, params, defaults, body)
    
    elif self.current_token and self.current_token.type == TokenType.FOR:
        return self.parse_async_for()
    
    elif self.current_token and self.current_token.type == TokenType.WITH:
        return self.parse_async_with()
    
    else:
        self.error("Expected 'def', 'for', or 'with' after 'async'")

def parse_async_for(self) -> AsyncForLoop:
    """Parse async for loop."""
    self.expect(TokenType.FOR)
    target_token = self.expect(TokenType.IDENTIFIER)
    self.expect(TokenType.IN)
    iterable = self.parse_expression()
    self.expect(TokenType.COLON)
    self.skip_newlines()
    
    body = self.parse_block()
    
    return AsyncForLoop(target_token.value, iterable, body)

def parse_async_with(self) -> AsyncWithStmt:
    """Parse async with statement."""
    self.expect(TokenType.WITH)
    context_expr = self.parse_expression()
    
    context_var = None
    if self.current_token and self.current_token.type == TokenType.AS:
        self.advance()
        var_token = self.expect(TokenType.IDENTIFIER)
        context_var = var_token.value
    
    self.expect(TokenType.COLON)
    self.skip_newlines()
    body = self.parse_block()
    
    return AsyncWithStmt(context_var, context_expr, body)

def parse_try(self) -> TryStmt:
    """Parse try/except/finally statement."""
    self.expect(TokenType.TRY)
    self.expect(TokenType.COLON)
    self.skip_newlines()
    
    body = self.parse_block()
    except_handlers = []
    else_body = None
    finally_body = None
    
    # Parse except clauses
    while self.current_token and self.current_token.type == TokenType.EXCEPT:
        self.advance()
        
        exception_type = None
        var_name = None
        
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            type_token = self.expect(TokenType.IDENTIFIER)
            exception_type = type_token.value
            
            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()
                var_token = self.expect(TokenType.IDENTIFIER)
                var_name = var_token.value
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        handler_body = self.parse_block()
        
        except_handlers.append(ExceptHandler(exception_type, var_name, handler_body))
    
    # Parse else clause (if present)
    if self.current_token and self.current_token.type == TokenType.ELSE:
        self.advance()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        else_body = self.parse_block()
    
    # Parse finally clause (if present)
    if self.current_token and self.current_token.type == TokenType.FINALLY:
        self.advance()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        finally_body = self.parse_block()
    
    return TryStmt(body, except_handlers, else_body, finally_body)

def parse_raise(self) -> RaiseStmt:
    """Parse raise statement."""
    self.expect(TokenType.RAISE)
    
    exception = None
    cause = None
    
    if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
        exception = self.parse_expression()
        
        # Check for 'from' clause
        if self.current_token and self.current_token.type == TokenType.FROM:
            self.advance()
            cause = self.parse_expression()
    
    return RaiseStmt(exception, cause)

def parse_with(self) -> WithStmt:
    """Parse with statement (context manager)."""
    self.expect(TokenType.WITH)
    context_expr = self.parse_expression()
    
    context_var = None
    if self.current_token and self.current_token.type == TokenType.AS:
        self.advance()
        var_token = self.expect(TokenType.IDENTIFIER)
        context_var = var_token.value
    
    self.expect(TokenType.COLON)
    self.skip_newlines()
    body = self.parse_block()
    
    return WithStmt(context_var, context_expr, body)

def parse_yield(self) -> YieldStmt:
    """Parse yield statement (generator)."""
    self.expect(TokenType.YIELD)
    
    value = None
    if self.current_token and self.current_token.type not in (TokenType.NEWLINE, TokenType.EOF):
        value = self.parse_expression()
    
    return YieldStmt(value)

def parse_decorator(self) -> ASTNode:
    """Parse decorator and the decorated function/class."""
    decorators = []
    
    # Parse all decorators
    while self.current_token and self.current_token.type == TokenType.AT:
        self.advance()
        name_token = self.expect(TokenType.IDENTIFIER)
        
        args = []
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            while self.current_token and self.current_token.type != TokenType.RPAREN:
                args.append(self.parse_expression())
                if self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RPAREN)
        
        decorators.append(Decorator(name_token.value, args))
        self.skip_newlines()
    
    # Parse decorated function or class
    if self.current_token and self.current_token.type == TokenType.DEF:
        func = self.parse_function()
        return DecoratedFunction(decorators, func)
    elif self.current_token and self.current_token.type == TokenType.CLASS:
        cls = self.parse_class()
        return DecoratedClass(decorators, cls)
    else:
        self.error("Decorator must precede a function or class definition")

# This function is called by parser.py to register all extension methods
def register_parser_extensions(parser_class):
    """Register all extension methods to the Parser class."""
    parser_class.parse_class = parse_class
    parser_class.parse_async = parse_async
    parser_class.parse_async_for = parse_async_for
    parser_class.parse_async_with = parse_async_with
    parser_class.parse_try = parse_try
    parser_class.parse_raise = parse_raise
    parser_class.parse_with = parse_with
    parser_class.parse_yield = parse_yield
    parser_class.parse_decorator = parse_decorator