import argparse
import json
import sys
import Colorer
from infos import get_all_info
from downloader import parallel_download_with_wget, download_with_thunder, download_with_wget

parser = argparse.ArgumentParser(description='Argument Parser for main function.')
parser.add_argument('--downloader', default='wget', choices=['wget', 'thunder'])
parser.add_argument('--multiprocess', action='store_false')
parser.add_argument('-w', '--write_info', action='store_true')
parser.add_argument('-i', '--show_info', action='store_true')

parser.add_argument('-f', '--folder_mode', default='title', choices=['model', 'title'])
parser.add_argument('-n', '--num_plus_model', action='store_true')
parser.add_argument('-s', '--start_page', default=1, type=int, help='this number included.')
parser.add_argument('-e', '--end_page', default=1, type=int, help='this number included.')
parser.add_argument('-r', '--resume_number', default=1, type=int, help='resume from this No. of album in info list.')
parser.add_argument('-t', '--terminate_number', default=1000, type=int, help='Terminate at this No. of album in info list, inclusive.')
args = parser.parse_args()


def main(root_html, output_folder=r'F:\Photo\test', thunder_base=r'C:\Users\qq787\Downloads'):
    info = get_all_info(root_html, args.start_page, args.end_page, mode=args.folder_mode, num_plus_model=args.num_plus_model)
    if args.write_info:
        with open(f'F:\Photo\info\{root_html}.txt', 'w') as f:
            json.dump(info, f)
    if args.show_info:
        print(info)
        sys.exit(0)
    if args.multiprocess:
        parallel_download_with_wget(info, output_folder, args.folder_mode, args.resume_number, args.terminate_number)
    else:  # deprecated.
        if args.downloader == 'thunder':
            download_with_thunder(info, thunder_base, output_folder, args.resume_number)
        elif args.downloader == 'wget':
            download_with_wget(info, output_folder, args.resume_number)
        else:
            raise ValueError


if __name__ == '__main__':
    output_folder = r'F:\Photo\test'
    root_html = 'https://www.tujigu.net/x/57/'
    main(root_html, r'F:\Photo\test')

