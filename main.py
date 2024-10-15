# -*- coding: utf-8 -*-
import sys
import random
import difflib
import os
import time
import requests
import pygame
import platform
import hashlib
import gettext
import glob
import ctypes
import msvcrt
# import ptvsd  # QThread断点工具
import win32com.client
import webbrowser as web
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor, QFontMetrics
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog, QScroller
from PyQt5.QtCore import QThreadPool, pyqtSignal, QRunnable, QObject, QCoreApplication
from datetime import datetime, timedelta
from ui import Ui_Form  # 导入ui文件
from smallwindow import Ui_smallwindow
from settings import Ui_settings
from Crypto.Cipher import ARC4

rewrite_print = print

def print(*arg):
   rewrite_print(*arg)
   rewrite_print(*arg, file=open('log.txt', "a", encoding='utf-8'))


with open('log.txt', 'w', encoding='utf-8') as log:
    log.write(f"OS：{platform.system()}\n")
    log.write(f"BUILD：{platform.release()}\n")
    log.write(f"PLATFORM：{platform.machine()}\n")
    log.write(f"TIME：{datetime.now()}\n\n")

try:
    config = {}
    with open('config.ini', 'r', encoding='utf-8') as file:
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                config[key.strip('[]')] = value.strip()
    try:
        language_value = config.get('language')
    except:
        language_value = "zh_CN"
    localedir1 = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'locale')
    translate = gettext.translation(
        domain=f"{language_value}", localedir=localedir1, languages=[f"{language_value}"])
    _ = translate.gettext
except:
    try:
        localedir1 = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'locale')
        translate = gettext.translation(
            domain="zh_CN", localedir=localedir1, languages=["zh_CN"])
        _ = translate.gettext
    except Exception as e:
            user32 = ctypes.windll.user32
            user32.MessageBoxW(None, f"程序启动时遇到严重错误:{e}", "Warning!", 0x30)

# version
dmversion = 6.2

# config变量
allownametts = None
checkupdate = None
bgimg = None
latest_version = None
last_name_list = None
non_repetitive = None
bgmusic = None
first_use = None

# 全局变量
name = None
mrunning = False
running = False
default_name_list = _("默认名单")
name_list = ""
history_file = ""
non_repetitive_list = ""
namelen = 0
main_window_name = None

# 窗口标识符
small_window_flag = None
settings_flag = None

# 初始化
today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
pygame.init()
pygame.mixer.init()


class MainWindow(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        # 设置窗口标志
        self.setWindowFlag(Qt.FramelessWindowHint)
        # 设置半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.m_flag = False
        self.setMinimumSize(QtCore.QSize(700, 409))
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", _("沉梦课堂点名器 %s") % dmversion))
        self.pushButton_2.setText(_(" 开始"))
        self.pushButton_5.setText(_(" 小窗模式"))
        font = QtGui.QFont()
        font.setPointSize(45)  # 字体大小
        self.label_3.setFont(font)
        self.label_3.setText(_("幸运儿是:"))
        self.spinBox.setValue(1)
        self.label_5.setText(_("当前名单："))
        self.label_4.setText(_("抽取人数："))
        self.progressBar.hide()

        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_4.clicked.connect(self.run_settings)
        self.pushButton_5.clicked.connect(self.small_mode)
        self.pushButton.clicked.connect(lambda: self.mini(1))

        # 启用触摸手势滚动
        scroller = QScroller.scroller(self.listWidget)
        scroller.grabGesture(self.listWidget.viewport(),
                             QScroller.LeftMouseButtonGesture)

        self.read_config()
        self.read_name_list(2)
        self.set_bgimg()
        self.cs_sha256()
        self.check_new_version()

        self.timer = None
        if first_use == 0:
            self.first_use_introduce()

    def set_bgimg(self):
        self.label_6.setText("")
        if bgimg == 2:
            folder_name = "images"
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, folder_name)
            os.makedirs(folder_name, exist_ok=True)
            file_list = os.listdir(folder_path)
            if not file_list:
                print("要使用自定义背景功能，请在 %s 中放入图片文件" % folder_path)
                self.label_2.setStyleSheet("border-image: url(:/images/(1070).webp);"
                                           "border-radius: 28px;")
                return
            self.label_6.setText(_("自定义背景"))
            random_file = random.choice(file_list)
            print(random_file)
            self.label_2.setStyleSheet(f"border-image: url('./images/{random_file}');"
                                       "border-radius: 30px;")
        elif bgimg == 1 or bgimg == 0:
            self.label_2.setStyleSheet("border-image: url(:/images/bg.webp);"
                                       "border-radius: 28px;")
        elif bgimg == 3:
            self.label_2.setStyleSheet("background-color: rgba(42, 45, 47, 0.92);\n"
                                       "border-radius: 28px;")

    def small_mode(self):
        global small_window_flag
        # 保留对子窗口实例的引用
        if small_window_flag is None:
            self.showMinimized()
            small_Window = smallWindow(mainWindow)
            small_window_flag = small_Window.run_small_window()

    def run_settings(self):
        global settings_flag
        if settings_flag is None:
            settings_window = settingsWindow(mainWindow)
            settings_flag = settings_window.run_settings_window()

    def closeEvent(self, event):
        # 关闭其他窗口的代码
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QWidget) and widget != self:
                widget.close()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.pos().y() <= self.height() // 2.0:  # 只允许在上半部分拖动
                self.m_flag = True
                self.m_Position = event.globalPos() - self.pos()  # 获取鼠标相对窗口的位置
                event.accept()
                self.setCursor(QCursor(Qt.OpenHandCursor))  # 更改鼠标图标

    def mouseMoveEvent(self, event):
        if Qt.LeftButton and self.m_flag:
            self.setWindowState(Qt.WindowNoState)
            self.move(event.globalPos() - self.m_Position)  # 更改窗口位置
            event.accept()

    def mouseReleaseEvent(self, event):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))  # 恢复默认鼠标图标

    def mini(self, mode):
        if mode == 1:
            self.showMinimized()
        elif mode == 2:
            self.showNormal()
    # 功能实现代码

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
            print("first_run")
        txt_name = [filename for filename in os.listdir(
            folder_name) if filename.endswith(".txt")]
        # 获取所有txt文件
        mdnum = len(txt_name)
        if mdnum == 0:
            self.show_message(_("名单文件不存在，且默认名单无法生成，请反馈给我们！"), _("名单生成异常！"))
            sys.exit()
        print("共读取到 %d 个名单" % mdnum)
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
                print("first_run")
        else:
            print(f"所选文件的路径为: {file_path}\n")
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
        global allownametts, checkupdate, bgimg, last_name_list, language_value, latest_version, non_repetitive, bgmusic, first_use
        config = {}
        if not os.path.exists('config.ini'):
            with open('config.ini', 'w', encoding='utf-8') as file:
                file.write(
                    '[language]=zh_CN\n[allownametts]=1\n[checkupdate]=2\n[bgimg]=1\n[last_name_list]=None\n[latest_version]=0\n[non_repetitive]=0\n[bgmusic]=0\n[first_use]=0')
        with open('config.ini', 'r', encoding='utf-8') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    config[key.strip('[]')] = value.strip()
        try:
            language_value = config.get('language')
            allownametts = int(config.get('allownametts'))
            checkupdate = int(config.get('checkupdate'))
            bgimg = int(config.get('bgimg'))
            last_name_list = config.get('last_name_list')
            latest_version = config.get('latest_version')
            non_repetitive = int(config.get('non_repetitive'))
            bgmusic = int(config.get('bgmusic'))
            first_use = int(config.get('first_use'))

        except Exception as e:
            print(f"配置文件读取失败，已重置为默认值！{e}")
            self.show_message(_("配置文件读取失败，已重置为默认值！\n%s") % e, _("读取配置文件失败！"))
            os.remove("config.ini")
            self.read_config()
        return config

    def update_config(self, variable, new_value):
        config = self.read_config()
        config[variable] = new_value
        with open('config.ini', 'w', encoding='utf-8') as file:
            for key, value in config.items():
                file.write(f"[{key}]={value}\n")
        self.read_config()
        if variable == 'bgimg':
            self.set_bgimg()
        else:
            pass

    def cs_sha256(self):
        delrecordfile = 0
        os.makedirs('data', exist_ok=True)
        ctypes.windll.kernel32.SetFileAttributesW('data', 2)
        os.makedirs('bak', exist_ok=True)
        ctypes.windll.kernel32.SetFileAttributesW('bak', 2)

        for filename1 in os.listdir('name'):
            if filename1.endswith('.txt'):
                file_path = os.path.join('name', filename1)
                output_file_path = os.path.join('data', filename1 + '.cmxz')

                if not os.path.exists(output_file_path):
                    sha256_value = self.calculate_sha256(file_path)
                    with open(output_file_path, 'w') as f:
                        f.write(sha256_value)
                    print(f'已保存标识符值：{output_file_path}')
                    self.fileoperation('name', filename1, 'encrypt')
                else:
                    sha256_value = self.calculate_sha256(file_path)
                    with open(output_file_path, 'r') as f:
                        saved_sha256_value = f.read().strip()

                    if sha256_value == saved_sha256_value:
                        print(f'{filename1} 的标识符值与记录一致。')
                        self.fileoperation('name', filename1, 'encrypt')

                    else:
                        print(f'警告：{filename1} 的标识符值与记录不一致。')
                        self.fileoperation('bak', filename1, 'decrypt')
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as original_file, open(processed_file_path, 'r', encoding='utf-8', errors='ignore') as bak_file:
                            original_content = original_file.read()
                            bak_content = bak_file.read()

                            if original_content == bak_content:
                                print('文件内容一致。')
                            else:
                                print('文件内容不一致。以下是修改的内容：')
                                # 去除内容中的空行
                                bak_lines = [
                                    line for line in bak_content.splitlines() if line.strip()]
                                original_lines = [
                                    line for line in original_content.splitlines() if line.strip()]
                                diff = difflib.unified_diff(
                                    bak_lines, original_lines)
                                diff_str = '\n'.join(diff)
                                diff_str = diff_str[11:]
                                self.show_message(_("警告：%s 最近被修改，加号是新增的，减号是减少的\n\n此记录会在 2天后 不再展示。\n%s") % (
                                    filename1, diff_str), _("警告"))
                                # 确保在最后一次循环才执行manage_deadline(filename1)
                                delrecordfile = delrecordfile + 1

        if delrecordfile > 0:
            self.manage_deadline("0")

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def fileoperation(self, folder_path, filename, operation):
        enfilename = filename + ".cmxz"
        file_path = os.path.join(folder_path, filename)
        if operation == 'encrypt':
            if filename.endswith('.txt'):
                self.process_file(file_path, 'encrypt')
        elif operation == 'decrypt':
            if enfilename.endswith('.cmxz'):
                file_path = os.path.join(folder_path, enfilename)
                self.process_file(file_path, 'decrypt')
            return processed_file_path

    def process_file(self, file_path, operation):
        global processed_file_path
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            # 文件不存在时弹窗提示
            self.show_message(_("警告：%s 的备份被删除，此名单可能已经被修改！") %
                              file_path, _("警告"))
        cipher = ARC4.new(b'cmxztopktdmq')
        if operation == 'encrypt':
            try:
                processed_data = cipher.encrypt(data)
                processed_file_path = os.path.join(
                    'bak', os.path.basename(file_path) + '.cmxz')
                if os.path.exists(processed_file_path):
                    print(f'加密文件已存在: {processed_file_path}')
                    return processed_file_path
            except:
                print("加密文件不存在")

        elif operation == 'decrypt':
            try:
                processed_data = cipher.decrypt(data)
                original_filename = os.path.basename(file_path)[:-5]
                processed_file_path = os.path.join('bak', original_filename)
            except:
                print("解密文件不存在")

        try:
            with open(processed_file_path, 'wb') as f:
                f.write(processed_data)

            print(f'文件{operation}成功: {processed_file_path}')
            return processed_file_path
        except:
            self.manage_deadline("1")

    def manage_deadline(self, now):
        timefile_path = os.path.join('bak', 'adeadline.txt')
        current_date = datetime.now().date()

        def write_to_file():
            # 获取默认截止日期并写入文件
            global result_time
            deadline_date = datetime.now() + timedelta(days=2)
            result_time = deadline_date
            if now != "1":
                with open(timefile_path, 'w') as file:
                    file.write(deadline_date.strftime('%Y-%m-%d'))
                self.fileoperation('bak', 'adeadline.txt', 'encrypt')
                os.remove(timefile_path)
            else:
                print("名单校验已重置")

        def read_from_file():
            # 从文件中读取截止日期
            if os.path.exists(timefile_path + '.cmxz'):
                self.fileoperation('bak', 'adeadline.txt', 'decrypt')
                with open(timefile_path, 'r') as file:
                    date_str = file.read().strip()
                    if date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d').date()
                return None

        def remove_directory(data_folder):
            txt_files = glob.glob(os.path.join(data_folder, '*.txt'))
            # 获取指定文件夹中所有扩展名为 .cmxz 的文件列表
            cmxz_files = glob.glob(os.path.join(data_folder, '*.cmxz'))
            all_files = txt_files + cmxz_files
            # 循环删除文件
            for file_path in all_files:
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except OSError as e:
                    print(f"Error: {e.filename} - {e.strerror}")

        deadline_date = read_from_file()

        if deadline_date:
            # 如果截止日期已过，删除数据文件夹
            if current_date > deadline_date:
                print(f"截止日期({deadline_date})已过。删除数据文件夹。")
                try:
                    # 递归删除目录及其内容
                    remove_directory("data")
                    remove_directory("bak")
                    print("数据文件夹已删除。")
                except OSError as e:
                    print(f"删除数据文件夹时发生错误: {e}")
            else:
                print(f"截止日期是{deadline_date}。尚未过期。暂不重置校验")
                if now == "1":
                    remove_directory("data")  # 异常处理
                    remove_directory("bak")
                try:
                    os.remove(timefile_path)
                except:
                    pass
        else:
            # 如果没有截止日期，生成随机日期并写入文件
            if now == "1":
                remove_directory("data")  # 异常处理
                remove_directory("bak")
            write_to_file()
            print(f"生成了一个随机截止日期: {result_time}。写入文件。")

    def process_name_file(self, file_path):
        global name_list, namelen, non_repetitive_list
        try:
            with open(file_path, encoding='utf8') as f:
                # 读取每一行，去除行尾换行符，过滤掉空行和仅包含空格的行
                name_list = [line.strip()
                             for line in f.readlines() if line.strip()]
        except:
            print("utf8解码失败，尝试gbk")
            try:
                with open(file_path, encoding='gbk') as f:
                    name_list = [line.strip()
                                 for line in f.readlines() if line.strip()]
            except:
                self.show_message(
                    _("名单文件%s编码错误，请检查文件编码是否为utf8或gbk") % file_path, _("错误"))
                self.label_3.setText(_("名单文件无效！"))
        print("\n", name_list)
        namelen = len(name_list)
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
        if name != '' or name_set != None:
            if mode == 1:
                with open(history_file, "a", encoding="utf-8") as file:
                    content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                        today, dmversion, name_set)
                    file.write(content)
            else:
                with open(history_file, "a", encoding="utf-8") as file:
                    content = "%s 沉梦课堂点名器%s 幸运儿是：%s\n" % (
                        today, dmversion, name)
                    file.write(content)
                print(today, "幸运儿是： %s " % name)
        else:
            pass

    def start(self):
        num = self.spinBox.value()
        if num > 1:
            self.start_mulit()
        else:
            self.threadpool = QThreadPool()
            self.thread = WorkerThread()
            self.thread.signals.show_progress.connect(self.update_progress_bar)
            self.thread.signals.update_pushbotton.connect(
                self.update_pushbotton)
            self.thread.signals.update_list.connect(self.update_list)
            self.thread.signals.enable_button.connect(self.enable_button)
            self.thread.signals.qtimer.connect(self.qtimer)
            self.thread.signals.save_history.connect(self.save_history)
            self.thread.signals.finished.connect(lambda: print("结束点名"))

            self.threadpool.start(self.thread)
            self.ttsinitialize()

    def check_new_version(self):
        self.threadpool1 = QThreadPool()
        self.update_thread = UpdateThread()
        self.threadpool1.start(self.update_thread)
        self.update_thread.signals.find_new_version.connect(
            self.update_message)
        self.update_thread.signals.finished.connect(
            lambda: print("检查更新线程结束"))

    def update_message(self, message, title):  # 更新弹窗
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        okButton = msgBox.addButton("立刻前往", QMessageBox.AcceptRole)
        noButton = msgBox.addButton("下次一定", QMessageBox.RejectRole)
        ignoreButton = msgBox.addButton("忽略本次更新", QMessageBox.RejectRole)
        msgBox.exec_()
        clickedButton = msgBox.clickedButton()
        if clickedButton == okButton:
            web.open_new("https://cmxz.top/ktdmq")
            self.update_list(1, title)
        elif clickedButton == ignoreButton:
            self.update_list(1, title)
            self.update_config("latest_version", newversion)
        else:
            self.update_list(1, title)

    def start_mulit(self):
        num = self.spinBox.value()
        if num > namelen:
            self.show_message(_("连抽人数大于名单人数!"), _("错误"))
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
                    print("无法写入历史记录")
                print(today, "幸运儿是： %s " % name_set)
                self.listWidget.addItem("----------------------------")
                self.listWidget.addItem(_("连抽：%d 人") % num)
                for name in name_set:
                    self.listWidget.addItem(name)
                self.listWidget.addItem("----------------------------")
                target_line = num - 2 if num > 2 else num - 1
                self.listWidget.setCurrentRow(
                    self.listWidget.count() - target_line)
                self.label_3.setText(_("幸运儿是:"))
            else:
                print("连抽中...")

    def reset_repetive_list(self):
        global non_repetitive_list
        print("已重置不重复列表")
        self.update_list(1, _("已重置单抽列表(%s人)") % namelen)
        non_repetitive_list = name_list.copy()

    def update_progress_bar_mulit(self):
        global mrunning
        mrunning = True
        self.progressBar.setStyleSheet(" QProgressBar {\n"
                                       "        border: 2px solid rgba(88, 88, 88, 0.81);\n"
                                       "        border-radius: 2px;\n"
                                       "        background-color: rgba(0, 0, 0, 0);\n"
                                       "    }\n"
                                       "\n"
                                       "    QProgressBar::chunk {\n"
                                       "        background-color: QLinearGradient(\n"
                                       "            x1: 0, y1: 0, x2: 1, y2: 1,\n"
                                       "            stop: 0 #ffda95, stop: 1 #FF9800\n"
                                       "        );\n"
                                       "    }")
        if self.progressBar.value() < 100:
            self.value += 1
            self.progressBar.setValue(self.value)

        else:
            mrunning = False
            self.value = 0
            self.progressBar.setValue(self.value)
            self.progressBar.hide()
            self.ptimer.stop()  # 停止定时器
            self.progressBar.setStyleSheet(" QProgressBar {\n"
                                           "        border: 2px solid rgba(88, 88, 88, 0.81);\n"
                                           "        border-radius: 2px;\n"
                                           "        background-color: rgba(0, 0, 0, 0);\n"
                                           "    }\n"
                                           "\n"
                                           "    QProgressBar::chunk {\n"
                                           "        background-color: QLinearGradient(\n"
                                           "            x1: 0, y1: 0, x2: 1, y2: 1,\n"
                                           "            stop: 0 #00BCD4, stop: 1 #8BC34A\n"
                                           "        );\n"
                                           "        border-radius: 8px;\n"
                                           "    }")

    def update_progress_bar(self, mode, value, value2):
        self.progressBar.setValue(value)
        self.progressBar.setMaximum(value2)
        if mode == 1:
            self.progressBar.show()
        elif mode == 0:
            self.progressBar.hide()

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
                                            "    font-size: 18px;\n"
                                            "}\n"
                                            "QPushButton{background:rgba(118, 218, 96, 1);border-radius:5px;}QPushButton:hover{background:rgba(80, 182, 84, 1);}")
            self.pushButton_5.clicked.disconnect()
            self.pushButton_5.clicked.connect(self.small_mode)
            self.pushButton_5.setStyleSheet(
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
                                            "    font-size: 18px;\n"
                                            "}\n"
                                            "QPushButton{background:rgba(249, 117, 83, 1);border-radius:5px;}QPushButton:hover{background:rgba(226, 82, 44, 1);}")
            self.pushButton_2.setStyleSheet("QPushButton {\n"
                                            "    font-size: 18px;\n"
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
                                            "    font-size: 18px;\n"
                                            "}\n"
                                            "QPushButton{background:rgba(249, 117, 83, 1);border-radius:5px;}QPushButton:hover{background:rgba(226, 82, 44, 1);}")
            self.pushButton_2.setStyleSheet("QPushButton {\n"
                                            "    font-size: 18px;\n"
                                            "}\n"
                                            "QPushButton{background:rgba(112, 198, 232, 1);border-radius:5px;}QPushButton:hover{background:rgba(93, 167, 196, 1);}")
            self.pushButton_5.clicked.disconnect()
            self.pushButton_5.clicked.connect(self.start)
            self.pushButton_2.clicked.disconnect()
            self.pushButton_2.clicked.connect(self.reset_repetive_list)

    def update_list(self, mode, value):
        if mode == 2:
            mode = 1
            value = f" {main_window_name}"
            if non_repetitive == 1:
                value += _(" (还剩%s人)") % (len(non_repetitive_list))
        if mode == 1:
            if value == "":
                pass
            else:
                self.listWidget.addItem(value)
                self.listWidget.setCurrentRow(self.listWidget.count() - 1)
        elif mode == 0:
            self.label_3.setText(value)

    def qtimer(self, start):
        global non_repetitive_list, name, main_window_name
        if start == 1:
            if len(name_list) == 0:
                self.show_message(_("名单文件为空，请输入名字（一行一个）后再重新点名！"), _("警告"))
                self.qtimer(0)
                self.label_3.setText(_("名单文件为空！"))
                name = ""
                try:
                    self.opentext(file_path)
                except Exception as e:
                    self.show_message(_("选择的名单文件%s不存在！") %
                                      file_path, "\n%s" % e)
            else:
                self.timer = QTimer(self)
                time = random.randint(30, 40)
                self.timer.start(time)
                self.timer.timeout.connect(self.setname)

        elif start == 0:
            try:
                self.timer.stop()
                if non_repetitive == 1:
                    if len(non_repetitive_list) > 0:
                        if main_window_name in non_repetitive_list:
                            non_repetitive_list.remove(main_window_name)
                        else:
                            print(f"不重复的单抽名单中没有{main_window_name}")
                if allownametts != 1:
                    try:
                        if main_window_name != "":
                            self.threadpool2 = QThreadPool()
                            self.check_speaker = CheckSpeakerThread(1)
                            self.check_speaker.signals.update_list.connect(
                                self.update_list)
                            self.check_speaker.signals.update_pushbotton.connect(
                                self.update_pushbotton)
                            self.check_speaker.signals.enable_button.connect(
                                self.enable_button)
                            self.check_speaker.signals.save_history.connect(
                                self.save_history)
                            self.threadpool2.start(self.check_speaker)
                        else:
                            print("名单文件为空！")
                    except Exception as e:
                        print(f"语音播报失败，原因：{e}")
            except Exception as e:
                print(f"停止计时器失败:{e}")

    def setname(self):
        global name, non_repetitive_list, main_window_name
        font = QtGui.QFont()
        font.setPointSize(45)  # 字体大小
        self.label_3.setFont(font)
        if non_repetitive == 1:
            if len(non_repetitive_list) == 0:
                non_repetitive_list = name_list.copy()
        if namelen == 0:
            self.show_message(_("名单文件为空，请输入名字（一行一个）后再重新点名！"), _("警告"))
            name = ""
            try:
                self.opentext(file_path)
            except Exception as e:
                print(f"文件不存在:{e}")
                self.show_message(_("选择的名单文件%s不存在！") % file_path, "\n%s" % e)
            finally:
                self.label_3.setText(_("名单文件为空！"))
                self.qtimer(0)
                return
        try:
            if non_repetitive == 1:
                name = random.choice(non_repetitive_list)
            else:
                name = random.choice(name_list)
        except:
            pass
        font = self.label_3.font()
        font_size = font.pointSize()

        # 检测文本宽度
        metrics = QFontMetrics(font)
        while metrics.width(name) > 1.8*self.label_3.width() and font_size > 0:
            font_size -= 1
            font.setPointSize(font_size)
            self.label_3.setFont(font)
            metrics = QFontMetrics(font)
        font = self.label_3.font()
        font_size = font.pointSize()
        main_window_name = name
        self.label_3.setText(main_window_name)

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


class WorkerSignals(QObject):
    # 定义信号
    show_progress = pyqtSignal(int, int, int)
    update_list = pyqtSignal(int, str)
    update_pushbotton = pyqtSignal(str, int)
    find_new_version = pyqtSignal(str, str)
    enable_button = pyqtSignal(int)
    save_history = pyqtSignal()
    finished = pyqtSignal()
    qtimer = pyqtSignal(int)
    speakertest = pyqtSignal(int, str)


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
        global running
        # ptvsd.debug_this_thread()  # 在此线程启动断点调试

        def stop():
            if allownametts == 1:
                self.signals.update_list.emit(2, "")
                self.signals.update_pushbotton.emit(_(" 小窗模式"), 2)
                self.signals.enable_button.emit(1)
                try:
                    self.signals.save_history.emit()
                except:
                    print(_("无法写入历史记录"))
                if non_repetitive == 1:
                    if namelen != 0:
                        if len(non_repetitive_list) == 2:
                            self.signals.update_list.emit(1, _("最终的幸运儿即将出现："))
                        elif len(non_repetitive_list) == 1:
                            self.signals.update_list.emit(
                                1, _("点击开始重置名单,或切换名单继续点名"))
                            self.signals.update_list.emit(0, _("此名单已完成抽取！"))
            self.signals.update_pushbotton.emit(_(" 开始"), 1)
            if namelen == 0:
                self.signals.update_pushbotton.emit(_(" 小窗模式"), 2)

        if running:  # 结束按钮
            self.signals.qtimer.emit(0)
            self.signals.show_progress.emit(0, 0, 100)
            self.signals.enable_button.emit(1)
            running = False
            stop()
            if bgmusic == 1:
                try:
                    pygame.mixer.music.fadeout(600)
                    pygame.mixer.music.unload()
                except pygame.error as e:
                    print(f"停止音乐播放时发生错误：{str(e)}")
            self.signals.finished.emit()
            # 向主线程发送终止信号

        else:  # 开始按钮
            running = True
            self.signals.qtimer.emit(1)
            print("开始点名")
            self.signals.show_progress.emit(1, 0, 0)
            self.signals.enable_button.emit(2)

            if bgmusic == 1:
                folder_name = "dmmusic"
                current_dir = os.path.dirname(os.path.abspath(__file__))
                folder_path = os.path.join(current_dir, folder_name)
                os.makedirs('dmmusic', exist_ok=True)
                # 获取文件夹中的文件列表
                file_list = os.listdir(folder_path)
                if not file_list:
                    self.signals.update_pushbotton.emit(_(" 结束"), 2)
                    print("要使用背景音乐功能，请在 %s 中放入mp3格式的音乐" % folder_path)
                    return
                try:
                    self.signals.update_pushbotton.emit(_(" 请稍后."), 2)
                    self.signals.enable_button.emit(3)
                    random_file = random.choice(file_list)
                    file_path = os.path.join(folder_path, random_file)
                    print("播放音乐：%s" % file_path)
                    pygame.mixer.music.load(file_path)
                    sound = pygame.mixer.Sound(file_path)
                    music_length = sound.get_length()
                    random_play = round(random.uniform(2, 4), 1)
                    start_time = round(music_length / random_play, 1)
                    self.signals.update_pushbotton.emit(_(" 请稍后.."), 2)
                    self.volume = 0.0
                    pygame.mixer.music.set_volume(self.volume)
                    pygame.mixer.music.play(1, start=start_time)
                    print(
                        f"音频时长：{music_length},随机数：{random_play},音频空降：{start_time}")

                    # 使用 for 循环进行音量淡入
                    for i in range(33):  # 50 次循环，每次增加0.02的音量
                        if self.volume < 0.66:
                            self.volume += 0.02
                            if i == 10:
                                self.signals.update_pushbotton.emit(
                                    _(" 请稍后..."), 2)
                            if self.volume >= 0.66:
                                self.volume = 0.66
                            pygame.mixer.music.set_volume(self.volume)
                            pygame.time.delay(15)

                    print("音量淡入完成。")
                    self.signals.update_pushbotton.emit(_(" 结束"), 2)
                    self.signals.enable_button.emit(4)

                except pygame.error as e:
                    print("无法播放音乐文件：%s，错误信息：%s" % (file_path, e))
            else:
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
        global newversion, checkupdate, latest_version
        # ptvsd.debug_this_thread()  # 在此线程启动断点调试
        headers = {
            'User-Agent': 'CMXZ-CRP_%s,%s,%s,%s,%s%s_%s' % (dmversion, allownametts, bgimg, language_value, platform.system(), platform.release(), platform.machine())
        }
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
                if newversion > dmversion and float(latest_version) < newversion:
                    print("检测到新版本:", newversion,
                          "当前版本为:", dmversion)
                    new_version_detail = requests.get(
                        updatecheck + "?detail", timeout=5, headers=headers)
                    new_version_detail = new_version_detail.text
                    self.signals.find_new_version.emit(_("云端最新版本为%s，要现在下载新版本吗？<br>您也可以稍后访问沉梦小站官网获取最新版本。<br><br>%s") % (
                        newversion, new_version_detail), findnewversion)
                else:
                    if float(latest_version) == newversion:
                        print("\n已忽略%s版本更新,当前版本：%s" % (newversion, dmversion))
            except:
                print("网络异常,无法检测更新")
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

        font = QtGui.QFont()
        font.setPointSize(34)  # 字体大小
        self.label_2.setFont(font)

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
                        self.main_instance.save_history()
                    except:
                        print("无法写入历史记录")
                else:
                    self.get_name_list()  # 只有未移动时才输出消息
            else:
                self.frame.show()
                self.label.show()
                self.label_2.show()
                self.pushButton_7.hide()
                self.minimum_flag = False
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def qtimer(self, start):
        if start == 1:
            self.timer = QTimer()
            time = random.randint(30, 40)
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
                            self.label_2.setText(_("名单抽取完成"))
                        else:
                            self.label_3.setText("")
                    else:
                        info = self.small_window_name
                    self.main_instance.update_list(1, _("小窗：%s") % info)
                else:
                    pass
            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        global name, non_repetitive_list, non_repetitive
        font = QtGui.QFont()
        font.setPointSize(34)  # 字体大小
        self.label_2.setFont(font)
        if non_repetitive == 1:
            if len(non_repetitive_list) == 0:
                non_repetitive_list = name_list.copy()
                self.main_instance.update_list(1, _("名单已重置"))
            a = str(len(non_repetitive_list))
            if a != "0":
                self.label_3.setText(_("剩%s人") % a)
        if name_list == []:
            name = ""
            self.label_2.setText(_("名单为空!"))
            self.main_instance.mini(2)
            self.qtimer(0)
        else:
            try:
                if non_repetitive == 1:
                    name = random.choice(non_repetitive_list)
                else:
                    name = random.choice(name_list)
            except:
                pass

            font = self.label_2.font()
            font_size = font.pointSize()
            # 检测文本宽度
            metrics = QFontMetrics(font)
            while metrics.width(name) > 1.8*self.label_2.width() and font_size > 0:
                font_size -= 1
                font.setPointSize(font_size)
                self.label_2.setFont(font)
                metrics = QFontMetrics(font)
            self.small_window_name = name
            self.label_2.setText(name)

    def get_name_list(self):
        self.qtimer(1)

    def closeEvent(self, event):
        print("小窗被关闭")
        self.main_instance.mini(2)
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
        self.pushButton_7.show()
        self.minimum_flag = True


class settingsWindow(QtWidgets.QMainWindow, Ui_settings):  # 设置窗口
    def __init__(self, main_instance=None):
        super().__init__()
        central_widget = QtWidgets.QWidget(self)  # 创建一个中央小部件
        self.setCentralWidget(central_widget)  # 设置中央小部件为QMainWindow的中心区域
        self.setupUi(central_widget)  # 初始化UI到中央小部件上
        self.setFixedSize(682, 523)
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.groupBox.setTitle(_("功能设置"))
        self.radioButton_3.setText(_("默认背景"))
        self.radioButton_4.setText(_("自定义"))
        self.radioButton_5.setText(_("无"))
        self.checkBox.setText(_("不放回模式(单抽结果不重复)"))
        self.checkBox_3.setText(_("检查更新"))
        self.checkBox_2.setText(_("语音播报"))
        self.checkBox_4.setText(_("背景音乐"))
        self.label.setText(_("背景图片"))
        self.radioButton.setText(_("正常模式"))
        self.radioButton_2.setText(_("听写模式(不说\"恭喜\")"))
        self.groupBox_3.setTitle(_("语言设置"))
        self.pushButton_2.setText(_("保存"))
        self.pushButton.setText(_("取消"))
        self.groupBox_2.setTitle(_("名单管理"))
        self.pushButton_4.setText(_("删除所选名单"))
        self.pushButton_6.setText(_("统计所选名单"))
        self.pushButton_3.setText(_("新建名单"))
        self.pushButton_5.setText(_("编辑所选名单"))
        self.groupBox_6.setTitle(_("快捷打开"))
        self.pushButton_8.setText(_("历史记录目录"))
        self.pushButton_9.setText(_("背景图片目录"))
        self.pushButton_10.setText(_("背景音乐目录"))
        self.pushButton_12.setText(_("名单文件目录"))
        self.groupBox_5.setTitle(_("关于"))
        self.label_2.setText(_("沉梦课堂点名器 %s") % dmversion)
        self.label_3.setText(_("<html><head/><body><p align=\"center\">一个支持 单抽，连抽的课堂点名小工具<br/></p><p align=\"center\"><a href=\"https://cmxz.top/ktdmq\"><span style=\" text-decoration: underline; color:#0000ff;\">沉梦小站</span></a></p><p align=\"center\"><a href=\"https://github.com/Yish1/Class-Roster-Picker-NEXT\"><span style=\" text-decoration: underline; color:#0000ff;\">Yish1/Class-Roster-Picker-NEXT: 课堂点名器</span></a></p></body></html>"))
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", _("课堂点名器设置")))

        self.main_instance = main_instance
        self.read_name_list()
        self.read_config()
        self.find_langluge()

        self.enable_tts = None
        self.enable_update = None
        self.enable_bgimg = None
        self.language_value = None
        self.disable_repetitive = None
        self.enable_bgmusic = None

        self.window = QWidget()
        self.window.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.pushButton.clicked.connect(self.close)
        self.pushButton_3.clicked.connect(self.add_new_list)
        self.pushButton_4.clicked.connect(self.delete_list)
        self.pushButton_5.clicked.connect(self.edit_list)
        self.pushButton_2.clicked.connect(self.save_settings)
        self.pushButton_6.clicked.connect(self.count_name)
        self.comboBox_2.currentIndexChanged.connect(self.change_langluge)
        self.pushButton_12.clicked.connect(lambda: self.open_fold("name"))
        self.pushButton_10.clicked.connect(lambda: self.open_fold("dmmusic"))
        self.pushButton_9.clicked.connect(lambda: self.open_fold("images"))
        self.pushButton_8.clicked.connect(lambda: self.open_fold("history"))

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
        self.radioButton_3.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))
        self.radioButton_4.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))
        self.radioButton_5.toggled.connect(
            lambda checked: self.process_config("enable_bgimg", checked))

    def read_name_list(self):
        txt_files_name = self.main_instance.read_name_list(1)
        self.comboBox_1.addItems(txt_files_name)  # 添加文件名到下拉框

    def refresh_name_list(self):
        txt_name = [filename for filename in os.listdir(
            "name") if filename.endswith(".txt")]
        txt_files_name = [os.path.splitext(
            filename)[0] for filename in txt_name]

        return txt_files_name

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
                self.main_instance.opentext(newnamepath)
            else:
                self.main_instance.show_message(_("同名文件已存在，请勿重复创建！"), _("警告！"))
            txt_name = self.refresh_name_list()
            self.comboBox_1.clear()  # 清空下拉框的选项
            self.comboBox_1.addItems(txt_name)  # 添加新的文件名到下拉框

    def delete_list(self):
        target_filename, ok_pressed = QInputDialog.getText(
            self.window, _("删除名单"), _("再次输入名单名称将删除此名单！"))
        if ok_pressed and target_filename:
            if target_filename == self.comboBox_1.currentText():
                target_filepath = os.path.join(
                    "name", f"{target_filename}.txt")
                try:
                    os.remove(target_filepath)  # 删除文件
                    message = (_("已成功删除名单： '%s.txt' ") % target_filename)
                    QMessageBox.information(
                        self.window, _("删除成功"), message, QMessageBox.Ok)
                    txt_name = self.refresh_name_list()
                    self.comboBox_1.clear()  # 清空下拉框的选项
                    self.comboBox_1.addItems(txt_name)  # 添加新的文件名到下拉框
                except Exception as e:
                    QMessageBox.warning(
                        self.window, _('警告'), _('名单文件不存在，或已被删除！\n%s') % e, QMessageBox.Ok)
            else:
                self.main_instance.show_message(_("名单名称输入错误！"), _("错误"))

    def edit_list(self):
        target_filename = self.comboBox_1.currentText()
        target_filepath = os.path.join(
            "name", f"{target_filename}"+".txt")
        try:
            self.main_instance.opentext(target_filepath)  # 自带错误处理
        except Exception as e:
            # 捕捉预料外的错误
            print(f"名单文件不存在，无法编辑{e}")
            QMessageBox.warning(
                self.window, _('警告'), _('名单文件不存在，或已被删除！\n%s') % e, QMessageBox.Ok)

    def find_langluge(self):
        # 读取指定目录下的文件夹名
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
        self.language_value = self.comboBox_2.currentText()

    def closeEvent(self, event):
        print("设置被关闭")
        try:
            self.main_instance.mini(2)
            self.main_instance.read_name_list()
        except Exception as e:
            print(e)
        global settings_flag
        settings_flag = None
        event.accept()  # 确保仅关闭子窗口，不影响主窗口

    def run_settings_window(self):
        self.show()
        return self

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
                    self.threadpool = QThreadPool()
                    self.check_speaker = CheckSpeakerThread()
                    self.threadpool.start(self.check_speaker)

                    def spearker_test(result, e):
                        if result == 1:
                            self.radioButton.setEnabled(True)
                            self.radioButton_2.setEnabled(True)
                            self.radioButton.setChecked(True)
                        else:
                            self.main_instance.show_message(
                                _("语音播报无法在此设备上开启，可能是您使用的系统为精简版，删除了自带的语音库！\n%s") % e, _("错误"))
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
                        _("您正在使用自定义背景功能，由于此工具可能需要在公众场合展示，请选择适宜场景的合适背景！ \n\n因使用不合适的背景图片而造成的后果由您自行承担！\n\n\n使用教程：\n\n在稍后打开的\images文件夹中放入您喜欢的图片(建议暗色系、长宽比16:9)，程序将随机选取图片使用。"), _("声明"))
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
                    _("不放回模式，即单抽结束后的名字不会放回列表中，下次将不会抽到此名字\n当名单抽取完成、切换名单或者手动点击按钮时将会重置不放回列表！"), _("说明"))

        elif key == "enable_bgmusic":
            self.enable_bgmusic = 1 if checked else 0
            if not checked:
                print("正在关闭背景音乐")
            else:
                print("正在开启背景音乐")
                self.main_instance.show_message(
                    _("开启背景音乐功能后，需要在稍后打开的背景音乐目录下放一些您喜欢的音乐\n程序将随机选取一首，播放随机的音乐进度"), _("提示"))
                self.open_fold("dmmusic")

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

        self.close()

    def count_name(self):
        name_counts = {}  # 存储名字出现次数的字典
        file = "history/%s中奖记录.txt" % self.comboBox_1.currentText()
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
            cresult = _("中奖名单统计(统计会覆盖上一次结果):\n")
            for name, count in sorted_counts:
                cresult += "%s 出现了 %s 次\n" % (name, count)
                with open('中奖统计.txt', 'w', encoding="utf-8") as file:
                    file.write(cresult)
            QMessageBox.information(self, _("保存结果"), _("统计结果已保存到'中奖统计.txt'"))
            self.main_instance.opentext('中奖统计.txt')
        except Exception as e:
            print("读取文件时发生错误:", e)
            self.main_instance.show_message(
                _("历史记录文件不存在，无法统计次数！\n%s") % e, _("错误"))


class CheckSpeakerThread(QRunnable):
    def __init__(self, mode=None):
        super().__init__()
        self.signals = WorkerSignals()
        self.mode = mode
        self.allownametts = allownametts

    def ttsread(self, text):
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)

    def run(self):
        # ptvsd.debug_this_thread()  # 在此线程启动断点调试
        if self.mode != 1:
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Volume = 0
                speaker.Speak("1")
                print("此设备系统支持语音播报功能！")
                self.signals.speakertest.emit(1, "")
            except Exception as e:
                print("此设备系统不支持语音播报功能！Reason：", e)
                self.signals.speakertest.emit(0, e)
        else:
            self.signals.update_list.emit(2, "")
            if non_repetitive == 1:
                self.signals.enable_button.emit(6)
            else:
                self.signals.enable_button.emit(1)
            self.signals.update_pushbotton.emit(_(" 小窗模式"), 2)
            if non_repetitive == 1:
                if namelen != 0:

                    if len(non_repetitive_list) == 1:
                        self.signals.update_list.emit(1, _("最终的幸运儿即将出现："))
                    elif len(non_repetitive_list) == 0:
                        self.signals.update_list.emit(
                            1, _("点击开始重置名单,或切换名单继续点名"))
                        # self.signals.update_list.emit(1,_("或切换名单继续点名"))
                        self.signals.update_list.emit(0, _("此名单已完成抽取！"))
            if self.allownametts == 2:
                self.ttsread(text=_("恭喜 %s") % main_window_name)
            elif self.allownametts == 3:
                time.sleep(0.3)
                self.ttsread(text=main_window_name)
            elif self.allownametts == 1:
                pass

            try:
                self.signals.save_history.emit()
            except:
                print(_("无法写入历史记录"))
            # 终止信号

        self.signals.finished.emit()


if __name__ == "__main__":
    try:
        # 防止重复运行
        lock_file = os.path.expanduser("~/.program_lock")
        fd = os.open(lock_file, os.O_RDWR | os.O_CREAT)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError:
            os.close(fd)
            print("另一个点名器正在运行。")
            user32 = ctypes.windll.user32
            user32.MessageBoxW(None, _("另一个点名器正在运行！"), "Warning!", 0x30)
            sys.exit()

        if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_EnableHighDpiScaling, True)
        # 启用高DPI自适应
        if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
            QtWidgets.QApplication.setAttribute(
                QtCore.Qt.AA_UseHighDpiPixmaps, True)
        app = QtWidgets.QApplication(sys.argv)
        mainWindow = MainWindow()
        mainWindow.show()
        sys.exit(app.exec_())
    except Exception as e:
        user32 = ctypes.windll.user32
        user32.MessageBoxW(None, f"程序启动时遇到严重错误:{e}", "Warning!", 0x30)
        sys.exit()
