import math

from bitarray import bitarray

class LZ78:
    def compress(self, path_file: str, path_save: str):        
        message = open(path_file, "rb")
        file = open(path_save, "wb")

        history = dict()
        out = bitarray(endian='big')

        last_idx, next_idx, bit_numeric, is_end_mark = 0, 1, 1, True

        while message:
            number_size = math.ceil(math.log(bit_numeric, 2))
            byte = message.read(1)

            if not byte:
                if last_idx != 0:
                    is_end_mark = False

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
        
        out.append(is_end_mark)
        out.tofile(file)
        file.close()

    def decompress(self, path_file: str, path_save: str):
        output_stream = open(path_save, "wb")

        data = bitarray(endian='big')
        with open(path_file,'rb') as f:
            data.fromfile(f)

        history = dict()
        bit_numeric, number_size, is_end_mark = 1, 1, data[-1]
        del data[-1]

        pos = 0
        iteration = 1

        while pos + number_size + 8 < len(data):
            current_idx = data[pos:pos + number_size].to01()
            current_idx = int(current_idx, 2)

            pos += number_size

            byte = data[pos:pos+8].tobytes()
            
            pos += 8
            bit_numeric += 1
            number_size = math.ceil(math.log(bit_numeric, 2))

            if current_idx != 0:
                history_byte = history[current_idx]

                if pos + 8 >= len(data) and not is_end_mark:
                    byte = history_byte
                else:
                    byte = history_byte + byte

            history[iteration] = byte
            output_stream.write(byte)
            iteration += 1
        
        output_stream.close()
