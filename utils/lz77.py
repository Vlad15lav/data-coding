from bitarray import bitarray

class LZ77:
    def __init__(self, max_offset: int=255, max_length: int=15):
        self.max_offset = max_offset
        self.max_length = max_length

    def findBestPattern(self, data: bytes, cur_position: int) -> [int, int]:
        start_pos_buffer = max(0, cur_position - self.max_offset)
        end_pos_window = min(cur_position + self.max_length, len(data) + 1)

        best_offset, best_length = 0, 0
        flag = False
        for j in range(end_pos_window - 1, cur_position - 1, -1):
            cur_pattern = data[cur_position:j+2]
            cur_length_pattern = len(cur_pattern)

            for i in range(start_pos_buffer, cur_position):
                cur_offset_buffer = cur_position - i

                repeat, last = cur_length_pattern // cur_offset_buffer,\
                    cur_length_pattern % cur_offset_buffer
                buffer_pattern = data[i:cur_position] * repeat + data[i:i+last]

                if buffer_pattern == cur_pattern and cur_length_pattern > best_length:
                    best_offset = cur_offset_buffer 
                    best_length = cur_length_pattern
                    flag = True
                    break
            
            if flag: break

        return best_offset, best_length

    def encode(self, path_file: str, path_save: str):        
        with open(path_file, 'rb') as input_file:
            message = input_file.read()

        file = open(path_save, "wb")

        pos, length_str, out = 0, len(message), bitarray(endian='big')
        while pos < length_str:
            cur_offset, cur_length = self.findBestPattern(message, pos)
            pos += cur_length

            if cur_offset:
                out.append(True)
                out.frombytes(bytes([cur_offset]))
                out.frombytes(bytes([cur_length]))
            else:
                out.append(False)

            out.frombytes(bytes([message[pos]]))
            pos += 1
        
        out.fill()
        file.write(out.tobytes())
        file.close()

    def decode(self, path_file: str, path_save: str):
        processed = open(path_save, "wb")

        output_buffer = []
        data = bitarray(endian='big')
        with open(path_file,'rb') as f:
            data.fromfile(f)

        while len(data):
            flag = data.pop(0)
            
            # (0, 0, char)
            if not flag:
                byte = data[0:8].tobytes()
                output_buffer.append(byte)
                del data[0:8]

            # (offset, length, char)
            else:
                offset = ord(data[0:8].tobytes())
                length = ord(data[8:16].tobytes())
                del data[0:16]
                for _ in range(length):
                    output_buffer.append(output_buffer[-offset])

                byte = data[0:8].tobytes()
                output_buffer.append(byte)
                del data[0:8]

        processed.write(b''.join(output_buffer)) 
        processed.close()