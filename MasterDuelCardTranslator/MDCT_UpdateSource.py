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

print('正在更新英文卡片数据。翻译数据请手动更新。本次更新可能需要若干分钟。')
print('英文卡片数据来源：https://db.ygoprodeck.com/api/v7/cardinfo.php')
print('请参考：https://db.ygoprodeck.com/api-guide/')
print('\n')

con = sqlite3.connect('source.cdb')
cursor = con.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT, desc TEXT);')

print('请稍候。正在进行：访问网络，下载英文卡片数据。')

db = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
data_list = db.json()['data']

if len(data_list) > 10000:
    print('请稍候。正在进行：保存英文卡片数据。')
    cursor.execute('DELETE FROM data;')
    i = 0
    for data in data_list:
        sql = 'INSERT INTO data VALUES ({}, "{}", "{}", "{}");'.format(
            data['id'], 
            data['name'].replace('"', '""'), 
            data['type'].replace('"', '""'), 
            data['desc'].replace('"', '""')
        )
        cursor.execute(sql)
        i += 1
else:
    raise Exception('The number of cards does NOT seem right.')

con.commit()

res = cursor.execute('SELECT id, name, type, desc FROM data').fetchall()

cursor.close()
con.close()

print('请稍候。正在进行：优化卡片文本数据。')

con = sqlite3.connect('search.db')
cursor = con.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS data (desc TEXT PRIMARY KEY, id INTEGER, name TEXT);')
cursor.execute('DELETE FROM data;')

source_card_desc_and_id = []

for source_card_info in res:
    source_card_id = source_card_info[0]
    source_card_name = source_card_info[1]
    source_card_desc = (source_card_info[3] + '\r\n').replace('[ Monster Effect ]\r\n', '').replace('[ Flavor Text ]\r\n', '').replace('[ Pendulum Effect ]', '[Pendulum Effect]').replace('\r\n', '\n').replace('\n', ' ')
    source_card_desc_list = source_card_desc.split('---------------------------------------- ')
    if len(source_card_desc_list) == 1:
        source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
    elif len(source_card_desc_list) == 2:
        source_card_desc = source_card_desc_list[0] + source_card_desc_list[1]
        source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
        source_card_desc = source_card_desc_list[1] + source_card_desc_list[0]
        source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
    else:
        raise Exception('Invalid card text of id = {}'.format(source_card_id))

for source_card_info in source_card_desc_and_id:
    sql = 'INSERT INTO data VALUES ("{}", {}, "{}");'.format(source_card_info[0].replace('"', '""'), source_card_info[1], source_card_info[2].replace('"', '""'))
    try:
        cursor.execute(sql)
    except:
        pass
con.commit()
con.close()

input('\nDone.')