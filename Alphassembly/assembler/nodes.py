class EOFNode:
    def __init__(self):
        pass

class SptNode:
    def __init__(self, target, arg):
        self.target = target
        self.arg = arg

class PtNode:
    def __init__(self, target, storage):
        self.target = target
        self.storage = storage

class BCallNode:
    def __init__(self):
        pass

class ModuloNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2

class LoadNode:
    def __init__(self, string):
        self.string = string


class PrintNode:
    def __init__(self):
        pass


class StringNode:
    def __init__(self, val):
        self.tok = val


class VariableNode:
    def __init__(self, tok) -> None:
        self.tok = tok


class IntegerNode:
    def __init__(self, val):
        self.tok = val


class FloatNode:
    def __init__(self, val):
        self.tok = val


class RegisterNode:
    def __init__(self, val):
        self.tok = val


class CmpNode:
    def __init__(self, cases):
        self.cases = cases
        

class DoneNode:
    def __init__(self):
        pass


class PopNode:
    def __init__(self, reg):
        self.reg = reg


class DivNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2


class MulNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2


class SubNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2


class AddNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2


class PowNode:
    def __init__(self, val1, val2):
        self.val1 = val1
        self.val2 = val2


class PushNode:
    def __init__(self, value):
        self.value = value


class LabelNode:
    def __init__(self, name):
        self.name = name


class JumpNode:
    def __init__(self, label):
        self.label = label


class JeNode:
    def __init__(self, label, argument):
        self.label = label
        self.argument = argument


class JnNode:
    def __init__(self, label, argument):
        self.label = label
        self.argument = argument


class JgNode:
    def __init__(self, label, argument):
        self.label = label
        self.argument = argument


class JlNode:
    def __init__(self, label, argument):
        self.label = label
        self.argument = argument


class JtNode:
    def __init__(self, label):
        self.label = label


class JfNode:
    def __init__(self, label):
        self.label = label


class CallNode:
    def __init__(self, label):
        self.label = label


class RetNode:
    def __init__(self):
        pass


class MovNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class ListNode:
    def __init__(self, nodes_list):
        self.nodes_list = nodes_list

class TestNode:
    def __init__(self, left, right):
        self.left = left
        self.right = right
