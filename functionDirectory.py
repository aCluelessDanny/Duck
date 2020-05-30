
from collections import defaultdict

## -- CONSTANT
class Constant():
  def __init__(self, value, vartype, vAddr):
    self.value = value
    self.vartype = vartype
    self.vAddr = vAddr


## -- VARIABLE
class Var():
  def __init__(self, name, vartype, vAddr):
    self.name = name
    self.vartype = vartype
    self.dims = []
    self.vAddr = vAddr


## -- FUNCTION
class Function():
  def __init__(self, name, returnType, debug):
    self.debug = debug
    self.name = name
    self.returnType = returnType
    self.returnAddr = None
    self.quadStart = None
    self.varTable = None
    self.paramTable = []
    self.era = []

  ## GETTERS
  # Get variable
  def getVar(self, name):
    return self.varTable[name]

  # Get dimensions of a specified variable
  def getDimensionsOfVar(self, name):
    return self.varTable[name].dims

  # Get return address for function
  def getReturnAddr(self):
    return self.returnAddr

  ## SETTERS
  # Set return address for function
  def setReturnAddr(self, addr):
    self.returnAddr = addr

  # Set start of quad for function
  def setQuadStart(self, qs):
    self.quadStart = qs

  # Set "era" (local and temporary counters)
  def setEra(self, era):
    self.era = era

  ## PUSH/ADD
  # Add variable
  def addVar(self, name, vartype, vAddr):
    self.varTable[name] = Var(name, vartype, vAddr)

    if self.debug:
      v = self.varTable[name]
      print(f'\t\t\t\t\t> VAR: {v.name} - {v.vartype} -> {v.vAddr}')

  # Add dimension to var
  def addDimensionToVar(self, var, dim):
    self.varTable[var].dims.append(dim)

    if self.debug:
      v = self.varTable[var]
      space = 1
      for i in v.dims:
        space *= i
      space += v.vAddr - 1

      print(f'\t\t\t\t\t>> VAR: {v.name} - {v.vartype}{v.dims} -> {v.vAddr} - {space}')

  # Add parameter
  def addParam(self, vartype):
    self.paramTable.append(vartype)

  # Create var table
  def createVarTable(self):
    self.varTable = dict()

  # Delete var table
  def deleteVarTable(self):
    self.varTable = None


## -- FUNCTION DIRECTORY
class FunctionDirectory():
  def __init__(self, debug):
    self.debug = debug
    self.directory = dict()
    self.cteTable = dict()
    self.globalFunc = None
    self.currentFunc = None
    self.currentType = "void"
    self.paramCount = 0
    self.varHelper = None

  ## SETTERS
  # NOTE: `currentFunc` is set in addFunction()
  # Set name for global function
  def setGlobalFunction(self):
    self.globalFunc = 'global'

  # Set name for current function
  def setCurrentFunction(self, currentFunc):
    self.currentFunc = currentFunc

  # Set current type used in parser
  def setCurrentType(self, t):
    self.currentType = t

  # Set var helper used in parser
  def setVarHelper(self, var):
    self.varHelper = var

  # Set return address for current function
  def setReturnAddr(self, addr):
    self.directory[self.currentFunc].setReturnAddr(addr)

  # Set start of quad for current function
  def setQuadStart(self, qs):
    self.directory[self.currentFunc].setQuadStart(qs)

  # Set "era" for current function
  def setEra(self, era):
    self.directory[self.currentFunc].setEra(era)

  # Increment param count of function by 1
  def incrementParamCount(self):
    self.paramCount += 1

  # Reset param count to 0
  def resetParamCount(self):
    self.paramCount = 0

  ## GETTERS
  # Returns desired variable
  def getVar(self, name):
    ret = None
    # Priority: Local -> Global
    if name in self.directory[self.currentFunc].varTable:
      ret = self.directory[self.currentFunc].getVar(name)
    elif name in self.directory[self.globalFunc].varTable:
      ret = self.directory[self.globalFunc].getVar(name)
    else:     # Else, raise an error
      raise Exception(f'Variable {name} does not exist!')

    return ret

  # Returns virtual address of desired variable
  def getVAddr(self, name):
    try:      # Get vAddr of variables
      return self.getVar(name).vAddr
    except:   # If it reaches here, that means it's already an address
      return name

  # Get constant
  def getCte(self, value, vartype):
    return self.cteTable[(value, vartype)]

  # Get dimensions of a specified variable
  def getDimensionsOfVar(self, name):
    try:
      return self.getVar(name).dims
    except:
      raise Exception(f'Variable {name} does not exist!')

  # Get parameter of function
  def getParamOfFunc(self, func):
    return self.directory[func].paramTable[self.paramCount]

  # Get quadStart of function
  def getQuadStartOfFunc(self, func):
    return self.directory[func].quadStart

  # Get a function's return type
  def getReturnTypeOfFunc(self, func):
    return self.directory[func].returnType

  # Get the current function's return type
  def getCurrentFuncReturnType(self):
    return self.directory[self.currentFunc].returnType

  # Get a function's return address
  def getReturnAddrOfFunc(self, func):
    return self.directory[func].returnAddr

  # Get the current function's return address
  def getCurrentFuncReturnAddr(self):
    return self.directory[self.currentFunc].returnAddr

  # Get ERA of function
  def getEra(self, func):
    return self.directory[func].era

  ## PUSH/ADD
  # Adds function to the directory
  def addFunction(self, name):
    self.directory[name] = Function(name, self.currentType, self.debug)
    self.currentFunc = name

    if self.debug:
      print(f'-- {self.currentFunc} - {self.currentType}')

  # Add parameters to current function
  def addFuncParam(self):
    self.directory[self.currentFunc].addParam(self.currentType)

  # Add variable to the current function's var table
  def addVar(self, name, vAddr):
    self.directory[self.currentFunc].addVar(name, self.currentType, vAddr)

  # Add constant
  def addCte(self, value, vartype, vAddr):
    self.cteTable[(value, vartype)] = Constant(value, vartype, vAddr)

    if self.debug:
      c = self.cteTable[(value, vartype)]
      print(f'\t\t\t\t\t> CTE: {c.value} - {c.vartype} -> {c.vAddr}')

  # Add dimension to a specified variable in the current scope
  def addDimensionToVar(self, var, dim):
    self.directory[self.currentFunc].addDimensionToVar(var, dim)

  ## FUNCTIONS
  # Creates var table for current function
  def createVarTable(self):
    if self.directory[self.currentFunc].varTable is None:
      self.directory[self.currentFunc].createVarTable()

  # Deletes var table for current function
  def deleteVarTable(self):
    self.directory[self.currentFunc].deleteVarTable()
    self.currentFunc = self.globalFunc

  # Verify number of parameters of function
  def verifyParamCount(self, func):
    return (self.paramCount == len(self.directory[func].paramTable))

  # Return boolean if function exists
  def functionExists(self, func):
    if func in self.directory:
      return True
    return False

  # Returns a boolean if variable exists in local or global scope
  def varExists(self, var):
    if var in self.directory[self.currentFunc].varTable or var in self.directory[self.globalFunc].varTable:
      return True
    return False

  # Returns a boolean if a constant exists
  def cteExists(self, cte, vartype):
    return (cte, vartype) in self.cteTable

  # Returns a boolean if variable is available to declare in current context
  def varAvailable(self, var):
    if var not in self.directory[self.currentFunc].varTable:
      return True
    return False
