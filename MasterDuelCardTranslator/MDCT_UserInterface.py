#    Master Duel Card Translator Project
#    Copyright (C) 2022  Rehcramon and LLForever
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
import json
import os
import tkinter as tk
import tkinter.messagebox

import MDCT_Common

def about_messagebox():
    tk.messagebox.showinfo('关于 '+MDCT_Common.SHORT_TITLE, MDCT_Common.INFO)

def update_source_command():
    ret = tk.messagebox.askquestion('更新源数据', '''\
要更新源数据吗？此过程需要访问网络，可能需要若干分钟。
数据来源：https://db.ygoprodeck.com/api/v7/cardinfo.php
请参考：https://db.ygoprodeck.com/api-guide/\
''')
    if ret == 'no':
        return
    toplevel = tk.Toplevel()
    toplevel.title('更新源数据')
    toplevel.geometry('300x200')
    toplevel.attributes('-topmost', True)
    toplevel.update()

    text_common = '''\
正在更新源数据。本次更新可能需要若干分钟。
请耐心等待，不要关闭本界面。
若MDCT出现若干分钟的未响应，是正常情况。
'''
    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=MDCT_Common.load_setting('font'))
    text.pack()

    text.insert(tk.INSERT, text_common + '\n[1/3]访问网络并下载源数据。')
    text.config(state=tk.DISABLED)
    toplevel.update()

    try:
        db = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php')
    except:
        tk.messagebox.showerror('更新源数据失败', '更新源数据时出现了一些问题。有可能是网络状况不佳。请检查网络状况后再次尝试。')
        toplevel.destroy()
        return

    data_list = db.json()['data']

    if len(data_list) < 10000:
        tk.messagebox.showerror('更新源数据失败', '源数据的内容可能存在问题。欢迎反馈此情况。谢谢。失败原因：卡片数量不足。')
        toplevel.destroy()
        return

    text.config(state=tk.NORMAL)
    text.delete('1.0', tk.END)
    text.insert(tk.INSERT, text_common + '\n[2/3]保存源数据。')
    text.config(state=tk.DISABLED)
    toplevel.update()

    con = sqlite3.connect('source.cdb')
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY, name TEXT UNIQUE, type TEXT, desc TEXT);')

    data_list_overwrite_file = open('source_overwrite.json', 'r')
    data_list_overwrite = json.loads(' '.join(data_list_overwrite_file.readlines()))
    data_list_overwrite_file.close()
    data_list = data_list_overwrite + data_list

    cursor.execute('DELETE FROM data;')
    for data in data_list:
        sql = 'INSERT INTO data VALUES ({}, "{}", "{}", "{}");'.format(
            data['id'], 
            data['name'].replace('"', '""'), 
            data['type'].replace('"', '""'), 
            data['desc'].replace('"', '""')
        )
        try:
            cursor.execute(sql)
        except:
            pass
    con.commit()

    res = cursor.execute('SELECT id, name, type, desc FROM data').fetchall()

    con.close()

    text.config(state=tk.NORMAL)
    text.delete('1.0', tk.END)
    text.insert(tk.INSERT, text_common + '\n[3/3]优化源数据。')
    text.config(state=tk.DISABLED)
    toplevel.update()

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
            tk.messagebox.showerror('更新源数据失败', '源数据的内容可能存在问题。欢迎反馈此情况。谢谢。失败原因：编号{}的卡源数据文本格式错误。'.format(source_card_id))
            toplevel.destroy()
            return

    for source_card_info in source_card_desc_and_id:
        sql = 'INSERT INTO data VALUES ("{}", {}, "{}");'.format(source_card_info[0].replace('"', '""'), source_card_info[1], source_card_info[2].replace('"', '""'))
        try:
            cursor.execute(sql)
        except:
            pass
    con.commit()
    con.close()

    tk.messagebox.showinfo('更新源数据完成', '已更新源数据。')
    toplevel.destroy()

def update_target_command():
    ret = tk.messagebox.askquestion('更新目标数据', '''\
要更新目标数据吗？此过程需要访问网络，可能需要若干分钟。
数据来源：https://github.com/mycard/ygopro-database/raw/master/locales/zh-CN/cards.cdb
请参考：https://github.com/mycard/ygopro-database/

若要手动更新目标数据：请关闭MDCT后，下载最新版本的YGOPro，将其目录下的cards.cdb复制到MDCT目录下并更名为ygocore.cdb。\
''')
    if ret == 'no':
        return
    toplevel = tk.Toplevel()
    toplevel.title('更新目标数据')
    toplevel.geometry('300x200')
    toplevel.attributes('-topmost', True)
    toplevel.update()

    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=MDCT_Common.load_setting('font'))
    text.pack()

    text.insert(tk.INSERT, '''\
正在更新目标数据。本次更新可能需要若干分钟。
请耐心等待，不要关闭本界面。
若MDCT出现若干分钟的未响应，这是正常情况。
''')
    text.config(state=tk.DISABLED)
    toplevel.update()

    try:
        db = requests.get('https://github.com/mycard/ygopro-database/raw/master/locales/zh-CN/cards.cdb')
    except:
        tk.messagebox.showerror('更新目标数据失败', '''\
更新源数据时出现了一些问题。有可能是网络状况不佳。请检查网络状况后再次尝试。也可以手动更新目标数据。
若要手动更新目标数据：请关闭MDCT后，下载最新版本的YGOPro，将其目录下的cards.cdb复制到MDCT目录下并更名为ygocore.cdb。\
''')
        toplevel.destroy()
        return

    db_file = open('target.cdb', 'wb')
    db_file.write(db.content)
    db_file.close()

    try:
        os.replace('ygocore.cdb', 'ygocore.old.cdb')
    except:
        pass
    os.replace('target.cdb', 'ygocore.cdb')

    tk.messagebox.showinfo('更新目标数据完成', '已更新目标数据。')
    toplevel.destroy()