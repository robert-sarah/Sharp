"""
Enhanced Parser for Sharp Programming Language.
Supports multi-line dictionaries, lists, 'in' operator, and more.
"""

from typing import List, Optional, Any
from lexer import Token, TokenType
from ast_nodes import *

class Parser:
    """Enhanced parser for Sharp with better syntax support."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None
        self.paren_depth = 0  # Track nesting level for multi-line support

    def error(self, message: str):
        """Raise a syntax error with location info."""
        if self.current_token:
            raise SyntaxError(f"{message} at line {self.current_token.line}, column {self.current_token.column}")
        else:
            raise SyntaxError(message)

    def advance(self):
        """Move to next token."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def peek(self, offset: int = 1) -> Optional[Token]:
        """Look ahead at token."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def expect(self, token_type: TokenType) -> Token:
        """Consume a token of expected type."""
        if not self.current_token or self.current_token.type != token_type:
            expected_name = token_type.name
            got_name = self.current_token.type.name if self.current_token else 'EOF'
            
            # Provide helpful context for common syntax errors
            error_msg = f"Expected {expected_name}, got {got_name}"
            
            if token_type == TokenType.LPAREN and expected_name == "LPAREN":
                if got_name == "NEWLINE":
                    error_msg += " (Missing parentheses in function definition? Use: def name():)"
                elif got_name == "IDENTIFIER":
                    error_msg += " (Missing operator or parentheses?)"
            elif token_type == TokenType.COLON and got_name == "NEWLINE":
                error_msg += " (Missing colon? Use: def name():"
            
            self.error(error_msg)
        token = self.current_token
        self.advance()
        return token

    def skip_newlines(self):
        """Skip newline tokens (but not at higher paren depth)."""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def skip_newlines_preserve_indentation(self):
        """Skip newlines while inside brackets/parens."""
        while self.current_token and self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT, TokenType.DEDENT):
            if self.current_token.type == TokenType.INDENT or self.current_token.type == TokenType.DEDENT:
                if self.paren_depth == 0:
                    break
            self.advance()

    def parse(self) -> Program:
        """Parse entire program."""
        statements = []
        self.skip_newlines()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        if not self.current_token:
            return None
        
        if self.current_token.type == TokenType.DEF:
            return self.parse_function()
        elif self.current_token.type == TokenType.CLASS:
            return self.parse_class()
        elif self.current_token.type == TokenType.ASYNC:
            return self.parse_async()
        elif self.current_token.type == TokenType.LET:
            return self.parse_variable()
        elif self.current_token.type == TokenType.IF:
            return self.parse_if()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for()
        elif self.current_token.type == TokenType.MATCH:
            return self.parse_match()
        elif self.current_token.type == TokenType.RETURN:
            return self.parse_return()
        elif self.current_token.type == TokenType.BREAK:
            self.advance()
            return BreakStmt()
        elif self.current_token.type == TokenType.CONTINUE:
            self.advance()
            return ContinueStmt()
        elif self.current_token.type == TokenType.TYPE:
            return self.parse_type_def()
        elif self.current_token.type == TokenType.IMPORT:
            return self.parse_import()
        elif self.current_token.type == TokenType.FROM:
            return self.parse_from_import()
        elif self.current_token.type == TokenType.TRY:
            return self.parse_try()
        elif self.current_token.type == TokenType.RAISE:
            return self.parse_raise()
        elif self.current_token.type == TokenType.WITH:
            return self.parse_with()
        elif self.current_token.type == TokenType.YIELD:
            return self.parse_yield()
        elif self.current_token.type == TokenType.PASS:
            self.advance()
            return PassStmt()
        elif self.current_token.type == TokenType.AT:
            return self.parse_decorator()
        else:
            return self.parse_expression_statement()

    def parse_function(self) -> FunctionDef:
        """Parse function definition."""
        self.expect(TokenType.DEF)
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
        
        return FunctionDef(name_token.value, params, defaults, body)

    def parse_variable(self) -> VarDecl:
        """Parse variable declaration."""
        self.expect(TokenType.LET)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        
        return VarDecl(name_token.value, value)

    def parse_if(self) -> IfExpr:
        """Parse if expression."""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        then_body = self.parse_block()
        elif_parts = []
        else_body = None
        
        while self.current_token and self.current_token.type == TokenType.ELIF:
            self.advance()
            elif_cond = self.parse_expression()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            elif_body = self.parse_block()
            elif_parts.append((elif_cond, elif_body))
        
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            else_body = self.parse_block()
        
        return IfExpr(condition, then_body, elif_parts, else_body)

    def parse_while(self) -> WhileLoop:
        """Parse while loop."""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = self.parse_block()
        
        return WhileLoop(condition, body)

    def parse_for(self) -> ForLoop:
        """Parse for loop."""
        self.expect(TokenType.FOR)
        target_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = self.parse_block()
        
        return ForLoop(target_token.value, iterable, body)

    def parse_match(self) -> MatchExpr:
        """Parse match expression."""
        self.expect(TokenType.MATCH)
        value = self.parse_expression()
        self.expect(TokenType.COLON)
        self.skip_newlines()
        self.expect(TokenType.INDENT)
        
        cases = []
        while self.current_token and self.current_token.type == TokenType.CASE:
            self.advance()
            pattern = self.parse_expression()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            body = self.parse_block()
            cases.append((pattern, body))
        
        self.expect(TokenType.DEDENT)
        
        return MatchExpr(value, cases)

    def parse_return(self) -> ReturnStmt:
        """Parse return statement."""
        self.expect(TokenType.RETURN)
        
        if self.current_token and self.current_token.type in (TokenType.NEWLINE, TokenType.EOF, TokenType.DEDENT):
            return ReturnStmt(None)
        
        value = self.parse_expression()
        return ReturnStmt(value)

    def parse_type_def(self) -> TypeDef:
        """Parse type definition."""
        self.expect(TokenType.TYPE)
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        self.expect(TokenType.INDENT)
        
        variants = []
        
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            self.skip_newlines()
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                break
            
            variant_token = self.expect(TokenType.IDENTIFIER)
            
            fields = []
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                while self.current_token and self.current_token.type != TokenType.RPAREN:
                    field_token = self.expect(TokenType.IDENTIFIER)
                    fields.append(field_token.value)
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
            
            variants.append((variant_token.value, fields))
            self.skip_newlines()
        
        self.expect(TokenType.DEDENT)
        
        return TypeDef(name_token.value, variants)

    def parse_import(self) -> ImportStmt:
        """Parse import statement."""
        self.expect(TokenType.IMPORT)
        module_token = self.expect(TokenType.IDENTIFIER)
        
        alias = None
        if self.current_token and self.current_token.type == TokenType.AS:
            self.advance()
            alias_token = self.expect(TokenType.IDENTIFIER)
            alias = alias_token.value
        
        return ImportStmt(module_token.value, None, alias)

    def parse_from_import(self) -> FromImportStmt:
        """Parse from...import statement."""
        self.expect(TokenType.FROM)
        module_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.IMPORT)
        
        items = []
        while True:
            item_token = self.expect(TokenType.IDENTIFIER)
            item_name = item_token.value
            alias = None
            
            if self.current_token and self.current_token.type == TokenType.AS:
                self.advance()
                alias_token = self.expect(TokenType.IDENTIFIER)
                alias = alias_token.value
            
            items.append((item_name, alias))
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return FromImportStmt(module_token.value, items)

    def parse_block(self) -> List[ASTNode]:
        """Parse a block of statements."""
        statements = []
        self.expect(TokenType.INDENT)
        
        while self.current_token and self.current_token.type != TokenType.DEDENT:
            self.skip_newlines()
            if self.current_token and self.current_token.type == TokenType.DEDENT:
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.DEDENT)
        return statements

    def parse_expression_statement(self) -> ASTNode:
        """Parse expression statement (may include assignment)."""
        expr = self.parse_expression()
        
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            if isinstance(expr, Identifier):
                self.advance()
                value = self.parse_expression()
                return Assignment(expr.name, value)
        
        return expr

    def parse_expression(self) -> ASTNode:
        """Parse expression."""
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        """Parse logical OR."""
        left = self.parse_and()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, 'or', right)
        
        return left

    def parse_and(self) -> ASTNode:
        """Parse logical AND."""
        left = self.parse_not()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            self.advance()
            right = self.parse_not()
            left = BinaryOp(left, 'and', right)
        
        return left

    def parse_not(self) -> ASTNode:
        """Parse logical NOT."""
        if self.current_token and self.current_token.type == TokenType.NOT:
            self.advance()
            operand = self.parse_not()
            return UnaryOp('not', operand)
        
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        """Parse comparison (including 'in' operator)."""
        left = self.parse_bitwise_or()
        
        while self.current_token and self.current_token.type in (
            TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE,
            TokenType.GT, TokenType.GE, TokenType.IN
        ):
            op_token = self.current_token
            op_map = {
                TokenType.EQ: '==',
                TokenType.NE: '!=',
                TokenType.LT: '<',
                TokenType.LE: '<=',
                TokenType.GT: '>',
                TokenType.GE: '>=',
                TokenType.IN: 'in',
            }
            op = op_map[op_token.type]
            self.advance()
            right = self.parse_bitwise_or()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_bitwise_or(self) -> ASTNode:
        """Parse bitwise OR."""
        left = self.parse_bitwise_xor()
        
        while self.current_token and self.current_token.type == TokenType.PIPE:
            self.advance()
            right = self.parse_bitwise_xor()
            left = BinaryOp(left, '|', right)
        
        return left

    def parse_bitwise_xor(self) -> ASTNode:
        """Parse bitwise XOR."""
        left = self.parse_bitwise_and()
        
        while self.current_token and self.current_token.type == TokenType.BIT_XOR:
            self.advance()
            right = self.parse_bitwise_and()
            left = BinaryOp(left, '^', right)
        
        return left

    def parse_bitwise_and(self) -> ASTNode:
        """Parse bitwise AND."""
        left = self.parse_shift()
        
        while self.current_token and self.current_token.type == TokenType.BIT_AND:
            self.advance()
            right = self.parse_shift()
            left = BinaryOp(left, '&', right)
        
        return left

    def parse_shift(self) -> ASTNode:
        """Parse shift operators."""
        left = self.parse_additive()
        
        while self.current_token and self.current_token.type in (TokenType.LSHIFT, TokenType.RSHIFT):
            op = '<<' if self.current_token.type == TokenType.LSHIFT else '>>'
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_additive(self) -> ASTNode:
        """Parse addition and subtraction."""
        left = self.parse_multiplicative()
        
        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.current_token.type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication, division, modulo."""
        left = self.parse_power()
        
        while self.current_token and self.current_token.type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_token = self.current_token
            op = {
                TokenType.STAR: '*',
                TokenType.SLASH: '/',
                TokenType.PERCENT: '%',
            }[op_token.type]
            self.advance()
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_power(self) -> ASTNode:
        """Parse power operator."""
        left = self.parse_unary()
        
        if self.current_token and self.current_token.type == TokenType.POWER:
            self.advance()
            right = self.parse_power()
            return BinaryOp(left, '**', right)
        
        return left

    def parse_unary(self) -> ASTNode:
        """Parse unary operators."""
        if self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.BIT_NOT):
            op_token = self.current_token
            op = {
                TokenType.PLUS: '+',
                TokenType.MINUS: '-',
                TokenType.BIT_NOT: '~',
            }[op_token.type]
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """Parse postfix operations (indexing, attribute access, function calls)."""
        expr = self.parse_primary()
        
        while True:
            if self.current_token and self.current_token.type == TokenType.LBRACKET:
                self.advance()
                
                # Check for slice syntax (start:end:step)
                if self.current_token and self.current_token.type == TokenType.COLON:
                    # [:end] or [:end:step]
                    start = None
                    self.advance()  # Skip colon
                    
                    if self.current_token and self.current_token.type in (TokenType.RBRACKET, TokenType.COLON):
                        end = None
                    else:
                        end = self.parse_expression()
                    
                    step = None
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        self.advance()
                        if self.current_token and self.current_token.type != TokenType.RBRACKET:
                            step = self.parse_expression()
                    
                    self.expect(TokenType.RBRACKET)
                    expr = SliceAccess(expr, start, end, step)
                else:
                    # Could be index or slice with start [start:...]
                    first_expr = self.parse_expression()
                    
                    if self.current_token and self.current_token.type == TokenType.COLON:
                        # It's a slice
                        start = first_expr
                        self.advance()  # Skip colon
                        
                        if self.current_token and self.current_token.type in (TokenType.RBRACKET, TokenType.COLON):
                            end = None
                        else:
                            end = self.parse_expression()
                        
                        step = None
                        if self.current_token and self.current_token.type == TokenType.COLON:
                            self.advance()
                            if self.current_token and self.current_token.type != TokenType.RBRACKET:
                                step = self.parse_expression()
                        
                        self.expect(TokenType.RBRACKET)
                        expr = SliceAccess(expr, start, end, step)
                    else:
                        # Regular index
                        self.expect(TokenType.RBRACKET)
                        expr = IndexAccess(expr, first_expr)
            elif self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()
                attr_token = self.expect(TokenType.IDENTIFIER)
                expr = AttributeAccess(expr, attr_token.value)
            elif self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                args = []
                kwargs = {}
                
                while self.current_token and self.current_token.type != TokenType.RPAREN:
                    arg = self.parse_expression()
                    
                    if self.current_token and self.current_token.type == TokenType.ASSIGN and isinstance(arg, Identifier):
                        self.advance()
                        kwargs[arg.name] = self.parse_expression()
                    else:
                        args.append(arg)
                    
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                        self.skip_newlines_preserve_indentation()
                
                self.expect(TokenType.RPAREN)
                expr = FunctionCall(expr, args, kwargs)
            else:
                break
        
        return expr

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions."""
        if not self.current_token:
            self.error("Unexpected EOF")
        
        # Literals
        if self.current_token.type == TokenType.INTEGER:
            value = int(self.current_token.value)
            self.advance()
            return IntLiteral(value)
        
        elif self.current_token.type == TokenType.FLOAT:
            value = float(self.current_token.value)
            self.advance()
            return FloatLiteral(value)
        
        elif self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return StringLiteral(value)
        
        elif self.current_token.type == TokenType.TRUE:
            self.advance()
            return BoolLiteral(True)
        
        elif self.current_token.type == TokenType.FALSE:
            self.advance()
            return BoolLiteral(False)
        
        elif self.current_token.type == TokenType.NIL:
            self.advance()
            return NilLiteral()
        
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            self.paren_depth += 1
            self.skip_newlines_preserve_indentation()
            
            # Check for empty tuple
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()
                self.paren_depth -= 1
                return TupleLiteral([])
            
            # Parse first expression
            expr = self.parse_expression()
            self.skip_newlines_preserve_indentation()
            
            # Check if it's a tuple (has comma) or just grouped expression
            if self.current_token and self.current_token.type == TokenType.COMMA:
                # It's a tuple
                elements = [expr]
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    self.skip_newlines_preserve_indentation()
                    
                    if self.current_token and self.current_token.type == TokenType.RPAREN:
                        break
                    
                    elements.append(self.parse_expression())
                    self.skip_newlines_preserve_indentation()
                
                self.expect(TokenType.RPAREN)
                self.paren_depth -= 1
                return TupleLiteral(elements)
            else:
                # Just grouped expression
                self.expect(TokenType.RPAREN)
                self.paren_depth -= 1
                return expr
        
        elif self.current_token.type == TokenType.LBRACKET:
            return self.parse_list_or_comprehension()
        
        elif self.current_token.type == TokenType.LBRACE:
            return self.parse_dict_or_set()
        
        elif self.current_token.type == TokenType.LAMBDA:
            return self.parse_lambda()
        
        else:
            self.error(f"Unexpected token: {self.current_token.type.name}")

    def parse_list_or_comprehension(self) -> ASTNode:
        """Parse list literal or list comprehension (multi-line support)."""
        self.expect(TokenType.LBRACKET)
        self.paren_depth += 1
        self.skip_newlines_preserve_indentation()
        
        if self.current_token and self.current_token.type == TokenType.RBRACKET:
            self.advance()
            self.paren_depth -= 1
            return ListLiteral([])
        
        elements = []
        first_elem = self.parse_expression()
        elements.append(first_elem)
        
        # Check for comprehension
        if self.current_token and self.current_token.type == TokenType.FOR:
            self.advance()
            var_token = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.IN)
            iterable = self.parse_expression()
            
            condition = None
            if self.current_token and self.current_token.type == TokenType.IF:
                self.advance()
                condition = self.parse_expression()
            
            self.skip_newlines_preserve_indentation()
            self.expect(TokenType.RBRACKET)
            self.paren_depth -= 1
            return ListComprehension(first_elem, var_token.value, iterable, condition)
        
        # Regular list
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
            self.skip_newlines_preserve_indentation()
            
            if self.current_token and self.current_token.type == TokenType.RBRACKET:
                break
            
            elements.append(self.parse_expression())
            self.skip_newlines_preserve_indentation()
        
        self.skip_newlines_preserve_indentation()
        self.expect(TokenType.RBRACKET)
        self.paren_depth -= 1
        return ListLiteral(elements)

    def parse_dict_or_set(self) -> ASTNode:
        """Parse dictionary or set literal (multi-line support)."""
        self.expect(TokenType.LBRACE)
        self.paren_depth += 1
        self.skip_newlines_preserve_indentation()
        
        if self.current_token and self.current_token.type == TokenType.RBRACE:
            self.advance()
            self.paren_depth -= 1
            return DictLiteral([])
        
        first_key = self.parse_expression()
        
        # Check if it's a dictionary
        if self.current_token and self.current_token.type == TokenType.COLON:
            # Dictionary
            self.advance()
            self.skip_newlines_preserve_indentation()
            first_value = self.parse_expression()
            
            pairs = [(first_key, first_value)]
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                self.skip_newlines_preserve_indentation()
                
                if self.current_token and self.current_token.type == TokenType.RBRACE:
                    break
                
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                self.skip_newlines_preserve_indentation()
                value = self.parse_expression()
                pairs.append((key, value))
                self.skip_newlines_preserve_indentation()
            
            self.skip_newlines_preserve_indentation()
            self.expect(TokenType.RBRACE)
            self.paren_depth -= 1
            return DictLiteral(pairs)
        else:
            # Set (not fully supported, treat as list)
            elements = [first_key]
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                self.skip_newlines_preserve_indentation()
                
                if self.current_token and self.current_token.type == TokenType.RBRACE:
                    break
                
                elements.append(self.parse_expression())
                self.skip_newlines_preserve_indentation()
            
            self.skip_newlines_preserve_indentation()
            self.expect(TokenType.RBRACE)
            self.paren_depth -= 1
            return ListLiteral(elements)

    def parse_lambda(self) -> Lambda:
        """Parse lambda expression."""
        self.expect(TokenType.LAMBDA)
        
        params = []
        while self.current_token and self.current_token.type != TokenType.COLON:
            param_token = self.expect(TokenType.IDENTIFIER)
            params.append(param_token.value)
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
        
        self.expect(TokenType.COLON)
        body = self.parse_expression()
        
        return Lambda(params, body)
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

