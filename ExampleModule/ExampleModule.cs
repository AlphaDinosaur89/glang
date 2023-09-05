using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Alphassembly.Module
{
    public class ExampleModule
    {
        Vm vm;

        public ExampleModule(Vm v)
        {
            vm = v;
        }

        public int ReturnString_args = 0;
        public Value_t ReturnString(List<Value_t> args)
        {
            return new String_t("Balls");
        }
    }
}
