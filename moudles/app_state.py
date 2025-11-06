# -*- coding: utf-8 -*-
"""
应用全局状态管理模块
使用单例模式管理应用的全局状态，避免使用 global 关键字
"""
from typing import Optional, List
from datetime import datetime
from PyQt5.QtCore import QThreadPool
import pygame


class AppState:
    """应用全局状态管理类（单例模式）"""
    
    _instance: Optional['AppState'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        # ============ 应用版本 ============
        self.dmversion = 6.62
        
        # ============ 配置变量 ============
        self.allownametts: Optional[int] = None   # 1关闭 2正常模式 3听写模式
        self.checkupdate: Optional[int] = None    # 0/1关闭 2开启
        self.bgimg: Optional[int] = None         # 1默认 2自定义 3无
        self.latest_version: Optional[str] = None
        self.last_name_list: Optional[str] = None  # 记录上次选中的名单
        self.non_repetitive: Optional[int] = None  # 0关闭 1开启
        self.bgmusic: Optional[int] = None        # 0关闭 1开启
        self.first_use: Optional[int] = None
        self.roll_speed: Optional[int] = None
        self.inertia_roll: Optional[int] = None   # 0关闭 1开启
        self.title_text: Optional[str] = None     # 标题文字: 幸运儿是:
        self.language_value: Optional[str] = None
        self.need_move_config: Optional[str] = None # 是否需要移动配置文件
        
        # ============ 运行时变量 ============
        self.appdata_path: Optional[str] = None   # AppData 路径
        self.name: Optional[str] = None
        self.mrunning: bool = False
        self.running: bool = False
        self.default_music: bool = False
        self.default_name_list: str = "默认名单"  # 需要翻译时在使用处调用 _()
        self.name_list: List[str] = []
        self.history_file: str = ""
        self.file_path: str = ""
        self.non_repetitive_list: List[str] = []
        self.non_repetitive_dict = {}
        self.namelen: int = 0
        self.newversion: Optional[float] = None
        self.origin_name_list: Optional[str] = None
        self.cust_font: Optional[str] = None
        self.name_path: Optional[str] = None
        self.selected_file: Optional[str] = None
        self.connect: bool = False
        
        # ============ 窗口标识符 ============
        self.windows_move_flag: Optional[bool] = None
        self.small_window_flag = None  # 小窗口实例引用
        self.settings_flag = None      # 设置窗口实例引用
        
        # ============ 系统对象 ============
        self.today: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.threadpool: QThreadPool = QThreadPool()
        
        # 初始化 pygame mixer
        try:
            pygame.mixer.init()
        except Exception as e:
            try:
                from moudles.logger_util import log_print as _log
                _log(f"pygame mixer 初始化失败: {e}")
            except Exception:
                try:
                    print(f"pygame mixer 初始化失败: {e}")
                except Exception:
                    pass
    
    def reset_runtime_state(self):
        """重置运行时状态（用于测试或重启）"""
        self.name = None
        self.mrunning = False
        self.running = False
        self.default_music = False
        self.name_list = []
        self.history_file = ""
        self.non_repetitive_list = []
        self.non_repetitive_dict = {}
        self.namelen = 0
        self.origin_name_list = None
        self.today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def reset_window_flags(self):
        """重置窗口标识符"""
        self.windows_move_flag = None
        self.small_window_flag = None
        self.settings_flag = None


# 提供便捷的全局实例访问
app_state = AppState()


def get_app_state() -> AppState:
    """获取全局应用状态实例"""
    return app_state
