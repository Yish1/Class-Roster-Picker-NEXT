# -*- coding: utf-8 -*-
"""
语音播报线程模块
"""
import pythoncom
import win32com.client
from PyQt5.QtCore import QRunnable

from moudles import app_state
from moudles.i18n import _
from moudles.WorkSignals import WorkerSignals
from moudles.logger_util import log_print

# 便捷引用全局状态
state = app_state


class SpeakerThread(QRunnable):
    """语音播报线程"""
    
    def __init__(self, content, mode=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.mode = mode
        self.allownametts = state.allownametts
        self.content = content

    def ttsread(self, text, volume=None):
        """使用 Windows SAPI 进行语音播报"""
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        # for voice in speaker.GetVoices(): # 查询本机所有语言
        #     log_print(voice.GetDescription())
        try:
            if state.language_value == "en_US":
                speaker.Voice = speaker.GetVoices(
                    "Name=Microsoft Zira Desktop").Item(0)
            else:
                speaker.Voice = speaker.GetVoices(
                    "Name=Microsoft Huihui Desktop").Item(0)
        except Exception as e:
            log_print("无法切换语音语言，Reason：", e)

        if volume is not None:
            speaker.Volume = volume
        speaker.Speak(text)

    def run(self):
        """线程运行入口"""
        # debugpy.breakpoint()  # 在此线程启动断点调试
        if self.mode == 1:
            try:
                self.ttsread("1", 0)
                log_print("此设备系统支持语音播报功能！")
                self.signals.speakertest.emit(1, "")
            except Exception as e:
                log_print("此设备系统不支持语音播报功能！Reason：", e)
                e = str(e)
                self.signals.speakertest.emit(0, e)
        else:
            try:
                if self.content != None:
                    if self.allownametts == 2:
                        self.ttsread(text=_("恭喜 %s") % self.content)
                    elif self.allownametts == 3:
                        self.ttsread(self.content)
                    elif self.allownametts == 1:
                        pass

                    if self.mode == 2:
                        pass
                    else:
                        try:
                            self.signals.enable_button.emit(1)
                        except:
                            pass

                else:
                    pass
            except Exception as e:
                log_print("语音播报出现错误！Reason：", e)

        self.signals.finished.emit()
