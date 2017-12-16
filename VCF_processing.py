#!/usr/bin/env python3

import sys

from settings import *

rec_indicies = REC_INDICIES
rec_stores = {}

try:
    with open(sys.argv[1]) as f:
        text = f.readlines()
except IndexError:
    text = ''
    print("File not found")

if text:
    for i, line in enumerate(text):
        if line.split('\t')[0] == '8':
            rec_indicies[line.split('\t')[4]][0] = i+1
        elif line.split('\t')[0] == '9':
            rec_indicies[line.split('\t')[4]][1] = i-1
        else:
            continue

    for rec in REC_TYPES:
        if rec_indicies[rec] != [0, 0]:
            rec_stores[rec] = text[rec_indicies[rec][0]: rec_indicies[rec][1]]

    for k in rec_stores:
        print(k, len(rec_stores[k]))
        if k == '04':
            for line in (rec_stores[k]):
                print(len(line.split('\t')), line)