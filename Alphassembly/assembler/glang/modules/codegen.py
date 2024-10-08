from asyncio import ReadTransport
from doctest import OutputChecker
from .errors import *
from .ctresult import *
from .consts import *
from .nodes import *
from .builtins import *
from .lexer import Token

class Codegen:
    def __init__(self):
        self.label_idx = 0
        self.var_idx = 0
        self.loopsc = []
        self.loopsb = []
        self.loop_breakc = False
        self.class_bcall = '18'
        self.class_definitions = {}
        self.hoisted_definitions = ''
        self.modules = {}
    
    def emit(self, node):
        method_name = f'emit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_emit_method)
        return method(node)
    
    def no_emit_method(self, node):
        raise Exception(f"No emit_{type(node).__name__} method defined")
    
    def emit_list(self, node):
        res = CTResult()
        output = ""
        
        for element_node in node:
            output += res.register(self.emit(element_node))
            if res.should_return(): return res
        
        return res.success(output)
    
    def emit_StringNode(self, node):
        res = CTResult()
        
        output = "mov ax, "
        output += '"' + node.tok.value + '"\n'
        return res.success(output)
    
    def emit_IntegerNode(self, node):
        res = CTResult()
        
        output = "mov ax, "
        output += str(node.tok.value) + '\n'
        return res.success(output)
    
    def emit_FloatNode(self, node):
        res = CTResult()
        
        output = "mov ax, "
        output += str(node.tok.value) + '\n'
        return res.success(output)
    
    def emit_ListNode(self, node):
        res = CTResult()
        # TODO: implement this
        output = ""
        
        length = len(node.element_nodes)
        
        variables = []
        # make list of arguments
        for _ in range(length):
            variables.append(self.var_idx)
            self.var_idx += 1
        
        i = 0
        for var in variables:
            output += res.register(self.emit(node.element_nodes[i]))
            if res.error: return res
                
            output += f"mov [.V{var}], ax\n"
            i += 1
            
        output += 'mov ax, {'
        i = 0
        for var in variables:
            output += f"[.V{var}]"
            
            if not i == len(variables)-1:
                output += ', '
            
            i += 1
        output += '}\n'
        
        #print(output)
        #exit()
        
        return res.success(output)
    
    def emit_VarAssignNode(self, node):
        res = CTResult()
        output = ""
        
        if type(node.var_name_tok) is BinOpNode:
            if type(node.var_name_tok.left_node) is not VarAccessNode:
                node.var_name_tok.left_node = VarAccessNode(node.var_name_tok.left_node.tok)
                        
            output += res.register(self.emit(node.value_node))
            if res.error: return res
            output += f"push ax\n"
            
            self.class_bcall = '17'
            output += res.register(self.emit(node.var_name_tok))
            if res.error: return res
            self.class_bcall = '18'
            
            return res.success(output)
        
        output += res.register(self.emit(node.value_node))
        if res.error: return res
        output += f"mov [{node.var_name_tok.value}], ax\n"
        return res.success(output)
    
    def emit_VarAccessNode(self, node):
        res = CTResult()
        
        return res.success(f"mov ax, [{node.var_name_tok.value}]\n")
    
    def op_op(self, node):
        output = ""
        op = ""
        # TODO:
        # make this to put it in a variable instead
        # as it wont work when calling functions for example
        # can probably be done for just functions
        
        if node.op_tok.type == TT_EE:
            op = "== "
        elif node.op_tok.type == TT_NE:
            op = "!= "
        elif node.op_tok.type == TT_LT:
            op = "< "
        elif node.op_tok.type == TT_GT:
            op = "> "
        elif node.op_tok.type == TT_LTE:
            op = "<= "
        elif node.op_tok.type == TT_GTE:
            op = ">= "
        
        if op != "":
            if type(node.left_node) is not VarAccessNode and type(node.left_node) is not StringNode:
                output += f"{node.left_node.tok.value} "
            elif type(node.left_node) is StringNode:
                output += f"\"{node.left_node.tok.value}\" "
            elif type(node.left_node) is VarAccessNode:
                output += f"[{node.left_node.var_name_tok.value}] "
                
            output += op
                
            if type(node.right_node) is not VarAccessNode and type(node.right_node) is not StringNode:
                output += f"{node.right_node.tok.value} "
            elif type(node.right_node) is StringNode:
                output += f"\"{node.right_node.tok.value}\" "
            elif type(node.right_node) is VarAccessNode:
                output += f"[{node.right_node.var_name_tok.value}] "
                
        return output
    
    def andor_op(self, node, a=False):
        res = CTResult()
        
        if not a:
            output = "cmp "
        else:
            output = ""
        
        lnode = node.left_node
        rnode = node.right_node
        
        if lnode.op_tok.matches(TT_KEYWORD, 'and'):
            output += res.register(self.andor_op(lnode, True)) + "&& "
            if res.error: return res
        elif lnode.op_tok.matches(TT_KEYWORD, 'or'):
            output += res.register(self.andor_op(lnode, True)) + "|| "
            if res.error: return res
        
        output += self.op_op(lnode)
        
        if node.op_tok.matches(TT_KEYWORD, 'and') and not lnode.op_tok.matches(TT_KEYWORD, 'and'):
            if output[-3:-1] in ('&&', '||'):
                output = output[:-3]
            output += "&& "
        if node.op_tok.matches(TT_KEYWORD, 'or') and not lnode.op_tok.matches(TT_KEYWORD, 'or'):
            if output[-3:-1] in ('&&', '||'):
                output = output[:-3]
            output += "|| "
        
        output += self.op_op(rnode)
        
        return res.success(output)
    
    def class_def(self, node):
        res = CTResult()
        output = ""
        
        last_node = node.right_node
        while type(last_node) is BinOpNode:
            last_node = last_node.right_node
        
        nd, _ = node.remove_last_node()
        
        self.class_bcall = '18'
        
        output += res.register(self.emit(nd))
        if res.error: return res
        self.class_bcall = '17'
        
        output += 'push ax\n'
        
        output += f'mov ax, "{last_node.var_name_tok.value}"\n'
        output += 'push ax\n'
        
        #output += 'mov ax, 17\n'
        #output += 'bcall\n'
        
        return res.success(output)
    
    def class_access(self, node):
        res = CTResult()
        output = ""
        
        i = 0
        right = node.right_node
        while type(right) is BinOpNode:
            right = right.right_node
            i += 1
        
        output += res.register(self.emit(node.left_node))
        if res.error: return res
        output += 'push ax\n'
        
        right = node.right_node
        
        if type(right) is BinOpNode:
            left = node.right_node.left_node
        while type(right) is BinOpNode:
            if type(right) is BinOpNode:
                left = right.left_node
                right = right.right_node
            
            output += f'mov ax, "{left.var_name_tok.value}"\n'
            output += f'push ax\n'
            
            output += f'mov ax, {self.class_bcall}\n'
            output += 'bcall\n'
            output += f'push ax\n'
        
        if type(node.right_node) is CallNode:            
            output += f'mov ax, "{node.right_node.node_to_call.var_name_tok.value}"\n'
            output += 'push ax\n'
        elif type(node.right_node) is ListAccessNode:
            s = ''
            if type(node.right_node.left_node) is CallNode:
                s = node.right_node.left_node.node_to_call.var_name_tok.value
            else:
                s = node.right_node.left_node.var_name_tok.value
            output += f'mov ax, "{s}"\n'
            output += f'push ax\n'
        elif type(node.right_node) is not BinOpNode:
            output += f'mov ax, "{node.right_node.var_name_tok.value}"\n'
            output += f'push ax\n'
        else:
            output += f'mov ax, "{right.var_name_tok.value}"\n'
            output += f'push ax\n'
        
        return res.success(output)
    
    def emit_BinOpNode(self, node):
        res = CTResult()
        output = ""
        
        if not node.op_tok.value in ('and', 'or', 'DOT') and not node.op_tok.type in (TT_DOT):
            if res.should_return(): return res
            output += res.register(self.emit(node.right_node))
            if node.op_tok.type in (TT_PLUS, TT_MINUS, TT_MUL, TT_DIV, TT_MOD):
                output += "push ax\n"
            else:
                output += "mov bx, ax\n"
                #output += "push ax\n" README: UNcomment this and add pops to all conditions if they dont work, they should though
            
            output += res.register(self.emit(node.left_node))
            if res.should_return(): return res
        else:
            if node.op_tok.matches(TT_KEYWORD, 'and') or node.op_tok.matches(TT_KEYWORD, 'or'):
                output += res.register(self.emit(node.left_node))
                if res.error: return res
                
                left_var = self.var_idx
                self.var_idx += 1
                
                output += "test ax, ax\n"
                output += f"mov [.V{left_var}], ax\n"
                
                output += res.register(self.emit(node.right_node))
                if res.error: return res
                
                right_var = self.var_idx
                self.var_idx += 1
                
                output += "test ax, ax\n"
                output += f"mov [.V{right_var}], ax\n"
                
                # allows for something like this:
                # 1 and 1 | 1 or 2 | foo() and bar()
                # ignore this if True or
                # it has been some time since i worked on this and this fixed conditional operations so i am not changing it
                if True or type(node.right_node) is not BinOpNode:
                    varname = Token(TT_IDENTIFIER, f'.V{right_var}',
                                    node.right_node.pos_start,
                                    node.right_node.pos_start)
                    node.right_node = BinOpNode(VarAccessNode(varname), Token(TT_NE, None,
                                                                       node.right_node.pos_start, 
                                                                       node.right_node.pos_end),
                                                                       IntegerNode(Token(TT_INT, 0,
                                                                                         node.right_node.pos_start,
                                                                                         node.right_node.pos_end)))
                if True or type(node.left_node) is not BinOpNode:
                    varname = Token(TT_IDENTIFIER, f'.V{left_var}',
                                    node.left_node.pos_start,
                                    node.left_node.pos_start)
                    node.left_node = BinOpNode(VarAccessNode(varname), Token(TT_NE, None,
                                                                       node.left_node.pos_start, 
                                                                       node.left_node.pos_end),
                                                                       IntegerNode(Token(TT_INT, 0,
                                                                                         node.left_node.pos_start,
                                                                                         node.left_node.pos_end)))
                output += res.register(self.andor_op(node)) + '\n'
                if res.error: return res
                
                l0 = self.label_idx
                self.label_idx += 1
                l1 = self.label_idx
                self.label_idx += 1
                l2 = self.label_idx
                self.label_idx += 1
                
                output += f"jt .L{l0}\n"
                output += f"jmp .L{l1}\n"
                output += f".L{l0}:\n"
                output += f"    mov ax, 1\n"
                output += f"    jmp .L{l2}\n"
                output += f".L{l1}:\n"
                output += f"    mov ax, 0\n"
                output += f".L{l2}:\n"
                return res.success(output)
        
        if node.op_tok.type == TT_DOT:
            if self.class_bcall == '18':
                output += res.register(self.class_access(node))
            else:
                output += res.register(self.class_def(node))
            if res.error: return res
                

            output += f'mov ax, {self.class_bcall}\n'
            output += 'bcall\n'
            
            if type(node.right_node) is CallNode:
                tempvar = self.var_idx
                output += f'mov [.V{tempvar}], ax\n'
                self.var_idx += 1
                
                output += res.register(self.make_args(node.right_node.arg_nodes))
                if res.error: return res
                
                output += res.register(self.emit(node.left_node))
                if res.error: return res
                
                # this pushes the object onto the stack
                output += 'push ax\n'
                output += f'call [.V{tempvar}]\n'
            elif type(node.right_node) is ListAccessNode:
                if not type(node.right_node.access_node) is StringNode:
                    var1 = self.var_idx
                    self.var_idx += 1
                    output += f'mov [.V{var1}], ax\n'
            
                    output += res.register(self.emit(node.right_node.access_node))
                    
                    if res.error: return res
                    output += "push ax\n"
                    
                    if type(node.right_node.left_node) is CallNode:
                        var = self.var_idx
                        self.var_idx += 1
                        output += res.register(self.make_args(node.right_node.left_node.arg_nodes))
                        if res.error: return res
                            
                        output += res.register(self.emit(node.left_node))
                        if res.error: return res
                        
                        # this pushes the object onto the stack
                        output += 'push ax\n'
                        
                        output += f'call [.V{var1}]\n'
                     
                    output += "push ax\n"
                    
                    output += "mov ax, 6\n"
                    output += "bcall\n"
                else:
                    var1 = self.var_idx
                    self.var_idx += 1
                    output += f'mov [.V{var1}], ax\n'
                    
                    if type(node.right_node.left_node) is CallNode:
                        var = self.var_idx
                        self.var_idx += 1
                        output += res.register(self.make_args(node.right_node.left_node.arg_nodes))
                        if res.error: return res
                            
                        output += res.register(self.emit(node.left_node))
                        if res.error: return res
                        
                        # this pushes the object onto the stack
                        output += 'push ax\n'
                        
                        output += f'call [.V{var1}]\n'
                    
                    output += "push ax\n"
                    
                    output += res.register(self.emit(node.right_node.access_node))
                    if res.error: return res
                    output += "push ax\n"
                    
                    output += "mov ax, 18\n"
                    output += "bcall\n"
                
        elif node.op_tok.type == TT_PLUS:
            output += "add ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_MINUS:
            output += "sub ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_MUL:
            output += "mul ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_DIV:
            output += "div ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_POW:
            output += "pow ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_MOD:
            output += "mod ax, sp\n"
            output += "pop\n"
        elif node.op_tok.type == TT_EE:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax == bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"
        elif node.op_tok.type == TT_NE:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax != bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"
        elif node.op_tok.type == TT_LT:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax < bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"
        elif node.op_tok.type == TT_GT:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax > bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"
        elif node.op_tok.type == TT_LTE:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax <= bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"
        elif node.op_tok.type == TT_GTE:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            l2 = self.label_idx
            self.label_idx += 1
            
            output += "cmp ax >= bx\n"
            output += f"jt .L{l0}\n"
            output += f"jmp .L{l1}\n"            
            output += f".L{l0}:\n"
            output += f"    mov ax, 1\n"
            output += f"    jmp .L{l2}\n"
            output += f".L{l1}:\n"
            output += f"    mov ax, 0\n"
            output += f".L{l2}:\n"

        return res.success(output)

    def emit_UnaryOpNode(self, node):
        res = CTResult()
        output = ""
        
        output += res.register(self.emit(node.node))
        if res.error: return res
        
        if node.op_tok.type == TT_MINUS:
            output += "mov bx, 0\n"
            output += "sub bx, 1\n"
            output += "mul ax, bx\n"
        elif node.op_tok.type == TT_MUL:
            var = self.var_idx
            self.var_idx += 1
            
            output += res.register(self.emit(node.node))
            if res.error: return res
            output += f'mov [.V{var}], ax\n'
            
            output += f"pt [.V{var}], [.Vptr]\n"
            output += "mov ax, [.Vptr]\n"
        elif node.op_tok.type == TT_INC:
            output += f"add [{node.node.var_name_tok.value}], 1\n"
            output += f"mov ax, [{node.node.var_name_tok.value}]\n"
        elif node.op_tok.type == TT_DEC:
            output += f"sub [{node.node.var_name_tok.value}], 1\n"
            output += f"mov ax, [{node.node.var_name_tok.value}]\n"
        elif node.op_tok.matches(TT_KEYWORD, 'not'):
            l0 = self.label_idx
            self.label_idx += 1
            output += 'test ax, ax\n'
            output += f'mov ax, 0\n'
            output += f'jt .L{l0}\n'
            output += f'mov ax, 1\n'
            output += f'.L{l0}:\n'
        
        return res.success(output)

    def emit_IfNode(self, node):
        res = CTResult()
        output = ""
        l0 = self.label_idx
        end = l0
        self.label_idx += 1
        l0 = self.label_idx
        else_l0 = l0
        self.label_idx += 1
        l0 = self.label_idx
        
        for case in node.cases:
            l0 = self.label_idx
            self.label_idx += 1
            l1 = self.label_idx
            self.label_idx += 1
            
            output += res.register(self.emit(case[0]))
            if res.error: return res
            
            output += "test ax, ax\n"
            output += "cmp ax != 0\n"
            output += f"jt .L{l1}\n"
            output += f"jmp .L{l0}\n"
            
            output += f".L{l1}:\n"
            output += res.register(self.emit(case[1]))
            if res.error: return res
            output += f"jmp .L{end}\n"

            output += f".L{l0}:\n"
        
        output += f".L{else_l0}:\n"
        if node.else_case:
            output += res.register(self.emit(node.else_case[0]))
            if res.error: return res
        
        output += f".L{end}:\n"
        
        return res.success(output)
    
    def emit_ContinueNode(self, node):
        if not self.loop_breakc:
            return CTResult().failure(CTError(node.pos_start,
                                       node.pos_end,
                                       "Cannot continue outside of a loop"))
        return CTResult().success(f"jmp .L{self.loopsc[-1]}\n")

    def emit_BreakNode(self, node):
        if not self.loop_breakc:
            return CTResult().failure(CTError(node.pos_start,
                                       node.pos_end,
                                       "Cannot break outside of a loop"))
        return CTResult().success(f"jmp .L{self.loopsb[-1]}\n")

    def emit_WhileNode(self, node):
        res = CTResult()
        output = ""
        
        l0 = self.label_idx
        self.label_idx += 1
        l1 = self.label_idx
        self.label_idx += 1
        continue_label = l0
        break_label = l1
        
        self.loopsc.append(continue_label)
        self.loopsb.append(break_label)
        
        output += f".L{l0}:\n"
        output += res.register(self.emit(node.condition_node))
        if res.error: return res
        #output += "cmp ax != 0\n"
        #output += f"jf .L{l1}\n"
        output += "test ax, ax\n"
        output += "cmp ax == 1\n"
        output += f"jf .L{l1}\n" 
        
        for node in node.body_node:
            self.loop_breakc = True
            if type(node) is not CallNode:
                output += res.register(self.emit(node))
                if res.error: return res
            else:
                self.loop_breakc = False
                output += res.register(self.emit(node))
                if res.should_return(): return res
        del self.loopsc[-1]
        del self.loopsb[-1]
        
        output += f"jmp .L{l0}\n"
        output += f".L{l1}:\n"
        
        return res.success(output)

    def emit_ForNode(self, node):
        res = CTResult()
        output = ""
        
        l0 = self.label_idx
        self.label_idx += 1
        l1 = self.label_idx
        self.label_idx += 1
        continue_label = self.label_idx
        self.label_idx += 1
        break_label = self.label_idx
        self.label_idx += 1
        
        self.loopsc.append(continue_label)
        self.loopsb.append(break_label)
        
        var_name = node.var_name_tok.value
        
        output += res.register(self.emit(node.start_value_node))
        if res.error: return res
        output += f"mov [{node.var_name_tok.value}], ax\n"
        
        end_value = self.var_idx
        self.var_idx += 1
        step_value = self.var_idx
        self.var_idx += 1
        
        output += res.register(self.emit(node.end_value_node))
        if res.error: return res
        output += f"mov [.V{end_value}], ax\n"
        
        if node.step_value_node:
            output += res.register(self.emit(node.step_value_node))
            if res.error: return res
            output += f"mov [.V{step_value}], ax\n"
        else:
            output += f"mov [.V{step_value}], 1\n"
        
        output += f"jmp .L{l1}\n"
        output += f".L{l0}:\n"
        
        for node in node.body_node:
            self.loop_breakc = True
            if type(node) is not CallNode:
                output += res.register(self.emit(node))
                if res.error: return res
            else:
                self.loop_breakc = False
                output += res.register(self.emit(node))
                if res.error: return res
        del self.loopsc[-1]
        del self.loopsb[-1]
        
        output += f".L{continue_label}:\n"
        output += f"add [{var_name}], [.V{step_value}]\n"
        
        l2 = self.label_idx
        self.label_idx += 1
        l3 = self.label_idx
        self.label_idx += 1
        
        output += f".L{l1}:\n"
        output += f"cmp [.V{step_value}] >= 0\n"
        output += f"jt .L{l2}\n"
        output += f"jmp .L{l3}\n"
        output += f".L{l2}:\n"
        output += f"cmp [{var_name}] < [.V{end_value}]\n"
        output += f"jt .L{l0}\n"
        output += f"jmp .L{break_label}\n"
        output += f".L{l3}:\n"
        output += f"cmp [{var_name}] > [.V{end_value}]\n"
        output += f"jt .L{l0}\n"
        output += f".L{break_label}:\n"
        
        return res.success(output)
    
    def make_args(self, nodes):
        res = CTResult()
        output = ""
        
        output += f'mov cx, {len(nodes)}\n'
        for node in nodes[::-1]:
            output += res.register(self.emit(node))
            if res.error: return res
            output += "push ax\n"
        
        return res.success(output)
    
    def emit_CallNode(self, node):
        res = CTResult()
        output = ""
        
        if type(node.node_to_call) is not VarAccessNode:
            return res.failure(CTError(node.node_to_call.pos_start,
                                       node.node_to_call.pos_end,
                                       "Function name is not an identifier"))
        
        func_name = node.node_to_call.var_name_tok.value or None
        
        if not func_name in BUILTINS:
            output += res.register(self.make_args(node.arg_nodes))
            if res.error: return res
            
            output += res.register(self.emit(node.node_to_call))
            if res.error: return res
            
            output += "call ax\n"
        else:
            if not func_name in ("asm", "ref", "new"):
                arg_len = len(node.arg_nodes)
                output += res.register(self.make_args(node.arg_nodes))
                    
                output += res.register(BUILTINS[func_name].execute(arg_len))
            else:
                if func_name == "asm":
                    # TODO: return error if arg len is not 1
                    args = node.arg_nodes[0]
                    output += res.register(BUILTINS[func_name].execute(1, args.tok.value, True))
                elif func_name == "ref":
                    arg = node.arg_nodes[0]
                    output += res.register(BUILTINS[func_name].execute(1, arg.var_name_tok.value, True))
                elif func_name == "new":
                    args_len = len(node.arg_nodes)
                    
                    if args_len < 1:
                        return res.failure(CTError(
                        node.pos_start, node.pos_end,
                        f"{1 - len(args_len)} too few args passed into new()"
                    ))
                    
                    arg = node.arg_nodes[0]
                    args = node.arg_nodes[1:]
                    
                    if type(arg) is not ClassNode:
                        return res.failure(CTError(
                            arg.pos_start, arg.pos_end,
                            f"Expected class"
                        ))
                    
                    if arg.var_name_tok.value not in self.class_definitions.keys():
                        return res.failure(CTError(
                            arg.pos_start, arg.pos_end,
                            f"class {arg.var_name_tok.value} not found"
                        ))
                    
                    #value
                    #variable
                    #attr
                    
                    class_name = arg.var_name_tok.value
                    
                    output += f'mov [.temp{class_name}], \'object {class_name}\'\n' if class_name not in self.modules else f'mov [.temp{class_name}], \'module {class_name}\'\n'
                    
                    for property, value in self.class_definitions[class_name]:
                        #value

                        if value is None:
                            output += f'mov ax, 0\n'
                        else:
                            output += res.register(self.emit(value))
                            if res.error: return res
                            
                        output += 'push ax\n'
                        
                        #variable
                        output += f'mov ax, [.temp{class_name}]\n'
                        output += 'push ax\n'
                        
                        #attr
                        output += res.register(self.emit(property))
                        if res.error: return res
                        output += 'push ax\n'
                        
                        output += 'mov ax, 17\n'
                        output += 'bcall\n'
                    
                    methods = self.class_definitions[f'.{class_name}methods'] or None
                    
                    c_id = str(self.var_idx)
                    self.var_idx += 1
                    
                    if methods and methods.element_nodes:
                        for node in methods.element_nodes:
                            func_name = node.func_name_tok.value
                            
                            try:
                                emit = False
                                _ = node.func_name_tok.set
                                c_id = node.func_name_tok.c_id
                            except AttributeError:
                                emit = True
                                func_name = '.' + func_name + c_id
                                node.func_name_tok.value = func_name
                                setattr(node.func_name_tok, 'set', True)
                                setattr(node.func_name_tok, 'c_id', c_id)
                           
                            if func_name == '.constructor' + c_id:
                                if len(node.arg_name_toks) < 1:
                                    return res.failure(CTError(node.func_name_tok.pos_start, node.func_name_tok.pos_end,
                                                            'Class construtor must have at least one argument'))
                                node.body_node.append(ReturnNode(VarAccessNode(node.arg_name_toks[0]),
                                                                 pos_start=node.arg_name_toks[0].pos_start,
                                                                 pos_end=node.arg_name_toks[0].pos_end))
                            
                            # Avoid redefining already defined methods
                            if emit:
                                output += res.register(self.emit(node))
                                if res.error: return res
                            
                            #value
                            output += f'mov ax, [{func_name}]\n'
                            output += 'push ax\n'
                    
                            #variable
                            output += f'mov ax, [.temp{class_name}]\n'
                            output += 'push ax\n'
                            
                            #attr
                            output += f'mov ax, \'{func_name[1:-len(c_id)]}\'\n'
                            output += 'push ax\n'
                            
                            output += 'mov ax, 17\n'
                            output += 'bcall\n'
                            
                            if func_name == '.constructor' + c_id:
                                for arg in args[::-1]:
                                    output += res.register(self.emit(arg))
                                    if res.error: return res
                                    
                                    output += 'push ax\n'
                                
                                output += f'mov ax, [.temp{class_name}]\n'
                                output += 'push ax\n'
                                
                                output += f'call [.constructor{c_id}]\n'
                                output += f'mov [.temp{class_name}], ax\n'
                    
                    output += f'mov ax, [.temp{class_name}]\n'
        
        return res.success(output)
    
    def emit_ReturnNode(self, node):
        res = CTResult()
        output = ""
        
        if node.node_to_return:
            output += res.register(self.emit(node.node_to_return))
            if res.error: return res
        else:
            output += "mov ax, 0\n"
        output += "ret\n"
        
        return res.success(output)

    def emit_FuncDefNode(self, node):
        res = CTResult()
        output = ""
        
        l0 = self.label_idx
        self.label_idx += 1
        
        self.hoisted_definitions += 'mov ax, "function"\n'
        self.hoisted_definitions += 'push ax\n'
        
        self.hoisted_definitions += f"mov [{node.func_name_tok.value}], {node.func_name_tok.value}\n"
        self.hoisted_definitions += f"mov ax, [{node.func_name_tok.value}]\n"
        self.hoisted_definitions += 'push ax\n'
        
        self.hoisted_definitions += "mov ax, '.type'\n"
        self.hoisted_definitions += "push ax\n"
        self.hoisted_definitions += "mov ax, 17\n"
        self.hoisted_definitions += "bcall\n"
        
        output += f"jmp .L{l0}\n"
        
        output += f"{node.func_name_tok.value}:\n"
        
        for arg in node.arg_name_toks:
            output += f"mov [{arg.value}], sp\n"
            output += f"pop\n"
        
        output += res.register(self.emit(node.body_node))
        if res.error: return res
        
        output += f"mov ax, 0\n"
        output += f"ret\n"
        output += f".L{l0}:\n"
        output += f'mov ax, [{node.func_name_tok.value}]\n'
        
        return res.success(output)
    
    def emit_ClassNode(self, node):
        res = CTResult()
        output = ""
        
        output += f"mov ax, 0\n"
        
        return res.success(output)

    # inheriting more than 1 class is still not supported!
    def emit_ClassAssignNode(self, node):
        res = CTResult()
        output = ""
        #print(f"Inheritances: {node.inheritances}") #TODO: make inheritance work n stuff
        class_name = node.var_name_tok.value
        self.class_definitions[class_name] = node.value_node.element_nodes
        if node.module: self.modules[class_name] = node.module
        
        # inherit and override variables
        var_list = []
        if node.value_node.element_nodes:
            for var in node.value_node.element_nodes:
                if var[0].tok.value == '.type':
                    continue
                var_list.append(var[0].tok.value)
        
        #print("var_list:", var_list)
        
        #print(f"value_node: {node.value_node.element_nodes}")
        
        for inheritance in node.inheritances:
            vars = self.class_definitions[inheritance]
            for var in vars:
                if var[0].tok.value == '.type' or var[0].tok.value in var_list:
                    continue
                self.class_definitions[class_name].append(var)
        
        self.class_definitions[f'.{class_name}methods'] = node.methods
        
        # override method
        method_list = []
        if node.methods.element_nodes:
            for method in node.methods.element_nodes:
                method_list.append(method.func_name_tok.value)
        
        #print("method_list:", method_list)
        # inherit methods
        for inheritance in node.inheritances:
            klass = self.class_definitions[f'.{inheritance}methods']
            for method in klass.element_nodes:
                if method.func_name_tok.value in method_list:
                    continue
                self.class_definitions[f'.{class_name}methods'].element_nodes.append(method)
        
        #print(self.class_definitions[f'.{class_name}methods'].element_nodes)

        return res.success(output)
    
    def emit_ListAccessNode(self, node):
        res = CTResult()
        output = ""
        
        if type(node.access_node) is StringNode:
            output += res.register(self.emit(node.left_node))
            if res.error: return res
            output += 'push ax\n'
            
            output += res.register(self.emit(node.access_node))
            if res.error: return res
            output += 'push ax\n'
            
            output += 'mov ax, 18\n'
            output += "bcall\n"
            
            return res.success(output)
        
        output += res.register(self.emit(node.access_node))
        if res.error: return res
        output += "push ax\n"
        
        output += res.register(self.emit(node.left_node))
        if res.error: return res
        output += "push ax\n"
        
        output += "mov ax, 6\n"
        output += "bcall\n"
        
        return res.success(output)
    
    def emit_ListVarAssignNode(self, node):
        res = CTResult()
        output = ""
        
        if type(node.access_node) is StringNode:
            output += res.register(self.emit(node.value_node))
            if res.error: return res
            output += "push ax\n"
            
            output += f'mov ax, [{node.var_name.value}]\n'
            output += 'push ax\n'
            
            output += res.register(self.emit(node.access_node))
            if res.error: return res
            output += 'push ax\n'
            
            output += 'mov ax, 17\n'
            output += "bcall\n"
            
            return res.success(output)
        
        output += res.register(self.emit(node.value_node))
        if res.error: return res
        output += "push ax\n"
        
        output += res.register(self.emit(node.access_node))
        if res.error: return res
        output += "push ax\n"
        
        output += f"push [{node.var_name.value}]\n"
        output += "mov ax, 7\n"
        output += "bcall\n"
        
        return res.success(output)
    
    def setr(self, variable, attr):
        # setattr
        output = ''
        #value
        #variable
        #attr
        
        #value
        output += 'push ax\n'
        
        #variable
        output += f'mov ax, [.V{variable}]\n'
        output += 'push ax\n'
        
        #attr
        output += f'mov ax, "{attr}"\n'
        output += 'push ax\n'
        
        output += 'mov ax, 17\n'
        output += "bcall\n"
        
        return output
    
    def getr(self, variable, attr):
        # getattr
        output = ''
        #variable
        #attr
        
        #variable
        output += f'mov ax, [.V{variable}]\n'
        output += 'push ax\n'
        
        #attr
        output += f'mov ax, "{attr}"\n'
        output += 'push ax\n'
        
        output += 'mov ax, 18\n'
        output += "bcall\n"
        
        return output
    
    def emit_DictNode(self, node):
        res = CTResult()
        output = ""
        var = self.var_idx
        self.var_idx += 1
        
        #if node.dic == {}:
        #    output += 'mov ax, "{}"'
        #    return res.success(output)
        
        output += f'mov [.V{var}], "dict"\n'
        output += f'mov ax, "dict"\n'
        output += self.setr(var, '.type')
        
        keys = 'mov ax, {'
        values = 'mov ax, {'
        i = 0
        for key in node.dic.keys():
        
            var1 = self.var_idx
            self.var_idx += 1
            output += f'mov [.V{var1}], "{key}"\n'
            keys += f'[.V{var1}]'
            
            if not i == len(node.dic.keys())-1:
                keys += ', '
                
            output += res.register(self.emit(node.dic[key]))
            if res.error: return res
            
            var1 = self.var_idx
            self.var_idx += 1
            output += f'mov [.V{var1}], ax\n'
            
            values += f'[.V{var1}]'
            if not i == len(node.dic.values())-1:
                values += ', '
            
            output += self.setr(var, key)
            
            i += 1
        
        keys += '}\n'
        values += '}\n'
        output += keys
        output += self.setr(var, '.keys')
        
        #output += values
        #output += self.setr(var, '.values')
        
        output += f'mov ax, [.V{var}]\n'
        
        return res.success(output)
