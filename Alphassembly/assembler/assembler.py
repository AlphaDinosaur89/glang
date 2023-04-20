from lib2to3.pytree import Node
from math import log
from tokenize import Token
from consts import *
from nodes import *
import struct

class Assembler:
    def __init__(self, nodes):
        self.nodes = nodes
        self.labels = {}
        self.binary = bytearray()
        self.idx = 0
        self.variables = {}
        self.var_idx = 0

    def visit(self, node):
        if node == None:
            return
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    def assemble(self):
        self.fixlabel = True
        
        self.flag = True
        for node in self.nodes:
            self.idx += 1
            self.visit(node)
        
        self.binary = bytearray()
        
        self.idx = 0

        for node in self.nodes:
            self.idx += 1
            self.visit(node)
        
        self.binary = bytearray()
        
        self.idx = 0

        for node in self.nodes:
            self.idx += 1
            self.visit(node)
        
        self.binary = bytearray()
        
        self.fixlabel = False        
        self.flag = False
        
        self.idx = 0

        for node in self.nodes:
            self.idx += 1
            self.visit(node)
        self.binary.append(0)
        
        return self.binary
    
    def make_variable(self, varname):
        if varname not in self.variables:
            pass
        else:
            self.idx += 2
            self.binary.append(4)
            self.make_int32(self.variables[varname])
            return
        
        self.variables[varname] = self.var_idx
        
        self.idx += 2
        self.binary.append(4)
        self.make_int32(self.var_idx)
        
        self.var_idx += 1
    
    def bytes_needed(self, n):
        if n == 0:
            return 1
        elif n is None:
            return 1
        return int(log(n, 256)) + 1
    
    def make_int32(self, integer, label=None):
        if integer is None:
            integer = 0
        
        if label:
            if label in self.labels.keys():
                self.idx += 1
                integer = self.labels[label]
        
        needed_bytes = self.bytes_needed(integer)
        if needed_bytes == 0:
            needed_bytes = 1
        
        self.idx += needed_bytes
        if needed_bytes > 1 and self.fixlabel:
            for label in self.labels:
                if self.labels[label] > self.idx:
                    self.labels[label] += needed_bytes-1
        self.binary.append(needed_bytes)
            
        self.binary.extend(integer.to_bytes(needed_bytes, 'little'))
    
    def make_double64(self, float):
        if float > 1.7976931348623157E+308:
            raise Exception("Float too big")
        
        needed_bytes = 8
        if needed_bytes == 0:
            needed_bytes = 1
        
        self.idx += needed_bytes
            
        self.binary.extend(struct.pack("d", float))

    def make_string(self, string):
        for char in string:
            self.binary.append(ord(char))

        self.binary.append(0)
    
    def make_arg(self, val, jmp=False):
        pc = False
        if type(val) is ListNode:
            self.make_list(val)
        elif val.type == TT_IDENTIFIER:
            if val.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[val.value])
            else:
                #try:
                #    if self.bytes_needed(self.labels[val.value]) == 2:
                #        pass
                #    elif self.bytes_needed(self.labels[val.value]) == 3:
                #        self.idx -= 1
                #    elif self.bytes_needed(self.labels[val.value]) == 4:
                #        self.idx -= 2
                #    else:
               #         self.idx += 1
               # except KeyError:
               #     pass
               if not jmp:
                    self.idx += 1
                    self.binary.append(2)
                    
                    self.make_int32(None, label=val.value)
               else:
                   if self.labels.get(val.value):
                        self.idx += 1
                        #if self.bytes_needed(self.labels[val.value]) == 2:
                        #    pass
                        #elif self.bytes_needed(self.labels[val.value]) == 3:
                        #    self.idx -= 1
                        #elif self.bytes_needed(self.labels[val.value]) == 4:
                        #    self.idx -= 2
                        #else:
                        #    self.idx += 1
                                
                        self.binary.append(2)
                        if self.labels.get(val.value):
                                self.make_int32(None, label = val.value)
                   
                #raise Exception(f"Register: {val.value} not found")
        elif val.type == TT_INT:
            if self.bytes_needed(val.value) == 2:
                pass
            elif self.bytes_needed(val.value) == 3:
                self.idx -= 1
            elif self.bytes_needed(val.value) == 4:
                self.idx -= 2
            else:
                self.idx += 1
                
            self.idx += self.bytes_needed(val.value)
            self.binary.append(2)
            self.make_int32(val.value)
        elif val.type == TT_FLOAT:
            self.idx += 1
            self.binary.append(5)
            self.make_double64(val.value)
        elif val.type == TT_STRING:
            self.idx += len(val.value) + 2
            self.binary.append(3)
            self.make_string(val.value)
        elif val.type == TT_VARIABLE:
            self.make_variable(val.value)
    
    def make_register(self, val):
        if val.type == TT_IDENTIFIER:
            if val.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[val.value])
            else:
                raise Exception(f"Register: '{val.value}' not found")
    
    def make_op(self, val):
        self.idx += 1
        if val.type == TT_EE:
            self.binary.append(1)
        elif val.type == TT_NE:
            self.binary.append(2)
        elif val.type == TT_GT:
            self.binary.append(3)
        elif val.type == TT_GTE:
            self.binary.append(4)
        elif val.type == TT_LT:
            self.binary.append(5)
        elif val.type == TT_LTE:
            self.binary.append(6)
        else:
            raise Exception(f"Unrecognized operator: '{val.type}'")
    
    def make_list(self, node):
        self.idx += 2
        self.binary.append(6)
        
        self.make_int32(len(node.nodes_list))
        
        for node in node.nodes_list:
            val = self.visit(node)
            self.make_arg(val)

    ###################################

    def visit_LoadNode(self, node):
        string = node.string.value

        self.binary.append(9)

        self.make_string(string)

        self.idx += len(string) + 1
    
    def visit_PrintNode(self, node):
        self.binary.append(8)
    
    def visit_DoneNode(self, node):
        self.binary.append(7)
    
    def visit_PopNode(self, node):
        self.binary.append(6)
        
        if not node.reg == None:
            self.make_register(node.reg)
        else:
            self.idx += 1
            self.binary.append(0)
    
    def visit_DivNode(self, node):
        self.binary.append(5)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")

        self.make_arg(node.val2)
    
    def visit_MulNode(self, node):
        self.binary.append(4)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")

        self.make_arg(node.val2)
    
    def visit_SubNode(self, node):
        self.binary.append(3)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")
            
        self.make_arg(node.val2)
    
    def visit_AddNode(self, node):
        self.binary.append(2)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")
            
        self.make_arg(node.val2)
    
    def visit_ModuloNode(self, node):
        self.binary.append(21)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")
            
        self.make_arg(node.val2)
    
    def visit_PowNode(self, node):
        self.binary.append(23)

        if node.val1.type == TT_IDENTIFIER:
            if node.val1.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                self.binary.append(REGISTERS[node.val1.value])
        elif node.val1.type == TT_VARIABLE:
            self.make_variable(node.val1.value)
        else:
            raise Exception("Left operand must be a register or variable")
            
        self.make_arg(node.val2)
    
    def visit_PushNode(self, node):
        if type(node.value) is not ListNode:
            value = node.value.value or None
            type_ = node.value.type or None
        
        self.binary.append(1)

        # TODO: test if this works (pushing list)
        if type(node.value) is ListNode:
            self.make_list(node.value)
        elif type_ == TT_INT:
            self.binary.append(2)
            self.make_int32(value)

            self.idx += self.bytes_needed(value) + 1
            self.idx -= self.bytes_needed(value) - 1
        elif type_ == TT_FLOAT:
            self.binary.append(5)
            self.make_double64(value)
            
            self.idx += 1
        elif type_ == TT_IDENTIFIER:
            self.binary.append(1)
            
            if value in REGISTERS:
                if value == "ax":
                    self.binary.append(0xa)
                if value == "bx":
                    self.binary.append(0xb)
                if value == "cx":
                    self.binary.append(0xc)
                if value == "dx":
                    self.binary.append(0xd)
                if value == "sp":
                    self.binary.append(0xe)
            else:
                raise Exception(f"Register not found: {value}")

            self.idx += 2
        elif type_ == TT_VARIABLE:
            self.make_variable(value)
    
    def visit_LabelNode(self, node):
        self.idx -= 1
        if self.flag:
            self.labels[node.name.value] = self.idx
    
    def visit_JumpNode(self, node):
        
        #label = self.labels.get(node.label.value, None) or 0
        
        #if type(node.label.value) is str and label is None:
        #    raise Exception("Label not found")
        
        self.binary.append(10)
        
        self.make_arg(node.label, jmp=True)
    
    def visit_JeNode(self, node):
        self.idx += 1
        
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
        
        self.binary.append(13)

        self.make_int32(label)
        
        self.make_arg(node.argument)

    def visit_JnNode(self, node):
        self.idx += 1
        
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
    
        self.binary.append(14)

        self.make_int32(label)
        
        self.make_arg(node.argument)
    
    def visit_JgNode(self, node):
        self.idx += 1
        
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
    
        self.binary.append(15)

        self.make_int32(label)
        
        self.make_arg(node.argument)
    
    def visit_JlNode(self, node):
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
    
        self.binary.append(16)

        self.make_int32(label)
        
        self.make_arg(node.argument)
    
    def visit_JtNode(self, node):
        self.idx += 1
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
    
        self.binary.append(19)

        self.make_int32(label)
    
    def visit_JfNode(self, node):
        self.idx += 1
    
        label = self.labels.get(node.label.value, None) or 0
        if type(node.label.value) is str and label is None:
            raise Exception("Label not found")
    
        self.binary.append(20)

        self.make_int32(label)
    
    def visit_CallNode(self, node):
        
        #label = self.labels.get(node.label.value, None) or 0
        #if type(node.label.value) is str and label is None:
        #    raise Exception("Label not found")
    
        self.binary.append(11)
        
        self.make_arg(node.label, jmp=True)
        
        #self.make_int32(label)
    
    def visit_RetNode(self, node):
        self.binary.append(12)
    
    def visit_MovNode(self, node):
        # 1 register
        # 2 int
        # 3 str
        # 4 variable
        # 5 float
        # 6 list
        self.binary.append(17)

        if node.left.type == TT_IDENTIFIER:
            if node.left.value in REGISTERS:
                self.idx += 2
                self.binary.append(1)
                if node.left.value == "ax":
                    self.binary.append(0xa)
                elif node.left.value == "bx":
                    self.binary.append(0xb)
                elif node.left.value == "cx":
                    self.binary.append(0xc)
                elif node.left.value == "dx":
                    self.binary.append(0xd)
                elif node.left.value == "sp":
                    self.binary.append(0xe)
            else:
                raise Exception(f"Register: {node.left.value} not found")
        elif node.left.type == TT_INT:
            raise Exception("Cannot copy value to an integer")
        elif node.left.type == TT_FLOAT:
            raise Exception("Cannot copy value to a float")
        elif node.left.type == TT_STRING:
            raise Exception("Cannot copy value to a string")
        elif node.left.type == TT_VARIABLE:
            self.make_variable(node.left.value)
        else:
            # can only happend when moving to a list
            raise Exception("Cannot copy value to a list")
        
        self.make_arg(node.right)
    
    def visit_StringNode(self, node):
        return node.tok

    def visit_IntegerNode(self, node):
        return node.tok
    
    def visit_FloatNode(self, node):
        return node.tok
    
    def visit_RegisterNode(self, node):
        return node.tok

    def visit_VariableNode(self, node):
        return node.tok
    
    def visit_ListNode(self, node):
        return node

    def visit_CmpNode(self, node):
        cases = node.cases
        
        self.idx += 1
        
        self.binary.append(18)
        i = 0
        while True:
            case = cases[i]
            left = self.visit(case[0])
            middle = case[1]
            right = self.visit(case[2])

            self.make_arg(left)
            self.make_op(middle)
            self.make_arg(right)
            
            i += 1
            if i >= len(cases):
                break

            if cases[i] == TT_AND:
                self.idx += 1
                self.binary.append(1)
                i += 1
            elif cases[i] == TT_OR:
                self.idx += 1
                self.binary.append(2)
                i += 1

        self.binary.append(0)
    
    def visit_EOFNode(self, node):
        self.idx -= 1
        pass
    
    def visit_BCallNode(self, node):
        self.binary.append(22)
    
    def visit_TestNode(self, node):
        self.binary.append(24)

        if node.left.type == TT_IDENTIFIER:
            if node.left.value in REGISTERS:
                self.idx += 1
                if node.left.value == "ax":
                    self.binary.append(0xa)
                elif node.left.value == "bx":
                    self.binary.append(0xb)
                elif node.left.value == "cx":
                    self.binary.append(0xc)
                elif node.left.value == "dx":
                    self.binary.append(0xd)
                elif node.left.value == "sp":
                    self.binary.append(0xe)
            else:
                raise Exception(f"Register: {node.left.value} not found")
        elif node.left.type == TT_INT:
            raise Exception("Cannot copy value to an integer")
        elif node.left.type == TT_FLOAT:
            raise Exception("Cannot copy value to a float")
        elif node.left.type == TT_STRING:
            raise Exception("Cannot copy value to a string")
        elif node.left.type == TT_VARIABLE:
            self.make_variable(node.left.value)
        else:
            # can only happend when moving to a list
            raise Exception("Cannot copy value to a list")

        self.make_arg(node.right)
        
        # TODO: Finish implementation of test instruction
    
    def visit_PtNode(self, node):
        self.binary.append(25)
        
        if node.target.type == TT_VARIABLE:
            self.make_variable(node.target.value)
        else:
            raise Exception("Can only point to a variable") # TODO: maybe change this in the future if needed

        if node.storage.type == TT_VARIABLE:
            self.make_variable(node.storage.value)
        else:
            raise Exception("Can only store a pointer in a variable")
    
    def visit_SptNode(self, node):
        self.binary.append(26)
        
        if node.target.type == TT_IDENTIFIER:
            if node.target.type in REGISTERS:
                self.make_register(node.target)
            else:
                raise Exception(f"Register: {node.target.value} not found")
        elif node.target.type == TT_VARIABLE:
            self.make_variable(node.target.value)
        else:
            raise Exception("Can only set a pointer value in a variable or a register")
        
        self.make_arg(node.arg)