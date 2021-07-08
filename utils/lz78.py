import math

from bitarray import bitarray

class LZ78:
    def compress(self, path_file: str, path_save: str):        
        message = open(path_file, "rb")
        file = open(path_save, "wb")

        history = dict()
        out = bitarray(endian='big')

        last_idx, next_idx, bit_numeric, last_byte = 0, 1, 1, True

        while message:
            number_size = math.ceil(math.log(bit_numeric, 2))
            byte = message.read(1)

            if not byte:
                if last_idx != 0:
                    last_byte = False

                    num = bin(last_idx)[2:].zfill(number_size)
                    out.extend(num)
                    out.frombytes(b'\x00')
                break

            if (last_idx, byte) in history:
                last_idx = history[(last_idx, byte)]
            else:
                history[(last_idx, byte)] = next_idx

                num = bin(last_idx)[2:].zfill(number_size)
                out.extend(num)
                out.frombytes(byte)
                
                last_idx = 0
                next_idx += 1
                bit_numeric += 1

        out.tofile(file)
        file.close()

    def decompress(self, path_file: str, path_save: str):
        pass