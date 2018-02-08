import psycopg2

hostname = 'localhost'
username = 'postgres'
password = 'postgres'
database = 'AppleMDM'
con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )

cur = con.cursor()
cur.execute("CREATE TABLE SyncAssets \
(SessionKey char(100),sToken char(300),AppName char(200),TotalCount INT,RedeemedCount INT,AvailableCount INT)")

con.commit()

cur.execute('CREATE TABLE DeviceAppMap(SessionKey char(100),SerialNumber char(50),AppName char(100))')

con.commit()

#cur.execute("SELECT AppName FROM DeviceAppMap \
#WHERE SerialNumber = '"+SerialNumber+"'")
cur.execute("CREATE TABLE AdamIDs (AppName char(100),SerialNumber char(50)")


con.commit()
cur.close()
con.close()
