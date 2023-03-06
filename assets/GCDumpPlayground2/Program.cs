using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GCDumpPlayground2
{
    static class Utils
    {
        public static int Size = (int)(Math.Pow(1024, 2)) * 10;
    }

    class SimpleLinkedList
    {
        public byte Data;
        public SimpleLinkedList Next;
    }

    class A
    {
        public static object AObject = new object();
        public static object BObject = B.BObject;
        public static object CObject = C.CObject;

        public SimpleLinkedList Head;
        public SimpleLinkedList Tail;

        public void DoWork()
        {
            Head = new SimpleLinkedList();
            SimpleLinkedList ptr = Head;

            for (int i = 0; i < Utils.Size; i++)
            {
                ptr.Next = new SimpleLinkedList();
                ptr = ptr.Next;
            }

            Tail = ptr;
        }
    }

    class B
    {
        public static object AObject = A.AObject;
        public static object BObject = new object();
        public static object CObject = C.CObject;

        public SimpleLinkedList Head;
        public SimpleLinkedList Tail;

        public void DoWork()
        {
            Head = new SimpleLinkedList();
            SimpleLinkedList ptr = Head;

            for (int i = 0; i < Utils.Size; i++)
            {
                ptr.Next = new SimpleLinkedList();
                ptr = ptr.Next;
            }

            Tail = ptr;
        }
    }
    

    class C
    {
        public static object AObject = A.AObject;
        public static object BObject = B.BObject;
        public static object CObject = new object();

        public SimpleLinkedList Head;
        public SimpleLinkedList Tail;

        public void DoWork()
        {
            Head = new SimpleLinkedList();
            SimpleLinkedList ptr = Head;

            for (int i = 0; i < Utils.Size; i++)
            {
                ptr.Next = new SimpleLinkedList();
                ptr = ptr.Next;
            }

            Tail = ptr;
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            // scale of size where 1 is 1GB (e.g., 0.5 would be half a gig)
            if (args.Length >= 1)
                Utils.Size = (int)(Utils.Size * float.Parse(args[0]));
            else
                Utils.Size *= 3; // default to ~3GB
            Console.WriteLine("Eating memory...");
            A a = new A();
            B b = new B();
            C c = new C();

            Task.WaitAll(
                Task.Run(() => a.DoWork()),
                Task.Run(() => b.DoWork()),
                Task.Run(() => c.DoWork())
            );

            Console.WriteLine("Pause for gcdumps.  Press <enter> to exit.");
            Console.ReadLine();
        }
    }
}
