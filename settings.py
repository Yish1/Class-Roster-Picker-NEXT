# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'e:\class roster picker\settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_settings(object):
    def setupUi(self, settings):
        settings.setObjectName("settings")
        settings.resize(682, 523)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(settings.sizePolicy().hasHeightForWidth())
        settings.setSizePolicy(sizePolicy)
        settings.setMinimumSize(QtCore.QSize(682, 523))
        settings.setMaximumSize(QtCore.QSize(682, 523))
        settings.setStyleSheet("* {\n"
"    font-size: 12px;\n"
"}")
        self.frame_5 = QtWidgets.QFrame(settings)
        self.frame_5.setGeometry(QtCore.QRect(0, 0, 331, 521))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.frame_5)
        self.groupBox.setMinimumSize(QtCore.QSize(267, 205))
        self.groupBox.setStyleSheet("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.frame_3 = QtWidgets.QFrame(self.groupBox)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 34))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.radioButton_3 = QtWidgets.QRadioButton(self.frame_3)
        self.radioButton_3.setObjectName("radioButton_3")
        self.horizontalLayout_2.addWidget(self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.frame_3)
        self.radioButton_4.setObjectName("radioButton_4")
        self.horizontalLayout_2.addWidget(self.radioButton_4)
        self.radioButton_5 = QtWidgets.QRadioButton(self.frame_3)
        self.radioButton_5.setObjectName("radioButton_5")
        self.horizontalLayout_2.addWidget(self.radioButton_5)
        self.gridLayout_4.addWidget(self.frame_3, 8, 0, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_3.setMinimumSize(QtCore.QSize(0, 0))
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_4.addWidget(self.checkBox_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 7, 0, 1, 1)
        self.frame_2 = QtWidgets.QFrame(self.groupBox)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 34))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButton = QtWidgets.QRadioButton(self.frame_2)
        self.radioButton.setObjectName("radioButton")
        self.horizontalLayout.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.frame_2)
        self.radioButton_2.setObjectName("radioButton_2")
        self.horizontalLayout.addWidget(self.radioButton_2)
        self.gridLayout_4.addWidget(self.frame_2, 5, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_4.addWidget(self.checkBox, 1, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_4.addWidget(self.checkBox_2, 4, 0, 1, 1)
        self.checkBox_4 = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_4.addWidget(self.checkBox_4, 3, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 1, 0, 2, 2)
        self.groupBox_2 = QtWidgets.QGroupBox(self.frame_5)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 193))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(37, -1, 35, -1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout_3.addWidget(self.pushButton_4, 2, 0, 1, 1)
        self.pushButton_6 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_6.setObjectName("pushButton_6")
        self.gridLayout_3.addWidget(self.pushButton_6, 4, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_3.addWidget(self.pushButton_3, 1, 0, 1, 1)
        self.comboBox_1 = QtWidgets.QComboBox(self.groupBox_2)
        self.comboBox_1.setStyleSheet("QComboBox {\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    font-size: 15px;\n"
"}\n"
"")
        self.comboBox_1.setObjectName("comboBox_1")
        self.gridLayout_3.addWidget(self.comboBox_1, 0, 0, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout_3.addWidget(self.pushButton_5, 3, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_2, 3, 0, 1, 2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.frame_5)
        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 44))
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 73))
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox_3)
        self.comboBox_2.setMinimumSize(QtCore.QSize(0, 0))
        self.comboBox_2.setMaximumSize(QtCore.QSize(236, 16777215))
        self.comboBox_2.setStyleSheet("QComboBox {\n"
"    font-size: 13px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    font-size: 15px;\n"
"}\n"
"")
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_3.addWidget(self.comboBox_2)
        self.gridLayout_2.addWidget(self.groupBox_3, 0, 0, 1, 2)
        self.frame_6 = QtWidgets.QFrame(settings)
        self.frame_6.setGeometry(QtCore.QRect(330, -3, 351, 466))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.groupBox_5 = QtWidgets.QGroupBox(self.frame_6)
        self.groupBox_5.setMinimumSize(QtCore.QSize(0, 53))
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 300))
        self.groupBox_5.setObjectName("groupBox_5")
        self.pushButton_7 = QtWidgets.QPushButton(self.groupBox_5)
        self.pushButton_7.setGeometry(QtCore.QRect(110, 10, 111, 101))
        self.pushButton_7.setStyleSheet("\n"
"QPushButton{\n"
"    border:none;\n"
"}")
        self.pushButton_7.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/picker.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_7.setIcon(icon)
        self.pushButton_7.setIconSize(QtCore.QSize(100, 100))
        self.pushButton_7.setObjectName("pushButton_7")
        self.label_2 = QtWidgets.QLabel(self.groupBox_5)
        self.label_2.setGeometry(QtCore.QRect(40, 120, 251, 21))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox_5)
        self.label_3.setGeometry(QtCore.QRect(10, 140, 311, 121))
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setScaledContents(False)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout_5.addWidget(self.groupBox_5, 2, 0, 1, 2)
        self.groupBox_6 = QtWidgets.QGroupBox(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_6.sizePolicy().hasHeightForWidth())
        self.groupBox_6.setSizePolicy(sizePolicy)
        self.groupBox_6.setMinimumSize(QtCore.QSize(0, 160))
        self.groupBox_6.setMaximumSize(QtCore.QSize(16777215, 153))
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_8.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_8.setContentsMargins(37, -1, 35, -1)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.pushButton_12 = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_12.setObjectName("pushButton_12")
        self.gridLayout_8.addWidget(self.pushButton_12, 0, 0, 1, 1)
        self.pushButton_8 = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_8.setObjectName("pushButton_8")
        self.gridLayout_8.addWidget(self.pushButton_8, 2, 0, 1, 1)
        self.pushButton_9 = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_9.setObjectName("pushButton_9")
        self.gridLayout_8.addWidget(self.pushButton_9, 4, 0, 1, 1)
        self.pushButton_10 = QtWidgets.QPushButton(self.groupBox_6)
        self.pushButton_10.setObjectName("pushButton_10")
        self.gridLayout_8.addWidget(self.pushButton_10, 3, 0, 1, 1)
        self.gridLayout_5.addWidget(self.groupBox_6, 1, 0, 1, 2)
        self.frame = QtWidgets.QFrame(settings)
        self.frame.setGeometry(QtCore.QRect(352, 449, 301, 71))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_2 = QtWidgets.QPushButton(self.frame)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 1, 1, 1)
        QtCore.QMetaObject.connectSlotsByName(settings)
import res
