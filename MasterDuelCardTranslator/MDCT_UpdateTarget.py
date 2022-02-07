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
import os

import MDCT_Common

MDCT_Common.print_info()

print('正在更新卡片翻译数据。本次更新可能需要若干分钟。')
print('卡片翻译数据来源：https://github.com/mycard/ygopro-database/raw/master/locales/zh-CN/cards.cdb')
print('请参考：https://github.com/mycard/ygopro-database/')
print('\n')

try:
    db = requests.get('https://github.com/mycard/ygopro-database/raw/master/locales/zh-CN/cards.cdb')
except:
    print('更新卡片翻译数据时出现了一些问题。有可能是网络状况不佳。请再次尝试，或者手动更新卡片翻译数据。\n')
    print('如果要手动更新卡片翻译数据，请下载最新的YGOPro，将其目录下的cards.cdb文件复制到本目录下，并重命名为ygocore.cdb。')
    input()
    raise

db_file = open('target.cdb', 'wb')
db_file.write(db.content)
db_file.close()

try:
    os.replace('ygocore.cdb', 'ygocore.old.cdb')
except:
    pass
os.replace('target.cdb', 'ygocore.cdb')

input('\nDone.')