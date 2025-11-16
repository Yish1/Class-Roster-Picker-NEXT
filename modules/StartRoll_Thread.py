from PyQt5.QtCore import QRunnable
from modules.app_state import app_state
from modules.WorkSignals import WorkerSignals
from modules.i18n import _
from modules.logger_util import log_print
from modules.Music_Player import MusicPlayer

import random
import time
import os
import pygame
# import debugpy

state = app_state


class StartRollThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.music = MusicPlayer()

    def set_volume(self):
        if self.volume < 1.0:
            self.volume += 0.02  # 每次增加0.02
            if self.volume > 1.0:
                self.volume = 1.0  # 确保音量不超过1.0
            pygame.mixer.music.set_volume(self.volume)
        else:
            self.timer.stop()  # 停止定时器

    def run(self):
        # debugpy.breakpoint()

        def stop():
            self.signals.update_pushbotton.emit(_(" 小窗模式"), 2)
            try:
                self.signals.save_history.emit()
            except:
                log_print(_("无法写入历史记录"))
            self.signals.update_list.emit(2, "")

            if state.non_repetitive == 1:
                if len(state.non_repetitive_list) > 0:
                    if state.origin_name_list in state.non_repetitive_list:
                        state.non_repetitive_list.remove(
                            state.origin_name_list)
                    else:
                        log_print(f"不重复的单抽名单中没有{state.origin_name_list}")
                if state.namelen != 0:
                    if len(state.non_repetitive_list) == 1:
                        self.signals.update_list.emit(1, _("最终的幸运儿即将出现："))
                    elif len(state.non_repetitive_list) == 0:
                        self.signals.update_list.emit(
                            1, _("点击开始重置名单,或切换名单继续点名"))
                        self.signals.update_list.emit(0, _("此名单已完成抽取！"))

            if state.allownametts != 1:
                pass
            else:
                self.signals.enable_button.emit(1)

            self.signals.update_pushbotton.emit(_(" 开始"), 1)
            if state.namelen == 0:
                self.signals.enable_button.emit(1)

            self.signals.update_list.emit(7, "")

        if state.running:  # 结束按钮
            self.signals.update_pushbotton.emit(_(" 请稍后..."), 2)
            self.signals.enable_button.emit(3)
            self.signals.enable_button.emit(2)

            if state.bgmusic == 1 or pygame.mixer.music.get_busy():
                self.music.stop_music()

            # debugpy.breakpoint()
            if state.inertia_roll == 1:
                if len(state.non_repetitive_list) == 1 or len(state.name_list) == 0:
                    log_print("不满足惯性滚动条件")
                else:
                    s = 50
                    speed = random.randint(
                        state.roll_speed-30, state.roll_speed+30)
                    while speed <= 650:
                        s += random.randint(100, 120)
                        s = s if s <= 280 else 150
                        speed += s
                        self.signals.change_speed.emit(speed)
                        time.sleep((speed+100) / 1000)

            self.signals.qtimer.emit(0)
            self.signals.show_progress.emit(0, 0, 100, "default")
            self.signals.key_space.emit(1)  # 调整空格为开始
            self.signals.enable_button.emit(7)  # 恢复spinbox
            state.running = False

            stop()
            self.signals.finished.emit()
            # 向主线程发送终止信号

        else:  # 开始按钮
            # debugpy.breakpoint()
            state.running = True
            self.signals.qtimer.emit(1)
            self.signals.enable_button.emit(6)  # 禁用人数选择框spinbox
            log_print("开始点名")
            if state.non_repetitive == 1 and len(state.non_repetitive_list) == 1:
                self.signals.show_progress.emit(1, 0, 0, "mulit_radius")
            else:
                self.signals.show_progress.emit(1, 0, 0, "default")
            self.signals.enable_button.emit(2)
            self.signals.key_space.emit(0)

            if len(state.name_list) != 0:
                if state.bgmusic == 1:
                    try:
                        self.signals.update_pushbotton.emit(_(" 加载音乐."), 2)
                        self.signals.enable_button.emit(3)

                        folder_path = os.path.join(state.appdata_path, "dmmusic")
                        try:
                            file_list = os.listdir(folder_path)
                        except Exception:
                            file_list = []

                        if file_list == []:
                            mid_title = self.music.play_default(self.signals)
                            if mid_title:
                                self.signals.update_list.emit(7, _("正在播放(默认音频):%s") % mid_title)
                            else:
                                self.signals.update_list.emit(7, _("播放默认音频失败！"))
                        else:
                            self.music.play_random_file(folder_path, self.signals)

                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)
                    except Exception as e:
                        self.signals.update_list.emit(7, _("无法播放：%s") % e)
                        log_print("无法播放音乐文件：%s，错误信息：%s" % (state.music_path, e))
                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)

            self.signals.update_pushbotton.emit(_(" 结束"), 2)
            self.signals.enable_button.emit(4)

            if state.non_repetitive == 1:
                self.signals.enable_button.emit(5)
                self.signals.update_pushbotton.emit(_(" 重置名单"), 1)
