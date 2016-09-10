from cython cimport view
from libc.stdint cimport int64_t


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


ctypedef int64_t dim_t
ctypedef int64_t inc_t
ctypedef int64_t doff_t


# Sucks to set these from magic numbers, but it's better than dragging
# the header into our header.
# We get some piece of mind from checking the values on init.
cpdef enum trans_t:
    NO_TRANSPOSE = 0
    TRANSPOSE = 8
    CONJ_NO_TRANSPOSE = 16
    CONJ_TRANSPOSE = 24


cpdef enum conj_t:
    NO_CONJUGATE = 0
    CONJUGATE = 16


cpdef enum side_t:
    LEFT = 0
    RIGHT = 1


cpdef enum uplo_t:
    LOWER = 192
    UPPER = 96
    DENSE = 224


cpdef enum diag_t:
    NONUNIT_DIAG = 0
    UNIT_DIAG = 256


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
    reals_ft  c, inc_t rsc, inc_t csc,
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
