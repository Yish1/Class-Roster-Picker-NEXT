# -*- coding: utf-8 -*-
import sys
import random
import os
import ctypes
import msvcrt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor, QFontMetrics, QKeySequence, QFontDatabase, QFont
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QFile, QThreadPool, pyqtSignal, QRunnable, QObject, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QScroller, QShortcut, QSizePolicy

from Ui import * 
from moudles import *
from window import *

from window.Setting import SettingsWindow

# import debugpy
# debugpy.listen(("0.0.0.0", 5678))
# debugpy.wait_for_client()  # 等待调试器连接

# 初始化全局应用状态
state = app_state

# 初始化 AppData 路径
state.appdata_path = os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP')
os.makedirs(state.appdata_path, exist_ok=True)
os.makedirs(os.path.join(state.appdata_path, 'history'), exist_ok=True)
os.makedirs(os.path.join(state.appdata_path, 'name'), exist_ok=True)
os.makedirs(os.path.join(state.appdata_path, 'dmmusic'), exist_ok=True)

# 初始化日志
init_log(os.path.join(state.appdata_path, 'log.txt'))

# init i18n with config language if present
try:
    config_path = os.path.join(state.appdata_path, 'config.ini')
    _config_boot = read_config_file(config_path)
    state.language_value = _config_boot.get('language', 'zh_CN')
    init_gettext(state.language_value)
except Exception as e:
    try:
        init_gettext('zh_CN')
    except Exception as e2:
        user32 = ctypes.windll.user32
        user32.MessageBoxW(None, f"程序启动时遇到严重错误:{e2}", "Warning!", 0x30)

# 设置默认名单（需要翻译）
state.default_name_list = _("默认名单")


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
        self.spinBox.setValue(1)
        self.label_7.setText("")
        self.progressBar.hide()
        self.commandLinkButton.hide()

        # 加载翻译
        self.apply_translations()

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
        if state.first_use == 0:
            self.first_use_introduce()


    def init_font(self):
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
            state.cust_font = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.font_m = QFont(state.cust_font, 52)

            self.label_3.setFont(self.font_m)
            self.pushButton_2.setFont(self.font_m)
            self.pushButton_5.setFont(self.font_m)
        else:
            log_print("字体加载失败")
        self.label_3.setText(state.title_text)

    def apply_translations(self):
        """Update runtime UI texts to the current language."""
        try:
            self.setWindowTitle(QCoreApplication.translate(
                "MainWindow", _("沉梦课堂点名器 %s") % state.dmversion))
            self.pushButton_2.setText(_(" 开始"))
            self.pushButton_5.setText(_(" 小窗模式"))
            self.label_5.setText(_("当前名单："))
            self.label_4.setText(_("抽取人数："))
            # Update background label if needed
            if state.bgimg == 2:
                self.label_6.setText(_("自定义背景"))
            # Update title text from config
            if state.title_text:
                self.label_3.setText(state.title_text)
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
            state.windows_move_flag = True
        else:
            state.windows_move_flag = False

    def set_bgimg(self):
        self.label_6.setText("")
        if state.bgimg == 2:
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
        elif state.bgimg == 1 or state.bgimg == 0:
            self.frame.setStyleSheet("#frame {\n"
                                     "border-image: url(:/images/bg.webp);"
                                     "border-radius: 28px;"
                                     "}")
        elif state.bgimg == 3:
            self.frame.setStyleSheet("#frame {\n"
                                     "background-color: rgba(42, 45, 47, 0.92);\n"
                                     "border-radius: 28px;"
                                     "}")

    def small_mode(self):
        # 保留对子窗口实例的引用
        if state.small_window_flag is None:
            self.showMinimized()
            small_Window = smallWindow(self)
            state.small_window_flag = small_Window.run_small_window()

    def run_settings(self, target_tab = None):
        if state.settings_flag is None:
            if target_tab:
                settings_window = SettingsWindow(self, target_tab)
            else:
                settings_window = SettingsWindow(self)
            state.settings_flag = settings_window.run_settings_window()

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
        state.name_path = os.path.join(
            state.appdata_path, "name", f"{state.default_name_list}.txt")  # 打开文件并写入内容
        with open(state.name_path, "w", encoding="utf8") as f:
            for i in name_list:
                f.write(i)
                f.write("\n")
                f.write("\n")

    def read_name_list(self, mode=None):
        folder_name = os.path.join(state.appdata_path, "name")
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
                self.comboBox.setCurrentText(state.last_name_list)
            except:
                pass
            self.comboBox.currentIndexChanged.connect(
                lambda: self.get_selected_file(0))
            if mode == 2:
                self.get_selected_file(1)
            else:
                pass

    def get_selected_file(self, first=None):
        # 获取当前选中的文件名
        state.selected_file = self.comboBox.currentText()
        self.update_config("last_name_list", state.selected_file)
        state.file_path = os.path.join(state.appdata_path, "name", state.selected_file+".txt")
        state.history_file = os.path.join(state.appdata_path, "history", "%s中奖记录.txt" % state.selected_file)
        if not os.path.exists(state.file_path):
            self.show_message(_("所选名单文件已被移动或删除！"), _("找不到文件！"))
            try:
                self.comboBox.setCurrentIndex(0)
            except:
                log_print("first_run")
        else:
                log_print(f"所选文件的路径为: {state.file_path}\n")
        self.process_name_file(state.file_path)
        if first == 1:
            info = _("\'%s'，共 %s 人") % (state.selected_file, state.namelen)
            if state.non_repetitive == 1:
                info += _("(不放回)")
            self.listWidget.addItem(info)

        if first == 0:
            info = _("切换至>\'%s\' 共 %s 人") % (state.selected_file, state.namelen)
            if state.non_repetitive == 1:
                info += _("(不放回)")
            self.listWidget.addItem(info)
            self.listWidget.setCurrentRow(self.listWidget.count() - 1)

    def read_config(self):
        config = {}
        config_path = os.path.join(state.appdata_path, 'config.ini')
        if not os.path.exists(config_path):
            with open(config_path, 'w', encoding='utf-8') as file:
                file.write("")

        config = read_config_file(config_path)
        try:
            state.language_value = config.get('language') if config.get(
                'language') else self.update_config("language", "zh_CN", "w!")
            state.allownametts = int(config.get('allownametts')) if config.get(
                'allownametts') else self.update_config("allownametts", 1, "w!")
            state.checkupdate = int(config.get('checkupdate')) if config.get(
                'checkupdate') else self.update_config("checkupdate", 2, "w!")
            state.bgimg = int(config.get('bgimg')) if config.get(
                'bgimg') else self.update_config("bgimg", 1, "w!")
            state.last_name_list = config.get('last_name_list') if config.get(
                'last_name_list') else self.update_config("last_name_list", "None", "w!")
            state.latest_version = config.get('latest_version') if config.get(
                'latest_version') else self.update_config("latest_version", 0, "w!")
            state.non_repetitive = int(config.get('non_repetitive')) if config.get(
                'non_repetitive') else self.update_config("non_repetitive", 1, "w!")
            state.bgmusic = int(config.get('bgmusic')) if config.get(
                'bgmusic') else self.update_config("bgmusic", 0, "w!")
            state.first_use = int(config.get('first_use')) if config.get(
                'first_use') else self.update_config("first_use", 0, "w!")
            state.inertia_roll = int(config.get('inertia_roll')) if config.get(
                'inertia_roll') else self.update_config("inertia_roll", 1, "w!")
            state.roll_speed = int(config.get('roll_speed')) if config.get(
                'roll_speed') else self.update_config("roll_speed", "80", "w!")
            state.title_text = config.get('title_text') if config.get(
                'title_text') else _("幸运儿是:")

        except Exception as e:
            log_print(f"配置文件读取失败，已重置无效为默认值！{e}")
            self.show_message(_("配置文件读取失败，已重置为默认值！\n%s") % e, _("读取配置文件失败！"))
            os.remove(config_path)
            self.read_config()
        return config

    def update_config(self, variable, new_value, mode=None):
        # delegate to config manager
        config_path = os.path.join(state.appdata_path, 'config.ini')
        update_entry(variable, str(new_value) if new_value is not None else None, config_path)
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
                self.dynamic_speed_preview(state.roll_speed)
            except:
                pass

    def process_name_file(self, file_path):
        try:
            with open(file_path, encoding='utf8') as f:
                # 读取每一行，去除行尾换行符，过滤掉空行和仅包含空格的行
                state.name_list = [line.strip()
                             for line in f.readlines() if line.strip()]
        except:
            log_print("utf8解码失败，尝试gbk")
            try:
                with open(file_path, encoding='gbk') as f:
                    state.name_list = [line.strip()
                                 for line in f.readlines() if line.strip()]
            except:
                self.show_message(
                    _("Error: 名单文件%s编码错误，请检查文件编码是否为utf8或gbk") % file_path, _("错误"))
                self.label_3.setText(_("名单文件无效！"))
        log_print("\n", state.name_list)
        state.namelen = len(state.name_list)
        self.spinBox.setMaximum(state.namelen)
        log_print("读取到的有效名单长度:", state.namelen)
        if state.non_repetitive == 1:
            state.non_repetitive_list = state.name_list.copy()

    def ttsinitialize(self):
        if state.allownametts == 2:
            log_print("语音播报(正常模式)")
        elif state.allownametts == 3:
            log_print("语音播报(听写模式)")
        elif state.allownametts == 1 or state.allownametts == 0:
            log_print("语音播报已禁用")

    def opentext(self, path):
        if sys.platform == "win32":
            os.system("start %s" % path)
        else:
            os.system("vim %s" % path)

    def save_history(self, mode=None, name_set=None):
        state.history_file = os.path.join(state.appdata_path, "history", "%s中奖记录.txt" % state.selected_file)

        if mode == 2:
            write_name = name_set
        else:
            write_name = state.name

        if write_name != '' or name_set != None:
            with open(state.history_file, "a", encoding="utf-8") as file:
                if mode == 1:
                        content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                            state.today, state.dmversion, name_set)
                else:
                        content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                            state.today, state.dmversion, write_name)
                file.write(content)

                log_print(state.today, "幸运儿是： %s " % write_name)
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
            self.thread = StartRollThread()
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

            state.threadpool.start(self.thread)

    def check_new_version(self):
        
        self.update_thread = UpdateThread()
        state.threadpool.start(self.update_thread)
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
        #     self.update_config("latest_version", state.newversion)
        else:
            self.update_list(1, title)

    def start_mulit(self):
        num = self.spinBox.value()
        if num > state.namelen:
            self.show_message(_("Error: 连抽人数大于名单人数!"), _("错误"))
        else:
            if state.mrunning == False:
                self.ptimer = QTimer(self)
                self.progressBar.setMaximum(100)
                self.progressBar.show()
                self.ptimer.timeout.connect(self.update_progress_bar_mulit)
                self.value = 0
                self.ptimer.start(5)
                log_print("连抽：%d 人" % num)
                name_set = random.sample(state.name_list, num)
                log_print(name_set)
                try:
                    self.save_history(1, name_set)
                except:
                    log_print("无法写入历史记录")
                log_print(state.today, "幸运儿是： %s " % name_set)
                self.listWidget.addItem("----------------------------")
                self.listWidget.addItem(_("连抽：%d 人") % num)
                for state.name in name_set:
                    self.listWidget.addItem(state.name)
                self.listWidget.addItem("----------------------------")
                target_line = num - 2 if num > 2 else num - 1
                self.listWidget.setCurrentRow(
                    self.listWidget.count() - target_line)
                self.label_3.setText(state.title_text)
            else:
                log_print("连抽中...")

    def reset_repetive_list(self):
        log_print("已重置不重复列表")
        self.update_list(1, _("已重置单抽列表(%s人)") % state.namelen)
        state.non_repetitive_list = state.name_list.copy()

    def update_progress_bar_mulit(self):
        state.mrunning = True
        self.update_progress_bar("", "", "", "mulit")  # 金色传说
        if self.progressBar.value() < 100:
            self.value += 1
            self.progressBar.setValue(self.value)

        else:
            state.mrunning = False
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
            value = f" {state.origin_name_list}" if state.origin_name_list else ""
            if state.non_repetitive == 1:
                value += _(" (还剩%s人)") % (len(state.non_repetitive_list)
                                          ) if state.origin_name_list else ""
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
        if start == 1:
            if len(state.name_list) == 0:
                self.show_message(
                    _("Error: 名单文件为空，请输入名字（一行一个）后再重新点名！"), _("错误"))
                self.qtimer(2)
                self.pushButton_5.setEnabled(True)
                self.pushButton_5.click()  # 名单没有人就自动按结束按钮
                state.origin_name_list = None
                self.font_m.setPointSize(45)
                self.label_3.setText(_(" 名单文件为空！"))
                state.name = ""
                try:
                    self.run_settings(f"1&{state.file_path}")
                except Exception as e:
                    self.show_message(_("选择的名单文件%s不存在！") %
                                      state.file_path, "\n%s" % e)
            else:
                self.timer = QTimer(self)
                log_print(f"滚动速度:{state.roll_speed}")
                self.timer.start(state.roll_speed)
                self.timer.timeout.connect(self.setname)

        elif start == 2:
            try:
                if self.timer:
                    self.timer.stop()
                
            except Exception as e:
                log_print(f"停止计时器失败:{e}")

        elif start == 0:
            try:
                if self.timer:
                    self.timer.stop()
                    # log_print("Debug:",state.name)
                    if state.allownametts != 1:
                        self.tts_read(state.origin_name_list)
                
            except Exception as e:
                log_print(f"计时器启动语音播报线程失败:{e}")            

    def setname(self):
        max_width = self.label_3.width()
        max_height = self.label_3.height()
        
        if state.windows_move_flag:
            self.font_m.setPointSize(150)  # 字体大小
            self.label_3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许 QLabel 扩展
            self.label_3.setMaximumSize(16777215, 16777215)
        else:
            self.font_m.setPointSize(90)
            self.label_3.setMaximumSize(max_width, max_height)
            
        self.label_3.setFont(self.font_m)
        if state.non_repetitive == 1:
            if len(state.non_repetitive_list) == 0:
                state.non_repetitive_list = state.name_list.copy()
        if state.namelen == 0:
            self.show_message(_("Error: 名单文件为空，请输入名字（一行一个）后再重新点名！"), _("错误"))
            state.name = ""
            try:
                self.run_settings(f"1&{state.file_path}")
            except Exception as e:
                log_print(f"文件不存在:{e}")
                self.show_message(_("选择的名单文件%s不存在！") % state.file_path, "\n%s" % e)
            finally:
                self.font_m.setPointSize(54)
                self.label_3.setFont(self.font_m)
                self.label_3.setText(_(" 名单文件为空！"))
                self.pushButton_5.setEnabled(True)
                self.pushButton_5.click()  # 名单没有人就自动按结束按钮(中途切换名单)
                state.origin_name_list = None
                self.qtimer(2)
                return
        try:
            if state.non_repetitive == 1:
                state.name = random.choice(state.non_repetitive_list)
            else:
                state.name = random.choice(state.name_list)
        except:
            pass

        font_size = self.font_m.pointSize()
        metrics = QFontMetrics(self.font_m)

        # 估算一行字符数
        a = max(1, round(metrics.horizontalAdvance(state.name) / max_width, 1)) # 估计行数
        b = metrics.height()# 字体高度
        d = 1.2 if font_size < 80 and len(state.name) < 6 else 2.2
        c = a * (b * d)# b*2考虑到字符行间隔

        # 如果文本换行后的高度超出了标签高度，逐步减小字体
        while c > max_height and font_size > 0:
            
            font_size -= 3
            self.font_m.setPointSize(font_size)
            self.label_3.setFont(self.font_m)
            metrics = QFontMetrics(self.font_m)
            b = metrics.height()
            d = 1.2 if font_size < 80 and len(state.name) < 6 else 2.2
            # 再次计算换行后估算行数
            a = max(1, round(metrics.horizontalAdvance(state.name) / max_width, 1))
            c = a * (b * d)

        state.origin_name_list = state.name
        self.label_3.setText(state.origin_name_list)
        # log_print(font_size,d)

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
            _("欢迎使用沉梦课堂点名器%s！\n\n此工具支持单抽(放回)、单抽(不放回)、连抽功能\n还有一些特色功能：语音播报、背景音乐、小窗模式\n\n进入主界面后，请点击左上角的设置按钮，按需开启功能，编辑名单\n如果遇到了问题，可以在沉梦小站中留言，或者在github上提交issues\n\n\t----Yish_") % state.dmversion, _("欢迎"), 1)
        self.update_config("first_use", 1)

    def tts_read(self, content, mode = None):
        try:
            if state.origin_name_list != "":
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
                state.threadpool.start(self.check_speaker)
            else:
                log_print("名单文件为空！")
        except Exception as e:
            log_print(f"语音播报失败，原因：{e}")

    def dynamic_speed_preview(self, speed):
        try:
            self.timer.setInterval(speed)
        except:
            pass


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
                log_print("用户选择继续运行。")

        # 启用 Windows DPI 感知（优先 Per-Monitor V2，回退到 System Aware）
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except Exception:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except Exception:
                    pass

        # Qt 高 DPI 设置（需在创建 QApplication 之前）
        # 自动根据屏幕缩放因子调整
        os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
        # 缩放舍入策略（Qt 5.14+ 生效）
        if hasattr(QtGui, "QGuiApplication") and hasattr(QtCore.Qt, "HighDpiScaleFactorRoundingPolicy"):
            try:
                QtGui.QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
                    QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                )
            except Exception:
                pass

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