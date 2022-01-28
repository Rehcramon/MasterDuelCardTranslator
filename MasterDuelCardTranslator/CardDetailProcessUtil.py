import tkinter as tk
import threading

class CardDetailProcessUtil:
    __card = None
    __threadExist = False
    __preDetailInfo = ''
    cardname_buffer = None
    cardname_buffer_status = None
    current_card_id = None

    @staticmethod
    def initUtil(card):
        CardDetailProcessUtil.__card = card
        CardDetailProcessUtil.__card.insert(tk.INSERT, '''
                未能匹配到任何卡名。
                请确保卡名区域没有被遮挡。尤其是本界面不能遮挡住卡名区域，请先将本界面移动到屏幕右下角。
                如果长时间仍无法匹配，可尝试关闭本程序后重新执行MDCT_PositionSetup进行配置。请务必注意配置完成时应能够识别正确的卡名。''')
        CardDetailProcessUtil.__card.config(state=tk.DISABLED)
        CardDetailProcessUtil.__card.pack()

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

def initUtil(card):
    CardDetailProcessUtil.initUtil(card)

def changeCardDetail(str):
    # threading.Thread(target=CardDetailProcessUtil.changeCardDetail(str))
    CardDetailProcessUtil.changeCardDetail(str)

def openThread():
    return not CardDetailProcessUtil.isThreadExist()

def setThreadStatus(boolStatus):
    CardDetailProcessUtil.setThreadStatus(boolStatus)

def setArgs(cardname_buffer, cardname_buffer_status, current_card_id):
    CardDetailProcessUtil.cardname_buffer = cardname_buffer
    CardDetailProcessUtil.cardname_buffer_status = cardname_buffer_status
    CardDetailProcessUtil.current_card_id = current_card_id

def getCardname_buffer():
    return CardDetailProcessUtil.cardname_buffer

def getCardname_buffer_status():
    return CardDetailProcessUtil.cardname_buffer_status

def getCurrent_card_id():
    return CardDetailProcessUtil.current_card_id