# -*- coding: utf-8 -*-
import sys
import random
import difflib
import os
import requests
import pygame
import hashlib
import gettext
import glob
import ctypes
# import ptvsd  # QThread断点工具
import win32com.client
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QCursor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog, QScroller, QScrollerProperties
from PyQt5.QtCore import QThreadPool, pyqtSignal, QRunnable, QObject, QCoreApplication
from datetime import datetime, timedelta
from ui import Ui_Form  # 导入ui文件
from smallwindow import Ui_smallwindow
from settings import Ui_settings
from Crypto.Cipher import ARC4
import webbrowser as web

dmversion = 6.0

name = None
allownametts = None
mrunning = False
running = False
default_name_list = "默认名单"
name_list = ""
small_window_flag = None
settings_flag = None
namelen = 0
pygame.init()
pygame.mixer.init()


class DraggableWindow(QtWidgets.QMainWindow, Ui_Form):
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
            "MainWindow", "沉梦课堂点名器 6.0"))
        self.pushButton_2.setText(" 开始")
        self.pushButton_5.setText(" 小窗模式")
        self.label_3.setText("幸运儿是:")
        self.spinBox.setValue(1)
        self.label_5.setText("当前名单：")
        self.label_4.setText("抽取人数：")
        self.progressBar.hide()

        self.pushButton_2.clicked.connect(self.start)
        self.pushButton_4.clicked.connect(self.run_settings)
        self.pushButton_5.clicked.connect(self.small_mode)
        self.pushButton.clicked.connect(lambda:self.mini(1))

        # 启用触摸手势滚动
        scroller = QScroller.scroller(self.listWidget)
        scroller.grabGesture(self.listWidget.viewport(), QScroller.LeftMouseButtonGesture)

        self.read_name_list()
        self.cs_sha256()
        self.timer = None

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
            if event.pos().y() <= self.height() // 2.3:  # 只允许在上半部分拖动
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


    def mini(self,mode):
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

    def read_name_list(self,mode = None):
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
            self.show_message("名单文件不存在，且默认名单无法生成，请反馈给我们！", "名单生成异常！")
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
            self.comboBox.currentIndexChanged.connect(
                lambda: self.get_selected_file(0))
            self.get_selected_file()

    def get_selected_file(self, first=None):
        global file_path
        # 获取当前选中的文件名
        selected_file = self.comboBox.currentText()
        file_path = os.path.join("name", selected_file+".txt")
        print(file_path)
        if not os.path.exists(file_path):
            self.show_message("所选名单文件已被移动或删除！", "找不到文件！")
            try:
                self.comboBox.setCurrentIndex(0)
            except:
                print("first_run")
        else:
            print(f"所选文件的路径为: {file_path}\n")
        self.process_name_file(file_path)
        if first == 0:
            self.listWidget.addItem("切换至>\'%s\' 共 %s 人" % (selected_file,namelen))
            self.listWidget.setCurrentRow(self.listWidget.count() - 1)

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
                                self.show_message("警告：%s 最近被修改，加号是新增的，减号是减少的\n\n此记录会在 2天后 不再展示。\n%s" % (
                                    filename1, diff_str), "警告")
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
            self.show_message("警告：%s 的备份被删除，此名单可能已经被修改！" % file_path, "警告")
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
        global name_list, namelen
        with open(file_path, encoding='utf8') as f:
            # 读取每一行，去除行尾换行符，过滤掉空行和仅包含空格的行
            name_list = [line.strip()
                         for line in f.readlines() if line.strip()]

        print("\n", name_list)
        namelen = len(name_list)
        print("读取到的有效名单长度:", namelen)

    def ttsinitialize(self):
        global allownametts
        try:
            with open('allownametts.ini', 'r') as file:
                allownametts = int(file.read())
        except FileNotFoundError:
            # 语音播报开关
            ifvoice = QMessageBox()
            ifvoice.setWindowTitle("语音播报")
            ifvoice.setText(
                "需要开启语音播报功能吗？\n单抽后会播报抽取结果。\n")
            allow_button = ifvoice.addButton("好的", QMessageBox.ActionRole)
            cancel_button = ifvoice.addButton("下次一定", QMessageBox.ActionRole)
            dictation_button = ifvoice.addButton(
                "听写模式(不会读\"恭喜\")", QMessageBox.ActionRole)
            button = ifvoice.addButton("取消", QMessageBox.NoRole)
            button.setVisible(False)
            ifvoice.exec_()
            if ifvoice.clickedButton() == allow_button:
                # 同意
                allownametts = 1
                with open('allownametts.ini', "w", encoding='utf-8') as f:
                    f.write("1")
                QMessageBox.information(
                    None, "语音播报", "语音播报已经开启，您可以删除目录下的allownametts.ini重新设置此功能。")
            elif ifvoice.clickedButton() == cancel_button:
                allownametts = 0
                # 不同意
                with open('allownametts.ini', "w", encoding='utf-8') as f:
                    f.write("0")
                QMessageBox.information(
                    None, "语音播报", "语音播报已禁用，您可以删除目录下的allownametts.ini重新设置此功能。")
            elif ifvoice.clickedButton() == dictation_button:
                allownametts = 2
                # 听写模式
                with open('allownametts.ini', "w", encoding='utf-8') as f:
                    f.write("2")
                QMessageBox.information(
                    None, "语音播报", "语音播报（听写模式）已启用，您可以删除目录下的allownametts.ini重新设置此功能。")
        except ValueError:
            QMessageBox.information(
                None, "语音播报", "目录下的allownametts.ini中不是一个有效的值")
            if os.path.exists("allownametts.ini"):
                os.remove("allownametts.ini")
                self.ttsinitialize()

    def opentext(self, path):
        if sys.platform == "win32":
            os.system("start %s" % path)
        else:
            os.system("vim %s" % path)

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
            self.thread.signals.finished.connect(lambda: print("结束点名"))

            self.threadpool.start(self.thread)
            self.ttsinitialize()

    def start_mulit(self):
        num = self.spinBox.value()
        if num > namelen:
            self.show_message("连抽人数大于名单人数!", "错误")
        else:
            if mrunning == False:
                self.ptimer = QTimer(self)
                self.progressBar.setMaximum(100)
                self.progressBar.show()
                self.ptimer.timeout.connect(self.update_progress_bar_mulit)
                self.value = 0
                self.ptimer.start(5)
                print("连抽：%d 人" % num)
                name_set = set()
                while len(name_set) != num:
                    name_set.add(random.choice(name_list))
                name_set = list(name_set)
                random.shuffle(name_set)
                today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    print(
                        today,
                        "沉梦课堂点名器%s" % dmversion,
                        "幸运儿是： %s " % name_set,
                        file=open("点名器中奖名单.txt", "a"),
                    )
                except:
                    print("无法写入历史记录")
                print(today, "幸运儿是： %s " % name_set)
                self.listWidget.addItem("----------------------------")
                self.listWidget.addItem("连抽：%d 人" % num)
                for name in name_set:
                    self.listWidget.addItem(name)
                self.listWidget.addItem("----------------------------")
                self.listWidget.setCurrentRow(self.listWidget.count() - num+2)
            else:
                print("连抽中...")


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

    def update_pushbotton(self, text):
        self.pushButton_5.setText(text)

    def enable_button(self, value):
        if value == 1:
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

        elif value == 0:
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

        elif value == 3:
            self.pushButton_5.setEnabled(False)

        elif value == 4:
            self.pushButton_5.setEnabled(True)

    def update_list(self, mode, value):
        if mode == 1:
            if value == "":
                pass
            else:
                self.listWidget.addItem(value)
                self.listWidget.setCurrentRow(self.listWidget.count() - 1)
        elif mode == 0:
            self.label_3.setText(value)

    def qtimer(self, start, time=None):
        if start == 1:
            self.timer = QTimer(self)
            self.timer.start(time)
            self.timer.timeout.connect(self.setname)
            print("计时器启动")

        elif start == 0:
            try:
                self.timer.stop()
            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        global name
        if len(name_list) == 0:
            self.show_message("名单文件为空，请输入名字（一行一个）后再重新点名！", "警告")
            self.qtimer(0)
            self.label_3.setText("名单文件为空！")
            name = ""
            try:
                self.opentext(file_path)
            except Exception as e:
                self.show_message("选择的名单文件%s不存在！" % file_path,"\n%s" % e)
        else:
            name = random.choice(name_list)
            self.label_3.setText(name)

    def show_message(self, message, title):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        if message is None:
            message = "未知错误"
        message = str(message)
        msgBox.setText(message)
        msgBox.exec_()


class WorkerSignals(QObject):
    # 定义信号
    show_progress = pyqtSignal(int, int, int)
    update_list = pyqtSignal(int, str)
    update_pushbotton = pyqtSignal(str)
    enable_button = pyqtSignal(int)
    finished = pyqtSignal()
    qtimer = pyqtSignal(int, int)


class WorkerThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.name = name
        self.allownametts = allownametts

    def run(self):
        global running
        # ptvsd.debug_this_thread()  # 在此线程启动断点调试

        def ttsread(text):
            self.signals.enable_button.emit(3)
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            self.signals.enable_button.emit(4)

        def stop():
            self.signals.update_list.emit(1, name)
            self.signals.update_pushbotton.emit(" 小窗模式")
            self.signals.enable_button.emit(1)
            self.signals.finished.emit()
            # 向主线程发送终止信号

        if running:  # 结束按钮
            self.signals.qtimer.emit(0, 0)
            self.signals.show_progress.emit(0, 0, 100)
            running = False
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if name != "":
                try:
                    print(
                        today,
                        "沉梦课堂点名器%s" % dmversion,
                        "幸运儿是： %s " % name,
                        file=open("点名器中奖名单.txt", "a"),
                    )
                except:
                    print("无法写入历史记录")
                print(today, "幸运儿是： %s " % name)
            else:
                print("名单为空!")
            try:
                pygame.mixer.music.fadeout(800)
                pygame.mixer.music.unload()
            except pygame.error as e:
                print(f"停止音乐播放时发生错误：{str(e)}")
            if self.allownametts == 1:
                ttsread(text="恭喜 %s" % name)
            elif self.allownametts == 2:
                ttsread(text=name)
            elif self.allownametts == 0:
                pass

            stop()

        else:  # 开始按钮
            running = True
            self.signals.qtimer.emit(1, 50)
            print("开始点名")
            self.signals.show_progress.emit(1, 0, 0)
            self.signals.update_pushbotton.emit(" 结束")
            self.signals.enable_button.emit(0)
            folder_name = "dmmusic"
            current_dir = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_dir, folder_name)
            os.makedirs('dmmusic', exist_ok=True)
            # 获取文件夹中的文件列表
            file_list = os.listdir(folder_path)
            if not file_list:
                print("要使用背景音乐功能，请在 %s 中放入mp3格式的音乐" % folder_path)
                return
            # 从列表中随机选择一个文件
            random_file = random.choice(file_list)
            # 生成完整的文件路径
            file_path = os.path.join(folder_path, random_file)
            try:
                print("播放音乐：%s" % file_path)
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(1)
            except pygame.error as e:
                print("无法播放音乐文件：%s，错误信息：{str(e)}") % file_path

class smallWindow(QtWidgets.QMainWindow, Ui_smallwindow):#小窗模式i
    def __init__(self,main_instance = None):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))

        self.setMinimumSize(QtCore.QSize(322, 191))
        # 设置半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.m_flag = False
        self.label_2.setText("开始")
        self.m_moved = False  # 用于检测是否移动
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", "点名器小窗模式"))
        self.timer = None
        self.runflag = None
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
            if self.runflag == True:
                self.qtimer(0)
                today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    print(
                        today,
                        "沉梦课堂点名器%s" % dmversion,
                        "幸运儿是： %s " % name,
                        file=open("点名器中奖名单.txt", "a"),
                    )
                except:
                    print("无法写入历史记录")
                print(today, "幸运儿是： %s " % name)
            else:
                self.get_name_list()# 只有未移动时才输出消息
            
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
    def qtimer(self,start, time=None):
        if start == 1:
            self.timer = QTimer()
            self.timer.start(time)
            self.timer.timeout.connect(self.setname)
            self.runflag = True

        elif start == 0:
            try:
                self.timer.stop()
                self.runflag = False
                if name != "":
                    self.main_instance.update_list(1,"小窗：%s"%name)
                else:
                    pass
            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        global name
        if name_list == []:
            name = ""
            self.label_2.setText("名单为空!")
            self.main_instance.mini(2)
            self.qtimer(0)
        else:
            name = random.choice(name_list)
            self.label_2.setText(name)

    def get_name_list(self):
            self.qtimer(1, 50)

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


class settingsWindow(QtWidgets.QMainWindow, Ui_settings):  # 设置窗口
    def __init__(self, main_instance=None):
        super().__init__()
        central_widget = QtWidgets.QWidget(self)  # 创建一个中央小部件
        self.setCentralWidget(central_widget)  # 设置中央小部件为QMainWindow的中心区域
        self.setupUi(central_widget)  # 初始化UI到中央小部件上
        self.setFixedSize(307, 419)
        self.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.groupBox_2.setTitle("名单管理")
        self.pushButton_5.setText("编辑所选名单")
        self.pushButton_4.setText("删除所选名单")
        self.pushButton_3.setText("新建名单")
        self.pushButton_2.setText("保存")
        self.checkBox_4.setText("背景图片")
        self.radioButton_3.setText("预设1")
        self.radioButton_4.setText("预设2")
        self.radioButton_5.setText("无")
        self.pushButton.setText("取消")
        self.groupBox.setTitle("功能设置")
        self.checkBox.setText("背景音乐")
        self.checkBox_2.setText("语音播报")
        self.radioButton.setText("正常模式")
        self.radioButton_2.setText("听写模式(不说\"恭喜\")")
        self.checkBox_3.setText("检查更新")
        self.setWindowTitle(QCoreApplication.translate(
            "MainWindow", "课堂点名器设置"))
        self.main_instance = main_instance
        self.read_name_list()

        self.window = QWidget()
        self.window.setWindowIcon(QtGui.QIcon(':/icons/picker.ico'))
        self.pushButton_3.clicked.connect(self.add_new_list)
        self.pushButton_4.clicked.connect(self.delete_list)
        self.pushButton_5.clicked.connect(self.edit_list)

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
            self.window, "新增名单", "请输入名单名称:")
        if ok_pressed and newfilename:
            print("新增名单名称是: %s" % newfilename)
            newnamepath = os.path.join(
                "name", f"{newfilename}.txt")  # 打开文件并写入内容
            with open(newnamepath, "w", encoding="utf8") as f:
                pass
            message = ("已创建名为 '%s.txt' 的文件，路径为: %s" %
                        (newfilename, newnamepath))

            QMessageBox.information(
                self.window, "新建成功", message, QMessageBox.Ok)
            self.main_instance.opentext(newnamepath)
            txt_name = self.refresh_name_list()
            self.comboBox_1.clear()  # 清空下拉框的选项
            self.comboBox_1.addItems(txt_name)  # 添加新的文件名到下拉框
        

    def delete_list(self):
        target_filename, ok_pressed = QInputDialog.getText(
            self.window, "删除名单", "再次输入名单名称将删除此名单！")
        if ok_pressed and target_filename:
            target_filepath = os.path.join(
                "name", f"{target_filename}.txt")
            if os.path.exists(target_filepath):
                os.remove(target_filepath)  # 删除文件
                message = ("已成功删除名为 '%s.txt' 的文件。" % target_filename)
                QMessageBox.information(
                    self.window, "删除成功", message, QMessageBox.Ok)
                txt_name = self.refresh_name_list()
                self.comboBox_1.clear()  # 清空下拉框的选项
                self.comboBox_1.addItems(txt_name)  # 添加新的文件名到下拉框
            else:
                QMessageBox.warning(
                    self.window, '警告', '名单文件不存在', QMessageBox.Ok)

    def edit_list(self):
        target_filename = self.comboBox_1.currentText()
        target_filepath = os.path.join(
                "name", f"{target_filename}"+".txt")
        if os.path.exists(target_filepath):
            self.main_instance.opentext(target_filepath)
        else:
            QMessageBox.warning(
                self.window, '警告', '名单文件不存在', QMessageBox.Ok) 

    def closeEvent(self, event):
        print("设置被关闭")
        self.main_instance.mini(2)
        self.main_instance.read_name_list(2)
        global settings_flag
        settings_flag = None
        event.accept()  # 确保仅关闭子窗口，不影响主窗口
        
    def run_settings_window(self):
        self.show()
        return self

if __name__ == "__main__":
    if hasattr(QtCore.Qt, "AA_EnableHighDpiScaling"):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_EnableHighDpiScaling, True)
    # 启用高DPI自适应
    if hasattr(QtCore.Qt, "AA_UseHighDpiPixmaps"):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = DraggableWindow()
    mainWindow.show()
    sys.exit(app.exec_())
