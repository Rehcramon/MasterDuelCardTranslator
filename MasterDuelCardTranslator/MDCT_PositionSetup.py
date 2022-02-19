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

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common
from MDCT_CorrectRecognitionResult import correct_recognition_result

MDCT_Common.print_info()

settings_file = open('settings.json', 'r')
settings = json.loads(settings_file.readline())
settings_file.close()

welcome_message = '''
欢迎使用Master Duel Card Translator。
现在正在选择所需要识别的文本区域。请按照以下步骤完成。
1. 确保Yu-Gi-Oh! Master Duel所显示的语言是英语；
2. 启动Yu-Gi-Oh! Master Duel，进入单人模式（Solo）的任意决斗，之后选择一张卡片，让屏幕左侧出现卡片的信息；
3. 回到本界面，并将本界面移动到不会遮挡到卡片文本的位置，准备好之后按下回车；
4. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车；
5. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车；
6. 将鼠标移动到卡片文本的文字区域的左上角（大约在第一个字符左上角的位置），按下回车；
7. 将鼠标移动到卡片文本的文字区域的右下角（大约在灰色三角形左下角的位置），按下回车。

请务必注意，本次配置之中需要按下5次回车，需要移动4次鼠标到特定的位置。
它们的顺序是：按下回车、移动鼠标、按下回车、移动鼠标、按下回车、移动鼠标、按下回车、移动鼠标、按下回车。
'''

print(welcome_message)

input('如果已经完成了第1-3步，准备好进行第4-7步，请按下回车。')
input('正在进行 4. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车。')
left_top_pos = pyautogui.position()
input('正在进行 5. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车。')
right_bottom_pos = pyautogui.position()

width = right_bottom_pos[0] - left_top_pos[0]
height = right_bottom_pos[1] - left_top_pos[1]

if width <= 0 or height <= 0:
    print('选择的区域不是合法的矩形。')
    input('选择区域失败，请关闭并重启本程序。')
    raise Exception('Invalid area.')

nx = left_top_pos[0]
ny = left_top_pos[1]
nw = width
nh = height

pyautogui.screenshot('screenshot.png', region=(nx, ny, nw, nh))
card_name = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang=settings['source_language'], config='--psm 7')[:-1]
card_name = correct_recognition_result(card_name)

print('\n当前所识别的卡名为“{}”。'.format(card_name))
print('如果卡名基本正确，请继续进行第6-7步。')
print('如果卡名不正确，请重启本程序重新配置。\n')

input('正在进行 6. 将鼠标移动到卡片文本的文字区域的左上角（大约在第一个字符左上角的位置），按下回车。')
left_top_pos = pyautogui.position()
input('正在进行 7. 将鼠标移动到卡片文本的文字区域的右下角（大约在灰色三角形左下角的位置），按下回车。')
right_bottom_pos = pyautogui.position()

width = right_bottom_pos[0] - left_top_pos[0]
height = right_bottom_pos[1] - left_top_pos[1]

if width <= 0 or height <= 0:
    print('选择的区域不是合法的矩形。')
    input('选择区域失败，请关闭并重启本程序。')
    raise Exception('Invalid area.')

position = {
    'x': left_top_pos[0],
    'y': left_top_pos[1],
    'w': width,
    'h': height,
    'nx': nx,
    'ny': ny,
    'nw': nw,
    'nh': nh
}

settings['position'] = position
settings['geometry'] = '300x500+{}+{}'.format(max(position['x'] + position['w'], position['nx'] + position['nw']) + 20, position['ny'])

MDCT_Common.save_settings(settings)

pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))
card_desc = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang=settings['source_language'])
card_desc = correct_recognition_result(card_desc)

print('\n\n当前所识别的卡片文本为：\n{}\n'.format(card_desc))
print('如果文本除了最后一行均正确，建议关闭本程序后启动Master Duel Card Translator以查看效果。')
print('如果文本除了最后一行之外，有着不正确的情况，请重启本程序重新配置。')

input('\n请关闭本程序。谢谢。')