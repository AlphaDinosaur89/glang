from .nodes import *
from .errors import *
from .consts import *
from .parse_result import *


class Parser:
    def __init__(self, tokens):
        self.current_tok = None
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
        self.call_nodes = []
        self.var_accesses = []
        self.current_func_name = None

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Syntax error"
            ))

        return res, self.call_nodes, self.var_accesses
    
    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()


        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)

        return res.success(statements)
    
    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()

        # return, continue break and stuff can be added here
        if self.current_tok.matches(TT_KEYWORD, 'var'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier"
                ))
            
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            expr = None

            if self.current_tok.type == TT_DOT:
                left = var_name
                op_tok = self.current_tok
                
                res.register_advancement()
                self.advance()
                right = res.register(self.call())
                if res.error: return res
        
                var_name = BinOpNode(StringNode(left), op_tok, right)
            
            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))
        
        elif self.current_tok.matches(TT_KEYWORD, 'return'):
            res.register_advancement()
            self.advance()

            expr = res.try_register(self.expr())
            if not expr:
                self.reverse(res.to_reverse_count)
            
            return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))
        
        elif self.current_tok.matches(TT_KEYWORD, 'class'):
            res.register_advancement()
            self.advance()
            
            inheritances = []
            
            class_name = self.current_tok
            if not class_name.type == TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected identifier but got {class_name.type}"
                ))
            
            res.register_advancement()
            self.advance()
            
            if self.current_tok.type == TT_LPAREN:
                res.register_advancement()
                self.advance()
                
                if not self.current_tok.matches(TT_KEYWORD, "class"):
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected class but got {self.current_tok.value}"
                        ))
                
                res.register_advancement()
                self.advance()
                
                if not self.current_tok.type == TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected identifier but got {self.current_tok.value}"
                        ))
                
                inheritances.append(self.current_tok.value)
                
                res.register_advancement()
                self.advance()
                
                # TODO: Make it so you can inherit multiple classes with ","
                # example class A(class B, class C):
                if not self.current_tok.type == TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ')' but got {self.current_tok.value}"
                        ))
                
                res.register_advancement()
                self.advance()
            
            if self.current_tok.type == TT_DCOLON:
                res.register_advancement()
                self.advance()
                
                if self.current_tok.type != TT_NEWLINE:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected newline but got {self.current_tok.type}"
                    ))
                
                res.register_advancement()
                self.advance()
                
                base_name = class_name.value
                if len(inheritances) > 0:
                    base_name = inheritances[0]
                properties = [(StringNode(Token(TT_STRING, '.type',
                                                self.current_tok.pos_start,
                                                self.current_tok.pos_end)),
                                                StringNode(Token(TT_STRING, base_name,
                                                                 self.current_tok.pos_start,
                                                                 self.current_tok.pos_end)))]
                
                methods = []
                while self.current_tok.type in (TT_IDENTIFIER, TT_KEYWORD):
                    property_ = self.current_tok
                    val = None
                    
                    if self.current_tok.matches(TT_KEYWORD, 'def'):
                        methods.append(res.register(self.func_def()))
                        if res.error: return res

                        if self.current_tok.type != TT_NEWLINE:
                            return res.failure(InvalidSyntaxError(
                                self.current_tok.pos_start, self.current_tok.pos_end,
                                f"Expected newline but got {self.current_tok}"
                            ))
                        
                        while self.current_tok.type == TT_NEWLINE:
                            res.register_advancement()
                            self.advance()
                        
                        continue
                    elif self.current_tok.matches(TT_KEYWORD, 'end'):
                        break
                    elif self.current_tok.type == TT_KEYWORD:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            f"Expected def or identifier but got {self.current_tok}"
                        ))
                    
                    res.register_advancement()
                    self.advance()
                    
                    if self.current_tok.type == TT_EQ:
                        res.register_advancement()
                        self.advance()
                        val = res.register(self.expr())
                        if res.error: return res
                    
                    if self.current_tok.type != TT_NEWLINE:
                        return res.failure(InvalidSyntaxError(
                            self.current_tok.pos_start, self.current_tok.pos_end,
                            f"Expected newline but got {self.current_tok}"
                        ))
                    
                    while self.current_tok.type == TT_NEWLINE:
                        res.register_advancement()
                        self.advance()
                    
                    properties.append((StringNode(property_), val))
                
                while self.current_tok.type == TT_NEWLINE:
                    res.register_advancement()
                    self.advance()
                
                if not self.current_tok.matches(TT_KEYWORD, 'end'):
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected end but got {self.current_tok}"
                    ))
                    
                res.register_advancement()
                self.advance()
                
                methods = None if methods == [] else methods
                
                return res.success(ClassAssignNode(class_name, 
                                                   ListNode(properties,
                                                                        pos_start=self.current_tok.pos_start,
                                                                        pos_end=self.current_tok.pos_end),
                                                   ListNode(methods,
                                                                        pos_start=self.current_tok.pos_start,
                                                                        pos_end=self.current_tok.pos_end),
                                                   inheritances))
            
            #this used to be res.success(ClassNode(class_name, inheritances)) but it returns an error (too many arguments)
            return res.success(ClassNode(class_name))
        
        expr = res.register(self.expr())
        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "InvalidSyntaxError"
            ))

        return res.success(expr)

    def expr(self):
        res = ParseResult()

        node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'and'), (TT_KEYWORD, 'or'))))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "InvalidSyntaxError"
            ))

        return res.success(node)

    def comp_expr(self):
        res = ParseResult()

        node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "InvalidSyntaxError"
            ))

        return res.success(node)

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type == TT_IDENTIFIER and self.tokens[self.tok_idx+1].type in (TT_INC, TT_DEC): # (placeholder) relace to TT_INC, TT_DEC
            factor = res.register(self.power())
            if res.error: return res
            tok = self.current_tok
            res.register_advancement()
            self.advance()
            res.register_advancement()
            self.advance()
            return res.success(UnaryOpNode(tok, factor))
        if tok.type in (TT_PLUS, TT_MINUS, TT_MUL, TT_INC, TT_DEC):
            res.register_advancement()
            self.advance()
            if tok.type in (TT_INC, TT_DEC):                
                res.register_advancement()
                self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()
    
    # only added because is a requirement
    # TODO: Add functions
    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error: return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "InvalidSyntaxError"
                    ))

                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expr()))
                    if res.error: return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        f"Expected ',' or ')'"
                    ))

                res.register_advancement()
                self.advance()
            
            node = CallNode(atom, arg_nodes) # expects identifiers make it so you can call anything
            self.call_nodes.append(node.node_to_call.var_name_tok.value)\
                if not node.node_to_call.var_name_tok.value in self.call_nodes else None in self.call_nodes
            return res.success(node)
        elif self.current_tok.type == TT_DOT:
            left = atom
            op_tok = self.current_tok
            
            res.register_advancement()
            self.advance()
            right = res.register(self.call())
            if res.error: return res
            
            return res.success(BinOpNode(left, op_tok, right))
        elif self.current_tok.type == TT_LSQUARE: # TODO: make it so this can be a dict access aswell
            # NOTE: you cant do something like this foo[0][1] but it will work with (foo[0])[1] (idk how to fix ngl)
            # same with function calls, for it to work you have to do this (foo())[0]
            # TODO: figure out how to fix this
            # yet another TODO: Make it so you can assign values to lists with this syntax var balls[0] = 1
            res.register_advancement()
            self.advance()
            
            access = res.register(self.arith_expr())
            if res.error: return res
            
            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ']'"
                ))
            
            res.register_advancement()
            self.advance()
                        
            return res.success(ListAccessNode(atom, access))
        
        return res.success(atom)

    def power(self):
        return self.bin_op(self.call, (TT_POW, TT_MOD), self.factor)

    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        pos_start = self.current_tok.pos_start.copy()

        if tok.type == TT_INT:
            res.register_advancement()
            self.advance()
            return res.success(IntegerNode(tok))
        
        elif tok.type == TT_FLOAT:
            res.register_advancement()
            self.advance()
            return res.success(FloatNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            self.var_accesses.append(tok.value)
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(list_expr)

        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        
        elif self.current_tok.matches(TT_KEYWORD, 'continue'):
            res.register_advancement()
            self.advance()
            return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))
        
        elif self.current_tok.matches(TT_KEYWORD, 'break'):
            res.register_advancement()
            self.advance()
            return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))
        
        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        
        elif tok.matches(TT_KEYWORD, 'def'):
            func_def = res.register(self.func_def())
            if res.error: return res
            return res.success(func_def)
        
        elif tok.matches(TT_KEYWORD, 'class'):
            class_node = res.register(self.statement())
            if res.error: return res
            return res.success(class_node)

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "InvalidSyntaxError"
        ))

    def list_expr(self):
        res = ParseResult()
        elements_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '['"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            elements_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Unexpected token"
                ))

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                elements_nodes.append(res.register(self.expr()))
                if res.error: return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ']'"
                ))

            res.register_advancement()
            self.advance()

        return res.success(ListNode(
            elements_nodes,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def if_expr(self):
        res = ParseResult()
        all_cases = res.register(self.if_expr_cases('if'))
        if res.error: return res
        cases, else_case = all_cases
        return res.success(IfNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_DCOLON:
                return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ':'"
                    ))
            
            res.register_advancement()
            self.advance()

            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error: return res
                else_case = (statements, True)

                if self.current_tok.matches(TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected 'end'"
                    ))
            else:
                expr = res.register(self.statement())
                if res.error: return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'elif'):
            all_cases = res.register(self.if_expr_b())
            if res.error: return res
            cases, else_case = all_cases
        else:
            else_case = res.register(self.if_expr_c())
            if res.error: return res

        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '{case_keyword}'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.statement())
        if res.error: return res
        
        if not self.current_tok.type == TT_DCOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))
        
        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            statements = res.register(self.statements())
            if res.error: return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error: return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.statement())
            if res.error: return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error: return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)
        return res.success((cases, else_case))
    
    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'for'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'for'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected identifier"
            ))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected '='"
            ))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'to'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'to'"
            ))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error: return res
        
        if self.current_tok.matches(TT_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        if not self.current_tok.type == TT_DCOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'end'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))
        
    ################################
    
    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res

        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)
    
    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'while'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'while'"
            ))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error: return res

        if not self.current_tok.type == TT_DCOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error: return res

            if not self.current_tok.matches(TT_KEYWORD, 'end'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected 'end'"
                ))

            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition, body, True))

        body = res.register(self.statement())
        if res.error: return res

        return res.success(WhileNode(condition, body, False))

    def func_def(self):
        res = ParseResult()
        
        res.register_advancement()
        self.advance()

        func_name = self.current_tok
        self.current_func_name = func_name.value
        res.register_advancement()
        self.advance()
        
        if self.current_tok.type != TT_LPAREN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '('"
            ))
        
        res.register_advancement()
        self.advance()
        
        arg_name_toks = []
        
        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected argument name"
                    ))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()

            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    f"Expected ',' or ')'"
                ))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected identifier or ')'"
                ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_DCOLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected ':'"
            ))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected NEWLINE"
            ))

        res.register_advancement()
        self.advance()

        body = res.register(self.statements())
        if res.error: return res

        if not self.current_tok.matches(TT_KEYWORD, 'end'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                f"Expected 'end'"
            ))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(
            func_name,
            arg_name_toks,
            body,
            False
        ))
    