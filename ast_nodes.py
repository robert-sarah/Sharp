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
# Classes and OOP
@dataclass
class ClassDef(ASTNode):
    name: str
    bases: List[str]  # Base class names
    body: List[ASTNode]

@dataclass
class MethodDef(ASTNode):
    name: str
    params: List[str]
    defaults: List[Optional[ASTNode]]
    body: List[ASTNode]
    decorators: List[str]  # List of decorator names

@dataclass
class SelfRef(ASTNode):
    pass

@dataclass
class SuperCall(ASTNode):
    args: List[ASTNode]

# Decorators
@dataclass
class Decorator(ASTNode):
    name: str
    args: List[ASTNode]

@dataclass
class DecoratedFunction(ASTNode):
    decorators: List[ASTNode]  # List of Decorator nodes
    func: FunctionDef

@dataclass
class DecoratedClass(ASTNode):
    decorators: List[ASTNode]  # List of Decorator nodes
    cls: 'ClassDef'

# Type Annotations
@dataclass
class TypeAnnotation(ASTNode):
    name: str
    annotation: str  # Type annotation as string

@dataclass
class FunctionDefWithTypes(ASTNode):
    name: str
    params: List[str]
    param_types: List[Optional[str]]  # Type annotations for params
    return_type: Optional[str]
    defaults: List[Optional[ASTNode]]
    body: List[ASTNode]

# Exception Handling
@dataclass
class TryStmt(ASTNode):
    body: List[ASTNode]
    except_handlers: List['ExceptHandler']  # List of except clauses
    else_body: Optional[List[ASTNode]]  # Else clause (if no exception)
    finally_body: Optional[List[ASTNode]]  # Finally clause (always runs)

@dataclass
class ExceptHandler(ASTNode):
    exception_type: Optional[str]  # None means catch-all
    var_name: Optional[str]  # Variable name to bind exception
    body: List[ASTNode]

@dataclass
class RaiseStmt(ASTNode):
    exception: Optional[ASTNode]  # Exception to raise
    cause: Optional[ASTNode]  # Cause (from clause)

@dataclass
class WithStmt(ASTNode):
    context_var: Optional[str]
    context_expr: ASTNode
    body: List[ASTNode]

# Generators
@dataclass
class YieldStmt(ASTNode):
    value: Optional[ASTNode]

@dataclass
class GeneratorExpr(ASTNode):
    expr: ASTNode
    target: str
    iterable: ASTNode
    condition: Optional[ASTNode]

# Async/Await
@dataclass
class AsyncFunctionDef(ASTNode):
    name: str
    params: List[str]
    defaults: List[Optional[ASTNode]]
    body: List[ASTNode]

@dataclass
class AwaitExpr(ASTNode):
    value: ASTNode

@dataclass
class AsyncForLoop(ASTNode):
    target: str
    iterable: ASTNode
    body: List[ASTNode]

@dataclass
class AsyncWithStmt(ASTNode):
    context_var: Optional[str]
    context_expr: ASTNode
    body: List[ASTNode]

# *args and **kwargs
@dataclass
class VarArgs(ASTNode):
    args: List[ASTNode]  # Arguments list
    kwargs: dict  # Keyword arguments

# Unpacking
@dataclass
class UnpackingAssignment(ASTNode):
    targets: List[str]  # a, b, *rest = values
    values: ASTNode

# Scope modifiers
@dataclass
class GlobalStmt(ASTNode):
    """Global statement: global x, y, z"""
    names: List[str]

@dataclass
class NonlocalStmt(ASTNode):
    """Nonlocal statement: nonlocal x, y"""
    names: List[str]