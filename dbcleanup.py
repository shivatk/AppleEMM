import psycopg2

hostname = 'appleemm.cyob1f1ueydk.us-east-1.rds.amazonaws.com'
username = 'shivatk'
password = 'shivatk'
database = 'shivatk'

con = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )

cur = con.cursor()

cur.execute("DELETE FROM DEPRecords")
con.commit()
cur.execute("DELETE FROM SyncAssets")
con.commit()
cur.execute("DELETE FROM DeviceDetails")
con.commit()
cur.execute("DELETE FROM DeviceAppMap")
con.commit()

cur.close()
con.close()
