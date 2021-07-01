import argparse

from utils.lz77 import LZ77

def get_args():
    parser = argparse.ArgumentParser('Data-Compression - Vlad15lav')
    parser.add_argument('-f', '--file', type=str, help='path file')
    parser.add_argument('-s', '--save', type=str, help='path save file')
    parser.add_argument('--type', type=str, default='LZ77', help='name data compression algorithm')
    parser.add_argument('--compress', help='compression mode', action="store_true")
    parser.add_argument('--max_length', type=int, default=255, help='max length pattern')
    parser.add_argument('--max_offset', type=int, default=15, help='max offset in buffer')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    opt = get_args()
    tool = LZ77(max_length=opt.max_length, max_offset=opt.max_offset)

    type_mode = tool.encode if opt.compress else tool.decode
    type_mode(opt.file, opt.save)
    