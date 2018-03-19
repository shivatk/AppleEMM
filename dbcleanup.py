import psycopg2

hostname = 'localhost'
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
