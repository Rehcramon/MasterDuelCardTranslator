import json

import pyautogui

input('左上角')
left_top_pos = pyautogui.position()
input('右下角')
right_bottom_pos = pyautogui.position()

width = right_bottom_pos[0] - left_top_pos[0]
height = right_bottom_pos[1] - left_top_pos[1]

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