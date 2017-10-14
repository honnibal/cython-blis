import numpy
import numpy.random
from .py import gemm
from timeit import default_timer as timer
numpy.random.seed(0)


def create_data(nO, nI, batch_size):
    X = numpy.zeros((batch_size, nI), dtype='f')
    X += numpy.random.uniform(-1., 1., X.shape)
    W = numpy.zeros((nO, nI), dtype='f')
    W += numpy.random.uniform(-1., 1., W.shape)
    return X, W


def get_numpy_blas():
    blas_libs = numpy.__config__.blas_opt_info['libraries']
    return blas_libs[0]


def numpy_gemm(X, W, n=1000):
    nO, nI = W.shape
    batch_size = X.shape[0]
    total = 0.
    y = numpy.zeros((batch_size, nO), dtype='f')
    for i in range(n):
        numpy.dot(X, W, out=y)
        total += y.sum()
        y.fill(0)
    print('Total:', total)


def blis_gemm(X, W, n=1000):
    nO, nI = W.shape
    batch_size = X.shape[0]
    total = 0.
    y = numpy.zeros((batch_size, nO), dtype='f')
    for i in range(n):
        gemm(X, W, out=y)
        total += y.sum()
        y.fill(0.)
    print('Total:', total)


def main(nI=128*3, nO=128*3, batch_size=2000):
    print("Setting up data for gemm "
          "nO={nO} nI={nI} batch_size={batch_size}".format(**locals()))
    numpy_blas = get_numpy_blas()
    X1, W1 = create_data(nI, nO, batch_size)
    X2 = X1.copy()
    W2 = W1.copy()
    print("Blis...")
    start = timer()
    blis_gemm(X2, W2)
    end = timer()
    blis_time = end-start
    print("%.2f seconds" % blis_time) 
    print("Numpy (%s)..." % numpy_blas)
    start = timer()
    numpy_gemm(X1, W1)
    end = timer()
    numpy_time = end-start
    print("%.2f seconds" % numpy_time) 

if __name__:
    main()
