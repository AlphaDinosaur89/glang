using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;

namespace Alphassembly
{
    class BuiltinFunctions
    {
        public Dictionary<Int64, Func<List<Value_t>, Value_t>> Functions;
        public Vm vm;

        public BuiltinFunctions()
        {
            // TODO: Add list() conversion
            Functions = new Dictionary<Int64, Func<List<Value_t>, Value_t>>();
            Functions.Add(0, Input); // input()
            Functions.Add(1, RandInt); // randint()
            Functions.Add(2, ToInteger); // int()
            Functions.Add(3, ToInteger); // float()
            Functions.Add(4, ToStr); // string()
            Functions.Add(5, ArithFunc); // arithmetics
            Functions.Add(6, GetAt); // getat()
            Functions.Add(7, SetAt); // setat()
            Functions.Add(8, Push); // push()
            Functions.Add(9, Pop); // pop()
            Functions.Add(10, Len); // len()
            Functions.Add(11, Type); // type()
            Functions.Add(12, ToChar); // char()
            Functions.Add(13, SystemExec); // system()
            Functions.Add(14, BreakInput); // breakinput()
            Functions.Add(15, OpenFile); // open()
            Functions.Add(16, Ord); // ord()
            Functions.Add(17, SetAttr); // setattr()
            Functions.Add(18, GetAttr); // getattr()
            Functions.Add(19, Post); // post()
            Functions.Add(20, Get); // get()
            Functions.Add(21, Time); // time()
        }

        public int GetFuncLen(Int64 funcid)
        {
            switch (funcid)
            {
                case 0:
                    return 0;
                case 1:
                    return 2;
                case 2:
                    return 1;
                case 3:
                    return 1;
                case 4:
                    return 1;
                case 5:
                    if (vm.Getbx() is not Integer_t) {
                        Console.Error.WriteLine("bx value is not an integer");
                        Environment.Exit(1);
                    }

                    return Convert.ToInt32(vm.Getbx().Value);
                case 6:
                    return 2;
                case 7:
                    return 3;
                case 8:
                    return 2;
                case 9:
                    return 1;
                case 10:
                    return 1;
                case 11:
                    return 1;
                case 12:
                    return 1;
                case 13:
                    return 1;
                case 14:
                    return 0;
                case 15:
                    return 1;
                case 16:
                    return 1;
                case 17:
                    return 3;
                case 18:
                    return 2;
                case 19:
                    return 3;
                case 20:
                    return 1;
                case 21:
                    return 0;
                default:
                    Console.Error.WriteLine($"Unknown function id: {funcid}");
                    Environment.Exit(1);
                    return 0; // type checker doesnt know line above quits and cant return
            }
        }

        private Value_t Ord(List<Value_t> args)
        {
            // args[0] = char

            return new Integer_t(Convert.ToChar(args[0].Value));
        }

        private Value_t OpenFile(List<Value_t> args)
        {
            // args[0] = filename

            string fullText = System.IO.File.ReadAllText($"{Convert.ToString(args[0].Value)}");
            string[] linesStrings = System.IO.File.ReadAllLines($"{Convert.ToString(args[0].Value)}");

            List_t lines = new List_t(new List<Value_t>());

            foreach (String line in linesStrings)
            {
                lines.Add(new String_t(line));
            }

            List_t ret = new List_t(new List<Value_t>());
            ret.Add(new String_t(fullText));
            ret.Add(lines);

            return ret;
        }

        private Value_t Input(List<Value_t> args)
        {
            return new String_t(Convert.ToString(Console.ReadLine()));
        }

        private Value_t BreakInput(List<Value_t> args)
        {            
            return new String_t(Convert.ToString(Console.ReadKey().KeyChar));
        }

        private Value_t RandInt(List<Value_t> args)
        {
            // args[0] = minimun value
            // args[1] = maximun value

            Random rand = new Random();

            return new Integer_t(rand.Next(Convert.ToInt32(args[0].Value), Convert.ToInt32(args[1].Value) + 1));
        }

        // TODO: add conversion to other types
        private Value_t ToInteger(List<Value_t> args)
        {
            // args[0] = value

            try
            {
                return new Integer_t(Convert.ToInt64(double.Parse(Convert.ToString(args[0].Value),
                    System.Globalization.CultureInfo.InvariantCulture)));
            }
            catch
            {
                try
                {
                    return new Integer_t(Convert.ToInt64(args[0].Value));
                }
                catch
                {
                    Console.Error.WriteLine("Invalid string to convert to integer");
                    Environment.Exit(1);
                    return new Value_t();
                }
            }
        }

        private Value_t ToFloat(List<Value_t> args)
        {
            // args[0] = value

            try
            {
                return new Integer_t(Convert.ToInt64(double.Parse(Convert.ToString(args[0].Value),
                    System.Globalization.CultureInfo.InvariantCulture)));
            }
            catch
            {
                Console.Error.WriteLine("Invalid value to convert to float");
                Environment.Exit(1);
                return new Value_t();
            }
        }

        private Value_t ToStr(List<Value_t> args)
        {
            // args[0] = value

            return new String_t(Convert.ToString(args[0].Value));
        }

        private Value_t ToChar(List<Value_t> args)
        {
            // args[0] = value

            return new String_t(Convert.ToString(Convert.ToChar(Convert.ToInt64(args[0].Value))));
        }

        private Value_t ArithFunc(List<Value_t> args)
        {
            // 3, 2, 2, 1, 3
            Value_t num1 = args[0];
            int i = 1;
            while (i < args.Count) 
            {
                Value_t middle = args[i];
                i++;
                Value_t num2 = args[i];
                i++;

                if (num1 is not Integer_t && num1 is not Float_t)
                {
                    Console.Error.WriteLine("num1 is not float or integer");
                    Environment.Exit(1);
                } else if (middle is not Integer_t)
                {
                    Console.Error.WriteLine("middle is not integer");
                    Environment.Exit(1);
                } else if (num2 is not Integer_t && num2 is not Float_t)
                {
                    Console.Error.WriteLine("num2 is not float or integer");
                    Environment.Exit(1);
                }

                if ((Int64)middle.Value == 1)
                {
                    if (num1 is Integer_t && num2 is Integer_t)
                    {
                        num1 = new Integer_t((Int64)num1.Value + (Int64)num2.Value);
                    } else
                    {
                        num1 = new Float_t(Convert.ToDouble(num1.Value) + Convert.ToDouble(num2.Value));
                    }
                }
                else if ((Int64)middle.Value == 2)
                {
                    if (num1 is Integer_t && num2 is Integer_t)
                    {
                        num1 = new Integer_t((Int64)num1.Value - (Int64)num2.Value);
                    }
                    else
                    {
                        num1 = new Float_t(Convert.ToDouble(num1.Value) - Convert.ToDouble(num2.Value));
                    }
                }
                else if ((Int64)middle.Value == 3)
                {
                    if (num1 is Integer_t && num2 is Integer_t)
                    {
                        num1 = new Integer_t((Int64)num1.Value * (Int64)num2.Value);
                    }
                    else
                    {
                        num1 = new Float_t(Convert.ToDouble(num1.Value) * Convert.ToDouble(num2.Value));
                    }
                }
                else if ((Int64)middle.Value == 4)
                {
                    num1 = new Float_t(Convert.ToDouble(num1.Value) / Convert.ToDouble(num2.Value));
                }
                else if ((Int64)middle.Value == 5)
                {
                    if (num1 is Integer_t && num2 is Integer_t)
                    {
                        num1 = new Integer_t((Int64)num1.Value % (Int64)num2.Value);
                    }
                    else
                    {
                        num1 = new Float_t(Convert.ToDouble(num1.Value) % Convert.ToDouble(num2.Value));
                    }
                }
                else if ((Int64)middle.Value == 6)
                {
                    if (num1 is Integer_t && num2 is Integer_t)
                    {
                        num1 = new Integer_t(Convert.ToInt64(Math.Pow(Convert.ToDouble(num1.Value), Convert.ToDouble(num2.Value))));
                    }
                    else
                    {
                        num1 = new Float_t(Math.Pow(Convert.ToDouble(num1.Value), Convert.ToDouble(num2.Value)));
                    }
                }
                else
                {
                    Console.Error.WriteLine($"arithmetic operation not found: {middle.Value}");
                    Environment.Exit(1);
                    return null;
                }
            }
            
            return num1;
        }

        private Value_t GetAt(List<Value_t> args)
        {
            // args[0] = list/String_t
            // args[1] = idx

            /*
            if (args[0] is not List_t || args[0] is not String_t)
            {
                Console.Error.WriteLine("Argument is not a list or string");
                Environment.Exit(0);
            }
            */

            if (args[0] is List_t || args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "list")
            {
                return ((List<Value_t>)args[0].Value)[Convert.ToInt32(args[1].Value)];
            } else if (args[0] is String_t || args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "string")
            {
                return new String_t(Convert.ToString(Convert.ToString((args[0].Value))[Convert.ToInt32(args[1].Value)]));
            } else
            {
                Console.Error.WriteLine("Error at GetAt function");
                Environment.Exit(1);
                return null;
            }
        }

        private Value_t SetAt(List<Value_t> args)
        {
            // args[0] = list
            // args[1] = idx
            // args[2] = value

            if (args[0] is List_t)
            {
                ((List<Value_t>)args[0].Value)[Convert.ToInt32(args[1].Value)] = args[2];
                return args[0];
            } 
            else if (args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "list")
            {
                ((List<Value_t>)args[0].Value)[Convert.ToInt32(args[1].Value)] = args[2];
                return args[0];
            }
            else if (args[0] is String_t || (args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "list"))
            {
                StringBuilder tempStringBuilder = new StringBuilder(Convert.ToString((String_t)args[0].Value));
                tempStringBuilder[Convert.ToInt32(args[1].Value)] = Convert.ToChar((String_t)args[2].Value);

                String tempString = new String(Convert.ToString(tempStringBuilder));

                return new String_t(tempString);
            } else
            {
                Console.Error.WriteLine("Error at SetAt function");
                Environment.Exit(1);
                return null;
            }
        }

        private Value_t Push(List<Value_t> args)
        {
            // args[0] = list
            // args[1] = value
            ((List < Value_t >) args[0].Value).Add(args[1]);

            return args[0];
        }

        private Value_t Pop(List<Value_t> args)
        {
            // args[0] = list
            ((List<Value_t>)args[0].Value).RemoveAt(((List<Value_t>)args[0].Value).Count-1);

            return args[0];
        }

        private Value_t Len(List<Value_t> args)
        {
            // args[0] = list

            if (args[0] is List_t || args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "list")
            {
                return new Integer_t(((List<Value_t>)args[0].Value).Count);
            } else if (args[0] is String_t || args[0] is Pointer_t && ((Pointer_t)args[0]).PointerType == "string")
            {
                return new Integer_t(Convert.ToString(args[0].Value).Length);
            } else
            {
                Console.Error.WriteLine("Error at Len function");
                Environment.Exit(1);
                return null;
            }             
        }

        private Value_t Type(List<Value_t> args)
        {
            // args[0] = value
            Value_t value = args[0];

            if (value is String_t)
            {
                return new String_t("str");
            } else if (value is Integer_t)
            {
                return new String_t("int");
            } else if (value is Float_t)
            {
                return new String_t("float");
            } else if (value is List_t)
            {
                return new String_t("list");
            } else if (value is Pointer_t)
            {
                return new String_t("ptr");
            }

            Console.Error.WriteLine("This is unreachable in Type function");
            Environment.Exit(1);

            return new Integer_t(0);
        }

        private Value_t SystemExec(List<Value_t> args)
        {
            // args[0] = code

            var process = Process.Start("cmd", $"/C {Convert.ToString((args[0]).Value)}");
            process.WaitForExit();

            return new Integer_t(0);
        }

        private Value_t SetAttr(List<Value_t> args)
        {
            // args[0] = attribute
            // args[1] = variable
            // args[2] = value

            args[1].SetObj(args[0].GetString(), args[2]);

            return args[1];
        }

        private Value_t GetAttr(List<Value_t> args)
        {
            // (Inverted because i am dumb and made the compiler do it this way)
            // args[0] = attribute
            // args[1] = variable

            Value_t value = args[1].GetObj(args[0].GetString());

            if (value != null)
            {
                return value;
            }

            return new Integer_t(0);
        }

        private Value_t Post(List<Value_t> args)
        {
            // args[0] = values
            // args[1] = url
            // args[2] = header

            HttpClient client = new HttpClient();

            Dictionary<string, string> values = new();
            foreach (var val in args[0].Obj)
            {
                values[val.Key] = val.Value.GetString();
            }
            dynamic content = new FormUrlEncodedContent(values);

            foreach (var val in args[2].Obj)
            {
                if (val.Key == "Content-Type")
                {
                    var data = values;
                    var json = JsonSerializer.Serialize(data);
                    content = new StringContent(json, Encoding.UTF8, val.Value.GetString());

                    continue;
                }

                client.DefaultRequestHeaders.Add(val.Key, val.Value.GetString());
            }

            Task<HttpResponseMessage> task = client.PostAsync($"{args[1].GetString()}", content);
            HttpResponseMessage response = task.Result;

            Task<string> task2 = response.Content.ReadAsStringAsync();
            string responseString = task2.Result;

            return new String_t(responseString);
        }

        private Value_t Get(List<Value_t> args)
        {
            // args[0] = url

            HttpClient client = new();

            Task<string> task = client.GetStringAsync(args[0].GetString());
            string responseString = task.Result;

            return new String_t(responseString);
        }

        private Value_t Time(List<Value_t> args)
        {
            DateTime currentTime = DateTime.UtcNow;
            long unixTime = ((DateTimeOffset)currentTime).ToUnixTimeMilliseconds();

            return new Float_t(unixTime/1000.0);
        }
    }
}
