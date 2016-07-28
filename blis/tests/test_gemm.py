from __future__ import division
from hypothesis import given, assume
from math import sqrt, floor

from .common import *
from .. import gemm
from ..blis import NO_TRANSPOSE, TRANSPOSE

def _stretch_matrix(data, m, n):
    orig_len = len(data)
    orig_m = m
    orig_n = n
    ratio = sqrt(len(data) / (m * n))
    m = int(floor(m * ratio))
    n = int(floor(n * ratio))
    data = np.ascontiguousarray(data[:m*n], dtype=data.dtype)
    return data.reshape((m, n)), m, n

def _reshape_for_gemm(A, B, a_rows, a_cols, out_cols, dtype):
    A, a_rows, a_cols = _stretch_matrix(A, a_rows, a_cols)
    if len(B) < a_cols or a_cols < 1:
        return (None, None, None)
    b_cols = int(floor(len(B) / a_cols))
    B = np.ascontiguousarray(B.flatten()[:a_cols*b_cols], dtype=dtype)
    B = B.reshape((a_cols, b_cols))
    out_cols = B.shape[1]
    C = np.zeros(shape=(A.shape[0] * B.shape[1],), dtype=dtype)
    return A, B, C


@given(
    ndarrays(min_len=10, max_len=100,
             min_val=-100.0, max_val=100.0, dtype='float64'),
    ndarrays(min_len=10, max_len=100,
             min_val=-100.0, max_val=100.0, dtype='float64'),
    integers(min_value=2, max_value=1000),
    integers(min_value=2, max_value=1000),
    integers(min_value=2, max_value=1000))
def test_memoryview_double_notrans(A, B, a_rows, a_cols, out_cols):
    A, B, C = _reshape_for_gemm(A, B, a_rows, a_cols, out_cols, 'float64')
    assume(A is not None)
    assume(B is not None)
    assume(C is not None)
    gemm(0, 0,
        A.shape[0], B.shape[1], A.shape[1],
        1.0,
        np.ascontiguousarray(A.flatten(), dtype='float64'), A.shape[1], 1,
        np.ascontiguousarray(B.flatten(), dtype='float64'), B.shape[1], 1,
        1.0,
        C, B.shape[1], 1)
    my_result = C.reshape((A.shape[0], B.shape[1]))

    numpy_result = A.dot(B)
    assert_allclose(numpy_result, my_result, atol=1e-5, rtol=1e-5)


@given(
    ndarrays(min_len=10, max_len=100,
             min_val=-100.0, max_val=100.0, dtype='float32'),
    ndarrays(min_len=10, max_len=100,
             min_val=-100.0, max_val=100.0, dtype='float32'),
    integers(min_value=2, max_value=1000),
    integers(min_value=2, max_value=1000),
    integers(min_value=2, max_value=1000))
def test_memoryview_float_notrans(A, B, a_rows, a_cols, out_cols):
    A, B, C = _reshape_for_gemm(A, B, a_rows, a_cols, out_cols, dtype='float32')
    assume(A is not None)
    assume(B is not None)
    assume(C is not None)
    gemm(0, 0,
        A.shape[0], B.shape[1], A.shape[1],
        1.0,
        np.ascontiguousarray(A.flatten(), dtype='float32'), A.shape[1], 1,
        np.ascontiguousarray(B.flatten(), dtype='float32'), B.shape[1], 1,
        1.0,
        C, B.shape[1], 1)
    my_result = C.reshape((A.shape[0], B.shape[1]))

    numpy_result = A.dot(B)
    assert_allclose(numpy_result, my_result, atol=1e-5, rtol=1e-5)
