from PyQt5 import QtWidgets, QtCore, QtGui
from Ui import Ui_msgbox
from modules.i18n import _

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