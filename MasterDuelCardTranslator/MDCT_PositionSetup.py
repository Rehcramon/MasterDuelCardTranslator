import json

import pyautogui

import MDCT_Common

MDCT_Common.print_info()

welcome_message = '''
欢迎使用Master Duel Card Translator。
现在正在选择所需要识别的文本区域。请按照以下步骤完成。
1. 确保Yu-Gi-Oh! Master Duel所显示的语言是英语，并且是以窗口模式运行；
2. 启动Yu-Gi-Oh! Master Duel，进入单人模式（Solo）的任意决斗，之后任意选择一张卡片，让屏幕左侧出现卡片的信息；
3. 回到本界面，并将本界面移动到不会遮挡到卡片名称的位置；
4. 将鼠标移动到卡片名称的文字区域的左上角（大约在灰色三角形右下方稍偏上的位置），按下回车；
5. 将鼠标移动到卡片名称的文字区域的右下角（大约在属性的左下方稍偏左上的位置），按下回车。


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

settings = {
    'position': {
        'x': left_top_pos[0],
        'y': left_top_pos[1],
        'w': width,
        'h': height
    }
}

settings_string = json.dumps(settings)

settings_file = open('settings.json', 'w')
settings_file.write(settings_string)
settings_file.close()

print('Done.')

print('目前所选择的区域是({}, {})与({}, {})之间的位置。'.format(left_top_pos[0], left_top_pos[1], right_bottom_pos[0], right_bottom_pos[1]))

input('请关闭本程序。建议启动Master Duel Card Translator以查看效果。')