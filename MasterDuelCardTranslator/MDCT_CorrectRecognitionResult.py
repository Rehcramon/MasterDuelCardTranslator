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

import re

BEFORE_AND_AFTER_PLAIN = [
    ('@ignister', '@Ignister'),
    ('@lgnister', '@Ignister'),
    ('A.i.', 'A.I.'),
    ('A.l.', 'A.I.'),
    ('A.|.', 'A.I.')
]

BEFORE_AND_AFTER_REGULAR = [
    ('Live(.){1,3}Twin', 'Live☆Twin'),
    ('Evil(.){1,3}Twin', 'Evil★Twin')
]

def correct_recognition_result(s):
    for p in BEFORE_AND_AFTER_PLAIN:
        s = s.replace(p[0], p[1])
    for p in BEFORE_AND_AFTER_REGULAR:
        s = re.sub(p[0], p[1], s)
    return s