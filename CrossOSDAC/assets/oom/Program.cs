using System;
using System.Text;

namespace oom
{
    class Program
    {
        public static void Main()
        {
            StringBuilder sb = new StringBuilder(15, 15);
            sb.Append("Substring #1 ");
            sb.Insert(0, "Substring #2 ", 1);
        }
    }
}
