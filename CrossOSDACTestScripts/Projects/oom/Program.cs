using System;
using System.Collections.Generic;

namespace oom
{
    class Program
    {
        public static void Main()
        {
            Double[] values = GetData();
            // Compute mean.
            Console.WriteLine("Sample mean: {0}, N = {1}",
                                GetMean(values), values.Length);
        }

        private static Double[] GetData()
        {
            Random rnd = new Random();
            List<Double> values = new List<Double>();
            for (int ctr = 1; ctr <= 200000000; ctr++) {
                values.Add(rnd.NextDouble());
                if (ctr % 10000000 == 0)
                    Console.WriteLine("Retrieved {0:N0} items of data.",
                                    ctr);
            }
            return values.ToArray();
        }

        private static Double GetMean(Double[] values)
        {
            Double sum = 0;
            foreach (var value in values)
                sum += value;

            return sum / values.Length;
        }
    }
}
