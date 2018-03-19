import requests
import json
import psycopg2
from iTunesLookup import getAppName
import os
import csv
import sys

hostname = 'localhost'
username = 'shivatk'
password = '8989'
database = 'FirstDriver'

def SyncAssets(sToken,SessionKey):
    hostname = 'localhost'
    username = 'shivatk'
    password = '8989'
    database = 'FirstDriver'
    con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
    cur = con.cursor()
    URL = 'https://vpp.itunes.apple.com/WebObjects/MZFinance.woa/wa/getVPPAssetsSrv'
    payload = '{"sToken":"'+sToken+'","includeLicenseCounts":true}'
    r = requests.post(url=URL,data=payload)
    _dump = json.loads(r.text)

    if _dump.get('errorMessage'):
        return 'LoginFailed'

    _assetDict = _dump.get('assets')

    for i in range(0,len(_assetDict)):
        adamId = (_assetDict[i]['adamIdStr'])
        Name = getAppName(adamId)
        totalCount = _assetDict[i]['totalCount']
        availableCount = _assetDict[i]['availableCount']
        redeemedCount = totalCount - availableCount
        cur.execute("INSERT INTO SyncAssets(SessionKey,sToken,AppName,TotalCount,RedeemedCount,AvailableCount)\
        VALUES('"+str(SessionKey)+"','"+sToken+"','"+str(Name)+"','"+str(totalCount)+"','"+str(redeemedCount)+"','"+str(availableCount)+"');")

    con.commit()
    cur.execute("SELECT AppName,TotalCount,RedeemedCount,AvailableCount FROM SyncAssets\
    WHERE SessionKey ='"+str(SessionKey)+"'")

    rows = cur.fetchall()
    con.commit()
    cur.close()
    con.close()
    return rows

def getVPPLicensesBySerial(sToken,SerialNumber,batchToken,SessionKey):
    hostname = 'localhost'
    username = 'shivatk'
    password = '8989'
    database = 'FirstDriver'
    con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
    cur = con.cursor()

    if batchToken == '':
        payload = '{"sToken":"'+sToken+'"}'
    else:
        payload = '{"sToken":"'+sToken+'","batchToken":"'+batchToken+'"}'

    URL = 'https://vpp.itunes.apple.com/WebObjects/MZFinance.woa/wa/getVPPLicensesSrv'
    r = requests.post(url=URL,data=payload)
    _raw = json.loads(r.text)
    if _raw.get('errorMessage'):
        return 'LoginFailed'
    if _raw.get('batchCount') == 0:
        cur.close()
        con.close()
        return

    _licenseList = _raw.get('licenses')

    for i in range(0,len(_licenseList)):
        try:
            if _licenseList[i]['serialNumber'] == SerialNumber:
                AppName = getAppName(_licenseList[i]['adamIdStr'])
                cur.execute("INSERT INTO DeviceAppMap(SessionKey, SerialNumber, AppName) \
                VALUES ('"+str(SessionKey)+"','"+SerialNumber+"','"+AppName+"');")
                con.commit()
        except:
            pass
    batchToken = _raw.get('batchToken')

    if batchToken == None:
        return

    getVPPLicensesBySerial(sToken,SerialNumber,batchToken,SessionKey)
    cur.execute("SELECT AppName FROM DeviceAppMap \
    WHERE SerialNumber = '"+SerialNumber+"' AND SessionKey ='"+str(SessionKey)+"'")
    rows = cur.fetchall()
    cur.close()
    con.close()
    return rows

def vpprevoke(sToken,filepath,SessionKey):
    sToken = sToken
    licenseFile = open(filepath, "r")
    reader = csv.reader(licenseFile)
    licenselist = []
    for row in reader:
        licenselist.append(str(row[0]))
    cleanedList = [x.strip() for x in licenselist if x.strip()]
    for i in cleanedList:
        vpprevokelicense(sToken,i,SessionKey)
    return

def vpprevokelicense(sToken,license,SessionKey):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(APP_ROOT, 'licensefiles/')
    Logger = "/".join([target, str(SessionKey)])
    logFileDestination = Logger + '.log'
    Log_file = open(logFileDestination,'a')
    URL = 'https://vpp.itunes.apple.com/WebObjects/MZFinance.woa/wa/disassociateVPPLicenseSrv'
    payload = '{"sToken":"'+sToken+'","licenseId":"'+license+'"}'
    print(license)
    r = requests.post(url=URL,data=payload)
    _raw = json.loads(r.text)
    if _raw.get('errorMessage'):
        Log_file.write('LicenseID - '+license +' '+_raw.get('errorMessage')+'\n')
        Log_file.close()
        return
    if _raw.get('status') == 0:
        Log_file.write(license +' revoked successfully \n')
    else:
        Log_file.write(license +' Unable to revoke \n')
        Log_file.close()
        return
    Log_file.close()
    return


if __name__ == '__main__':
        vpprevoke('eyJleHBEYXRlIjoiMjAxOS0wMS0zMFQyMTo1Mjo1Ni0wODAwIiwidG9rZW4iOiJDc1RUL0dRTjVwOXlQWFpKdkpvblVnRXNGYjlmMXJTdytCZHJtdEx4VnU4QkZPNUs0eHF5MVlFMjFzbmJPYXNSMU5jamVsRzJjVDlDYkRBOE5hSys2TFR4a0k2c1VUVnkxQytQVXZrNUQwaz0iLCJvcmdOYW1lIjoiQWlyV2F0Y2gifQ==','/Users/shivatk/Flask/code/licensefiles/3816006.csv','chiller')
