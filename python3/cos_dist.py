import math
from urllib.parse import urlparse, urlunparse
import re


def cos_dist(a, b):
    a = re.split(r'&|=|/|"|\'|%2f|%2F|\.', urlparse(a).query) + re.split(r"/", urlparse(a).path)[1:]
    b = re.split(r'&|=|/|"|\'|%2f|%2F|\.', urlparse(b).query) + re.split(r"/", urlparse(b).path)[1:]
    z = list(set(a + b))
    a_dict = {}
    for i in a:
        if i not in a_dict.keys():
            a_dict[i] = 0
        a_dict[i] += 1

    for i in z:
        if i not in a_dict.keys():
            a_dict[i] = 0
    a = [a_dict.get(key) for key in sorted(a_dict.keys())]

    b_dict = {}
    for i in b:
        if i not in b_dict.keys():
            b_dict[i] = 0
        b_dict[i] += 1

    for i in z:
        if i not in b_dict.keys():
            b_dict[i] = 0
    b = [b_dict.get(key) for key in sorted(b_dict.keys())]

    part_up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(a, b):
        part_up += a1 * b1
        a_sq += a1 ** 2
        b_sq += b1 ** 2
    part_down = math.sqrt(a_sq * b_sq)
    if part_down == 0.0:
        return 0.0
    else:
        return part_up / part_down

