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

import os
import json
import traceback
import sqlite3
import tkinter as tk
import tkinter.scrolledtext
import threading

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common
import CardDetailProcessUtil as CDPU
import MDCT_TargetParser

try:

    try:
        settings_file = open('settings.json', 'r')
        settings = json.loads(settings_file.readline())
        settings_file.close()
        position = settings['position']
    except:
        pyautogui.alert('请先执行MDCT_PositionSetup，确保配置正确后再执行本程序。', MDCT_Common.SHORT_TITLE)
        raise

    root = tk.Tk()
    root.title(MDCT_Common.SHORT_TITLE)
    root.geometry(settings['geometry'])
    root.resizable(True, True)
    root.attributes('-topmost', True)
    root.update()

    def update_geometry(event):
        settings['geometry'] = root.geometry(None)
        settings_file = open('settings.json', 'w')
        settings_string = json.dumps(settings)
        settings_file.write(settings_string)
        settings_file.close()
    
    root.bind('<Configure>', update_geometry)
    CDPU.initUtil(tk.scrolledtext.ScrolledText(root, width=10000, height=10000, font=settings['font']))

    current_card_id = 0

    CDPU.setArgs(current_card_id)

    def getCardDetail():
        CDPU.setThreadStatus(True)

        con_source = sqlite3.connect('source.cdb')
        cursor_source = con_source.cursor()
        cursor_source.execute('PRAGMA case_sensitive_like=ON;')

        con = sqlite3.connect('search.db')
        cursor = con.cursor()

        con1 = sqlite3.connect('ygocore.cdb')
        cursor1 = con1.cursor()

        current_card_id = CDPU.getCurrent_card_id()

        pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))

        # add LRU Cache Before OCR. Improved performance in most scenarios
        screenshotImg = Image.open('screenshot.png')
        imgMD5 = CDPU.dhash(screenshotImg)
        imgCache = CDPU.getLRUCacheByKey(imgMD5)
        if (imgCache == None):
            screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
            card_desc = pytesseract.image_to_string(screenshotInvertImg, lang='eng')
            card_desc = card_desc.replace(' ', '').replace('"', '""')
        else:
            card_desc = imgCache

        if len(card_desc) >= 10:
            CDPU.putKeyValueInCache(CDPU.dhash(screenshotImg), card_desc)

            card_desc_work_list = card_desc.split('\n')
            card_desc_found = False
            card_desc_work_exchange_buffer = ''
            for i in range(len(card_desc_work_list)):
                card_desc_work = ''
                for card_desc_line in card_desc_work_list:
                    card_desc_work += card_desc_line
                    sql = 'SELECT id, name FROM data WHERE desc LIKE "{}%"'.format(card_desc_work)
                    res = cursor.execute(sql).fetchall()
                    if len(res) == 1:
                        if res[0][0] != current_card_id:
                            current_card_id = res[0][0]
                            sql1 = 'SELECT name, desc FROM texts WHERE id = {} LIMIT 1'.format(res[0][0])
                            res1 = cursor1.execute(sql1).fetchall()
                            if len(res1) == 1:
                                sql_target_data = 'SELECT id, ot, alias, setcode, type, atk, def, level, race, attribute, category FROM datas WHERE id = {} LIMIT 1'.format(res[0][0])
                                res_target_data = cursor1.execute(sql_target_data).fetchall()
                                card_data_string = MDCT_TargetParser.get_card_data_string(res_target_data[0])
                                CDPU.changeCardDetail(
                                    '{}\n{}\n{}\n{}'.format(res1[0][0], res[0][1], card_data_string, res1[0][1]))
                        card_desc_found = True
                        break
                if card_desc_found == True:
                    break
                elif i == 0:
                    pyautogui.screenshot('screenshot.png', region=(position['nx'], position['ny'], position['nw'], position['nh']))
                    # add LRU Cache Before OCR. Improved performance in most scenarios
                    screenshotImg = Image.open('screenshot.png')
                    imgMD5 = CDPU.dhash(screenshotImg)
                    imgCache = CDPU.getLRUCacheByKey(imgMD5)
                    if (imgCache == None):
                        screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
                        card_name = pytesseract.image_to_string(screenshotInvertImg, lang='eng', config='--psm 7')[:-1]
                    else:
                        card_name = imgCache
                    if len(card_name) >= 3:
                        sql_source = 'SELECT id, name FROM data WHERE name = "{}"'.format(card_name.replace('"', '""'))
                        res = cursor_source.execute(sql_source).fetchall()
                        if len(res) != 1 and len(card_name) >= 10:
                            sql_source = 'SELECT id, name FROM data WHERE name LIKE "%{}%"'.format(card_name[1:-1].replace('"', '""'))
                            res = cursor_source.execute(sql_source).fetchall()
                        if len(res) == 1:
                            if res[0][0] != current_card_id:
                                current_card_id = res[0][0]
                                sql1 = 'SELECT name, desc FROM texts WHERE id = {} LIMIT 1'.format(res[0][0])
                                res1 = cursor1.execute(sql1).fetchall()
                                if len(res1) == 1:
                                    sql_target_data = 'SELECT id, ot, alias, setcode, type, atk, def, level, race, attribute, category FROM datas WHERE id = {} LIMIT 1'.format(res[0][0])
                                    res_target_data = cursor1.execute(sql_target_data).fetchall()
                                    card_data_string = MDCT_TargetParser.get_card_data_string(res_target_data[0])
                                    CDPU.changeCardDetail(
                                        '{}\n{}\n{}\n{}'.format(res1[0][0], res[0][1], card_data_string, res1[0][1]))
                            break
                if i > 0:
                    card_desc_work_list[i - 1] = card_desc_work_exchange_buffer
                card_desc_work_exchange_buffer = card_desc_work_list[i]
                card_desc_work_list[i] = '%'
        CDPU.setThreadStatus(False)
        CDPU.setArgs(current_card_id)
        con_source.close()
        con.close()
        con1.close()

    def update_card_detail():
        if(CDPU.openThread()):
            T = threading.Thread(target=getCardDetail)
            T.start()

        root.after(180, update_card_detail)
    update_card_detail()

    root.mainloop()

except Exception as e:
    exception_file = open('exception.txt', 'w')
    exception_file.write(traceback.format_exc())
    exception_file.close()
    raise