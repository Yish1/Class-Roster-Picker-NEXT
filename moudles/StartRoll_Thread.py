from PyQt5.QtCore import QRunnable
from PyQt5.QtCore import QFile
from moudles.app_state import app_state
from moudles.WorkSignals import WorkerSignals
from moudles.i18n import _
from moudles.logger_util import log_print

import random
import time
import os
import ctypes
import pygame

state = app_state


class StartRollThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

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
                try:
                    if state.default_music == True:
                        pass
                    else:
                        pygame.mixer.music.fadeout(600)
                    pygame.mixer.music.unload()
                    try:
                        tmp_file = os.path.join(state.appdata_path, 'tmp.cmxz')
                        os.remove(tmp_file)
                    except:
                        pass
                except Exception as e:
                    log_print(f"停止音乐播放时发生错误：{str(e)}")

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
                    # debugpy.breakpoint()
                    folder_name = os.path.join(state.appdata_path, "dmmusic")
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    folder_path = folder_name
                    # 获取文件夹中的文件列表
                    file_list = os.listdir(folder_path)
                    if not file_list:
                        try:
                            if state.non_repetitive == 1 and len(state.non_repetitive_list) == 1:
                                mid_file = ['hyl.mid']
                            else:
                                mid_file = ['olg.mid', 'qqss.mid', 'april.mid', 'hyl.mid', 'hzt.mid',
                                            'lemon.mid', 'ltinat.mid', 'qby.mid', 'xxlg.mid', 'ydh.mid', 'level5.mid', 'zyzy.mid']
                            mid_load = random.choice(mid_file)
                            state.file_path = f":/mid/{mid_load}"
                            file = QFile(state.file_path)
                            file.open(QFile.ReadOnly)
                            tmp_file = os.path.join(
                                state.appdata_path, 'tmp.cmxz')
                            ctypes.windll.kernel32.SetFileAttributesW(
                                tmp_file, 0x80)
                            with open(tmp_file, "wb") as f:
                                f.write(file.readAll())
                            ctypes.windll.kernel32.SetFileAttributesW(
                                tmp_file, 2)
                            state.default_music = True

                            mid_load = mid_load.rsplit('.mid', 1)[0]
                            mid_name = {
                                "olg": "Only My Railgun",
                                # https://www.midishow.com/en/midi/47670.html
                                "qqss": "前前前世(ぜんぜんぜんせ)",
                                # https://www.midishow.com/en/midi/ff14-op-midi-download-151208
                                "april": "若能绽放光芒(光るなら)",
                                # https://www.midishow.com/en/midi/1115.html
                                "hyl": "好运来(Good Luck Comes)",
                                # https://www.midishow.com/en/midi/ff14-lycoris-recoil-ed-midi-download-158585
                                "hzt": "花の塔",
                                # https://www.midishow.com/en/midi/71733.html#删除部分前奏_Yish_
                                "lemon": "Lemon",
                                # https://www.midishow.com/en/midi/late-in-autumn-midi-download-148678删除部分前奏_Yish_
                                "ltinat": "Late in autumn",
                                "qby": "千本桜",                     # https://www.midishow.com/en/midi/71765.html
                                "xxlg": "小小恋歌",                  # https://www.midishow.com/en/midi/71740.html
                                "ydh": "运动员进行曲",               # https://www.midishow.com/en/midi/140621.html
                                "level5": "LEVEL5 -Judgelight-",    # https://www.midishow.com/en/midi/23834.html
                                # https://www.midishow.com/en/midi/ff14-8-op-claris-midi-download-171600
                                "zyzy": "自言自语(ヒトリゴト)-ClariS"
                            }
                            mid_load = mid_name.get(mid_load, mid_load)

                            log_print(
                                "正在播放默认音频:%s\n请在 %s 中放入mp3格式的音乐" % (mid_load, folder_path))
                            self.signals.update_list.emit(
                                7, _("正在播放(默认音频):%s") % mid_load)
                        except Exception as e:
                            state.default_music = True
                            log_print("err: %s" % str(e))
                    else:
                        state.default_music = False
                    try:
                        self.signals.update_pushbotton.emit(_(" 加载音乐."), 2)
                        self.signals.enable_button.emit(3)

                        if state.default_music == True:
                            tmp_file = os.path.join(
                                state.appdata_path, 'tmp.cmxz')
                            pygame.mixer.music.load(tmp_file)
                            pygame.mixer.music.play(-1)
                        else:
                            random_file = random.choice(file_list)
                            state.file_path = os.path.join(
                                folder_path, random_file)
                            pygame.mixer.music.load(state.file_path)
                            log_print("播放音乐：%s" % state.file_path)
                            sound = pygame.mixer.Sound(state.file_path)
                            music_length = sound.get_length()
                            random_play = round(random.uniform(2, 5), 1)
                            start_time = round(music_length / random_play, 1)
                            self.signals.update_pushbotton.emit(
                                _(" 加载音乐.."), 2)
                            music_name = random_file.rsplit('.', 1)[0]
                            self.signals.update_list.emit(
                                7, _("正在播放:%s") % music_name)
                            self.volume = 0.0
                            pygame.mixer.music.set_volume(self.volume)
                            pygame.mixer.music.play(-1, start=start_time)
                            log_print(
                                f"音频时长：{music_length},随机数：{random_play},音频空降：{start_time}")

                            # 使用 for 循环进行音量淡入
                            for i in range(50):  # 50 次循环，每次增加0.02的音量
                                if self.volume < 0.70:
                                    self.volume += 0.014
                                    self.volume = min(self.volume, 0.70)
                                    if i == 10:
                                        self.signals.update_pushbotton.emit(
                                            _(" 请稍后..."), 2)
                                    pygame.mixer.music.set_volume(self.volume)
                                    pygame.time.delay(30)
                            log_print("音量淡入完成。")

                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)

                    except Exception as e:
                        self.signals.update_list.emit(7, _("无法播放：%s") % e)
                        log_print("无法播放音乐文件：%s，错误信息：%s" % (state.file_path, e))
                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)

            self.signals.update_pushbotton.emit(_(" 结束"), 2)
            self.signals.enable_button.emit(4)

            if state.non_repetitive == 1:
                self.signals.enable_button.emit(5)
                self.signals.update_pushbotton.emit(_(" 重置名单"), 1)
