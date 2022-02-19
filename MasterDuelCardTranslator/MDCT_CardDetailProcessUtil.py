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

import tkinter as tk
import threading
from collections import OrderedDict
from PIL import Image

class Cache(dict):
    def __init__(self, max_size):
        self.data = OrderedDict()
        self.max_size = max_size

    def set(self, key, value):
        if key not in self.data:
            if len(self.data) >= self.max_size:
                self.data.popitem(last=False)
        else:
            # 因为set时，要更新key所在的顺序位置，所以先要删除它
            self.data.pop(key)
        self.data[key] = value

    def get(self, key):
        if key in self.data:
            # 因为get时，要更新key所在的顺序位置，所以先要删除它
            value = self.data.pop(key)
            self.data[key] = value
            return value
        else:
            return None

class CardDetailProcessUtil:
    __card = None
    __threadExist = False
    __preDetailInfo = ''
    current_card_id = None
    __LRUCache = None

    @staticmethod
    def initUtil(card):
        CardDetailProcessUtil.__card = card
        CardDetailProcessUtil.__card.insert(tk.INSERT, '''
　　未能匹配到任何卡片。
　　请确保卡片信息区域没有被遮挡。尤其是本界面不能遮挡住卡名和卡片文本，请先将本界面移动到屏幕右侧。
　　如果仍无法匹配，可执行菜单栏中的“设置”->“配置文字区域”。请务必注意配置完成时应能够识别正确的卡名和卡片文本。

　　重新配置完成时，如果出现了非正确的卡名或卡片文本，还请帮忙反馈。十分感谢。
　　反馈地址：https://github.com/Rehcramon/MasterDuelCardTranslator/issues
''')
        CardDetailProcessUtil.__card.config(state=tk.DISABLED)
        CardDetailProcessUtil.__card.pack(fill=tk.BOTH, expand=True)

        CardDetailProcessUtil.__LRUCache = Cache(300)

    @staticmethod
    def changeCardDetail(str):
        if(CardDetailProcessUtil.__preDetailInfo == str):
            return
        CardDetailProcessUtil.__preDetailInfo = str
        CardDetailProcessUtil.__card.config(state=tk.NORMAL)
        CardDetailProcessUtil.__card.delete('1.0', tk.END)
        CardDetailProcessUtil.__card.insert(tk.INSERT, CardDetailProcessUtil.__preDetailInfo)
        CardDetailProcessUtil.__card.config(state=tk.DISABLED)

    @staticmethod
    def isThreadExist():
        return CardDetailProcessUtil.__threadExist

    @staticmethod
    def setThreadStatus(boolStatus):
        CardDetailProcessUtil.__threadExist = boolStatus

    @staticmethod
    def putKVInCache(key, value):
        CardDetailProcessUtil.__LRUCache.set(key, value)

    @staticmethod
    def getCacheByKey(key):
        return CardDetailProcessUtil.__LRUCache.get(key)

def initUtil(card):
    CardDetailProcessUtil.initUtil(card)

def changeCardDetail(str):
    CardDetailProcessUtil.changeCardDetail(str)

def openThread():
    return not CardDetailProcessUtil.isThreadExist()

def setThreadStatus(boolStatus):
    CardDetailProcessUtil.setThreadStatus(boolStatus)

def setArgs(current_card_id):
    CardDetailProcessUtil.current_card_id = current_card_id

def getCurrent_card_id():
    return CardDetailProcessUtil.current_card_id

def getLRUCacheByKey(key):
    return CardDetailProcessUtil.getCacheByKey(key)

def putKeyValueInCache(k, v):
    CardDetailProcessUtil.putKVInCache(k, v)


def dhash(image, hash_size=8):
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)