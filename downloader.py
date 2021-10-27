from utils import *

import shutil
import threading
import urllib
import urllib.request
import requests
import multiprocessing
import wget
from copy import deepcopy
from stop_thread import stop_thread
from urllib.request import urlopen
from win32com.client import Dispatch


def download_with_thunder(info, src_path, output_folder, start=1, end=10000):
    """
    :param info: [(url1, p1, name1),(url2, p2, name2),...]
    :param src_path: default thunder download destination.
    :param output_folder: output father folder path.
    :param start: starting album number, included.
    :param end: ending album number, not included.
    """
    thunder = Dispatch('ThunderAgent.Agent64.1')
    for num, album in enumerate(info[start - 1:end - 1]):
        num += start
        ps = album[1]
        name = album[2]
        logging.info('Start downloading {}P, the No.{} album out of {}.'.format(name + ps, num, len(info)))
        for p in range(int(album[1])):
            url = album[0].format(p + 1)
            filename = "{}.jpg".format(p + 1)
            thunder.AddTask(url, filename)
            thunder.CommitTasks()
            check_thunder_start(src_path, filename)
        check_thunder_finish(src_path, ps)
        dst_path = exclusive_path(output_folder, name, ps)
        check_rename(src_path, dst_path)
        logging.info('Finish downloading {}P.'.format(name + ps))
    logging.info('All done.')


def download_with_wget(info, output_folder, start=1, end=10000):
    # For each album in info that contains info in all designated pages
    for num, album in enumerate(info[start - 1:end - 1]):
        num += start
        ps = album[1]
        name = album[2]
        # Make exclusive directory for the album.
        dst_path = exclusive_path(output_folder, name, ps)
        dst = os.path.join(output_folder, dst_path)
        os.mkdir(dst)
        logging.info('Start downloading {}P, the No.{} album out of {}.'.format(name + ps, num, len(info)))
        # For all pics in the album.
        # stime = time.time()
        for p in range(int(album[1])):
            # Fill to obtain urls and download with wget.
            # TODO: Download multiple urls in parallel.
            url = album[0].format(p + 1)
            for i in range(10):
                try:
                    wget.download(url, out=dst)
                except urllib.error.ContentTooShortError:
                    continue
                else:
                    break
        logging.info('Finish downloading {}P.'.format(name + ps))
        # etime = time.time()
        # print("download take time: ", etime - stime)
    logging.info('All done.')


def process_queue(crawl_queue, dst):
    for i in range(1):  # how many pics would each thread take response
        try:
            url = crawl_queue.pop()
        except IndexError:
            # crawl queue is empty
            break
        else:
            for j in range(100):
                try:
                    wget.download(url, out=dst)
                    # start = url.rfind('/')
                    # filename = url[start+1:]
                    # urllib.request.urlretrieve(url, os.path.join(dst, filename))
                except urllib.error.ContentTooShortError:
                    print(url)
                    print('ContentTooShort')
                    continue
                except ConnectionResetError:
                    raise AssertionError
                else:
                    break


def parallel_download(crawl_queue, dst, max_threads=8, sleep_time=0.2):
    threads = []
    timeout = 0
    queue = deepcopy(crawl_queue)
    while threads or queue:
        # the crawl is still active
        for thread in threads.copy():
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        while len(threads) < max_threads and queue:
            # can start some more threads
            thread = threading.Thread(target=process_queue, args=(queue, dst))
            thread.setDaemon(True)  # set daemon so main thread can exit when receives ctrl-c
            # thread = multiprocessing.Process(target=process_queue, args=(crawl_queue, dst))
            # thread.daemon = True
            thread.start()
            threads.append(thread)
        # all threads have been processed
        # sleep temporarily so CPU can focus execution on other threads
        time.sleep(sleep_time)
        timeout += 1
        if timeout > 100000:
            raise TimeoutError


def parallel_download_with_wget(info, output_folder, mode='model', start=1, end=10000):
    usage = 0
    duplicate = 0
    # For each album in designated pages
    for num, album in enumerate(info[start - 1:end]):
        num += start
        ps = album[1]
        name = album[2]
        if mode == 'title':
            title = album[-1]
            dst_path, duplicate = title_path(output_folder, ps, title)
            logging.info('Start downloading {}P, the No.{} album out of {}.'.format(title + ' - ' + ps, num, len(info)))
        elif mode == 'model':
            dst_path = exclusive_path(output_folder, name, ps)
            logging.info('Start downloading {}P, the No.{} album out of {}.'.format(name + ps, num, len(info)))
        dst = os.path.join(output_folder, dst_path)
        if duplicate:
            if check_integrity(dst, ps):
                logging.warning('This is a duplicated album, pass.')
                continue
            else:
                logging.warning('Existing folder with incomplete files, remove and download again.')
                shutil.rmtree(dst)
        os.mkdir(dst)
        crawl_queue = []  # deque()
        # Temporarily store all pic urls of the album in crawl_queue.
        for p in range(int(album[1])):
            url = album[0].format(p + 1)
            crawl_queue.append(url)
        stime = time.time()
        try:
            parallel_download(crawl_queue, dst)
        except:
            logging.warning('Due to the exception, remove and download again.')
            for pic in os.listdir(dst):
                os.remove(os.path.join(dst, pic))
            # print('crawl', crawl_queue, 'dst', dst)
            parallel_download(crawl_queue, dst)
        while True:
            final_check = check_integrity(dst, ps)
            if not final_check:
                logging.warning('\nDue to the incompleteness, download again.')
                for pic in os.listdir(dst):
                    os.remove(os.path.join(dst, pic))
                parallel_download(crawl_queue, dst)
            else:
                break
        etime = time.time()
        usage += etime - stime
        int_usage = int(usage)
        print(' ')
        logging.info('Finish downloading {}P. (time usage: {} sec)'.format(name + ps, int_usage))
    logging.info('All done.')
