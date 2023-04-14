import getopt
import sys
import clog
import utils
import os
from builtins_ import *
from modules.consts import TT_KEYWORD, TT_STRING, TT_EOF, TT_KEYWORD, TT_NEWLINE
from modules import lexer, _parser, codegen, errors, nodes, consts

# glang Compiler
# glc

try:
    opts, args = getopt.getopt(sys.argv[1:], "o:I:shr")
except getopt.GetoptError as e:
    clog.error(e)
    exit(1)

HELP = """\
Usage: glc [options] file...
  -o <file>         Place the output into <file>
  -I <directory>    Add <directory> to include search path .\\std is added by default
  -s                Doesn't print compilation information
  -r                Compile program and run afterwards
  -h                Displays this message\
"""

# argument parsing

silent = False
run = False
output = "a.asb"
include = ['.\\', '.\\std\\']
for opt in opts:
    if opt[0] == '-h':
        print(HELP)
        exit()
    elif opt[0] == '-o':
        output = opt[1]
    elif opt[0] == '-s':
        silent = True
    elif opt[0] == '-r':
        run = True
    elif opt[0] == '-I':
        if opt[1][-1] != '\\':
            opt[1] += '\\'
        include.append(opt[1])

if len(args) < 1:
    utils.error("no input files")
    utils.fail(1)
elif len(args) > 1:
    utils.error("more than 1 input files not supported yet")
    utils.fail(1)

def assemble(filename):
    # switch this to an cx_Freeze executable in PATH

    cmd(f"..\\main.py {filename} {output}", f"alsm {filename} {output}")

def cmd(command, message=None):
    if not silent:
        if message is None:
            clog.log(f"[CMD] {command}")
        else:
            clog.log(f"[CMD] {message}")

    os.system(command)

def preprocess(tokens):
    i = 0
    included_files = []
    while i < len(tokens):
        token = tokens[i]
        if token.matches(TT_KEYWORD, 'include'):
            token = tokens[i+1]
            if token.type != TT_STRING:
                return None, errors.InvalidSyntaxError(token.pos_start,
                                                       token.pos_end,
                                                       "Expected string")
            del tokens[i]
            inc = token
            del tokens[i]
                       
            if not inc.value in included_files:
                for path in include:
                    try:
                        f = open(path + inc.value, "r")
                        f.close()
                        f = path + inc.value
                        included_files.append(inc.value)
                        break
                    except FileNotFoundError:
                        f = None
                
                if f is None:
                    return None, errors.IncludeError(inc.pos_start,
                                            inc.pos_end,
                                            f"File not found {inc.value} in the include path")
                
                with open(f, "r") as file:
                    text = ""
                    for char in file.readlines():
                        text += char
                
                text += '\n'
                lex = lexer.Lexer(inc.value, text)
                toks = lex.make_tokens()
                temp = tokens
                tokens = toks[0]
                tokens.extend(temp)
                i = -1
        
        i += 1
    
    temp_tokens = []

    i = 0
    while i <= len(tokens)-1:
        token = tokens[i]
        if token.type == TT_EOF and i != len(tokens)-1:
            pass
        elif token.matches(TT_KEYWORD, 'end'):
            temp_tokens.append(lexer.Token(TT_KEYWORD, 'end', pos_start=token.pos_start,
                                           pos_end=token.pos_end))
            temp_tokens.append(lexer.Token(TT_NEWLINE, pos_start=token.pos_start,
                                           pos_end=token.pos_end))
        else:
            temp_tokens.append(token)
        i += 1
    
    tokens = temp_tokens
    return tokens, None

def compile():
    with open(args[0], "r") as f:
        text = ""
        for char in f.readlines():
            text += char

    try:
        text += '\n'
        lex = lexer.Lexer(args[0], text)
        tokens, error = lex.make_tokens()
        if error:
            utils.errorp(error)
            utils.fail(1)
    except Exception as e:
        utils.errorp(e)
        utils.fail(1)
    
    try:
        tokens, error = preprocess(tokens)
        if error:
            utils.errorp(error)
            utils.fail(1)
    except Exception as e:
        utils.errorp(e)
        utils.fail(1)
    
    out = os.path.splitext(output)[0]
    
    if not silent:
        clog.log(f"Generating {out}.as")
    
    try:
        parser = _parser.Parser(tokens)
        result = parser.parse()
        
        try:
            if result.error:
                utils.errorp(result.error)
                utils.fail(1)
        except AttributeError:
            pass
        
        ast, call_nodes, var_accesses = result
    except Exception as e:
        utils.errorp(e)
        utils.fail(1)
    
    if ast.error:
        utils.errorp(ast.error)
        utils.fail(1)
    
    init = ""
    init += "mov [true], 1\n"
    init += "mov [false], 0\n\n"
    
    for text in BUILTINS:
        init += text

    # dead code elimination
    for node in ast.node:
        if isinstance(node, nodes.FuncDefNode):
            if not node.func_name_tok.value in call_nodes \
                and not node.func_name_tok.value in var_accesses:
                ast.node.remove(node)
    
    #try:
    cdgen = codegen.Codegen()
    result = cdgen.emit(ast.node)
    result, error = result.value, result.error
    #except Exception as e:
    #    utils.errorp(e)
    #    utils.fail(1)
    
    if error:
        utils.errorp(error)
        utils.fail(1)
    
    result = init + cdgen.hoisted_definitions + result
    
    with open(out + ".as", "w") as o:
        o.write(result)
        
    try:
        assemble(out + ".as")
    except Exception as e:
        utils.errorp(e)
        utils.fail(1)
    
    if run:
        cmd(f'..\\..\\bin\\Debug\\net5.0\\Alphassembly.exe {output}')

compile()
