import argparse
import os
import math
import pickle

from bitarray import bitarray

def get_args():
	parser = argparse.ArgumentParser('LZW - Vladislav')
	parser.add_argument('-f', '--file', type=str, help='path file')
	parser.add_argument('-c', '--cache', type=str, default='cache.pkl', help='path cache')
	parser.add_argument('-d', action="store_true", help='decompress')

	args = parser.parse_args()
	return args

class LZW:
	def __init__(self):
		self.cache_alpha = None

	def compress(self, path_file: str):
		try:
			with open(path_file) as f:
				message = f.read()
		except:
			with open(path_file, encoding="utf-8") as f:
				message = f.read()
		file = open(os.path.splitext(path_file)[0] + '.lzw', "wb")
		out = bitarray(endian='big')

		alphabet = set(message)
		history = dict(zip(alphabet, range(1, len(alphabet) + 1)))
		self.cache_alpha = history.copy()

		new_index = len(history) + 1
		phase = new_index
		P, result = '', ''

		for c in message:
			num_bits = math.ceil(math.log(phase, 2))

			isExcept = True
			try:
				history[P + c]
			except KeyError:
				isExcept = False
			
			if isExcept:
				P += c
			else:
				out.extend(bin(history[P])[2:].zfill(num_bits))
				phase += 1
				
				history[P + c] = new_index
				new_index += 1

				P = c

		out.extend(bin(history[P])[2:].zfill(num_bits))
		out.tofile(file)
		file.close()

	def save_cache(self, path_cache: str='cache.pkl'):
		with open(path_cache, 'wb') as handle:
			pickle.dump(self.cache_alpha, handle, protocol=pickle.HIGHEST_PROTOCOL)

	def load_cache(self, path_cache: str='cache.pkl'):
		with open(path_cache, 'rb') as handle:
			self.cache_alpha = pickle.load(handle)
	
	def decompress(self, path_file: str):
		data = bitarray(endian='big')
		with open(path_file, 'rb') as f:
			data.fromfile(f)
		
		if self.cache_alpha:
			history = {value:key for key, value in self.cache_alpha.items()}
		else:
			raise ValueError("Don't have dictonary for alphabet!")
		
		new_index = len(history) + 1
		phase = new_index
		num_bits = math.ceil(math.log(phase, 2))

		cW = int(data[:num_bits].to01(), 2)
		str_cW = history[cW]
		result = str_cW

		pos = num_bits
		phase += 1
		num_bits = math.ceil(math.log(phase, 2))

		while sum(data[pos:pos + num_bits]):
			cW = int(data[pos:pos + num_bits].to01(), 2)
			
			pos += num_bits
			phase += 1
			num_bits = math.ceil(math.log(phase, 2))
			
			isExcept = True
			try:
				history[cW]
			except KeyError:
				isExcept = False
			
			if isExcept:
				P = str_cW
				str_cW = history[cW]

				history[new_index] = P + str_cW[0]
				new_index += 1
			else:
				history[new_index] = str_cW + str_cW[0]
				new_index += 1
				str_cW = history[cW]
			
			result += str_cW
		
		try:
			output_stream = open(os.path.splitext(path_file)[0] + '_d.txt', "w")
			output_stream.write(result)
		except:
			output_stream.close()
			output_stream = open(os.path.splitext(path_file)[0] + '_d.txt', "w", encoding="utf-8")
			output_stream.write(result)
		output_stream.close()

def main():
	opt = get_args()

	tool = LZW()

	if not opt.d:
		tool.compress(path_file=opt.file)
		tool.save_cache(path_cache=opt.cache)
	else:
		tool.load_cache(path_cache=opt.cache)
		tool.decompress(path_file=opt.file)

if __name__ == '__main__':
	main()