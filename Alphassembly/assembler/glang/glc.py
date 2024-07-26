import argparse
import sys
import os
import traceback
import inspect

from modules import lexer, _parser, codegen, nodes
from modules.errors import Error, IncludeError, PreprocessError
from clog import log, error, errorp
from builtins_ import BUILTINS

# Constants
TT_KEYWORD = lexer.TT_KEYWORD
TT_STRING = lexer.TT_STRING
TT_EOF = lexer.TT_EOF
TT_NEWLINE = lexer.TT_NEWLINE
TT_IDENTIFIER = lexer.TT_IDENTIFIER
TT_DCOLON = lexer.TT_DCOLON


def parse_arguments():
    parser = argparse.ArgumentParser(prog="glc", description="glang Compiler")
    parser.add_argument("file", help="Input file")
    parser.add_argument("-o", dest="output", help="Place the output into <file>")
    parser.add_argument("-I", dest="include", action="append", help="Add <directory> to include search path")
    parser.add_argument("-s", dest="silent", action="store_true", help="Doesn't print compilation information")
    parser.add_argument("-r", dest="run", action="store_true", help="Compile program and run afterwards")
    return parser.parse_args()


def preprocess_tokens(tokens, include_paths):
    included_files = []
    included_modules = []
    temp_tokens = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.matches(TT_KEYWORD, 'include'):
            token = tokens[i + 1]
            if token.type != TT_STRING:
                return None, IncludeError(token.pos_start, token.pos_end, "Expected string")
            del tokens[i]
            inc = token
            del tokens[i]
            
            for path in include_paths:
                file_path = os.path.abspath(os.path.join(path, inc.value))
                if file_path in included_files: break
                if os.path.isfile(file_path):
                    included_files.append(file_path)
                    with open(file_path, "r") as file:
                        text = file.read() + '\n'
                    lex = lexer.Lexer(file_path, text)
                    toks = lex.make_tokens()
                    tokens = toks[0] + tokens
                    i = -1
                    break
            else:
                return None, f"File not found: {inc.value} in the include path"

        i += 1

    i = 0
    while i <= len(tokens) - 1:
        token = tokens[i]
        if token.type == TT_EOF and i != len(tokens) - 1:
            pass
        elif token.matches(TT_KEYWORD, 'end'):
            temp_tokens.append(lexer.Token(TT_KEYWORD, 'end', pos_start=token.pos_start, pos_end=token.pos_end))
            temp_tokens.append(lexer.Token(TT_NEWLINE, pos_start=token.pos_start, pos_end=token.pos_end))
        else:
            temp_tokens.append(token)
        i += 1

    tokens = temp_tokens
    return tokens, None


def cmd(silent, command, message=None):
    if not silent:
        if message is None:
            log(f"[CMD] {command}")
        else:
            log(f"[CMD] {message}")

    os.system(command)


def assemble(filename, output, silent):
    # switch this to an cx_Freeze executable in PATH

    cmd(silent, f"..\\main.py {filename} {output}", f"alsm {filename} {output}")


def compile_file(input_file, output_file, include_paths, silent, run):
    if not os.path.isfile(input_file):
        error(f"File not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r") as f:
        text = f.read()

    try:
        text += '\n'
        lex = lexer.Lexer(input_file, text)
        tokens, error = lex.make_tokens()
        if error:
            errorp(error)
            sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        errorp(e)
        sys.exit(1)

    try:
        tokens, error = preprocess_tokens(tokens, include_paths)
        if error:
            errorp(error)
            sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        errorp(e)
        sys.exit(1)
    
    output_base = os.path.splitext(output_file)[0]
    if not silent:
        log(f"Generating {output_base}.as")

    try:
        parser = _parser.Parser(tokens)
        result = parser.parse()
        if type(result) is not tuple and result.error:
            errorp(result.error)
            sys.exit(1)
        ast, call_nodes, var_accesses = result
        if ast.error:
            errorp(ast.error)
            sys.exit(1)
    except Exception as e:
        print(traceback.format_exc())
        errorp(e)
        sys.exit(1)

    init_code = ""
    init_code += "push 0\n"
    init_code += "mov [true], 1\n"
    init_code += "mov [false], 0\n\n"
    init_code += "\n".join(BUILTINS)

    for node in ast.node[:]:
        if isinstance(node, nodes.FuncDefNode):
            if node.func_name_tok.value not in call_nodes and node.func_name_tok.value not in var_accesses:
                ast.node.remove(node)

    try:
        cdgen = codegen.Codegen()
        result = cdgen.emit(ast.node)
        result, error = result.value, result.error
    except Exception as e:
        print(traceback.format_exc())
        errorp(e)
        sys.exit(1)

    if error:
        errorp(error)
        sys.exit(1)

    result = init_code + cdgen.hoisted_definitions + result

    with open(output_file + '.as', "w") as o:
        o.write(result)
        
    try:
        assemble(output_file + ".as", output_file + ".asb", silent)
    except Exception as e:
        print(traceback.format_exc())
        errorp(e)
        sys.exit(1)

    if run:
        cmd = f'..\\..\\bin\\Release\\net6.0\\Alphassembly.exe {output_file}.asb'
        if not silent:
            log(f"[CMD] {cmd}")
        os.system(cmd)


def main():
    args = parse_arguments()

    input_file = args.file
    output_file = args.output if args.output else "a"
    args.include = [] if args.include == None else args.include
    args.include.extend(['.\\', '.\\std\\'])
    silent = args.silent
    run = args.run

    compile_file(input_file, output_file, args.include, silent, run)


if __name__ == '__main__':
    main()
