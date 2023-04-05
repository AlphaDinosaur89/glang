from .builtin_function import *
BuiltinFunction.print = BuiltinFunction("print")
BuiltinFunction.exit = BuiltinFunction("exit")
BuiltinFunction.asm = BuiltinFunction("asm")
BuiltinFunction.ref = BuiltinFunction("ref")
# add argc and argv functions

BUILTINS = {
    "print": BuiltinFunction.print,
    "exit": BuiltinFunction.exit,
    "asm": BuiltinFunction.asm,
    "ref": BuiltinFunction.ref,
    'new': None # done in codegen
}