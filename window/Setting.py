from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QCoreApplication, QStandardPaths
from PyQt5.QtWidgets import QWidget, QInputDialog, QMessageBox, QFileDialog, QListWidgetItem

from window.Msgbox import msgbox
from Ui import Ui_Settings

from moudles import *

import os, difflib, tarfile
from datetime import datetime

# 便捷引用全局状态
state = app_state

class SettingsWindow(QtWidgets.QMainWindow, Ui_Settings):  # 设置窗口
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

        self.main_instance = main_instance
        self.read_name_list()
        self.read_config()
        self.find_language()
        self.find_history()
        self.slider_value_changed("init")
        self.apply_translations()

        self.enable_tts = None
        self.title_text = None
        self.enable_update = None
        self.enable_bgimg = None
        self.language_value = None
        self.disable_repetitive = None
        self.enable_bgmusic = None
        self.inertia_roll = None
        self.file_path_bak = None # 文件路径备份
        self.bak_file_path = None # 备份文件路径
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
        self.comboBox_2.currentIndexChanged.connect(self.change_language)
        self.pushButton_12.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'name'))))
        self.pushButton_15.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'name'))))
        self.pushButton_10.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'dmmusic'))))
        self.pushButton_9.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'images'))))
        self.pushButton_8.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'history'))))
        self.pushButton_11.clicked.connect(self.save_name_list)
        self.pushButton_13.clicked.connect(self.read_name_inlist)
        self.pushButton_14.clicked.connect(lambda: os.system(
            "start https://cmxz.top/ktdmq#toc-head-8"))
        self.pushButton_16.clicked.connect(lambda: self.open_fold((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'history'))))
        self.pushButton_17.clicked.connect(lambda: self.delete_file((os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'history'))))
        self.pushButton_18.clicked.connect(self.save_allconfig)
        self.pushButton_19.clicked.connect(self.load_backup)
        self.pushButton_20.clicked.connect(self.apply_backup)

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
        self.pushButton_20.hide()
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
        self.label_9.show()
        self.label_9.setText(_("可以开始点名后调整滑块预览速度"))
        if mode == "init":
            self.horizontalSlider.setValue(state.roll_speed)
            self.label_6.setText(f"{state.roll_speed} ms")
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
        name_dir = os.path.join(state.appdata_path, "name")
        txt_name = [filename for filename in os.listdir(
            name_dir) if filename.endswith(".txt")]
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

        self.file_path = os.path.join(state.appdata_path, "name", selected_text_inlist+".txt")

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
                state.appdata_path, "name", f"{newfilename}.txt")  # 打开文件并写入内容
            if not os.path.exists(newnamepath):
                log_print("新增名单名称是: %s" % newfilename)
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
            target_folder = os.path.join(state.appdata_path, "history")
            text1 = _("删除历史记录")
            text2 = _("输入要删除的历史记录名称：(无需输入\"中奖记录\")")
        else:
            target_folder = os.path.join(state.appdata_path, "name")
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
                state.appdata_path, "history", selected_text_inlist+".txt")

            if not self.file_path or not os.path.isfile(self.file_path):
                return

            else:
                file_content = self.read_txt()
                self.textEdit_2.setPlainText(file_content)

        else:
            # Find模式，读取指定目录下的文件夹名
            history_dir = os.path.join(state.appdata_path, "history")
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
                    log_print(f"目录不存在: {history_dir}")
            except Exception as e:
                log_print(f"读取历史文件夹失败: {e}")

    def find_language(self):
        locale_dir = "./locale"
        try:
            if os.path.exists(locale_dir) and os.path.isdir(locale_dir):
                folders = [folder for folder in os.listdir(
                    locale_dir) if os.path.isdir(os.path.join(locale_dir, folder))]
                self.comboBox_2.addItems(folders)
                self.comboBox_2.setCurrentText(state.language_value)
        except Exception as e:
            log_print(f"读取语言失败:{e}")

    def change_language(self):
        """Change language at runtime without restart."""
        try:
            self.language_value = self.comboBox_2.currentText()
            # Set module-level gettext to new language
            set_language(self.language_value)
            # Persist selection to config
            config_path = os.path.join(state.appdata_path, 'config.ini')
            update_entry('language', self.language_value , config_path)
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
        log_print("设置被关闭")
        try:
            self.main_instance.mini(2)
            self.main_instance.read_name_list()
            self.main_instance.get_selected_file(0)
        except Exception as e:
            log_print(e)
        state.settings_flag = None
        event.accept()  # 确保仅关闭子窗口,不影响主窗口

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
            self.label_2.setText(_("沉梦课堂点名器 V%s") % state.dmversion)
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
            self.groupBox_8.setTitle(_("备份"))
            self.pushButton_18.setText(_("一键备份所有内容"))
            self.groupBox_9.setTitle(_("恢复"))
            self.pushButton_20.setText(_("确认恢复"))
            self.pushButton_19.setText(_("导入备份"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _("备份恢复"))
            self.setWindowTitle(QCoreApplication.translate(
                "MainWindow", _("沉梦课堂点名器设置")))
        except Exception as e:
            log_print(f"settings apply_translations error: {e}")

    def read_config(self):
        if state.allownametts == 2:
            self.checkBox_2.setChecked(True)
            self.radioButton.setChecked(True)
            self.radioButton_2.setChecked(False)
        elif state.allownametts == 3:
            self.checkBox_2.setChecked(True)
            self.radioButton.setChecked(False)
            self.radioButton_2.setChecked(True)
        elif state.allownametts == 1 or state.allownametts == 0:
            self.checkBox_2.setChecked(False)
            self.radioButton.setEnabled(False)
            self.radioButton_2.setEnabled(False)

        if state.checkupdate == 2:
            self.checkBox_3.setChecked(True)
        else:
            self.checkBox_3.setChecked(False)

        if state.bgimg == 1:
            self.radioButton_3.setChecked(True)
            self.radioButton_4.setChecked(False)
            self.radioButton_5.setChecked(False)
        elif state.bgimg == 2:
            self.radioButton_3.setChecked(False)
            self.radioButton_4.setChecked(True)
            self.radioButton_5.setChecked(False)
        elif state.bgimg == 3:
            self.radioButton_3.setChecked(False)
            self.radioButton_4.setChecked(False)
            self.radioButton_5.setChecked(True)

        if state.non_repetitive == 1:
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

        if state.bgmusic == 1:
            self.checkBox_4.setChecked(True)
        elif state.bgmusic == 0:
            self.checkBox_4.setChecked(False)

        if state.inertia_roll == 1:
            self.checkBox_5.setChecked(True)
        else:
            self.checkBox_5.setChecked(False)

        if state.title_text:
            self.lineEdit.setText(state.title_text)

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
                    state.threadpool.start(self.check_speaker)

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
                    log_print("正在开启播报正常模式")
                    self.enable_tts = 1
                elif checked and not self.radioButton.isChecked() and self.radioButton_2.isChecked():
                    log_print("正在开启播报听写模式")
                    self.enable_tts = 2

            elif not self.checkBox_2.isChecked():
                self.radioButton.setEnabled(False)
                self.radioButton_2.setEnabled(False)
                log_print("正在关闭播报")
                self.enable_tts = 0

        elif key == "enable_update":
            self.enable_update = 2 if checked else 1
            if not checked:
                self.main_instance.show_message(
                    _("您正在关闭检查更新功能！更新意味着带来 新功能、优化 以及修复错误，强烈建议您开启此功能！"), _("警告"))
                log_print("正在关闭检查更新")
            else:
                log_print("正在开启检查更新")

        elif key == "enable_bgimg":
            if checked:
                if self.radioButton_3.isChecked():
                    self.enable_bgimg = 1
                    log_print("背景1")
                elif self.radioButton_4.isChecked():
                    self.enable_bgimg = 2
                    self.main_instance.show_message(
                        _("您正在使用自定义背景功能，由于此工具可能需要在公众场合展示，请选择适宜场景的合适背景！ \n因使用不合适的背景图片而造成的后果由您自行承担！\n\n使用教程：\n\n在稍后打开的\\images文件夹中放入您喜欢的图片(建议暗色系、长宽比16:9)，程序将随机选取图片使用。"), _("声明!"))
                    folder_path = os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'images')
                    os.makedirs(folder_path, exist_ok=True)
                    self.main_instance.opentext(folder_path)
                    log_print("背景自定义")
                elif self.radioButton_5.isChecked():
                    self.enable_bgimg = 3
                    log_print("背景无")

        elif key == "disable_repetitive":
            self.disable_repetitive = 1 if checked else 0
            if not checked:
                log_print("正在关闭不放回模式")
            else:
                log_print("正在开启不放回模式")
                self.main_instance.show_message(
                    _("不放回模式，即单抽结束后的名字不会放回列表中，下次将不会抽到此名字\n\n当名单抽取完成、切换名单 或 手动点击按钮 时将会重置不放回列表！"), _("说明"))

        elif key == "enable_bgmusic":
            self.enable_bgmusic = 1 if checked else 0
            if not checked:
                log_print("正在关闭背景音乐")
            else:
                log_print("正在开启背景音乐")
                self.main_instance.show_message(
                    _("开启背景音乐功能后，需要在稍后打开的背景音乐目录下放一些您喜欢的音乐\n程序将随机选取一首，播放随机的音乐进度\n\n注：程序自带几首默认音频，当您在音乐目录下放入音乐后，默认音频将不会再进入候选列表！"), _("提示"))
                folder_path = os.path.join(os.getenv('APPDATA'), 'CMXZ', 'CRP', 'dmmusic')
                os.makedirs(folder_path, exist_ok=True)
                self.open_fold(folder_path)

        elif key == "inertia_roll":
            self.inertia_roll = 1 if checked else 0
            if not checked:
                log_print("正在关闭惯性滚动")
            else:
                log_print("正在开启惯性滚动")

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
            log_print("未知错误")
            return

        for item in selected_items:
            count_target = item.text()

        file = os.path.join(state.appdata_path, "history", "%s.txt" % count_target)
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
            log_print("正在保存为文本")
            cresult = _("\"%s\" 名单中奖统计:\n\n" %
                        (count_target.replace("中奖记录", "")))
            result_path = os.path.join(state.appdata_path, "中奖统计.txt")
            for name, count in sorted_counts:
                cresult += "%s 出现了 %s 次\n" % (name, count)
                with open(result_path, 'w', encoding="utf-8") as file:
                    file.write(cresult)

            self.textEdit_2.setPlainText(
                _("统计已保存至%s下的/中奖统计.txt中\n(每次统计会覆盖上一次统计结果)\n\n") % state.appdata_path + cresult)

        except Exception as e:
            log_print("读取文件时发生错误:", e)
            self.main_instance.show_message(
                _("Error: 历史记录文件不存在，无法统计次数！\n%s") % e, _("错误"))
            return

    def save_allconfig(self):
        if hasattr(state, "appdata_path") and state.appdata_path:
            try:
                src_dir = state.appdata_path
                ts = datetime.now().strftime("%Y-%m-%d-%H%M_%S")
                default_name = f"{ts}.CRPBAK"

                # 默认目录：桌面
                desktop_dir = (
                    QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
                    or os.path.join(os.path.expanduser("~"), "Desktop")
                )

                # 让用户选择保存位置
                dest_path, a = QFileDialog.getSaveFileName(
                    self.window,
                    _("选择备份保存位置"),
                    os.path.join(desktop_dir, default_name),
                    "CRP Backup (*.CRPBAK);;All Files (*.*)",
                )
                if not dest_path:
                    return  # 用户取消
                if not dest_path.lower().endswith(".crpbak"):
                    dest_path += ".CRPBAK"

                abs_src_dir = os.path.abspath(src_dir)
                abs_dest_path = os.path.abspath(dest_path)

                def add_to_tar(tar, current_dir):
                    """递归扫描目录并添加文件"""
                    for entry in os.scandir(current_dir):
                        try:
                            full_path = entry.path
                            if entry.is_dir(follow_symlinks=False):
                                add_to_tar(tar, full_path)  # 递归进入子目录
                            elif entry.is_file(follow_symlinks=False):
                                # 避免把目标备份文件自身加入
                                if os.path.abspath(full_path) == abs_dest_path:
                                    continue
                                arcname = os.path.relpath(full_path, abs_src_dir)
                                tar.add(full_path, arcname=arcname)
                        except Exception as e:
                            log_print(f"跳过文件 {entry.path}: {e}")

                # 打包为 tar.gz 实际格式，扩展名为 .CRPBAK
                
                with tarfile.open(dest_path, "w:gz") as tar:
                    add_to_tar(tar, src_dir)
                # with open(dest_path, "rb+") as f: # 消除Gzip头部
                #     header = f.read(3)
                #     if header[:3] == b'\x1f\x8b\x08':
                #         f.seek(0)
                #         f.write(b'\x00' * 3)

                QMessageBox.information(
                    self.window,
                    _("备份完成"),
                    _("已创建备份文件：%s") % dest_path,
                    QMessageBox.Ok,
                )
                try:
                    self.listWidget_3.clear()
                    self.listWidget_3.addItem(_("已创建备份文件：%s") % dest_path)
                    os.startfile(os.path.dirname(dest_path))
                except Exception:
                    pass

            except Exception as e:
                log_print(f"备份失败: {e}")
                QMessageBox.warning(
                    self.window,
                    _("错误"),
                    _("Error: 备份失败！\n%s") % e,
                    QMessageBox.Ok,
                )
        else:
            QMessageBox.warning(self.window, _("错误"), _("未找到数据目录，无法备份。"), QMessageBox.Ok)
            
    def load_backup(self):
        self.bak_file_path, a = QFileDialog.getOpenFileName(None, _("选择备份文件"), "", "CRP Backup (*.CRPBAK);;All Files (*.*)")
        if not self.bak_file_path:
            return  # 用户取消

        try:
            # with open(file_path, "r+b") as f:
            #     f.seek(0)
            #     f.write(b"\x1f\x8b\x08")
            self.listWidget_3.clear()
            self.pushButton_20.show()

            with tarfile.open(self.bak_file_path, "r:gz") as tar:
                log_print("备份文件结构：")
                folder_count = {}
                file_tree = ""
                for member in tar.getmembers():
                    log_print("  ├─", member.name)
                    file_tree += "  ├─ %s\n" % member.name

                    folder = os.path.dirname(member.name) or "root"
                    folder_count[folder] = folder_count.get(folder, 0) + 1

            if len(folder_count) <= 1 and "config.ini" not in file_tree:
                self.listWidget_3.addItem(_("警告：备份文件中未找到任何有效数据！"))
                self.pushButton_20.setEnabled(False)
                return

            self.listWidget_3.addItem(_("加载的备份文件路径: %s") % self.bak_file_path)
            self.listWidget_3.addItem(_("！！！请确定以下数据后，点击\"确认恢复\"按钮将覆盖当前数据！！！\n"))
            self.pushButton_20.setEnabled(True)

            if "config.ini" in file_tree:
                self.listWidget_3.addItem(_("读取到配置文件: config.ini"))
            if folder_count.get("name", None) is not None:
                self.listWidget_3.addItem(_("读取到 %s 个名单") % folder_count["name"])
            if folder_count.get("history", None) is not None:
                self.listWidget_3.addItem(_("读取到 %s 个历史记录") % folder_count["history"])
            if folder_count.get("dmmusic", None) is not None:
                self.listWidget_3.addItem(_("读取到 %s 个背景音乐文件") % folder_count["dmmusic"])
            if folder_count.get("images", None) is not None:
                self.listWidget_3.addItem(_("读取到 %s 个背景图片文件") % folder_count["images"])

            self.listWidget_3.addItem(_("\n备份文件结构："))
            self.listWidget_3.addItem(file_tree)

            # QMessageBox.information(None, "成功", "文件已加载并打印结构到控制台！")

        except Exception as e:
            QMessageBox.critical(None, "错误", f"打开或解析文件失败：\n{e}")
        
    def apply_backup(self):
        try:
            with tarfile.open(self.bak_file_path, "r:gz") as tar:
                members = tar.getmembers()
                for member in tar.getmembers():
                    target_path = os.path.join(state.appdata_path, member.name)
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    tar.extract(member, path=state.appdata_path)
                log_print(f"所有文件已解压至: {state.appdata_path}")

            QMessageBox.information(None, _("成功"), _("备份已成功恢复至：\n%s，部分设置需要重启程序后生效！") % state.appdata_path)
            self.close()

        except Exception as e:
            QMessageBox.critical(None, _("错误"), _("应用备份失败：\n%s") % e)