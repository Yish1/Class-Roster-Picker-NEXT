from PyQt5.QtCore import QRunnable
import requests
import platform

# Avoid circular import: import required symbols directly
from .app_state import app_state
from .WorkSignals import WorkerSignals
from .i18n import _
from .logger_util import log_print

state = app_state

class UpdateThread(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        # debugpy.breakpoint()  # 在此线程启动断点调试
        headers = {
            'User-Agent': 'CMXZ-CRP_%s,%s,%s,%s,%s,%s%s_%s' % (state.dmversion, state.allownametts, state.bgimg, state.bgmusic, state.language_value, platform.system(), platform.release(), platform.machine())
        }
        log_print(headers)
        updatecheck = "https://cmxz.top/programs/dm/check.php"
        # try:
        #     check_mode = requests.get(
        #         updatecheck + "?mode", timeout=5, headers=headers)
        #     if int(check_mode.text) == 1:
        #         log_print("检测到强制更新版本，这意味着当前版本有严重bug，请更新至最新版本！")
        #         state.checkupdate = 2
        #         state.latest_version = 0
        # except:
        #     pass
        if state.checkupdate == 2:
            try:
                page = requests.get(updatecheck, timeout=5, headers=headers)
                state.newversion = float(page.text)
                log_print("云端版本号为:", state.newversion)
                findnewversion = _("检测到新版本！")
                if state.newversion > state.dmversion:# and float(state.latest_version) < state.newversion:
                    log_print("检测到新版本:", state.newversion,
                          "当前版本为:", state.dmversion)
                    new_version_detail = requests.get(
                        updatecheck + "?detail", timeout=5, headers=headers)
                    new_version_detail = new_version_detail.text
                    self.signals.find_new_version.emit(_("云端最新版本为%s，要现在下载新版本吗？<br>您也可以稍后访问沉梦小站官网获取最新版本。<br><br>%s") % (
                        state.newversion, new_version_detail), findnewversion)
                # else:
                #     if float(state.latest_version) == state.newversion and state.dmversion != state.newversion:
                #         log_print("\n已忽略%s版本更新,当前版本：%s" % (state.newversion, state.dmversion))
                #         findnewversion += _("(已忽略)")
                #         self.signals.update_list.emit(1, findnewversion)
                if state.newversion:
                    state.connect = True
            except Exception as e:
                log_print(f"网络异常,无法检测更新:{e}")
                noconnect = _("网络连接异常，检查更新失败")
                self.signals.update_list.emit(1, noconnect)

        elif state.checkupdate == 1:
            log_print("检查更新已关闭")

        self.signals.finished.emit()