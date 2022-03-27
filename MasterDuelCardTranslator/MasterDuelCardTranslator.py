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
from MDCT_ReplaceText import replace_text

try:
    con_cache = sqlite3.connect('cache.db')
    cursor_cache = con_cache.cursor()
    cursor_cache.execute('CREATE TABLE IF NOT EXISTS cache (hash TEXT PRIMARY KEY, txt TEXT);')
    con_cache.commit()
    con_cache.close()

    MDCT_Common.load_settings()

    root = tk.Tk()
    MDCT_UserInterface.ROOT = root
    root.title(MDCT_Common.SHORT_TITLE)
    root.attributes('-topmost', get_setting('topmost'))
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

    def font_plus():
        font_string_array = get_setting('font').split(' ')
        font_size = int(font_string_array[1])
        font_size += 2
        font_string_array[1] = str(font_size)
        font_string = ' '.join(font_string_array)
        set_setting('font', font_string)
        card_display_text.config(font=font_string)

    menu = tk.Menu(root)
    root.config(menu=menu)
    settings_menu = tk.Menu(menu, tearoff=0)
    help_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label='设置', menu=settings_menu)
    menu.add_cascade(label='帮助', menu=help_menu)
    menu.add_separator()
    menu.add_command(label='A-', command=font_minus)
    menu.add_command(label='A+', command=font_plus)

    mode_menu = tk.Menu(settings_menu, tearoff=0)
    advanced_settings_menu = tk.Menu(settings_menu, tearoff=0)
    settings_menu.add_cascade(label='当前模式', menu=mode_menu)
    settings_menu.add_separator()
    settings_menu.add_command(label='更新源数据', command=MDCT_UserInterface.update_source)
    settings_menu.add_command(label='更新目标数据', command=MDCT_UserInterface.update_target)
    settings_menu.add_separator()
    settings_menu.add_cascade(label='高级', menu=advanced_settings_menu)

    mode_menu_var = tk.StringVar(mode_menu)
    mode_menu_var.set(MDCT_Common.get_setting('mode'))
    mode_menu.add_radiobutton(label='决斗模式', var=mode_menu_var, value=MDCT_Common.MODE_DUEL, command=MDCT_UserInterface.set_duel_mode)
    mode_menu.add_radiobutton(label='组卡模式', var=mode_menu_var, value=MDCT_Common.MODE_DECK, command=MDCT_UserInterface.set_deck_mode)

    capture_method_menu = tk.Menu(advanced_settings_menu, tearoff=0)
    advanced_settings_menu_topmost_var = tk.IntVar(advanced_settings_menu)
    advanced_settings_menu_topmost_var.set(get_setting('topmost'))
    advanced_settings_menu_save_screenshots_var = tk.IntVar(advanced_settings_menu)
    advanced_settings_menu_save_screenshots_var.set(get_setting('save_screenshots'))
    advanced_settings_menu_raw_text_var = tk.IntVar(advanced_settings_menu)
    advanced_settings_menu_raw_text_var.set(get_setting('show_raw_text'))
    advanced_settings_menu_pause_var = tk.IntVar(advanced_settings_menu)
    advanced_settings_menu_pause_var.set(get_setting('pause'))
    advanced_settings_menu.add_checkbutton(label='置于顶层', var=advanced_settings_menu_topmost_var, command=MDCT_UserInterface.change_topmost)
    advanced_settings_menu.add_separator()
    advanced_settings_menu.add_cascade(label='捕获截图方法', menu=capture_method_menu)
    advanced_settings_menu.add_checkbutton(label='每次OCR都保存截图文件', var=advanced_settings_menu_save_screenshots_var, command=MDCT_UserInterface.change_save_screenshots)
    advanced_settings_menu.add_checkbutton(label='仅显示OCR结果', var=advanced_settings_menu_raw_text_var, command=MDCT_UserInterface.change_show_raw_text)
    advanced_settings_menu.add_checkbutton(label='暂停执行OCR及后续步骤', var=advanced_settings_menu_pause_var, command=MDCT_UserInterface.change_pause)
    advanced_settings_menu.add_separator()
    advanced_settings_menu.add_command(label='设定哈希时图片大小', command=MDCT_UserInterface.set_cache_hash_size)
    advanced_settings_menu.add_command(label='设定缓存中哈希值步进长度', command=MDCT_UserInterface.set_cache_hash_step)
    advanced_settings_menu.add_command(label='清空缓存', command=MDCT_UserInterface.clear_cache)

    capture_method_menu_var = tk.StringVar(capture_method_menu)
    capture_method_menu_var.set(get_setting('capture_method'))
    capture_method_menu_enable_zoom_var = tk.IntVar(capture_method_menu)
    capture_method_menu_enable_zoom_var.set(get_setting('enable_zoom'))
    capture_method_menu.add_radiobutton(
        label='识别并绘制窗口',
        var=capture_method_menu_var,
        value=MDCT_Common.CAPTURE_METHOD_FINDWINDOW_PRINTWINDOW,
        command=MDCT_UserInterface.set_capture_method_findwindow_printwindow
    )
    capture_method_menu.add_radiobutton(
        label='识别窗口后截图',
        var=capture_method_menu_var,
        value=MDCT_Common.CAPTURE_METHOD_FINDWINDOW_SCREENSHOT,
        command=MDCT_UserInterface.set_capture_method_findwindow_screenshot
    )
    capture_method_menu.add_radiobutton(
        label='截图后读取自定义区域',
        var=capture_method_menu_var,
        value=MDCT_Common.CAPTURE_METHOD_SCREENSHOT_CUSTOM,
        command=MDCT_UserInterface.set_capture_method_screenshot_custom
    )
    capture_method_menu.add_separator()
    capture_method_menu.add_checkbutton(label='自动缩放识别区域 *适用于"识别并绘制窗口"和"识别窗口后截图"', var=capture_method_menu_enable_zoom_var, command=MDCT_UserInterface.change_enable_zoom)
    capture_method_menu.add_command(label='自定义截图区域 *适用于"截图后读取自定义区域"', command=MDCT_UserInterface.configure_custom_position)

    author_menu = tk.Menu(help_menu, tearoff=0)
    help_menu.add_command(label='查看帮助', command=MDCT_UserInterface.view_help)
    help_menu.add_command(label='发送反馈', command=MDCT_UserInterface.browse_new_issue)
    help_menu.add_command(label='检查更新', command=MDCT_UserInterface.check_update)
    help_menu.add_separator()
    help_menu.add_command(label='MDCT项目首页', command=MDCT_UserInterface.browse_github)
    help_menu.add_cascade(label='联系作者', menu=author_menu)
    help_menu.add_separator()
    help_menu.add_command(label='关于 {}'.format(MDCT_Common.SHORT_TITLE), command=MDCT_UserInterface.about_messagebox)
    help_menu.add_command(label='许可证全文', command=MDCT_UserInterface.license_text)

    author_menu.add_command(label='Rehcramon@GitHub', command=MDCT_UserInterface.browse_rehcramon_github)
    author_menu.add_command(label='Rehcramon@bilibili', command=MDCT_UserInterface.browse_rehcramon_bilibili)
    author_menu.add_separator()
    author_menu.add_command(label='LLForever@GitHub', command=MDCT_UserInterface.browse_llforever_github)

    card_display_text = tk.scrolledtext.ScrolledText(root, width=1, height=1, font=get_setting('font'))
    CDPU.initUtil(card_display_text)
    CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '　　这是空白页。')

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

        con_cache = sqlite3.connect('cache.db')
        cursor_cache = con_cache.cursor()

        screenshot_result = MDCT_Common.get_screenshots_for_ocr()
        if screenshot_result[0] == MDCT_Common.RETURN_CODE_NO_WINDOW:
            if current_card_id != MDCT_Common.RETURN_CODE_NO_WINDOW:
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '　　未检测到标题为"masterduel"的窗口。')
                current_card_id = MDCT_Common.RETURN_CODE_NO_WINDOW
        elif screenshot_result[0] == MDCT_Common.RETURN_CODE_NO_WIDTH_HEIGHT:
            if current_card_id != MDCT_Common.RETURN_CODE_NO_WIDTH_HEIGHT:
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '　　虽然检测到了标题为"masterduel"的窗口，但是获取窗口大小失败。')
                current_card_id = MDCT_Common.RETURN_CODE_NO_WIDTH_HEIGHT
        elif screenshot_result[0] == MDCT_Common.RETURN_CODE_SCREENSHOT_FAIL:
            if current_card_id != MDCT_Common.RETURN_CODE_SCREENSHOT_FAIL:
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '　　截图失败。')
                current_card_id = MDCT_Common.RETURN_CODE_SCREENSHOT_FAIL
        else:
            if current_card_id == None or current_card_id < -1: # MDCT_Common.RETURN_CODE_NO_RESULT = -1
                CDPU.changeCardDetail(MDCT_Common.WELCOME_MESSAGE + '　　未能匹配到任何卡片。')
                current_card_id = MDCT_Common.RETURN_CODE_NO_RESULT
            screenshotImg = screenshot_result[2]
            
            imgMD5 = CDPU.dhash(screenshotImg).replace('"', '""').replace('\\', '\\\\')
            sql_cache = 'SELECT txt FROM cache WHERE hash = "{}"'.format(imgMD5)
            res_cache = cursor_cache.execute(sql_cache).fetchall()
            if len(res_cache) == 0:
                screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
                card_desc = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'))
                card_desc = replace_text(card_desc)
                card_desc = card_desc.replace(' ', '').replace('"', '""')
                sql_cache = 'INSERT INTO cache (hash, txt) VALUES ("{}", "{}")'.format(imgMD5, card_desc)
                cursor_cache.execute(sql_cache)
                con_cache.commit()
            else:
                card_desc = res_cache[0][0].replace('"', '""')

            if len(card_desc) >= 10:
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
                        
                        imgMD5 = CDPU.dhash(screenshotImg)
                        sql_cache = 'SELECT txt FROM cache WHERE hash = "{}"'.format(imgMD5)
                        res_cache = cursor_cache.execute(sql_cache).fetchall()
                        if len(res_cache) == 0:
                            screenshotInvertImg = ImageOps.invert(screenshotImg.convert('L'))
                            card_name = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'), config='--psm 7')[:-1]
                            card_name = replace_text(card_name)
                            sql_cache = 'INSERT INTO cache (hash, txt) VALUES ("{}", "{}")'.format(imgMD5, card_name.replace('"', '""'))
                            cursor_cache.execute(sql_cache)
                            con_cache.commit()
                        else:
                            card_name = res_cache[0][0].replace('"', '""')
                        if len(card_name) >= 3:
                            sql_source = 'SELECT id, name FROM data WHERE name = "{}"'.format(card_name.replace('"', '""'))
                            res = cursor_source.execute(sql_source).fetchall()
                            if len(res) != 1 and len(card_name) >= 10:
                                sql_source = 'SELECT id, name FROM data WHERE name LIKE "{}%"'.format(card_name[:-1].replace('"', '""'))
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
        con_cache.close()

    def get_card_raw_text():
        global current_card_id
        CDPU.setThreadStatus(True)
        current_card_id = None
        screenshot_result = MDCT_Common.get_screenshots_for_ocr()
        if screenshot_result[0] == MDCT_Common.RETURN_CODE_OK:
            screenshotInvertImg = ImageOps.invert(screenshot_result[1].convert('L'))
            card_name = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'), config='--psm 7')[:-1]
            card_name = replace_text(card_name)
            screenshotInvertImg = ImageOps.invert(screenshot_result[2].convert('L'))
            card_desc = pytesseract.image_to_string(screenshotInvertImg, lang=get_setting('source_language'))
            card_desc = replace_text(card_desc)
            raw_text = 'Name:\n{}\n\nText:\n{}'.format(card_name, card_desc)
        else:
            raw_text = 'RETURN CODE: {}'.format(screenshot_result[0])
        if raw_text != CDPU.getText():
            CDPU.changeCardDetail(raw_text)
        CDPU.setThreadStatus(False)

    def update_card_detail():
        if (not get_setting('pause')) and CDPU.openThread():
            if not get_setting('show_raw_text'):
                T = threading.Thread(target=getCardDetail)
            else:
                T = threading.Thread(target=get_card_raw_text)
            T.start()
        root.after(20, update_card_detail)

    update_card_detail()
    
    root.mainloop()

except Exception as e:
    exception_file = open('exception.txt', 'w')
    exception_file.write(traceback.format_exc())
    exception_file.close()
    raise