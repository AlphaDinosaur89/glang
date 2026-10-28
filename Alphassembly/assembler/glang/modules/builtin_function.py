from .errors import *
from .ctresult import *

class BaseFunction():
    def __init__(self, name):
        self.name = name or "<anonymous>"

    def check_args(self, arg_names, args_len):
        res = CTResult()

        if args_len > len(arg_names):
            return res.failure(CTError(
            self.pos_start, self.pos_end,
            f"{args_len - len(arg_names)} too many args passed into {self}",
            self.context
        ))
        
        if args_len < len(arg_names):
            return res.failure(CTError(
            self.pos_start, self.pos_end,
            f"{len(arg_names) - len(args_len)} too few args passed into {self}",
            self.context
        ))

        return res.success(None)

    def populate_args(self, arg_names, args_len):
        output = ""
        for i in range(args_len):
            arg_name = arg_names[i]
            output += f"mov [.V{arg_name}], sp\n"
            output += f"pop\n"
        return output

    def check_and_populate_args(self, arg_names, args_len):
        res = CTResult()
        output = ""
        
        res.register(self.check_args(arg_names, args_len))
        if res.should_return(): return res
        output += self.populate_args(arg_names, args_len)
        return res.success(output)


class BuiltinFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self, args_len, args=None, p=False):
        res = CTResult()
        output = ""

        method_name = f'execute_{self.name}'
        method = getattr(self, method_name, self.no_visit_method)

        if not p:
            output += res.register(self.check_and_populate_args(method.arg_names, args_len))
            if res.error: return res

            output += res.register(method())
            if res.error: return res
        else:
            output += res.register(method(args))

        return res.success(output)

    def no_visit_method(self, node, context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy = BuiltinFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<built-in function {self.name}>"

    def execute_print(self):
        output = ""
        
        output += "push [.Vvalue]\n"
        output += "print\n"
        output += "pop\n"

        return CTResult().success(output)
    execute_print.arg_names = ['value']

    def execute_exit(self):
        output = ""
        
        output += "push [.Vretcode]\n"
        output += "done\n"

        return CTResult().success(output)
    execute_exit.arg_names = ['retcode']
    
    def execute_asm(self, arg):
        output = ""
        
        output += f"{arg}\n"
        
        return CTResult().success(output)
    
    def execute_ref(self, arg): # TODO: this does not work as .Vvalue is used multiple times
        output = ""
        
        # get the name of the variable that needs to be pointed to
        output += f"pt [{arg}], [.Vptr]\n"
        output += "mov ax, [.Vptr]\n"
        
        return CTResult().success(output)
    execute_ref.arg_names = ['ptr']
