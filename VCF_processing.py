#!/usr/bin/env python3

import sys, os

from settings import *

rec_indicies = REC_INDICIES

try:
    with open(sys.argv[1]) as f:
        text = f.readlines()
except IndexError:
    text = ''
    print("File not found")

if not text:
    print("VISA send to us empty file")
    os._exit(250)

rec_stores = extracting_records(text, rec_indicies)

for k in rec_stores:
    print(k, len(rec_stores[k]))