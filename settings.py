#!/usr/bin/env python3

import sys
import os
from decimal import Decimal as D
from datetime import *
import time
import re



def crDateToPosix(dateString, mask):
    try:
        timeObject=time.strptime(dateString, mask)
        dateValue=time.mktime(timeObject) #expressed in UTC
        posixValue=str(int(dateValue))+'000'
    except ValueError:
        posixValue='0'
    return posixValue


def udaEntry(sequence,name,value,type):
    #print sequence, name, value, type
    if type=="cgdate" and value=="0":
        return
    elif value is not None and value != '':
        # Add code to escape xml reserved chars
        value = value.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;").replace("'", "&apos;").replace("\"","&quot;");
        return sequence.append('<entry><string>' + name + '</string><' + type +'>' + value + '</' + type + '></entry>')
    else:
        return


def isaNumberCheck(value):
    try:
        bvalue = int(value)
    except ValueError:
        bvalue = None

    return bvalue


# Expected format is MMDDYYY
def validateCheckDate(value):
    try:
        bvalue = int(value)
        datelen = len(value)
        if datelen == 8:
            chkYear = int(value[4:])
            # Posix starts 01 01 1970
            # Seems to end 12 31 3000; 2.6py
            if chkYear < 1970 or chkYear > 3000:  # Posix starts 1 1 1970
                bvalue = 0  # out of range
        else:
            bvalue = 0  # length
    except ValueError:
        bvalue = None

    return bvalue


def updateOline(field, value, end=None):
    existingValue = getattr(oline, field)
    updateValue = str(fdict.get(value, value)).strip()[0:end]
    existingValue[1] = updateValue
    return


class Base(object):
    def __init__(self,seq=[]):
        orderSequence = [[value, [order, '']] for order, value in enumerate(seq)]
        self.__dict__=dict(orderSequence)

    def exists(self,key):
        v=self.__dict__.get(key,False)
        return v
    def buildList (self):
        x = self.__dict__.values()
        x.sort()
        outLine='|'.join([str(i[1]) for i in x])+'\n'
        return outLine

def extracting_records(text, rec_indicies={}, rec_stores={}):
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

    return rec_stores

ISO_CURRENCY_MAPPING = {
        '784':'AED;United Arab Emirates',
        '051':'AMD;Armenia',
        '032':'ARS;Argentina',
        '036':'AUD;Australia',
        '944':'AZN;Azerbaijan',
        '977':'BAM;Bosnia and Herzegovina',
        '052':'BBD;Barbados',
        '975':'BGN;Bulgaria',
        '048':'BHD;Bahrain',
        '096':'BND;Brunei',
        '068':'BOB;Bolivia',
        '986':'BRL;Brazil',
        '044':'BSD;Bahamas',
        '072':'BWP;Botswana',
        '084':'BZD;Belize',
        '124':'CAD;Canada',
        '756':'CHF;Switzerland',
        '152':'CLP;Chile',
        '156':'CNY;China',
        '170':'COP;Colombia',
        '188':'CRC;Costa Rica',
        '203':'CZK;Czech Republic',
        '208':'DKK;Denmark',
        '214':'DOP;Dominican Republic',
        '818':'EGP;Egypt',
        '978':'EUR;European Monetary Union',
        '826':'GBP;United Kingdom',
        '936':'GHS;Ghana',
        '320':'GTQ;Guatemala',
        '344':'HKD;Hong Kong',
        '340':'HNL;Honduras',
        '191':'HRK;Croatia',
        '348':'HUF;Hungary',
        '360':'IDR;Indonesia',
        '376':'ILS;Israel',
        '356':'INR;India',
        '352':'ISK;Iceland',
        '388':'JMD;Jamaica',
        '400':'JOD;Jordan',
        '392':'JPY;Japan',
        '404':'KES;Kenya',
        '410':'KRW;South Korea',
        '414':'KWD;Kuwait',
        '136':'KYD;Cayman Islands',
        '398':'KZT;Kazakhstan',
        '422':'LBP;Lebanon',
        '144':'LKR;Sri Lanka',
        '807':'MKD;Macedonia',
        '496':'MNT;Mongolia',
        '446':'MOP;Macau',
        '480':'MUR;Mauritius',
        '462':'MVR;Maldives',
        '454':'MWK;Malawi',
        '484':'MXN;Mexico',
        '458':'MYR;Malaysia',
        '943':'MZN;Mozambique',
        '516':'NAD;Namibia',
        '566':'NGN;Nigeria',
        '558':'NIO;Nicaragua',
        '578':'NOK;Norway',
        '554':'NZD;New Zealand',
        '512':'OMR;Oman',
        '604':'PEN;Peru',
        '598':'PGK;Papua New Guinea',
        '608':'PHP;Philippines',
        '586':'PKR;Pakistan',
        '985':'PLN;Poland',
        '600':'PYG;Paraguay',
        '634':'QAR;Qatar',
        '946':'RON;Romania',
        '941':'RSD;Serbia',
        '643':'RUB;Russia',
        '682':'SAR;Saudi Arabia',
        '752':'SEK;Sweden',
        '702':'SGD;Singapore',
        '764':'THB;Thailand',
        '788':'TND;Tunisia',
        '949':'TRY;Turkey',
        '780':'TTD;Trinidad and Tobago',
        '901':'TWD;Taiwan',
        '834':'TZS;Tanzania',
        '980':'UAH;Ukraine',
        '800':'UGX;Uganda',
        '840':'USD;US',
        '858':'UYU;Uruguay',
        '704':'VND;Vietnam',
        '548':'VUV;Vanuatu',
        '950':'XAF;Communaute Financiere Africaine',
        '951':'XCD;East Caribbean',
        '952':'XOF;Communaute Financiere Africaine',
        '953':'XPF;Comptoirs Francais du Pacifique',
        '710':'ZAR;South Africa',
        '967':'ZMW;Zambia'
    }

AIR_CLASS_DICT = {
        'C':'100',
        'B':'101', # Business
        'F':'102', # First Class
        'V':'100',
        'Q':'100',
        'O':'100',
        'Y':'100',
        'W':'100',
        'S':'100',
        'P':'102', # First Class
        'M':'100',
        'J':'101', # Business
        'H':'100',
        'K':'100',
        'L':'100',
        'U':'100',
        'T':'100',
        'E':'100'
}

RENTAL_DICT = {
        'Hertz': 'ZE',
        'Avis': 'ZI',
        'Enterprise': 'ET',
        'Budget': 'ZD',
        'Ace': 'AC',
        'Advantage': 'AD',
        'Alamo': 'AL',
        'Europcar': 'EP',
        'Sixt': 'SX',
        'National': 'ZL',
        'Dollar': 'ZR',
        'Thrifty': 'ZT'
        #'Other'  :'OO' # Verify the Other Entity Code with PM
}

# rec types
REC_TYPES = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '14', '15', '16', '17', '18', '20', '21',
             '25', '26', '27', '28', '29', '30', '31', '99']

# rec indicies
REC_INDICIES = {rec: [0, 0] for rec in REC_TYPES}

# rec stores
# REC_STORES = {rec: None for rec in REC_TYPES}
