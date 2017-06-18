import numpy as np

np.random.seed(1234)

d = 64
nb = 100000
nq = 10000
xb = np.random.random((nb, d)).astype('float32')
xb[:, 0] += np.arange(nb) / 1000.

ids = (np.random.random(xb.shape[0]) * nb).astype('int')
print ids

