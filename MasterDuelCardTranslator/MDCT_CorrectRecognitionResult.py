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

BEFORE_AND_AFTER = [
    ('@ignister', '@Ignister'),
    ('@lgnister', '@Ignister'),
    ('A.i.', 'A.I.'),
    ('A.l.', 'A.I.'),
    ('A.|.', 'A.I.')
]

def correct_recognition_result(s):
    for p in BEFORE_AND_AFTER:
        s = s.replace(p[0], p[1])
    return s