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
import webbrowser
import tkinter as tk
import tkinter.messagebox

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common
from MDCT_Common import get_setting
from MDCT_Common import set_setting
from MDCT_CorrectRecognitionResult import correct_recognition_result

def setup_position():
    ret = tk.messagebox.askquestion('配置文字区域 ({})'.format(MDCT_Common.SHORT_TITLE), '''\
　　是要重新配置MDCT所识别的文字区域吗？如果是，则请仔细阅读以下信息。

　　欢迎使用Master Duel Card Translator。
　　MDCT的原理是读取屏幕截图之后，根据卡名区域和卡片文本区域的图片转文字结果来进行卡片的匹配与翻译。因此，在配置与使用的过程中请务必保证不要遮挡这两个区域。如果现在或之后有任何界面遮挡住了这两个区域，请立即将它们移开。

　　在点击“是”之后，会依次跳出4个对话框。请依次将鼠标移动到对话框中所要求的位置后按下回车。这是为了配置截图的区域，需要记录卡名左上角、卡名右下角、卡片文本左上角和卡片文本右下角这4个点。MDCT根据这4个点来定位卡名和卡片文本的位置。
　　这个过程中，请尽量不要用鼠标点击任何位置，除非是移动对话框或者是让对话框回到最前。
　　请再次注意，不要点击这4个对话框的“确认”按钮。“确认”按钮应在鼠标移动到对话框要求的位置后通过回车键触发。

　　在这4个对话框之后，会有最后1个对话框展示当前识别的文字。请确认是否正确。

　　如果已经准备好了配置，请启动Yu-Gi-Oh! Master Duel，将语言修改为English，进入SOLO或DUEL LIVE*的任意一场决斗，点击任意一张卡片，让屏幕左侧出现卡片的信息。之后点击“是”继续。

* 可能需要暂停播放DUEL LIVE。
''')
    if ret == 'no':
        return

    tk.messagebox.showinfo('配置文字区域 1/4', '1. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车。')
    left_top_pos = pyautogui.position()
    tk.messagebox.showinfo('配置文字区域 2/4', '2. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车。')
    right_bottom_pos = pyautogui.position()
    width = right_bottom_pos[0] - left_top_pos[0]
    height = right_bottom_pos[1] - left_top_pos[1]
    if width <= 0 or height <= 0:
        tk.messagebox.showerror('配置文字区域失败', '选择的区域不是合法的矩形。请重新配置。')
        return
    nx = left_top_pos[0]
    ny = left_top_pos[1]
    nw = width
    nh = height

    tk.messagebox.showinfo('配置文字区域 3/4', '3. 将鼠标移动到卡片文本的文字区域的左上角（大约在第一个字符左上角稍偏左上的位置），按下回车。')
    left_top_pos = pyautogui.position()
    tk.messagebox.showinfo('配置文字区域 4/4', '4. 将鼠标移动到卡片文本的文字区域的右下角（大约在灰色三角形左下角稍偏上的位置），按下回车。')
    right_bottom_pos = pyautogui.position()
    width = right_bottom_pos[0] - left_top_pos[0]
    height = right_bottom_pos[1] - left_top_pos[1]
    if width <= 0 or height <= 0:
        tk.messagebox.showerror('配置文字区域失败', '选择的区域不是合法的矩形。请重新配置。')
        return
    tx = left_top_pos[0]
    ty = left_top_pos[1]
    tw = width
    th = height

    card_name_screenshot = pyautogui.screenshot(region=(nx, ny, nw, nh))
    card_name = pytesseract.image_to_string(ImageOps.invert(card_name_screenshot.convert('L')), lang=get_setting('source_language'), config='--psm 7')[:-1]
    card_name = correct_recognition_result(card_name)

    card_desc_screenshot = pyautogui.screenshot(region=(tx, ty, tw, th))
    card_desc = pytesseract.image_to_string(ImageOps.invert(card_desc_screenshot.convert('L')), lang=get_setting('source_language'))[:-1]
    card_desc = correct_recognition_result(card_desc)

    ret = tk.messagebox.askquestion('请确认配置结果', '''\
当前识别结果的卡片名称为：
{}
当前识别结果的卡片文本为：
{}

如果基本正确，请点击“是”以保存修改。
如果不太正确，请点击“否”以取消修改。\
'''.format(card_name, card_desc))
    if ret == 'no':
        return

    position = {
        'nx': nx,
        'ny': ny,
        'nw': nw,
        'nh': nh,
        'tx': tx,
        'ty': ty,
        'tw': tw,
        'th': th
    }
    set_setting('position', position)
    set_setting('geometry', '300x500+{}+{}'.format(max(position['tx'] + position['tw'], position['nx'] + position['nw']) + 20, position['ny']))
    MDCT_Common.save_settings()

def update_source():
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
    toplevel.attributes('-topmost', True)
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

def browse_latest_release():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/releases/latest')

def browse_new_issue():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator/issues/new/choose')

def browse_github():
    webbrowser.open('https://github.com/Rehcramon/MasterDuelCardTranslator')

def browse_bilibili():
    webbrowser.open('https://space.bilibili.com/4191644')

def about_messagebox():
    tk.messagebox.showinfo('关于 '+MDCT_Common.SHORT_TITLE, MDCT_Common.INFO)