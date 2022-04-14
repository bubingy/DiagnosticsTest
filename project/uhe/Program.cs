using System;

namespace uhe
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("ready to throw exception");
            throw (new Exception("Exception!!!"));
        }
    }
}
