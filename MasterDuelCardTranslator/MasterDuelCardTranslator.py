import os
import time
import json
import sqlite3

import tkinter as tk

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

settings_file = open('settings.json', 'r')
settings = json.loads(settings_file.readline())
position = settings['position']

con = sqlite3.connect('name_and_id.db')
cursor = con.cursor()
cursor.execute('PRAGMA case_sensitive_like=ON;')

con1 = sqlite3.connect('ygocore.cdb')
cursor1 = con1.cursor()

root = tk.Tk()
root.title('MD Card Translator')
root.geometry('300x250')
root.resizable(False, True)
root.attributes('-topmost', True)
root.update()
card_detail = tk.Label(root, wraplength=290, justify=tk.LEFT, anchor='nw')
card_detail.pack()

cardname_buffer = ''
cardname_buffer_status = False

def update_card_detail():
    global cardname_buffer
    global cardname_buffer_status
    pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))
    cardname = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang='eng', config='--psm 7')[:-1].replace('"', '""')
    if len(cardname) >= 1:
        sql = 'SELECT id, name FROM data WHERE name = "{}"'.format(cardname)
        res = cursor.execute(sql).fetchall()
        if len(res) != 1 and len(cardname) >= 10:
            sql = 'SELECT id, name FROM data WHERE name LIKE "{}%"'.format(cardname[:-1])
            res = cursor.execute(sql).fetchall()
        if len(res) != 1 and len(cardname) >= 10:
            if cardname_buffer_status == True:
                cardname_overlap_status = True
                cardname_origin = cardname
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
                    sql = 'SELECT id, name FROM data WHERE name LIKE "{}%"'.format(cardname_buffer)
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
            sql1 = 'SELECT name, desc FROM texts WHERE id = {} LIMIT 1'.format(res[0][0])
            res1 = cursor1.execute(sql1).fetchall()
            if len(res1) == 1:
                card_detail.config(text='{} ({})\n\n{}'.format(res1[0][0], res[0][1], res1[0][1].replace('\r', '')))
    root.after(50, update_card_detail)

update_card_detail()
#quit_button = tk.Button(root, text='退出', command=root.destroy)
#quit_button.pack()

root.mainloop()
