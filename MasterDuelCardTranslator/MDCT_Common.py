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

VERSION = '1.2'

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

def print_info():
    print(INFO)

SETTINGS = None

def load_settings(filename = 'settings.json'):
    global SETTINGS
    settings_file = open(filename, 'r')
    SETTINGS = json.loads(settings_file.readline())
    settings_file.close()

def get_setting(key):
    return SETTINGS[key]

def set_setting(key, value):
    SETTINGS[key] = value

def save_settings():
    settings_file = open('settings.json', 'w')
    settings_file.write(json.dumps(SETTINGS))
    settings_file.close()

def get_position():
    return SETTINGS['position']