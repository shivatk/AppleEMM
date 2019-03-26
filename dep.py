import json
import requests
from requests_oauthlib import OAuth1
import psycopg2


def getDEPSession(DEPToken):
    CK = DEPToken['CK']
    CS = DEPToken['CS']
    AT = DEPToken['AT']
    AS = DEPToken['AS']
    URL = 'https://mdmenrollment.apple.com/session'
    auth = OAuth1(CK, CS, AT, AS)
    r = requests.get(url=URL, auth=auth)
    if r.text == 'token_expiredUnauthorized':
        return 'Unauthorized'

    if r.status_code == '400':
        return 'BadRequest'

    if r.status_code == '401':
        return 'Unauthorized'

    _raw = json.loads(r.text)
    return _raw.get('auth_session_token')


def getDEPProfileName(uuid, Token, DEPToken):
    hostname = 'appleemm.cyob1f1ueydk.us-east-1.rds.amazonaws.com'
    username = 'firstdriver'
    password = 'firstdriver'
    database = 'firstdriver'
    con = psycopg2.connect(
        host=hostname, user=username, password=password, dbname=database
    )
    cur = con.cursor()
    cur.execute(
        "SELECT Name FROM DEPProfileName\
    WHERE UUID ='" +
        str(uuid) +
        "'"
    )
    response = cur.fetchall()
    if response != []:
        return response[0][0]

    URL = 'https://mdmenrollment.apple.com/profile'
    QueryString = {"profile_uuid": uuid}
    Headers = {"X-Server-Protocol-Version": "2", "X-ADM-Auth-Session": Token}
    r = requests.get(url=URL, headers=Headers, params=QueryString)
    if r.status_code == '401':
        Token = getDEPSession(DEPToken)
        getDEPProfileName(uuid, Token, DEPToken)
    _raw = json.loads(r.text)
    Name = _raw.get('profile_name')
    cur.execute(
        "INSERT INTO DEPProfileName (UUID,Name)\
    VALUES ('" +
        str(uuid) +
        "','" +
        str(Name) +
        "')"
    )
    con.commit()
    cur.close()
    con.close()
    return Name


def DEPFetch(SessionKey, DEPToken, Cursor):
    cursor = Cursor
    hostname = 'appleemm.cyob1f1ueydk.us-east-1.rds.amazonaws.com'
    username = 'firstdriver'
    password = 'firstdriver'
    database = 'firstdriver'
    con = psycopg2.connect(
        host=hostname, user=username, password=password, dbname=database
    )
    cur = con.cursor()
    URL = 'https://mdmenrollment.apple.com/server/devices'
    if Cursor == '':
        payload = '{"limit":1000}'
    else:
        payload = '{"limit":1000,"cursor":"' + str(cursor) + '"}'
    print(payload)
    try:
        Token = getDEPSession(DEPToken)
    except:
        return ('Invalid')

    if Token == 'BadRequest':
        return ('BadRequest')

    if Token == 'Unauthorized':
        return ('Token Expired')

    Headers = {"X-Server-Protocol-Version": "2", "X-ADM-Auth-Session": Token}
    r = requests.post(url=URL, headers=Headers, data=payload)
    if r.status_code == '401':
        Token = getDEPSession(DEPToken)
    _raw = json.loads(r.text)
    Cursor = _raw.get('cursor')
    more = _raw.get('more_to_follow')
    devices = _raw.get('devices')
    for i in devices:
        SerialNumber = i['serial_number']
        status = i['profile_status']
        if status != 'empty':
            uuid = i['profile_uuid']
            Name = getDEPProfileName(uuid, Token, DEPToken)
        else:
            Name = ''
        date = i['device_assigned_date']
        cur.execute(
            "INSERT INTO DEPRecords (SessionKey,SerialNumber,ProfileStatus,ProfileName,DateAssigned)\
        VALUES('" +
            str(SessionKey) +
            "','" +
            str(SerialNumber) +
            "','" +
            str(status) +
            "',\
        '" +
            str(Name) +
            "','" +
            str(date) +
            "')"
        )
        con.commit()
    print('iteration continues..')
    if more == True:
        DEPFetch(SessionKey, DEPToken, Cursor)
    else:
        pass
    cur.execute(
        "SELECT SerialNumber,ProfileStatus,ProfileName,DateAssigned FROM DEPRecords \
    WHERE SessionKey ='" +
        str(SessionKey) +
        "'"
    )
    respo = cur.fetchall()
    cur.close()
    con.close()
    return respo


def getDeviceDetails(SessionKey, SerialNumber, DEPToken):
    hostname = 'appleemm.cyob1f1ueydk.us-east-1.rds.amazonaws.com'
    username = 'firstdriver'
    password = 'firstdriver'
    database = 'firstdriver'
    con = psycopg2.connect(
        host=hostname, user=username, password=password, dbname=database
    )
    cur = con.cursor()
    try:
        Token = getDEPSession(DEPToken)
    except:
        return ('Invalid')

    if Token == 'BadRequest':
        return ('BadRequest')

    if Token == 'Unauthorized':
        return ('Token Expired')

    URL = 'https://mdmenrollment.apple.com/devices'
    Headers = {"X-Server-Protocol-Version": "2", "X-ADM-Auth-Session": Token}
    payload = '{"devices":["' + str(SerialNumber) + '"]}'
    r = requests.post(url=URL, headers=Headers, data=payload)
    _raw = json.loads(r.text)
    D = _raw.get('devices')
    DeviceDetails = D[SerialNumber]
    if DeviceDetails['response_status'] == 'NOT_ACCESSIBLE':
        return 'Null'

    model = DeviceDetails['model']
    status = DeviceDetails['profile_status']
    if status != 'empty':
        uuid = DeviceDetails['profile_uuid']
        Name = getDEPProfileName(uuid, Token, DEPToken)
        Name = Name.replace("'", "")
        Date = DeviceDetails['profile_assign_time']
    else:
        Name = ''
        Date = ''
    cur.execute(
        "INSERT INTO DeviceDetails (SessionKey,SerialNumber,Model,\
    ProfileStatus,ProfileName,ProfileAssignedDate)\
    VALUES ('" +
        str(SessionKey) +
        "','" +
        str(SerialNumber) +
        "','" +
        str(model) +
        "',\
    '" +
        str(status) +
        "','" +
        str(Name) +
        "','" +
        str(Date) +
        "')"
    )
    con.commit()
    cur.execute(
        "SELECT SerialNumber,Model,ProfileStatus,ProfileName,ProfileAssignedDate\
    FROM DeviceDetails\
    WHERE SessionKey='" +
        str(SessionKey) +
        "'"
    )
    rows = cur.fetchall()
    return rows

    cur.close()
    con.close()


def main():
    DEPToken = {
        "CK": "CK_62cf6d022b46e3a62f3f56fa023b48565dc0e7ca1d5369542b68d75ef31fef32fca91f63655f77215722b4f05a629d9e",
        "CS": "CS_b2ae1454efcc7fc1e5916b7cac19ae720151596d",
        "AT": "AT_O8611596003Oda71f1a2fa417f9f38b7be6564740880c1d4553dO1486752482811",
        "AS": "AS_3064ccc454819b4d015da8fb90e8b916a99fa7e1",
    }
    # DEPFetch('abc',DEPToken,'')
    a = getDEPSession(DEPToken)
    print(a)


if __name__ == '__main__':
    main()
