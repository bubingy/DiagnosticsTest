using System;

namespace runfeaturetest
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello World!");
            int x = 0;
            for (int i = 0; i < 10; i++)
            {
                x++;
                System.Threading.Thread.Sleep(1000);
            }
            Console.WriteLine(x);
        }
    }
}
