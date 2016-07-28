# cython: infer_types=True
# cython: boundscheck=False

cdef extern from "_include/blis.h" nogil:
    enum blis_err_t "err_t": 
        pass


    cdef struct blis_cntx_t "cntx_t":
        pass


    ctypedef enum blis_trans_t "trans_t":
        BLIS_NO_TRANSPOSE
        BLIS_TRANSPOSE
        BLIS_CONJ_NO_TRANSPOSE
        BLIS_CONJ_TRANSPOSE

    ctypedef enum blis_conj_t "conj_t":
        BLIS_NO_CONJUGATE
        BLIS_CONJUGATE

    ctypedef enum blis_side_t "side_t":
        BLIS_LEFT
        BLIS_RIGHT

    ctypedef enum blis_uplo_t "uplo_t":
        BLIS_LOWER
        BLIS_UPPER
        BLIS_DENSE

    ctypedef enum blis_diag_t "diag_t":
        BLIS_NONUNIT_DIAG
        BLIS_UNIT_DIAG

    blis_err_t bli_init()
    blis_err_t bli_finalize()

    # BLAS level 3 routines
    void bli_dgemm(
       blis_trans_t transa,
       blis_trans_t transb,
       dim_t   m,
       dim_t   n,
       dim_t   k,
       double*  alpha,
       double*  a, inc_t rsa, inc_t csa,
       double*  b, inc_t rsb, inc_t csb,
       double*  beta,
       double*  c, inc_t rsc, inc_t csc,
       blis_cntx_t* cntx
    )
    # BLAS level 3 routines
    void bli_sgemm(
       blis_trans_t transa,
       blis_trans_t transb,
       dim_t   m,
       dim_t   n,
       dim_t   k,
       float*  alpha,
       float*  a, inc_t rsa, inc_t csa,
       float*  b, inc_t rsb, inc_t csb,
       float*  beta,
       float*  c, inc_t rsc, inc_t csc,
       blis_cntx_t* cntx
    )

    void bli_dger(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       dim_t   n,
       double*  alpha,
       double*  x, inc_t incx,
       double*  y, inc_t incy,
       double*  a, inc_t rsa, inc_t csa,
       blis_cntx_t* cntx
    )

    void bli_sger(
       blis_conj_t  conjx,
       blis_conj_t  conjy,
       dim_t   m,
       dim_t   n,
       float*  alpha,
       float*  x, inc_t incx,
       float*  y, inc_t incy,
       float*  a, inc_t rsa, inc_t csa,
       blis_cntx_t* cntx
    )

    void bli_dgemv(
       blis_trans_t transa,
       blis_conj_t  conjx,
       dim_t   m,
       dim_t   n,
       double*  alpha,
       double*  a, inc_t rsa, inc_t csa,
       double*  x, inc_t incx,
       double*  beta,
       double*  y, inc_t incy,
       blis_cntx_t* cntx
     )

    void bli_sgemv(
       blis_trans_t transa,
       blis_conj_t  conjx,
       dim_t   m,
       dim_t   n,
       float*  alpha,
       float*  a, inc_t rsa, inc_t csa,
       float*  x, inc_t incx,
       float*  beta,
       float*  y, inc_t incy,
       blis_cntx_t* cntx
     )

    void bli_daxpyv(
       blis_conj_t  conjx,
       dim_t   m,
       double*  alpha,
       double*  x, inc_t incx,
       double*  y, inc_t incy,
       blis_cntx_t* cntx
     )
    
    void bli_saxpyv(
       blis_conj_t  conjx,
       dim_t   m,
       float*  alpha,
       float*  x, inc_t incx,
       float*  y, inc_t incy,
       blis_cntx_t* cntx
     )

    void bli_dscalv(
       blis_conj_t  conjalpha,
       dim_t   m,
       double*  alpha,
       double*  x, inc_t incx,
       blis_cntx_t* cntx
    )

    void bli_sscalv(
       blis_conj_t  conjalpha,
       dim_t   m,
       float*  alpha,
       float*  x, inc_t incx,
       blis_cntx_t* cntx
    )


bli_init()


# BLAS level 3 routines
cdef void gemm(
    trans_t trans_a,
    trans_t trans_b,
    dim_t   m,
    dim_t   n,
    dim_t   k,
    real_ft  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  b, inc_t rsb, inc_t csb,
    real_ft  beta,
    reals_ft  c, inc_t rsc, inc_t csc,
    void* cntx=NULL
) nogil:
    cdef float alpha_f = alpha
    cdef float beta_f = beta
    cdef double alpha_d = alpha
    cdef double beta_d = beta
    if reals_ft is floats_t:
        bli_sgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_f, a, rsa, csa, b, rsb, csb, &beta_f, c, rsc, csc, <blis_cntx_t*>cntx)
    elif reals_ft is doubles_t:
        bli_dgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_d, a, rsa, csa, b, rsb, csb, &beta_d, c, rsc, csc, <blis_cntx_t*>cntx)
    elif reals_ft is float1d_t:
        bli_sgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_f, &a[0], rsa, csa, &b[0], rsb, csb, &beta_f, &c[0],
            rsc, csc, <blis_cntx_t*>cntx)
    elif reals_ft is double1d_t:
        bli_dgemm(
            <blis_trans_t>trans_a, <blis_trans_t>trans_b,
            m, n, k,
            &alpha_d, &a[0], rsa, csa, &b[0], rsb, csb, &beta_d, &c[0],
            rsc, csc, <blis_cntx_t*>cntx)
    else:
        # Impossible --- panic?
        pass


cdef void ger(
    conj_t  conjx,
    conj_t  conjy,
    dim_t   m,
    dim_t   n,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy,
    reals_ft  a, inc_t rsa, inc_t csa,
    void* cntx=NULL
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_sger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_f,
            x, incx, y, incy, a, rsa, csa,
            <blis_cntx_t*>cntx)
    elif reals_ft is doubles_t:
        bli_dger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_d,
            x, incx, y, incy, a, rsa, csa, <blis_cntx_t*>cntx)
    elif reals_ft is float1d_t:
        bli_sger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_f,
            &x[0], incx, &y[0], incy, &a[0], rsa, csa, <blis_cntx_t*>cntx)

    elif reals_ft is double1d_t:
        bli_dger(
            <blis_conj_t>conjx, <blis_conj_t>conjy,
            m, n,
            &alpha_d,
            &x[0], incx, &y[0], incy, &a[0], rsa, csa, <blis_cntx_t*>cntx)
    else:
        # Impossible --- panic?
        pass


cdef void gemv(
    trans_t transa,
    conj_t  conjx,
    dim_t   m,
    dim_t   n,
    real_ft  alpha,
    reals_ft  a, inc_t rsa, inc_t csa,
    reals_ft  x, inc_t incx,
    real_ft  beta,
    reals_ft  y, inc_t incy,
    void* cntx=NULL
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    cdef float beta_f = alpha
    cdef double beta_d = alpha
    if reals_ft is floats_t:
        bli_sgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_f, a, rsa, csa,
            x, incx, &beta_f,
            y, incy, <blis_cntx_t*>cntx)
    elif reals_ft is doubles_t:
        bli_dgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_d, a, rsa, csa,
            x, incx, &beta_d,
            y, incy, <blis_cntx_t*>cntx)
    elif reals_ft is float1d_t:
        bli_sgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_f, &a[0], rsa, csa,
            &x[0], incx, &beta_f,
            &y[0], incy, <blis_cntx_t*>cntx)
    elif reals_ft is double1d_t:
        bli_dgemv(
            <blis_trans_t>transa, <blis_conj_t>conjx,
            m, n,
            &alpha_d, &a[0], rsa, csa,
            &x[0], incx, &beta_d,
            &y[0], incy, <blis_cntx_t*>cntx)
    else:
        # Impossible --- panic?
        pass


cdef void axpyv(
    conj_t  conjx,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    reals_ft  y, inc_t incy,
    void* cntx=NULL
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_saxpyv(<blis_conj_t>conjx, m,  &alpha_f, x, incx, y, incy,
                   <blis_cntx_t*>cntx)
    elif reals_ft is doubles_t:
        bli_daxpyv(<blis_conj_t>conjx, m,  &alpha_d, x, incx, y, incy,
                   <blis_cntx_t*>cntx)
    elif reals_ft is float1d_t:
        bli_saxpyv(<blis_conj_t>conjx, m,  &alpha_f, &x[0], incx, &y[0], incy,
                   <blis_cntx_t*>cntx)
    elif reals_ft is double1d_t:
        bli_daxpyv(<blis_conj_t>conjx, m,  &alpha_d, &x[0], incx, &y[0], incy,
                   <blis_cntx_t*>cntx)
    else:
        # Impossible --- panic?
        pass


cdef void scalv(
    conj_t  conjalpha,
    dim_t   m,
    real_ft  alpha,
    reals_ft  x, inc_t incx,
    void* cntx=NULL
) nogil:
    cdef float alpha_f = alpha
    cdef double alpha_d = alpha
    if reals_ft is floats_t:
        bli_sscalv(<blis_conj_t>conjalpha, m, &alpha_f, x, incx, <blis_cntx_t*>cntx)
    elif reals_ft is doubles_t:
        bli_dscalv(<blis_conj_t>conjalpha, m, &alpha_d, x, incx, <blis_cntx_t*>cntx)
    elif reals_ft is float1d_t:
        bli_sscalv(<blis_conj_t>conjalpha, m, &alpha_f, &x[0], incx, <blis_cntx_t*>cntx)
    elif reals_ft is double1d_t:
        bli_dscalv(<blis_conj_t>conjalpha, m, &alpha_d, &x[0], incx, <blis_cntx_t*>cntx)
    else:
        # Impossible --- panic?
        pass


def gemm_(
    trans_t trans_a,
    trans_t trans_b,
    dim_t   m,
    dim_t   n,
    dim_t   k,
    double  alpha,
    reals1d_ft  a, inc_t rsa, inc_t csa,
    reals1d_ft  b, inc_t rsb, inc_t csb,
    double  beta,
    reals1d_ft  c, inc_t rsc, inc_t csc
):
    gemm(trans_a, trans_b, m, n, k, alpha, a, rsa, csa, b, rsb, csb, beta, c,
         rsc, csc)
