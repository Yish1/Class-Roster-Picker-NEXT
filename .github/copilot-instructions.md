# 沉梦课堂点名器 (Class-Roster-Picker-NEXT) 指南

## 概述

这是一个使用 Python 和 PyQt5 构建的桌面应用程序，用于从名单中随机抽取名字。它具有丰富的功能，如多种抽取模式、自定义界面、背景音乐和多语言支持。

## 核心架构

- **主入口**: `main.py` 是应用程序的入口，负责初始化主窗口 (`MainWindow`)、加载配置和处理核心逻辑。
- **UI 定义**:
    - UI 布局由 Qt Designer 创建，并保存为 `.ui` 文件 (例如 `picker.ui`, `settings.ui`)。
    - 这些 `.ui` 文件通过 `pyuic5` 编译成相应的 Python 文件 (例如 `ui.py`, `settings.py`)。
    - 资源文件 (如图片、字体) 在 `res/` 目录下，并通过 `pyrcc5` 从 `res/ui1.qrc` 编译到 `ui1_rc.py` 中。
- **模块化**:
    - `modules/config_manager.py`: 负责读写 `config.ini` 配置文件。
    - `modules/i18n.py`: 使用 `gettext` 实现国际化 (i18n)，支持运行时语言切换。
    - `main.py`, `settings.py`, `smallwindow.py`: 分别管理主窗口、设置窗口和小窗口的逻辑。
- **数据流**:
    - **名单**: 存储在 `name/` 目录下的 `.txt` 文件中，每行一个名字。
    - **配置**: `config.ini` 文件存储用户设置，如语言、主题、功能开关等。
    - **历史记录**: 抽取结果保存在 `history/` 目录中。

## 开发工作流

- **环境设置**:
  ```bash
  pip install -r requirements.txt
  ```
- **运行应用**:
  ```bash
  python main.py
  ```
- **UI 修改**:
  1. 使用 Qt Designer 编辑 `.ui` 文件。
  2. 使用 `pyuic5` 将 `.ui` 文件转换为 `.py` 文件。例如：
     ```bash
     pyuic5 -x picker.ui -o ui.py
     ```
- **资源更新**:
  1. 修改 `res/ui1.qrc` 文件以添加或删除资源。
  2. 使用 `pyrcc5` 重新编译资源文件：
     ```bash
     pyrcc5 res/ui1.qrc -o ui1_rc.py
     ```
- **国际化 (i18n)**:
  1. 在代码中使用 `_("text to translate")` 来标记需要翻译的字符串。`_` 函数由 `modules.i18n` 提供。
  2. 使用 `pygettext.py` 提取字符串到 `.pot` 文件。
  3. 使用 Poedit 或类似工具从 `.pot` 文件创建和编辑 `.po` 翻译文件。
  4. 将 `.po` 文件编译成 `.mo` 文件，并放置在 `locale/<lang>/LC_MESSAGES/` 目录下。
- **构建可执行文件**:
  项目使用 Nuitka 进行打包。`README.md` 中提供了构建命令，这是一个很好的起点：
  ```bash
  nuitka --standalone --lto=no --clang --msvc=latest --disable-ccache --windows-uac-admin --windows-console-mode=disable --enable-plugin=pyqt5,upx --output-dir=o --windows-icon-from-ico=picker.ico --nofollow-import-to=unittest main.py
  ```

## 代码约定和模式

- **配置管理**: 通过 `modules.config_manager` 中的 `read_config_file` 和 `update_entry` 函数来操作 `config.ini`。
- **多线程**: 使用 `QThreadPool` 和 `QRunnable` 来处理耗时任务（如网络请求、音乐播放），避免 UI 冻结。
- **窗口管理**: 使用全局标志 (如 `settings_flag`) 来跟踪子窗口的实例，防止重复创建。
- **样式**: 主要通过 `setStyleSheet` 在 Python 代码中直接设置 PyQt 控件的样式。
- **字体**: 自定义字体从 `res/` 目录加载，并在应用中通过 `QFontDatabase` 进行管理。
