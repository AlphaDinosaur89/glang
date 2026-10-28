from consts import *
from nodes import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_tok = None
        self.tok_idx = -1
        self.advance()
    
    def advance(self):
        self.tok_idx += 1
        self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        return self.statements()

    ###############################

    def statement(self):
        if self.current_tok.matches(TT_KEYWORD, "ld"):
            self.advance()

            val = self.current_tok
            self.advance()

            return LoadNode(val)
        elif self.current_tok.matches(TT_KEYWORD, "print"):
            self.advance()

            return PrintNode()
        elif self.current_tok.matches(TT_KEYWORD, "done"):
            self.advance()

            return DoneNode()
        elif self.current_tok.matches(TT_KEYWORD, "pop"):
            self.advance()

            arg = None
            if self.current_tok.type == TT_IDENTIFIER:
                arg = self.current_tok
                self.advance()

            return PopNode(arg)
        elif self.current_tok.matches(TT_KEYWORD, "div"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()

            return DivNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "mul"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()

            return MulNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "sub"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()
            
            return SubNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "add"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()
            
            return AddNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "mod"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()
            
            return ModuloNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "push"):
            self.advance()

            if self.current_tok.type != TT_LCURLY:
                value = self.current_tok
                self.advance()
            else:
                value = self.expr()                
            
            return PushNode(value)
        elif self.current_tok.matches(TT_KEYWORD, "jmp"):
            self.advance()

            label = self.current_tok
            if self.current_tok.type == TT_LABEL:
                raise Exception(f"Expected identifier")
            self.advance()

            return JumpNode(label)
        elif self.current_tok.matches(TT_KEYWORD, "je"):
            self.advance()
            
            label = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()

            argument = self.current_tok
            self.advance()
            
            return JeNode(label, argument)
        elif self.current_tok.matches(TT_KEYWORD, "jn"):
            self.advance()
            
            label = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()

            argument = self.current_tok
            self.advance()
            
            return JnNode(label, argument)
        elif self.current_tok.matches(TT_KEYWORD, "jl"):
            self.advance()
            
            label = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()

            argument = self.current_tok
            self.advance()
            
            return JlNode(label, argument)
        elif self.current_tok.matches(TT_KEYWORD, "jg"):
            self.advance()
            
            label = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()

            argument = self.current_tok
            self.advance()
            
            return JgNode(label, argument)
        elif self.current_tok.matches(TT_KEYWORD, "jt"):
            self.advance()

            label = self.current_tok
            self.advance()
            
            return JtNode(label)
        elif self.current_tok.matches(TT_KEYWORD, "jf"):
            self.advance()
            
            label = self.current_tok
            self.advance()
            
            return JfNode(label)
        elif self.current_tok.matches(TT_KEYWORD, "call"):
            self.advance()

            label = self.current_tok
            self.advance()

            return CallNode(label)
        elif self.current_tok.matches(TT_KEYWORD, "bcall"):
            self.advance()

            return BCallNode()
        elif self.current_tok.matches(TT_KEYWORD, "ret"):
            self.advance()

            return RetNode()
        elif self.current_tok.type == TT_LABEL:
            self.advance()

            name = self.current_tok
            self.advance()

            return LabelNode(name)
        elif self.current_tok.matches(TT_KEYWORD, "mov"):
            self.advance()

            target = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            if self.current_tok.type != TT_LCURLY:
                value = self.current_tok
                self.advance()
            else:
                value = self.expr()
            
            # when you mov from labels:
            # mov ax, label
            try:
                if value.type == TT_KEYWORD:
                    value.type = TT_IDENTIFIER
            except AttributeError:
                pass

            return MovNode(target, value)
        elif self.current_tok.matches(TT_KEYWORD, "cmp"):
            self.advance()

            cases = []
            while True:
                left = self.expr()

                middle = self.current_tok
                self.advance()

                right = self.expr()
                cases.append((left, middle, right))

                if self.current_tok.type == TT_AND:
                    cases.append(TT_AND)
                    self.advance()
                elif self.current_tok.type == TT_OR:
                    cases.append(TT_OR)
                    self.advance()
                else:
                    break
            return CmpNode(cases)
        elif self.current_tok.matches(TT_KEYWORD, "pow"):
            self.advance()

            val1 = self.current_tok
            self.advance()

            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            val2 = self.current_tok

            self.advance()
            
            return PowNode(val1, val2)
        elif self.current_tok.matches(TT_KEYWORD, "test"):
            self.advance()
            
            target = self.current_tok
            self.advance()
            
            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            if self.current_tok.type != TT_LCURLY:
                value = self.current_tok
                self.advance()
            else:
                value = self.expr()
            
            return TestNode(target, value)
        elif self.current_tok.matches(TT_KEYWORD, "pt"):
            self.advance()
            
            target = self.current_tok
            self.advance()
            
            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            
            storage = self.current_tok
            self.advance()
            
            return PtNode(target, storage)
        elif self.current_tok.matches(TT_KEYWORD, "spt"):
            self.advance()
            
            target = self.current_tok
            self.advance()
            
            if not self.current_tok.type == TT_COMMA:
                raise Exception(f"Expected ','")
            
            self.advance()
            
            arg = self.current_tok
            self.advance()
            
            return SptNode(target, arg)
        elif self.current_tok.matches(TT_EOF, None):
            return EOFNode()
        else:
            return self.expr()
        
            #raise Exception(f"Unknown instruction: {self.current_tok.value}")

    def statements(self):
        statements = []

        while self.current_tok.type == TT_NEWLINE:
            self.advance()

        statements.append(self.statement())

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break

            statements.append(self.statement())
        
        return statements
    
    def expr(self):
        tok = self.current_tok
        if self.current_tok.type == TT_STRING:
            self.advance()
            return StringNode(tok)
        elif self.current_tok.type == TT_INT:
            self.advance()
            return IntegerNode(tok)
        elif self.current_tok.type == TT_FLOAT:
            self.advance()
            return FloatNode(tok)
        elif self.current_tok.type == TT_IDENTIFIER:
            if self.current_tok.value in REGISTERS:
                self.advance()
                return RegisterNode(tok)
            else:
                raise Exception(f"Unexpected identifier: {self.current_tok.value}")
        elif self.current_tok.type == TT_VARIABLE:
            self.advance()
            return VariableNode(tok)
        elif self.current_tok.type == TT_LCURLY:
            self.advance()
            
            lst = []
            if self.current_tok.type != TT_RCURLY:
                lst.append(self.expr())
                
                if self.current_tok.type == TT_RCURLY:
                    self.advance()
                    return ListNode(lst)
                elif self.current_tok.type == TT_COMMA:
                    while self.current_tok.type != TT_NEWLINE:
                        self.advance()
                        
                        lst.append(self.expr())
                        
                        if self.current_tok.type == TT_RCURLY:
                            self.advance()
                            return ListNode(lst)
                    raise Exception("Expected '}'")
                else:
                    raise Exception("expected '}' or ','")
            else:
                self.advance()
                return ListNode([])
        else:
            raise Exception("Syntax Error")