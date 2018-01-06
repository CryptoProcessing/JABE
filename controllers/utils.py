import os


def split_list(a_list, count=None):
    """
    Делим список пополам
    :param a_list: список
    :return:
    """
    if not count:
        count = os.cpu_count()

    if len(a_list) < count*20:
        count = 1

    splitted_list = []
    half = len(a_list) // count

    for i in range(count-1):
        splitted_list.append((a_list[i*half:half+i*half], i*half))

    splitted_list.append((a_list[half+(count-2)*half:], (count-1)*half))

    return splitted_list
