
from collections import deque

from lexer import tokens
from funcDir import FunctionDirectory
from quads import Quads

""" State variables (accessible in `p` within each production)
- funcDir -> Function directory
- quads -> Quadruple handler
"""

# Precedence rules for arithmetic
precedence = (
  ('left', '|'),
  ('left', '&'),
  ('left', 'IS_EQUAL', 'IS_NOT_EQUAL', '<', 'LESS_THAN_OR_EQUAL', '>', 'MORE_THAN_OR_EQUAL'),
  ('left', '+', '-'),
  ('left', '*', '/', '%')
)

# Parsing productions
# PROGRAMA
def p_programa(p):
  "programa : PROGRAMA found_program ID found_program_name ';' vars functions PRINCIPAL '(' ')' '{' body '}'"
  p.quads.addEndQuad()
  p[0] = p

def p_found_program(p):
  "found_program : empty"
  p.funcDir = FunctionDirectory()
  p.quads = Quads()

def p_found_program_name(p):
  'found_program_name : empty'
  p.funcDir.addFunction(p[-1])
  p.funcDir.setGlobalFunction(p[-1])

# VARS
def p_vars(p):
  """vars : VAR found_var var_declare
          | empty"""
  pass

def p_found_var(p):
  "found_var : empty"
  p.funcDir.createVarTable()

def p_var_declare(p):
  """var_declare : type ':' var_name ';' var_declare
                 | type ':' var_name ';'"""
  pass

def p_var_name(p):
  """var_name : variable p_found_var_name ',' var_name
              | variable p_found_var_name"""
  pass

def p_found_var_name(p):
  "p_found_var_name : empty"
  var = p[-1]
  if p.funcDir.varExists(var):
    s_error(p.lineno, p.lexpos, f'Variable "{var}" already exists!"')
  else:
    p.funcDir.addVar(var[0], var[1])

def p_variable_mat(p):
  "variable : ID '[' CTE_INT ']' '[' CTE_INT ']'"
  p[0] = (p[1], 2)

def p_variable_list(p):
  "variable : ID '[' CTE_INT ']'"
  p[0] = (p[1], 1)

def p_variable(p):
  "variable : ID"
  p[0] = (p[1], 0)

# TYPE
def p_type(p):
  """type : INT
          | FLOAT
          | CHAR
          | BOOL"""
  p.funcDir.setCurrentType(p[1])
  p[0] = p[1]

# FUNCTIONS
# TODO: Missing logic for functions parameters and their types
def p_functions(p):
  """functions : FUNCION func_type ID found_func_name '(' func_params ')' vars found_func_start '{' body '}' found_func_end functions
               | empty"""
  pass

def p_func_type(p):
  """func_type : type
               | VOID"""
  if p[1] == 'void':
    p.funcDir.setCurrentType('void')

def p_found_func_name(p):
  "found_func_name : empty"
  func = p[-1]
  if p.funcDir.functionExists(func):
    s_error(p.lineno, p.lexpos, f'Function "{func}" already exists!"')
  else:
    p.funcDir.addFunction(func)
    p.funcDir.createVarTable()

def p_func_params(p):
  """func_params : func_param
                 | empty"""
  pass

def p_func_param(p):
  """func_param : type variable found_func_param ',' func_param
                | type variable found_func_param"""
  pass

def p_found_func_param(p):
  "found_func_param : empty"
  param = p[-1]
  if p.funcDir.varExists(param):
    s_error(p.lineno, p.lexpos, f'Multiple declaration of "{param}"!')
  else:
    p.funcDir.addVar(param[0], param[1])
    p.funcDir.addFuncParam()

def p_found_func_start(p):
  "found_func_start : empty"
  p.funcDir.setQuadStart(p.quads.getQuadCount())

def p_found_func_end(p):
  "found_func_end : empty"
  p.funcDir.deleteVarTable()
  p.quads.resetTemporals()
  p.quads.addEndFuncQuad()

# BODY
# TODO: Missing functionality
def p_body(p):
  """body : statement body
          | statement"""
  pass

def p_statement(p):
  """statement : assignment
               | call_func
               | return
               | read
               | write
               | if
               | for
               | while"""
  pass

def p_assignment(p):
  "assignment : expr_var '=' found_expr_duo_op expr found_assignment_end ';'"
  pass

def p_found_assignment_end(p):
  "found_assignment_end : empty"
  p.quads.addAssignQuad()

# TODO: Missing logic for calling functions
def p_call_func(p):
  "call_func : ID found_call_func_name '(' call_func_params ')' found_call_func_end ';'"
  pass

def p_found_call_func_name(p):
  """found_call_func_name : empty"""
  func = p[-1]
  if p.funcDir.functionExists(func):
    p.quads.addEraQuad()
    p.quads.pushFunction(func)
  else:
    raise Exception(f'Function {func}() does not exist!')

def p_call_func_params(p):
  """call_func_params : call_func_param
                      | empty"""
  pass

def p_call_func_param(p):
  """call_func_param : expr func_single_step ',' call_func_param
                     | expr func_single_step"""
  pass

def p_func_single_step(p):
  "func_single_step : empty"
  target_param = p.funcDir.getParamOfFunc(p.quads.getTopFunction())
  p.quads.addParamQuad(target_param, p.funcDir.getParamCount())
  p.funcDir.incrementParamCount()
  pass

def p_found_call_func_end(p):
  "found_call_func_end : empty"
  func = p.quads.popFunction()
  if p.funcDir.verifyParams(func):
    p.quads.addGoSubQuad(func, p.funcDir.getQuadStartOfFunc(func))
  else:
    raise Exception(f'Wrong number of parameters in {func}!')

# TODO: Missing logic for return
def p_return(p):
  "return : REGRESA '(' expr ')' ';'"
  pass

# TODO: Missing logic for read
def p_read(p):
  "read : LEE '(' read_params ')' ';'"
  pass

def p_read_params(p):
  """read_params : expr_var ',' read_params
                 | expr_var"""
  pass

# TODO: Missing logic for write
def p_write(p):
  "write : ESCRIBE '(' write_params ')' ';'"
  pass

def p_write_params(p):
  """write_params : expr_var ',' write_params
                  | expr_var"""
  pass

def p_if(p):
  """if : SI '(' expr ')' found_if_expr ENTONCES '{' body '}'
        | SI '(' expr ')' found_if_expr ENTONCES '{' body '}' else"""
  p.quads.completeIfQuad()

def p_found_if_expr(p):
  "found_if_expr : empty"
  p.quads.addIfQuad()

def p_else(p):
  "else : SINO found_else '{' body '}'"
  pass

def p_found_else(p):
  "found_else : empty"
  p.quads.addElseQuad()

# TODO: Missing logic for 'for' loops (ask about how this works)
def p_for(p):
  "for : DESDE ID ':' expr HASTA expr HACER '{' body '}'"
  pass

def p_while(p):
  "while : MIENTRAS found_while '(' expr ')' found_while_expr HAZ '{' body '}'"
  p.quads.completeWhileQuad()

def p_found_while(p):
  "found_while : empty"
  p.quads.prepareWhile()

def p_found_while_expr(p):
  "found_while_expr : empty"
  p.quads.addWhileQuad()

# EXPRESSION -> Order of operator precedence:
# Factors (*, /, %) > Arithmetic (+, -) > Comparison (==, !=, <, <=, >, >=) > Logic (&, |)
def p_expr(p):
  "expr : expr_logic"
  pass

def p_expr_logic(p):
  "expr_logic : expr_compare found_expr_logic expr_logic2"
  pass

def p_expr_logic2(p):
  """expr_logic2 : '&' found_expr_duo_op expr_logic
                 | '|' found_expr_duo_op expr_logic
                 | empty"""
  pass

def p_found_expr_logic(p):
  "found_expr_logic : empty"
  p.quads.addDualOpQuad(['&', '|'])

def p_expr_compare(p):
  "expr_compare : expr_arith found_expr_compare expr_compare2"
  pass

def p_expr_compare2(p):
  """expr_compare2 : IS_EQUAL found_expr_duo_op expr_compare
                   | IS_NOT_EQUAL found_expr_duo_op expr_compare
                   | '<' found_expr_duo_op expr_compare
                   | LESS_THAN_OR_EQUAL found_expr_duo_op expr_compare
                   | '>' found_expr_duo_op expr_compare
                   | MORE_THAN_OR_EQUAL found_expr_duo_op expr_compare
                   | empty"""
  pass

def p_found_expr_compare(p):
  "found_expr_compare : empty"
  p.quads.addDualOpQuad(['==', '!=', '<', '<=', '>', '>='])

def p_expr_arith(p):
  "expr_arith : expr_factor found_expr_arith expr_arith2"
  pass

def p_expr_arith2(p):
  """expr_arith2 : '+' found_expr_duo_op expr_arith
                 | '-' found_expr_duo_op expr_arith
                 | empty"""
  pass

def p_found_expr_arith(p):
  "found_expr_arith : empty"
  p.quads.addDualOpQuad(['+', '-'])

def p_expr_factor(p):
  "expr_factor : expr_atom found_expr_factor expr_factor2"
  pass

def p_expr_factor2(p):
  """expr_factor2 : '*' found_expr_duo_op expr_factor
                  | '/' found_expr_duo_op expr_factor
                  | '%' found_expr_duo_op expr_factor
                  | empty"""
  pass

def p_found_expr_factor(p):
  "found_expr_factor : empty"
  p.quads.addDualOpQuad(['*', '/', '%'])

def p_found_expr_duo_op(p):
  "found_expr_duo_op : empty"
  p.quads.pushOperator(p[-1])

def p_expr_atom(p):
  """expr_atom : expr_group
               | expr_mono expr_var"""
  pass

def p_expr_group(p):
  "expr_group : '(' found_expr_duo_op expr ')'"
  p.quads.popOperator()

def p_expr_mono_op(p):
  """expr_mono : '-'
               | '!'
               | '$'
               | '?'
               | empty"""
  pass

def p_expr_var_mat_elem(p):
  "expr_var : ID '[' expr ']' '[' expr ']'"
  var = p.funcDir.getVar(p[1], 2)
  p.quads.pushVar(var.name, var.vartype)

def p_expr_var_list_elem(p):
  "expr_var : ID '[' expr ']'"
  var = p.funcDir.getVar(p[1], 1)
  p.quads.pushVar(var.name, var.vartype)

def p_expr_var_atom(p):
  "expr_var : ID"
  var = p.funcDir.getVar(p[1], 0)
  p.quads.pushVar(var.name, var.vartype)

def p_cte(p):
  """expr_var : CTE_INT
              | CTE_FLOAT
              | CTE_CHAR
              | CTE_BOOL"""
  t = None
  if (type(p[1]) is int):
    t = 'int'
  elif (type(p[1]) is float):
    t = 'float'
  elif (type(p[1]) is bool):
    t = 'bool'
  else:
    t = 'char'
  p.quads.pushVar(p[1], t)

def p_empty(p):
  "empty :"
  pass

# Error handling
def p_error(p):
  raise Exception(f'({p.lineno}:{p.lexpos}) Syntax error at "{p.value}"')

def s_error(lineno, lexpos, msg):
  raise Exception(f'({lineno}:{lexpos} - {msg}')
