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
import sys
import subprocess
import webbrowser
import tkinter as tk
import tkinter.messagebox

import MDCT_Common
from MDCT_Common import get_setting
from MDCT_Common import set_setting

ROOT = None

def set_mode(v):
    set_setting('mode', v)

def set_duel_mode():
    set_mode(0)

def set_deck_mode():
    set_mode(1)

def update_source():
    ret = tk.messagebox.askquestion('更新源数据', '''\
要更新源数据吗？此过程需要访问网络，可能需要若干分钟。
数据来源：https://db.ygoprodeck.com/api/v7/cardinfo.php
请参考：https://db.ygoprodeck.com/api-guide/ \
''')
    if ret == 'no':
        return
    toplevel = tk.Toplevel()
    toplevel.title('更新源数据')
    toplevel.geometry('300x200')
    toplevel.attributes('-topmost', get_setting('topmost'))
    toplevel.update()

    text_common = '''\
正在更新源数据。可能需要若干分钟。
请耐心等待，不要关闭本界面。
若MDCT出现若干分钟的未响应，是正常情况。
'''
    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=get_setting('font'))
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
    cursor.execute('CREATE TABLE IF NOT EXISTS data (desc TEXT, id INTEGER, name TEXT, PRIMARY KEY (desc, id));')
    cursor.execute('DELETE FROM data;')

    source_card_desc_and_id = []

    for source_card_info in res:
        source_card_id = source_card_info[0]
        source_card_name = source_card_info[1]
        source_card_desc = (source_card_info[3] + '\r\n').replace('[ Pendulum Effect ]', '[Pendulum Effect]').replace('\r\n', '\n').replace('\n', ' ')
        source_card_desc_list = source_card_desc.split('---------------------------------------- ')
        if len(source_card_desc_list) == 2:
            source_card_desc = (source_card_desc_list[0] + source_card_desc_list[1]).replace('[ Monster Effect ]', ' ').replace('[ Flavor Text ]', ' ')
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            source_card_desc = (source_card_desc_list[1] + source_card_desc_list[0]).replace('[ Monster Effect ]', ' ').replace('[ Flavor Text ]', ' ')
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            continue
        source_card_desc_list = source_card_desc.split('[ Monster Effect ]')
        if len(source_card_desc_list) == 2:
            source_card_desc = (source_card_desc_list[0] + source_card_desc_list[1])
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            source_card_desc = (source_card_desc_list[1] + source_card_desc_list[0])
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            continue
        source_card_desc_list = source_card_desc.split('[ Flavor Text ]')
        if len(source_card_desc_list) == 2:
            source_card_desc = (source_card_desc_list[0] + source_card_desc_list[1])
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            source_card_desc = (source_card_desc_list[1] + source_card_desc_list[0])
            source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))
            continue
        source_card_desc_and_id.append((source_card_desc.replace(' ', ''), source_card_id, source_card_name))

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

def update_target():
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
    toplevel.attributes('-topmost', get_setting('topmost'))
    toplevel.update()

    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=get_setting('font'))
    text.pack()

    text.insert(tk.INSERT, '''\
正在更新目标数据。可能需要若干分钟。
请耐心等待，不要关闭本界面。
若MDCT出现若干分钟的未响应，是正常情况。
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

def change_topmost():
    set_setting('topmost', not get_setting('topmost'))
    ROOT.attributes('-topmost', get_setting('topmost'))
    ROOT.update()

def set_capture_method(v):
    set_setting('capture_method', v)

def set_capture_method_findwindow_printwindow():
    set_capture_method(MDCT_Common.CAPTURE_METHOD_FINDWINDOW_PRINTWINDOW)

def set_capture_method_findwindow_screenshot():
    set_capture_method(MDCT_Common.CAPTURE_METHOD_FINDWINDOW_SCREENSHOT)

def change_show_raw_text():
    set_setting('show_raw_text', not get_setting('show_raw_text'))

def change_pause():
    set_setting('pause', not get_setting('pause'))

def change_save_screenshots():
    set_setting('save_screenshots', not get_setting('save_screenshots'))

def view_help():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/wiki/Home-(Simplified-Chinese)')

def browse_new_issue():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/issues/new/choose')

def check_update():
    exec = sys.argv[0].split('\\')[-1]
    if exec != 'MasterDuelCardTranslator.exe':
        tk.messagebox.showerror('检查更新失败', '''\
似乎MDCT并不是以可执行文件的形式运行的。
如果这是使用源代码运行的，请使用git pull等方式更新源代码。
感谢理解与支持。\
''')
        return
    try:
        latest = requests.get('https://api.github.com/repos/Rehcramon/MasterDuelCardTranslator/releases/latest', headers={'Accept': 'application/vnd.github.v3+json'}).json()
    except:
        ret = tk.messagebox.askquestion('要查看最新版本页面吗？', '''\
检查更新失败。有可能是网络状况不佳。
点击“是”使用浏览器查看最新版本页面。点击“否”取消更新。\
''')
        if ret == 'yes':
            webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/releases/latest')
        return
    if latest['tag_name'] == 'v{}'.format(MDCT_Common.VERSION):
        tk.messagebox.showinfo('检查更新', '当前最新版本为v{}，无需更新。'.format(MDCT_Common.VERSION))
        return
    asset_name = 'MasterDuelCardTranslator_{}.zip'.format(latest['tag_name'])
    for asset in latest['assets']:
        if asset['name'].find('MDCT_Patch') != -1 and asset['name'].split('FROM')[1][1:-4] == MDCT_Common.VERSION:
            asset_name = asset['name']
            break
    asset_size = None
    asset_browser_download_url = None
    for asset in latest['assets']:
        if asset['name'] == asset_name:
            asset_size = asset['size']
            asset_browser_download_url = asset['browser_download_url']
            break
    if asset_size == None or asset_browser_download_url == None:
        tk.messagebox.showinfo('检查更新', '作者可能还在发布最新版本，请稍后重试。\n如果一直都是这种情况，希望能够反馈，谢谢。')
        return
    ret = tk.messagebox.askquestion('检查更新', '''\
当前最新版本为{}，需要更新吗？
点击“是”以下载并安装更新。点击“否”取消更新。
更新可能需要若干分钟，请耐心等待。

更新文档：
{}

即将下载的文件：{}
文件大小：约 {} MB\
'''.format(latest['tag_name'], latest['body'], asset_name, asset_size >> 20))
    if ret == 'no':
        return
    toplevel = tk.Toplevel()
    toplevel.title('正在更新MDCT')
    toplevel.geometry('300x200')
    toplevel.attributes('-topmost', get_setting('topmost'))
    toplevel.update()

    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=get_setting('font'))
    text.pack()

    text.insert(tk.INSERT, '''\
正在更新MDCT。可能需要若干分钟。
若MDCT出现若干分钟的未响应，是正常情况。
如果长时间未响应，则有可能是网络状况不佳，建议强行退出本界面后手动更新。

如果更新成功，MDCT将会重新启动。届时可能需要重新配置MDCT。\
''')
    text.config(state=tk.DISABLED)
    toplevel.update()

    try:
        patch = requests.get(asset_browser_download_url)
    except:
        ret = tk.messagebox.askquestion('要查看最新版本页面吗？', '''\
下载更新失败。有可能是网络状况不佳。
点击“是”使用浏览器查看最新版本页面。点击“否”取消更新。\
''')
        if ret == 'yes':
            webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/releases/latest')
        toplevel.destroy()
        return

    patch_file = open('patch.zip', 'wb')
    patch_file.write(patch.content)
    patch_file.close()
    toplevel.destroy()
    
    try:
        subprocess.run(['powershell', '.\MDCT_PatchInstaller.ps1'])
    except:
        tk.messagebox.showinfo('请手动更新', '似乎本机上没有安装Windows Powershell，故无法继续更新。\n请退出MDCT后，将目录下的patch.zip解压缩覆盖即可完成更新。')

def browse_github():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator')

def browse_rehcramon_github():
    webbrowser.open('https://github.com/Rehcramon')

def browse_rehcramon_bilibili():
    webbrowser.open('https://space.bilibili.com/4191644')

def browse_llforever_github():
    webbrowser.open('https://github.com/LLForever')

def about_messagebox():
    tk.messagebox.showinfo('关于 '+MDCT_Common.SHORT_TITLE, MDCT_Common.INFO)

def license_text():
    toplevel = tk.Toplevel(ROOT)
    toplevel.title('GNU General Public License v3.0')
    toplevel.geometry('650x700')
    toplevel.attributes('-topmost', get_setting('topmost'))
    text = tk.scrolledtext.ScrolledText(toplevel, width=10000, height=10000, font=get_setting('font'))
    text.pack()
    text.insert(tk.INSERT, MDCT_Common.LICENSE)
    text.config(state=tk.DISABLED)
    toplevel.update()
    toplevel.mainloop()