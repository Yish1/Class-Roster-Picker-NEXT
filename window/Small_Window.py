from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QRunnable
from PyQt5.QtGui import QCursor, QFontMetrics
from Ui.SmallWindow import Ui_smallwindow
from modules import *

import random, pygame, os

state = app_state

class smallWindow(QtWidgets.QMainWindow, Ui_smallwindow):  # 小窗模式i
    def __init__(self, main_instance=None):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.main_instance = main_instance

    def run_small_window(self):
        self.setMinimumSize(QtCore.QSize(322, 191))
        # 设置半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.pushButton_7.hide()
        self.pushButton_4.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.minimummode)

        self.pushButton_7.mousePressEvent = self.mousePressEvent
        self.pushButton_7.mouseMoveEvent = self.mouseMoveEvent
        self.pushButton_7.mouseReleaseEvent = self.mouseReleaseEvent


        # font_id = QFontDatabase.addApplicationFont("ttf2.ttf")
        # if font_id != -1:  # 确保字体加载成功
        #     state.cust_font = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font_s = QtGui.QFont(state.cust_font, 34)
        self.label_2.setFont(self.font_s)

        self.label_2.setText(_("开始"))
        self.m_flag = False
        self.m_moved = False  # 用于检测是否移动
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", _("点名器小窗模式")))
        self.timer = None
        self.runflag = None
        self.minimum_flag = False
        self.signals = WorkerSignals()
        self.music = MusicPlayer()

        # 自动隐藏倒计时：开启小窗即开始计时，30秒后最小化
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.minimummode)
        self.start_auto_hide()
        self.apply_transparency()

        self.show()
        return self

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_moved = False  # 重置移动标志
            self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.setWindowState(Qt.WindowNoState)
            self.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            self.m_moved = True  # 标记为移动过
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.m_flag and not self.m_moved:
            if self.minimum_flag == False:
                if self.runflag == True:
                    self.qtimer(0)
                else:
                    self.get_name_list()  # 只有未移动时才输出消息
            else:
                self.frame.show()
                self.label.show()
                self.label_2.show()
                self.label_3.show()
                self.pushButton_7.hide()
                self.minimum_flag = False
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def qtimer(self, start):
        if start == 1:
            self.timer = QTimer()
            if state.roll_speed:
                tick = state.roll_speed
            else:
                tick = random.randint(60, 99)
            self.timer.start(tick)
            self.timer.timeout.connect(self.setname)
            self.runflag = True
            self.play_music()
            # 开始点名时停止自动隐藏计时
            self.stop_auto_hide()

        elif start == 0:
            try:
                if state.bgmusic == 1 or pygame.mixer.music.get_busy():
                    self.music_thread = Play_Music_Thread(0)
                    state.threadpool.start(self.music_thread)
                # 非阻塞惯性滚动
                can_inertia = (
                    state.inertia_roll == 1 and
                    len(state.name_list) > 1 and
                    not (state.non_repetitive == 1 and len(state.non_repetitive_list) <= 1)
                )
                if can_inertia:
                    s = 50
                    base = max(30, int(state.roll_speed)) if state.roll_speed else 60
                    speed = random.randint(base - 30, base + 30)
                    self._inertia_step(speed, s)
                else:
                    if state.inertia_roll == 1:
                        log_print("小窗：不满足惯性滚动条件")
                    self._finalize_stop_procedure()


            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        self.font_s.setPointSize(40)
        self.label_2.setFont(self.font_s)

        if state.non_repetitive == 1:
            if len(state.non_repetitive_list) == 0:
                state.non_repetitive_list = state.name_list.copy()
                self.main_instance.update_list(1, _("不放回名单已重置"))
            a = str(len(state.non_repetitive_list))
            if a != "0":
                self.label_3.setText(_("剩%s人") % a)

        if state.name_list == []:
            state.name = ""
            self.font_s.setPointSize(29)
            self.label_2.setFont(self.font_s)
            self.label_2.setText(_("名单为空!"))
            self.main_instance.mini(2)
            self.qtimer(0)
            try:
                self.main_instance.run_settings(f"1&{state.file_path}")
            except Exception as e:
                print(f"无法打开设置:{e}")
        

        else:
            try:
                if state.non_repetitive == 1:
                    state.name = random.choice(state.non_repetitive_list)
                else:
                    state.name = random.choice(state.name_list)
            except:
                pass

            font_size = self.font_s.pointSize()
            metrics = QFontMetrics(self.font_s)        
            max_width = self.label_2.width()
            max_height = self.label_2.height()

            # 估算一行字符数
            a = max(1, round(metrics.horizontalAdvance(state.name) / max_width, 1)) # 估计行数
            b = metrics.height()# 字体高度
            d = 1 if font_size < 80 and len(state.name) < 5 else 2
            c = a * (b * d)# b*2考虑到字符行间隔
            
            # 如果文本换行后的高度超出了标签高度，逐步减小字体
            while c > max_height and font_size > 0:
                
                font_size -= 3
                self.font_s.setPointSize(font_size)
                self.label_2.setFont(self.font_s)
                metrics = QFontMetrics(self.font_s)
                b = metrics.height()

                # 再次计算换行后估算行数
                a = max(1, round(metrics.horizontalAdvance(state.name) / max_width, 1))
                d = 1 if font_size < 80 and len(state.name) < 5 else 2
                c = a * (b * d)

            self.small_window_name = state.name
            self.label_2.setText(self.small_window_name)
            # print(font_size, d)

    def get_name_list(self):
        self.qtimer(1)

    def closeEvent(self, event):
        print("小窗被关闭")
        try:
            self.main_instance.mini(2)
        except:
            pass # 防止主窗口关闭后，小窗关闭报错
        state.small_window_flag = None
        event.accept()  # 确保仅关闭子窗口，不影响主窗口

    def close_window(self):
        self.close()

    def minimummode(self):
        self.frame.hide()
        self.label.hide()
        self.label_2.hide()
        self.label_3.hide()
        self.pushButton_7.show()
        self.minimum_flag = True

    # 自动隐藏计时控制
    def start_auto_hide(self):
        try:
            self.auto_hide_timer.start(30 * 1000)  # 30秒
        except Exception:
            pass

    def stop_auto_hide(self):
        try:
            self.auto_hide_timer.stop()
        except Exception:
            pass

    def reset_auto_hide(self):
        self.stop_auto_hide()
        self.start_auto_hide()

    def dynamic_speed_preview(self, speed):
        """动态调整计时器速度（用于惯性滚动）"""
        try:
            if self.timer:
                self.timer.setInterval(int(speed))
        except Exception as e:
            log_print(f"小窗：调整速度失败:{e}")

    def _inertia_step(self, speed: int, s: int):
        """惯性滚动的单步，使用 singleShot 链式调度，避免阻塞 UI。"""
        try:
            if speed > 650:
                self._finalize_stop_procedure()
                return
            self.dynamic_speed_preview(speed)
            s_next = s + random.randint(100, 120)
            s_next = s_next if s_next <= 280 else 150
            speed_next = speed + s_next
            delay = max(0, int(speed + 100))
            QtCore.QTimer.singleShot(delay, lambda: self._inertia_step(speed_next, s_next))
        except Exception as e:
            log_print(f"小窗：惯性滚动过程中出错:{e}")
            self._finalize_stop_procedure()

    def play_music(self):
        """播放背景音乐"""
        self.music_thread = Play_Music_Thread(1)
        state.threadpool.start(self.music_thread)

    def _finalize_stop_procedure(self):
        """停止计时器并执行停止后的 UI 与数据更新。"""
        try:
            if self.timer:
                self.timer.stop()
            self.runflag = False
            if state.name != "":
                if state.non_repetitive == 1:
                    try:
                        state.non_repetitive_list.remove(self.small_window_name)
                    except ValueError:
                        pass
                    info = self.small_window_name + _(" (剩%s人)") % len(state.non_repetitive_list)
                    if len(state.non_repetitive_list) == 0:
                        self.font_s.setPointSize(29)
                        self.label_2.setFont(self.font_s)
                        self.label_2.setText(_("名单抽取完成"))
                        self.label_3.setText("")
                    else:
                        a = str(len(state.non_repetitive_list))
                        if a != "0":
                            self.label_3.setText(_("剩%s人") % a)
                else:
                    info = self.small_window_name
                try:
                    self.main_instance.save_history(2, self.small_window_name)
                except:
                    print("无法写入历史记录")
                self.main_instance.update_list(1, _("小窗：%s") % info)
                state.origin_name_list = state.name
                self.main_instance.tts_read(self.small_window_name, 2)
            # 结束点名后恢复并重新开始30秒倒计时
            self.reset_auto_hide()
        except Exception as e:
            print(f"小窗：停止流程出错:{e}")

    def apply_transparency(self, value=None):
        """应用小窗口透明度设置"""
        if state.small_window_transparent is not None:
            
            if value is not None:
                transparency_value = value / 100
            else:
                transparency_value = state.small_window_transparent / 100

            self.label.setStyleSheet("QWidget {\n"
                "background-color: rgba(194, 194, 194, %s);\n"
                "border-radius: 28px;\n"
                "}" % transparency_value)

class Play_Music_Thread(QRunnable):
    def __init__(self, mode=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.music = MusicPlayer()
        self.mode = mode

    def run(self):
        if self.mode == 1:
            try:
                if state.bgmusic != 1 or pygame.mixer.music.get_busy():
                    return
                
                folder_path = os.path.join(state.appdata_path, "dmmusic")
                try:
                    file_list = os.listdir(folder_path)
                except Exception:
                    file_list = []

                if file_list == []:
                    mid_title = self.music.play_default()
                    log_print(f"小窗：播放默认音乐:{mid_title}")
                else:
                    self.music.play_random_file(folder_path)
                    
            except Exception as e:
                log_print(f"小窗：播放音乐出错:{e}")
        
        elif self.mode == 0:
            try:
                self.music.stop_music()
            except Exception as e:
                log_print(f"小窗：停止音乐出错:{e}")