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
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QDesktopWidget, QMessageBox, QListView, QMainWindow, QGridLayout, QInputDialog
from PyQt5.QtCore import QThreadPool, pyqtSignal, QRunnable, QObject, QCoreApplication
from datetime import datetime, timedelta
from smallwindow import Ui_smallwindow  # 导入ui文件
from Crypto.Cipher import ARC4
import webbrowser as web

class smallWindow(QtWidgets.QMainWindow, Ui_smallwindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 初始化UI
        self.setMinimumSize(QtCore.QSize(322, 191))
        # 设置半透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.m_flag = False
        self.label_2.setText("开始")
        self.m_moved = False  # 用于检测是否移动
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.timer = None
        self.runflag = None

    def closeEvent(self, event):
        # 关闭其他窗口的代码
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QWidget) and widget != self:
                widget.close()
        event.accept()

    def center(self):
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 1.75),
                  int((screen.height() - size.height()) / 0.4))

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
            else:
                self.get_name_list(self.name_list)# 只有未移动时才输出消息
            
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
    def qtimer(self,start, time=None):
        if start == 1:
            self.timer = QTimer()
            self.timer.start(time)
            self.timer.timeout.connect(self.setname)
            print("计时器启动")
            self.runflag = True

        elif start == 0:
            try:
                self.timer.stop()
                self.runflag = False
            except Exception as e:
                print(f"无法停止计时器:{e}")

    def setname(self):
        global name
        name = random.choice(self.name_list)
        self.label_2.setText(name)

    def get_name_list(self,name_list,mode = None):
        if mode == 0:
            self.name_list = name_list
        else:
            self.qtimer(1, 15)

    def closeEvent(self, event):
        print("子窗口被关闭")
        event.accept()  # 确保仅关闭子窗口，不影响主窗口

    def close_window(self):
        self.close() 

def run_small_window(name_list,mode = None):
    small_Window = smallWindow()
    if mode == 1:
        small_Window.close_window()
    else:
        small_Window.show()
        small_Window.get_name_list(name_list,0)
        return small_Window

