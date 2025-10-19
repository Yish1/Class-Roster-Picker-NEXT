from PyQt5.QtCore import QFile
from moudles.app_state import app_state
from moudles.logger_util import log_print
from moudles.i18n import _

import os
import random
import ctypes
import pygame


state = app_state


class MusicPlayer:
    """封装音乐播放与停止逻辑"""

    def stop_music(self):
        if state.bgmusic == 1 or pygame.mixer.music.get_busy():
            try:
                if state.default_music is True:
                    pass
                else:
                    pygame.mixer.music.fadeout(600)
                pygame.mixer.music.unload()
                try:
                    tmp_file = os.path.join(state.appdata_path, 'tmp.cmxz')
                    os.remove(tmp_file)
                except Exception:
                    pass
            except Exception as e:
                log_print(f"停止音乐播放时发生错误：{str(e)}")

    def _mid_title_map(self):
        return {
            "olg": "Only My Railgun",
            "qqss": "前前前世(ぜんぜんぜんせ)",
            "april": "若能绽放光芒(光るなら)",
            "hyl": "好运来(Good Luck Comes)",
            "hzt": "花の塔",
            "lemon": "Lemon",
            "ltinat": "Late in autumn",
            "qby": "千本桜",
            "xxlg": "小小恋歌",
            "ydh": "运动员进行曲",
            "level5": "LEVEL5 -Judgelight-",
            "zyzy": "自言自语(ヒトリゴト)-ClariS",
        }

    def play_default(self, signals=None):
        """播放默认 tmp.cmxz 音频（循环）"""
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
            tmp_file = os.path.join(state.appdata_path, 'tmp.cmxz')
            ctypes.windll.kernel32.SetFileAttributesW(tmp_file, 0x80)
            with open(tmp_file, "wb") as f:
                f.write(file.readAll())
            ctypes.windll.kernel32.SetFileAttributesW(tmp_file, 2)
            state.default_music = True

            mid_key = mid_load.rsplit('.mid', 1)[0]
            mid_title = self._mid_title_map().get(mid_key, mid_key)

        except Exception as e:
            state.default_music = True
            log_print("err: %s" % str(e))
            return None
        
        tmp_file = os.path.join(state.appdata_path, 'tmp.cmxz')
        pygame.mixer.music.load(tmp_file)
        pygame.mixer.music.play(-1)
        return mid_title

    def play_random_file(self, folder_path, signals=None):
        """从目录中随机选择音频播放，返回展示名称"""
        file_list = os.listdir(folder_path)
        random_file = random.choice(file_list)
        state.file_path = os.path.join(folder_path, random_file)
        pygame.mixer.music.load(state.file_path)
        log_print("播放音乐：%s" % state.file_path)
        sound = pygame.mixer.Sound(state.file_path)
        music_length = sound.get_length()
        random_play = round(random.uniform(2, 5), 1)
        start_time = round(music_length / random_play, 1)
        if signals:
            signals.update_pushbotton.emit(_(" 加载音乐.."), 2)
        music_name = random_file.rsplit('.', 1)[0]
        if signals:
            signals.update_list.emit(7, _("正在播放:%s") % music_name)
        volume = 0.0
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1, start=start_time)
        log_print(f"音频时长：{music_length},随机数：{random_play},音频空降：{start_time}")

        # 音量淡入
        for i in range(50):  # 50 次循环
            if volume < 0.70:
                volume += 0.014
                volume = min(volume, 0.70)
                if i == 10 and signals:
                    signals.update_pushbotton.emit(_(" 加载音乐..."), 2)
                pygame.mixer.music.set_volume(volume)
                pygame.time.delay(30)
        log_print("音量淡入完成。")
        return music_name
