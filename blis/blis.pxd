from cython cimport view


ctypedef float[:] float1d_t
ctypedef double[:] double1d_t
ctypedef float* floats_t
ctypedef double* doubles_t


cdef fused reals_ft:
    floats_t
    doubles_t
    float1d_t
    double1d_t


cdef fused reals1d_ft:
    float1d_t
    double1d_t


cdef fused real_ft:
    float
    double


ctypedef int dim_t
ctypedef int inc_t
ctypedef int doff_t


cpdef enum trans_t:
    NO_TRANSPOSE
    TRANSPOSE
    CONJ_NO_TRANSPOSE
    CONJ_TRANSPOSE


cpdef enum conj_t:
    NO_CONJUGATE
    CONJUGATE


cpdef enum side_t:
    LEFT
    RIGHT


cpdef enum uplo_t:
    LOWER
    UPPER
    DENSE


cpdef enum diag_t:
    NONUNIT_DIAG
    UNIT_DIAG


cdef void gemm(
    trans_t transa,
    trans_t transb,
    dim_t   m,
    dim_t   n,
    dim_t   k,
    real_ft  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  b, inc_t rsb, inc_t csb,
    real_ft  beta,
    reals_ft  c, inc_t rsc, inc_t csc
) nogil


cdef void ger(
    conj_t  conjx,
    conj_t  conjy,
    dim_t   m,
    dim_t   n,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy,
    reals_ft  a, inc_t rsa, inc_t csa
) nogil


cdef void gemv(
    trans_t transa,
    conj_t  conjx,
    dim_t   m,
    dim_t   n,
    real_ft  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  x, inc_t incx,
    real_ft  beta,
    reals_ft  y, inc_t incy
) nogil


cdef void axpyv(
    conj_t  conjx,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy
) nogil


cdef void scalv(
    conj_t  conjalpha,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx
) nogil
