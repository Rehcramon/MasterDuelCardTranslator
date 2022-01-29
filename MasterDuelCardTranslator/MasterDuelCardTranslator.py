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
import time

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common
import CardDetailProcessUtil as CDPU

try:

    try:
        settings_file = open('settings.json', 'r')
        settings = json.loads(settings_file.readline())
        settings_file.close()
        position = settings['position']
    except:
        pyautogui.alert('请先执行MDCT_PositionSetup，确保配置正确后再执行本程序。', MDCT_Common.SHORT_TITLE)
        raise

    # con = sqlite3.connect('name_and_id.db')
    # cursor = con.cursor()
    # cursor.execute('PRAGMA case_sensitive_like=ON;')
    #
    # con1 = sqlite3.connect('ygocore.cdb')
    # cursor1 = con1.cursor()

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

    # card_detail = tk.scrolledtext.ScrolledText(root, width=10000, height=10000, font=settings['font'])
    # card_detail.insert(tk.INSERT, '''
    #     未能匹配到任何卡名。
    #     请确保卡名区域没有被遮挡。尤其是本界面不能遮挡住卡名区域，请先将本界面移动到屏幕右下角。
    #     如果长时间仍无法匹配，可尝试关闭本程序后重新执行MDCT_PositionSetup进行配置。请务必注意配置完成时应能够识别正确的卡名。''')
    # card_detail.config(state=tk.DISABLED)
    # card_detail.pack()

    cardname_buffer = ''
    cardname_buffer_status = False
    current_card_id = 0

    CDPU.setArgs(cardname_buffer, cardname_buffer_status, current_card_id)

    def getCardDetail():
        CDPU.setThreadStatus(True)

        con = sqlite3.connect('name_and_id.db')
        cursor = con.cursor()
        cursor.execute('PRAGMA case_sensitive_like=ON;')

        con1 = sqlite3.connect('ygocore.cdb')
        cursor1 = con1.cursor()

        cardname_buffer = CDPU.getCardname_buffer()
        cardname_buffer_status = CDPU.getCardname_buffer_status()
        current_card_id = CDPU.getCurrent_card_id()

        pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))

        # add LRU Cache Before OCR. Improved performance in most scenarios
        screenshotImg = Image.open('screenshot.png')
        screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
        imgMD5 = CDPU.dhash(screenshotImg)
        imgCache = CDPU.getLRUCacheByKey(imgMD5)
        if (imgCache == None):
            cardname = pytesseract.image_to_string(screenshotInvertImg, lang='eng', config='--psm 7')[:-1]
        else:
            cardname = imgCache

        cardname_origin = cardname
        # start to execute SQL
        if len(cardname) >= 1:
            sql = 'SELECT id, name FROM data WHERE name = "{}"'.format(cardname.replace('"', '""'))
            res = cursor.execute(sql).fetchall()
            if len(res) != 1 and len(cardname) >= 10:
                CDPU.putKeyValueInCache(CDPU.dhash(screenshotImg), cardname_origin)
                sql = 'SELECT id, name FROM data WHERE name LIKE "{}%"'.format(cardname[:-1].replace('"', '""'))
                res = cursor.execute(sql).fetchall()
            if len(res) != 1 and len(cardname) >= 10:
                CDPU.putKeyValueInCache(CDPU.dhash(screenshotImg), cardname_origin)
                if cardname_buffer_status == True:
                    cardname_overlap_status = True
                    cardname = cardname[1:-1]
                    for i in range(0, len(cardname_buffer) - 5):
                        cardname_overlap_status = True
                        j = 0
                        while i + j < len(cardname_buffer) and j < len(cardname):
                            if cardname_buffer[i + j] == cardname[j]:
                                j += 1
                            else:
                                cardname_overlap_status = False
                                break
                        if cardname_overlap_status == True and j < len(cardname):
                            cardname_buffer = cardname_buffer + cardname[j:]
                            break
                    if cardname_overlap_status == True:
                        sql = 'SELECT id, name FROM data WHERE name LIKE "{}%"'.format(
                            cardname_buffer.replace('"', '""'))
                        res = cursor.execute(sql).fetchall()
                    else:
                        cardname_buffer = cardname_origin[:-1]
                        cardname_buffer_status = True
                else:
                    cardname_buffer = cardname[:-1]
                    cardname_buffer_status = True
            if len(res) == 1:
                cardname_buffer = ''
                cardname_buffer_status = False
                if current_card_id != res[0][0]:
                    current_card_id = res[0][0]
                    sql1 = 'SELECT name, desc FROM texts WHERE id = {} LIMIT 1'.format(res[0][0])
                    res1 = cursor1.execute(sql1).fetchall()
                    if len(res1) == 1:
                        CDPU.changeCardDetail(
                            '{} ({})\n\n{}'.format(res1[0][0], res[0][1], res1[0][1].replace('\r', '')))
                        CDPU.putKeyValueInCache(CDPU.dhash(screenshotImg), cardname_origin)
        CDPU.setThreadStatus(False)
        CDPU.setArgs(cardname_buffer, cardname_buffer_status, current_card_id)
        con.close()
        con1.close()

    def update_card_detail():
        # global cardname_buffer
        # global cardname_buffer_status
        # global current_card_id

        if(CDPU.openThread()):
            T = threading.Thread(target=getCardDetail)
            # T.setDaemon(True)
            T.start()

        root.after(180, update_card_detail)
    update_card_detail()
    #quit_button = tk.Button(root, text='退出', command=root.destroy)
    #quit_button.pack()

    root.mainloop()

except Exception as e:
    exception_file = open('exception.txt', 'w')
    exception_file.write(traceback.format_exc())
    exception_file.close()
    raise