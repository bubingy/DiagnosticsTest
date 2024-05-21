/*
This is a simulator for managed memory behaviors to test the GC performance. It has the following aspects:

1) It provides general things you'd want to do when testing perf, eg, # of threads, running time, allocated bytes.

2) It includes different building blocks to simulate different relevant behaviors for GC, eg, survival rates,
   flat or pointer-rich object graphs, different SOH/LOH ratio.
   
The idea is when we see a relevant behavior we want this simulator to be able to generate that behavior but we
also want to have a dial (ie, how intense that behavior is) and mix it with other behaviors.

Each run writes out a log named pid-output.txt that includes some general info such as parameters used and execution time.

**********************************************************************************************************************

For perf runs I usually run with GC internal logging on which means I'd want to get the last (in memory) part of the log 
at the end. So this provides a config that make it convenient for that purpose by intentionally inducing an exception at 
the end so you can get the last part of the logging by setting this

   for your post mortem debugging in the registry: 
   under HKLM\Software\Microsoft\Windows NT\CurrentVersion\AeDebug 
   you can add a reg value called Debugger of REG_SZ type and it should be
   "d:\debuggers\amd64\windbg" -p %ld -e %ld -c ".jdinfo 0x%p; !DumpGCLog c:\temp;q"
   (obviously make sure the directory for windbg is correct for the machine you run the test on and
   replace c:\temp with whatever directory that you want to put the last part of the log in)

This is by default off and can be turned on via the -endException/-ee config.

**********************************************************************************************************************

When working on this please KEEP THE FOLLOWING IN MIND:

1) Do not use anything fancier than needed. In other words, use very simple code in this project. I am not against 
   using cool/rich lang/framework features normally but for this purpose we want something that's as easy to reason about 
   as possible, eg, using things like linq is forbidden because you don't know how much allocations/survivals it 
   does and even if you do understand perfectly (which is doubtful) it might change and it's a burden for other 
   people who need to work on this. 
   
2) Clearly document your intentions for each building block you write. This is important for others because a building
   block is supposed to be easy to use so in general another person shouldn't need to understand how the code works
   in order to use it. For example, if a building block is supposed to allocate X bytes with Y links (where the user
   specifies X and Y) it should say that in the comments.

3) Only add new files if there's a good reason to. Do NOT create tons of little files.

**********************************************************************************************************************

Right now it's fairly simple - during initialization it allocates an array that holds onto byte 
arrays that are placed on SOH and LOH based on the alloc ratio given; and during steady state it 
allocates byte arrays and survives based on survival intervals given.

It has the following characteristics:

It has a very flat object graph and very simple lifetime. It's a simple test that's good for things that
mostly just care about # of bytes allocated/promoted like BGC scheduling.

It allows you to specify the following commandline args. Notes on commandline args -

1) they are NOT case sensitive;

2) always specify a number as the value for an arg. For boolean values use 1 for true and 0 for false.

3) if you want to still specify an arg but want to use the default (Why? Maybe you want to run this with a lot of different
configurations and it's easier to compare if you have all the configs specified), just specify something that can't be parsed
as an integer. For example you could specify "defArgName". That way you could replace all defArgName with a value if you needed.

-threadCount/-tc: g_threadCount
allocating thread count (usually I use half of the # of CPUs on the machine, this is just to reduce the OS scheduler effect 
so we can test the GC effect better)

-lohAllocRatio/-lohar: g_lohAllocRatio
LOH alloc ratio (this controls the bytes we allocate on LOH out of all allocations we do)
It's in in per thousands (not percents! even though in the output it says %). So if it's 5, that means 
5 of the allocations will be on LOH.

-totalLiveMB/-tlmb: g_totalLiveBytesMB
this is the total live data size in MB

-totalAllocMB/-tamb: g_totalAllocBytesMB
this is the total allocated size in MB, instead of accepting an arg like # of iterations where you don't really know what 
an iteration does, we use the allocated bytes to indicate how much work the threads do.

-totalMins/-tm: g_totalMinutesToRun
time to run in minutes (for things that need long term effects like scheduling you want to run for 
a while, eg, a few hours to see how stable it is)

Note that if neither -totalAllocMB nor -totalMins is specified, it will run for the default for -totalMins.
If both are specified, we take whichever one that's met first. 

-sohSizeRange/-sohsr: g_sohAllocLow, g_sohAllocHigh
eg: -sohSizeRange 100-4000 will set g_sohAllocLow and g_sohAllocHigh to 100 and 4000
we allocate SOH that's randomly chosen between this range.

-sohSizeRange1/-sohsr1: g_sohAllocLow1, g_sohAllocHigh1
if specified we alternate between allocating this range and the other range. This is to test free list management.

-lohSizeRange/-lohsr: g_lohAllocLow, g_lohAllocHigh
we allocate LOH that's randomly chosen between this range.

-lohSizeRange1/-lohsr1: g_lohAllocLow1, g_lohAllocHigh1
if specified we alternate between allocating this range and the other range.

-sohSurvInterval/-sohsi: g_sohSurvInterval
meaning every Nth SOH object allocated will survive. This is something we will consider changing to survival rate
later. When the allocated objects are of similiar sizes the surv rate is 1/g_sohSurvInterval but we may not want them
to all be similiar sizes.

-lohSurvInterval/-lohsi: g_lohSurvInterval
meaning every Nth LOH object allocated will survive. 

Note that -sohSurvInterval/-lohSurvInterval are only applicable for steady state, during initialization everything
survives.

-sohPinningInterval/-sohpi: g_sohPinningInterval
meaning every Nth SOH object survived will be pinned. 

-lohPinningInterval/-lohpi: g_lohPinningInterval
meaning every Nth LOH object survived will be pinned. 

-allocType/-at: g_allocType

What kind of objects are we allocating? Current supported types: 
0 means SimpleItem - a byte array (implemented by the Item class)
1 means ReferenceItem - contains refs and can form linked list (implemented by the ReferenceItemWithSize class)
NOTE!!! currently pinning is not implemented by ReferenceItem.

-handleTest - NOT IMPLEMENTED other than pinned handles. Should write some interesting cases for weak handles.

-lohPauseMeasure/-lohpm: g_lohPauseMeasure
measure the time it takes to do a LOH allocation. When turned on the top 10 longest pauses will be included in the log file.
TODO: The longest pauses are interesting but we should also include all pauses by pause buckets.

-endException/-ee: g_endException
induces an exception at the end so you can do some post mortem debugging.

-disableConsoleOutput/-dco: g_disableConsoleOutput
disable printing stuff on the console

The default for these args are specified in "Default parameters".

---

Other things worth noting:

1) There's also a lohPauseMeasure var that you could make into a config - for now I just always measure pauses for LOH 
   allocs (since it was used for measuring LOH alloc pause wrt BGC sweep).

2) At the end of the test I do an EmptyWorkingSet - the reason for this is when I run the test in a loop if I don't 
   empty the WS for an iteration it's common to observe that it heavily affects the beginning of the next iteration.
*/

using System;
using System.Collections.Generic;
using System.Threading;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;


sealed class Rand
{
    /* Generate Random numbers
     */
    private int x = 0;

    public int getRand()
    {
        x = (314159269 * x + 278281) & 0x7FFFFFFF;
        return x;
    }

    // obtain random number in the range 0 .. r-1
    public int getRand(int r)
    {
        // require r >= 0
        int x = (int)(((long)getRand() * r) >> 31);
        return x;
    }

    public int getRand(int low, int high)
    {
        int p = getRand(high - low);
        return (low + p);
    }

    public double getFloat()
    {
        return (double)getRand() / (double)0x7FFFFFFF;
    }

};

interface ITypeWithPayload
{
    byte[] GetPayload();
    void Free();
}

enum ItemType
{
    SimpleItem = 0,
    ReferenceItem = 1
};

enum ItemState
{
    // there isn't a handle associated with this object.
    NoHandle = 0,
    Pinned = 1,
    Strong = 2,
    WeakShort = 3,
    WeakLong = 4
};

class Item : ITypeWithPayload
{
    public byte[] payload;
    public ItemState state;
    public GCHandle h;

    public Item(int size, bool isPinned=false, bool isWeakLong=false)
    {
        //int baseSize = (3 + 2) * sizeof(IntPtr);
        // I am currently using this for 64-bit only.
        int baseSize = (3 + 2) * 8;
        if (size <= baseSize)
        {
            //Console.WriteLine("allocating objects <= {0} is not supported for the Item class", size);
            throw new System.InvalidOperationException("Item class does not support allocating an object of this size");
        }
        int payloadSize = size - baseSize;
        payload = new byte[payloadSize];

        // We only support these 3 states right now.
        state = (isPinned ? ItemState.Pinned : (isWeakLong ? ItemState.WeakLong : ItemState.NoHandle));

        // We can consider supporting multiple handles pointing to the same object. For now 
        // I am only doing at most one handle per item.
        if (isPinned)
        {
            h = GCHandle.Alloc(payload, GCHandleType.Pinned);
        }
        else if (isWeakLong)
        {
            h = GCHandle.Alloc(payload, GCHandleType.WeakTrackResurrection);
        }
    }

    public void Free()
    {
        if (state != ItemState.NoHandle)
        {
            //Console.WriteLine("freeing handle to byte[{0}]", payload.Length);
            h.Free();
        }

        payload = null;
    }

    public byte[] GetPayload()
    {
        return payload;
    }
};

// This just contains a byte array to take up space
// and since it contains a ref it will exercise mark stack.
class SimpleRefPayLoad
{
    public byte[] payload;

    public SimpleRefPayLoad(int size)
    {
        // this object takes up 3 ptr sizes.
        // the byte array also takes up 3 ptr.
        int sizePayload = size - 8 * 6;
        payload = new byte[sizePayload];
    }
}

enum ReferenceItemOperation
{
    NewWithExistingList = 0,
    NewWithNewList = 1,
    MultipleNew = 2,
    MaxOperation = 3
};

// ReferenceItem is structured this way so we can point to other
// ReferenceItemWithSize objets on decommand and record how much 
// memory it's holding alive.
class ReferenceItemWithSize : ITypeWithPayload
{
    // The size includes indirect children too.
    public int sizeTotal;
    
    // The way we link these together is a linked list.
    // level indicates how many nodes are on the list pointed
    // to by next.
    // We could traverse the list to figure out sizeTotal and level,
    // but I'm keeping them so it's readily available. The list could
    // get very long.
    public int level;
    SimpleRefPayLoad payload;
    ReferenceItemWithSize next;

    public void Free(){}
    public byte[] GetPayload()
    {
        return payload.payload;
    }

    public ReferenceItemWithSize(int size)
    {
        int sizePayload = size - (2 + 3) * 8;
        payload = new SimpleRefPayLoad(sizePayload);
        sizeTotal = size;
        level = 1;
    }

    // The way this is written means you'd need to construct
    // a list from the leave node first.
    public void ReferTo(ReferenceItemWithSize refItem)
    {
        if (refItem != null)
        {
            next = refItem;
            sizeTotal += next.sizeTotal;
            level += refItem.level;
        }
    }

    public void Print()
    {
        int levelCalculated = 0;

        ReferenceItemWithSize nextItem = next;

        while (nextItem != null)
        {
            levelCalculated++;
            //Console.WriteLine("Level: {0,4}, size: {1, 10}", level, sizeTotal);
            nextItem = nextItem.next;
        }

        //Console.WriteLine("this item recorded level {0,4}, calculated level is {1,4}", level, levelCalculated);
    }
}

class MemoryAlloc
{
    private Rand rand;
    private ItemType type;
    private object[] oldArr;
    // TODO We should consider adding another array for medium lifetime.
    private int threadIndex;
    public bool lohPauseMeasure = false;
    private bool printIterInfo = false;
    int sohLow = 0;
    int sohHigh = 0;
    int lohLow = 0;
    int lohHigh = 0;
    int sohLow1 = 0;
    int sohHigh1 = 0;
    int lohLow1 = 0;
    int lohHigh1 = 0;
    int lohAllocIterval = 0;
    int lohAllocRatio = 0;
    Int64 totalLiveBytes = 0;
    Int64 totalLiveBytesCurrent = 0;
    Int64 totalAllocBytes = 0;
    int sohSurvInterval = 0;
    int lohSurvInterval = 0;
    int sohPinningInterval = 0;
    int lohPinningInterval = 0;
    int totalMinutesToRun = 0;
    long printIteration = 0;

    // TODO: replace this with an array that records the 10 longest pauses 
    // and pause buckets.
    public List<double> lohAllocPauses = new List<double>(10);

    //static StreamWriter sw;

    MemoryAlloc(int _threadIndex,
                ItemType _type,
                int _lohAllocRatio, 
                Int64 _totalLiveBytes,
                Int64 _totalAllocBytes,
                int _totalMinutesToRun,
                int _sohLow,
                int _sohHigh,
                int _lohLow,
                int _lohHigh,
                int _sohLow1,
                int _sohHigh1,
                int _lohLow1,
                int _lohHigh1,
                int _sohSurvInterval, 
                int _lohSurvInterval,
                int _sohPinningInterval,
                int _lohPinningInterval,
                bool _lohPauseMeasure,
                long _printIteration)
    {
        rand = new Rand();
        threadIndex = _threadIndex;
        type = _type;

        sohLow = _sohLow;
        sohHigh = _sohHigh;
        lohLow = _lohLow;
        lohHigh = _lohHigh;
        sohLow1 = _sohLow1;
        sohHigh1 = _sohHigh1;
        lohLow1 = _lohLow1;
        lohHigh1 = _lohHigh1;

        printIterInfo = true;
        lohPauseMeasure = _lohPauseMeasure;

        lohAllocRatio = _lohAllocRatio;
        // We need to convert the ratio to an interval so we can decide whether we should allocate
        // a large or a small object. Each LOH object is about ~50x each SOH object, which is 
        // why we are * 50 here.
        if (lohAllocRatio > 0)
        {
            lohAllocIterval = 1000 * 50 / lohAllocRatio;
        }
  
        totalLiveBytes = _totalLiveBytes;
        totalAllocBytes = _totalAllocBytes;

        // default is we survive every 30th element for SOH...this is about 3%.
        sohSurvInterval = _sohSurvInterval;

        // default is we survive every 5th element for SOH...this is about 20%.
        lohSurvInterval = _lohSurvInterval;

        sohPinningInterval = _sohPinningInterval;
        lohPinningInterval = _lohPinningInterval;
        totalMinutesToRun = _totalMinutesToRun;

        printIteration = _printIteration;
    }

    int GetAllocBytes(bool isLarge)
    {
        return (isLarge ? rand.getRand(lohLow, lohHigh) : rand.getRand(sohLow, sohHigh));
    }

    void TouchPage(byte[] b)
    {
        int size = b.Length;

        int pageSize = 4096;

        int numPages = size / pageSize;

        for (int i = 0; i < numPages; i++)
        {
            b[i * pageSize] = (byte)i;
        }
    }
    void TouchPage(ITypeWithPayload item)
    {
        byte[] b = item.GetPayload();
        TouchPage(b);
    }

    public void Init()
    {
        int numSOHElements = (int)(((double)totalLiveBytes * (1000.0 - (double)lohAllocRatio) / 1000.0) / (double)((sohLow + sohHigh) / 2));
        int numLOHElements = (int)(((double)totalLiveBytes * (double)lohAllocRatio / 1000.0) / (double)((lohLow + lohHigh) / 2));

        /*
        sw.WriteLine("Allocating {0} soh elements and {1} loh", numSOHElements, numLOHElements);
        */

        int numElements = numSOHElements + numLOHElements;

        oldArr = new object[numElements];

        int sohAllocatedElements = 0;
        int lohAllocatedElements = 0;
        Int64 sohAllocatedBytes = 0;
        Int64 lohAllocatedBytes = 0;

        for (int i = 0; i < numElements; i++)
        {
            bool isLarge = false;
            if (lohAllocIterval != 0)
            {
                isLarge = ((i % lohAllocIterval) == 0);
            }

            int allocBytes = GetAllocBytes(isLarge);
            object item = (type == ItemType.SimpleItem) ? (object)(new Item(allocBytes)) : new ReferenceItemWithSize(allocBytes);
            TouchPage((ITypeWithPayload)item);
            oldArr[i] = item;
            //Console.WriteLine("ELE#{0}: {1:n0}", i, allocBytes);

            if (isLarge)
            {
                lohAllocatedBytes += allocBytes;
                lohAllocatedElements++;
            }
            else
            {
                sohAllocatedBytes += allocBytes;
                sohAllocatedElements++;
            }
        }

        if (totalAllocBytes != 0)
        {
            totalAllocBytes -= lohAllocatedBytes + sohAllocatedBytes;
        }


        if (type != ItemType.SimpleItem)
        {
            long totalLiveBytesSaved = totalLiveBytes;
            totalLiveBytes = VerifyLiveSize();
        }

        totalLiveBytesCurrent = totalLiveBytes;
    }

    // This really doesn't belong in this class - this should be a building block that takes
    // a data structure and modifies it based on configs, eg, it can modify arrays based on 
    // its element type.
    //
    // Note that this implementation will involve almost only old generation objects so it
    // doesn't affect ephemeral collection time. 
    // 
    // One way to use this is -
    // 
    // we move the first half of the array elements off the array and link them together onto a list.
    // then we discard the list and allocate the 1st half of the array again.
    // we move the second half of the array elements off the array and link them together onto a list.
    // then we discard the list and allocate the 2nd half of the array again.
    // repeat.
    // This means the live data size would be smaller when we remove the list completely and before we
    // allocate enough to replace what we removed.
    // 
    // TODO: ways to configure -
    // 
    // How and how much to convert the array onto a list/lists can be specified a config, eg we could 
    // pick every Nth to convert and make only short lists; or pick elements randomly, or
    // on a distribution, eg, the middle of the array is the most empty.
    // 
    // When do to this, eg do this periodically, or interleaved with replacing elements in the array.
    // 
    // Whether replace the array element with a new one when taking the old one off the array - this 
    // would be useful for temporarily increasing the live data size to see how the heap size changes.
    void MakeListFromContiguousItems(int beginIndex, int endIndex)
    {
        // Take off the end element and link it onto the previous element. Do this
        // till we get to the begin element.
        for (int index = endIndex; index > beginIndex; index--)
        {
            ReferenceItemWithSize refItem = (ReferenceItemWithSize)oldArr[index];
            ReferenceItemWithSize refItemPrev = (ReferenceItemWithSize)oldArr[index - 1];
            refItemPrev.ReferTo(refItem);

            bool isLarge = false;
            if (lohAllocIterval != 0)
            {
                isLarge = ((index % lohAllocIterval) == 0);
            }

            // We are allocating some temp objects here just so that it will trigger GCs.
            // It's unnecesssary if other threads are already allocating objects.
            int allocBytes = GetAllocBytes(isLarge);
            byte[] bTemp = new byte[allocBytes];
            TouchPage(bTemp);

            oldArr[index] = null;
        }

        // This GC will see the longest list.
        // GC.Collect();

        ((ReferenceItemWithSize)oldArr[beginIndex]).Print();
    }
    
    // Somehow I am seeing the live size going lower and lower. This is to verify that we are still
    // surviving what we think we survive. This is pretty slow as we need to go through the whole
    // array.
    // This is only for ref items as simple items are easy to manage.
    long VerifyLiveSize()
    {
        if (type == ItemType.SimpleItem)
            return 0;

        //Console.WriteLine("-----verify BEG------");

        int numElements = oldArr.Length;

        // Each element is pointer size so 8-bytes.
        long liveSizeCalculated = (numElements + 3) * 8;
        //Console.WriteLine("total {0:n0}", liveSizeCalculated);
        int numElementsNull = 0;

        for (int index = 0; index < numElements; index++)
        {
            ReferenceItemWithSize currentItem = (ReferenceItemWithSize)oldArr[index];

            if (currentItem == null)
            {
                numElementsNull++;
            }
            else
            {
                //Console.WriteLine("total {0:n0} + ELE#{1} {2:n0} = {3:n0}",
                //    liveSizeCalculated, index, currentItem.sizeTotal,
                //    (liveSizeCalculated + currentItem.sizeTotal));
                //Console.WriteLine("ELE#{0}: {1:n0}", index, currentItem.sizeTotal);
                liveSizeCalculated += currentItem.sizeTotal;
            }
        }

        //Console.WriteLine("current live is supposed to be {0:n0}, actual is {1:n0}, {2} null items, {3} total items", 
        //    totalLiveBytesCurrent, liveSizeCalculated, numElementsNull, numElements);

        //Console.WriteLine("-----verify END------\n");

        // This is for debugging. They should match up.
        if (liveSizeCalculated != totalLiveBytesCurrent)
        {
            //Console.WriteLine("Problem!!!!, recorded - actual = {0:n0}", (totalLiveBytesCurrent - liveSizeCalculated));
        }

        return liveSizeCalculated;
    }

    public void TimeTest()
    {
        Int64 n = 0;

        Stopwatch stopwatch = new Stopwatch();
        Stopwatch stopwatchGlobal = new Stopwatch();

        //Int64 print_iter = (Int64)1500 * 1024 * 1024;
        Int64 print_iter = printIteration;

        Int64 sohAllocatedBytesTotal = 0;
        Int64 lohAllocatedBytesTotal = 0;

        Int64 sohAllocatedBytes = 0;
        Int64 sohSurvivedBytes = 0;
        Int64 sohPinnedBytes = 0;
        Int64 sohAllocatedCount = 0;
        Int64 sohSurvivedCount = 0;

        Int64 lohAllocatedBytes = 0;
        Int64 lohSurvivedBytes = 0;
        Int64 lohPinnedBytes = 0;
        Int64 lohAllocatedCount = 0;
        Int64 lohSurvivedCount = 0;

        long elapsedLastMS = 0;


        stopwatchGlobal.Reset();
        stopwatchGlobal.Start();

        while (true)
        {
            //if (printIterInfo && (n > 0) && ((n % print_iter) == 0) && (threadIndex == 0))
            if (printIterInfo && (n > 0) && ((n % print_iter) == 0))
            {
                long elapsedCurrentMS = (long)stopwatchGlobal.ElapsedMilliseconds;
                long elapsedDiffMS = elapsedCurrentMS - elapsedLastMS;
                elapsedLastMS = elapsedCurrentMS;
                
                sohAllocatedBytesTotal += sohAllocatedBytes;
                lohAllocatedBytesTotal += lohAllocatedBytes;

                // Reset the numbers.
                sohAllocatedBytes = 0;
                sohSurvivedBytes = 0;
                sohPinnedBytes = 0;
                sohAllocatedCount = 0;
                sohSurvivedCount = 0;

                lohAllocatedBytes = 0;
                lohSurvivedBytes = 0;
                lohPinnedBytes = 0;
                lohAllocatedCount = 0;
                lohSurvivedCount = 0;
            }

            if (n % ((Int64)1 * 1024 * 1024) == 0)
            {
                if (totalMinutesToRun != 0)
                {
                    long elapsedMSec = (long)stopwatchGlobal.Elapsed.TotalMilliseconds;
                    int elapsedMin = (int)(elapsedMSec / (long)1000 / 60);
                    //Console.WriteLine("iter {0}, {1}s elapsed, {2}min", n, elapsedMSec / 1000, elapsedMin);
                    if (elapsedMin >= totalMinutesToRun)
                    {
                        break;
                    }
                }

                if (totalAllocBytes != 0)
                {
                    if ((sohAllocatedBytesTotal + lohAllocatedBytesTotal) >= totalAllocBytes)
                    {
                        //Console.WriteLine("T{0}: SOH/LOH alocated {1:n0}/{2:n0} >= {3:n0}", threadIndex, sohAllocatedBytesTotal, lohAllocatedBytesTotal, totalAllocBytes);
                        break;
                    }
                }
            }

            bool isLarge = false;
            if (lohAllocIterval != 0)
            {
                isLarge = ((n % lohAllocIterval) == 0);
            }

            int allocBytes = GetAllocBytes(isLarge);

            bool shouldSurvive = false;
            bool shouldBePinned = false;

            if (isLarge)
            {
                lohAllocatedBytes += allocBytes;
                lohAllocatedCount++;
                if (lohSurvInterval != 0)
                {
                    shouldSurvive = ((lohAllocatedCount % lohSurvInterval) == 0);
                }
                
                if (shouldSurvive)
                {
                    lohSurvivedCount++;
                    if (lohPinningInterval != 0)
                    {
                        shouldBePinned = ((lohSurvivedCount % lohPinningInterval) == 0);
                    }
                }
            }
            else
            {
                sohAllocatedBytes += allocBytes;
                sohAllocatedCount++;
                if (sohSurvInterval != 0)
                {
                    shouldSurvive = ((sohAllocatedCount % sohSurvInterval) == 0);
                }
                if (shouldSurvive)
                {
                    sohSurvivedCount++;
                    if (sohPinningInterval != 0)
                    {
                        shouldBePinned = ((sohSurvivedCount % sohPinningInterval) == 0);
                    }
                }
            }

            if (isLarge && lohPauseMeasure)
            {
                stopwatch.Reset();
                stopwatch.Start();
            }

            // TODO: We should have a sequence number that just grows (since we only allocate sequentially on 
            // the same thread anyway). This way we can use this number to indicate the ages of items. 
            // If an item with a very current seq number points to an item with small seq number we can conclude
            // that we have young gen object pointing to a very old object. This can help us recognize things
            // like object locality, eg if demotion has demoted very old objects next to young objects.
            object item = (type == ItemType.SimpleItem) ? (object)(new Item(allocBytes, shouldBePinned)) : new ReferenceItemWithSize(allocBytes);

            if (isLarge && lohPauseMeasure)
            {
                stopwatch.Stop();
                lohAllocPauses.Add(stopwatch.Elapsed.TotalMilliseconds);
            }

            TouchPage((ITypeWithPayload)item);

            //Thread.Sleep(1);

            if (shouldSurvive)
            {
                if (isLarge)
                {
                    lohSurvivedBytes += allocBytes;
                    lohPinnedBytes += (shouldBePinned ? allocBytes : 0);
                }
                else
                {
                    sohSurvivedBytes += allocBytes;
                    sohPinnedBytes += (shouldBePinned ? allocBytes : 0);
                }

                // TODO: How to survive shouldn't belong here; it should
                // belong to the building block that churns the array.
                if (type == ItemType.SimpleItem)
                {
                    int itemToReplace = rand.getRand(oldArr.Length);
                    if (oldArr[itemToReplace] != null)
                    {
                        ((ITypeWithPayload)oldArr[itemToReplace]).Free();
                    }
                    oldArr[itemToReplace] = item;
                }
                else
                {
                    // For ref items we want to creative some variation, ie, we want
                    // to create different graphs. But we also want to keep our live 
                    // data size the same. So we do a few different operations -
                    // If the live data size is the same as what we set, we randomly
                    // choose an action which can be one of the following -
                    // 
                    // 1) create a new item, take a few items off the array and link them onto 
                    // the new item.
                    //
                    // 2) create a new item and a few extra ones and link them onto the new item.
                    // note this may not have much affect in ephemeral GCs 'cause it's very likely 
                    // they all get promoted to gen2.
                    //
                    // 3) replace a bunch of entries with newly created items.
                    // 
                    // If the live data size is > what's set, we random choose a non null entry 
                    // and set it to null.
                    ReferenceItemWithSize refItem = (ReferenceItemWithSize)item;
                    ReferenceItemWithSize childItem = null;
                    int randomIndex = 0;
                    // 5 is just a random number I picked that's big enough to exercise the mark stack reasonably.
                    // MakeListFromContiguousItems is another way to make a list.
                    int numItemsToModify = rand.getRand(5);
                    long totalLiveBytesSaved = totalLiveBytesCurrent;
                    //Console.WriteLine("\nlive is supposed to be {0:n0}, current {1:n0}, new item s {2:n0} -> OP {3}",
                    //    totalLiveBytes, totalLiveBytesCurrent, refItem.sizeTotal,
                    //    ((totalLiveBytesCurrent < totalLiveBytes) ? "INC" : "DEC"));

                    if (totalLiveBytesCurrent < totalLiveBytes)
                    {
                        // TODO: need to handle when we get an index that's the same as randomIndexToSurv!!!
                        int randomIndexToSurv = rand.getRand(oldArr.Length);

                        int operationIndex = rand.getRand((int)(ReferenceItemOperation.MaxOperation));
                        if (operationIndex == (int)ReferenceItemOperation.NewWithExistingList)
                        {
                            for (int itemModifyIndex = 0; itemModifyIndex < numItemsToModify; itemModifyIndex++)
                            {
                                randomIndex = rand.getRand(oldArr.Length);
                                ReferenceItemWithSize randomItem = (ReferenceItemWithSize)oldArr[randomIndex];
                                if (randomItem != null)
                                {
                                    randomItem.ReferTo(childItem);
                                    oldArr[randomIndex] = null;
                                    childItem = randomItem;
                                }
                            }
                            int totalChildrenSize = (childItem == null) ? 0 : childItem.sizeTotal;
                            totalLiveBytesCurrent -= totalChildrenSize;
                            refItem.ReferTo(childItem);
                        }
                        else if (operationIndex == (int)ReferenceItemOperation.NewWithNewList)
                        {
                            for (int itemModifyIndex = 0; itemModifyIndex < numItemsToModify; itemModifyIndex++)
                            {
                                ReferenceItemWithSize randomItem = new ReferenceItemWithSize(allocBytes);
                                randomItem.ReferTo(childItem);
                                childItem = randomItem;
                            }
                            refItem.ReferTo(childItem);
                        }
                        else if (operationIndex == (int)ReferenceItemOperation.MultipleNew)
                        {
                            for (int itemModifyIndex = 0; itemModifyIndex < numItemsToModify; itemModifyIndex++)
                            {
                                randomIndex = rand.getRand(oldArr.Length);
                                // This doesn't have to be allocBytes, could be randomly generated and based on
                                // the LOH alloc interval.
                                // For large objects creating a few new ones could be quite significant.
                                ReferenceItemWithSize randomItemNew = new ReferenceItemWithSize(allocBytes);
                                int randomSizeNew = randomItemNew.sizeTotal;
                                totalLiveBytesCurrent += randomSizeNew;

                                ReferenceItemWithSize randomItemToReplace = (ReferenceItemWithSize)oldArr[randomIndex];
                                int itemSizeToReplace = (randomItemToReplace == null) ? 0: randomItemToReplace.sizeTotal;
                                oldArr[randomIndex] = randomItemNew;
                                totalLiveBytesCurrent -= itemSizeToReplace;
                            }
                        }

                        // Now survive the item we allocated.
                        ReferenceItemWithSize itemToReplace = (ReferenceItemWithSize)oldArr[randomIndexToSurv];
                        int sizeToReplace = (itemToReplace == null)? 0 : itemToReplace.sizeTotal;
                        long totalLiveBytesCurrentSaved = totalLiveBytesCurrent;
                        totalLiveBytesCurrent -= sizeToReplace;
                        oldArr[randomIndexToSurv] = item;
                        totalLiveBytesCurrent += refItem.sizeTotal;
                        //Console.WriteLine("final ELE#{0}, s - {1:n0} replaced by {2:n0}",
                        //    randomIndexToSurv, sizeToReplace, refItem.sizeTotal);
                        ////refItem.Print();
                        //Console.WriteLine("{0:n0} - {1} + {2} = {3:n0} op {4}, heap {5:n0}",
                        //    totalLiveBytesCurrentSaved,
                        //    sizeToReplace, refItem.sizeTotal, 
                        //    totalLiveBytesCurrent,
                        //    (ReferenceItemOperation)operationIndex, GC.GetTotalMemory(false));
                    }
                    else
                    {
                        long sizeToReduce = totalLiveBytesCurrent - totalLiveBytes;
                        //Console.WriteLine("need to reduce {0:n0}->{1:n0} ({2} to reduce)",
                        //    totalLiveBytesCurrent, totalLiveBytes, sizeToReduce);

                        int numItemsSearched = 0;
                        int numItemsModified = 0;
                        int numBytesReduced = 0;
                        while (totalLiveBytesCurrent >= totalLiveBytes)
                        {
                            randomIndex = rand.getRand(oldArr.Length);
                            ReferenceItemWithSize randomItem = (ReferenceItemWithSize)oldArr[randomIndex];
                            if (randomItem != null)
                            {
                                totalLiveBytesCurrent -= randomItem.sizeTotal;
                                numBytesReduced += randomItem.sizeTotal;
                                oldArr[randomIndex] = null;
                                numItemsModified++;
                            }
                            numItemsSearched++;
                        }
                        //Console.WriteLine("T#{0} searched {1:n0} items to find {2} modifed",
                        //    threadIndex, numItemsSearched, numItemsModified);
                        //Console.WriteLine("reduced {0}->{1:n0} ({2} to reduce), heap {3:n0}",
                        //    numBytesReduced, totalLiveBytesCurrent, sizeToReduce, GC.GetTotalMemory(false));
                    }

                    VerifyLiveSize();
                }
            }

            n++;
        }
    }

    void PrintPauses()
    {
        if (lohPauseMeasure)
        {
            /*
            sw.WriteLine("T{0} {1:n0} entries in pause, top entries(ms)", threadIndex, lohAllocPauses.Count);
            sw.Flush();
            */

            int numLOHAllocPauses = lohAllocPauses.Count;
            if (numLOHAllocPauses >= 0)
            {
                lohAllocPauses.Sort();
                //lohAllocPauses.OrderByDescending(a => a);
                /*
                sw.WriteLine("===============STATS for thread {0}=================", threadIndex);

                int startIndex = ((numLOHAllocPauses < 10) ? 0 : (numLOHAllocPauses - 10));
                for (int i = startIndex; i < numLOHAllocPauses; i++)
                {
                    sw.WriteLine(lohAllocPauses[i]);
                }

                sw.WriteLine("===============END STATS for thread {0}=================", threadIndex);
                */
            }
        }
    }

    [DllImport("psapi.dll")]
    public static extern bool EmptyWorkingSet(IntPtr hProcess);

    static void DoTest()
    {
        Process currentProcess = Process.GetCurrentProcess();
        int currentPid = currentProcess.Id;
        //string logFileName = currentPid + "-output.txt";
        //sw = new StreamWriter(logFileName);

        /*Console.WriteLine("Process {0}: {1} threads, LOH alloc ratio is {2}o/oo, total live {3}MB, SOH/LOH surv every {4}/{5} elements(every {6}/{7} pinned), {8} LOH alloc pauses",
            currentPid, //0
            g_threadCount, //1
            g_lohAllocRatio, //2
            g_totalLiveBytesMB, //3
            g_sohSurvInterval, //4
            g_lohSurvInterval, //5
            g_sohPinningInterval, //6
            g_lohPinningInterval, //7
            (g_lohPauseMeasure ? "measuring" : "not measuring"));//8*/

        if (g_totalAllocBytesMB != 0)
        {
            //Console.WriteLine("Stopping test after {0}MB", g_totalAllocBytesMB);
        }
        else
        {
           // //Console.WriteLine("Stopping test after {0} mins", g_totalMinutesToRun);
        }

        /*
        sw.WriteLine("Process {0}: {1} threads, LOH alloc ratio is {2}%, total live {3}MB, SOH/LOH surv every {4}/{5} elements(every {6}/{7} pinned), {8} LOH alloc pauses",
            currentPid, g_threadCount, g_lohAllocRatio, g_totalLiveBytesMB, g_sohSurvInterval, g_lohSurvInterval,
            g_sohPinningInterval, g_lohPinningInterval, (g_lohPauseMeasure ? "measuring" : "not measuring"));
        sw.Flush();
        */

        MemoryAlloc[] t = new MemoryAlloc[g_threadCount];
        ThreadStart ts;
        Thread[] threads = new Thread[g_threadCount];
        Int64 totalLiveBytes = (Int64)g_totalLiveBytesMB * (Int64)1024 * (Int64)1024;
        Int64 livePerThread = totalLiveBytes / g_threadCount;
        Int64 allocPerThread = 0;
        if (g_totalAllocBytesMB != 0)
        {
            Int64 totalAllocBytes = (Int64)g_totalAllocBytesMB * (Int64)1024 * (Int64)1024;
            allocPerThread = totalAllocBytes / g_threadCount;
            //Console.WriteLine("allocating {0:n0} per thread", allocPerThread);
        }
        for (int i = 0; i < g_threadCount; i++)
        {
            // For now we have every thread do the same thing, in the future we'd want to have the flexibility 
            // to have different threads do different tasks, eg, one thread might provide some caching functionality
            // while other threads act as worker threads, to simulate real-world workloads; or some threads allocate
            // ReferenceItem type while others allocate SimpleItem type.
            t[i] = new MemoryAlloc(
                i,
                g_allocType,
                g_lohAllocRatio, livePerThread, allocPerThread, 
                g_totalMinutesToRun, 
                g_sohAllocLow, g_sohAllocHigh,
                g_lohAllocLow, g_lohAllocHigh,
                g_sohAllocLow1, g_sohAllocHigh1,
                g_lohAllocLow1, g_lohAllocHigh1,
                g_sohSurvInterval, g_lohSurvInterval, 
                g_sohPinningInterval, g_lohPinningInterval, 
                g_lohPauseMeasure, g_printIteration);
            ts = new ThreadStart(t[i].TimeTest);
            threads[i] = new Thread(ts);
            t[i].Init();
        }

        //sw.WriteLine("after init: heap size {0}, press any key to continue", GC.GetTotalMemory(false));
        //Console.ReadLine();

        long tStart, tEnd;

        for (int i = 0; i < g_threadCount; i++)
        {
            threads[i].Start();
        }

        for (int i = 0; i < g_threadCount; i++)
        {
            threads[i].Join();
        }


        /*
        sw.WriteLine("took {0}ms", (tEnd - tStart));
        sw.Flush();
        */

        for (int i = 0; i < g_threadCount; i++)
        {
            t[i].PrintPauses();
        }

        /*
        sw.Flush();
        sw.Close();
        */
    }

    // Default parameters.
    static int g_threadCount = 4;
    static int g_lohAllocRatio = 5;
    static int g_totalLiveBytesMB = 200;
    static int g_totalAllocBytesMB = 0;
    static int g_totalMinutesToRun = 0;

    static int g_sohAllocLow = 100;
    static int g_sohAllocHigh = 4000;
    static int g_lohAllocLow = 100 * 1000;
    static int g_lohAllocHigh = 200 * 1000;

    static int g_sohAllocLow1 = 0;
    static int g_sohAllocHigh1 = 0;
    static int g_lohAllocLow1 = 0;
    static int g_lohAllocHigh1 = 0;

    static int g_sohSurvInterval = 30;
    static int g_lohSurvInterval = 5;
    static int g_sohPinningInterval = 100;
    static int g_lohPinningInterval = 100;

    static ItemType g_allocType = ItemType.ReferenceItem;

    static bool g_lohPauseMeasure = false;
    static bool g_endException = false;
    static long g_printIteration = (Int64)1 * 1024 * 1024;

    // strRet is what's inbetween strStart and strEnd (not including them)
    // returns what's left in str.
    static string ParseString(string str, string strStart, string strEnd, out string strRet)
    {
        strRet = null;
        int startIndex = ((strStart == null) ? 0 : str.IndexOf(strStart));
        if (startIndex == -1)
        {
            //Console.WriteLine("couldn't find {0} in \"{1}\"!!!", strStart, str);
            return null;
        }
        int strStartLen = ((strStart == null) ? 0 : strStart.Length);

        string strRemaining = str.Substring(startIndex + strStartLen);
        //Console.WriteLine("str is {0}, remaining is {1}", str, strRemaining);

        if (strEnd == null)
        {
            strRet = strRemaining;
            strRemaining = null;
        }
        else
        {
            int endIndex = strRemaining.IndexOf(strEnd);
            strRet = strRemaining.Substring(0, endIndex);
            strRemaining = strRemaining.Substring(endIndex + strEnd.Length);
        }
        //Console.WriteLine("found {0}, remaining is {1}", strRet, strRemaining);
        return strRemaining;
    }

    // Parse a range of the format
    // low-high
    static void ParseRange(string strRange, ref string low, ref string high)
    {
        high = ParseString(strRange, null, "-", out low);
        //Console.WriteLine("{0}: {1}-{2}", strRange, low, high);
    }

    static void ParseInt32(string strInt32, ref int valueWithDefault)
    {
        int val;
        if (Int32.TryParse(strInt32, out val))
        {
            valueWithDefault = val;
        }
    }
    public static void Main(String[] args)
    {
        string strLow = null;
        string strHigh = null;

        for (int i = 0; i < args.Length; ++i)
        {
            string currentArg = args[i];
            string currentArgValue;
            if (currentArg.Equals("-threadCount") || currentArg.Equals("-tc"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_threadCount);
            }
            else if (currentArg.Equals("-lohAllocRatio") || currentArg.Equals("-lohar"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_lohAllocRatio);
            }
            else if (currentArg.Equals("-totalLiveMB") || currentArg.Equals("-tlmb"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_totalLiveBytesMB);
            }
            else if (currentArg.Equals("-totalAllocMb") || currentArg.Equals("-tamb"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_totalAllocBytesMB);
            }
            else if (currentArg.Equals("-totalMins") || currentArg.Equals("-tm"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_totalMinutesToRun);
            }
            else if (currentArg.Equals("-sohSizeRange") || currentArg.Equals("-sohsr"))
            {
                currentArgValue = args[++i];
                ParseRange(currentArgValue, ref strLow, ref strHigh);
                g_sohAllocLow = Int32.Parse(strLow);
                g_sohAllocHigh = Int32.Parse(strHigh);
            }
            else if (currentArg.Equals("-lohSizeRange") || currentArg.Equals("-lohsr"))
            {
                currentArgValue = args[++i];
                ParseRange(currentArgValue, ref strLow, ref strHigh);
                g_lohAllocLow = Int32.Parse(strLow);
                g_lohAllocHigh = Int32.Parse(strHigh);
            }
            else if (currentArg.Equals("-sohSizeRange1") || currentArg.Equals("-sohsr1"))
            {
                currentArgValue = args[++i];
                ParseRange(currentArgValue, ref strLow, ref strHigh);
                g_sohAllocLow1 = Int32.Parse(strLow);
                g_sohAllocHigh1 = Int32.Parse(strHigh);
            }
            else if (currentArg.Equals("-lohSizeRange1") || currentArg.Equals("-lohsr1"))
            {
                currentArgValue = args[++i];
                ParseRange(currentArgValue, ref strLow, ref strHigh);
                g_lohAllocLow1 = Int32.Parse(strLow);
                g_lohAllocHigh1 = Int32.Parse(strHigh);
            }
            else if (currentArg.Equals("-sohSurvInterval") || currentArg.Equals("-sohsi"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_sohSurvInterval);
            }
            else if (currentArg.Equals("-lohSurvInterval") || currentArg.Equals("-lohsi"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_lohSurvInterval);
            }
            else if (currentArg.Equals("-sohPinningInterval") || currentArg.Equals("-sohpi"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_sohPinningInterval);
            }
            else if (currentArg.Equals("-lohPinningInterval") || currentArg.Equals("-lohpi"))
            {
                currentArgValue = args[++i];
                ParseInt32(currentArgValue, ref g_lohPinningInterval);
            }
            else if (currentArg.Equals("-allocType") || currentArg.Equals("-at"))
            {
                currentArgValue = args[++i];
                g_allocType = (ItemType)Int32.Parse(currentArgValue);
            }
            else if (currentArg.Equals("-lohPauseMeasure") || currentArg.Equals("-lohpm"))
            {
                currentArgValue = args[++i];
                g_lohPauseMeasure = (Int32.Parse(currentArgValue) == 1);
            }
            else if (currentArg.Equals("-endException") || currentArg.Equals("-ee"))
            {
                currentArgValue = args[++i];
                g_endException = (Int32.Parse(currentArgValue) == 1);
            }
            else if (currentArg.Equals("-printIter") || currentArg.Equals("-pi"))
            {
                currentArgValue = args[++i];
                g_printIteration = Int64.Parse(currentArgValue);
            }
        }

        if ((g_totalAllocBytesMB == 0) && (g_totalMinutesToRun == 0))
        {
            g_totalMinutesToRun = 1;
        }

        DoTest();

        if (g_endException)
        {
            GC.Collect(2, GCCollectionMode.Forced, true);
            EmptyWorkingSet(Process.GetCurrentProcess().Handle);
            //Debugger.Break();
            throw new System.ArgumentException("Just an opportunity for debugging", "test");
        }
    }
};


