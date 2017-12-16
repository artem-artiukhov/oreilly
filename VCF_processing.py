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
print({k: len(rec_stores[k]) for k in rec_stores.keys()})
current_person = ''

for trans in rec_stores['05']:
    if trans[0] not in ('1', '4'):
        print('Transaction', trans.split('\t')[3], "concerns deleting or removing, we are skipping it")

    # for person in rec_stores['04']:
    #     if trans.split('\t')[1].strip()[-4:] in person.split('\t')[2].strip()[-4:]:
    #         if current_person != person.split('\t')[4].strip() + person.split('\t')[5].strip():
    #             current_person = person.split('\t')[4].strip() + person.split('\t')[5].strip()
    #             print(person.split('\t')[4].strip(), person.split('\t')[5].strip(), 'found in record 04 - cardholder')
    #             print(person.split('\t')[4].strip(), person.split('\t')[5].strip())

    # for car_sum in rec_stores['02']:
    #     if trans.split('\t')[3] in car_sum:
    #         print(trans.split('\t')[8], 'spent: {:.2f}'.format(float(trans.split('\t')[14]) / 100))
    #         # print("transaction", trans.split('\t')[3], 'found in 02 car summary')

    # for car_det in rec_stores['27']:
    #     if trans.split('\t')[3] in car_det:
    #         print("transaction", trans.split('\t')[3], 'found in 27 car detail')

    # for lodg_sum in rec_stores['09']:
    #     if trans.split('\t')[3] in lodg_sum:
    #         print(trans.split('\t')[8], 'spent: {:.2f}'.format(float(trans.split('\t')[14]) / 100))
    #         # print("transaction", trans.split('\t')[3], 'found in 09 lodging summary')
    #         print("stopped at", lodg_sum.split('\t')[30].strip(), 'on', lodg_sum.split('\t')[6], 'during', lodg_sum.split('\t')[23], 'nights')

    # for lodg_det in rec_stores['26']:
    #     if trans.split('\t')[3] in lodg_det:
            # print("transaction", trans.split('\t')[3], 'found in 26 lodging detail')
            # print("he/she had next items", lodg_det.split('\t')[6].lstrip('0') + ':', ', '.join(lodg_det.split('\t')[7:25]))

    # for passenger in rec_stores['14']:
    #     if trans.split('\t')[3] in passenger:
            # print(trans.split('\t')[8], 'spent: {:.2f}'.format(float(trans.split('\t')[14]) / 100))
            # print("transaction", trans.split('\t')[3], 'found in 14 passenger detail')
            # print("Passenger ", passenger.split('\t')[10].strip(), 'flies')
    #
    # for leg in rec_stores['15']:
    #     if trans.split('\t')[3] in leg:
    #         # print("transaction", trans.split('\t')[3], 'found in 15 leg detail')
    #         print("on leg", leg.split('\t')[5].strip(), "from", leg.split('\t')[16], 'to', leg.split('\t')[6].strip(),
    #               'by', leg.split('\t')[7], 'ticked purchased in:', leg.split('\t')[23])

    # for line_item in rec_stores['07']:
    #     if trans.split('\t')[3] in line_item:
    #         print(trans.split('\t')[8], 'spent: {:.2f}'.format(float(trans.split('\t')[14]) / 100))
    #         # print("transaction", trans.split('\t')[3], 'found in 07 line item detail')
    #
    # for sum_item in rec_stores['08']:
    #     if trans.split('\t')[3] in sum_item:
    #         print("transaction", trans.split('\t')[3], 'found in 08 line item summary')
    #
    # for ship_item in rec_stores['21']:
    #     if trans.split('\t')[3] in ship_item:
    #         print("transaction", trans.split('\t')[3], 'found in 21 line item summary')
