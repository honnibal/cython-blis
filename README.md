Fast BLAS-like operations from Python and Cython, without the tears
========================================================

I hate trying to make sure my numpy stack is linked to the correct BLAS, and I want to avoid asking my users to do it.

BLAS is so ubiquitous in numeric computing, that at some point you stop noticing this missing stair.
You just remember not to trip. But I've always wanted a better solution.

This library vendorises BLIS, a BLAS-like library of linear algebra routines. It's not quite as fast as OpenBLAS,
but it's close, the code is clean and well organised, only little bits are in Assembly, and nothing is in Fortran.

The wrapper is designed to be used from Cython code, and makes heavy use of fused types. This means that you can call the
same function with either a pointer *or* a memory view, and it all just works, with no runtime cost. If you're a frequent
Cython user, you should recognise this as pretty neat. It's usually frustrating when you have a pointer but the API wants
a memoryview, because you can't create one without first acquiring the GIL. The opposite situation is also quite annoying.
Fused types are also used to allow float/double polymorphism, to keep the API trim.

The wrapper isn't finished yet, and nothing has docstrings etc. But the concept works!

You can do 

    pip install blis
    
And, at least on OSX and Ubuntu, the library installs without any dramas. It does take a little longer to compile than it might.
It would be good to trim down the amount of stuff it's compiling.

Windows support for this will probably be painful, but it would be very nice, as Windows users could really use more easily installed options for
numeric computing. I hope someone can help out, and the Windows support could move forward.
