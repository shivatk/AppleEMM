import psycopg2

hostname = 'localhost'
username = 'firstdriver'
password = 'firstdriver'
database = 'firstdriver'
con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )

cur = con.cursor()
#cur.execute("CREATE TABLE SyncAssets \
#(SessionKey char(100),sToken char(300),AppName char(200),TotalCount INT,RedeemedCount INT,AvailableCount INT)")
#con.commit()
#cur.execute("CREATE TABLE DEPRecords (SessionKey char(100),SerialNumber char(50),ProfileStatus char(50),ProfileName char(100),DateAssigned char(100))")
#con.commit()
#
#cur.execute('CREATE TABLE DEPProfileName(UUID char(100),Name char(100))')
#con.commit()

#cur.execute("CREATE TABLE DeviceDetails(SessionKey char(100),SerialNumber char(100),Model char(200),ProfileStatus char(20),ProfileName char(100),ProfileAssignedDate char(100))")
#con.commit()
#cur.execute('CREATE TABLE DeviceAppMap(SessionKey char(100),SerialNumber char(50),AppName char(100))')

#con.commit()

#cur.execute("DELETE FROM DEPRecords")

#WHERE SerialNumber = '"+SerialNumber+"'")
cur.execute("CREATE TABLE AdamIDs (AppName char(200),AdamID char(50))")


con.commit()
cur.close()
con.close()
