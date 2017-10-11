import numpy
import numpy.random
from blis.blis import gemm_
from blis.blis import init
from timeit import default_timer as timer
numpy.random.seed(0)
init()

def create_data(nO, nI, batch_size):
    X = numpy.zeros((batch_size, nI), dtype='f')
    X += numpy.random.uniform(-1., 1., X.shape)
    W = numpy.zeros((nO, nI), dtype='f')
    W += numpy.random.uniform(-1., 1., W.shape)
    return X, W


def run_numpy(X, W):
    nO, nI = W.shape
    batch_size = X.shape[0]
    total = 0.
    for i in range(1000):
        y = numpy.dot(X, W)
        total += y.sum()
    print(total)


def run_blis(X, W):
    nO, nI = W.shape
    batch_size = X.shape[0]
    total = 0.
    y = numpy.zeros((batch_size, nO), dtype='f')
    for i in range(1000):
        # Output dim: batch_size * nr_row
        # vec dim:    batch_size * nr_col
        # mat dim:    nr_row     * nr_col
        # vec:   M * K
        # mat.T: K * N
        # out: M * N
        gemm_(0, 0, batch_size, nO, nI,
              1.0,
              X, X.shape[1], 1,
              W, W.shape[1], 1,
              1.0,
              y, y.shape[1], 1)
        total += y.sum()
        y.fill(0.)
    print(total)

def main(nI=128*3, nO=128*3, batch_size=2000):
    print("Setting up data "
          "nO={nO} nI={nI} batch_size={batch_size}".format(**locals()))
    X1, W1 = create_data(nI, nO, batch_size)
    X2 = X1.copy()
    W2 = W1.copy()
    print("Numpy...")
    start = timer()
    run_numpy(X1, W1)
    end = timer()
    numpy_time = end-start
    print("%.2f seconds" % numpy_time) 
    print("Blis...")
    start = timer()
    run_blis(X2, W2)
    end = timer()
    blis_time = end-start
    print("%.2f seconds" % numpy_time) 


if __name__:
    main()
