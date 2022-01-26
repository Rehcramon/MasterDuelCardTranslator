#    Master Duel Card Translator Project
#    Copyright (C) 2022  Rehcramon
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
1. 确保Yu-Gi-Oh! Master Duel所显示的语言是英语，并且是以窗口模式运行；
2. 启动Yu-Gi-Oh! Master Duel，进入单人模式（Solo）的任意决斗，之后任意选择一张卡片，让屏幕左侧出现卡片的信息；
3. 回到本界面，并将本界面移动到不会遮挡到卡片名称的位置，准备好之后按下回车；
4. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车；
5. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车。

请务必注意，本次配置之中需要按下3次回车，需要移动2次鼠标到特定的位置。
它们的顺序是：按下回车、移动鼠标、按下回车、移动鼠标、按下回车。
'''

print(welcome_message)

input('如果已经完成了第1~3步，准备好进行第4~5步，请按下回车。')
input('正在进行 4. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车。')
left_top_pos = pyautogui.position()
input('正在进行 5. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车。')
right_bottom_pos = pyautogui.position()

width = right_bottom_pos[0] - left_top_pos[0]
height = right_bottom_pos[1] - left_top_pos[1]

if width <= 0 or height <= 0:
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
settings['position'] = position
settings['geometry'] = '300x250+{}+{}'.format(position['x'], position['y'] + position['h'] + 20)

settings_string = json.dumps(settings)

settings_file = open('settings.json', 'w')
settings_file.write(settings_string)
settings_file.close()

pyautogui.screenshot('screenshot.png', region=(position['x'], position['y'], position['w'], position['h']))
cardname = pytesseract.image_to_string(ImageOps.invert(Image.open('screenshot.png').convert('L')), lang='eng', config='--psm 7')[:-1]

print('\n\n当前所识别的卡名为“{}”。'.format(cardname))
print('如果卡名正确（如果卡名只有第1个字符和/或最后1个字符不正确，也可认为是正确的），建议关闭本程序后启动Master Duel Card Translator以查看效果。')
print('如果卡名不正确，请重启本程序重新配置。')
print('\n如果一直都无法配置成功，请记录下({}, {})与({}, {})这两个数据，连同MDCT文件夹中screenshot.png图片一起反馈。\n'.format(
    left_top_pos[0], left_top_pos[1], right_bottom_pos[0], right_bottom_pos[1]))

input('请关闭本程序。谢谢。')