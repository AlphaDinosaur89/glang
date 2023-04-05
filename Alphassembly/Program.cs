using System;
using System.Collections.Generic;
using System.IO;

// alphassembly vm

namespace Alphassembly
{
    struct Case
    {
        public Value_t left;
        public int middle;
        public Value_t right;
    }

    class Vm
    {
        public Int64 ip;
        public Stack<Value_t> stack;
        public Stack<Int64> retstack;

        // registers

        public List<Value_t> ax = new List<Value_t>(); // scratch register
        public List<Value_t> bx = new List<Value_t>(); // preserved register
        public List<Value_t> cx = new List<Value_t>(); // scratch register
        public List<Value_t> dx = new List<Value_t>(); // preserved register
        public Value_t sp;                             // TODO: make this be used as an actual pointer

        // registers

        public Dictionary<Int64, Value_t> BaseVariables = new Dictionary<Int64, Value_t>();
        public List<Dictionary<Int64, Value_t>> Variables = new List<Dictionary<Int64, Value_t>>();

        // flags

        public bool Comp_Flag;

        // flags

        public Vm()
        {
            IncreaseScope(); // scope is at 0
            ax.Add(new Value_t());
            cx.Add(new Value_t());
            ip = 0;
            stack = new Stack<Value_t>();
            retstack = new Stack<Int64>();
        }

        public void IncreaseScope()
        {
            Variables.Add(new Dictionary<Int64, Value_t>());
            bx.Add(new Value_t());
            dx.Add(new Value_t());
        }

        public void DecreaseScope()
        {
            bx.RemoveAt(bx.Count - 1);
            dx.RemoveAt(dx.Count - 1);
            Variables.RemoveAt(Variables.Count - 1);
        }

        public void PrintStack()
        {
            foreach (Value_t v in stack)
            {
                Console.WriteLine(v.Value);
            }
        }

        public Stack<Value_t> GetStack()
        {
            return stack;
        }

        public Value_t GetVariable(Int64 key)
        {
            int i = Variables.Count;

            while (i-1 > 0)
            {
                try
                {
                    return Variables[i - 1][key];
                }
                catch (KeyNotFoundException)
                {
                    i--;
                    if (i == -1)
                    {
                        Console.Error.WriteLine($"Variable {key} not found");
                        Environment.Exit(1);
                    }
                }
            }

            return Variables[i-1][key];
        }
        
        public void SetVariable(Int64 key, Value_t value)
        {
            Variables[Variables.Count-1][key] = value;
        }
        
        public void AddVariable(Int64 key, Value_t value)
        {
            Variables[Variables.Count-1].Add(key, value);
        }

        public Value_t Getax()
        {
            return ax[ax.Count - 1];
        }

        public Value_t Getbx()
        {
            return bx[bx.Count - 1];
        }

        public Value_t Getcx()
        {
            return cx[cx.Count - 1];
        }

        public Value_t Getdx()
        {
            return dx[dx.Count - 1];
        }

        public void Setax(Value_t value)
        {
            ax[ax.Count - 1] = value;
        }

        public void Setbx(Value_t value)
        {
            bx[bx.Count - 1] = value;
        }

        public void Setcx(Value_t value)
        {
            cx[cx.Count - 1] = value;
        }

        public void Setdx(Value_t value)
        {
            dx[dx.Count - 1] = value;
        }
    }

    class Value_t
    {
        protected object value;

        public Dictionary<String, Value_t> Obj = new();

        public virtual object Value { get => value; set => this.value = value; }

        public virtual void SetObj(string key, Value_t value) 
        {
            if (Obj.ContainsKey(key))
            {
                Obj[key] = value;
            }
            else
            {
                Obj.Add(key, value);
            }
        }

        public virtual Value_t GetObj(string key)
        {
            Value_t result = null;

            if (Obj.ContainsKey(key))
            {
                result = Obj[key];
            }

            return result;
        }

        public virtual void SetValue(object num)
        {
            Value = num;
        }

        public virtual object GetValue()
        {
            return Value;
        }

        public virtual string GetString() { return ""; }

    }

    class Float_t : Value_t
    {
        public Float_t(double num)
        {
            Value = num;
        }

        public void SetValue(double num)
        {
            Value = num;
        }

        public Float_t Copy()
        {
            Float_t f = new Float_t((double)Value);
            return f;
        }

        public override string GetString()
        {
            return Convert.ToString(Value, System.Globalization.CultureInfo.InvariantCulture);
        }
    }

    class Integer_t : Value_t
    {

        public Integer_t(Int64 num)
        {
            Value = num;
        }

        public void SetValue(Int64 num)
        {
            Value = num;
        }

        public Integer_t Copy()
        {
            Integer_t i = new Integer_t((Int64)Value);
            return i;
        }

        public override string GetString()
        {
            return Value.ToString();
        }

    }

    class String_t : Value_t
    {

        public String_t(string str)
        {
            Value = str;
        }

        public void SetValue(string str)
        {
            Value = str;
        }

        public String_t Copy()
        {
            String_t i = new String_t((string)Value);
            return i;
        }

        public override string GetString()
        {
            if (Value is Value_t)
            {
                Value = ((Value_t)Value).GetString();
            }
            return (string)Value;
        }

    }

    class List_t : Value_t
    {

        public List_t(List<Value_t> num)
        {
            Value = num;
        }

        public void SetValue(List<Value_t> num)
        {
            Value = num;
        }

        public List_t Copy()
        {
            List_t i = new List_t((List<Value_t>)Value);
            return i;
        }

        public override string GetString()
        {
            string s = "";
            s += '[';
            List<Value_t> vl;
            if (Value is Pointer_t)
            {
                Value = ((Pointer_t)Value).Value;
            }
            vl = (List<Value_t>)Value;
            for (int i = 0; i < vl.Count; i++)
            {
                Value_t val = vl[i];

                if (val is not String_t)
                {
                    s += val.GetString();
                } else
                {
                    s += "'";
                    s += val.GetString();
                    s += "'";
                }
                if (i != ((List<Value_t>)Value).Count-1)
                    s += ", ";
            }
            s += ']';

            return s;
        }

        public void Add(Value_t val)
        {
            ((List<Value_t>)Value).Add(val);
        }

    }

    class Pointer_t : Value_t
    {
        /* not sure if this is the correct way to implement this
         * not sure if pointers can only point to variables
         * (i will add an address type for functions)
         */

        // pointer location in vm.Variables
        private readonly int Reference;
        private readonly int VarScope;
        public readonly string PointerType;

        public override object Value
        {
            get
            {
                if (Program.vm.Variables[VarScope][Reference].Value != null)
                {
                    return Program.vm.Variables[VarScope][Reference].Value;
                }
                else
                {
                    return new Integer_t(0); // null pointer
                }
            }
            set
            {
                if (Program.vm.Variables[VarScope][Reference].Value != null)
                {
                    Program.vm.Variables[VarScope][Reference].Value = value;
                }
                else
                {
                    Console.Error.WriteLine("Null pointer exception: Tried using a null pointer");
                    Environment.Exit(1);
                }
            }
        }

        public override void SetObj(string key, Value_t value)
        {
            if (Program.vm.Variables[VarScope][Reference].Obj.ContainsKey(key))
            {
                Program.vm.Variables[VarScope][Reference].Obj[key] = value;
            }
            else
            {
                Program.vm.Variables[VarScope][Reference].Obj.Add(key, value);
            }
        }

        public override Value_t GetObj(string key)
        {
            Value_t result = null;

            if (Program.vm.Variables[VarScope][Reference].Obj.ContainsKey(key))
            {
                result = Program.vm.Variables[VarScope][Reference].Obj[key];
            }

            return result;
        }

        public void Set(Value_t value)
        {
            Program.vm.Variables[VarScope][Reference] = value;
        }

        public void SetValue(Value_t value)
        {
            Program.vm.Variables[VarScope][Reference].Value = value;
        }

        public override object GetValue()
        {
            return Program.vm.Variables[VarScope][Reference].Value;
        }

        public Value_t GetVar()
        {
            return Program.vm.Variables[VarScope][Reference];
        }

        public Pointer_t(int scope, int id)
        {
            VarScope = scope;
            Reference = id;
            PointerType = GetValueType(Program.vm.Variables[VarScope][Reference]);
        }

        public Pointer_t Copy()
        {
            Pointer_t pointer = new Pointer_t((int)VarScope, Convert.ToInt32(Value));
            return pointer;
        }

        public override String GetString()
        {
            return Program.vm.Variables[VarScope][Reference].GetString();
        }

        private string GetValueType(Value_t value)
        {
            if (value is Integer_t)
            {
                return "int";
            } else if (value is String_t)
            {
                return "string";
            } else if (value is Float_t)
            {
                return "float";
            } else if (value is List_t)
            {
                return "list";
            } else if (value is Pointer_t)
            {
                return "ptr";
            } else
            {
                Console.Error.WriteLine("Unreachable code in Pointer_t.GetValueType()");
                return "";
            }
        }
    }

    class Program
    {
        public static Stack<Value_t> Reverse(Stack<Value_t> input)
        {
            Stack<Value_t> temp = new Stack<Value_t>();

            while (input.Count != 0)
                temp.Push(input.Pop());

            return temp;
        }

        public static int GetLen(Stack<Value_t> stack)
        {
            int len = stack.Count;

            return len;
        }

        public static int GetLen_1(Stack<Int64> stack)
        {
            int len = stack.Count;

            return len;
        }

        enum op : short
        {
            NULL,
            PUSH,
            ADD,
            SUB,
            MUL,
            DIV,
            POP,
            DONE,
            PRINT,
            LD,
            JMP,
            CALL,
            RET,
            JE,
            JN,
            JG,
            JL,
            MOV,
            CMP,
            JT,
            JF,
            MOD,
            BCALL,
            POW,
            TEST,
            PT,
            SPT
        }

        static List<int> fileBytes;
        static object b;
        public static Vm vm;

        static void Advance()
        {
            vm.ip++;
            b = fileBytes[(int)vm.ip];
        }

        static Integer_t ParseInt32()
        {
            int intlen = (int)b;
            Advance();

            int[] bytes = new int[9];

            for (int i = 0; i < intlen; i++)
            {
                bytes[i] = (int)b;
                if (i != intlen - 1)
                {
                    Advance();
                }
            }

            Int64 ret = BitConverter.ToInt64(new byte[8] {
                (byte)bytes[0], (byte)bytes[1],
                (byte)bytes[2], (byte)bytes[3],
                (byte)bytes[4], (byte)bytes[5],
                (byte)bytes[6], (byte)bytes[7]
            });
            Integer_t val_ = new Integer_t(ret);

            return val_;
        }

        static Float_t ParseFloat32()
        {
            int intlen = 8;
            Advance();

            int[] bytes = new int[9];

            for (int i = 0; i < intlen; i++)
            {
                bytes[i] = (int)b;
                if (i != intlen - 1)
                {
                    Advance();
                }
            }

            double ret = BitConverter.ToDouble(new byte[8] { 
                (byte)bytes[0], (byte)bytes[1],
                (byte)bytes[2], (byte)bytes[3],
                (byte)bytes[4], (byte)bytes[5],
                (byte)bytes[6], (byte)bytes[7] });
            Float_t val_ = new Float_t(ret);

            return val_;
        }

        static String_t ParseString()
        {
            string str_ = "";
            for (; ; )
            {
                if ((int)b == 0)
                {
                    vm.ip--;
                    return new String_t(str_);
                }
                else
                {
                    str_ += Convert.ToChar(b);
                }

                Advance();
            }
        }

        static Value_t ParseVariable()
        {
            Advance();

            Int64 ValIdx = (Int64)ParseInt32().Value;

            Value_t ret = null;
            
            try
            {
                ret = vm.GetVariable(ValIdx);
            }
            catch (KeyNotFoundException)
            {
                Console.Error.Write("Variable not found: ");
                Console.Error.WriteLine(ValIdx);
                Console.Error.WriteLine(vm.ip);
                Environment.Exit(0);
            }

            return ret;
        }

        static List_t ParseList()
        {
            Advance();

            List_t list = new List_t(new List<Value_t>());

            Int64 listlen = (Int64)ParseInt32().Value;
            Advance();

            if (listlen != 0)
            {
                for (int i = 0; i < listlen; i++)
                {
                    list.Add(ParseArg());
                }
            }
            return list;
        }

        static Int64 MakeVariable()
        {
            /* Define variable if not defined
             * and set variable value to ParseArg()
             * unless type is variable then check if it is defined
             * and set variable value as the variable
             */

            Int64 ValIdx = (Int64)ParseInt32().Value;
            Advance();
            Value_t _v = null;
            try
            {
                _v = vm.GetVariable(ValIdx);
            } catch (KeyNotFoundException)
            {}

            if (_v != null)
            {
                vm.SetVariable(ValIdx, ParseArg()); 
                return ValIdx;
            }

            vm.AddVariable(ValIdx, ParseArg());

            return ValIdx;
        }

        static Value_t ParseArg()
        {
            Value_t ret = null;
            if ((int)b == 1)
            {
                Advance();

                switch ((int)b)
                {
                    case 0xa:
                        ret = vm.Getax();
                        Advance();
                        break;
                    case 0xb:
                        ret = vm.Getbx();
                        Advance();
                        break;
                    case 0xc:
                        ret = vm.Getcx();
                        Advance();
                        break;
                    case 0xd:
                        ret = vm.Getdx();
                        Advance();
                        break;
                    case 0xe:
                        if (vm.stack.Count < 1)
                        {
                            Console.Error.WriteLine("Stack empty");
                            Environment.Exit(0);
                        }
                        ret = vm.stack.Peek();
                        Advance();
                        break;
                }
            }
            else if ((int)b == 2)
            {
                Advance();

                ret = ParseInt32();
                Advance();
            }
            else if ((int)b == 3)
            {
                Advance();

                ret = ParseString();
            }
            else if ((int)b == 4)
            {
                ret = ParseVariable();
                Advance();
            } 
            else if ((int)b == 5)
            {
                ret = ParseFloat32();
                Advance();
            }
            else if ((int)b == 6)
            {
                ret = ParseList();
            }
            else
            {
                Console.Error.WriteLine(String.Format("Unknown type: {0}, ip {1}", (int)b, vm.ip));
                Environment.Exit(0);
            }

            return ret;
        }

        static Int64 BytesNeeded(Int64 integer)
        {
            int n = 0;
            while (integer != 0)
            {
                integer >>= 8;
                n++;
            }

            return n;
        }

        static string GetType(Value_t value)
        {
            if (value is Pointer_t)
            {
                return ((Pointer_t)value).PointerType;
            } else if (value is Integer_t)
            {
                return "int";
            } else if (value is String_t)
            {
                return "string";
            } else if (value is Float_t)
            {
                return "float";
            } else if (value is List_t)
            {
                return "list";
            } else
            {
                Console.Error.WriteLine("unreachable code reached in GetType function");
                Environment.Exit(1);
                return "";
            }
        }

        static int Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.Error.WriteLine("\nNo file to run");
                return 1;
            }

            string filename = args[0];
            if (File.Exists(filename))
            {
                BuiltinFunctions funcs = new BuiltinFunctions();
                vm = new Vm();
                funcs.vm = vm;
                int l = 0;
                fileBytes = new List<int>();
                foreach (byte o in File.ReadAllBytes(filename))
                {
                    l++;
                    fileBytes.Add(Convert.ToInt32(o));
                }
                
                int currop = 0;
                Value_t num1;
                Value_t num2;
                Value_t result;
                int i;

                for (; ; )
                {
                    if (vm.ip >= fileBytes.Count)
                    {
                        break;
                    }

                    b = fileBytes[(int)vm.ip];

                    switch ((op)currop)
                    {
                        case op.JF:
                            int count = (int)b;
                            if (!vm.Comp_Flag)
                            {
                                vm.ip = (Int64)ParseInt32().Value;
                                b = fileBytes[(int)vm.ip];
                            }
                            else
                            {
                                for (i = 0; i < count + 1; i++)
                                {
                                    Advance();
                                }
                            }

                            currop = 0;
                            break;
                        case op.JT:
                            count = (int)b;
                            if (vm.Comp_Flag)
                            {
                                vm.ip = (Int64)ParseInt32().Value;
                                b = fileBytes[(int)vm.ip];
                            }
                            else
                            {
                                for (i = 0; i < count + 1; i++)
                                {
                                    Advance();
                                }
                            }

                            currop = 0;
                            break;
                        case op.CMP:
                            /* Make list of cases */
                            // case structure: {left_val, comp_operator, right_val}

                            List<Case> CaseList = new List<Case>();
                            List<int> OpList = new List<int>();

                            // case

                            while ((int)b != 0)
                            {
                                Case newcase;

                                newcase.left = ParseArg();
                                newcase.middle = (int)b;
                                Advance();
                                // For some weird ass reason if the the right of the case is a string u need to advance twice after the ParseArg so dont remove this
                                i = (int)b;
                                newcase.right = ParseArg();
                                if (i == 3)
                                {
                                    Advance();
                                    Advance();
                                }

                                CaseList.Add(newcase);

                                if ((int)b != 0)
                                {
                                    OpList.Add((int)b);
                                    Advance();
                                }
                            }

                            /* Interpret cases */

                            bool lastres = false;
                            i = 0;
                            l = 0;
                            int k = 0;
                            int j = 0;
                            Case c = CaseList[k];

                            while (true)
                            {
                                if (k < CaseList.Count)
                                {
                                    c = CaseList[k];
                                }
                                else
                                {
                                    break;
                                }

                                if (c.middle == 1)
                                {
                                    vm.Comp_Flag = false;
                                    if (c.left.GetString() == c.right.GetString())
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }
                                else if (c.middle == 2)
                                {
                                    vm.Comp_Flag = false;
                                    if (c.left.GetString() != c.right.GetString())
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }
                                else if (c.middle == 3)
                                {
                                    vm.Comp_Flag = false;
                                    if (Convert.ToDouble(c.left.Value) > Convert.ToDouble(c.right.Value))
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }
                                else if (c.middle == 4)
                                {
                                    vm.Comp_Flag = false;
                                    if (Convert.ToDouble(c.left.Value) >= Convert.ToDouble(c.right.Value))
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }
                                else if (c.middle == 5)
                                {
                                    vm.Comp_Flag = false;
                                    if (Convert.ToDouble(c.left.Value) < Convert.ToDouble(c.right.Value))
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }
                                else if (c.middle == 6)
                                {
                                    vm.Comp_Flag = false;
                                    if (Convert.ToDouble(c.left.Value) <= Convert.ToDouble(c.right.Value))
                                    {
                                        vm.Comp_Flag = true;
                                    }
                                }

                                if (i == 1)
                                {
                                    if (OpList[j] == 1)
                                    {
                                        vm.Comp_Flag = vm.Comp_Flag && lastres;
                                    }
                                    else if (OpList[j] == 2)
                                    {
                                        vm.Comp_Flag = vm.Comp_Flag || lastres;
                                    }
                                    l += 1;
                                    i = 0;
                                    j += 1;
                                }

                                i += 1;
                                k += 1;
                                lastres = vm.Comp_Flag;
                            }

                            currop = 0;
                            break;
                        case op.MOV:
                            /*
                             * 1 register
                             * 2 int
                             * 3 str
                             * 4 variable
                             * 5 float
                             * 6 list
                             */

                            Value_t val2 = null;
                            int reg = 0;
                            bool isvar = false;

                            if ((int)b != 4)
                            {
                                Advance();

                                switch ((int)b)
                                {
                                    case 0xa:
                                        reg = 0xa;
                                        break;
                                    case 0xb:
                                        reg = 0xb;
                                        break;
                                    case 0xc:
                                        reg = 0xc;
                                        break;
                                    case 0xd:
                                        reg = 0xd;
                                        break;
                                    case 0xe:
                                        reg = 0xe;
                                        break;
                                }

                                Advance();

                                val2 = ParseArg();
                            } else
                            {
                                isvar = true;
                                Advance();

                                MakeVariable();
                            }

                            if (!isvar)
                            {
                                switch (reg)
                                {
                                    case 0xa:
                                        vm.Setax(val2);
                                        break;
                                    case 0xb:
                                        vm.Setbx(val2);
                                        break;
                                    case 0xc:
                                        vm.Setcx(val2);
                                        break;
                                    case 0xd:
                                        vm.Setdx(val2);
                                        break;
                                    case 0xe:
                                        if (vm.stack.Count > 0)
                                            vm.stack.Pop();
                                        vm.stack.Push(val2);
                                        break;
                                }
                            }
                            currop = 0;

                            break;
                        case op.RET:
                            if (GetLen_1(vm.retstack) < 1)
                            {
                                currop = 0;
                                break;
                            }

                            vm.ip = vm.retstack.Pop() - 1;
                            b = fileBytes[(int)vm.ip];
                            vm.DecreaseScope();
                            currop = 0;

                            break;
                        case op.CALL:
                            int bt = (int)b;

                            if (bt != 1)
                                vm.retstack.Push(vm.ip + fileBytes[(int)(vm.ip+1)] + 3);
                            if (bt == 1)
                                vm.retstack.Push(vm.ip + 3);

                            Value_t arg = ParseArg();
                            if (arg is not Integer_t)
                            {
                                Console.Error.WriteLine("Call value must be integer");
                                Environment.Exit(0);
                            }

                            vm.ip = (Int64)arg.Value;
                            b = fileBytes[(int)vm.ip];
                            vm.IncreaseScope();
                            currop = 0;
                            break;
                        case op.JMP:
                            arg = ParseArg();
                            if (arg is not Integer_t)
                            {
                                Console.Error.WriteLine("Jump value must be integer");
                                Environment.Exit(0);
                            }
                            vm.ip = (Int64)arg.Value;
                            b = fileBytes[(int)vm.ip];
                            currop = 0;
                            break;
                        case op.JE:
                            Int64 label = (Int64)ParseInt32().Value;
                            Advance();

                            if (Convert.ToString(vm.stack.Peek().Value) == Convert.ToString(ParseArg().Value))
                            {
                                vm.ip = label;
                                b = fileBytes[(int)vm.ip];
                                currop = 0;
                                break;
                            }
                            currop = 0;

                            break;
                        case op.JN:
                            label = (Int64)ParseInt32().Value;
                            Advance();

                            if (Convert.ToString(vm.stack.Peek().Value) != Convert.ToString(ParseArg().Value))
                            {
                                vm.ip = label;
                                b = fileBytes[(int)vm.ip];
                                currop = 0;
                                break;
                            }
                            currop = 0;

                            break;
                        case op.JG:
                            label = (Int64)ParseInt32().Value;
                            Advance();

                            if (Convert.ToInt32(vm.stack.Peek().Value) > Convert.ToInt32(ParseArg().Value))
                            {
                                vm.ip = label;
                                b = fileBytes[(int)vm.ip];
                                currop = 0;
                                break;
                            }
                            currop = 0;

                            break;
                        case op.JL:
                            label = (Int64)ParseInt32().Value;
                            Advance();

                            if (Convert.ToInt32(vm.stack.Peek().Value) < Convert.ToInt32(ParseArg().Value))
                            {
                                vm.ip = label;
                                b = fileBytes[(int)vm.ip];
                                currop = 0;
                                break;
                            }
                            currop = 0;

                            break;
                        case op.LD:
                            vm.stack.Push(ParseString());
                            currop = 0;
                            break;
                        case op.PRINT:
                            if (GetLen(vm.stack) < 1)
                            {
                                Console.Error.WriteLine("Stack empty");
                                return 1;
                            }

                            Value_t stackpeek = vm.stack.Peek();

                            Console.Write(vm.stack.Peek().GetString());

                            currop = 0;

                            break;
                        case op.DONE:
                            Int64 ret = (Int64)((Integer_t)vm.stack.Pop()).Value;
                            return Convert.ToInt32(ret);
                        case op.POP:
                            if ((int)b == 0)
                            {
                                vm.stack.Pop();
                                Advance();
                            }
                            currop = 0;
                            break;
                        case op.DIV:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            int num1_ = (int)b;
                            num1 = null;
                            Int64 varidx = 0;
                            Int64 sip;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            }
                            else
                            {
                                sip = vm.ip - 1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            result = new Float_t(Convert.ToDouble(num1.Value) / Convert.ToDouble(num2.Value));

                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.MUL:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            num1_ = (int)b;
                            num1 = null;
                            varidx = 0;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            }
                            else
                            {
                                sip = vm.ip - 1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            if (arg is Integer_t && num1 is Integer_t)
                                result = new Integer_t((Int64)num1.Value * (Int64)num2.Value);
                            else
                            {
                                result = new Float_t(Convert.ToDouble(num1.Value) * Convert.ToDouble(num2.Value));
                            }

                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.SUB:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            num1_ = (int)b;
                            num1 = null;
                            varidx = 0;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            }
                            else
                            {
                                sip = vm.ip - 1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            if (num2 is Integer_t && num1 is Integer_t)
                                result = new Integer_t((Int64)num1.Value - (Int64)num2.Value);
                            else
                            {
                                result = new Float_t(Convert.ToDouble(num1.Value) - Convert.ToDouble(num2.Value));
                            }
                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.ADD:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            num1_ = (int)b;
                            num1 = null;
                            varidx = 0;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            } else
                            {
                                sip = vm.ip-1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            if (num2 is Integer_t && num1 is Integer_t)
                                result = new Integer_t((Int64)num1.Value + (Int64)num2.Value);
                            else if (num1 is String_t && num2 is String_t)
                            {
                                result = new String_t((string)num1.Value + (string)num2.Value);
                            }
                            else
                            {
                                result = new Float_t(Convert.ToDouble(num1.Value) + Convert.ToDouble(num2.Value));
                            }
                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.MOD:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            num1_ = (int)b;
                            num1 = null;
                            varidx = 0;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            }
                            else
                            {
                                sip = vm.ip - 1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            if (arg is Integer_t && num1 is Integer_t)
                                result = new Integer_t((Int64)num1.Value % (Int64)num2.Value);
                            else
                            {
                                result = new Float_t(Convert.ToDouble(num1.Value) % Convert.ToDouble(num2.Value));
                            }
                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.POW:
                            reg = 0;
                            if ((int)b != 4)
                            {
                                Advance();
                            }

                            num1_ = (int)b;
                            num1 = null;
                            varidx = 0;

                            switch (num1_)
                            {
                                case 0xa:
                                    reg = 0xa;
                                    break;
                                case 0xb:
                                    reg = 0xb;
                                    break;
                                case 0xc:
                                    reg = 0xc;
                                    break;
                                case 0xd:
                                    reg = 0xd;
                                    break;
                                case 0xe:
                                    reg = 0xe;
                                    break;
                                case 4:
                                    reg = 1;
                                    break;
                            }

                            if (reg != 1)
                            {
                                Advance();
                            }
                            else
                            {
                                sip = vm.ip - 1;
                                Advance();
                                varidx = (Int64)ParseInt32().Value;
                                vm.ip = sip;
                                Advance();
                            }

                            switch (reg)
                            {
                                case 1:
                                    num1 = ParseVariable();
                                    Advance();
                                    break;
                                case 0xa:
                                    num1 = vm.Getax();
                                    break;
                                case 0xb:
                                    num1 = vm.Getbx();
                                    break;
                                case 0xc:
                                    num1 = vm.Getcx();
                                    break;
                                case 0xd:
                                    num1 = vm.Getdx();
                                    break;
                                case 0xe:
                                    num1 = vm.stack.Peek();
                                    break;
                            }

                            arg = ParseArg();
                            num2 = arg;

                            if (arg is Integer_t && num1 is Integer_t)
                            {
                                result = new Integer_t(Convert.ToInt64(Math.Pow(Convert.ToDouble(num1.Value), Convert.ToDouble(num2.Value))));
                            }
                            else
                            {
                                result = new Float_t(Math.Pow(Convert.ToDouble(num1.Value), Convert.ToDouble(num2.Value)));
                            }
                            switch (reg)
                            {
                                case 1:
                                    vm.SetVariable(varidx, result);
                                    break;
                                case 0xa:
                                    vm.Setax(result);
                                    break;
                                case 0xb:
                                    vm.Setbx(result);
                                    break;
                                case 0xc:
                                    vm.Setcx(result);
                                    break;
                                case 0xd:
                                    vm.Setdx(result);
                                    break;
                                case 0xe:
                                    if (vm.stack.Count > 0)
                                    {
                                        vm.stack.Pop();
                                    }
                                    vm.stack.Push(result);
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.PUSH:
                            Value_t retval = null;
                            int type_ = (int)b;

                            if (type_ == 2)
                            {
                                Advance();
                                retval = ParseInt32();
                                Advance();
                            }
                            else if (type_ == 1)
                            {
                                Advance();
                                switch ((int)b)
                                {
                                    case 0xa:
                                        retval = vm.Getax();
                                        Advance();
                                        break;
                                    case 0xb:
                                        retval = vm.Getbx();
                                        Advance();
                                        break;
                                    case 0xc:
                                        retval = vm.Getcx();
                                        Advance();
                                        break;
                                    case 0xd:
                                        retval = vm.Getdx();
                                        Advance();
                                        break;
                                    case 0xe:
                                        retval = vm.stack.Peek();
                                        Advance();
                                        break;
                                }
                            }
                            else if (type_ == 4)
                            {
                                retval = ParseVariable();
                                Advance();
                            }
                            else if (type_ == 5)
                            {
                                retval = ParseFloat32();
                                Advance();
                            }
                            else if (type_ == 6)
                            {
                                retval = ParseList();
                            }
                            else
                            {
                                Console.Error.WriteLine(String.Format("Unknown push type: {0}, ip: {1}", type_, vm.ip));
                                return 1;
                            }

                            vm.stack.Push(retval);

                            currop = 0;
                            break;
                        case op.BCALL:
                            Int64 functionid = Convert.ToInt32(vm.Getax().Value);

                            List<Value_t> args_list = new List<Value_t>();

                            for (i = 0; i < funcs.GetFuncLen(functionid); i++)
                            {
                                try
                                {
                                    args_list.Add(vm.stack.Pop());
                                } catch (InvalidOperationException)
                                {
                                    Console.Error.WriteLine($"Too few arguments passed to function with id: {functionid}");
                                    Environment.Exit(1);
                                }
                            }

                            vm.Setax(funcs.Functions[functionid](args_list));

                            currop = 0;
                            break;
                        case op.TEST:
                            int register = (int)b;

                            Advance();

                            Value_t value = ParseArg();

                            if (value is Integer_t && (Int64)value.Value != 0 ||
                                value is String_t && value.GetString() != "" ||
                                value is Float_t && (double)value.Value != (double)0.0 ||
                                value is List_t && value.GetString() != "[]"
                                )
                            {
                                ret = 1;
                            } else
                            {
                                ret = 0;
                            }

                            switch (register)
                            {
                                case 0xa:
                                    vm.Setax(new Integer_t(ret));
                                    break;
                                case 0xb:
                                    vm.Setbx(new Integer_t(ret));
                                    break;
                                case 0xc:
                                    vm.Setcx(new Integer_t(ret));
                                    break;
                                case 0xd:
                                    vm.Setdx(new Integer_t(ret));
                                    break;
                                case 0xe:
                                    vm.stack.Push(new Integer_t(ret));
                                    break;
                            }

                            currop = 0;
                            break;
                        case op.PT:
                            int scope;
                            Advance();

                            Int64 VarId = (long)ParseInt32().Value;
                            Advance();
                            
                            // look for current scope point to variable if it exists
                            // if not go down 1 scope and repeat
                            // if its never found return an error
                            if ((int)b == 4)
                            {
                                Advance();
                                long StoreIdx = (long)ParseInt32().Value;

                                i = vm.Variables.Count - 1;
                                while (vm.Variables[i][VarId] == null)
                                {
                                    if (i == 0 && vm.Variables[i][VarId] == null)
                                    {
                                        Console.Error.WriteLine($"Variable {VarId} not found");
                                    }
                                    else
                                    {
                                        break;
                                    }
                                    i--;
                                }
                                scope = i;
                                vm.SetVariable(StoreIdx, new Pointer_t(scope, (int)VarId));
                            }
                            Advance();

                            currop = 0;
                            break;
                        case op.SPT:
                            Advance();

                            VarId = (long)ParseInt32().Value;
                            Advance();

                            val2 = ParseArg();

                            if (vm.GetVariable(VarId) is Pointer_t)
                            {
                                ((Pointer_t)vm.GetVariable(VarId)).Set(val2);
                            } else
                            {
                                Console.Error.WriteLine("Can only use spt instruction on pointers");
                                Environment.Exit(1);
                            }

                            currop = 0;
                            break;
                    }

                    if (currop == (int)op.NULL)
                    {
                        switch (b)
                        {
                            case (int)op.SPT:
                                currop = 26;
                                break;
                            case (int)op.PT:
                                currop = 25;
                                break;
                            case (int)op.TEST:
                                currop = 24;
                                break;
                            case (int)op.POW:
                                currop = 23;
                                break;
                            case (int)op.BCALL:
                                currop = 22;
                                break;
                            case (int)op.MOD:
                                currop = 21;
                                break;
                            case (int)op.JF:
                                currop = 20;
                                break;
                            case (int)op.JT:
                                currop = 19;
                                break;
                            case (int)op.CMP:
                                currop = 18;
                                break;
                            case (int)op.MOV:
                                currop = 17;
                                break;
                            case (int)op.JL:
                                currop = 16;
                                break;
                            case (int)op.JG:
                                currop = 15;
                                break;
                            case (int)op.JN:
                                currop = 14;
                                break;
                            case (int)op.JE:
                                currop = 13;
                                break;
                            case (int)op.RET:
                                currop = 12;
                                break;
                            case (int)op.CALL:
                                currop = 11;
                                break;
                            case (int)op.JMP:
                                currop = 10;
                                break;
                            case (int)op.LD:
                                currop = 9;
                                break;
                            case (int)op.PRINT:
                                currop = 8;

                                if (GetLen(vm.stack) < 1)
                                {
                                    Console.Error.WriteLine("\nStack empty");
                                    return 1;
                                }
                                break;
                            case (int)op.DONE:
                                currop = 7;
                                vm.ip--;

                                if (GetLen(vm.stack) < 1)
                                {
                                    Console.Error.WriteLine("\nStack empty");
                                    return 1;
                                }
                                break;
                            case (int)op.POP:
                                if (GetLen(vm.stack) < 1)
                                {
                                    Console.Error.WriteLine("\nNot enough items in stack");
                                    return 1;
                                }
                                currop = 6;
                                break;
                            case (int)op.DIV:
                                currop = 5;
                                break;
                            case (int)op.MUL:
                                currop = 4;
                                break;
                            case (int)op.SUB:
                                currop = 3;
                                break;
                            case (int)op.ADD:
                                currop = 2;
                                break;
                            case (int)op.PUSH:
                                currop = 1;
                                break;
                            case (int)op.NULL:
                                break;
                            default:
                                Console.Error.WriteLine(String.Format("Unknown instruction: {0}", b));
                                return 1;
                        }
                        vm.ip++;
                    }
                }
                return 0;
            }
            else
            {
                Console.Error.WriteLine("File not found");
                return 1;
            }
        }
    }
}
