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

VERSION = '0.5'

SHORT_TITLE = 'MDCT v{}'.format(VERSION)

INFO = '''
    Master Duel Card Translator Project
    Copyright (C) 2022  LLForever and Rehcramon

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to
    redistribute it under certain conditions.
    See the GNU General Public License for more details.

    Version {}
    https://github.com/Rehcramon/MasterDuelCardTranslator
'''.format(VERSION)

def print_info():
    print(INFO)