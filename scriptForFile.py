
import os
import time
from itertools import groupby
from random import randint


def getExactlyBin(path):
    bankList = []
    with open(path, 'r') as f:
        lines = f.readlines()
        ccList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x ) if
                  not key]
    for id,cc in enumerate(ccList):
        minList = []
        for i, s in enumerate(cc):
            if "Card BIN" in s:
                if len(s.strip()) > 10:
                    cardBin = cc[i].split(":")[1].strip()
                    minList.append(cardBin)
            if "Date of birth" in s:
                DOB = cc[i].split(":")[1].split("/")[-1].strip()
                minList.append(DOB)
            if "Address" in s:
                postcode = cc[i].split(",")[-1][:4].strip()
                minList.append(postcode)
            if "Card Number" in s:
                cardNumber = cc[i].split(":")[1].strip()
                minList.append(cardNumber)
        bankList.append([id,minList])
    return bankList

def countCC(path):
    with open(path, 'r') as f:
        lines = f.readlines()
        myList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x ) if not key]
        newList = []
        for i in myList:
            if len(i)>5:
                newList.append(i)
        return len(newList)

def getExactlyId(sid,path):
    id = int(sid)
    ccData = {
        'cardBIN':'',
        'DOB':'',
        'postcode':'',
        'cardNumber':'',
    }
    with open(path, 'r') as f:
        lines = f.readlines()
        ccList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x )
                  if
                  not key]
    for i, cc in enumerate(ccList[id]):
        if "Card BIN" in cc:
            cardBin = cc.split(":")[1].strip()
            ccData['cardBIN'] = cardBin
        if "Date of birth" in cc:
            DOB = cc.split(":")[1].split("/")[-1].strip()
            ccData['DOB'] = DOB
        if "Address" in cc:
            postcode = cc.split(",")[-1][:4]
            ccData['postcode'] = postcode
        if "Card Number" in cc:
            cardNumber = cc.split(":")[1].strip()
            ccData['cardNumber'] = cardNumber
    return ccData

def removeRecord(id,path):
    with open(path, 'r') as d:
        lines = d.readlines()
        ccList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x)if not key]
    ccList.pop(id)
    with open(path, 'w') as f:
        for id,line in enumerate(ccList):
            for l in line:
                f.write(l)
            if id == len(ccList):
                return
            f.write("Received:\n")




def buyExactlyId(pathFile,binID,user_id):
    if not os.path.exists(f"sold/{user_id}"):
        os.makedirs(f"sold/{user_id}")

    fileName = f"{int(time.time())}.txt"
    with open(pathFile, 'r') as f:
        lines = f.readlines()
        ccList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x ) if
                  not key]
    with open(f"sold/{user_id}/{fileName}",'a+') as s:
        for line in ccList[binID]:
            s.writelines(line)
    return f"sold/{user_id}/{fileName}"


def searchBin(path,bin):
    foundBins = []
    with open(path, 'r') as f:
        lines = f.readlines()
        ccList = [list(group) for key, group in groupby(lines, key=lambda x: 'Received:' in x )
                  if
                  not key]
    for id, cc in enumerate(ccList):
        for i, s in enumerate(cc):
            if "Card BIN" in s:
                if bin in s:
                    foundBins.append(id)
    return foundBins


def generateOrder(n=6):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def percentage(num, per):
    return round(float((num * per) / 100),1)




def getExactlyIdByCardNumber(path,ccID):
    with open(path, 'r') as f:
        lines = f.readlines()
        myList = [list(group) for key, group in groupby(lines, key=lambda x:'Received:' in x ) if not key]
        for id,cc in enumerate(myList):
            for i, s in enumerate(cc):
                if "Card Number" in s.strip():
                    if str(ccID) in cc[i].split(":")[1].strip():
                        return id
