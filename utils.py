import time
import os
import logging


logging.getLogger().setLevel(logging.INFO)


def check_thunder_start(src_path, filename, patience=500):
    """
    :param src_path: default thunder download destination.
    :param filename: the file name that thunder saves as.
    :param patience: maximally patience/20 seconds to wait.
    :return:
    """
    cache_file = filename + ".xltd"
    for i in range(patience):
        flag = os.path.exists(os.path.join(src_path, cache_file)) or \
               os.path.exists(os.path.join(src_path, filename))
        if flag:
            return
        else:
            time.sleep(0.05)
    raise TimeoutError


def check_thunder_finish(src_path, ps, patience=500):
    """
    :param src_path: default thunder download destination.
    :param ps: number of pictures in current album.
    :param patience: maximally patience/20 seconds to wait.
    :return:
    """
    for i in range(patience):
        file_num = len(os.listdir(src_path))
        if file_num != int(ps):
            time.sleep(0.05)
        else:
            return
    raise TimeoutError


def check_integrity(dst, ps):
    """
    :param dst: download destination.
    :param ps: number of pictures in current album.
    :return:
    """
    file_num = len(os.listdir(dst))
    flag = (file_num == int(ps))
    return flag


def check_rename(src_path, dst_path, patience=200):
    """
    :param src_path: default thunder download destination.
    :param dst_path: output son folder path.
    :param patience: maximally patience/10 seconds to wait.
    :return:
    """
    for i in range(patience):
        try:
            os.rename(src_path, dst_path)
        except PermissionError:
            time.sleep(0.05)
        else:
            return
    raise TimeoutError


def exclusive_path(output_folder, name, ps, tolerance=100):
    """
    :param output_folder: output father folder path.
    :param name: model name of current album.
    :param ps: number of pictures in current album.
    :param tolerance: how many folders with the same name can be tolerated.
    :return:
    """
    dst_path = os.path.join(output_folder, '{}P').format(name + ps)
    for i in range(tolerance):
        if not os.path.exists(dst_path):
            break
        else:
            new_dst_path = dst_path + '-{}'.format(i + 1)
            if not os.path.exists(new_dst_path):
                dst_path = new_dst_path
                break
            else:
                continue
    return dst_path


def title_path(output_folder, ps, title):
    dst_path = os.path.join(output_folder, '{} - {}P').format(title, ps)
    duplicate = os.path.exists(dst_path)
    if duplicate is True:
        return dst_path, 1
    return dst_path, 0
