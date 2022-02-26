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

TYPE = [
    ('MAX_TYPE_VALUE', 0x4000000, ''),

    ('TYPE_MONSTER', 0x1, '怪兽'),
    ('TYPE_SPELL', 0x2, '魔法'),
    ('TYPE_TRAP', 0x4, '陷阱'),
    ('TYPE_NORMAL', 0x10, '通常'),
    ('TYPE_EFFECT', 0x20, '效果'),
    ('TYPE_FUSION', 0x40, '融合'),
    ('TYPE_RITUAL', 0x80, '仪式'),
    ('TYPE_TRAPMONSTER', 0x100, '陷阱怪兽'),
    ('TYPE_SPIRIT', 0x200, '灵魂'),
    ('TYPE_UNION', 0x400, '同盟'),
    ('TYPE_DUAL', 0x800, '二重'),
    ('TYPE_TUNER', 0x1000, '调整'),
    ('TYPE_SYNCHRO', 0x2000, '同调'),
    ('TYPE_TOKEN', 0x4000, '衍生物'),
    ('TYPE_QUICKPLAY', 0x10000, '速攻'),
    ('TYPE_CONTINUOUS', 0x20000, '永续'),
    ('TYPE_EQUIP', 0x40000, '装备'),
    ('TYPE_FIELD', 0x80000, '场地'),
    ('TYPE_COUNTER', 0x100000, '反击'),
    ('TYPE_FLIP', 0x200000, '反转'),
    ('TYPE_TOON', 0x400000, '卡通'),
    ('TYPE_XYZ', 0x800000, 'XYZ'),
    ('TYPE_PENDULUM', 0x1000000, '灵摆'),
    ('TYPE_SPSUMMON', 0x2000000, '特殊召唤'),
    ('TYPE_LINK', 0x4000000, '连接')
]

TYPE_ID_TO_TEXT = {}
TYPE_ENUM_TO_ID = {}

for type_entry in TYPE:
    TYPE_ID_TO_TEXT[type_entry[1]] = type_entry[2]
    TYPE_ENUM_TO_ID[type_entry[0]] = type_entry[1]

ATTRIBUTE_ID_TO_TEXT = {
    0x01: '地',
    0x02: '水',
    0x04: '炎',
    0x08: '风',
    0x10: '光',
    0x20: '暗',
    0x40: '神'
}

RACE_ID_TO_TEXT = {
    0x1: '战士',
    0x2: '魔法师',
    0x4: '天使',
    0x8: '恶魔',
    0x10: '不死',
    0x20: '机械',
    0x40: '水',
    0x80: '炎',
    0x100: '岩石',
    0x200: '鸟兽',
    0x400: '植物',
    0x800: '昆虫',
    0x1000: '雷',
    0x2000: '龙',
    0x4000: '兽',
    0x8000: '兽战士',
    0x10000: '恐龙',
    0x20000: '鱼',
    0x40000: '海龙',
    0x80000: '爬虫类',
    0x100000: '念动力',
    0x200000: '幻神兽',
    0x400000: '创造神',
    0x800000: '幻龙',
    0x1000000: '电子界'
}

def parse_sql_entry(e):
    return {
        'id': e[0],
        'ot': e[1],
        'alias': e[2],
        'setcode': e[3],
        'type': e[4],
        'atk': e[5],
        'def': e[6],
        'level': e[7],
        'race': e[8],
        'attribute': e[9],
        'category': e[10]
    }

def get_card_data_string(e):
    o = parse_sql_entry(e)
    l = []
    i = 0x1
    while i <= TYPE_ENUM_TO_ID['MAX_TYPE_VALUE']:
        if (i & o['type']) > 0:
            l.append(TYPE_ID_TO_TEXT[i])
        i <<= 1
    ret_str = '[' + ']['.join(l) + ']'
    if (TYPE_ENUM_TO_ID['TYPE_MONSTER'] & o['type']) > 0:
        ret_str += '[{}属性][{}族]'.format(ATTRIBUTE_ID_TO_TEXT[o['attribute']], RACE_ID_TO_TEXT[o['race']])
        if o['atk'] == -2:
            o['atk'] = '?'
        if (TYPE_ENUM_TO_ID['TYPE_LINK'] & o['type']) > 0:
            link_value = 0
            def_tmp = o['def']
            while def_tmp > 0:
                if (def_tmp & 1) > 0:
                    link_value += 1
                def_tmp >>= 1
            ret_str += '[LINK-{}]\n[ATK/{}]'.format(link_value, o['atk'])
        else:
            if o['def'] == -2:
                o['def'] = '?'
            if (TYPE_ENUM_TO_ID['TYPE_XYZ'] & o['type']) > 0:
                ret_str += '[Rank {}]'.format(o['level'] & 0xFFFF)
            else:
                ret_str += '[Level{}]'.format(o['level'] & 0xFFFF)
            if (TYPE_ENUM_TO_ID['TYPE_PENDULUM'] & o['type']) > 0:
                ret_str += '[<{}>]'.format((o['level'] & 0x000F0000) >> 16)
            ret_str += '\n[ATK/{}][DEF/{}]'.format(o['atk'], o['def'])
    ret_str += '\n'
    return ret_str