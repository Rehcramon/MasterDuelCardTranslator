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

last_cardname = ''

def update_card_detail():
    global last_cardname
    pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))
    cardname = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang='eng', config='--psm 7')[0:-1].replace('"', '""')
    if last_cardname != cardname:
        sql = 'SELECT id, name FROM data WHERE name LIKE "{}%" LIMIT 1'.format(cardname)
        res = cursor.execute(sql).fetchall()
        if len(res) == 0:
            sql = 'SELECT id, name FROM data WHERE name LIKE "%{}" LIMIT 1'.format(cardname)
            res = cursor.execute(sql).fetchall()
        if len(res) == 1 and (cardname == res[0][1] or len(cardname) >= 8):
            sql = 'SELECT name, desc FROM texts WHERE id = {} LIMIT 1'.format(res[0][0])
            res = cursor1.execute(sql).fetchall()
            if len(res) == 1:
                card_detail.config(text='{} ({})\n\n{}\n\n\n*本软件还处于开发阶段'.format(res[0][0], cardname, res[0][1].replace('\r', '')))
                last_cardname = cardname
    root.after(50, update_card_detail)

update_card_detail()
#quit_button = tk.Button(root, text='退出', command=root.destroy)
#quit_button.pack()

root.mainloop()
