#
# The classes for the abstract syntax tree (AST)
#
#  AST 
#   |
#   +-- Exp 
#   |    |
#   |    +-- NumLitExp
#   |    +-- StringLitExp
#   |    +-- IdentExp
#   |    +-- ArrayRefExp 
#   |    +-- FunCallExp 
#   |    +-- UnaryExp 
#   |    +-- BinOpExp 
#   |    +-- ParenthExp
#   |
#   +-- Stmt 
#   |    |
#   |    +-- ExpStmt 
#   |    +-- CompStmt 
#   |    +-- IfStmt 
#   |    +-- ForStmt 
#   |    +-- AssignStmt
#   |    +-- TransformStmt 
#   |
#   +-- NewAST 
#        |
#        +-- VarDecl
#        +-- FieldDecl 
#        +-- FunDecl
#        +-- Pragma 
#        +-- Container
#
# - The NewAST is an AST used only in the output code generation. Such separation is needed to
#   simplify the input language.
#

import codegen

#-----------------------------------------------
# AST - Abstract Syntax Tree
#-----------------------------------------------

class AST:

    def __init__(self, line_no = ''):
        '''Create an abstract syntax tree node'''
        self.line_no = line_no           # may be null (i.e. empty string)
        
    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        raise NotImplementedError('%s: abstract function "replicate" not implemented' %
                                  self.__class__.__name__)

    def __repr__(self):
        '''Return a string representation for this AST object'''
        return codegen.CodeGen().generate(self)

    def __str__(self):
        '''Return a string representation for this AST object'''
        return repr(self)
    
#-----------------------------------------------
# Expression
#-----------------------------------------------

class Exp(AST):

    def __init__(self, line_no = ''):
        '''Create an expression'''
        AST.__init__(self, line_no)

#-----------------------------------------------
# Number Literal
#-----------------------------------------------

class NumLitExp(Exp):

    INT = 1
    FLOAT = 2
    
    def __init__(self, val, lit_type, line_no = ''):
        '''Create a numeric literal'''
        Exp.__init__(self, line_no)
        self.val = val
        self.lit_type = lit_type

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return NumLitExp(self.val, self.lit_type, self.line_no)
        
#-----------------------------------------------
# String Literal
#-----------------------------------------------

class StringLitExp(Exp):

    def __init__(self, val, line_no = ''):
        '''Create a string literal'''
        Exp.__init__(self, line_no)
        self.val = val

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return StringLitExp(self.val, self.line_no)
        
#-----------------------------------------------
# Identifier
#-----------------------------------------------

class IdentExp(Exp):

    def __init__(self, name, line_no = ''):
        '''Create an identifier'''
        Exp.__init__(self, line_no)
        self.name = name
        
    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return IdentExp(self.name, self.line_no)

#-----------------------------------------------
# Array Reference
#-----------------------------------------------

class ArrayRefExp(Exp):

    def __init__(self, exp, sub_exp, line_no = ''):
        '''Create an array reference'''
        Exp.__init__(self, line_no)
        self.exp = exp
        self.sub_exp = sub_exp

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return ArrayRefExp(self.exp.replicate(), self.sub_exp.replicate(), self.line_no)
        
#-----------------------------------------------
# Function Call
#-----------------------------------------------

class FunCallExp(Exp):

    def __init__(self, exp, args, line_no = ''):
        '''Create a function call'''
        Exp.__init__(self, line_no)
        self.exp = exp
        self.args = args
        
    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return FunCallExp(self.exp.replicate(), [a.replicate() for a in self.args], self.line_no)

#-----------------------------------------------
# Unary Expression
#-----------------------------------------------

class UnaryExp(Exp):
    PLUS = 1
    MINUS = 2
    LNOT = 3
    PRE_INC = 4
    PRE_DEC = 5
    POST_INC = 6
    POST_DEC = 7
    DEREF = 8
    ADDRESSOF = 9

    def __init__(self, exp, op_type, line_no = ''):
        '''Create a unary operation expression'''
        Exp.__init__(self, line_no)
        self.exp = exp
        self.op_type = op_type

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return UnaryExp(self.exp.replicate(), self.op_type, self.line_no)

#-----------------------------------------------
# Binary Operation
#-----------------------------------------------

class BinOpExp(Exp):
    MUL = 1
    DIV = 2
    MOD = 3
    ADD = 4
    SUB = 5
    LT = 6
    GT = 7
    LE = 8
    GE = 9
    EQ = 10
    NE = 11
    LOR = 12
    LAND = 13
    COMMA = 14
    EQ_ASGN = 15
    ASGN_ADD = 16
    ASGN_SHR = 17
    ASGN_SHL = 18

    def __init__(self, lhs, rhs, op_type, line_no = ''):
        '''Create a binary operation expression'''
        Exp.__init__(self, line_no)
        self.lhs = lhs
        self.rhs = rhs
        self.op_type = op_type

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return BinOpExp(self.lhs.replicate(), self.rhs.replicate(), self.op_type, self.line_no)

#-----------------------------------------------
# Parenthesized Expression
#-----------------------------------------------

class ParenthExp(Exp):

    def __init__(self, exp, line_no = ''):
        '''Create a parenthesized expression'''
        Exp.__init__(self, line_no)
        self.exp = exp

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return ParenthExp(self.exp.replicate(), self.line_no)
        
#-----------------------------------------------
# Comments
#-----------------------------------------------
class Comment(AST):

    def __init__(self, comment, line_no = ''):
        AST.__init__(self,line_no)
        self.text = comment

    def replicate(self):
        '''Replicates the comment node'''
        return Comment(self.text, self.line_no)

#-----------------------------------------------
# Statement
#-----------------------------------------------

class Stmt(AST):

    def __init__(self, line_no = '', label=None):
        '''Create a statement'''
        AST.__init__(self, line_no)
        self.label = None
    
    def setLabel(self, label):
        self.label = label
    
    def getLabel(self):
        return self.label
    

#-----------------------------------------------
# Expression Statement
#-----------------------------------------------

class ExpStmt(Stmt):

    def __init__(self, exp, line_no = '', label=None):
        '''Create an expression statement'''
        Stmt.__init__(self, line_no, label)
        self.exp = exp         # may be null

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        r_e = self.exp
        if r_e:
            r_e = r_e.replicate()
        return ExpStmt(r_e, self.line_no, self.label)

class GotoStmt(Stmt):
    def __init__(self, target, line_no = '', label=None):
        '''Create an expression statement'''
        Stmt.__init__(self, line_no, label)
        self.target = target

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return GotoStmt(self.target, self.line_no, self.label)
     
#-----------------------------------------------
# Compound Statement
#-----------------------------------------------

class CompStmt(Stmt):

    def __init__(self, stmts, line_no = '', label=None):
        '''Create a compound statement'''
        Stmt.__init__(self, line_no, label)
        self.stmts = stmts

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return CompStmt([s.replicate() for s in self.stmts], self.line_no, self.label)
    
#-----------------------------------------------
# If-Then-Else
#-----------------------------------------------

class IfStmt(Stmt):

    def __init__(self, test, true_stmt, false_stmt = None, line_no = '', label=None):
        '''Create an if statement'''
        Stmt.__init__(self, line_no, label)
        self.test = test
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt           # may be null

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        f_s = self.false_stmt
        if f_s:
            f_s = f_s.replicate()
        return IfStmt(self.test.replicate(), self.true_stmt.replicate(), f_s, self.line_no, self.label)

#-----------------------------------------------
# For Loop
#-----------------------------------------------

class ForStmt(Stmt):

    def __init__(self, init, test, itr, stmt, line_no = '', label=None):
        '''Create a for-loop statement'''
        Stmt.__init__(self, line_no, label)
        self.init = init      # may be null
        self.test = test      # may be null
        self.iter = itr      # may be null
        self.stmt = stmt

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        r_in = self.init
        r_t = self.test
        r_it = self.iter
        if r_in:
            r_in = r_in.replicate()
        if r_t:
            r_t = r_t.replicate()
        if r_it:
            r_it = r_it.replicate()
        return ForStmt(r_in, r_t, r_it, self.stmt.replicate(), self.line_no, self.label)

#-----------------------------------------------
# Assignment
#-----------------------------------------------

class AssignStmt(Stmt):

    def __init__(self, var, exp, line_no = '', label=None):
        '''Create a statement'''
        Stmt.__init__(self, line_no, label)
        self.var = var
        self.exp = exp

    def replicate(self):
        '''Replicate this node'''
        return AssignStmt(self.var, self.exp.replicate(), self.line_no, self.label)

#-----------------------------------------------
# Transformation
#-----------------------------------------------

class TransformStmt(Stmt):

    def __init__(self, name, args, stmt, line_no = '', label=None):
        '''Create a transformation statement'''
        Stmt.__init__(self, line_no, label)
        self.name = name
        self.args = args
        self.stmt = stmt

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return TransformStmt(self.name, self.args[:], self.stmt.replicate(), self.line_no)

#-----------------------------------------------
# New AST
#-----------------------------------------------

class NewAST(AST):

    def __init__(self, line_no = ''):
        '''Create a newly-added statement'''
        AST.__init__(self, line_no)

#-----------------------------------------------
# Variable Declaration
#-----------------------------------------------

class VarDecl(NewAST):

    def __init__(self, type_name, var_names, line_no = ''):
        '''Create a variable declaration'''
        NewAST.__init__(self, line_no)
        self.type_name = type_name
        self.var_names = var_names

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return VarDecl(self.type_name, self.var_names[:], self.line_no)

class VarDeclInit(NewAST):

    def __init__(self, type_name, var_name, init_exp, line_no = ''):
        '''Create an initializing variable declaration'''
        NewAST.__init__(self, line_no)
        self.type_name = type_name
        self.var_name  = var_name
        self.init_exp  = init_exp

    def replicate(self):
        return VarDeclInit(self.type_name, self.var_name, self.init_exp, self.line_no)

#-----------------------------------------------
# Field Declaration
#-----------------------------------------------

class FieldDecl(NewAST):

    def __init__(self, ty, name, line_no = ''):
        '''Create a field declaration'''
        NewAST.__init__(self, line_no)
        self.ty = ty
        self.name = name

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return FieldDecl(self.ty, self.name, self.line_no)

#-----------------------------------------------
# Function Declaration
#-----------------------------------------------

class FunDecl(NewAST):

    def __init__(self, name, return_type, modifiers, params, body, line_no = ''):
        '''Create a function declaration'''
        NewAST.__init__(self, line_no)
        self.name = name
        self.return_type = return_type
        self.modifiers = modifiers
        self.params = params
        self.body = body # a body should be a compound stmt

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return FunDecl(self.fun_name, self.return_type, self.modifiers[:], self.params[:], self.body.replicate(), self.line_no)

#-----------------------------------------------
# Pragma Directive
#-----------------------------------------------

class Pragma(NewAST):

    def __init__(self, pstring, line_no = ''):
        '''Create a pragma directive'''
        NewAST.__init__(self, line_no)
        self.pstring = pstring

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return Pragma(self.pstring, self.line_no)

#-----------------------------------------------
# Container
#-----------------------------------------------

class Container(NewAST):

    def __init__(self, ast, line_no = ''):
        '''Create a container AST (to protect the contained AST from any code transformations)'''
        NewAST.__init__(self, line_no)
        self.ast = ast

    def replicate(self):
        '''Replicate this abstract syntax tree node'''
        return Container(self.ast.replicate(), self.line_no)

#-----------------------------------------------
# While Loop
#-----------------------------------------------

class WhileStmt(NewAST):

    def __init__(self, test, stmt, line_no = ''):
        NewAST.__init__(self, line_no)
        self.test = test
        self.stmt = stmt
    
    def replicate(self):
        return WhileStmt(self.test.replicate(), self.stmt.replicate(), self.line_no)

#-----------------------------------------------
# Cast expression
#-----------------------------------------------

class CastExpr(NewAST):

    def __init__(self, ty, expr, line_no = ''):
        NewAST.__init__(self, line_no)
        self.ctype = ty
        self.expr = expr
    
    def replicate(self):
        return CastExpr(self.ctype, self.expr.replicate(), self.line_no)

