import os


def split_list(a_list, count=None):
    """
    Делим список пополам
    :param a_list: список
    :return:
    """
    if not count:
        count = os.cpu_count()

    if len(a_list) < count*10:
        count = 1

    splitted_list = []
    half = len(a_list) // count

    for i in range(count-1):
        splitted_list.append((a_list[i*half:half+i*half], i))

    splitted_list.append((a_list[half+(count-2)*half:], count-1))

    return splitted_list
