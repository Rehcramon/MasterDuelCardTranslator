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

import json

import win32gui
import win32ui
from ctypes import windll
from PIL import Image

VERSION = '2.0'

SHORT_TITLE = 'MDCT v{}'.format(VERSION)

INFO = '''\
    Master Duel Card Translator Project
    Copyright (C) 2022  Rehcramon and LLForever

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to
    redistribute it under certain conditions.
    See the GNU General Public License for more details.

    Version {}
    https://github.com/Rehcramon/MasterDuelCardTranslator \
'''.format(VERSION)

WELCOME_MESSAGE = '''\

　　欢迎使用Master Duel Card Translator。
\
'''

SETTINGS = None

def load_settings(filename = 'settings.json'):
    global SETTINGS
    settings_file = open(filename, 'r')
    SETTINGS = json.loads(' '.join(settings_file.readlines()))
    settings_file.close()

def get_setting(key):
    return SETTINGS[key]

def set_setting(key, value):
    SETTINGS[key] = value

def save_settings():
    settings_file = open('settings.json', 'w')
    settings_file.write(json.dumps(SETTINGS))
    settings_file.close()

# https://stackoverflow.com/questions/19695214/screenshot-of-inactive-window-printwindow-win32gui
# code by hazzey
def get_screenshot(window_title):
    ret = (False, None)
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        return ret
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    w = right - left
    h = bot - top
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
    if result == 1:
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        ret = (True, {'screenshot': im, 'w': w, 'h': h})
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    return ret

def get_screenshots_for_ocr():
    ret = get_screenshot('masterduel')
    if ret[0] == False:
        return (False, None, None)
    # Duel Mode
    mode = get_setting('mode')
    if mode == 0:
        name_image = ret[1]['screenshot'].crop((
            round(40 / 1920 * ret[1]['w']),
            round(150 / 1080 * ret[1]['h']),
            round(348 / 1920 * ret[1]['w']),
            round(190 / 1080 * ret[1]['h'])
        ))
        text_image = ret[1]['screenshot'].crop((
            round(30 / 1920 * ret[1]['w']),
            round(501 / 1080 * ret[1]['h']),
            round(385 / 1920 * ret[1]['w']),
            round(851 / 1080 * ret[1]['h'])
        ))
    # Deck Mode
    if mode == 1:
        name_image = ret[1]['screenshot'].crop((
            round(58 / 1920 * ret[1]['w']),
            round(120 / 1080 * ret[1]['h']),
            round(404 / 1920 * ret[1]['w']),
            round(160 / 1080 * ret[1]['h'])
        ))
        text_image = ret[1]['screenshot'].crop((
            round(54 / 1920 * ret[1]['w']),
            round(465 / 1080 * ret[1]['h']),
            round(442 / 1920 * ret[1]['w']),
            round(758 / 1080 * ret[1]['h'])
        ))
    return (True, name_image, text_image)