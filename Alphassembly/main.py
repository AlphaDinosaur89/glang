import sys
import clog
from lexer import *
from parser_ import *
from assembler import *

if len(sys.argv) == 1:
    raise Exception("No file to compile")
if len(sys.argv) == 2:
    outfile = "a.asb"
if len(sys.argv) >= 3:
    outfile = sys.argv[2]

clog.log(f"Compiling to {outfile}")

try:
    f = open(sys.argv[1], "r")
except Exception as e:
    print(e)
    exit(1)

script = ""
for i in f.readlines():
    script += i
script += '\n'

lexer = Lexer(script)
tokens = lexer.make_tokens()
f.close()

parser = Parser(tokens)
ast = parser.parse()

assembler = Assembler(ast)
binary = assembler.assemble()

f = open(outfile, "wb")
f.write(binary)
f.close()
