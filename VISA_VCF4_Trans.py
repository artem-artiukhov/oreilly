#!/usr/bin/python2.6

##expects first argument to be the input file name.  Second argument is an optional output file name.
##If there is no output file, prints to std output.
import sys
import os
from decimal import Decimal as D
from datetime import *
import time
import re

'''
    Developer:
    Rename file as: CustomerCode_VCF4{$1}_Trans.py.
    where {$1} represents feedcode id or country 
    for multiple Visa scripts. See 
    tbl_Feed.FeedCode in SQL DB
    Modify lines 22-26 with their actual card
    setting and remove this section upon MTP

'''
# Customer Name - Customerid - { Bank Name } Visa
# Firm Paid:  Yes/No  {Yes is default}
# Transaction is Deletable: Yes/No  {No is default}
# Transaction Date is Editable: Yes/No  {No is default}
# Transaction Amount is Editable: Yes/No  {No is default}

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
  
def outlist(d, *args):
    '''creates a sequence from dictionary items. If the key is not in the
       dictionary, it adds the key to the sequence.  This is used to create the
       output line.'''
    newlist=[]
    for a in args:
        b=d.get(a,'NotThere')
        if b=='NotThere':
            newlist.append(a)
        else:
            newlist.append(str(d[a]).strip())
    return newlist

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
            if chkYear < 1970 or chkYear > 3000: # Posix starts 1 1 1970
                bvalue = 0  # out of range
        else:
            bvalue = 0 # length         
    except ValueError:
        bvalue = None
        
    return bvalue
    
def main():
    try:
        file=open(sys.argv[1])
    except IOError:
        err='File %s not found' % sys.argv[1]
        sys.stderr.write(err)
        os._exit(250)
    else:
        text=file.readlines()
        file.close()
    
    
    try:
        outfile=open(sys.argv[2],'w')
    except IOError:
        err='Cannot open output file %s' % sys.argv[2]
        sys.stderr.write(err)
        os._exit(250)
    
    x=0
    pipe='|'
    headerFlag=False
    footerFlag=False
    transactionFlag=False
    skip=False
    transactionDict = {}
    store2={}
    store2prepare={}    
    store3={}
    store4={}
    store4prepare={}
    store7={}
    store9={}
    store14={}
    store15={}
    
    thisRecordSet = 0        
    store2count = 0
    store4count = 0    
           
    isoCurrencyMapping = {
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
    
    for line in text:
        if line[0:1]=='8':  #this is a header line
            thisRecordSet = 0
            fields = line.split('\t')
            fields[4] = fields[4].lstrip('0')
            #print 'record8 '+fields[4]
            if fields[4] in ('2','3','4','5','7','9','14','15'):
                thisRecordSet = fields[4]
            continue
        if line[0:1] == '9':
            thisRecordSet = 0
        if thisRecordSet == 0:
            continue
        if line[0:1] != '1' and line[0:1] != '4':
            print 'this is a change/delete '+str(thisRecordSet) + ' ' +line[0:1]
            continue
        
        fields = line.split('\t')
        recKey = fields[2]+'|'+fields[3]+'|'+fields[4]
        if thisRecordSet == '2':
            #car rental
            store2count = store2count + 1
            recKey = str(store2count)
            store2prepare[recKey] = store2prepare.setdefault(recKey,'N')
            store2prepare[recKey] = line
        elif thisRecordSet == '3':
            #cardholder record - may not need this
            store3[recKey] = store3.setdefault(recKey,'N')
            store3[recKey] = line
        elif thisRecordSet == '4':
            #cardholders deta;ls
            store4count = store4count + 1
            recKey = str(store4count)
            store4prepare[recKey] = store4prepare.setdefault(recKey,'N')
            store4prepare[recKey] = line
        elif thisRecordSet == '5':
            empID = fields[1]
            #store3.setdefault(recKey,'N')
            #store4[empID]=store4.setdefault(empID,'N')
            store2.setdefault(recKey,'N')
            store4[empID]=store4.setdefault(empID,'N')
            store7.setdefault(recKey,'')
            store9.setdefault(recKey,'N')
            store14.setdefault(recKey,'N')
            store15.setdefault(recKey,'|||||')
        elif thisRecordSet == '7':
            #item
            store7.setdefault(recKey,'')
            f7dict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'Item Sequence Number':fields[5],
            'Message Identifier':fields[6],
            'Item Commodity Code':fields[7],
            'Item Descriptor':fields[8],
            'Quantity':fields[9],
            'Unit Cost':fields[10],
            'Unit Measure':fields[11],
            'Vat Tax Amount':fields[12],
            'Type Supply':fields[13],
            'Last Item Indicator':fields[14],
            'Vat Tax Rate':fields[15],
            'Item Discount Amount':fields[16],
            'Item Total Amount':fields[17],
            'Item Product Code':fields[18],
            'Service Identifier':fields[19],
            'Purchase ID Description':fields[20],
            'Source Amount':fields[21],
            'Transaction Date':fields[22],
            'Merchant Category Code':fields[23],
            'Supplier Name':fields[24],
            'Supplier Postal Code':fields[25],
            'Processor Addendum Code':fields[26],
            'Line Item Tax Charged':fields[27],
            'Item Level Usage Code':fields[28],
            'Line Item Source':fields[29],
            'Optional Field 1':fields[30],
            'Optional Field 2':fields[31],
            'Optional Field 3':fields[32],
            'Optional Field 4':fields[33] }
            thisDesc = store7[recKey]
            if thisDesc == '':
                thisDesc=f7dict['Item Descriptor'].strip()
            else:
                thisDesc=thisDesc+', '+f7dict['Item Descriptor'].strip()
            store7[recKey]=thisDesc
        elif thisRecordSet == '9':
            #lodging record
            store9[recKey] = line
        elif thisRecordSet == '14':
            #travel record
            #print 'see record 14'
            store14[recKey] = line
        elif thisRecordSet == '15':
            #travel legs
            store15.setdefault(recKey,'|||||')
            f15dict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'Leg Number':fields[5],
            'Destination Code':fields[6],
            'Carrier Code':fields[7],
            'Service Class':fields[8],
            'Fare Basis':fields[9],
            'Date of Travel':fields[10],
            'Stopover Code':fields[11],
            'Coupon Number':fields[12],
            'Carrier Reference Number':fields[13],
            'Departure Time':fields[14],
            'Arrival Time':fields[15],
            'Origination Code':fields[16],
            'Conjunction Ticket Number':fields[17],
            'Message Identifier':fields[18],
            'Purchase ID':fields[19],
            'Source Amount':fields[20],
            'Transaction Date':fields[21],
            'Merchant Category Code':fields[22],
            'Supplier Name':fields[23],
            'Supplier Postal Code':fields[24],
            'Processor Addendum Code':fields[25],
            'Domestic International Indicator':fields[26],
            'Arrival Date':fields[27],
            'Departure Tax':fields[28],
            'Optional Field 1':fields[29],
            'Optional Field 2':fields[30],
            'Optional Field 3':fields[31],
            'Optional Field 4':fields[32] }
            
            thisDesc = store15[recKey]
            useDesc = thisDesc.split('|')
            if useDesc[0] == '':
                useFromTo = f15dict['Origination Code'].strip()+'/'+f15dict['Destination Code'].strip()
            else:
                useFromTo = useFromTo+'/'+f15dict['Destination Code'].strip()
            if useDesc[1] == '':
                useAirline = f15dict['Carrier Code'].strip()
            else:
                useAirline = useAirline+'/'+f15dict['Carrier Code'].strip()
            if useDesc[2] == '':
                useClass = f15dict['Service Class'].strip()
            else:
                useClass = useClass+'/'+f15dict['Service Class'].strip()
            if useDesc[3] == '':
                useTravelDate = f15dict['Leg Number'].strip() + ';' + f15dict['Date of Travel'].strip()
            else:
                useTravelDate = useTravelDate+'/'+f15dict['Leg Number'].strip() + ';' + f15dict['Date of Travel'].strip()
            if useDesc[4] == '':
                useDomestic = f15dict['Leg Number'].strip() + ';' + f15dict['Domestic International Indicator'].strip()
            else:
                useDomestic = useDomestic + '/' + f15dict['Leg Number'].strip() + ';' + f15dict['Domestic International Indicator'].strip()                
                
            store15[recKey]=useFromTo+'|'+useAirline+'|'+useClass+'|'+useTravelDate+'|'+useDomestic+'|'
                                        
    if store2count != 0:
        for recPass in range(store2count):
            recKey = str(recPass+1)
            line = store2prepare[recKey]
            fields = line.split('\t')
            recKey = fields[2]+'|'+fields[3]+'|'+fields[4]
            store2[recKey] = store2.setdefault(recKey,'N')
            store2[recKey] = line
                        
    if store4count != 0:
        #print 'store4'
        for recPass in range(store4count):
            recKey = str(recPass+1)
            line = store4prepare[recKey]
            fields = line.split('\t')
            #cardholder account and name
            empID = fields[22]
            #empID =empID[0:4]
            store4.setdefault(empID,'N')
            #first and last name only fields needed
            store4[empID] = fields[4].strip() + ' ' + fields[5].strip()

    for line in text:
        if line[0:1]=='6':
            headerFlag=True
            skip=True
        if line[0:1]=='7':  
            footerFlag=True  
            skip=True      

        if line[0:1]=='8':  #this is a header line
            fields = line.split('\t')
            fields[4] = fields[4].lstrip('0')
            skip=True
            if fields[4] == '5': #this is a card detail transaction set
                xfield=fields[4]
                transactionFlag=True
            else:
                transactionFlag=False
        elif line[0:1]=='9':  #this is a footer liner
            fields = line.split('\t')
            fields[4] = fields[4].lstrip('0')
            skip=True
            if fields[4]=='5':  #this is a card detail transaction set
                transactionFlag=False  #marks the end of the transaction set            
        elif line[0:1]=='4' and transactionFlag==True: #process this line
            fields = line.split('\t')
            #'Transaction Type Code':fields[17],
            if fields[17] == '30' or fields[17] == '31':
                #30 = Payment Reversal - NSF Check 31 = Payment
                skip = True
            else:
                skip=False
        else:
            skip=True

        if skip:
            continue  
        
        x=x+1
        ## For readability, the field values are put into a dictionary.
        #this is record 5
        # firstly decide which other records are held
        recKey = fields[2]+'|'+fields[3]+'|'+fields[4]
        empID = fields[1]
        #empID = empID[0:4]
        if store4[empID] == 'N':
            cardHolder = 'XXXXX'
        else:
            cardHolder = store4[empID]

        if store7[recKey] == '':
            itemDetail = False
        else:
            itemDetail = True        

        if store9[recKey] == 'N':
            hotelDetail = False
        else:
            hotelDetail = True        
        
        if store2[recKey] == 'N':
            rentalDetail = False
        else:
            rentalDetail = True        
        
        if store14[recKey] == 'N':
            travelDetail = False
        else:
            travelDetail = True     
        
        if store15[recKey] == '|||||':
            legDetail = False
        else:
            legDetail = True   
            
        if line[0:1]=='4':
            fdict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'Period':fields[5],
            'Acquiring BIN':fields[6],
            'Card Acceptor ID':fields[7],
            'Supplier Name':fields[8],
            'Supplier City':fields[9],
            'Supplier State Code':fields[10],
            'Supplier ISO Country':fields[11],
            'Supplier Postal Code':fields[12],
            'Source Amount':fields[13],
            'Billing Amount':fields[14],
            'Source Currency Code':fields[15],
            'Merchant Category Code':fields[16],
            'Transaction Type Code':fields[17],
            'Transaction Date':fields[18],
            'Billing Currency Code':fields[19],
            'Tax Amount':fields[20],
            'Dispute Amount':fields[21],
            'Dispute Reason Code':fields[22],
            'Dispute Date':fields[23],
            'Commodity Code':fields[24],
            'Supplier VAT Number':fields[25],
            'Supplier Order Number':fields[26],
            'Customer VAT Number':fields[27],
            'VAT Amount':fields[28],
            'Tax2 Amount':fields[29],
            'Purchase Identification Format':fields[30],
            'Customer Code/CRI':fields[31],
            'Purchase Identification':fields[32],
            'Transaction Time':fields[33],
            'Tax Amount Included':fields[34],
            'Tax 2 Amount Included':fields[35],
            'Order Type Code':fields[36],
            'Message Identifier':fields[37],
            'Processor Addendum':fields[38],
            'Merchant Profile':fields[39],
            'Usage Code':fields[40],
            'Enriched Transaction':fields[41],
            'Billing Account Number':fields[42],
            'DDA Number':fields[43],
            'DDA Savings Number':fields[44],
            'Dispute Status Code':fields[45],
            'Matched Indicator':fields[46],
            'Routing Number':fields[47],
            'Authorization Number':fields[48],
            'Cardholder Transaction':fields[49],
            'Extract ID':fields[50],
            'Memo Post Flag':fields[51],
            'Statement Date':fields[52],
            'User Data 1':fields[53],
            'User Data 1 description':fields[54],
            'User Data 2':fields[55],
            'User Data 2 description':fields[56],
            'User Data 3':fields[57],
            'User Data 3 description':fields[58],
            'User Data 4':fields[59],
            'User Data 4 description':fields[60],
            'User Data 5':fields[61],
            'User Data 5 description':fields[62],
            'Visa Commerce Batch ID':fields[63],
            'Commerce Payment':fields[64],
            'Line Item Matched Indicator':fields[65],
            'Issuer-Defined UsageCode':fields[66],
            'Source':fields[67],
            'Optional Field 1':fields[68],
            'Optional Field 2':fields[69],
            'Optional Field 3':fields[70],
            'Optional Field 4':fields[71],
            'Reserved Field':fields[72],
            'Reserved Field':fields[73],
            'Reserved Field':fields[74],
            'Reserved Field':fields[75],
            'description':'',
            'businessPurpose':'',
            'Reconciler':'0.0',
            'Reconciler_Decimal':'-1',
            'Divisor':'0',
            'hasReceipt':'0',
            'hasTaxReceipt':'0',
            'isPersonal':'0',
            'Uda_Values':'',
            'StatementDate':'',
            'WidgetEnabler':'',
            'WidgetOnAddTransaction':'', 
            'isDisableRowButton':'1'}
            
        #skip = False
        if skip:
            continue 
        
        if rentalDetail:
            xline = store2[recKey]
            fields = xline.split('\t')
            f2dict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'No Show Indicator':fields[5],
            'Daily Rental Rate':fields[6],
            'Other Charges':fields[7],
            'Check-out Date':fields[8],
            'Weekly Rental Rate':fields[9],
            'Insurance Charges':fields[10],
            'Fuel Charges':fields[11],
            'Class Code':fields[12],
            'One-way Dropoff Charges':fields[13],
            'Renter Name':fields[14],
            'Auto Towing':fields[15],
            'Regular Mileage Charges':fields[16],
            'Extra Mileage Charges':fields[17],
            'Late Return Hourly Charges':fields[18],
            'Return Location':fields[19],
            'Total Tax Vat':fields[20],
            'Telephone Charges':fields[21],
            'Corporate Identification':fields[22],
            'Extra Charge Code':fields[23],
            'Days Rented':fields[24],
            'Message Identifier':fields[25],
            'Purchase ID':fields[26],
            'Source Amount':fields[27],
            'Transaction Date':fields[28],
            'Merchant Category Code':fields[29],
            'Supplier Name':fields[30],
            'Supplier Postal Code':fields[31],
            'Processor Addendum Code':fields[32],
            'Optional Field 1':fields[33],
            'Optional Field 2':fields[34],
            'Optional Field 3':fields[35],
            'Optional Field 4':fields[36] }
        
        if hotelDetail:
            xline = store9[recKey]
            fields = xline.split('\t')
            f9dict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'No Show Indicator':fields[5],
            'Check In Date':fields[6],
            'Daily Room Rate':fields[7],
            'Total Other Charges':fields[8],
            'Total Tax Amount':fields[9],
            'Total Food Charges':fields[10],
            'Total Prepaid Expenses':fields[11],
            'Total Cash Advances':fields[12],
            'Total Valet Parking Charges':fields[13],
            'Total Mini Bar Charges':fields[14],
            'Total Laundry Charges':fields[15],
            'Total Telephone Charges':fields[16],
            'Total Gift Shop Purchases':fields[17],
            'Total Movie Charges':fields[18],
            'Total Business Center Charges':fields[19],
            'Health Club Charges':fields[20],
            'Extra Charge Code':fields[21],
            'Total Room Tax Amount':fields[22],
            'Lodging Nights':fields[23],
            'Total Non-Room Charges':fields[24],
            'Message Identifier':fields[25],
            'Purchase ID':fields[26],
            'Source Amount':fields[27],
            'Transaction Date':fields[28],
            'Merchant Category Code':fields[29],
            'Supplier Name':fields[30],
            'Supplier Postal Code':fields[31],
            'Processor Addendum Code':fields[32],
            'Optional Field 1':fields[33],
            'Optional Field 2':fields[34],
            'Optional Field 3':fields[35],
            'Optional Field 4':fields[36] }
        
        if travelDetail:
            xline = store14[recKey]
            fields = xline.split('\t')
            f14dict={
            'Load Transaction Code':fields[0],
            'Account Number':fields[1],
            'Posting Date':fields[2],
            'Transaction Reference':fields[3],
            'Sequence Number':fields[4],
            'Departure Date':fields[5],
            'Travel Agency Code':fields[6],
            'Travel Agency Name':fields[7],
            'Ticket Indicator':fields[8],
            'Ticket Number':fields[9],
            'Passenger Name':fields[10],
            'Exchange Ticket Number':fields[11],
            'Exchange Ticket Amount':fields[12],
            'Internet Indicator':fields[13],
            'Total Fare Amount':fields[14],
            'Total Fee Amount':fields[15],
            'Total Tax Amount':fields[16],
            'Message Identifier':fields[17],
            'Endorsement Restrictions':fields[18],
            'Purchase ID':fields[19],
            'Source Amount':fields[20],
            'Transaction Date':fields[21],
            'Merchant Category Code':fields[22],
            'Supplier Name':fields[23],
            'Supplier Postal Code':fields[24],
            'Processor Addendum Code':fields[25],
            'Passenger Specific Data':fields[26],
            'Ticket Issue Date':fields[27],
            'Number of Legs':fields[28],
            'E-Ticket Indicator':fields[29],
            'Optional Field 1':fields[30],
            'Optional Field 2':fields[31],
            'Optional Field 3':fields[32],
            'Optional Field 4':fields[33],
            'Travel Obligation Number':fields[34],
            'TCN Passenger Name':fields[35] }
       
        date_format = '%m/%d/%Y' 
        import datetime # needed?
        
        ########## BEGIN UDA SECTION ##########
                
        widgetOnAddTransactionList = []
        extraTextNarrative = ''  
                
        udaString=['<uda>']
        merchantName = fdict['Supplier Name'].strip()
        
        # Merchant Name
        merchantNameFormatted = merchantName
        
        if travelDetail:
            # Defining early to use with Merchant
            ticketNumber = f14dict['Ticket Number'].strip()
            if ticketNumber in merchantName:
                merchantNameFormatted = merchantName.replace(ticketNumber, '').strip()

        #udaEntry(udaString,'Merchant', merchantNameFormatted, 'string')
        
        extraTextNarrative = 'Merchant: ' + merchantNameFormatted
        
        # Location        
        merchantCity = fdict['Supplier City'].strip()
        location = ''
        if merchantCity:
            extraTextNarrative  = extraTextNarrative + ' Location: ' + merchantCity
            location = merchantCity
                
        # Country & Currency
        originCurrency = fdict['Supplier ISO Country'].strip()[-3:]
        originCurrencyCode = originCountry = ''
        
        if originCurrency:
            if originCurrency in isoCurrencyMapping:
                isoInfo = isoCurrencyMapping[originCurrency].split(';')
                originCurrencyCode = isoInfo[0]
                originCountry = isoInfo[1]

        if originCurrencyCode in ('USD', 'CAD'):
            merchantState = fdict['Supplier State Code'].strip()
            if merchantState:
                extraTextNarrative =  extraTextNarrative + ', ' + merchantState + ' '
                location = location + ', ' + merchantState + ' '
        else:
            if originCountry:
                extraTextNarrative = extraTextNarrative + ', ' + originCountry + ' '
                location = location + ', ' + originCountry
        
        # Zip Code
        zipCode = fdict['Supplier Postal Code'].strip()
        if len(zipCode) > 5:
            zipCodeFormatted = zipCode[0:5] + '-' + zipCode[5:]
        else:
            zipCodeFormatted = zipCode
        
        extraTextNarrative = extraTextNarrative + ' ' + zipCodeFormatted + ' '
        
        #if location:
        #    udaEntry(udaString, 'Location', location, 'string')
        
        ###### AIRFARE #####
        if travelDetail:

            extraTextNarrative = extraTextNarrative + ' AIR:' + merchantNameFormatted
                
            # Passenger Name
            passengerName = f14dict['Passenger Name'].strip() 
            if passengerName:                               
                passengerNameFormatted = re.sub("\s{2,}", '', passengerName)
                extraTextNarrative = extraTextNarrative + ' Passenger: ' + passengerNameFormatted
                #udaEntry(udaString,'PassengerName', passengerNameFormatted, 'string') 
            
            # Ticket Number
            if ticketNumber:
                #udaEntry(udaString,'TicketNum', f14dict['Ticket Number'].strip(), 'string')
                extraTextNarrative = extraTextNarrative + ' Ticket Number: ' + ticketNumber 
                    
            # Depart Date
            departDate = f14dict['Departure Date'].strip()
            if departDate:
                #udaEntry(udaString,'DepartDate', crDateToPosix(f14dict['Departure Date'].strip(), '%m%d%Y'), 'cgdate')
                if len(departDate) == 8 and isaNumberCheck(departDate):
                    departDateFormatted = departDate[0:2] + '/' + departDate[2:4] + '/' + departDate[4:8]
                else:
                    departDateFormatted = departDate
                extraTextNarrative = extraTextNarrative + ' Departure Date: ' + departDateFormatted
        
            # Number of Legs
            numLegs = f14dict['Number of Legs'].strip()
            if numLegs:
                useNumLegs = isaNumberCheck(numLegs)
                if useNumLegs:
                    numLegsFormatted = str(useNumLegs) 
                else:
                    numLegsFormatted = numLegs
                extraTextNarrative = extraTextNarrative + ' Number of Legs: ' + numLegsFormatted
            
        # LEG DETAIL
        if legDetail:
            
            # Retrieve leg stored data
            thisDesc = store15[recKey]
            useDesc = thisDesc.split('|')

            # Routing or From/To            
            if useDesc[0]:

                destinationLegs = useDesc[0].split('/')
                if len(destinationLegs) > 1:
                    fromAirport = destinationLegs[0]
                    destinationAirport = destinationLegs[1]
                else:
                    fromAirport = destinationLegs[0]

                if fromAirport:
                    extraTextNarrative = extraTextNarrative + ' Routing: ' + fromAirport
                if destinationAirport:
                    extraTextNarrative = extraTextNarrative + '/' + destinationAirport

            # Airline Company 
            if useDesc[1]:

                carrierCodes = useDesc[1].split('/')
                if len(carrierCodes) >= 1:
                    airlineCode = carrierCodes[0]
                    #udaEntry(udaString, 'Airline', airlineCode, 'string')
                    extraTextNarrative = extraTextNarrative + ' Airline Code: ' + airlineCode
                
            # Airclass
            if useDesc[2] != '':

                airClass = useDesc[2]

                # This hash is for reference only;
                # Not used in code at all
                airClassDict = {
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

                # The code values need to be changed, depending
                # on the class entity codes setup for the customer
                if 'F' in airClass or 'P' in airClass:
                    airClassCode = 'First'
                elif 'B' in airClass or 'J' in airClass:
                    airClassCode = 'Business'
                else:
                    airClassCode = 'Economy'
                udaEntry(udaString,'AirClass', airClassCode, 'string')
            # Arrival Date - try to use the last leg 'Travel Date'.
            # This is not available directly from Visa
            if useDesc[3] != '':                

                legDates = useDesc[3].split('/')
                tlen = len(legDates)
                if tlen > 1:
                    returnDate = legDates[tlen-1][3:]
                else:
                    returnDate = useDesc[3][3:]
                
                if returnDate:
                    if len(returnDate) == 8 and isaNumberCheck(returnDate):
                        returnDateFormatted = returnDate[0:2] + '/' + returnDate[2:4] + '/' + returnDate[4:8]
                    else:
                        returnDateFormatted = returnDate
                    extraTextNarrative = extraTextNarrative + ' Arrival Date: ' + returnDateFormatted
                
                #udaEntry(udaString,'ArrivalDate', crDateToPosix(returnDate, '%m%d%Y'), 'cgdate')
                #print 'AIRLINE CHECK: ' + extraTextNarrative
            
        ###### HOTEL #####
        if hotelDetail:
            
            # CheckIn Date         
            checkInDate = f9dict['Check In Date'].strip()
            if checkInDate:
                #udaEntry(udaString,'CheckIn', crDateToPosix(startDate, '%m%d%Y'),'cgdate')
                if len(checkInDate) == 8 and isaNumberCheck(checkInDate):
                    checkInDateFormatted = checkInDate[0:2] + '/' + checkInDate[2:4] + '/' + checkInDate[4:8]
                else:
                    checkInDateFormatted = checkInDate
                extraTextNarrative = extraTextNarrative + ' HOTEL: Check-In Date:' + checkInDateFormatted
                
            # Daily Room Rate
            dailyRoomRate = f9dict['Daily Room Rate'].strip()
            if dailyRoomRate and isaNumberCheck(dailyRoomRate):
                # Check if they are only sending zeros
                dailyRoomRateFormatted = dailyRoomRate
            else:
                dailyRoomRateFormatted = '(No Data)'

            extraTextNarrative = extraTextNarrative + ' Daily Room Rate: ' + dailyRoomRateFormatted
            
            # Number of Hotel Nights
            numNights = f9dict['Lodging Nights'].strip()            
            if numNights and isaNumberCheck(numNights):
                numNightsFormatted = numNights
            else:
                numNightsFormatted = '(No Data)'
                
            extraTextNarrative = extraTextNarrative + ' Stay Duration: ' + numNightsFormatted
            
            #print 'HOTEL CHECK: ' + extraTextNarrative
        
        ###### RENTAL #####
        if rentalDetail:
            
            rentalDict = {
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
            
            rentalDate = f2dict['Check-out Date'].strip()
            #udaEntry(udaString, 'PickUpDate', crDateToPosix(rentalDate, '%Y-%m-%d'), 'cgdate')
            if rentalDate:
                if len(rentalDate) == 8 and isaNumberCheck(rentalDate):
                    rentalDateFormatted = rentalDate[0:2] + '/' + rentalDate[2:4] + '/' + rentalDate[4:8]
                else:
                    rentalDateFormatted = rentalDate

                extraTextNarrative = extraTextNarrative + ' RENTAL: Check-out: ' + rentalDateFormatted
                
            # Renter Name
            renterName = f2dict['Renter Name'].strip()
            if renterName:
                extraTextNarrative = extraTextNarrative + ' Renter Name: ' + renterName
                
            # Rental Class
            rentalCode = f2dict['Class Code'].strip()
            if rentalCode:
                extraTextNarrative = extraTextNarrative + ' Rental Code: ' + rentalCode
            
            # Rental Location
            rentalReturnLoc = f2dict['Return Location'].strip()
            if rentalReturnLoc:
                extraTextNarrative = extraTextNarrative + ' Return Location: ' + rentalReturnLoc
            
            # Days Rented
            numDays = f2dict['Days Rented'].strip()
            if numDays and isaNumberCheck(numDays):
                numDaysFormatted = numDays
                extraTextNarrative = extraTextNarrative + ' Days Rented: ' + numDaysFormatted

            #print 'RENTAL CHECK: ' + extraTextNarrative

        udaString.append('</uda>')
         
        if len(udaString)>2:  
            udaStringOutput= ''.join(udaString)
        else: 
            udaStringOutput=''
                
        # Widgets - this only applies to platinum        
        # Disable the date field
        widgetOnAddTransactionList.append('dte1_ExpenseLineItemForm_Date.enabled=false')
        
        widgetOnAddTransactionString=(';').join(widgetOnAddTransactionList)

        ########## BEGIN DATA PROCESSING FOR DB ##########   
        
        # Transaction Unique ID
        # This information seem to be guaranteed for Visa clients
        combinedID = fdict['Transaction Reference'].strip()
        
        if fdict['Sequence Number'] is not None:
            combinedID = combinedID + fdict['Sequence Number'].strip()
        
        transactionDict.setdefault(combinedID, fdict)
        
        # Transaction Date
        transactionDate=''
        TransactionDate_Mask='MMddyyyy'
        
        # Amount Sign - Credit/Debit
        thisSign = ''
        if fdict['Transaction Type Code'] in ('11','61','63','65','71','73'):
            # 11 = Credit Voucher 61 = Credit Adjustment 63 = Finance Charge
            # CreditAdjustment 65 = Other Credits 71 = Fuel Discount 73 = Non-Fuel Discount
            thisSign = '-'
            
        # Statement Date
        if len(fdict['Statement Date'].strip())==8 and fdict['Statement Date'] != '00000000':
            statementDate=fdict['Statement Date']
            statementDateFormatted=statementDate[0:2]+'/'+statementDate[2:4]+'/'+statementDate[4:8]
        elif len(fdict['Posting Date'].strip())==8: 
            statementDate=fdict['Posting Date']
            statementDateFormatted=statementDate[0:2]+'/'+statementDate[2:4]+'/'+statementDate[4:8]
        else:
            statementDateFormatted = ''
        
        if skip: continue
        
        ########## END DATA PROCESSING SECTION ##########
     
        outputRecord =['Line_Number','Transaction_UniqueID','TransactionDate','TransactionDate_Mask','Name','Vendor_Name','Amount_Spent','Amount_Spent_Decimals','Currency_Code_Spent','VAT_Percent',\
                       'VAT_Percent_Decimals','VAT_Amount','VAT_Amount_Decimals','Amount_Original','Amount_Original_Decimals','CurrencyCode_Original','ExchangeRate','ExchangeRate_Decimals','MatterNumber',\
                       'DefaultCostCode','ExpenseMapping','AppendToDescription','ExtraText','CustomerUniqueID','isFirmPaid','isDeletable','isNeededReceipt','isAmountDisabled','isCurrencyDisabled','ParentID',\
                       'InputType','Description','Business_Purpose','hasReceipt','hasTaxReceipt','isPersonal','Country_Alpha','Reconciler','Reconciler_Decimal','Divisor','UDA_Values','StatementDate','WidgetEnabler',\
                       'WidgetOnAddTransaction','IsDisableRowButton','ReferenceData']
          
        oline = Base (outputRecord)  
        
        def updateOline (field, value, end=None):
            existingValue = getattr(oline, field)
            updateValue=str(fdict.get(value, value)).strip()[0:end]
            existingValue[1] = updateValue
            return         
        
        ########## BEGIN BUILDING LINE ##########
        
        updateOline('Line_Number', str(x))
        updateOline('Transaction_UniqueID', combinedID)
        updateOline('TransactionDate', 'Transaction Date')
        updateOline('TransactionDate_Mask', TransactionDate_Mask)
        updateOline('Name', merchantNameFormatted)
        updateOline('Vendor_Name', merchantNameFormatted)
        updateOline('Amount_Spent', thisSign+fdict['Billing Amount'])
        updateOline('Amount_Spent_Decimals', '2')
        updateOline('Currency_Code_Spent', fdict['Billing Currency Code'][-3:].zfill(3))
        updateOline('Amount_Original', thisSign+fdict['Source Amount'])
        updateOline('Amount_Original_Decimals', '2')
        updateOline('CurrencyCode_Original', fdict['Source Currency Code'][-3:].zfill(3))
        #updateOline('ExchangeRate', '')
        #updateOline('ExchangeRate_Decimals', '')
        #updateOline('MatterNumber', '')
        #updateOline('DefaultCostCode', '')        
        updateOline('ExpenseMapping', 'Merchant Category Code')
        updateOline('AppendToDescription', '')
        updateOline('ExtraText', extraTextNarrative)
        updateOline('CustomerUniqueID', 'Account Number')
        updateOline('isFirmPaid', '1')
        updateOline('isDeletable', '0')
        updateOline('isAmountDisabled', '1')
        updateOline('isCurrencyDisabled','1')
        updateOline('InputType', 'L')
        updateOline('Description', 'description')
        updateOline('Business_Purpose', 'businessPurpose')        
        updateOline('Reconciler', 'Reconciler')
        updateOline('Reconciler_Decimal', 'Reconciler_Decimal')
        updateOline('Divisor', 'Divisor')
        updateOline('hasReceipt', 'hasReceipt')
        updateOline('IsDisableRowButton', 'isDisableRowButton')
        updateOline('hasTaxReceipt', 'hasTaxReceipt')
        updateOline('UDA_Values', udaStringOutput)
        updateOline('StatementDate', statementDateFormatted)
        updateOline('WidgetOnAddTransaction', widgetOnAddTransactionString)
        updateOline('ReferenceData', 'Account ID: '+fdict['Account Number'])
                
        # Uncomment to see the output in eclipse
        # print oline.buildList().strip()
                
        outfile.writelines(oline.buildList())
        
        ########## END BUILDING LINE ##########
        
    #exit with error if not a complete Visa file.
    if headerFlag==False or footerFlag==False:
        print 'not a normal Visa file'
        os._exit(250)        
    outfile.close()
    os._exit(0)
    
if __name__ == '__main__':
    main()
