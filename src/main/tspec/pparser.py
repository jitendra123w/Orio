# 
# A PLY-based parser for the TSpec (Tuning Specifier)
#
import re
import tool.ply.lex, tool.ply.yacc
import orio.main.util.globals as g

#----------------------------------------------------------------------------------------------------------------------
# LEXER
# reserved keywords
keywords = [
    'def', 'arg', 'param', 'decl', 'let', 'spec', 'constraint',
    'build', 'build_command', 'batch_command', 'status_command', 'num_procs', 'libs',
    'input_params', 'input_vars', 'static', 'dynamic', 'void', 'char', 'short', 'int', 'long', 'float', 'double',
    'performance_params', 'performance_counter', 'method', 'repetitions',
    'search', 'time_limit', 'algorithm'
]

# map of reserved keywords
reserved = {}
for r in keywords:
    reserved[r] = r.upper()

# tokens
tokens = list(reserved.values()) + ['ID', 'EQ','EXPR', 'EXPR_IDX']

states = (
    ('pyexpr','inclusive'), # lexer state to match arbitrary expressions as raw strings
)

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'

literals = ";[]{}"

# PLY-Lex note: when building the master regular expression, rules are added in the following order:
# 1. All tokens defined by functions are added in the same order as they appear in the lexer file.
# 2. Tokens defined by strings are added next by sorting them in order of decreasing regular expression length (longer expressions are added first).

# count newlines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'[A-Za-z_]([A-Za-z0-9_\.]*[A-Za-z0-9_]+)*'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    #print('lexed %s:%s' %(t.type,t.value))
    return t

def t_EQ(t):
    r'='
    t.lexer.begin('pyexpr')
    return t

def t_pyexpr_EXPR(t):
    r'[^;]+'
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('INITIAL')           
    #print('lexed expr:%s' %t.value)
    return t

def t_EXPR_IDX(t):
    r'\[([^\]])+\]'
    # remove leading and trailing brackets
    t.value = t.lexer.lexdata[(t.lexer.lexpos-len(t.value)+1):t.lexer.lexpos-1]
    return t

# Error handling rule
def t_error(t):
    g.err('orio.main.tspec.pparser.lexer: illegal character (%s) at line %s' % (t.value[0], t.lexer.lineno))
#----------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------
# GRAMMAR
# file spec statements: start symbol when tspecs are in an external file
start = 'fspecs'
def p_fspecs(p):
    ''' fspecs : fspec fspecs
               | fspec
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

#----------------------------------------------------------------------------------------------------------------------
# file spec statement
def p_fspec1(p):
    ''' fspec : let '''
    p[0] = p[1]

def p_fspec2(p):
    ''' fspec : SPEC ID '{' specs '}' '''
    p[0] = (p[1], p.lineno(1), (p[2], p.lineno(2)), p[4])

#----------------------------------------------------------------------------------------------------------------------
# spec body statements: start symbol when tspecs are embedded into annotations
def p_specs(p):
    ''' specs : spec specs
              | spec
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

#----------------------------------------------------------------------------------------------------------------------
# specification statement
def p_spec(p):
    ''' spec : def
             | let
    '''
    p[0] = p[1]

#----------------------------------------------------------------------------------------------------------------------
# definition statement
def p_def(p):
    ''' def : DEF deftype '{' stmts '}' '''
    p[0] = (p[1], p.lineno(1), p[2], p[4])

#----------------------------------------------------------------------------------------------------------------------
# types of a definition statement
def p_def_type(p):
    ''' deftype : BUILD
                | PERFORMANCE_PARAMS
                | PERFORMANCE_COUNTER
                | INPUT_PARAMS
                | INPUT_VARS
                | SEARCH
    '''
    p[0] = (p[1], p.lineno(1))

#----------------------------------------------------------------------------------------------------------------------
# definition body statements
def p_stmts(p):
    ''' stmts : stmt ';' stmts
              | stmt ';'
    '''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

#----------------------------------------------------------------------------------------------------------------------
# definition body statement
def p_stmt(p):
    ''' stmt : let
             | arg
             | param
             | constraint
             | decl
    '''
    p[0] = p[1]

#----------------------------------------------------------------------------------------------------------------------
# let statement
def p_let(p):
    ''' let : LET ID EQ EXPR '''
    p[0] = (p[1], p.lineno(1), (p[2], p.lineno(2)), (p[4], p.lineno(4)))

#----------------------------------------------------------------------------------------------------------------------
# argument statement
def p_arg(p):
    ''' arg : ARG argtype EQ EXPR '''
    p[0] = (p[1], p.lineno(1), p[2], (p[4], p.lineno(4)))

#----------------------------------------------------------------------------------------------------------------------
# types of argument statements
def p_arg_type(p):
    ''' argtype : BUILD_COMMAND
                | BATCH_COMMAND
                | STATUS_COMMAND
                | NUM_PROCS
                | METHOD
                | REPETITIONS
                | ALGORITHM
                | TIME_LIMIT
                | LIBS
    '''
    p[0] = (p[1], p.lineno(1))

#----------------------------------------------------------------------------------------------------------------------
# parameter statement
def p_param(p):
    ''' param : PARAM ID brackets EQ EXPR '''
    is_range = p[3]
    p[0] = (p[1], p.lineno(1), (p[2], p.lineno(2)), is_range, (p[5], p.lineno(5)) )

#----------------------------------------------------------------------------------------------------------------------
# constraint statement
def p_constraint(p):
    ''' constraint : CONSTRAINT ID EQ EXPR '''
    p[0] = (p[1], p.lineno(1), (p[2], p.lineno(2)), (p[4], p.lineno(4)))

#----------------------------------------------------------------------------------------------------------------------
# declaration statement
def p_decl(p):
    ''' decl : DECL dyst type ID arrsizes EQ EXPR
             | DECL dyst type ID arrsizes
    '''
    id_name = (p[4], p.lineno(4))
    types = p[2] + p[3]
    if len(p) == 6:
        p[0] = (p[1], p.lineno(1), id_name, types, p[5], (None, None))
    else:
        p[0] = (p[1], p.lineno(1), id_name, types, p[5], (p[7], p.lineno(7)))

#----------------------------------------------------------------------------------------------------------------------
# optional static or dynamic modifier
def p_dyst(p):
    ''' dyst : DYNAMIC
             | STATIC
             | empty
    '''
    if p[1] <> None:
        p[0] = [(p[1], p.lineno(1))]
    else:
        p[0] = []

#----------------------------------------------------------------------------------------------------------------------
# data type of a declaration
def p_type(p):
    ''' type : VOID
             | CHAR
             | SHORT
             | INT
             | LONG
             | FLOAT
             | DOUBLE
    '''
    p[0] = [(p[1], p.lineno(1))]

#----------------------------------------------------------------------------------------------------------------------
# optional array brackets
def p_brackets(p):
    ''' brackets : '[' ']'
                 | empty
    '''
    if p[1] == None:
        p[0] = False
    else:
        p[0] = True
    
#----------------------------------------------------------------------------------------------------------------------
# optional array size expressions
def p_arrsizes(p):
    ''' arrsizes : EXPR_IDX arrsizes
                 | EXPR_IDX
                 | empty
    '''
    if len(p) == 3:
        p[0] = [(p[1], p.lineno(1))] + p[2]
    elif p[1] == None:
        p[0] = []
    else:
        p[0] = [(p[1], p.lineno(1))]

#----------------------------------------------------------------------------------------------------------------------
# empty/epsilon production
def p_empty(p):
    'empty :'
    pass

#----------------------------------------------------------------------------------------------------------------------
# Error rule for parse errors
def p_error(p):
    g.err("orio.main.tspec.pparser.parser: error in input line #%s, at token-type '%s', token-value '%s'"
          % (p.lineno, p.type, p.value))
#----------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------
def getParser(start_symbol):
    '''Create the parser'''
    _ = tool.ply.lex.lex()
    parser = tool.ply.yacc.yacc(method='LALR', debug=0, start=start_symbol)
    return parser


#--------------------------------------------------------------------------------

class TSpecParser:
    '''The parser of the TSpec language'''

    def __init__(self):
        '''To instantiate a TSpec parser'''
        pass
        
    #----------------------------------------------------------------------------

    def __parse(self, code, line_no, start_symbol):
        '''To parse the given code and return a sequence of statements'''

        # append multiple newlines to imitate the actual line number
        code = ('\n' * (line_no-1)) + code

        # append a newline on the given code
        code += '\n'

        # remove all comments
        code = re.sub(r'#.*?\n', '\n', code)

        # create the parser
        p = getParser(start_symbol)
        
        # parse the tuning specifications
        stmt_seq = p.parse(code)

        # return the statement sequence
        return stmt_seq


    #----------------------------------------------------------------------------

    def parseProgram(self, code, line_no = 1):
        '''To parse the given program body and return a sequence of statements'''
        return self.__parse(code, line_no, 'fspecs')

    #----------------------------------------------------------------------------

    def parseSpec(self, code, line_no = 1):
        '''To parse the given specification body and return a sequence of statements'''
        return self.__parse(code, line_no, 'specs')


