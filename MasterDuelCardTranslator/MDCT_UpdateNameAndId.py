import requests
import sqlite3

con = sqlite3.connect('name_and_id.db')
cursor = con.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS data (name TEXT PRIMARY KEY, id INTEGER NOT NULL);')

db = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
data_list = db.json()['data']

if len(data_list) > 10000:
    cursor.execute('DELETE FROM data;')
    i = 0
    for data in data_list:
        sql = 'INSERT INTO data VALUES ("{}", {});'.format(data['name'].replace('"', '""'), data['id'])
        cursor.execute(sql)
        i += 1
        print('[{}/{}]'.format(i, len(data_list)))

con.commit()
cursor.close()
con.close()

print('Done.')