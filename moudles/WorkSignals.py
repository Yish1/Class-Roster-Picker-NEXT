from PyQt5.QtCore import QObject, pyqtSignal

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
