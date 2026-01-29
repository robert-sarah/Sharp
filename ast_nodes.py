"""
AST (Abstract Syntax Tree) nodes for Sharp Programming Language.
"""

from dataclasses import dataclass
from typing import List, Optional, Any, Union

# Base node
@dataclass
class ASTNode:
    pass

# Literals
@dataclass
class IntLiteral(ASTNode):
    value: int

@dataclass
class FloatLiteral(ASTNode):
    value: float

@dataclass
class StringLiteral(ASTNode):
    value: str

@dataclass
class BoolLiteral(ASTNode):
    value: bool

@dataclass
class NilLiteral(ASTNode):
    pass

# Collections
@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class DictLiteral(ASTNode):
    pairs: List[tuple]  # List of (key, value) tuples

@dataclass
class TupleLiteral(ASTNode):
    elements: List[ASTNode]

# Identifiers and Variables
@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class VarDecl(ASTNode):
    name: str
    value: ASTNode

# Operations
@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Assignment(ASTNode):
    target: str
    value: ASTNode

@dataclass
class AugmentedAssignment(ASTNode):
    target: str
    op: str
    value: ASTNode

# Functions
@dataclass
class FunctionDef(ASTNode):
    name: str
    params: List[str]
    defaults: List[Optional[ASTNode]]
    body: List[ASTNode]

@dataclass
class FunctionCall(ASTNode):
    func: ASTNode
    args: List[ASTNode]
    kwargs: dict

@dataclass
class Lambda(ASTNode):
    params: List[str]
    body: ASTNode

# Control Flow
@dataclass
class IfExpr(ASTNode):
    condition: ASTNode
    then_body: List[ASTNode]
    elif_parts: List[tuple]  # List of (condition, body) tuples
    else_body: Optional[List[ASTNode]]

@dataclass
class WhileLoop(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ForLoop(ASTNode):
    target: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class MatchExpr(ASTNode):
    value: ASTNode
    cases: List[tuple]  # List of (pattern, body) tuples

@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode]

@dataclass
class BreakStmt(ASTNode):
    pass

@dataclass
class ContinueStmt(ASTNode):
    pass

# Index and Attribute access
@dataclass
class IndexAccess(ASTNode):
    obj: ASTNode
    index: ASTNode

@dataclass
class SliceAccess(ASTNode):
    obj: ASTNode
    start: Optional[ASTNode]
    end: Optional[ASTNode]
    step: Optional[ASTNode]

@dataclass
class AttributeAccess(ASTNode):
    obj: ASTNode
    attr: str

# List comprehension
@dataclass
class ListComprehension(ASTNode):
    expr: ASTNode
    target: str
    iterable: ASTNode
    condition: Optional[ASTNode]

@dataclass
class DictComprehension(ASTNode):
    key: ASTNode
    value: ASTNode
    target: str
    iterable: ASTNode
    condition: Optional[ASTNode]

# Type declarations
@dataclass
class TypeDef(ASTNode):
    name: str
    variants: List[tuple]  # List of (variant_name, fields) tuples

# Imports
@dataclass
class ImportStmt(ASTNode):
    module: str
    items: Optional[List[str]]
    alias: Optional[str]

@dataclass
class FromImportStmt(ASTNode):
    module: str
    items: List[tuple]  # List of (name, alias) tuples

# Program
@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

# Pass statement
@dataclass
class PassStmt(ASTNode):
    pass
