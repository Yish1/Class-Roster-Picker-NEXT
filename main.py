# -*- coding: utf-8 -*-
import sys
import random
import difflib
import os
import time
import requests
import platform
import gettext
import pygame
import ctypes
import msvcrt
import pythoncom
import win32com.client
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor, QFontMetrics, QKeySequence, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QFile, QThreadPool, pyqtSignal, QRunnable, QObject, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog, QScroller, QShortcut, QSizePolicy
from datetime import datetime

from ui import Ui_CRPmain  # 导入ui文件
from smallwindow import Ui_smallwindow
from settings import Ui_Settings
from msgbox import Ui_msgbox

from moudles import *

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))
# debugpy.wait_for_client()  # 等待调试器连接

init_log('log.txt')

# init i18n with config language if present
try:
    _config_boot = read_config_file('config.ini')
    language_value = _config_boot.get('language', 'zh_CN')
    init_gettext(language_value)
except Exception as e:
    try:
        init_gettext('zh_CN')
    except Exception as e2:
        user32 = ctypes.windll.user32
        user32.MessageBoxW(None, f"程序启动时遇到严重错误:{e2}", "Warning!", 0x30)

# version
dmversion = 6.56

# config变量
allownametts = None   # 1关闭 2正常模式 3听写模式
checkupdate = None    # 0/1关闭 2开启
bgimg = None         # 1默认 2自定义 3无
latest_version = None
last_name_list = None  # 记录上次选中的名单
non_repetitive = None  # 0关闭 1开启
bgmusic = None        # 0关闭 1开启
first_use = None
roll_speed = None
inertia_roll = None   # 0关闭 1开启
title_text = None     # 标题文字: 幸运儿是:

# 全局变量
name = None
mrunning = False
running = False
default_music = False
default_name_list = _("默认名单")
name_list = ""
history_file = ""
non_repetitive_list = ""
namelen = 0
newversion = None
origin_name_list = None
cust_font = None

# 窗口标识符
windows_move_flag = None
small_window_flag = None
settings_flag = None

# 初始化
today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
pygame.mixer.init()
threadpool = QThreadPool() # 创建线程池


class MainWindow(QtWidgets.QMainWindow, Ui_CRPmain):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        # 设置窗口标志
        self.setWindowFlag(Qt.FramelessWindowHint)
        # 设置半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 鼠标拖动标志
        self.m_flag = False
        self.resize_flag = False

        self.font_m = None

        self.setMinimumSize(QtCore.QSize(780, 445))
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", _("沉梦课堂点名器 %s") % dmversion))
        self.pushButton_2.setText(_(" 开始"))
        self.pushButton_5.setText(_(" 小窗模式"))
        self.spinBox.setValue(1)
        self.label_5.setText(_("当前名单："))
        self.label_4.setText(_("抽取人数："))
        self.label_7.setText("")
        self.progressBar.hide()
        self.commandLinkButton.hide()

        # 添加横线遮罩的 FrameWithLines
        self.linemask = FrameWithLines(self)
        self.linemask.setObjectName("linemask")
        self.gridLayout.addWidget(self.linemask, 0, 0, 1, 1)
        self.linemask.lower()
        self.linemask.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.setCentralWidget(self.frame)

        # 定义空格快捷键
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)

        # 连接按钮
        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_4.clicked.connect(self.run_settings)
        self.pushButton_5.clicked.connect(self.small_mode)
        self.pushButton.clicked.connect(lambda: self.mini(1))
        self.commandLinkButton.clicked.connect(self.restoresize)

        # 启用触摸手势滚动
        scroller = QScroller.scroller(self.listWidget)
        scroller.grabGesture(self.listWidget.viewport(),
                             QScroller.LeftMouseButtonGesture)

        # 启动时执行的函数
        self.read_config()
        self.read_name_list(2)
        self.set_bgimg()
        self.check_new_version()
        self.change_space(1)
        self.init_font()

        self.timer = None
        if first_use == 0:
            self.first_use_introduce()


    def init_font(self):
        global cust_font
        font_path = ":/fonts/font.ttf"
        # 读取字体文件
        font_file = QFile(font_path)
        if not font_file.open(QFile.ReadOnly):
            log_print("字体文件打开失败")
            return
        data = font_file.readAll()
        font_file.close()

        # 直接从内存加载字体，无需写入临时文件
        font_id = QFontDatabase.addApplicationFontFromData(data)
        if font_id != -1:  # 确保字体加载成功
            cust_font = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.font_m = QFont(cust_font, 52)

            self.label_3.setFont(self.font_m)
            self.pushButton_2.setFont(self.font_m)
            self.pushButton_5.setFont(self.font_m)
        else:
            log_print("字体加载失败")
        self.label_3.setText(title_text)

    def apply_translations(self):
        """Update runtime UI texts to the current language."""
        try:
            self.setWindowTitle(QCoreApplication.translate(
                "MainWindow", _("沉梦课堂点名器 %s") % dmversion))
            self.pushButton_2.setText(_(" 开始"))
            self.pushButton_5.setText(_(" 小窗模式"))
            self.label_5.setText(_("当前名单："))
            self.label_4.setText(_("抽取人数："))
            # Update background label if needed
            if bgimg == 2:
                self.label_6.setText(_("自定义背景"))
            # Update title text from config
            if title_text:
                self.label_3.setText(title_text)
        except Exception as e:
            log_print(f"apply_translations error: {e}")

    def mouseMoveEvent(self, event):
        # 获取鼠标相对于窗口的坐标
        pos = event.pos()
        rect = self.rect()  # 窗口的区域

        # 判断是否在右下角区域
        if (rect.width() - pos.x() <= 35 and
                rect.height() - pos.y() <= 35):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))  # 设置调整大小的鼠标指针
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))  # 恢复默认光标

        if self.resize_flag:
            # 调整窗口大小
            diff = event.globalPos() - self.m_Position
            new_width = self.width() + diff.x()
            new_height = self.height() + diff.y()
            self.resize(
                max(new_width, self.minimumWidth()),
                max(new_height, self.minimumHeight())
            )
            self.m_Position = event.globalPos()
        elif self.m_flag:
            # 拖动窗口
            self.move(event.globalPos() - self.m_Position)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if (self.width() - event.pos().x() <= 35 and
                    self.height() - event.pos().y() <= 35):
                self.resize_flag = True
                self.m_Position = event.globalPos()
            elif event.pos().y() <= self.height() // 2:
                self.m_flag = True
                self.m_Position = event.globalPos() - self.pos()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.resize_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))  # 恢复光标

    def resizeEvent(self, event):
        global windows_move_flag
        super().resizeEvent(event)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        # 检查窗口尺寸
        if self.width() > screen_geometry.width() * 0.9 or self.height() > screen_geometry.height() * 0.9:
            self.commandLinkButton.show()  # 显示按钮
            if self.width() > screen_geometry.width() or self.height() > screen_geometry.height():
                self.resize(screen_geometry.width(), screen_geometry.height())
        else:
            self.commandLinkButton.hide()  # 隐藏按钮

        if self.width() > 905 or self.height() > 495:
            windows_move_flag = True
        else:
            windows_move_flag = False

    def set_bgimg(self):
        self.label_6.setText("")
        if bgimg == 2:
            folder_name = "images"
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, folder_name)
            os.makedirs(folder_name, exist_ok=True)
            file_list = os.listdir(folder_path)
            if not file_list:
                log_print("要使用自定义背景功能，请在 %s 中放入图片文件" % folder_path)
                self.frame.setStyleSheet("#frame {\n"
                                         "border-image: url(:/images/(1070).webp);"
                                         "border-radius: 28px;"
                                         "}")
                return
            self.label_6.setText(_("自定义背景"))
            random_file = random.choice(file_list)
            log_print(random_file)
            self.frame.setStyleSheet("#frame {\n"
                                     f"border-image: url('./images/{random_file}');"
                                     "border-radius: 28px;"
                                     "}")
        elif bgimg == 1 or bgimg == 0:
            self.frame.setStyleSheet("#frame {\n"
                                     "border-image: url(:/images/bg.webp);"
                                     "border-radius: 28px;"
                                     "}")
        elif bgimg == 3:
            self.frame.setStyleSheet("#frame {\n"
                                     "background-color: rgba(42, 45, 47, 0.92);\n"
                                     "border-radius: 28px;"
                                     "}")

    def small_mode(self):
        global small_window_flag
        # 保留对子窗口实例的引用
        if small_window_flag is None:
            self.showMinimized()
            small_Window = smallWindow(mainWindow)
            small_window_flag = small_Window.run_small_window()

    def run_settings(self, target_tab = None):
        global settings_flag
        if settings_flag is None:
            if target_tab:
                settings_window = settingsWindow(mainWindow, target_tab)
            else:
                settings_window = settingsWindow(mainWindow)
            settings_flag = settings_window.run_settings_window()

    def closeEvent(self, event):
        # 关闭其他窗口的代码
        try:
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, QWidget) and widget != self:
                    widget.close()
        except:
            pass
        event.accept()

    def mini(self, mode):
        if mode == 1:
            self.showMinimized()
        elif mode == 2:
            self.showNormal()
    # 功能实现代码

    def restoresize(self):
        self.resize(905, 495)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def make_name_list(self):
        for i in range(1, 21):
            yield str(i).rjust(2, "0")

    def init_name(self, name_list):
        global name_path
        name_path = os.path.join(
            "name", f"{default_name_list}.txt")  # 打开文件并写入内容
        with open(name_path, "w", encoding="utf8") as f:
            for i in name_list:
                f.write(i)
                f.write("\n")

    def read_name_list(self, mode=None):
        folder_name = "name"
        os.makedirs("name", exist_ok=True)
        if not os.path.exists(folder_name) or not os.listdir(folder_name):
            self.init_name(self.make_name_list())
            log_print("first_run")
        txt_name = [filename for filename in os.listdir(
            folder_name) if filename.endswith(".txt")]
        # 获取所有txt文件
        mdnum = len(txt_name)
        if mdnum == 0:
            self.show_message(_("名单文件不存在，且默认名单无法生成，请反馈给我们！"), _("名单生成异常！"))
            sys.exit()
            log_print("共读取到 %d 个名单" % mdnum)
        txt_files_name = [os.path.splitext(
            filename)[0] for filename in txt_name]
        # 去除扩展名
        if mode == 1:
            return txt_files_name
        else:
            self.comboBox.disconnect()
            self.comboBox.clear()
            self.comboBox.addItems(txt_files_name)  # 添加文件名到下拉框
            try:
                self.comboBox.setCurrentText(last_name_list)
            except:
                pass
            self.comboBox.currentIndexChanged.connect(
                lambda: self.get_selected_file(0))
            if mode == 2:
                self.get_selected_file(1)
            else:
                pass

    def get_selected_file(self, first=None):
        global file_path, selected_file, history_file
        # 获取当前选中的文件名
        selected_file = self.comboBox.currentText()
        self.update_config("last_name_list", selected_file)
        file_path = os.path.join("name", selected_file+".txt")
        history_file = "history/%s中奖记录.txt" % selected_file
        if not os.path.exists(file_path):
            self.show_message(_("所选名单文件已被移动或删除！"), _("找不到文件！"))
            try:
                self.comboBox.setCurrentIndex(0)
            except:
                log_print("first_run")
        else:
                log_print(f"所选文件的路径为: {file_path}\n")
        self.process_name_file(file_path)
        if first == 1:
            info = _("\'%s'，共 %s 人") % (selected_file, namelen)
            if non_repetitive == 1:
                info += _("(不放回)")
            self.listWidget.addItem(info)

        if first == 0:
            info = _("切换至>\'%s\' 共 %s 人") % (selected_file, namelen)
            if non_repetitive == 1:
                info += _("(不放回)")
            self.listWidget.addItem(info)
            self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def read_config(self):
        global allownametts, checkupdate, bgimg, last_name_list, language_value, latest_version, non_repetitive, bgmusic, first_use, inertia_roll, roll_speed, title_text
        config = {}
        if not os.path.exists('config.ini'):
            with open('config.ini', 'w', encoding='utf-8') as file:
                file.write("")

        config = read_config_file('config.ini')
        try:
            language_value = config.get('language') if config.get(
                'language') else self.update_config("language", "zh_CN", "w!")
            allownametts = int(config.get('allownametts')) if config.get(
                'allownametts') else self.update_config("allownametts", 1, "w!")
            checkupdate = int(config.get('checkupdate')) if config.get(
                'checkupdate') else self.update_config("checkupdate", 2, "w!")
            bgimg = int(config.get('bgimg')) if config.get(
                'bgimg') else self.update_config("bgimg", 1, "w!")
            last_name_list = config.get('last_name_list') if config.get(
                'last_name_list') else self.update_config("last_name_list", "None", "w!")
            latest_version = config.get('latest_version') if config.get(
                'latest_version') else self.update_config("latest_version", 0, "w!")
            non_repetitive = int(config.get('non_repetitive')) if config.get(
                'non_repetitive') else self.update_config("non_repetitive", 1, "w!")
            bgmusic = int(config.get('bgmusic')) if config.get(
                'bgmusic') else self.update_config("bgmusic", 0, "w!")
            first_use = int(config.get('first_use')) if config.get(
                'first_use') else self.update_config("first_use", 0, "w!")
            inertia_roll = int(config.get('inertia_roll')) if config.get(
                'inertia_roll') else self.update_config("inertia_roll", 1, "w!")
            roll_speed = int(config.get('roll_speed')) if config.get(
                'roll_speed') else self.update_config("roll_speed", "80", "w!")
            title_text = config.get('title_text') if config.get(
                'title_text') else _("幸运儿是:")

        except Exception as e:
            log_print(f"配置文件读取失败，已重置无效为默认值！{e}")
            self.show_message(_("配置文件读取失败，已重置为默认值！\n%s") % e, _("读取配置文件失败！"))
            os.remove("config.ini")
            self.read_config()
        return config

    def update_config(self, variable, new_value, mode=None):
        # delegate to config manager
        update_entry(variable, str(new_value) if new_value is not None else None, 'config.ini')
        log_print(f"更新配置文件：[{variable}]={new_value}\n")

        if mode == "w!":
            pass
        else:
            self.read_config()
        if variable == 'bgimg':
            self.set_bgimg()
        elif variable == 'title_text':
            self.label_3.setText(new_value)
        elif variable == 'roll_speed':
            try:
                self.dynamic_speed_preview(roll_speed)
            except:
                pass

    def process_name_file(self, file_path):
        global name_list, namelen, non_repetitive_list
        try:
            with open(file_path, encoding='utf8') as f:
                # 读取每一行，去除行尾换行符，过滤掉空行和仅包含空格的行
                name_list = [line.strip()
                             for line in f.readlines() if line.strip()]
        except:
            log_print("utf8解码失败，尝试gbk")
            try:
                with open(file_path, encoding='gbk') as f:
                    name_list = [line.strip()
                                 for line in f.readlines() if line.strip()]
            except:
                self.show_message(
                    _("Error: 名单文件%s编码错误，请检查文件编码是否为utf8或gbk") % file_path, _("错误"))
                self.label_3.setText(_("名单文件无效！"))
        print("\n", name_list)
        namelen = len(name_list)
        self.spinBox.setMaximum(namelen)
        print("读取到的有效名单长度:", namelen)
        if non_repetitive == 1:
            non_repetitive_list = name_list.copy()

    def ttsinitialize(self):
        global allownametts
        if allownametts == 2:
            print("语音播报(正常模式)")
        elif allownametts == 3:
            print("语音播报(听写模式)")
        elif allownametts == 1 or allownametts == 0:
            print("语音播报已禁用")

    def opentext(self, path):
        if sys.platform == "win32":
            os.system("start %s" % path)
        else:
            os.system("vim %s" % path)

    def save_history(self, mode=None, name_set=None):
        global history_file
        os.makedirs('history', exist_ok=True)
        history_file = "history/%s中奖记录.txt" % selected_file

        if mode == 2:
            write_name = name_set
        else:
            write_name = name

        if write_name != '' or name_set != None:
            with open(history_file, "a", encoding="utf-8") as file:
                if mode == 1:
                        content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                            today, dmversion, name_set)
                else:
                        content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                            today, dmversion, write_name)
                file.write(content)

                log_print(today, "幸运儿是： %s " % write_name)
        else:
            pass

    def change_space(self, value: int):
        try:
            self.shortcut.activated.disconnect()
        except:
            pass

        if value == 1:
            self.shortcut.activated.connect(self.pushButton_2.click)
        elif value == 0:
            self.shortcut.activated.connect(self.pushButton_5.click)

    def start(self):
        num = self.spinBox.value()
        if num > 1:
            self.start_mulit()
        else:
            self.thread = WorkerThread()
            self.thread.signals.show_progress.connect(self.update_progress_bar)
            self.thread.signals.update_pushbotton.connect(
                self.update_pushbotton)
            self.thread.signals.update_list.connect(self.update_list)
            self.thread.signals.enable_button.connect(self.enable_button)
            self.thread.signals.qtimer.connect(self.qtimer)
            self.thread.signals.save_history.connect(self.save_history)
            self.thread.signals.key_space.connect(self.change_space)
            self.thread.signals.change_speed.connect(
                self.dynamic_speed_preview)
            self.thread.signals.finished.connect(
                lambda: log_print("结束点名") or self.ttsinitialize())

            threadpool.start(self.thread)

    def check_new_version(self):
        
        self.update_thread = UpdateThread()
        threadpool.start(self.update_thread)
        self.update_thread.signals.find_new_version.connect(
            self.update_message)
        self.update_thread.signals.update_list.connect(
            self.update_list)
        self.update_thread.signals.finished.connect(
            lambda: log_print("检查更新线程结束"))

    def update_message(self, message, title):  # 更新弹窗
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        okButton = msgBox.addButton("立刻前往", QMessageBox.AcceptRole)
        noButton = msgBox.addButton("下次一定", QMessageBox.RejectRole)
        # ignoreButton = msgBox.addButton("忽略本次更新", QMessageBox.RejectRole)
        msgBox.exec_()
        clickedButton = msgBox.clickedButton()
        if clickedButton == okButton:
            os.system("start https://cmxz.top/ktdmq")
            self.update_list(1, title)
        # elif clickedButton == ignoreButton:
        #     self.update_list(1, title)
        #     self.update_config("latest_version", newversion)
        else:
            self.update_list(1, title)

    def start_mulit(self):
        num = self.spinBox.value()
        if num > namelen:
            self.show_message(_("Error: 连抽人数大于名单人数!"), _("错误"))
        else:
            if mrunning == False:
                self.ptimer = QTimer(self)
                self.progressBar.setMaximum(100)
                self.progressBar.show()
                self.ptimer.timeout.connect(self.update_progress_bar_mulit)
                self.value = 0
                self.ptimer.start(5)
                print("连抽：%d 人" % num)
                name_set = random.sample(name_list, num)
                print(name_set)
                try:
                    self.save_history(1, name_set)
                except:
                    log_print("无法写入历史记录")
                print(today, "幸运儿是： %s " % name_set)
                self.listWidget.addItem("----------------------------")
                self.listWidget.addItem(_("连抽：%d 人") % num)
                for name in name_set:
                    self.listWidget.addItem(name)
                self.listWidget.addItem("----------------------------")
                target_line = num - 2 if num > 2 else num - 1
                self.listWidget.setCurrentRow(
                    self.listWidget.count() - target_line)
                self.label_3.setText(title_text)
            else:
                log_print("连抽中...")

    def reset_repetive_list(self):
        global non_repetitive_list
        print("已重置不重复列表")
        self.update_list(1, _("已重置单抽列表(%s人)") % namelen)
        non_repetitive_list = name_list.copy()

    def update_progress_bar_mulit(self):
        global mrunning
        mrunning = True
        self.update_progress_bar("", "", "", "mulit")  # 金色传说
        if self.progressBar.value() < 100:
            self.value += 1
            self.progressBar.setValue(self.value)

        else:
            mrunning = False
            self.value = 0
            self.progressBar.setValue(self.value)
            self.update_progress_bar(0, "", "", "default")  # 隐藏并恢复默认进度条样式
            self.ptimer.stop()  # 停止定时器

    def update_progress_bar(self, mode, value, value2, style=None):
        if value == "" and value2 == "":
            pass
        else:
            self.progressBar.setValue(value)
            self.progressBar.setMaximum(value2)

        if mode == 1:
            self.progressBar.show()

        elif mode == 0:
            self.progressBar.hide()

        if style == "default":
            self.progressBar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid rgba(88, 88, 88, 0.81);
                    border-radius: 2px;
                    background-color: rgba(0, 0, 0, 0);
                }

                QProgressBar::chunk {
                    background-color: QLinearGradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #00BCD4, stop: 1 #8BC34A
                    );
                    border-radius: 8px;
                }
            """)

        elif style == "mulit" or style == "mulit_radius":
            radius_style = f"        border-radius: 8px;\n" if style == "mulit_radius" else ""
            self.progressBar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid rgba(88, 88, 88, 0.81);
                    border-radius: 2px;
                    background-color: rgba(0, 0, 0, 0);
                }}

                QProgressBar::chunk {{
                    background-color: QLinearGradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #ffda95, stop: 1 #FF9800
                    );
                    {radius_style}
                }}
            """)

    def update_pushbotton(self, text, mode=None):
        if mode == 1:
            self.pushButton_2.setText(text)
        else:
            self.pushButton_5.setText(text)

    def enable_button(self, value):
        if value == 1:  # 初始状态
            self.pushButton_5.setEnabled(True)
            self.pushButton_2.setEnabled(True)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icons/swindow.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_5.setIcon(icon)
            self.pushButton_2.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(118, 218, 96, 1);border-radius:5px;}QPushButton:hover{background:rgba(80, 182, 84, 1);}")
            self.pushButton_5.clicked.disconnect()
            self.pushButton_5.clicked.connect(self.small_mode)
            self.pushButton_5.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(237, 237, 237, 1);border-radius:5px;}QPushButton:hover{background:rgba(210, 210, 210, 0.6);}")
            self.pushButton_2.clicked.disconnect()
            self.pushButton_2.clicked.connect(self.start)

        elif value == 2:  # 开始单抽
            self.pushButton_2.setEnabled(False)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icons/stop.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_5.setIcon(icon)
            self.pushButton_5.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(249, 117, 83, 1);border-radius:5px;}QPushButton:hover{background:rgba(226, 82, 44, 1);}")
            self.pushButton_2.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(237, 237, 237, 1);border-radius:5px;}QPushButton:hover{background:rgba(80, 182, 84, 1);}")
            self.pushButton_5.clicked.disconnect()
            self.pushButton_5.clicked.connect(self.start)

        elif value == 3:  # 禁用开始键
            self.pushButton_5.setEnabled(False)

        elif value == 4:  # 启用开始键
            self.pushButton_5.setEnabled(True)

        elif value == 5:  # 不重复单抽开始
            self.pushButton_2.setEnabled(True)
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/icons/stop.png"),
                           QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_5.setIcon(icon)
            self.pushButton_5.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(249, 117, 83, 1);border-radius:5px;}QPushButton:hover{background:rgba(226, 82, 44, 1);}")
            self.pushButton_2.setStyleSheet("QPushButton {\n"
                                            "    font-size: 20px;\n"
                                            "	 color: rgb(58, 58, 58);\n"
                                            "}\n"
                                            "QPushButton{background:rgba(112, 198, 232, 1);border-radius:5px;}QPushButton:hover{background:rgba(93, 167, 196, 1);}")
            self.pushButton_5.clicked.disconnect()
            self.pushButton_5.clicked.connect(self.start)
            self.pushButton_2.clicked.disconnect()
            self.pushButton_2.clicked.connect(self.reset_repetive_list)

        elif value == 6:
            self.spinBox.setEnabled(False)  # 开始单抽后不允许选择人数

        elif value == 7:
            self.spinBox.setEnabled(True)

    def update_list(self, mode, value):
        if mode == 2:
            mode = 1
            value = f" {origin_name_list}" if origin_name_list else ""
            if non_repetitive == 1:
                value += _(" (还剩%s人)") % (len(non_repetitive_list)
                                          ) if origin_name_list else ""
        if mode == 1:
            if value == "":
                pass
            else:
                self.listWidget.addItem(value)
                self.listWidget.setCurrentRow(self.listWidget.count() - 1)
        elif mode == 0:
            self.font_m.setPointSize(54)
            self.label_3.setFont(self.font_m)
            self.label_3.setText(value)

        elif mode == 7:
            self.label_7.setText(value)

    def qtimer(self, start):
        global non_repetitive_list, name, origin_name_list
        if start == 1:
            if len(name_list) == 0:
                self.show_message(
                    _("Error: 名单文件为空，请输入名字（一行一个）后再重新点名！"), _("错误"))
                self.qtimer(2)
                self.pushButton_5.setEnabled(True)
                self.pushButton_5.click()  # 名单没有人就自动按结束按钮
                origin_name_list = None
                self.font_m.setPointSize(45)
                self.label_3.setText(_(" 名单文件为空！"))
                name = ""
                try:
                    self.run_settings(f"1&{file_path}")
                except Exception as e:
                    self.show_message(_("选择的名单文件%s不存在！") %
                                      file_path, "\n%s" % e)
            else:
                self.timer = QTimer(self)
                print(f"滚动速度:{roll_speed}")
                self.timer.start(roll_speed)
                self.timer.timeout.connect(self.setname)

        elif start == 2:
            try:
                if self.timer:
                    self.timer.stop()
                
            except Exception as e:
                print(f"停止计时器失败:{e}")

        elif start == 0:
            try:
                if self.timer:
                    self.timer.stop()
                    # print("Debug:",name)
                    if allownametts != 1:
                        self.tts_read(origin_name_list)
                
            except Exception as e:
                print(f"计时器启动语音播报线程失败:{e}")            

    def setname(self):
        global name, non_repetitive_list, origin_name_list, windows_move_flag
        max_width = self.label_3.width()
        max_height = self.label_3.height()
        
        if windows_move_flag:
            self.font_m.setPointSize(150)  # 字体大小
            self.label_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许 QLabel 扩展
            self.label_3.setMaximumSize(16777215, 16777215)
        else:
            self.font_m.setPointSize(90)
            self.label_3.setMaximumSize(max_width, max_height)
            
        self.label_3.setFont(self.font_m)
        if non_repetitive == 1:
            if len(non_repetitive_list) == 0:
                non_repetitive_list = name_list.copy()
        if namelen == 0:
            self.show_message(_("Error: 名单文件为空，请输入名字（一行一个）后再重新点名！"), _("错误"))
            name = ""
            try:
                self.run_settings(f"1&{file_path}")
            except Exception as e:
                print(f"文件不存在:{e}")
                self.show_message(_("选择的名单文件%s不存在！") % file_path, "\n%s" % e)
            finally:
                self.font_m.setPointSize(54)
                self.label_3.setFont(self.font_m)
                self.label_3.setText(_(" 名单文件为空！"))
                self.pushButton_5.setEnabled(True)
                self.pushButton_5.click()  # 名单没有人就自动按结束按钮(中途切换名单)
                origin_name_list = None
                self.qtimer(2)
                return
        try:
            if non_repetitive == 1:
                name = random.choice(non_repetitive_list)
            else:
                name = random.choice(name_list)
        except:
            pass

        font_size = self.font_m.pointSize()
        metrics = QFontMetrics(self.font_m)

        # 估算一行字符数
        a = max(1, round(metrics.horizontalAdvance(name) / max_width, 1)) # 估计行数
        b = metrics.height()# 字体高度
        d = 1.2 if font_size < 80 and len(name) < 6 else 2.2
        c = a * (b * d)# b*2考虑到字符行间隔

        # 如果文本换行后的高度超出了标签高度，逐步减小字体
        while c > max_height and font_size > 0:
            
            font_size -= 3
            self.font_m.setPointSize(font_size)
            self.label_3.setFont(self.font_m)
            metrics = QFontMetrics(self.font_m)
            b = metrics.height()
            d = 1.2 if font_size < 80 and len(name) < 6 else 2.2
            # 再次计算换行后估算行数
            a = max(1, round(metrics.horizontalAdvance(name) / max_width, 1))
            c = a * (b * d)

        origin_name_list = name
        self.label_3.setText(origin_name_list)
        # print(font_size,d)

    def show_message(self, message, title, first=None):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        if message is None:
            message = _("未知错误")
        message = str(message)
        if first == 1:
            msgBox.setIconPixmap(QtGui.QIcon(
                ':/icons/picker.ico').pixmap(64, 64))
        msgBox.setText(message)
        msgBox.exec_()

    def first_use_introduce(self):
        self.show_message(
            _("欢迎使用沉梦课堂点名器%s！\n\n此工具支持单抽(放回)、单抽(不放回)、连抽功能\n还有一些特色功能：语音播报、背景音乐、小窗模式\n\n进入主界面后，请点击左上角的设置按钮，按需开启功能，编辑名单\n如果遇到了问题，可以在沉梦小站中留言，或者在github上提交issues\n\n\t----Yish_") % dmversion, _("欢迎"), 1)
        self.update_config("first_use", 1)

    def tts_read(self, content, mode = None):
        try:
            if origin_name_list != "":
                if mode:
                    self.check_speaker = SpeakerThread(content, mode)
                else:
                    self.check_speaker = SpeakerThread(content)
                self.check_speaker.signals.update_list.connect(
                    self.update_list)
                self.check_speaker.signals.update_pushbotton.connect(
                    self.update_pushbotton)
                self.check_speaker.signals.enable_button.connect(
                    self.enable_button)
                self.check_speaker.signals.save_history.connect(
                    self.save_history)
                threadpool.start(self.check_speaker)
            else:
                print("名单文件为空！")
        except Exception as e:
            print(f"语音播报失败，原因：{e}")

    def dynamic_speed_preview(self, speed):
        try:
            self.timer.setInterval(speed)
        except:
            pass


class WorkerSignals(QObject):
    # 定义信号
    show_progress = pyqtSignal(int, int, int, str)
    update_list = pyqtSignal(int, str)
    update_pushbotton = pyqtSignal(str, int)
    find_new_version = pyqtSignal(str, str)
    enable_button = pyqtSignal(int)
    save_history = pyqtSignal()
    finished = pyqtSignal()
    qtimer = pyqtSignal(int)
    speakertest = pyqtSignal(int, str)
    key_space = pyqtSignal(int)
    change_speed = pyqtSignal(int)


class WorkerThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.name = name

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
        global running, default_music, roll_speed

        def stop():
            self.signals.update_pushbotton.emit(_(" 小窗模式"), 2)
            try:
                self.signals.save_history.emit()
            except:
                print(_("无法写入历史记录"))
            self.signals.update_list.emit(2, "")

            if non_repetitive == 1:
                if len(non_repetitive_list) > 0:
                    if origin_name_list in non_repetitive_list:
                        non_repetitive_list.remove(origin_name_list)
                    else:
                        print(f"不重复的单抽名单中没有{origin_name_list}")
                if namelen != 0:
                    if len(non_repetitive_list) == 1:
                        self.signals.update_list.emit(1, _("最终的幸运儿即将出现："))
                    elif len(non_repetitive_list) == 0:
                        self.signals.update_list.emit(
                            1, _("点击开始重置名单,或切换名单继续点名"))
                        self.signals.update_list.emit(0, _("此名单已完成抽取！"))

            if allownametts != 1:
                pass
            else:
                self.signals.enable_button.emit(1)

            self.signals.update_pushbotton.emit(_(" 开始"), 1)
            if namelen == 0:
                self.signals.enable_button.emit(1)

            self.signals.update_list.emit(7, "")

        if running:  # 结束按钮
            self.signals.update_pushbotton.emit(_(" 请稍后..."), 2)
            self.signals.enable_button.emit(3)
            self.signals.enable_button.emit(2)

            if bgmusic == 1 or pygame.mixer.music.get_busy():
                try:
                    if default_music == True:
                        pass
                    else:
                        pygame.mixer.music.fadeout(600)
                    pygame.mixer.music.unload()
                    try:
                        os.remove("tmp.cmxz")
                    except:
                        pass
                except Exception as e:
                    print(f"停止音乐播放时发生错误：{str(e)}")

            # debugpy.breakpoint()
            if inertia_roll == 1:
                if len(non_repetitive_list) == 1 or len(name_list) == 0:
                    print("不满足惯性滚动条件")
                else:
                    s = 50
                    speed = random.randint(roll_speed-30, roll_speed+30)
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
            running = False

            stop()
            self.signals.finished.emit()
            # 向主线程发送终止信号

        else:  # 开始按钮
            running = True
            self.signals.qtimer.emit(1)
            self.signals.enable_button.emit(6)  # 禁用人数选择框spinbox
            print("开始点名")
            if non_repetitive == 1 and len(non_repetitive_list) == 1:
                self.signals.show_progress.emit(1, 0, 0, "mulit_radius")
            else:
                self.signals.show_progress.emit(1, 0, 0, "default")
            self.signals.enable_button.emit(2)
            self.signals.key_space.emit(0)

            if len(name_list) != 0:
                if bgmusic == 1:
                    # debugpy.breakpoint()
                    folder_name = "dmmusic"
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    folder_path = os.path.join(current_dir, folder_name)
                    os.makedirs('dmmusic', exist_ok=True)
                    # 获取文件夹中的文件列表
                    file_list = os.listdir(folder_path)
                    if not file_list:
                        try:
                            if non_repetitive == 1 and len(non_repetitive_list) == 1:
                                mid_file = ['hyl.mid']
                            else:
                                mid_file = ['olg.mid', 'qqss.mid', 'april.mid', 'hyl.mid', 'hzt.mid',
                                            'lemon.mid', 'ltinat.mid', 'qby.mid', 'xxlg.mid', 'ydh.mid', 'level5.mid', 'zyzy.mid']
                            mid_load = random.choice(mid_file)
                            file_path = f":/mid/{mid_load}"
                            file = QFile(file_path)
                            file.open(QFile.ReadOnly)
                            ctypes.windll.kernel32.SetFileAttributesW(
                                "tmp.cmxz", 0x80)
                            with open("tmp.cmxz", "wb") as f:
                                f.write(file.readAll())
                            ctypes.windll.kernel32.SetFileAttributesW(
                                "tmp.cmxz", 2)
                            default_music = True

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

                            print(
                                "正在播放默认音频:%s\n请在 %s 中放入mp3格式的音乐" % (mid_load, folder_path))
                            self.signals.update_list.emit(
                                7, _("正在播放(默认音频):%s") % mid_load)
                        except Exception as e:
                            default_music = True
                            print("err: %s" % str(e))
                    else:
                        default_music = False
                    try:
                        self.signals.update_pushbotton.emit(_(" 加载音乐."), 2)
                        self.signals.enable_button.emit(3)

                        if default_music == True:
                            pygame.mixer.music.load("tmp.cmxz")
                            pygame.mixer.music.play(-1)
                        else:
                            random_file = random.choice(file_list)
                            file_path = os.path.join(folder_path, random_file)
                            pygame.mixer.music.load(file_path)
                            print("播放音乐：%s" % file_path)
                            sound = pygame.mixer.Sound(file_path)
                            music_length = sound.get_length()
                            random_play = round(random.uniform(2, 5), 1)
                            start_time = round(music_length / random_play, 1)
                            self.signals.update_pushbotton.emit(_(" 加载音乐.."), 2)
                            music_name = random_file.rsplit('.', 1)[0]
                            self.signals.update_list.emit(
                                7, _("正在播放:%s") % music_name)
                            self.volume = 0.0
                            pygame.mixer.music.set_volume(self.volume)
                            pygame.mixer.music.play(-1, start=start_time)
                            print(
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
                            print("音量淡入完成。")

                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)

                    except Exception as e:
                        self.signals.update_list.emit(7, _("无法播放：%s") % e)
                        print("无法播放音乐文件：%s，错误信息：%s" % (file_path, e))
                        self.signals.update_pushbotton.emit(_(" 结束"), 2)
                        self.signals.enable_button.emit(4)

            self.signals.update_pushbotton.emit(_(" 结束"), 2)
            self.signals.enable_button.emit(4)

            if non_repetitive == 1:
                self.signals.enable_button.emit(5)
                self.signals.update_pushbotton.emit(_(" 重置名单"), 1)


class UpdateThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        global newversion, checkupdate, latest_version, connect
        # debugpy.breakpoint()  # 在此线程启动断点调试
        headers = {
            'User-Agent': 'CMXZ-CRP_%s,%s,%s,%s,%s,%s%s_%s' % (dmversion, allownametts, bgimg, bgmusic, language_value, platform.system(), platform.release(), platform.machine())
        }
        print(headers)
        updatecheck = "https://cmxz.top/programs/dm/check.php"
        # try:
        #     check_mode = requests.get(
        #         updatecheck + "?mode", timeout=5, headers=headers)
        #     if int(check_mode.text) == 1:
        #         print("检测到强制更新版本，这意味着当前版本有严重bug，请更新至最新版本！")
        #         checkupdate = 2
        #         latest_version = 0
        # except:
        #     pass
        if checkupdate == 2:
            try:
                page = requests.get(updatecheck, timeout=5, headers=headers)
                newversion = float(page.text)
                print("云端版本号为:", newversion)
                findnewversion = _("检测到新版本！")
                if newversion > dmversion:# and float(latest_version) < newversion:
                    print("检测到新版本:", newversion,
                          "当前版本为:", dmversion)
                    new_version_detail = requests.get(
                        updatecheck + "?detail", timeout=5, headers=headers)
                    new_version_detail = new_version_detail.text
                    self.signals.find_new_version.emit(_("云端最新版本为%s，要现在下载新版本吗？<br>您也可以稍后访问沉梦小站官网获取最新版本。<br><br>%s") % (
                        newversion, new_version_detail), findnewversion)
                # else:
                #     if float(latest_version) == newversion and dmversion != newversion:
                #         print("\n已忽略%s版本更新,当前版本：%s" % (newversion, dmversion))
                #         findnewversion += _("(已忽略)")
                #         self.signals.update_list.emit(1, findnewversion)
                if newversion:
                    connect = True
            except Exception as e:
                print(f"网络异常,无法检测更新:{e}")
                noconnect = _("网络连接异常，检查更新失败")
                self.signals.update_list.emit(1, noconnect)

        elif checkupdate == 1:
            print("检查更新已关闭")

        self.signals.finished.emit()


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
        #     cust_font = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.font_s = QtGui.QFont(cust_font, 34)
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
        global origin_name_list
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
                if name != "":
                    if non_repetitive == 1:
                        non_repetitive_list.remove(self.small_window_name)
                        info = self.small_window_name + \
                            _(" (剩%s人)") % len(non_repetitive_list)
                        if len(non_repetitive_list) == 0:
                            self.font_s.setPointSize(29)
                            self.label_2.setFont(self.font_s)
                            self.label_2.setText(_("名单抽取完成"))
                            self.label_3.setText("")
                        else:
                            a = str(len(non_repetitive_list))
                            if a != "0":
                                self.label_3.setText(_("剩%s人") % a)
                    else:
                        info = self.small_window_name
                    self.main_instance.update_list(1, _("小窗：%s") % info)
                    origin_name_list = name
                    self.main_instance.tts_read(self.small_window_name, 2)
                else:
                    pass
            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        global name, non_repetitive_list, non_repetitive
        self.font_s.setPointSize(40)
        self.label_2.setFont(self.font_s)

        if non_repetitive == 1:
            if len(non_repetitive_list) == 0:
                non_repetitive_list = name_list.copy()
                self.main_instance.update_list(1, _("不放回名单已重置"))
            a = str(len(non_repetitive_list))
            if a != "0":
                self.label_3.setText(_("剩%s人") % a)

        if name_list == []:
            name = ""
            self.font_s.setPointSize(29)
            self.label_2.setFont(self.font_s)
            self.label_2.setText(_("名单为空!"))
            self.main_instance.mini(2)
            self.qtimer(0)
            try:
                self.main_instance.run_settings(f"1&{file_path}")
            except Exception as e:
                print(f"无法打开设置:{e}")
        

        else:
            try:
                if non_repetitive == 1:
                    name = random.choice(non_repetitive_list)
                else:
                    name = random.choice(name_list)
            except:
                pass

            font_size = self.font_s.pointSize()
            metrics = QFontMetrics(self.font_s)        
            max_width = self.label_2.width()
            max_height = self.label_2.height()

            # 估算一行字符数
            a = max(1, round(metrics.horizontalAdvance(name) / max_width, 1)) # 估计行数
            b = metrics.height()# 字体高度
            d = 1 if font_size < 80 and len(name) < 5 else 2
            c = a * (b * d)# b*2考虑到字符行间隔
            
            # 如果文本换行后的高度超出了标签高度，逐步减小字体
            while c > max_height and font_size > 0:
                
                font_size -= 3
                self.font_s.setPointSize(font_size)
                self.label_2.setFont(self.font_s)
                metrics = QFontMetrics(self.font_s)
                b = metrics.height()

                # 再次计算换行后估算行数
                a = max(1, round(metrics.horizontalAdvance(name) / max_width, 1))
                d = 1 if font_size < 80 and len(name) < 5 else 2
                c = a * (b * d)

            self.small_window_name = name
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
        global small_window_flag
        small_window_flag = None
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


class settingsWindow(QtWidgets.QMainWindow, Ui_Settings):  # 设置窗口
    def __init__(self, main_instance, target_tab = None):
        super().__init__()
        central_widget = QtWidgets.QWidget(self)  # 创建一个中央小部件
        self.setCentralWidget(central_widget)  # 设置中央小部件为QMainWindow的中心区域
        self.setupUi(central_widget)  # 初始化UI到中央小部件上
        self.setMinimumSize(675, 555)
        self.resize(675, 555)
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.setWindowFlags(self.windowFlags() & ~
                            QtCore.Qt.WindowMinimizeButtonHint)  # 禁止最小化

        current_range = self.horizontalSlider.value()
        self.label_6.setText(f"{current_range} ms")
        self.pushButton.setText(_("取消"))
        self.pushButton_2.setText(_("保存"))
        self.groupBox_3.setTitle(_("语言设置"))
        self.groupBox_6.setTitle(_("快捷访问"))
        self.pushButton_12.setText(_("名单文件目录"))
        self.pushButton_10.setText(_("背景音乐目录"))
        self.pushButton_8.setText(_("历史记录目录"))
        self.groupBox_5.setTitle(_("关于"))
        self.label_10.setText(_("Tips: 按下空格键可以快捷开始/结束！"))
        self.label_2.setText(_("沉梦课堂点名器 V%s") % dmversion)
        self.label_3.setText(_("<html><head/><body><p align=\"center\"><span style=\" font-size:7pt; text-decoration: underline;\">一个支持 单抽，连抽的课堂点名小工具</span></p><p align=\"center\"><br/></p><p align=\"center\"><span style=\" font-size:8pt; font-weight:600;\">Contributors: Yish1, QQB-Roy, limuy2022</span></p><p align=\"center\"><span style=\" font-size:7pt; font-weight:600; font-style:italic;\"><br/></span><a href=\"https://cmxz.top/ktdmq\"><span style=\" font-size:7pt; font-weight:600; font-style:italic; text-decoration: underline; color:#0000ff;\">沉梦小站</span></a></p><p align=\"center\"><a href=\"https://github.com/Yish1/Class-Roster-Picker-NEXT\"><span style=\" font-size:7pt; font-weight:600; font-style:italic; text-decoration: underline; color:#0000ff;\">Yish1/Class-Roster-Picker-NEXT: 课堂点名器</span></a></p><p align=\"center\"><span style=\" font-size:7pt;\"><br/></span></p></body></html>"))
        self.groupBox.setTitle(_("功能设置"))
        self.checkBox_4.setText(_("背景音乐"))
        self.checkBox_3.setText(_("检查更新"))
        self.checkBox.setText(_("不放回模式(单抽结果不重复)"))
        self.label_5.setText(_("名单滚动速度:"))
        self.radioButton.setText(_("正常模式"))
        self.radioButton_2.setText(_("听写模式(不说\"恭喜\")"))
        self.checkBox_5.setText(_("惯性滚动"))
        self.checkBox_2.setText(_("语音播报"))
        self.groupBox_7.setTitle(_("个性化设置"))
        self.label.setText(_("背景图片"))
        self.radioButton_3.setText(_("默认背景"))
        self.radioButton_4.setText(_("自定义"))
        self.radioButton_5.setText(_("无"))
        self.lineEdit.setPlaceholderText(_("幸运儿是:"))
        self.pushButton_9.setText(_("背景图片目录"))
        self.label_7.setText(_("启动时标题:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _("基本设置"))
        self.groupBox_2.setTitle(_("名单管理"))
        self.pushButton_3.setText(_("新建名单"))
        self.pushButton_4.setText(_("删除名单"))
        self.pushButton_15.setText(_("访问名单文件目录"))
        self.pushButton_13.setText(_("撤销未保存的修改"))
        self.pushButton_11.setText(_("保存修改"))
        self.label_8.setText(_("！！！编辑名单时请确保名字为 一行一个！！！"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _("名单管理"))
        self.groupBox_4.setTitle(_("历史记录列表"))
        self.pushButton_5.setText(_("统计所选历史记录"))
        self.pushButton_16.setText(_("访问历史记录目录"))
        self.pushButton_17.setText(_("删除历史记录"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _("历史记录"))
        self.pushButton_6.setText(_("反馈"))
        self.pushButton_14.setText(_("定制"))
        self.label_4.setText(_("<html><head/><body><p><span style=\" font-size:8pt;\">感谢您使用 沉梦课堂点名器！欢迎访问沉梦小站博客cmxz.top获取更多有趣的应用！</span></p><p><span style=\" font-size:8pt;\">                —— Yish_</span></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _("反馈/定制"))

        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", _("沉梦课堂点名器设置")))

        self.main_instance = main_instance
        self.read_name_list()
        self.read_config()
        self.find_langluge()
        self.find_history()
        self.slider_value_changed("init")

        self.enable_tts = None
        self.title_text = None
        self.enable_update = None
        self.enable_bgimg = None
        self.language_value = None
        self.disable_repetitive = None
        self.enable_bgmusic = None
        self.inertia_roll = None
        self.file_path_bak = None
        self.roll_speed = None
        self.file_path = None
        self.isload = None

        self.window = QWidget()
        self.window.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.pushButton.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.add_new_list)
        self.pushButton_4.clicked.connect(self.delete_file)
        self.pushButton_2.clicked.connect(self.save_settings)
        self.pushButton_5.clicked.connect(self.count_name)
        self.pushButton_6.clicked.connect(lambda: os.system(
            "start https://cmxz.top/ktdmq#toc-head-17"))
        self.comboBox_2.currentIndexChanged.connect(self.change_langluge)
        self.pushButton_12.clicked.connect(lambda: self.open_fold("name"))
        self.pushButton_15.clicked.connect(lambda: self.open_fold("name"))
        self.pushButton_10.clicked.connect(lambda: self.open_fold("dmmusic"))
        self.pushButton_9.clicked.connect(lambda: self.open_fold("images"))
        self.pushButton_8.clicked.connect(lambda: self.open_fold("history"))
        self.pushButton_11.clicked.connect(self.save_name_list)
        self.pushButton_13.clicked.connect(self.read_name_inlist)
        self.pushButton_14.clicked.connect(lambda: os.system(
            "start https://cmxz.top/ktdmq#toc-head-8"))
        self.pushButton_16.clicked.connect(lambda: self.open_fold("history"))
        self.pushButton_17.clicked.connect(lambda: self.delete_file("history"))
        self.listWidget.itemSelectionChanged.connect(self.read_name_inlist)
        self.listWidget_2.itemSelectionChanged.connect(
            lambda: self.find_history(1))
        self.tabWidget.currentChanged.connect(self.tab_changed)
        self.horizontalSlider.valueChanged.connect(self.slider_value_changed)

        self.checkBox.toggled.connect(
            lambda checked: self.process_config("disable_repetitive", checked))
        self.checkBox_2.toggled.connect(
            lambda checked: self.process_config("enable_tts", checked))
        self.radioButton.toggled.connect(
            lambda checked: self.process_config("enable_tts", checked))
        self.radioButton_2.toggled.connect(
            lambda checked: self.process_config("enable_tts", checked))
        self.checkBox_3.toggled.connect(
            lambda checked: self.process_config("enable_update", checked))
        self.checkBox_4.toggled.connect(
            lambda checked: self.process_config("enable_bgmusic", checked))
        self.checkBox_5.toggled.connect(
            lambda checked: self.process_config("inertia_roll", checked))
        self.radioButton_3.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))
        self.radioButton_4.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))
        self.radioButton_5.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))

        self.lineEdit.textChanged.connect(
            lambda text: self.process_config("title_text", text))

        self.pushButton_11.setEnabled(False)
        self.pushButton_13.setEnabled(False)
        self.pushButton_17.setEnabled(False)
        self.pushButton_5.setEnabled(False)
        self.label_9.hide()

        if target_tab and "&" in target_tab:
            try:
                target_tab, target_name = target_tab.split("&", 1)
                target_tab = int(target_tab)
                # 处理 target_name，去除 "name\" 和 ".txt"
                target_name = target_name.rsplit("\\", 1)[-1].rsplit(".", 1)[0]
                self.tabWidget.setCurrentIndex(target_tab)

                items = self.listWidget.findItems(target_name, QtCore.Qt.MatchContains)
                if items:
                    self.listWidget.setCurrentItem(items[0])

            except (ValueError, IndexError):
                pass

    def slider_value_changed(self, mode=None):
        global roll_speed
        self.label_9.show()
        self.label_9.setText(_("可以开始点名后调整滑块预览速度"))
        if mode == "init":
            self.horizontalSlider.setValue(roll_speed)
            self.label_6.setText(f"{roll_speed} ms")
        else:
            current_range = self.horizontalSlider.value()
            self.label_6.setText(
                f"{current_range} ms")

            self.process_config("roll_speed", current_range)
            self.main_instance.dynamic_speed_preview(current_range)

    def tab_changed(self, index):
        if index != 0:
            self.frame.hide()
            if index == 1:
                self.file_path = self.file_path_bak
        else:
            self.frame.show()

    def read_name_list(self):
        txt_files_name = self.main_instance.read_name_list(1)
        self.listWidget.addItems(txt_files_name)  # 添加文件名到列表

    def refresh_name_list(self):
        txt_name = [filename for filename in os.listdir(
            "name") if filename.endswith(".txt")]
        txt_files_name = [os.path.splitext(
            filename)[0] for filename in txt_name]

        return txt_files_name

    def read_name_inlist(self):

        selected_items = self.listWidget.selectedItems()

        if not selected_items:
            self.pushButton_11.setEnabled(False)
            self.pushButton_13.setEnabled(False)
            return
        else:
            self.pushButton_11.setEnabled(True)
            self.pushButton_13.setEnabled(True)

        # 获取列表选择的文件
        for item in selected_items:
            selected_text_inlist = item.text()

        self.file_path = os.path.join("name", selected_text_inlist+".txt")

        if not self.file_path or not os.path.isfile(self.file_path):
            return

        else:
            file_content = self.read_txt()
            lines = file_content.splitlines()
            non_empty_lines = [line for line in lines if line.strip()]
            file_content = "\n".join(non_empty_lines)
            self.textEdit.setPlainText(file_content)
            self.file_path_bak = self.file_path

    def read_txt(self):
        file_content = None
        try:
            # 打开文件并读取内容
            with open(self.file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            # 打开文件并读取内容
            with open(self.file_path, 'r', encoding='gbk') as f:
                file_content = f.read()
        finally:
            return file_content

    def add_new_list(self):
        newfilename, ok_pressed = QInputDialog.getText(
            self.window, _("新增名单"), _("请输入名单名称:"))
        if ok_pressed and newfilename:
            newnamepath = os.path.join(
                "name", f"{newfilename}.txt")  # 打开文件并写入内容
            if not os.path.exists(newnamepath):
                print("新增名单名称是: %s" % newfilename)
                with open(newnamepath, "w", encoding="utf8") as file:
                    file.write("")
                message = (_("已创建名为 '%s.txt' 的文件，路径为: %s\n\n请在稍后打开的文本中输入名单内容，一行一个名字，不要出现空格！") %
                           (newfilename, newnamepath))
                QMessageBox.information(
                    self.window, _("新建成功"), message, QMessageBox.Ok)
            else:
                self.main_instance.show_message(
                    _("Error: 同名文件已存在，请勿重复创建！"), _("错误"))
            txt_name = self.refresh_name_list()
            self.listWidget.clear()  # 清空下拉框的选项
            self.listWidget.addItems(txt_name)  # 添加新的文件名到下拉框

    def delete_file(self, mode=None):
        if mode == "history":
            target_folder = "history"
            text1 = _("删除历史记录")
            text2 = _("输入要删除的历史记录名称：(无需输入\"中奖记录\")")
        else:
            target_folder = "name"
            text1 = _("删除名单")
            text2 = _("输入要删除的名单名称：")

        target_filename, ok_pressed = QInputDialog.getText(
            self.window, text1, text2)

        target_filename += "中奖记录" if mode == "history" else ""

        if ok_pressed and target_filename:
            target_filepath = os.path.join(
                target_folder, f"{target_filename}.txt")
            try:
                os.remove(target_filepath)  # 删除文件
                message = (_("已成功删除文件： '%s.txt' ") % target_filename)
                QMessageBox.information(
                    self.window, _("删除成功"), message, QMessageBox.Ok)
                txt_name = self.refresh_name_list()
                self.listWidget.clear()  # 清空下拉框的选项
                self.listWidget.addItems(txt_name)  # 添加新的文件名到下拉框
            except Exception as e:
                QMessageBox.warning(
                    self.window, _('错误'), _('Error: 目标文件不存在，或已被删除！\n%s') % e, QMessageBox.Ok)

        if mode == "history":
            self.listWidget_2.clear()
            self.find_history()

    def save_name_list(self):
        current_name = self.textEdit.toPlainText()
        current_name_count = len(current_name.splitlines())

        if os.path.isfile(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    original_name = f.read()
            except Exception as e:
                self.main_instance.show_message(
                    _("Error: 无法读取源文件！\n%s" % e), _("错误"))
                return

        change_message = ""
        # 去除内容中的空行
        current_lines = [
            line for line in original_name.splitlines() if line.strip()]
        original_lines = [
            line for line in current_name.splitlines() if line.strip()]
        diff = difflib.unified_diff(
            current_lines, original_lines)
        diff_str = '\n'.join(diff)
        diff_str = diff_str[11:]

        minus_lines = []
        plus_lines = []

        text = diff_str.strip().split('\n')
        for lines in text:
            lines = lines.strip()  # 去掉行首尾的空白字符
            if lines.startswith('-'):
                minus_lines.append(lines[1:].strip())
            elif lines.startswith('+'):
                plus_lines.append(lines[1:].strip())

        if plus_lines:
            formatted_plus = '\n'.join(', '.join(
                f'"{item}"' for item in plus_lines[i:i+8]) for i in range(0, len(plus_lines), 8))
            change_message += _("新增了：\n%s\n\n") % formatted_plus

        if minus_lines:
            formatted_minus = '\n'.join(', '.join(
                f'"{item}"' for item in minus_lines[i:i+8]) for i in range(0, len(minus_lines), 8))
            change_message += _("删除了：\n%s\n\n") % formatted_minus

        if change_message == "":
            change_message = _("未进行任何修改。\n\n")

        text = _("您正在保存文件：\"%s\" |修改后的名单中共有 %s 个名字|与源文件相比:|%s") % (
            os.path.basename(self.file_path), current_name_count, change_message)
        msg = msgbox(text)
        msg.exec_()

        if msg.get_result() == 1:
            try:
                # 写入文件内容
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(current_name)
                self.main_instance.show_message(_("名单保存成功！"), _("提示"))
            except Exception as e:
                self.main_instance.show_message(
                    _("Error: 名单保存出现错误！\n%s" % e), _("错误"))
        elif msg.get_result() == 0:
            self.main_instance.show_message(_("已取消保存！"), _("提示"))

    def find_history(self, mode=None):
        if mode == 1:
            # Read模式
            selected_items = self.listWidget_2.selectedItems()
            if not selected_items:
                self.pushButton_5.setEnabled(False)
                self.pushButton_17.setEnabled(False)
                return
            else:
                self.pushButton_5.setEnabled(True)
                self.pushButton_17.setEnabled(True)

            # 获取列表选择的文件
            for item in selected_items:
                selected_text_inlist = item.text()

            self.file_path = os.path.join(
                "history", selected_text_inlist+".txt")

            if not self.file_path or not os.path.isfile(self.file_path):
                return

            else:
                file_content = self.read_txt()
                self.textEdit_2.setPlainText(file_content)

        else:
            # Find模式，读取指定目录下的文件夹名
            history_dir = "./history"
            try:
                if os.path.exists(history_dir) and os.path.isdir(history_dir):
                    history_file = [filename for filename in os.listdir(
                        history_dir) if filename.endswith(".txt")]
                    history_files_name = [os.path.splitext(
                        filename)[0] for filename in history_file]
                    if not history_files_name:
                        return

                    self.listWidget_2.addItems(history_files_name)
                else:
                    print(f"目录不存在: {history_dir}")
            except Exception as e:
                print(f"读取历史文件夹失败: {e}")

    def find_langluge(self):
        locale_dir = "./locale"
        try:
            if os.path.exists(locale_dir) and os.path.isdir(locale_dir):
                folders = [folder for folder in os.listdir(
                    locale_dir) if os.path.isdir(os.path.join(locale_dir, folder))]
                self.comboBox_2.addItems(folders)
                self.comboBox_2.setCurrentText(language_value)
        except Exception as e:
            print(f"读取语言失败:{e}")

    def change_langluge(self):
        """Change language at runtime without restart."""
        try:
            self.language_value = self.comboBox_2.currentText()
            # Set module-level gettext to new language
            set_language(self.language_value)
            # Persist selection to config
            update_entry('language', self.language_value)
            # Refresh main window and settings window texts
            try:
                self.main_instance.apply_translations()
            except Exception as e:
                log_print(f"Error applying main window translations: {e}")
            try:
                self.apply_translations()
            except Exception as e:
                log_print(f"Error applying settings translations: {e}")
        except Exception as e:
            self.main_instance.show_message(str(e), "Error")

    def closeEvent(self, event):
        print("设置被关闭")
        try:
            self.main_instance.mini(2)
            self.main_instance.read_name_list()
            self.main_instance.get_selected_file(0)
        except Exception as e:
            print(e)
        global settings_flag
        settings_flag = None
        event.accept()  # 确保仅关闭子窗口，不影响主窗口

    def run_settings_window(self):
        self.show()
        return self

    def apply_translations(self):
        """Refresh texts in the settings window after a language change."""
        try:
            current_range = self.horizontalSlider.value()
            self.label_6.setText(f"{current_range} ms")
            self.pushButton.setText(_("取消"))
            self.pushButton_2.setText(_("保存"))
            self.groupBox_3.setTitle(_("语言设置"))
            self.groupBox_6.setTitle(_("快捷访问"))
            self.pushButton_12.setText(_("名单文件目录"))
            self.pushButton_10.setText(_("背景音乐目录"))
            self.pushButton_8.setText(_("历史记录目录"))
            self.groupBox_5.setTitle(_("关于"))
            self.label_10.setText(_("Tips: 按下空格键可以快捷开始/结束！"))
            self.label_2.setText(_("沉梦课堂点名器 V%s") % dmversion)
            self.groupBox.setTitle(_("功能设置"))
            self.checkBox_4.setText(_("背景音乐"))
            self.checkBox_3.setText(_("检查更新"))
            self.checkBox.setText(_("不放回模式(单抽结果不重复)"))
            self.label_5.setText(_("名单滚动速度:"))
            self.radioButton.setText(_("正常模式"))
            self.radioButton_2.setText(_("听写模式(不说\"恭喜\")"))
            self.checkBox_5.setText(_("惯性滚动"))
            self.checkBox_2.setText(_("语音播报"))
            self.groupBox_7.setTitle(_("个性化设置"))
            self.label.setText(_("背景图片"))
            self.radioButton_3.setText(_("默认背景"))
            self.radioButton_4.setText(_("自定义"))
            self.radioButton_5.setText(_("无"))
            self.lineEdit.setPlaceholderText(_("幸运儿是:"))
            self.pushButton_9.setText(_("背景图片目录"))
            self.label_7.setText(_("启动时标题:"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _("基本设置"))
            self.groupBox_2.setTitle(_("名单管理"))
            self.pushButton_3.setText(_("新建名单"))
            self.pushButton_4.setText(_("删除名单"))
            self.pushButton_15.setText(_("访问名单文件目录"))
            self.pushButton_13.setText(_("撤销未保存的修改"))
            self.pushButton_11.setText(_("保存修改"))
            self.label_8.setText(_("！！！编辑名单时请确保名字为 一行一个！！！"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _("名单管理"))
            self.groupBox_4.setTitle(_("历史记录列表"))
            self.pushButton_5.setText(_("统计所选历史记录"))
            self.pushButton_16.setText(_("访问历史记录目录"))
            self.pushButton_17.setText(_("删除历史记录"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _("历史记录"))
            self.pushButton_6.setText(_("反馈"))
            self.pushButton_14.setText(_("定制"))
            self.label_4.setText(_("感谢您使用 沉梦课堂点名器！欢迎访问沉梦小站博客cmxz.top获取更多有趣的应用！\n                —— Yish_"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _("反馈/定制"))
            self.setWindowTitle(QCoreApplication.translate(
                "MainWindow", _("沉梦课堂点名器设置")))
        except Exception as e:
            log_print(f"settings apply_translations error: {e}")

    def read_config(self):
        if allownametts == 2:
            self.checkBox_2.setChecked(True)
            self.radioButton.setChecked(True)
            self.radioButton_2.setChecked(False)
        elif allownametts == 3:
            self.checkBox_2.setChecked(True)
            self.radioButton.setChecked(False)
            self.radioButton_2.setChecked(True)
        elif allownametts == 1 or allownametts == 0:
            self.checkBox_2.setChecked(False)
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)

        if checkupdate == 2:
            self.checkBox_3.setChecked(True)
        else:
            self.checkBox_3.setChecked(False)

        if bgimg == 1:
            self.radioButton_3.setChecked(True)
            self.radioButton_4.setChecked(False)
            self.radioButton_5.setChecked(False)
        elif bgimg == 2:
            self.radioButton_3.setChecked(False)
            self.radioButton_4.setChecked(True)
            self.radioButton_5.setChecked(False)
        elif bgimg == 3:
            self.radioButton_3.setChecked(False)
            self.radioButton_4.setChecked(False)
            self.radioButton_5.setChecked(True)

        if non_repetitive == 1:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

        if bgmusic == 1:
            self.checkBox_4.setChecked(True)
        elif bgmusic == 0:
            self.checkBox_4.setChecked(False)

        if inertia_roll == 1:
            self.checkBox_5.setChecked(True)
        else:
            self.checkBox_5.setChecked(False)

        if title_text:
            self.lineEdit.setText(title_text)

    def open_fold(self, value):
        os.makedirs(value, exist_ok=True)
        self.main_instance.opentext(value)

    def process_config(self, key, checked):
        if key == "enable_tts":
            if checked and self.checkBox_2.isChecked():
                if self.radioButton_2.isChecked() or self.radioButton.isChecked():
                    self.radioButton.setEnabled(True)
                    self.radioButton_2.setEnabled(True)

                # 如果两个 radioButton 都没有被选中，默认选中 radioButton
                if checked and not self.radioButton.isChecked() and not self.radioButton_2.isChecked():
                    self.checkBox_2.setText(_("正在检测兼容性..."))
                    self.check_speaker = SpeakerThread("1", 1)
                    threadpool.start(self.check_speaker)

                    def spearker_test(result, e):
                        if result == 1:
                            self.radioButton.setEnabled(True)
                            self.radioButton_2.setEnabled(True)
                            self.radioButton.setChecked(True)
                        else:
                            self.main_instance.show_message(
                                _("Error: 语音播报无法在此设备上开启，可能是您使用的系统为精简版，删除了自带的语音库！\n%s") % e, _("错误"))
                            self.checkBox_2.setChecked(False)
                            self.radioButton.setEnabled(False)
                            self.radioButton_2.setEnabled(False)
                        self.checkBox_2.setText(_("语音播报"))
                    self.check_speaker.signals.speakertest.connect(
                        spearker_test)

                # 检查选中的情况并设置 enable_tts
                if checked and self.radioButton.isChecked() and not self.radioButton_2.isChecked():
                    print("正在开启播报正常模式")
                    self.enable_tts = 1
                elif checked and not self.radioButton.isChecked() and self.radioButton_2.isChecked():
                    print("正在开启播报听写模式")
                    self.enable_tts = 2

            elif not self.checkBox_2.isChecked():
                self.radioButton.setEnabled(False)
                self.radioButton_2.setEnabled(False)
                print("正在关闭播报")
                self.enable_tts = 0

        elif key == "enable_update":
            self.enable_update = 2 if checked else 1
            if not checked:
                self.main_instance.show_message(
                    _("您正在关闭检查更新功能！更新意味着带来 新功能、优化 以及修复错误，强烈建议您开启此功能！"), _("警告"))
                print("正在关闭检查更新")
            else:
                print("正在开启检查更新")

        elif key == "enable_bgimg":
            if checked:
                if self.radioButton_3.isChecked():
                    self.enable_bgimg = 1
                    print("背景1")
                elif self.radioButton_4.isChecked():
                    self.enable_bgimg = 2
                    self.main_instance.show_message(
                        _("您正在使用自定义背景功能，由于此工具可能需要在公众场合展示，请选择适宜场景的合适背景！ \n因使用不合适的背景图片而造成的后果由您自行承担！\n\n使用教程：\n\n在稍后打开的\\images文件夹中放入您喜欢的图片(建议暗色系、长宽比16:9)，程序将随机选取图片使用。"), _("声明!"))
                    os.makedirs("images", exist_ok=True)
                    self.main_instance.opentext("images")
                    print("背景自定义")
                elif self.radioButton_5.isChecked():
                    self.enable_bgimg = 3
                    print("背景无")

        elif key == "disable_repetitive":
            self.disable_repetitive = 1 if checked else 0
            if not checked:
                print("正在关闭不放回模式")
            else:
                print("正在开启不放回模式")
                self.main_instance.show_message(
                    _("不放回模式，即单抽结束后的名字不会放回列表中，下次将不会抽到此名字\n\n当名单抽取完成、切换名单 或 手动点击按钮 时将会重置不放回列表！"), _("说明"))

        elif key == "enable_bgmusic":
            self.enable_bgmusic = 1 if checked else 0
            if not checked:
                print("正在关闭背景音乐")
            else:
                print("正在开启背景音乐")
                self.main_instance.show_message(
                    _("开启背景音乐功能后，需要在稍后打开的背景音乐目录下放一些您喜欢的音乐\n程序将随机选取一首，播放随机的音乐进度\n\n注：程序自带几首默认音频，当您在音乐目录下放入音乐后，默认音频将不会再进入候选列表！"), _("提示"))
                self.open_fold("dmmusic")

        elif key == "inertia_roll":
            self.inertia_roll = 1 if checked else 0
            if not checked:
                print("正在关闭惯性滚动")
            else:
                print("正在开启惯性滚动")

        elif key == "title_text":
            self.title_text = checked

        elif key == "roll_speed":
            self.roll_speed = checked

    def save_settings(self):
        if self.enable_tts == 1:
            self.main_instance.update_config("allownametts", 2)
        elif self.enable_tts == 2:
            self.main_instance.update_config("allownametts", 3)
        elif self.enable_tts == 0:
            self.main_instance.update_config("allownametts", 1)

        if self.enable_update == 2:
            self.main_instance.update_config("checkupdate", 2)
        elif self.enable_update == 1:
            self.main_instance.update_config("checkupdate", 1)

        if self.enable_bgimg == 1:
            self.main_instance.update_config("bgimg", 1)
        elif self.enable_bgimg == 2:
            self.main_instance.update_config("bgimg", 2)
        elif self.enable_bgimg == 3:
            self.main_instance.update_config("bgimg", 3)

        if self.language_value is not None:
            self.main_instance.update_config("language", self.language_value)

        if self.disable_repetitive == 1:
            self.main_instance.update_config("non_repetitive", 1)
        elif self.disable_repetitive == 0:
            self.main_instance.update_config("non_repetitive", 0)

        if self.enable_bgmusic == 1:
            self.main_instance.update_config("bgmusic", 1)
        elif self.enable_bgmusic == 0:
            self.main_instance.update_config("bgmusic", 0)

        if self.inertia_roll == 1:
            self.main_instance.update_config("inertia_roll", 1)
        elif self.inertia_roll == 0:
            self.main_instance.update_config("inertia_roll", 0)

        if self.title_text:
            self.main_instance.update_config("title_text", self.title_text)

        if self.roll_speed:
            self.main_instance.update_config("roll_speed", self.roll_speed)

        self.close()

    def count_name(self):
        name_counts = {}  # 存储名字出现次数的字典

        selected_items = self.listWidget_2.selectedItems()
        self.listWidget_2.setCurrentItem(None)

        if not selected_items:
            print("未知错误")
            return

        for item in selected_items:
            count_target = item.text()

        file = "history/%s.txt" % count_target
        try:
            with open(file, encoding="utf-8") as file:
                for line in file:
                    if "幸运儿是：" in line:
                        cnames = line.split("幸运儿是：")[1].strip().strip("[]'")
                        cnames = cnames.split("', '")
                        for cname in cnames:
                            if cname not in name_counts:
                                name_counts[cname] = 1
                            else:
                                name_counts[cname] += 1
            sorted_counts = sorted(name_counts.items(),
                                   key=lambda x: x[1], reverse=True)
            # 保存文本
            print("正在保存为文本")
            cresult = _("\"%s\" 名单中奖统计:\n\n" %
                        (count_target.replace("中奖记录", "")))
            for name, count in sorted_counts:
                cresult += "%s 出现了 %s 次\n" % (name, count)
                with open('中奖统计.txt', 'w', encoding="utf-8") as file:
                    file.write(cresult)

            self.textEdit_2.setPlainText(
                _("统计已保存至安装目录下的/中奖统计.txt中\n(每次统计会覆盖上一次统计结果)\n\n")+cresult)

        except Exception as e:
            print("读取文件时发生错误:", e)
            self.main_instance.show_message(
                _("Error: 历史记录文件不存在，无法统计次数！\n%s") % e, _("错误"))


class SpeakerThread(QRunnable):
    def __init__(self, content, mode=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.mode = mode
        self.allownametts = allownametts
        self.content = content

    def ttsread(self, text, volume=None):
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        # for voice in speaker.GetVoices(): # 查询本机所有语言
        #     print(voice.GetDescription())
        try:
            if language_value == "en_US":
                speaker.Voice = speaker.GetVoices(
                    "Name=Microsoft Zira Desktop").Item(0)
            else:
                speaker.Voice = speaker.GetVoices(
                    "Name=Microsoft Huihui Desktop").Item(0)
        except Exception as e:
            print("无法切换语音语言，Reason：", e)

        if volume is not None:
            speaker.Volume = volume
        speaker.Speak(text)

    def run(self):
        # debugpy.breakpoint()  # 在此线程启动断点调试
        if self.mode == 1:
            try:
                self.ttsread("1", 0)
                print("此设备系统支持语音播报功能！")
                self.signals.speakertest.emit(1, "")
            except Exception as e:
                print("此设备系统不支持语音播报功能！Reason：", e)
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
                print("语音播报出现错误！Reason：", e)

        self.signals.finished.emit()


class FrameWithLines(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.border_radius = 28  # 圆角半径

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter(self)

        # 设置裁剪区域，带圆角的矩形
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(self.rect())  # 将 QRect 转换为 QRectF
        path.addRoundedRect(rect, self.border_radius, self.border_radius)
        painter.setClipPath(path)

        # 设置遮罩画笔
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 90))  # 半透明黑色
        pen.setWidth(int(1.3))  # 横线宽度
        painter.setPen(pen)

        # 绘制横线，确保在圆角矩形内
        line_spacing = int(3.0)  # 横线间距
        y = 0
        while y < self.height():
            painter.drawLine(0, y, self.width(), y)
            y += line_spacing

        # 绘制右下角的直角标志
        marker_color = QtGui.QColor(140, 140, 140)
        marker_pen = QtGui.QPen(marker_color)
        marker_pen.setWidth(int(2.6))  # 设置线条宽度
        painter.setPen(marker_pen)

        # 设置直角的起点和终点
        line_length = 13  # 直角标志的长度
        margin = 20
        x_start = self.width() - margin - line_length  # 水平线起点
        y_start = self.height() - margin - line_length  # 垂直线起点

        # 水平线
        painter.drawLine(x_start, self.height() - margin,
                         self.width() - margin, self.height() - margin)
        # 垂直线
        painter.drawLine(self.width() - margin, y_start,
                         self.width() - margin, self.height() - margin)

        painter.end()


class msgbox(QtWidgets.QDialog, Ui_msgbox):  # 保存弹窗
    def __init__(self, text):
        super().__init__()

        self.setWindowModality(QtCore.Qt.ApplicationModal)  # 设置为模态窗口
        self.setupUi(self)  # 初始化UI到这个中央控件
        self.setWindowTitle(_("保存确认"))
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))

        self.pushButton.setText(_("确认保存"))
        self.pushButton_2.setText(_("取消"))
        self.label.setText(_("您正在保存:xxx"))
        self.label_2.setText(_("修改后的名单中共有xxx个名字"))
        self.label_3.setText(_("与源文件相比："))

        text_list = text.split("|")

        self.label.setText(text_list[0])
        self.label_2.setText(text_list[1])
        self.label_3.setText(text_list[2])
        self.textBrowser.setText(text_list[3])
        self.pushButton_2.clicked.connect(self.cancel)
        self.pushButton.clicked.connect(self.save)

        self.result = None

    def cancel(self):
        self.result = 0
        self.close()

    def save(self):
        self.result = 1
        self.close()

    def get_result(self):
        return self.result


if __name__ == "__main__":
    try:
        # 防止重复运行
        lock_file = os.path.expanduser("~/.Class_Roster_Picker_lock")
        fd = os.open(lock_file, os.O_RDWR | os.O_CREAT)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError:
            os.close(fd)
            user32 = ctypes.windll.user32
            result = user32.MessageBoxW(
                None,
                "另一个点名器正在运行。\n是否继续运行？\n\nAnother CRP is already running.\nDo you want to continue?",
                "Warning!",
                0x31
            )
            if result == 2:
                sys.exit()  # 退出程序
            elif result == 1:
                print("用户选择继续运行。")

        if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_EnableHighDpiScaling, True)
        # 启用高DPI自适应
        if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_UseHighDpiPixmaps, True)

        # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-logging --v=0"  # 禁止日志输出
        # os.environ["QTWEBENGINE_DISABLE_SYSTEM_PROXY"] = "1"  # 关闭系统代理
        # os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] += " --use-angle=gl --ignore-gpu-blacklist"  # 启用 OpenGL 后端，忽略 GPU 黑名单
        # QCoreApplication.setAttribute(Qt.AA_UseOpenGLES)
        # 以上是集成70mb的 QtWebEngine 的解决方案，已弃用

        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        user32 = ctypes.windll.user32
        user32.MessageBoxW(None, f"程序启动时遇到严重错误:{e}", "Warning!", 0x30)
        sys.exit()
