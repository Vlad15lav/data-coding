import numpy as np

from bitarray import bitarray

# number of combinations (n >= k)
def C(n: int, k: int):
    if k == n or k == 0:
        return 1
    if k != 1:
        return C(n-1, k) + C(n-1, k-1)
    else:
        return n

# http://dha.spb.ru/PDF/ReedMullerExamples.pdf
# https://scask.ru/h_book_codb.php?id=30

class ReedMuller:
    def __init__(self, m: int, sigma: int=1):
        self.m = m # indicator length
        self.sigma = sigma # order
        self.n = 2 ** m # code length
        self.d = 2 ** (m - sigma) # minimum code length
        self.k_i = [C(m, l) for l in range(sigma + 1)]
        self.k = sum(self.k_i) # number of order
        self.R = (self.n - self.k) / self.n # redundancy
        
        self.G = self.__get_matrix() # G matrix
    
    def __get_vector(self, m: int, i: int):
        return ([0] * (2 ** (m - i - 1)) + [1] * (2 ** (m - i - 1))) * (2 ** i)
        #return ([1] * (2 ** (m - i - 1)) + [0] * (2 ** (m - i - 1))) * (2 ** i)

    def __get_matrix(self):
        g_matrix = np.ones((1, self.n), dtype=np.int)
        #g_matrix = np.concatenate((g_matrix, [self.__get_vector(self.m, i) for i in range(self.m - 1, -1, -1)]))
        g_matrix = np.concatenate((g_matrix, [self.__get_vector(self.m, i) for i in range(self.m)]))
        for k in range(2, self.sigma + 1):
            shift = g_matrix.shape[0] - C(self.m, k - 1)
            for indexes in list(itertools.combinations(range(self.m), k)):
                temp = np.copy(g_matrix[shift + indexes[0]])

                for idx in indexes[1:]:
                    temp *= g_matrix[shift + idx]
                g_matrix = np.concatenate((g_matrix, [temp]))
        
        self.start_order = [0]
        for i in range(1, self.sigma + 1):
            self.start_order.append(self.start_order[i - 1] + self.k_i[i])
        
        return g_matrix

    def encode(self, message: str):
        #message = open(path_file, "r")

        a = bitarray()
        a.frombytes(message.encode('utf-8'))

        # add bits
        length_tail = self.k - (len(a) % self.k)
        a.extend('0' * length_tail)
        a.extend(bin(length_tail)[2:].zfill(self.k))
        
        # (v{1} || v{2} || .. || v{len(v)/k}) @ G
        result = bitarray()
        for i in range(len(a) // self.k):
            data = a[self.k * i:self.k * (i + 1)]
            out = ''.join(map(str, list(np.array(list(data.to01()), \
                   dtype=np.int) @ self.G % 2)))
            result.extend(out)

        del a
        return result
    
    def decode(self, message):
        pass
        # for i in range(len(message) / self.k):
        #     data = message[self.k * i:self.k * (i + 1)]
        #     for order in range(self.sigma, -1, -1):
        #         top = self.start_order[order]
        #         bottom = 0 if order == 0 else self.start_order[order - 1] + 1
        #         for j in range(top, bottom + 1):
