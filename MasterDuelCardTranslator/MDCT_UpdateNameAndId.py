#    Master Duel Card Translator Project
#    Copyright (C) 2022  LLForever and Rehcramon
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import sqlite3

import MDCT_Common

MDCT_Common.print_info()

print('正在更新卡名数据。翻译数据请手动更新。本次更新可能需要若干分钟。')
print('卡名数据来源：https://db.ygoprodeck.com/api/v7/cardinfo.php')
print('\n')

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
        print('\r更新进度：[{}/{}]'.format(i, len(data_list)), end='')

con.commit()
cursor.close()
con.close()

input('\nDone.')