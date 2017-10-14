Fast BLAS-like operations from Python and Cython, without the tears
========================================================

This repository provides the Blis linear algebra as a self-contained Python
C-extension. You can install the package via pip, optionally specifying your
machine's architecture via an environment variable:
    
    BLIS_ARCH=haswell pip install blis

After installation, run a simple matrix multiplication benchmark:

    $ python -m blis.benchmark    
    Setting up data nO=384 nI=384 batch_size=2000. Running 1000 iterations
    Blis...
    Total: 11032014.6484
    7.35 seconds
    Numpy (Openblas)...
    Total: 11032016.6016
    16.81 seconds

This is on a Dell XPS 13 i7-7500U. Running the same benchmark on a 2015 Macbook
Air gives:  
    
    Blis...
    Total: 11032014.6484
    8.89 seconds
    Numpy (Accelerate)...
    Total: 11032012.6953
    6.68 seconds
                            
It might be that Openblas is performing poorly on the relatively small
matrices (which are typically the sizes I'm working with for my neural
network models). 

Usage
-----

You can call the Python bindings with any object that exposes the buffer
interface, e.g. numpy arrays:

    from blis.py import gemm
    from numpy import ndarray, zeros

    nN = 500 # e.g. batch size
    nI = 128 # e.g. input dimension
    nO = 300 # e.g. output dimension
    A = ndarray((nN, nI), dtype='f') e.g. input data X
    B = ndarray((nI, nO), dtype='f') e.g. weights W
    C = gemm(A, B) # e.g. Y = X.dot(W)
    # If you already have an output buffer, you can avoid extra allocations.
    gemm(A, B, out=C)
    # Arrays must be C-contiguous
    # gemm(A, B.T, out=C, transB=True) <-- Raises TypeError
    B_T = numpy.ascontiguousarray(B.T)
    gemm(A, B_T, out=C, transB=True)

The library also provides fused-type, nogil Cython bindings. Fused types are
a simple template mechanism, allowing just a touch of compile-time generic
programming:

    cimport blis.cy
    A = <float*>calloc(nN * nI, sizeof(float))
    B = <float*>calloc(nO * nI, sizeof(float))
    C = <float*>calloc(nr_b0 * nr_b1, sizeof(float))
    blis.cy.gemm(blis.cy.NO_TRANSPOSE, blis.cy.NO_TRANSPOSE,
                 nO, nI, nN,
                 1.0, A, nI, 1, B, nO, 1,
                 1.0, C, nO, 1)


Bindings have been added as we've needed them. Please submit pull requests if
the library is missing some functions you require.

