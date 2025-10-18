from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from PyQt5.QtGui import QCursor, QFontMetrics
from moudles.app_state import app_state
from moudles.i18n import _
from Ui.SmallWindow import Ui_smallwindow

import random

state = app_state

class smallWindow(QtWidgets.QMainWindow, Ui_smallwindow):  # 小窗模式i
    def __init__(self, main_instance=None):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))

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
        self.main_instance = main_instance
        # self.cust_font_sw = cust_font_sw

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
                    try:
                        self.main_instance.save_history(2, self.small_window_name)
                    except:
                        print("无法写入历史记录")
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
            time = random.randint(60, 99)
            self.timer.start(time)
            self.timer.timeout.connect(self.setname)
            self.runflag = True

        elif start == 0:
            try:
                self.timer.stop()
                self.runflag = False
                if state.name != "":
                    if state.non_repetitive == 1:
                        state.non_repetitive_list.remove(self.small_window_name)
                        info = self.small_window_name + \
                            _(" (剩%s人)") % len(state.non_repetitive_list)
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
                    self.main_instance.update_list(1, _("小窗：%s") % info)
                    state.origin_name_list = state.name
                    self.main_instance.tts_read(self.small_window_name, 2)
                else:
                    pass
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

    def run_small_window(self):
        self.show()
        return self

    def minimummode(self):
        self.frame.hide()
        self.label.hide()
        self.label_2.hide()
        self.label_3.hide()
        self.pushButton_7.show()
        self.minimum_flag = True
