import json
import requests
import psycopg2

def getAppName(adamId):
    hostname = 'localhost'
    username = 'shivatk'
    password = '****'
    database = 'FirstDriver'
    con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
    cur = con.cursor()
    cur.execute("SELECT AppName FROM AdamIDs \
    WHERE AdamId='"+str(adamId)+"'")
    response = cur.fetchall()
    if response != []:
        return response[0][0]
    URL = 'https://itunes.apple.com/lookup?id='+str(adamId)
    r = requests.get(url=URL)
    _rawiTunes = json.loads(r.text)
    Res = _rawiTunes.get('results')
    try:
        Name = Res[0]['trackName']
    except:
        Name = adamId+' - Unable to fetch App Name'
        cur.close()
        con.close()
        return Name
    Name = Name.replace("'","")
    cur.execute("INSERT INTO AdamIds (AppName,AdamId)\
    VALUES('"+str(Name)+"','"+str(adamId)+"')")
    con.commit()
    cur.close()
    con.close()
    return Name
