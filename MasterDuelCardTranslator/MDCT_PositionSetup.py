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

import json

import pyautogui
from PIL import Image
from PIL import ImageOps
import pytesseract

import MDCT_Common

MDCT_Common.print_info()

welcome_message = '''
欢迎使用Master Duel Card Translator。
现在正在选择所需要识别的文本区域。请按照以下步骤完成。
1. 确保Yu-Gi-Oh! Master Duel所显示的语言是英语，文本大小不要是最小(Small)*；
2. 启动Yu-Gi-Oh! Master Duel，进入单人模式（Solo）的任意决斗，之后选择一张卡片**，让屏幕左侧出现卡片的信息；
3. 回到本界面，并将本界面移动到不会遮挡到卡片文本的位置，准备好之后按下回车；
4. 将鼠标移动到卡片文本的文字区域的左上角（第一个字符左上角即可），按下回车；
5. 将鼠标移动到卡片文本的文字区域的右下角（请定位在滚动栏左侧区域），按下回车。

* 最小的文本大小在实验中出现了识别失败的情况，请尽量使用中等(Medium)或最大(Large)进行游戏。
** 请尽量选择一张卡片本文较长的卡片，从而让游戏内的滚动栏显示出来。

请务必注意，本次配置之中需要按下3次回车，需要移动2次鼠标到特定的位置。
它们的顺序是：按下回车、移动鼠标、按下回车、移动鼠标、按下回车。
'''

print(welcome_message)

input('如果已经完成了第1~3步，准备好进行第4~5步，请按下回车。')
input('正在进行 4. 将鼠标移动到卡片文本的文字区域的左上角（第一个字符左上角即可），按下回车。')
left_top_pos = pyautogui.position()
input('正在进行 5. 将鼠标移动到卡片文本的文字区域的右下角（请定位在滚动栏左侧区域），按下回车。')
right_bottom_pos = pyautogui.position()

width = right_bottom_pos[0] - left_top_pos[0]
height = right_bottom_pos[1] - left_top_pos[1]

if width <= 0 or height <= 0:
    print('选择的区域不是合法的矩形。')
    input('选择区域失败，请关闭并重启本程序。')
    quit()

position = {
    'x': left_top_pos[0],
    'y': left_top_pos[1],
    'w': width,
    'h': height
}

settings_file = open('settings.json', 'r')
settings = json.loads(settings_file.readline())
settings_file.close()
settings['position'] = position
settings['geometry'] = '300x250+{}+{}'.format(position['x'] + position['w'] + 20, position['y'])

settings_string = json.dumps(settings)

settings_file = open('settings.json', 'w')
settings_file.write(settings_string)
settings_file.close()

pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))
cardname = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang='eng')

print('\n\n当前所识别的卡片文本为：\n{}\n'.format(cardname))
print('如果文本除了最后一行均正确，建议关闭本程序后启动Master Duel Card Translator以查看效果。')
print('如果文本除了最后一行之外，有着不正确的情况，请重启本程序重新配置。')
print('\n如果一直都无法配置成功，请使用MDCT文件夹中screenshot.png图片进行反馈。')
print('反馈地址：https://github.com/Rehcramon/MasterDuelCardTranslator/issues')

input('\n请关闭本程序。谢谢。')