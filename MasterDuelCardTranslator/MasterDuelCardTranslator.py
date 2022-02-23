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

import os
import os.path
import json
import traceback
import sqlite3
import tkinter as tk
import tkinter.scrolledtext
import tkinter.messagebox
import threading

from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common
from MDCT_Common import get_setting
from MDCT_Common import set_setting
import MDCT_UserInterface
import MDCT_CardDetailProcessUtil as CDPU
import MDCT_TargetParser
from MDCT_CorrectRecognitionResult import correct_recognition_result

try:

    try:
        MDCT_Common.load_settings()
    except:
        MDCT_Common.load_settings('_settings.json')
        MDCT_Common.save_settings()

    root = tk.Tk()
    root.title(MDCT_Common.SHORT_TITLE)
    root.attributes('-topmost', True)
    root.resizable(True, True)
    root.geometry(get_setting('geometry'))
    root.update()

    if (not os.path.isfile('source.cdb')) or (not os.path.isfile('search.db')):
        MDCT_UserInterface.update_source()
        if (not os.path.isfile('source.cdb')) or (not os.path.isfile('search.db')):
            raise Exception('No source database.')
    if not os.path.isfile('ygocore.cdb'):
        MDCT_UserInterface.update_target()
        if not os.path.isfile('ygocore.cdb'):
            raise Exception('No target database.')

    def update_geometry(event):
        set_setting('geometry', root.geometry(None))
        MDCT_Common.save_settings()
    
    root.bind('<Configure>', update_geometry)

    def font_minus():
        font_string_array = get_setting('font').split(' ')
        font_size = int(font_string_array[1])
        if font_size <= 2:
            return
        font_size -= 2
        font_string_array[1] = str(font_size)
        font_string = ' '.join(font_string_array)
        set_setting('font', font_string)
        card_display_text.config(font=font_string)
        MDCT_Common.save_settings()

    def font_plus():
        font_string_array = get_setting('font').split(' ')
        font_size = int(font_string_array[1])
        font_size += 2
        font_string_array[1] = str(font_size)
        font_string = ' '.join(font_string_array)
        set_setting('font', font_string)
        card_display_text.config(font=font_string)
        MDCT_Common.save_settings()

    menu = tk.Menu(root)
    root.config(menu=menu)
    settings_menu = tk.Menu(menu, tearoff=0)
    help_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label='设置', menu=settings_menu)
    menu.add_cascade(label='帮助', menu=help_menu)
    menu.add_separator()
    menu.add_command(label='A-', command=font_minus)
    menu.add_command(label='A+', command=font_plus)

    settings_menu.add_command(label='更新源数据', command=MDCT_UserInterface.update_source)
    settings_menu.add_command(label='更新目标数据', command=MDCT_UserInterface.update_target)

    author_menu = tk.Menu(help_menu, tearoff=0)
    help_menu.add_command(label='查看帮助', command=MDCT_UserInterface.view_help)
    help_menu.add_command(label='发送反馈', command=MDCT_UserInterface.browse_new_issue)
    help_menu.add_command(label='检查更新', command=MDCT_UserInterface.check_update)
    help_menu.add_separator()
    help_menu.add_command(label='MDCT项目首页', command=MDCT_UserInterface.browse_github)
    help_menu.add_cascade(label='联系作者', menu=author_menu)
    help_menu.add_separator()
    help_menu.add_command(label='关于 {}'.format(MDCT_Common.SHORT_TITLE), command=MDCT_UserInterface.about_messagebox)

    author_menu.add_command(label='Rehcramon@GitHub', command=MDCT_UserInterface.browse_rehcramon_github)
    author_menu.add_command(label='Rehcramon@bilibili', command=MDCT_UserInterface.browse_rehcramon_bilibili)
    author_menu.add_separator()
    author_menu.add_command(label='LLForever@GitHub', command=MDCT_UserInterface.browse_llforever_github)

    card_display_text = tk.scrolledtext.ScrolledText(root, width=1, height=1, font=get_setting('font'))
    CDPU.initUtil(card_display_text)

    current_card_id = None

    def getCardDetail():
        global current_card_id
        CDPU.setThreadStatus(True)

        con_source = sqlite3.connect('source.cdb')
        cursor_source = con_source.cursor()
        cursor_source.execute('PRAGMA case_sensitive_like=ON;')

        con = sqlite3.connect('search.db')
        cursor = con.cursor()

        con1 = sqlite3.connect('ygocore.cdb')
        cursor1 = con1.cursor()

        screenshot_result = MDCT_Common.get_screenshots_for_ocr()
        if screenshot_result[0] == False:
            if current_card_id != -2:
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '\n　　未检测到标题为“masterduel”的窗口。请启动Yu-Gi-Oh! Master Duel。')
                current_card_id = -2
        else:
            if current_card_id == None or current_card_id == -2:
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '\n　　未能匹配到任何卡片。')
                current_card_id = -1
            screenshotImg = screenshot_result[2]
            # add LRU Cache Before OCR. Improved performance in most scenarios
            imgMD5 = CDPU.dhash(screenshotImg)
            imgCache = CDPU.getLRUCacheByKey(imgMD5)
            if (imgCache == None):
                screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
                card_desc = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'))
                card_desc = correct_recognition_result(card_desc)
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
                        screenshotImg = screenshot_result[1]
                        # add LRU Cache Before OCR. Improved performance in most scenarios
                        imgMD5 = CDPU.dhash(screenshotImg)
                        imgCache = CDPU.getLRUCacheByKey(imgMD5)
                        if (imgCache == None):
                            screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
                            card_name = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'), config='--psm 7')[:-1]
                            card_name = correct_recognition_result(card_name)
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