"""
Parser for Sharp Programming Language.
Converts tokens to AST.
"""

from typing import List, Optional, Any
from lexer import Token, TokenType
from ast_nodes import *

class Parser:
    """Parses Sharp tokens into an AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = self.tokens[0] if tokens else None

    def error(self, message: str):
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
            self.error(f"Expected {token_type.name}, got {self.current_token.type.name if self.current_token else 'EOF'}")
        token = self.current_token
        self.advance()
        return token

    def skip_newlines(self):
        """Skip newline tokens."""
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def skip_newlines_and_indents(self):
        """Skip newlines and indents."""
        while self.current_token and self.current_token.type in (TokenType.NEWLINE, TokenType.INDENT):
            self.advance()

    def parse(self) -> Program:
        """Parse the entire program."""
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
        self.skip_newlines()
        
        if not self.current_token or self.current_token.type == TokenType.EOF:
            return None
        
        token_type = self.current_token.type
        
        if token_type == TokenType.DEF:
            return self.parse_function_def()
        elif token_type == TokenType.LET:
            return self.parse_var_decl()
        elif token_type == TokenType.IF:
            return self.parse_if()
        elif token_type == TokenType.WHILE:
            return self.parse_while()
        elif token_type == TokenType.FOR:
            return self.parse_for()
        elif token_type == TokenType.MATCH:
            return self.parse_match()
        elif token_type == TokenType.RETURN:
            return self.parse_return()
        elif token_type == TokenType.BREAK:
            self.advance()
            return BreakStmt()
        elif token_type == TokenType.CONTINUE:
            self.advance()
            return ContinueStmt()
        elif token_type == TokenType.PASS:
            self.advance()
            return PassStmt()
        elif token_type == TokenType.TYPE:
            return self.parse_type_def()
        elif token_type == TokenType.IMPORT:
            return self.parse_import()
        elif token_type == TokenType.FROM:
            return self.parse_from_import()
        else:
            return self.parse_expression_statement()

    def parse_function_def(self) -> FunctionDef:
        """Parse function definition."""
        self.expect(TokenType.DEF)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value
        
        self.expect(TokenType.LPAREN)
        params, defaults = self.parse_parameters()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = self.parse_block()
        
        return FunctionDef(name, params, defaults, body)

    def parse_parameters(self) -> tuple:
        """Parse function parameters."""
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
            else:
                break
        
        return params, defaults

    def parse_var_decl(self) -> VarDecl:
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
        
        # Handle elif
        while self.current_token and self.current_token.type == TokenType.ELIF:
            self.advance()
            elif_cond = self.parse_expression()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            elif_body = self.parse_block()
            elif_parts.append((elif_cond, elif_body))
        
        # Handle else
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
        while self.current_token and self.current_token.type == TokenType.CASE:
            self.advance()
            variant_token = self.expect(TokenType.IDENTIFIER)
            variant_name = variant_token.value
            
            fields = []
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()
                while self.current_token and self.current_token.type != TokenType.RPAREN:
                    field_token = self.expect(TokenType.IDENTIFIER)
                    fields.append(field_token.value)
                    if self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
            
            variants.append((variant_name, fields))
            self.skip_newlines()
        
        self.expect(TokenType.DEDENT)
        
        return TypeDef(name_token.value, variants)

    def parse_import(self) -> ImportStmt:
        """Parse import statement."""
        self.expect(TokenType.IMPORT)
        module_token = self.expect(TokenType.IDENTIFIER)
        module = module_token.value
        
        alias = None
        if self.current_token and self.current_token.type == TokenType.AS:
            self.advance()
            alias_token = self.expect(TokenType.IDENTIFIER)
            alias = alias_token.value
        
        return ImportStmt(module, None, alias)

    def parse_from_import(self) -> FromImportStmt:
        """Parse from...import statement."""
        self.expect(TokenType.FROM)
        module_token = self.expect(TokenType.IDENTIFIER)
        module = module_token.value
        
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
        
        return FromImportStmt(module, items)

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
        elif self.current_token and self.current_token.type in (TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN):
            if isinstance(expr, Identifier):
                op_token = self.current_token
                op = op_token.value or op_token.type.name.replace('_ASSIGN', '').lower()
                self.advance()
                value = self.parse_expression()
                return AugmentedAssignment(expr.name, op, value)
        
        return expr

    def parse_expression(self) -> ASTNode:
        """Parse logical OR expression."""
        return self.parse_or_expr()
    
    def parse_or_expr(self) -> ASTNode:
        """Parse logical OR expression."""
        left = self.parse_and_expr()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            op_token = self.current_token
            self.advance()
            right = self.parse_and_expr()
            left = BinaryOp(left, 'or', right)
        
        return left
    
    def parse_and_expr(self) -> ASTNode:
        """Parse logical AND expression."""
        left = self.parse_not_expr()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            op_token = self.current_token
            self.advance()
            right = self.parse_not_expr()
            left = BinaryOp(left, 'and', right)
        
        return left
    
    def parse_not_expr(self) -> ASTNode:
        """Parse logical NOT expression."""
        if self.current_token and self.current_token.type == TokenType.NOT:
            self.advance()
            expr = self.parse_not_expr()
            return UnaryOp('not', expr)
        
        return self.parse_comparison()
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression including IN operator."""
        left = self.parse_bitwise_or()
        
        while self.current_token and self.current_token.type in (
            TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE, 
            TokenType.GT, TokenType.GE, TokenType.IN
        ):
            op_token = self.current_token
            if op_token.type == TokenType.EQ:
                op = '=='
            elif op_token.type == TokenType.NE:
                op = '!='
            elif op_token.type == TokenType.LT:
                op = '<'
            elif op_token.type == TokenType.LE:
                op = '<='
            elif op_token.type == TokenType.GT:
                op = '>'
            elif op_token.type == TokenType.GE:
                op = '>='
            elif op_token.type == TokenType.IN:
                op = 'in'
            
            self.advance()
            right = self.parse_bitwise_or()
            left = BinaryOp(left, op, right)
        
        return left
        """Parse expression."""
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        """Parse logical OR expression."""
        left = self.parse_and()
        
        while self.current_token and self.current_token.type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, 'or', right)
        
        return left

    def parse_and(self) -> ASTNode:
        """Parse logical AND expression."""
        left = self.parse_not()
        
        while self.current_token and self.current_token.type == TokenType.AND:
            self.advance()
            right = self.parse_not()
            left = BinaryOp(left, 'and', right)
        
        return left

    def parse_not(self) -> ASTNode:
        """Parse logical NOT expression."""
        if self.current_token and self.current_token.type == TokenType.NOT:
            self.advance()
            operand = self.parse_not()
            return UnaryOp('not', operand)
        
        return self.parse_comparison()

    def parse_comparison(self) -> ASTNode:
        """Parse comparison operators."""
        left = self.parse_bitwise_or()
        
        while self.current_token and self.current_token.type in (TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op_token = self.current_token
            op = {
                TokenType.EQ: '==',
                TokenType.NE: '!=',
                TokenType.LT: '<',
                TokenType.LE: '<=',
                TokenType.GT: '>',
                TokenType.GE: '>=',
            }[op_token.type]
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
        """Parse bitwise shift operators."""
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
        """Parse multiplication, division, and modulo."""
        left = self.parse_power()
        
        while self.current_token and self.current_token.type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = '*' if self.current_token.type == TokenType.STAR else (
                '/' if self.current_token.type == TokenType.SLASH else '%'
            )
            self.advance()
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_power(self) -> ASTNode:
        """Parse exponentiation."""
        left = self.parse_unary()
        
        if self.current_token and self.current_token.type == TokenType.POWER:
            self.advance()
            right = self.parse_power()  # Right associative
            left = BinaryOp(left, '**', right)
        
        return left

    def parse_unary(self) -> ASTNode:
        """Parse unary operators."""
        if self.current_token and self.current_token.type in (TokenType.MINUS, TokenType.PLUS, TokenType.BIT_NOT):
            op = '-' if self.current_token.type == TokenType.MINUS else (
                '+' if self.current_token.type == TokenType.PLUS else '~'
            )
            self.advance()
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """Parse postfix expressions (function calls, indexing, attribute access)."""
        expr = self.parse_primary()
        
        while True:
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                # Function call
                self.advance()
                args, kwargs = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                expr = FunctionCall(expr, args, kwargs)
            elif self.current_token and self.current_token.type == TokenType.LBRACKET:
                # Indexing
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            elif self.current_token and self.current_token.type == TokenType.DOT:
                # Attribute access
                self.advance()
                attr_token = self.expect(TokenType.IDENTIFIER)
                expr = AttributeAccess(expr, attr_token.value)
            else:
                break
        
        return expr

    def parse_arguments(self) -> tuple:
        """Parse function arguments."""
        args = []
        kwargs = {}
        
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            # Check for keyword argument
            if self.current_token.type == TokenType.IDENTIFIER and self.peek() and self.peek().type == TokenType.ASSIGN:
                key_token = self.current_token
                self.advance()
                self.expect(TokenType.ASSIGN)
                value = self.parse_expression()
                kwargs[key_token.value] = value
            else:
                args.append(self.parse_expression())
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        
        return args, kwargs

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions (literals, identifiers, etc.)."""
        token = self.current_token
        
        if not token:
            self.error("Unexpected end of input")
        
        if token.type == TokenType.INTEGER:
            self.advance()
            return IntLiteral(token.value)
        
        elif token.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteral(token.value)
        
        elif token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)
        
        elif token.type == TokenType.TRUE:
            self.advance()
            return BoolLiteral(True)
        
        elif token.type == TokenType.FALSE:
            self.advance()
            return BoolLiteral(False)
        
        elif token.type == TokenType.NIL:
            self.advance()
            return NilLiteral()
        
        elif token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value)
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            
            # Check for tuple
            if self.current_token and self.current_token.type == TokenType.COMMA:
                elements = [expr]
                while self.current_token and self.current_token.type == TokenType.COMMA:
                    self.advance()
                    if self.current_token and self.current_token.type == TokenType.RPAREN:
                        break
                    elements.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return TupleLiteral(elements)
            
            self.expect(TokenType.RPAREN)
            return expr
        
        elif token.type == TokenType.LBRACKET:
            return self.parse_list_or_comprehension()
        
        elif token.type == TokenType.LBRACE:
            return self.parse_dict_or_set()
        
        elif token.type == TokenType.LAMBDA:
            return self.parse_lambda()
        
        else:
            self.error(f"Unexpected token: {token.type.name}")

    def parse_list_or_comprehension(self) -> ASTNode:
        """Parse list literal or list comprehension."""
        self.expect(TokenType.LBRACKET)
        
        if self.current_token and self.current_token.type == TokenType.RBRACKET:
            self.advance()
            return ListLiteral([])
        
        expr = self.parse_expression()
        
        # Check for comprehension
        if self.current_token and self.current_token.type == TokenType.FOR:
            self.advance()
            target_token = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.IN)
            iterable = self.parse_expression()
            
            condition = None
            if self.current_token and self.current_token.type == TokenType.IF:
                self.advance()
                condition = self.parse_expression()
            
            self.expect(TokenType.RBRACKET)
            return ListComprehension(expr, target_token.value, iterable, condition)
        
        # Regular list literal
        elements = [expr]
        while self.current_token and self.current_token.type == TokenType.COMMA:
            self.advance()
            if self.current_token and self.current_token.type == TokenType.RBRACKET:
                break
            elements.append(self.parse_expression())
        
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements)

    def parse_dict_or_set(self) -> ASTNode:
        """Parse dictionary or set literal."""
        self.expect(TokenType.LBRACE)
        
        if self.current_token and self.current_token.type == TokenType.RBRACE:
            self.advance()
            return DictLiteral([])
        
        first_expr = self.parse_expression()
        
        if self.current_token and self.current_token.type == TokenType.COLON:
            # Dictionary
            self.advance()
            first_value = self.parse_expression()
            
            pairs = [(first_expr, first_value)]
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token and self.current_token.type == TokenType.RBRACE:
                    break
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                value = self.parse_expression()
                pairs.append((key, value))
            
            self.expect(TokenType.RBRACE)
            return DictLiteral(pairs)
        else:
            # Could be dict comprehension or just list
            self.error("Set literals not yet supported, use list instead")

    def parse_lambda(self) -> Lambda:
        """Parse lambda expression."""
        self.expect(TokenType.LAMBDA)
        
        params = []
        if self.current_token and self.current_token.type == TokenType.IDENTIFIER:
            param_token = self.current_token
            self.advance()
            params.append(param_token.value)
            
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                param_token = self.expect(TokenType.IDENTIFIER)
                params.append(param_token.value)
        
        self.expect(TokenType.COLON)
        body = self.parse_expression()
        
        return Lambda(params, body)
