import ast
import datetime
import io
import json
import locale
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
import warnings
from collections import Counter
import ctypes
import fnmatch
from typing import Optional
from tkinter import filedialog, messagebox, ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    # 只在开发环境且未打包时尝试安装
    if not getattr(sys, 'frozen', False) and not hasattr(sys, '_MEIPASS'):
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinterdnd2"])
            from tkinterdnd2 import TkinterDnD, DND_FILES
            DND_AVAILABLE = True
        except:
            DND_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None

warnings.filterwarnings("ignore", category=SyntaxWarning)

class ExePathManager:
    """
    跨打包工具的exe路径管理器
    兼容: PyInstaller, Nuitka, cx_Freeze 等
    """

    @staticmethod
    def is_frozen() -> bool:
        """
        判断程序是否被打包
        返回: True表示已打包，False表示开发环境
        """
        # 检查多种打包工具的标识
        frozen_flags = [
            getattr(sys, 'frozen', False),
            hasattr(sys, '_MEI_ARCHIVE'),  # PyInstaller
            getattr(sys, 'nuitka_is_frozen', False),  # Nuitka
        ]
        
        # 增强检测：Nuitka 打包后 sys.frozen 可能为 False
        if not any(frozen_flags):
            # 方法1: 检查 sys.argv[0] 是否以 .exe 结尾
            if sys.argv[0].lower().endswith('.exe'):
                return True
            # 方法2: 检查 sys.executable 是否在临时目录
            if 'temp' in sys.executable.lower() or 'onefile' in sys.executable.lower():
                return True
            # 方法3: 使用 Windows API 获取当前进程名
            if sys.platform == 'win32':
                try:
                    import ctypes
                    buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.kernel32.GetModuleFileNameW(
                        ctypes.wintypes.HMODULE(0),
                        buffer,
                        ctypes.wintypes.MAX_PATH
                    )
                    exe_path = buffer.value
                    if exe_path.lower().endswith('.exe'):
                        return True
                except:
                    pass
        
        return any(frozen_flags)

    @staticmethod
    def get_real_exe_path() -> str:
        """
        获取exe真实路径（不受临时解压影响）
        返回: exe文件的完整绝对路径
        """
        # 开发环境：直接返回__file__
        if not ExePathManager.is_frozen():
            return os.path.abspath(__file__)

        # 打包环境：优先使用Windows API获取真实路径
        try:
            buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.kernel32.GetModuleFileNameW(
                ctypes.wintypes.HMODULE(0),
                buffer,
                ctypes.wintypes.MAX_PATH
            )
            real_path = buffer.value
            if os.path.exists(real_path) and os.path.isfile(real_path):
                return real_path
        except:
            pass

        # 回退到 sys.argv[0]
        try:
            if len(sys.argv) > 0:
                path = os.path.abspath(sys.argv[0])
                if os.path.exists(path):
                    return path
        except:
            pass

        # 最后尝试 sys.executable
        return os.path.abspath(sys.executable)

    @staticmethod
    def get_exe_directory() -> str:
        """获取exe所在目录"""
        exe_path = ExePathManager.get_real_exe_path()
        return os.path.dirname(exe_path)

    @staticmethod
    def get_resource_path(relative_path: str = '') -> str:
        """获取exe同目录下资源文件的绝对路径"""
        base_dir = ExePathManager.get_exe_directory()
        return os.path.join(base_dir, relative_path)

    @staticmethod
    def is_temp_directory(path: str) -> bool:
        """判断路径是否在临时目录"""
        temp_dirs = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('TEMP', ''), ''),
            os.path.join(os.environ.get('TMP', ''), ''),
        ]
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(temp_dir) for temp_dir in temp_dirs if temp_dir)

# ==================== 常量（frozenset 加速查找）====================
STANDARD_LIBS = frozenset({
    "abc", "argparse", "array", "ast", "asyncio", "atexit", "base64", "bdb",
    "binascii", "bisect", "builtins", "bz2", "calendar", "cgi", "cmath", "cmd",
    "code", "codecs", "codeop", "collections", "colorsys", "compileall", "concurrent",
    "configparser", "contextlib", "contextvars", "copy", "copyreg", "cProfile", "csv",
    "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal", "difflib", "dis",
    "distutils", "doctest", "email", "encodings", "enum", "errno", "faulthandler",
    "fcntl", "filecmp", "fileinput", "fnmatch", "fractions", "ftplib", "functools",
    "gc", "getopt", "getpass", "gettext", "glob", "graphlib", "grp", "gzip",
    "hashlib", "heapq", "hmac", "html", "http", "idlelib", "imaplib", "imghdr",
    "imp", "importlib", "inspect", "io", "ipaddress", "itertools", "json", "keyword",
    "lib2to3", "linecache", "locale", "logging", "lzma", "mailbox", "mailcap",
    "marshal", "math", "mimetypes", "mmap", "modulefinder", "msilib", "msvcrt",
    "multiprocessing", "netrc", "nis", "nntplib", "numbers", "operator", "optparse",
    "os", "ossaudiodev", "pathlib", "pdb", "pickle", "pickletools", "pipes",
    "pkgutil", "platform", "plistlib", "poplib", "posix", "posixpath", "pprint",
    "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
    "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter",
    "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex", "shutil",
    "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver", "spwd",
    "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog", "tabnanny",
    "tarfile", "telnetlib", "tempfile", "termios", "test", "textwrap", "threading",
    "time", "timeit", "token", "tokenize", "trace", "traceback",
    "tracemalloc", "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
    "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
    "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc",
    "zipapp", "zipfile", "zipimport", "zlib", "_thread", "_winapi", "nt", "ntpath",
    "zoneinfo", "tomllib","tkinter","tk"
})

MODULE_TO_PACKAGE = {
    "PIL": "pillow", "cv2": "opencv-python", "yaml": "PyYAML",
    "sklearn": "scikit-learn", "skimage": "scikit-image", "bs4": "beautifulsoup4",
    "dateutil": "python-dateutil", "serial": "pyserial", "usb": "pyusb",
    "Crypto": "pycryptodome", "OpenSSL": "pyOpenSSL", "wx": "wxPython",
    "nuitka": "nuitka", "PyInstaller": "pyinstaller", "tk": "tk"
}

PACKAGE_TO_MODULE = {v: k for k, v in MODULE_TO_PACKAGE.items()}
PACKAGE_TO_MODULE.update({
    "opencv-python": "cv2", "beautifulsoup4": "bs4", "python-dateutil": "dateutil",
    "pycryptodome": "Crypto", "pyOpenSSL": "OpenSSL", "pillow": "PIL",
    "PyYAML": "yaml", "scikit-learn": "sklearn", "scikit-image": "skimage",
    "pyserial": "serial", "pyusb": "usb", "wxPython": "wx", "tkinter": "tk",
    "pyinstaller": "PyInstaller"
})

EXCLUDE_PACKAGES = frozenset({
    "pyinstaller", "nuitka", "py2exe", "cx_freeze", "pyoxidizer", "pynsist",
    "py2app", "pytest", "nose", "coverage", "tox", "black", "flake8",
    "pylint", "mypy", "sphinx", "mkdocs", "pdoc", "ipdb", "pdbpp",
    "debugpy", "setuptools", "wheel", "win32api"
})

MIRROR = "https://pypi.tuna.tsinghua.edu.cn/simple"

# ==================== 工具函数 ====================
def get_startupinfo():
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None

def safe_widget_call(widget, method, *args, **kwargs):
    try:
        if widget and widget.winfo_exists():
            return getattr(widget, method)(*args, **kwargs)
    except tk.TclError:
        pass
    return None
# 平台常量
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')
IS_MACOS = sys.platform == 'darwin'

# 非法字符
ILLEGAL_CHARS = '<>:"/\\|?*' if IS_WINDOWS else '/'

def validate_path(path):
    """验证路径是否包含非法字符，返回 (is_valid, error_msg)"""
    if not path:
        return False, "路径不能为空"
    
    filename = os.path.basename(path)
    found = [c for c in ILLEGAL_CHARS if c in filename]
    
    if found:
        return False, f"文件名包含非法字符: {', '.join(found)}\n请修改后再试"
    
    if filename.startswith(' ') or filename.endswith(' '):
        return False, "文件名不能以空格开头或结尾"
    
    return True, ""
# ==================== 主题管理器 ====================
class ThemeManager:
    THEMES = {
        "🌞 默认主题": {"bg_main": "#f5f5f5", "bg_card": "#ffffff", "bg_input": "#fafafa",
            "border": "#e0e0e0", "text": "#212121", "text_secondary": "#757575",
            "accent": "#9e9e9e", "accent_hover": "#bdbdbd", "log_bg": "#fafafa", "log_fg": "#424242"},
        "🌿 薄荷绿意": {"bg_main": "#e8f5e9", "bg_card": "#c8e6c9", "bg_input": "#a5d6a7",
            "border": "#81c784", "text": "#1b5e20", "accent": "#4caf50", "accent_hover": "#66bb6a",
            "log_bg": "#e8f5e9", "log_fg": "#2e7d32"},
        "🍊 暖阳橙光": {"bg_main": "#fff3e0", "bg_card": "#ffe0b2", "bg_input": "#ffcc80",
            "border": "#ffb74d", "text": "#7c4d0f", "accent": "#ff9800", "accent_hover": "#ffa726",
            "log_bg": "#fff3e0", "log_fg": "#7c4d0f"},
        "🌸 樱花粉嫩": {"bg_main": "#fce4ec", "bg_card": "#f8bbd0", "bg_input": "#f48fb1",
            "border": "#f06292", "text": "#880e4f", "accent": "#e91e63", "accent_hover": "#f06292",
            "log_bg": "#fce4ec", "log_fg": "#880e4f"},
        "🌌 星际紫韵": {"bg_main": "#f3e8ff", "bg_card": "#e9d5ff", "bg_input": "#d8b4fe",
            "border": "#c084fc", "text": "#4a1a7a", "accent": "#9333ea", "accent_hover": "#a855f7",
            "log_bg": "#2d1b4e", "log_fg": "#e9d5ff"},
        "🌊 深海蔚蓝": {"bg_main": "#e3f2fd", "bg_card": "#bbdefb", "bg_input": "#90caf9",
            "border": "#64b5f6", "text": "#0d47a1", "accent": "#2196f3", "accent_hover": "#42a5f5",
            "log_bg": "#e3f2fd", "log_fg": "#1565c0"},
    }

    def __init__(self, app):
        self.app = app
        self.names = list(self.THEMES.keys())
        self.idx = 0
        self.current = self.names[0]

    def next(self):
        self.idx = (self.idx + 1) % len(self.names)
        self.current = self.names[self.idx]
        self.apply()

    def apply(self):
        c = self.THEMES[self.current]
        app = self.app
        app.root.configure(bg=c["bg_main"])
        safe_widget_call(app.log_text, 'configure', bg=c["log_bg"], fg=c["log_fg"], insertbackground=c["text"])
        style = ttk.Style()
        style.configure("TLabel", background=c["bg_main"], foreground=c["text"])
        style.configure("TLabelframe", background=c["bg_card"])
        style.configure("TLabelframe.Label", background=c["bg_card"], foreground=c["text"])
        style.configure("TFrame", background=c["bg_main"])
        style.configure("TEntry", fieldbackground=c["bg_input"], foreground=c["text"])
        style.configure("TProgressbar", background=c["accent"], troughcolor=c.get("progress_bg", "#eeeeee"))
        safe_widget_call(app.status_bar, 'configure', background=c["bg_card"])
        safe_widget_call(app.theme_btn, 'config', text=self.current)
        self._update_buttons(c)

    def _update_buttons(self, c):
        def rec(w):
            if w.winfo_class() == 'Button' and hasattr(w, 'normal_bg'):
                if w is self.app.theme_btn:
                    w.normal_bg, w.hover_bg, w.hover_fg = c["accent"], c["accent_hover"], "#ffffff"
                    safe_widget_call(w, 'configure', bg=c["accent"], fg="#ffffff")
                else:
                    w.normal_bg, w.hover_bg, w.hover_fg = c["bg_card"], c["accent"], "#ffffff"
                    safe_widget_call(w, 'configure', bg=c["bg_card"], fg=c["text"])
            for child in w.winfo_children():
                rec(child)
        rec(self.app.root)

class VersionInfoDialog(tk.Toplevel):
    def __init__(self, parent, app, version_data):
        super().__init__(parent)
        self.app = app
        self.result = version_data.copy()
        self.title("版本信息设置")
        self.geometry("400x350")
        self.transient(parent)
        #self.grab_set()
        
        self.setup_ui()
        self.load_data(version_data)
       
        # ✅ 修复：绑定方法名改为 self.on_drop
        if DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self.on_drop)
    
    def setup_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main, text="支持变量：{year}, {month}, {day}, {hour}, {minute}\n可将 version.txt 拖入窗口自动解析",
                 foreground="gray", font=("Arial", 8)).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(main, text="产品名称:").pack(anchor=tk.W)
        self.product_name = ttk.Entry(main, width=60)
        self.product_name.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main, text="公司名称:").pack(anchor=tk.W)
        self.company_name = ttk.Entry(main, width=60)
        self.company_name.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main, text="文件版本:").pack(anchor=tk.W)
        self.file_version = ttk.Entry(main, width=60)
        self.file_version.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main, text="产品版本:").pack(anchor=tk.W)
        self.product_version = ttk.Entry(main, width=60)
        self.product_version.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📂导入", command=self.import_version_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="默认", command=self.reset_default).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.RIGHT, padx=5)
    
    def import_version_file(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择 version.txt",
            filetypes=[("Version files", "version.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.parse_version_file(file_path)
    
    # ✅ 修复：方法名改为 on_drop
    def on_drop(self, event):
        """弹窗拖拽文件解析"""
        try:
            paths = self.app._parse_drop_paths(event.data)
        except Exception:
            paths = self._manual_parse_paths(event.data)
        
        if not paths:
            return
        
        files = paths[0]
        
        if not os.path.isfile(files):
            return
        
        if not files.lower().endswith('.txt'):
            messagebox.showwarning("无效文件", "请拖拽 .txt 版本文件")
            return
        
        self.parse_version_file(files)
    
    def _manual_parse_paths(self, data):
        """手动解析拖拽路径（兜底）"""
        if not data:
            return []
        
        data = data.strip('{}')
        
        try:
            paths = self.tk.splitlist(data)
        except Exception:
            import re
            quoted = re.findall(r'"([^"]+)"', data)
            if quoted:
                paths = quoted
            else:
                paths = [data]
        
        valid_paths = []
        for p in paths:
            p = p.strip()
            if p.startswith('file://'):
                p = p[7:]
            if p and os.path.exists(p):
                valid_paths.append(p)
        
        return valid_paths
    
    def parse_version_file(self, file_path):
        """解析 version.txt 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            
            # 提取 ProductName（多种格式）
            patterns = [
                r"StringStruct\(u'ProductName', u'([^']+)'\)",
                r"StringStruct\('ProductName', '([^']+)'\)",
                r'"ProductName"[,\s]*"([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.product_name.delete(0, tk.END)
                    self.product_name.insert(0, match.group(1))
                    break
            
            # 提取 CompanyName
            patterns = [
                r"StringStruct\(u'CompanyName', u'([^']+)'\)",
                r"StringStruct\('CompanyName', '([^']+)'\)",
                r'"CompanyName"[,\s]*"([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.company_name.delete(0, tk.END)
                    self.company_name.insert(0, match.group(1))
                    break
            
            # 提取 FileVersion
            patterns = [
                r"StringStruct\(u'FileVersion', u'([^']+)'\)",
                r"StringStruct\('FileVersion', '([^']+)'\)",
                r'"FileVersion"[,\s]*"([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.file_version.delete(0, tk.END)
                    self.file_version.insert(0, match.group(1))
                    break
            
            # 提取 ProductVersion
            patterns = [
                r"StringStruct\(u'ProductVersion', u'([^']+)'\)",
                r"StringStruct\('ProductVersion', '([^']+)'\)",
                r'"ProductVersion"[,\s]*"([^"]+)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    self.product_version.delete(0, tk.END)
                    self.product_version.insert(0, match.group(1))
                    break
            
            self.app.safe_log(f"✅ 已从 {os.path.basename(file_path)} 导入版本信息")
            
        except Exception as e:
            messagebox.showerror("导入失败", f"解析失败: {e}")

    def load_data(self, data):
        """加载现有版本信息到界面"""
        self.product_name.delete(0, tk.END)
        self.product_name.insert(0, data.get("ProductName", ""))

        self.company_name.delete(0, tk.END)
        self.company_name.insert(0, data.get("CompanyName", ""))

        # 加载文件版本
        file_version = data.get("FileVersion", "1.0.0.0")
        self.file_version.delete(0, tk.END)
        self.file_version.insert(0, file_version)

        # 加载产品版本
        product_version = data.get("ProductVersion", "")
        if not product_version:
            now = datetime.datetime.now()
            time_str = now.strftime("%H%M").lstrip("0")
            if time_str == "":
                time_str = "0"
            product_version = f"{now.year}.{now.month}.{now.day}.{time_str}"

        self.product_version.delete(0, tk.END)
        self.product_version.insert(0, product_version)

    def _sync_version_product_name(self):
        """同步版本信息中的产品名称为当前输出名称"""
        if hasattr(self, 'version_info') and self.version_info:
            current_name = self.output_name.get() if self.output_name.get() else "我的应用程序"
            if self.version_info.get("ProductName") != current_name:
                self.version_info["ProductName"] = current_name
                self._save_version_config()
                self.safe_log(f"🔄 已同步产品名称: {current_name}")
    def reset_default(self):
        import datetime
        now = datetime.datetime.now()
        default_data = {
            "ProductName": self.app.output_name.get() if self.app.output_name.get() else "我的应用程序",
            "CompanyName": "PyPackTool",
            "FileVersion": "1.0.0.0",
            "ProductVersion": f"{now.year}.{now.month}.{now.day}.{now.hour}{now.minute}"
        }
        self.load_data(default_data)

    def confirm(self):
        product_name = self.product_name.get().strip()
        company_name = self.company_name.get().strip()
        file_version = self.file_version.get().strip()
        product_version = self.product_version.get().strip()

        if not file_version:
            file_version = "1.0.0.0"

        if not product_version:
            now = datetime.datetime.now()
            time_str = now.strftime("%H%M").lstrip("0")
            if time_str == "":
                time_str = "0"
            product_version = f"{now.year}.{now.month}.{now.day}.{time_str}"

        self.result = {
            "ProductName": product_name if product_name else "我的应用程序",
            "CompanyName": company_name if company_name else "PyPackTool",
            "FileVersion": file_version,
            "ProductVersion": product_version
        }

        if hasattr(self, 'app'):
            self.app._version_info_ready = True
            self.app.version_info = self.result.copy()
            self.app._save_version_config()
            self.app.safe_log(f"✅ 版本信息已保存: 文件版本={file_version}, 产品版本={product_version}")

        self.destroy()
    
    def get_result(self):
        return self.result

class GlobalConfig:
    """全局配置管理（独立于项目）"""
    
    @staticmethod
    def get_config_dir():
        return ExePathManager.get_exe_directory()
    
    @staticmethod
    def save_upx_path(path):
        cfg = os.path.join(GlobalConfig.get_config_dir(), "upx_config.json")
        try:
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"upx_path": path, "use_upx": True}, f)
        except:
            pass
    
    @staticmethod
    def load_upx_path():
        cfg = os.path.join(GlobalConfig.get_config_dir(), "upx_config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("upx_path", ""), data.get("use_upx", True)
            except:
                pass
        return "", True
    
    @staticmethod
    def save_python_path(path):
        cfg = os.path.join(GlobalConfig.get_config_dir(), "python_config.json")
        try:
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"python_path": path}, f)
        except:
            pass
    
    @staticmethod
    def load_python_path():
        cfg = os.path.join(GlobalConfig.get_config_dir(), "python_config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("python_path", "")
            except:
                pass
        return ""

# ==================== UI 组件====================
class ModernButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.normal_bg = kw.pop("normal_bg", "#e8ecf1")
        self.hover_bg = kw.pop("hover_bg", "#4a8dd9")
        self.press_bg = kw.pop("press_bg", "#3a7dc9")
        self.normal_fg = kw.pop("normal_fg", "#333333")
        self.hover_fg = kw.pop("hover_fg", "#ffffff")
        super().__init__(master, **kw)
        self.configure(bg=self.normal_bg, fg=self.normal_fg, font=("微软雅黑", 10),
                      relief="flat", bd=1, padx=12, pady=5, cursor="hand2")
        self.bind("<Enter>", lambda e: self.configure(bg=self.hover_bg, fg=self.hover_fg))
        self.bind("<Leave>", lambda e: self.configure(bg=self.normal_bg, fg=self.normal_fg))
        self.bind("<ButtonPress-1>", lambda e: self.configure(bg=self.press_bg))
        self.bind("<ButtonRelease-1>", lambda e: self.configure(bg=self.hover_bg))

class ToggleSwitch(tk.Canvas):
    def __init__(self, master=None, width=26, height=18, on=False, command=None):
        self._on = on
        self._cmd = command
        
        try:
            bg = master.cget("bg")
        except tk.TclError:
            bg = "#f0f2f5"
        super().__init__(master, width=width, height=height, highlightthickness=0, bg=bg)
        self._r = height // 2
        self.bind("<Button-1>", lambda e: self.toggle())
        self.draw()

    def toggle(self):
        self._on = not self._on
        self.draw()
        if self._cmd: self._cmd(self._on)

    def draw(self):
        self.delete("all")
        color = "#4a8dd9" if self._on else "#c5d0dd"
        h = self._r * 2
        w = self.winfo_reqwidth()
        self.create_oval(0, 0, h, h, fill=color, outline="")
        self.create_oval(w-h, 0, w, h, fill=color, outline="")
        self.create_rectangle(h//2, 0, w-h//2, h, fill=color, outline="")
        x = w - h + 2 if self._on else 2
        self.create_oval(x, 2, x+h-4, h-2, fill="#ffffff", outline="")

    def is_on(self): return self._on
    def set(self, v):
        if self._on != v:
            self._on = v
            self.draw()
            if self._cmd: self._cmd(v)

class ToggleSwitchWithLabel(tk.Frame):
    def __init__(self, master=None, text="", on=False, command=None, **kw):
        super().__init__(master, **kw)
      
        try:
            bg = master.cget("bg")
        except tk.TclError:
            bg = "#f0f2f5"
        self.configure(bg=bg)
        tk.Label(self, text=text, font=("微软雅黑", 9), bg=bg).pack(side=tk.LEFT)
        self.switch = ToggleSwitch(self, on=on, command=command)
        self.switch.pack(side=tk.LEFT)

    def get(self): return self.switch.is_on()
    def set(self, v): self.switch.set(v)

# ==================== 图标制作弹窗 ====================
class IconMakerDialog(tk.Toplevel):
    SHAPES = {"圆角": 0.18, "方形": 0, "圆形": -1, "心形": -2}

    def __init__(self, parent, app, callback):
        super().__init__(parent)
        self.app = app
        self.callback = callback
        self.title("图标制作")
        self.geometry("450x300")
        self.img_path = None
        self.pil_img = None
        self.zoom = 1.0
        self.setup_ui()
        self.transient(parent)
        #self.grab_set()

    def setup_ui(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)
        self.preview = tk.Label(main, text="暂无图片", bg="white", relief="sunken", anchor="center")
        self.preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ctrl = ttk.Frame(main)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        ModernButton(ctrl, text="打开图片", command=self.load_image).pack(fill=tk.X, pady=5)
        ttk.Label(ctrl, text="形状:").pack(anchor=tk.W)
        self.shape_var = tk.StringVar(value="圆角")
        ttk.Combobox(ctrl, textvariable=self.shape_var, values=list(self.SHAPES.keys()),
                    state="readonly").pack(fill=tk.X, pady=5)
        ttk.Label(ctrl, text="缩放 (%):").pack(anchor=tk.W)
        self.scale_var = tk.IntVar(value=100)
        ttk.Scale(ctrl, from_=50, to=200, variable=self.scale_var, orient=tk.HORIZONTAL,
                 command=lambda v: self.refresh()).pack(fill=tk.X, pady=5)
        ModernButton(ctrl, text="生成并保存", command=self.save).pack(fill=tk.X, pady=20)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
        if path:
            self.img_path = path
            self.refresh()

    def refresh(self):
        if not self.img_path or not Image: return
        try:
            img = Image.open(self.img_path).convert("RGBA")
            self.zoom = self.scale_var.get() / 100.0
            size = 256
            w, h = img.size
            if w != h:
                s = min(w, h)
                img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            if self.zoom != 1.0:
                ns = int(size * self.zoom)
                img = img.resize((ns, ns), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (size, size), (0,0,0,0))
                canvas.paste(img, ((size-ns)//2, (size-ns)//2))
                img = canvas
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            shape = self.shape_var.get()
            if shape == "圆形":
                draw.ellipse((0, 0, size, size), fill=255)
            elif shape == "心形":
                pts = [(size/2, size*0.85), (size*0.15, size*0.35), (size*0.3, size*0.1),
                       (size/2, size*0.3), (size*0.7, size*0.1), (size*0.85, size*0.35)]
                draw.polygon(pts, fill=255)
            elif shape == "圆角":
                draw.rounded_rectangle((0, 0, size, size), radius=int(size*0.18), fill=255)
            else:
                draw.rectangle((0, 0, size, size), fill=255)
            self.pil_img = Image.composite(img, Image.new("RGBA", (size, size), (0,0,0,0)), mask)
            preview = self.pil_img.copy()
            preview.thumbnail((180, 180), Image.Resampling.LANCZOS)
            pw, ph = preview.size
            white = Image.new("RGB", (200, 200), (255, 255, 255))
            if preview.mode == "RGBA":
                white.paste(preview, ((200-pw)//2, (200-ph)//2), preview.split()[3])
            else:
                white.paste(preview, ((200-pw)//2, (200-ph)//2))
            buf = io.BytesIO()
            white.save(buf, format="PNG")
            photo = tk.PhotoImage(data=buf.getvalue())
            self.preview.config(image=photo, text="")
            self.preview.image = photo
        except Exception as e:
            self.app.safe_log(f"预览出错: {e}")

    def save(self):
        if not self.pil_img:
            messagebox.showwarning("提示", "请先打开图片")
            return
        name = self.app.output_name.get().replace(" ", "_")
        path = filedialog.asksaveasfilename(defaultextension=".ico", initialdir=self.app.current_dir,
                                             initialfile=f"{name}.ico", filetypes=[("Icons", "*.ico")])
        if path:
            self.pil_img.save(path, format="ICO", sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])
            self.callback(path)
            self.destroy()

# ==================== 智能排除弹窗 ====================
class ExcludeSelectorDialog(tk.Toplevel):
    CATEGORIES = {
        "🔴 GUI框架": ["PyQt5", "PyQt6", "PySide2", "PySide6", "wxPython", "Kivy"],
        "🟠 科学计算": ["numpy", "pandas", "scipy", "matplotlib", "sympy"],
        "🟡 深度学习": ["tensorflow", "torch", "torchvision", "keras"],
        "🟢 图像/视频": ["PIL", "pillow", "opencv-python", "cv2", "pygame"],
        "🔵 Web框架": ["django", "flask", "fastapi", "tornado"],
        "🟣 网络/爬虫": ["requests", "selenium", "beautifulsoup4", "scrapy"],
        "⚪ 数据库": ["pymysql", "psycopg2", "sqlalchemy", "pymongo"],
        "🟤 测试工具": ["pytest", "nose", "coverage", "tox"],
        "📦 文档处理": ["openpyxl", "xlrd", "python-docx", "pdfplumber", "reportlab"],
        "🔧 其他": ["pycryptodome", "jwt", "pydub", "moviepy", "eyed3", "mutagen", "tabulate"],
    }

    def __init__(self, parent, used, installed, current, callback):
        super().__init__(parent)
        self.callback = callback
        self.used = set(used)
        self.installed = set(installed)
        self.current = set(current)
        self.title("智能排除")
        self.geometry("650x550")
        self.setup_ui()
        self.transient(parent)
        self.grab_set()

    def setup_ui(self):
        main = ttk.Frame(self, padding=8)
        main.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text="🎯 智能排除 - 排除未使用的模块来减小体积", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(main, text="✅ 绿色=未使用(可排除)  ⚠️ 橙色=已使用(排除会出错)", foreground="blue", font=("Arial", 8)).pack(anchor=tk.W, pady=2)
        quick = ttk.Frame(main)
        quick.pack(fill=tk.X, pady=3)
        ModernButton(quick, text="⚡ 安全排除", command=self.select_safe).pack(side=tk.LEFT, padx=2)
        ModernButton(quick, text="🔍 分析显示", command=self.analyze_show).pack(side=tk.LEFT, padx=2)
        search = ttk.Frame(main)
        search.pack(fill=tk.X, pady=3)
        ttk.Label(search, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.filter())
        ttk.Entry(search, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        list_frame = ttk.Frame(main)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=3)
        sb = ttk.Scrollbar(list_frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        sbx = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        sbx.pack(side=tk.BOTTOM, fill=tk.X)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, font=("Consolas", 9),
                                 yscrollcommand=sb.set, xscrollcommand=sbx.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self.listbox.yview)
        sbx.config(command=self.listbox.xview)
        self.all_items = []
        for cat, mods in self.CATEGORIES.items():
            self.all_items.append(f"── {cat} ──")
            self.all_items.extend(mods)
        btn = ttk.Frame(main)
        btn.pack(fill=tk.X, pady=5)
        for text, cmd, side in [("全选", self.select_all, tk.LEFT), ("全不选", self.select_none, tk.LEFT),
                                ("反选", self.invert, tk.LEFT), ("取消", self.destroy, tk.RIGHT),
                                ("确定", self.confirm, tk.RIGHT)]:
            ModernButton(btn, text=text, command=cmd, width=6).pack(side=side, padx=2)
        self.status = ttk.Frame(main)
        self.status.pack(fill=tk.X, pady=5)
        self.sel_label = ttk.Label(self.status, text="已选择: 0", foreground="green")
        self.sel_label.pack(side=tk.LEFT)
        self.safe_label = ttk.Label(self.status, text="", foreground="green")
        self.safe_label.pack(side=tk.LEFT, padx=10)
        self.filter()
        self.listbox.bind("<<ListboxSelect>>", lambda e: self.update_count())

    def filter(self):
        s = self.search_var.get().lower()
        self.filtered = [i for i in self.all_items if not s or s in i.lower()]
        self.listbox.delete(0, tk.END)
        for item in self.filtered:
            self.listbox.insert(tk.END, item)
            idx = tk.END
            if item.startswith("──"):
                self.listbox.itemconfig(idx, foreground="blue")
            elif item in self.used:
                self.listbox.itemconfig(idx, foreground="orange", bg="#FFF8E7")
            else:
                self.listbox.itemconfig(idx, foreground="green", bg="#E8F5E9")
        self.preselect()

    def preselect(self):
        for i, item in enumerate(self.filtered):
            if item in self.current and not item.startswith("──"):
                self.listbox.selection_set(i)
        self.update_count()

    def select_safe(self):
        self.select_none()
        n = 0
        for i, item in enumerate(self.filtered):
            if not item.startswith("──") and item not in self.used:
                self.listbox.selection_set(i)
                n += 1
        self.update_count()
        self.safe_label.config(text=f"✅ 已选中 {n} 个可安全排除", foreground="green")

    def analyze_show(self):
        self.select_safe()
        if not any(not i.startswith("──") and i not in self.used for i in self.filtered):
            messagebox.showinfo("分析结果", "未发现可安全排除的模块！")

    def update_count(self):
        sel = [self.filtered[i] for i in self.listbox.curselection() if not self.filtered[i].startswith("──")]
        self.sel_label.config(text=f"已选择: {len(sel)}")
        used_sel = [m for m in sel if m in self.used]
        self.safe_label.config(text=f"⚠️ {len(used_sel)} 个模块被代码使用！" if used_sel else "✅ 所有选中模块可安全排除",
                              foreground="red" if used_sel else "green")

    def select_all(self):
        for i, item in enumerate(self.filtered):
            if not item.startswith("──"):
                self.listbox.selection_set(i)
        self.update_count()

    def select_none(self):
        self.listbox.selection_clear(0, tk.END)
        self.update_count()

    def invert(self):
        for i, item in enumerate(self.filtered):
            if not item.startswith("──"):
                if i in self.listbox.curselection():
                    self.listbox.selection_clear(i)
                else:
                    self.listbox.selection_set(i)
        self.update_count()

    def confirm(self):
        sel = {self.filtered[i] for i in self.listbox.curselection() if not self.filtered[i].startswith("──")}
        used = [m for m in sel if m in self.used]
        if used and not messagebox.askyesno("确认排除",
            f"⚠️ 以下 {len(used)} 个模块被代码使用，排除后可能出错！\n\n{', '.join(used[:10])}\n\n是否仍然排除？",
            icon="warning"):
            return
        self.callback(sel)
        self.destroy()

# ==================== 主程序 ====================
class PackageGUI:
    # ========== 工具配置（跨平台可执行文件查找）==========
    TOOL_CONFIG = {
        'python': {
            'names': ['python', 'python3', 'python.exe'],
            'common_paths': [
                r"C:\Python312\python.exe",
                r"C:\Python311\python.exe",
                r"C:\Python310\python.exe",
                r"D:\Python312\python.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"),
                "/usr/bin/python3",
                "/usr/local/bin/python3",
                "/usr/bin/python",
            ]
        },
        'upx': {
            'names': ['upx', 'upx.exe'],
            'common_paths': [
                r"C:\upx\upx.exe",
                r"C:\Program Files\upx\upx.exe",
                os.path.expanduser(r"~\upx\upx.exe"),
                "/usr/bin/upx",
                "/usr/local/bin/upx",
                "/opt/homebrew/bin/upx",
            ]
        },
        'makensis': {
            'names': ['makensis', 'makensis.exe'],
            'common_paths': [
                r"C:\Program Files (x86)\NSIS\makensis.exe",
                r"C:\Program Files\NSIS\makensis.exe",
                os.path.expanduser(r"~\NSIS\makensis.exe"),
            ]
        },
        'gcc': {
            'names': ['gcc', 'gcc.exe'],
            'common_paths': [
                r"C:\MinGW\bin\gcc.exe",
                r"C:\msys64\mingw64\bin\gcc.exe",
                "/usr/bin/gcc",
                "/usr/local/bin/gcc",
            ]
        },
        'cl': {
            'names': ['cl', 'cl.exe'],
            'common_paths': [
                r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
                r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe",
                "/usr/bin/cl",
                "/usr/local/bin/cl",
            ]
        },
    }


    def __init__(self):
        os.environ["PYTHONIOENCODING"] = "utf-8"
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.kernel32.SetConsoleCP(65001)
                ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            except: pass
        # 日期（自动获取)
        BUILD_DATE = "2026-05-20"
        self.BUILD_DATE = BUILD_DATE  # 保存到实例变量
        self.root = TkinterDnD.Tk() if DND_AVAILABLE else tk.Tk()
        self.root.title(f"Python代码打包工具 - 跨平台支持 {BUILD_DATE}")

        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        ww, wh = min(int(sw * 0.7), 950), min(int(sh * 0.65), 650)
        self.root.geometry(f"{ww}x{wh}+{(sw - ww) // 2}+{(sh - wh) // 2}")
        self.root.minsize(950, 650)

        default_icon = ExePathManager.get_resource_path("tool.ico")
        if os.path.exists(default_icon):
           try:
               self.root.iconbitmap(default_icon)
               # 如果 icon_path 为空，可以设置为默认值（可选）
               if not self.icon_path.get():
                  self.icon_path.set(default_icon)
           except Exception as e:
               pass

        # 立即刷新窗口
        self.root.update()

        # ========== 第2步：初始化基础变量 ==========
        self.current_dir = ExePathManager.get_exe_directory()
        self.safe_log(f"当前 exe 目录: {self.current_dir}")
        self.dist_dir = os.path.join(self.current_dir, "dist")
        os.makedirs(self.dist_dir, exist_ok=True)
   
        # 初始化变量
        self.hidden_imports_list = []
        self.data_files_list = []
        self.exclude_list = []
        self.analyzed_modules = []
        self.installed_packages = None
        self.process = None
        self.start_time = None
        self.use_venv = False
        self._upx_auto_find_done = False

        self.venv_process = None      # 虚拟环境创建进程
        self.stop_venv = False        # 虚拟环境停止标志
        # 编译器属性默认值
        self.has_msvc = False
        self.has_mingw = False
        self.mingw_path = None
        self.msvc_path = None
        # StringVar 初始化
        self.packer_type = tk.StringVar(value="PyInstaller")
        self.package_type = tk.StringVar(value="onefile")
        self.nuitka_jobs = tk.StringVar(value="auto")
        self.nuitka_backend = tk.StringVar(value="auto")
        self.target_platform = tk.StringVar(value="current")
        self.custom_python_path = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.upx_path = tk.StringVar()
        self.use_upx = tk.BooleanVar(value=True)
        self.debug_mode = tk.BooleanVar(value=False)
        self.version_info = None
        self._version_info_ready = False
        self._python_list_cache = []
        self._python_list_time = 0

        try:
            import multiprocessing
            self.cpu_count = multiprocessing.cpu_count()
        except:
            self.cpu_count = 4
        self.job_options = ["auto"] + [str(j) for j in [1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64] if j <= self.cpu_count]

        # ========== 第3步：构建UI（同步，但只构建框架） ==========
        self._build_ui()
        self.theme_manager = ThemeManager(self)
        self.theme_manager.apply()

        # 显示启动提示
        self.safe_log("🚀 程序启动中...")

        # ========== 第4步：异步加载所有耗时操作 ==========
        self.root.after(50, self._async_init)

        # 异步加载默认项目（如果有）
        default_input = self._find_default_py()
        if default_input:
            self.input_path.set(default_input)
            self.output_name.set(self._get_default_name())
            threading.Thread(target=self._async_load_config, daemon=True).start()
            threading.Thread(target=self._async_analyze_used, daemon=True).start()
        #注入目录与多开
        self._workdir_injected = False
        self._multi_injected = False
        self.workdir_enabled = False  # 默认开启
        self._temp_version_file = None  # 记录临时版本文件路径
        self.global_cache_file = os.path.join(self.current_dir, "global_cache.json") #全局缓存
        self.global_cache = self._load_global_cache()

        # 音乐播放器
        self.music_visible = False
        self.music_files = []
        self.current_music_index = 0
        self.music_process = None


    def _async_init(self):
        """异步初始化所有耗时操作"""
        # 1. 加载全局UPX配置
        if not self._load_upx_config():
            threading.Thread(target=self._async_find_upx, daemon=True).start()

        # 2. 加载Python配置（从缓存加载保存的路径）
        self._load_python_config()

        # 3. 获取当前Python路径状态
        current_python = self.custom_python_path.get()
        has_valid_python = current_python and os.path.exists(current_python)

        # 4. 根据环境处理Python路径
        if getattr(sys, 'frozen', False):
            # 打包环境：只使用已保存的路径，不自动检测
            if has_valid_python:
                self.safe_log(f"📁 使用已保存的Python路径: {current_python}")
                self._test_python()
            else:
                self.safe_log("💡 打包环境下请手动指定Python路径（点击浏览选择 python.exe）")
        else:
            # 开发环境：可以自动检测
            if has_valid_python:
                self.safe_log(f"📁 使用已保存的Python路径: {current_python}")
                self._test_python()
            else:
                self.safe_log("🔍 首次运行，正在自动检测系统Python...")
                threading.Thread(target=self._async_find_python, daemon=True).start()
        self._refresh_python_list()
        # 5. 检测编译器（耗时）
        threading.Thread(target=self._detect_compilers_async, daemon=True).start()

        # 6. 预加载打包器版本
        threading.Thread(target=self._preload_all_packers_version, daemon=True).start()

        # 7. 查找默认Python文件并加载项目配置（仅开发环境）
        if not getattr(sys, 'frozen', False):
            default_input = self._find_default_py()
            if default_input:
                self.input_path.set(default_input)
                self.output_name.set(self._get_default_name())
                # 异步加载配置，不阻塞
                threading.Thread(target=self._async_load_config, daemon=True).start()
                threading.Thread(target=self._async_analyze_used, daemon=True).start()

        self._on_packer_changed()
        self.safe_log("✅ 配置加载完成")
        
    def _detect_compilers_async(self):
        """后台检测编译器"""
        try:
            self.has_msvc = self._detect_msvc()
            self.has_mingw, self.mingw_path = self._detect_mingw()
        except Exception as e:
            self.safe_log(f"⚠️ 编译器检测失败: {e}")
        finally:
            # 更新UI（回到主线程）
            self.root.after(0, self._update_compiler_status)

    def _async_analyze_used(self):
        """后台分析使用的模块（启动时调用）"""
        self._analyze_used(show_log=True, auto_add=True)
        #result = self._analyze_used()
        #self.root.after(0, lambda: self.safe_log(f"📊 分析完成，发现 {len(result)} 个第三方模块"))

    def _load_global_cache(self):
        """加载全局缓存"""
        if os.path.exists(self.global_cache_file):
            try:
                with open(self.global_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_global_cache(self):
        """保存全局缓存"""
        try:
            with open(self.global_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_cache, f, ensure_ascii=False, indent=2)
        except:
            pass


    def _async_find_upx(self):
        """后台线程查找UPX"""
        if self._upx_auto_find_done:
            return

        upx_dir = self._find_upx_path()
        if upx_dir and not self.upx_path.get():
            upx_name = "upx.exe" if sys.platform == "win32" else "upx"
            upx_full = os.path.join(upx_dir, upx_name)
            self.root.after(0, lambda: self._set_upx_path(upx_full))

    def _set_upx_path(self, path):
        """安全设置UPX路径（主线程）"""
        if not self.upx_path.get():
            self.upx_path.set(path)
            self._save_upx_config()
            #self.safe_log(f"✅ 自动检测到UPX: {path}")
            if hasattr(self, 'upx_entry'):
                self.upx_entry.delete(0, tk.END)
                self.upx_entry.insert(0, path)

    def _find_system_python_by_cmd(self):
        """使用系统命令查找 Python"""

        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["where", "python.exe"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    startupinfo=get_startupinfo()
                )
                if result.returncode == 0:
                    paths = result.stdout.strip().split('\n')
                    for path in paths:
                        if path and os.path.exists(path):
                            if ExePathManager.is_temp_directory(path):
                                continue
                            if ExePathManager.is_frozen():
                                if os.path.abspath(path).lower() == os.path.abspath(sys.executable).lower():
                                    continue
                            return path
            except:
                pass
        else:
            try:
                result = subprocess.run(["which", "python3"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if path and os.path.exists(path):
                        return path
            except:
                pass
            try:
                result = subprocess.run(["which", "python"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    path = result.stdout.strip()
                    if path and os.path.exists(path):
                        return path
            except:
                pass

        return None

    def _async_find_python(self):
        """后台线程查找Python"""

        python_path = self._auto_detect_python()

        # 只在没有设置过Python路径时才自动设置
        if python_path and not self.custom_python_path.get():
            # 再次确认路径有效且不是程序自身（打包环境）
            if getattr(sys, 'frozen', False):
                if python_path.lower().endswith('python.exe') and 'common_venv' not in python_path.lower():
                    self.root.after(0, lambda: self._set_python_path(python_path))
            else:
                # 开发环境直接设置
                self.root.after(0, lambda: self._set_python_path(python_path))

    def _set_python_path(self, path):
        """安全设置Python路径（主线程）"""

        if not path or not os.path.exists(path):
            return

        if not path.lower().endswith('python.exe'):
            return

        # 使用 ExePathManager 判断打包环境
        if ExePathManager.is_frozen():
            if os.path.abspath(path).lower() == os.path.abspath(sys.executable).lower():
                self.safe_log("⚠️ 不能将程序自身设置为Python路径")
                return
            if ExePathManager.is_temp_directory(path):
                self.safe_log("⚠️ 路径在临时目录，无效")
                return

        path = path.replace('.EXE', '.exe').replace('.Exe', '.exe')
        self.custom_python_path.set(path)
        if not self.custom_python_path.get():
            self.custom_python_path.set(path)
            self._save_python_config()
            self.safe_log(f"✅ 自动检测到Python: {path}")
            self._test_python()
            if hasattr(self, 'python_path_entry'):
                self.python_path_entry.delete(0, tk.END)
                self.python_path_entry.insert(0, path)
        self._update_python_ui_state()

    # ========== 通用可执行文件查找方法 ==========
    def _find_executable(self, names, common_paths=None):
        """
        底层查找函数（支持路径空格）
        :param names: 可执行文件名列表
        :param common_paths: 额外完整路径列表
        :return: 完整路径或 None
        """
        import shutil
        # 1. shutil.which（最可靠）
        for name in names:
            try:
                path = shutil.which(name)
                if path and os.path.exists(path):
                    return path
            except:
                pass
        # 2. 手动遍历 PATH
        path_env = os.environ.get("PATH", "")
        for d in path_env.split(os.pathsep):
            for name in names:
                full = os.path.join(d, name)
                if os.path.exists(full):
                    return full
        # 3. 常见路径
        if common_paths:
            for p in common_paths:
                if os.path.exists(p):
                    return p
        return None

    def _find_tool(self, tool_name, use_cache=True):
        """
        通用工具路径查找（支持缓存）
        :param tool_name: 工具名，需在 TOOL_CONFIG 中定义
        :param use_cache: 是否使用缓存
        :return: 工具完整路径，未找到返回 None
        """
        cache_attr = f'_{tool_name}_path_cache'
        if use_cache and hasattr(self, cache_attr):
            return getattr(self, cache_attr)

        config = self.TOOL_CONFIG.get(tool_name)
        if not config:
            self.safe_log(f"⚠️ 未配置工具: {tool_name}")
            return None

        path = self._find_executable(config['names'], config.get('common_paths'))
        if use_cache:
            setattr(self, cache_attr, path)
        return path

    def _get_version_info(self):
        """获取完整的版本信息（优先级：弹窗设置 > version.txt > 默认值）"""
        # 1. 优先使用弹窗设置的版本信息
        if hasattr(self, 'version_info') and self.version_info and getattr(self, '_version_info_ready', False):
            product_name = self.version_info.get("ProductName", "")
            company_name = self.version_info.get("CompanyName", "")
            file_version = self.version_info.get("FileVersion", "")
            product_version = self.version_info.get("ProductVersion", "")

            if not product_name:
                product_name = self.output_name.get() if self.output_name.get() else "我的应用程序"
            if not company_name:
                company_name = "PyPackTool"
            if not file_version:
                file_version = "1.0.0.0"
            if not product_version:
                product_version = self._get_default_version()

            return {
                "ProductName": self._format_version_string(product_name),
                "CompanyName": self._format_version_string(company_name),
                "FileVersion": self._normalize_version(file_version),
                "ProductVersion": self._format_version_string(product_version),
                "Copyright": f"Copyright (c) {datetime.datetime.now().year} {company_name}",
                "InternalName": product_name.replace(" ", ""),
                "OriginalFilename": f"{product_name.replace(' ', '')}.exe"
            }

        # 2. 尝试从 version.txt 读取
        version_file = os.path.join(self.current_dir, "version.txt")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                version_info = {}
                # 解析各个字段...
                if version_info:
                    return version_info
            except:
                pass

        # 3. 使用默认值
        default_product = self.output_name.get() if self.output_name.get() else "我的应用程序"
        return {
            "ProductName": default_product,
            "CompanyName": "PyPackTool",
            "FileVersion": "1.0.0.0",
            "ProductVersion": self._get_default_version(),
            "Copyright": f"Copyright (c) {datetime.datetime.now().year} PyPackTool",
            "InternalName": default_product.replace(" ", ""),
            "OriginalFilename": f"{default_product.replace(' ', '')}.exe"
        }

    def _get_default_version(self):
        """获取默认版本号（基于当前时间）"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H%M").lstrip("0")
        if time_str == "":
            time_str = "0"
        return f"{now.year}.{now.month}.{now.day}.{time_str}"

    def _normalize_version(self, version_str, default="1.0.0.0"):
        """规范化版本号格式为 x.x.x.x"""
        if not version_str:
            return default
        import re
        parts = re.findall(r'\d+', str(version_str))
        clean_parts = []
        for part in parts[:4]:
            try:
                clean_parts.append(str(int(part)))
            except:
                clean_parts.append("0")
        while len(clean_parts) < 4:
            clean_parts.append("0")
        return ".".join(clean_parts)

    def _apply_version_to_pyinstaller(self, cmd):
        """为 PyInstaller 应用版本信息"""
        version_info = self._get_version_info()
        version_file = self._create_version_file_from_info(version_info)
        if version_file and os.path.exists(version_file):
            cmd.append(f"--version-file={version_file}")
            self.safe_log(f"📄 版本信息已应用:")
            self.safe_log(f"   产品名称: {version_info['ProductName']}")
            self.safe_log(f"   公司名称: {version_info['CompanyName']}")
            self.safe_log(f"   文件版本: {version_info['FileVersion']}")
            self.safe_log(f"   产品版本: {version_info['ProductVersion']}")
            return version_file
        return None

    def _apply_version_to_nuitka(self, cmd):
        """为 Nuitka 应用版本信息"""
        version_info = self._get_version_info()
        cmd.extend([
            f"--product-name={version_info['ProductName']}",
            f"--product-version={version_info['ProductVersion']}",
            f"--file-version={version_info['FileVersion']}",
            f"--company-name={version_info['CompanyName']}",
            f"--file-description={version_info['ProductName']}",
            f"--copyright={version_info['Copyright']}"
        ])
        self.safe_log(f"📄 版本信息已应用:")
        self.safe_log(f"   产品名称: {version_info['ProductName']}")
        self.safe_log(f"   公司名称: {version_info['CompanyName']}")
        self.safe_log(f"   文件版本: {version_info['FileVersion']}")
        self.safe_log(f"   产品版本: {version_info['ProductVersion']}")

    def _create_version_file_from_info(self, version_info):
        """根据版本信息字典创建 version.txt 文件"""
        version_file = os.path.join(self.current_dir, f"_temp_version_{int(time.time())}.txt")
        now = datetime.datetime.now()

        # 解析版本号
        file_vers = version_info['FileVersion'].split('.')
        file_vers_padded = []
        for i in range(4):
            if i < len(file_vers):
                try:
                    file_vers_padded.append(int(file_vers[i]))
                except:
                    file_vers_padded.append(0)
            else:
                file_vers_padded.append(0)

        prod_vers = version_info['ProductVersion'].split('.')
        prod_vers_padded = []
        for i in range(4):
            if i < len(prod_vers):
                try:
                    prod_vers_padded.append(int(prod_vers[i]))
                except:
                    prod_vers_padded.append(0)
            else:
                prod_vers_padded.append(0)

        lines = [
            "VSVersionInfo(",
            "  ffi=FixedFileInfo(",
            f"    filevers=({','.join(str(v) for v in file_vers_padded)}),",
            f"    prodvers=({','.join(str(v) for v in prod_vers_padded)}),",
            "    mask=0x3f,",
            "    flags=0x0,",
            "    OS=0x40004,",
            "    fileType=0x1,",
            "    subtype=0x0,",
            "    date=(0, 0)",
            "  ),",
            "  kids=[",
            "    StringFileInfo(",
            "      [",
            "        StringTable(",
            "          u'040904B0',",
            "          [",
            f"            StringStruct(u'CompanyName', u'{version_info['CompanyName']}'),",
            f"            StringStruct(u'FileDescription', u'{version_info['ProductName']}'),",
            f"            StringStruct(u'FileVersion', u'{version_info['FileVersion']}'),",
            f"            StringStruct(u'InternalName', u'{version_info['InternalName']}'),",
            f"            StringStruct(u'LegalCopyright', u'{version_info['Copyright']}'),",
            f"            StringStruct(u'OriginalFilename', u'{version_info['OriginalFilename']}'),",
            f"            StringStruct(u'ProductName', u'{version_info['ProductName']}'),",
            f"            StringStruct(u'ProductVersion', u'{version_info['ProductVersion']}')",
            "          ]",
            "        )",
            "      ]",
            "    ),",
            "    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])",
            "  ]",
            ")",
            "",
        ]

        content = "\n".join(lines)
        try:
            with open(version_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            return version_file
        except Exception as e:
            self.safe_log(f"⚠️ 创建版本文件失败: {e}")
            return None

    def _open_version_dialog(self):
        """打开版本信息设置弹窗"""
        now = datetime.datetime.now()
        current_product_name = self.output_name.get() if self.output_name.get() else "我的应用程序"

        # 获取当前版本信息
        if hasattr(self, 'version_info') and self.version_info and self._version_info_ready:
            # 已有保存的版本信息，但需要更新产品名称为当前文件名
            current_data = self.version_info.copy()
            # 同步产品名称为当前的输出名称
            current_data["ProductName"] = current_product_name
            self.safe_log(f"📦 使用已有版本配置，同步产品名称: {current_product_name}")
        else:
            # 尝试从配置文件加载
            if self._load_version_config():
                current_data = self.version_info.copy()
                # 同步产品名称为当前的输出名称
                current_data["ProductName"] = current_product_name
                self.safe_log(f"📦 从配置文件加载版本信息，同步产品名称: {current_product_name}")
            else:
                # 使用默认值
                time_str = now.strftime("%H%M").lstrip("0")
                if time_str == "":
                    time_str = "0"
                current_data = {
                    "ProductName": current_product_name,
                    "CompanyName": "PyPackTool",
                    "FileVersion": "1.0.0.0",
                    "ProductVersion": f"{now.year}.{now.month}.{now.day}.{time_str}"
                }
                self.safe_log(f"📦 使用默认版本信息，产品名称: {current_product_name}")

        dialog = VersionInfoDialog(self.root, self, current_data)
        self.root.wait_window(dialog)

        if hasattr(dialog, 'result') and dialog.result:
            self.version_info = dialog.result
            self._version_info_ready = True
            self.safe_log(f"✅ 版本信息已更新:")
            self.safe_log(f"   产品名称: {self.version_info.get('ProductName', '')}")
            self.safe_log(f"   公司名称: {self.version_info.get('CompanyName', '')}")
            self.safe_log(f"   文件版本: {self.version_info.get('FileVersion', '')}")
            self.safe_log(f"   产品版本: {self.version_info.get('ProductVersion', '')}")
            self._save_version_to_file()
            self._save_version_config()

    def _save_version_config(self):
        """保存版本信息配置"""
        if hasattr(self, 'version_info') and self.version_info:
            cfg = os.path.join(self.current_dir, "version_config.json")
            try:
                with open(cfg, "w", encoding="utf-8") as f:
                    json.dump(self.version_info, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.safe_log(f"⚠️ 保存版本配置失败: {e}")

    def _load_version_config(self):
        """加载版本信息配置"""
        cfg = os.path.join(self.current_dir, "version_config.json")
        if os.path.exists(cfg):
            try:
                with open(cfg, "r", encoding="utf-8") as f:
                    self.version_info = json.load(f)
                    return True
            except:
                pass
        return False

    def _format_version_string(self, template):
        """格式化版本字符串"""
        now = datetime.datetime.now()
        return template.format(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute
        )

    def _save_version_to_file(self):
        """将当前版本信息保存到 version.txt"""
        if not hasattr(self, 'version_info') or not self.version_info:
            return

        version_file = os.path.join(self.current_dir, "version.txt")
        now = datetime.datetime.now()

        product_name = self.version_info.get("ProductName", "我的应用程序")
        company_name = self.version_info.get("CompanyName", "PyPackTool")
        file_version = self.version_info.get("FileVersion", "1.0.0.0")
        product_version = self.version_info.get("ProductVersion",
                                                f"{now.year}.{now.month}.{now.day}.{now.hour}{now.minute}")

        # 格式化变量
        product_name = self._format_version_string(product_name)
        company_name = self._format_version_string(company_name)
        product_version = self._format_version_string(product_version)

        # 解析版本号
        version_parts = product_version.split('.')
        prod_vers = []
        for i in range(4):
            if i < len(version_parts):
                try:
                    prod_vers.append(int(version_parts[i]))
                except:
                    prod_vers.append(0)
            else:
                prod_vers.append(0)

        file_vers = file_version.split('.')
        file_vers_padded = []
        for i in range(4):
            if i < len(file_vers):
                try:
                    file_vers_padded.append(int(file_vers[i]))
                except:
                    file_vers_padded.append(0)
            else:
                file_vers_padded.append(0)

        lines = [
            "VSVersionInfo(",
            "  ffi=FixedFileInfo(",
            f"    filevers=({','.join(str(v) for v in file_vers_padded)}),",
            f"    prodvers=({','.join(str(v) for v in prod_vers)}),",
            "    mask=0x3f,",
            "    flags=0x0,",
            "    OS=0x40004,",
            "    fileType=0x1,",
            "    subtype=0x0,",
            "    date=(0, 0)",
            "  ),",
            "  kids=[",
            "    StringFileInfo(",
            "      [",
            "        StringTable(",
            "          u'040904B0',",
            "          [",
            f"            StringStruct(u'CompanyName', u'{company_name}'),",
            f"            StringStruct(u'FileDescription', u'{product_name}'),",
            f"            StringStruct(u'FileVersion', u'{file_version}'),",
            f"            StringStruct(u'InternalName', u'{product_name.replace(' ', '')}'),",
            f"            StringStruct(u'LegalCopyright', u'Copyright (c) {now.year} {company_name}'),",
            f"            StringStruct(u'OriginalFilename', u'{product_name.replace(' ', '')}.exe'),",
            f"            StringStruct(u'ProductName', u'{product_name}'),",
            f"            StringStruct(u'ProductVersion', u'{product_version}')",
            "          ]",
            "        )",
            "      ]",
            "    ),",
            "    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])",
            "  ]",
            ")",
            "",
        ]

        content = "\n".join(lines)
        try:
            with open(version_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            self.safe_log(f"✅ 版本信息已保存到 {version_file}")
        except Exception as e:
            self.safe_log(f"⚠️ 保存 version.txt 失败: {e}")

    def _build_ui(self):
        mf = ttk.Frame(self.root, padding="5")
        mf.pack(fill=tk.BOTH, expand=True)
        self.main_frame = mf

        top = ttk.Frame(mf)
        top.pack(fill=tk.X)
        self.top_frame = top
        if DND_AVAILABLE:
            top.drop_target_register(DND_FILES)
            top.dnd_bind("<<Drop>>", self._on_drop)

        r1 = ttk.Frame(top)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="输入文件:", width=8).pack(side=tk.LEFT)
        ttk.Label(r1, text="(可拖拽)", foreground="gray", font=("Arial", 8)).pack(
            side=tk.LEFT, padx=(2, 0))
        self.input_path = tk.StringVar()
        self.input_entry = ttk.Entry(r1, textvariable=self.input_path)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        if DND_AVAILABLE:
            self.input_entry.drop_target_register(DND_FILES)
            self.input_entry.dnd_bind("<<Drop>>", self._on_drop)
        ModernButton(r1, text="🔍选择", command=self._select_input, width=5).pack(side=tk.RIGHT)

        r2 = ttk.Frame(top)
        r2.pack(fill=tk.X, pady=2)
        ttk.Label(r2, text="输出目录:", width=8).pack(side=tk.LEFT)
        self.output_path = tk.StringVar(value=self.dist_dir)
        ttk.Entry(r2, textvariable=self.output_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ModernButton(r2, text="⚙️设置", command=self._select_output, width=5).pack(side=tk.RIGHT)

        r3 = ttk.Frame(top)
        r3.pack(fill=tk.X, pady=2)
        ttk.Label(r3, text="输出名称:", width=8).pack(side=tk.LEFT)
        self.output_name = tk.StringVar(value="我的应用程序")
        ttk.Entry(r3, textvariable=self.output_name).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ModernButton(r3, text="📷选图", command=self._select_icon, width=5).pack(side=tk.RIGHT, padx=1)
        ModernButton(r3, text="📊制图", command=self._open_icon_maker, width=5).pack(side=tk.RIGHT, padx=1)
        ModernButton(r3, text="🗑清除", command=self._clear_icon, width=5).pack(side=tk.RIGHT, padx=1)
        self.icon_label = ttk.Label(r3, text="", foreground="gray", font=("Arial", 9))
        self.icon_label.pack(side=tk.RIGHT, padx=2)

        r_env = ttk.Frame(top)
        r_env.pack(fill=tk.X, pady=2)
        ttk.Label(r_env, text="Python路径:", width=9).pack(side=tk.LEFT)
        #ttk.Entry(r_env, textvariable=self.custom_python_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        # 改为 Combobox
        self.python_path_combo = ttk.Combobox(r_env, textvariable=self.custom_python_path, state="readonly", width=30)
        self.python_path_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.python_path_combo.bind("<<ComboboxSelected>>", self._on_python_selected)
        self.refresh_python_btn = ModernButton(r_env, text="🔄", command=self._refresh_python_list, width=3)
        self.refresh_python_btn.pack(side=tk.LEFT, padx=1)
        self._add_tooltip(self.refresh_python_btn, "刷新")
        self.py_label = ttk.Label(r_env, text="", foreground="blue", font=("Consolas", 9))
        self.py_label.pack(side=tk.LEFT, padx=(10, 2))
        #for text, cmd in [("🔎浏览", self._select_python), ("🎫测试", self._test_python), ("🗑清除", self._clear_python)]:
            #ModernButton(r_env, text=text, command=cmd, width=5).pack(side=tk.LEFT, padx=1)
        self.browse_python_btn = ModernButton(r_env, text="🔎浏览", command=self._select_python, width=5)
        self.browse_python_btn.pack(side=tk.LEFT, padx=1)
        self.test_python_btn = ModernButton(r_env, text="🎫测试", command=self._test_python, width=5)
        self.test_python_btn.pack(side=tk.LEFT, padx=1)
        self.clear_switch_python_btn = ModernButton(r_env, text="🗑清除", command=self._clear_python, width=5)
        self.clear_switch_python_btn.pack(side=tk.LEFT, padx=1)

        opt = ttk.LabelFrame(top, text="打包选项", padding="3")
        opt.pack(fill=tk.X, pady=3)

        r4 = ttk.Frame(opt)
        r4.pack(fill=tk.X, pady=1)
        ttk.Label(r4, text="平台:", font=("Arial", 9)).pack(side=tk.LEFT)
        ttk.Combobox(r4, textvariable=self.target_platform, width=8, state="readonly",
                    values=("current", "Windows", "Linux", "macOS")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(r4, text="打包器:", font=("Arial", 9)).pack(side=tk.LEFT)
        self.packer_combo = ttk.Combobox(r4, textvariable=self.packer_type, width=9, state="readonly",
                                        values=("PyInstaller", "Nuitka", "Py2exe", "Cx_Freeze",
                                               "Pynsist", "PyOxidizer", "py2app"))
        self.packer_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.packer_combo.bind("<<ComboboxSelected>>", self._on_packer_changed)

        self.pkg_switch = ToggleSwitchWithLabel(r4, text="单模", on=True, command=self._on_pkg_switch)
        self.pkg_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.pkg_switch.switch, "开启：打包成单个exe文件\n关闭：打包成文件夹")

        self.multi_switch = ToggleSwitchWithLabel(
            r4, text="防多", command=self.multi_instance_switch, on=False
        )
        self.multi_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.multi_switch.switch, "开启后：打包的程序只能运行一个实例")
        
        self.workdir_switch = ToggleSwitchWithLabel(
            r4, text="目录", on=False, command=self._on_workdir_switch
        )
        self.workdir_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.workdir_switch.switch, "开启后：为exe所在目录\n关闭后：为系统临时目录")


        self.venv_switch = ToggleSwitchWithLabel(r4, text="虚拟", on=False, command=self._on_venv_switch)
        self.venv_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.venv_switch.switch, "开启：使用公共虚拟环境中的依赖库\n关闭：使用系统Python环境")

        self.debug_switch = ToggleSwitchWithLabel(
            r4, text="调试", on=False, command=self._on_debug
        )
        self.debug_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.debug_switch.switch, "开启后：显示控制台窗口，方便调试")


        self.upx_switch = ToggleSwitchWithLabel(
            r4, text="压缩", on=True, command=self._on_upx
        )
        self.upx_switch.pack(side=tk.LEFT, padx=3)
        self._add_tooltip(self.upx_switch.switch, "开启后：使用UPX压缩exe体积，减小文件大小")

        ttk.Entry(r4, textvariable=self.upx_path, width=15).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ModernButton(r4, text="🔧指定", command=self._select_upx, width=5).pack(side=tk.RIGHT)

        self.nuitka_frame = ttk.Frame(opt)
        self.nuitka_frame.pack(fill=tk.X, pady=2)
        self.nuitka_frame.pack_forget()

        nk = ttk.Frame(self.nuitka_frame)
        nk.pack(fill=tk.X, pady=1)
        ttk.Label(nk, text="并行:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Combobox(nk, textvariable=self.nuitka_jobs, width=8, state="readonly",
                    values=self.job_options).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(nk, text=f"(CPU {self.cpu_count}核)", font=("Arial", 8), foreground="green").pack(side=tk.LEFT)
        ttk.Label(nk, text="后端:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Combobox(nk, textvariable=self.nuitka_backend, width=8, state="readonly",
                    values=("auto", "MinGW64", "MSVC")).pack(side=tk.LEFT, padx=(0, 10))
        self.nuitka_backend.trace_add("write", lambda *a: self._update_compiler_status())
        self.compiler_label = ttk.Label(nk, text="", foreground="green", font=("Arial", 7))
        self.compiler_label.pack(side=tk.LEFT, padx=5)

        # GUI插件
        ttk.Label(nk, text="GUI插件:", font=("Arial", 8)).pack(side=tk.LEFT, padx=(10, 0))

        self.nuitka_gui_plugin = tk.StringVar(value="auto")
        plugin_combo = ttk.Combobox(nk, textvariable=self.nuitka_gui_plugin,
                                    width=8, state="readonly",
                                    values=("auto", "tk-inter", "pyqt5", "pyqt6",
                                            "pyside2", "pyside6", "wxpython", "kivy"))
        plugin_combo.pack(side=tk.LEFT, padx=5)

        # ========== Nuitka 4.1 兼容模式==========
        self.nuitka_compat_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            nk,
            text="4.1兼容",
            variable=self.nuitka_compat_mode,
            command=self._on_nuitka_compat_toggle
        ).pack(side=tk.LEFT, padx=(10, 2))

        ttk.Label(
            nk,
            text="(--deployment --windows-console-mode=disable)",
            foreground="gray",
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=0)

        self._update_compiler_status()

        # ========== 排除选项行（整个 bar 区域可拖拽 version.txt）==========
        bar = ttk.Frame(mf)
        bar.pack(fill=tk.X, pady=3)
        self.folders_bar = bar

        # ✅ 整个 bar 绑定 DND（左边按钮区+中间空白+右边版本信息都能拖）
        if DND_AVAILABLE:
            bar.drop_target_register(DND_FILES)
            bar.dnd_bind("<<Drop>>", self._on_version_drop)
        self.exclude_btn = ModernButton(bar, text="▶排除选项", command=self._toggle_exclude,
                                       normal_bg="#eef2f7", hover_bg="#e4e9f0", normal_fg="#4a5568", width=10)
        self.exclude_btn.pack(side=tk.LEFT)
        self.exclude_count = ttk.Label(bar, text="(0)", foreground="gray")
        self.exclude_count.pack(side=tk.LEFT, padx=5)
        # 自动导入按钮
        self.auto_import_btn = ModernButton(bar, text="⚡自动导入", command=self._auto_import_modules,
                                            normal_bg="#eef2f7", hover_bg="#e4e9f0", normal_fg="#4a5568",
                                            hover_fg="#ffffff", width=10)
        self.auto_import_count = ttk.Label(bar, text="", foreground="orange")
        # 初始不显示，等有分析结果再显示

        self.adv_btn = ModernButton(bar, text="▶依赖数据", command=self._toggle_advanced,
                                   normal_bg="#eef2f7", hover_bg="#e4e9f0", normal_fg="#4a5568", width=10)
        self.adv_btn.pack(side=tk.LEFT, padx=(20, 0))
        self.adv_count = ttk.Label(bar, text="(0)", foreground="gray")
        self.adv_count.pack(side=tk.LEFT, padx=5)
        
        self.version_info_btn = ModernButton(bar, text="📋版本更新", command=self._open_version_dialog,
                                     normal_bg="#eef2f7", hover_bg="#e4e9f0", normal_fg="#4a5568",
                                     hover_fg="#ffffff", width=10)
        self.version_info_btn.pack(side=tk.RIGHT, padx=5)
        
        self.exclude_frame = ttk.Frame(mf)
        self.exclude_visible = False

        r5 = ttk.Frame(self.exclude_frame)
        r5.pack(fill=tk.X, pady=1)
        ttk.Label(r5, text="排除模块:", width=8).pack(side=tk.LEFT)
        self.exclude_var = tk.StringVar()
        ttk.Entry(r5, textvariable=self.exclude_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        for text, cmd in [("🔄清空", self._clear_excludes), ("➖移除", self._remove_exclude),
                         ("➕添加", self._add_exclude), ("🔍智选", self._open_exclude),
                         ("⚡推荐", self._add_recommended)]:
            ModernButton(r5, text=text, command=cmd, width=5).pack(side=tk.RIGHT, padx=2)
        self.exclude_num = ttk.Label(r5, text="(0)", foreground="gray")
        self.exclude_num.pack(side=tk.RIGHT, padx=5)

        ef = ttk.Frame(self.exclude_frame)
        ef.pack(fill=tk.X, pady=2)
        sb = ttk.Scrollbar(ef, orient=tk.HORIZONTAL)
        sb.pack(side=tk.BOTTOM, fill=tk.X)
        self.exclude_listbox = tk.Listbox(ef, height=2, selectmode=tk.SINGLE, font=("Consolas", 8),
                                         xscrollcommand=sb.set)
        self.exclude_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        sb.config(command=self.exclude_listbox.xview)

        self.adv_frame = ttk.Frame(mf)
        self.adv_visible = False

        paned = ttk.PanedWindow(self.adv_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=2)

        hidden = ttk.LabelFrame(paned, text="依赖导入", padding="3")
        paned.add(hidden, weight=1)
        self.hidden_num = ttk.Label(hidden, text="(0)", foreground="gray")
        self.hidden_num.pack(side=tk.LEFT, padx=5)

        af = ttk.Frame(hidden)
        af.pack(fill=tk.X, pady=1)
        self.hidden_var = tk.StringVar()
        ttk.Entry(af, textvariable=self.hidden_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        ModernButton(af, text="🔩添加", command=self._add_hidden, width=5).pack(side=tk.RIGHT)

        bf = ttk.Frame(hidden)
        bf.pack(fill=tk.X, pady=1)
        for text, cmd in [("🔬分析", self._analyze_deps), ("📎推荐", self._add_recommended_hidden),
                         ("📦安装", self._auto_install), ("📄导出", self._export_req),
                         ("📂导入", self._import_req)]:
            ModernButton(bf, text=text, command=cmd, width=8).pack(side=tk.LEFT, padx=1)
        self.rec_label = ttk.Label(bf, text="", foreground="blue", font=("Arial", 7))
        self.rec_label.pack(side=tk.LEFT, padx=1)

        lf = ttk.Frame(hidden)
        lf.pack(fill=tk.BOTH, expand=True, pady=1)
        sb2 = ttk.Scrollbar(lf)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)
        self.hidden_listbox = tk.Listbox(lf, height=3, selectmode=tk.SINGLE, font=("Consolas", 8),
                                          yscrollcommand=sb2.set)
        self.hidden_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb2.config(command=self.hidden_listbox.yview)

        b3 = ttk.Frame(hidden)
        b3.pack(fill=tk.X, pady=1)
        for text, cmd in [("🗑删除", self._remove_hidden), ("🔁清空", self._clear_hidden),
                         ("💾保存", self._save_config), ("🐍虚拟", self._manage_venv),
                         ("autoexe", self._launch_auto)]:
            ModernButton(b3, text=text, command=cmd, width=8).pack(side=tk.LEFT, padx=1)

        data = ttk.LabelFrame(paned, text="数据文件", padding="3")
        paned.add(data, weight=1)

        for label, var in [("文件:", tk.StringVar()), ("目标:", tk.StringVar())]:
            f = ttk.Frame(data)
            f.pack(fill=tk.X, pady=1)
            ttk.Label(f, text=label, width=6).pack(side=tk.LEFT)
            if label == "文件:":
                self.data_src = var
                ttk.Entry(f, textvariable=self.data_src).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
                ModernButton(f, text="🔍浏览", command=self._select_data_src, width=6).pack(side=tk.RIGHT)
            else:
                self.data_tgt = var
                ttk.Entry(f, textvariable=self.data_tgt).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)
                ModernButton(f, text="🔩添加", command=self._add_data, width=6).pack(side=tk.RIGHT)

        df = ttk.Frame(data)
        df.pack(fill=tk.BOTH, expand=True, pady=1)
        sb3 = ttk.Scrollbar(df)
        sb3.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_listbox = tk.Listbox(df, height=2, selectmode=tk.SINGLE, font=("Consolas", 8),
                                       yscrollcommand=sb3.set)
        self.data_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb3.config(command=self.data_listbox.yview)
        if DND_AVAILABLE:
            self.data_listbox.drop_target_register(DND_FILES)
            self.data_listbox.dnd_bind("<<Drop>>", self._on_data_drop)

        b4 = ttk.Frame(data)
        b4.pack(fill=tk.X, pady=1)
        for text, cmd in [("❌删除", self._remove_data), ("🔄清空", self._clear_data),
                         ("📁打开", self._open_proj_dir), ("📁扫描", self._scan_data)]:
            ModernButton(b4, text=text, command=cmd, width=9).pack(side=tk.LEFT, padx=1)
        ttk.Label(data, text="💡 配置文件放项目下，点扫描或拖拽添加", foreground="gray",
                 font=("Arial", 7)).pack(anchor=tk.W, pady=1)

        btn = ttk.Frame(mf)
        btn.pack(fill=tk.X, pady=3)

        left = ttk.Frame(btn)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left, mode="determinate", variable=self.progress_var, maximum=100)
        self.progress_label = ttk.Label(left, text="", font=("Arial", 8))
        self.timer_label = ttk.Label(left, text="00:00", font=("Arial", 10, "bold"), foreground="#3a7dc9")

        right = ttk.Frame(btn)
        right.pack(side=tk.RIGHT)
        self.pack_btn = ModernButton(right, text="▶开始打包", command=self._toggle_pack, width=6)
        self.pack_btn.pack(side=tk.LEFT, padx=1)
        version = self._get_version()
        if version:
            self._add_tooltip(self.pack_btn, f"版本: {self.BUILD_DATE}")
        for text, cmd in [("🐍编译目录", self._open_output), ("📋导出日志", self._export_log),
                         ("⚪清空日志", self.clear_log), ("⏳恢复默认", self._reset),
                         ("🌞 默认主题", self._next_theme)]:
            ModernButton(right, text=text, command=cmd, width=6).pack(side=tk.LEFT, padx=1)
        self.theme_btn = right.winfo_children()[-1]

        log = ttk.LabelFrame(mf, text="打包日志", padding="2")
        log.pack(fill=tk.BOTH, expand=True, pady=3)
        ttk.Label(log, text="💡 可将数据文件拖拽到此区域自动添加", foreground="gray",
                 font=("Arial", 8)).pack(anchor=tk.W, pady=(0, 2))
        self.log_text = tk.Text(log, height=4, wrap=tk.WORD, font=("Consolas", 8))
        sb_log = ttk.Scrollbar(log, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb_log.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_log.pack(side=tk.RIGHT, fill=tk.Y)
        if DND_AVAILABLE:
            self.log_text.drop_target_register(DND_FILES)
            self.log_text.dnd_bind("<<Drop>>", self._on_log_drop)
            self.log_text.insert(tk.END, "💡 可将数据文件拖拽到此区域自动添加\n")

        status = ttk.Frame(mf)
        status.pack(fill=tk.X, pady=1)

        # 左侧状态文字
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(status, textvariable=self.status_var, relief=tk.SUNKEN,
                                      anchor=tk.W, font=("Arial", 8), width=20)
        self.status_label.pack(side=tk.LEFT, padx=2)

        # 中间进度条区域（固定宽度，不伸缩）
        progress_frame = ttk.Frame(status)
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.status_canvas = tk.Canvas(progress_frame, width=200, height=14, bg='#e0e0e0', highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.status_canvas.pack_forget()
        self.status_bar_id = None
        self.status_color = "#9e9e9e"

        self.status_pct = ttk.Label(progress_frame, text="", font=("Arial", 8), width=5)
        self.status_pct.pack(side=tk.LEFT, padx=2)

        # 右侧音乐播放器（固定宽度）
        music_container = ttk.Frame(status)
        music_container.pack(side=tk.RIGHT)

        self.music_toggle_btn = ModernButton(music_container, text="🎵🎬", command=self._toggle_music_panel, width=3)
        self.music_toggle_btn.pack(side=tk.RIGHT, padx=2)
        self._add_tooltip(self.music_toggle_btn, "播放器")
        self.music_frame = ttk.Frame(music_container)

        self.music_choose_btn = ModernButton(self.music_frame, text="📁", command=self._music_choose_folder, width=2)
        self.music_choose_btn.pack(side=tk.LEFT, padx=1)

        self.music_prev_btn = ModernButton(self.music_frame, text="⏮", command=self._music_prev, width=2)
        self.music_prev_btn.pack(side=tk.LEFT, padx=1)

        self.music_play_btn = ModernButton(self.music_frame, text="▶", command=self._music_play_pause, width=2)
        self.music_play_btn.pack(side=tk.LEFT, padx=1)

        self.music_stop_btn = ModernButton(self.music_frame, text="⏹", command=self._music_stop, width=2)
        self.music_stop_btn.pack(side=tk.LEFT, padx=1)

        self.music_next_btn = ModernButton(self.music_frame, text="⏭", command=self._music_next, width=2)
        self.music_next_btn.pack(side=tk.LEFT, padx=1)

        self.music_label = ttk.Label(self.music_frame, text="", font=("Arial", 7), foreground="gray", width=12)
        self.music_label.pack(side=tk.LEFT, padx=5)
        
        # 关于与帮助
        self.help_about_btn = ModernButton(status, text="❓", command=self._toggle_help_about, width=3)
        self.help_about_btn.pack(side=tk.RIGHT, padx=2)
        self._help_about_mode = "help"  # help 或 about
        self._add_tooltip(self.help_about_btn, "关于/帮助")

        self.status_bar = status

    def _on_version_drop(self, event):
        """主界面拖拽 version.txt - 直接生效，不打开弹窗"""
        temp_dialog = VersionInfoDialog.__new__(VersionInfoDialog)
        temp_dialog.app = self

        try:
            paths = temp_dialog._manual_parse_paths(event.data)
        except Exception:
            paths = []
        finally:
            del temp_dialog

        if not paths:
            return

        files = paths[0]

        if not os.path.isfile(files) or not files.lower().endswith('.txt'):
            return

        try:
            # 直接读取并解析 version.txt
            with open(files, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            self.version_info = {}

            # 提取各字段（和弹窗解析逻辑一致）
            match = re.search(r"StringStruct\(u'ProductName', u'([^']+)'\)", content)
            if match:
                self.version_info["ProductName"] = match.group(1)

            match = re.search(r"StringStruct\(u'CompanyName', u'([^']+)'\)", content)
            if match:
                self.version_info["CompanyName"] = match.group(1)

            match = re.search(r"StringStruct\(u'FileVersion', u'([^']+)'\)", content)
            if match:
                self.version_info["FileVersion"] = match.group(1)

            match = re.search(r"StringStruct\(u'ProductVersion', u'([^']+)'\)", content)
            if match:
                self.version_info["ProductVersion"] = match.group(1)

            # ✅ 直接生效：设置标志位
            self._version_info_ready = True
            '''
            # 按钮变绿
            self.version_info_btn.configure(
                normal_bg="#4caf50", hover_bg="#45a049", normal_fg="#ffffff"
            )
            '''
            self.safe_log(f"✅ 版本信息已生效: {os.path.basename(files)}")
            if self.version_info.get("ProductVersion"):
                self.safe_log(f"   产品版本: {self.version_info['ProductVersion']}")

        except Exception as e:
            self.safe_log(f"❌ 导入失败: {e}")

    def _import_version_from_file(self, file_path):
        """从 version.txt 导入版本信息（主界面拖拽，自动确认）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            import re
            version_info = {}

            match = re.search(r"StringStruct\(u'ProductName', u'([^']+)'\)", content)
            if match:
                version_info["ProductName"] = match.group(1)

            match = re.search(r"StringStruct\(u'CompanyName', u'([^']+)'\)", content)
            if match:
                version_info["CompanyName"] = match.group(1)

            match = re.search(r"StringStruct\(u'FileVersion', u'([^']+)'\)", content)
            if match:
                version_info["FileVersion"] = match.group(1)

            match = re.search(r"StringStruct\(u'ProductVersion', u'([^']+)'\)", content)
            if match:
                version_info["ProductVersion"] = match.group(1)

            self.version_info = version_info
            self._version_info_ready = True  # 添加这行
            self.safe_log(f"✅ 已从 {os.path.basename(file_path)} 导入版本信息")
            self.safe_log(f"   产品名称: {version_info.get('ProductName', '未设置')}")
            self.safe_log(f"   产品版本: {version_info.get('ProductVersion', '未设置')}")

        except Exception as e:
            self.safe_log(f"❌ 导入失败: {e}")

    def _add_tooltip(self, widget, text):
        def enter(e):
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{widget.winfo_rootx()+20}+{widget.winfo_rooty()+25}")
            tk.Label(tip, text=text, bg="#ffffe0", relief=tk.SOLID, borderwidth=1,
                    font=("微软雅黑", 9), padx=5, pady=2).pack()
            widget._tip = tip
        def leave(e):
            if hasattr(widget, '_tip') and widget._tip:
                widget._tip.destroy()
                widget._tip = None
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def safe_log(self, msg):
        try:
            if isinstance(msg, bytes):
                msg = msg.decode("utf-8", errors="replace")
            if sys.platform == "win32":
                if any(0x7F < ord(c) < 0x100 for c in msg):
                    try: msg = msg.encode("latin1").decode("gbk", errors="replace")
                    except: pass
            if self.log_text and self.log_text.winfo_exists():
                self.log_text.insert(tk.END, str(msg) + "\n")
                self.log_text.see(tk.END)
                self.root.update_idletasks()
        except: pass

    def _auto_import_modules(self):
        """自动导入分析出的模块到左侧依赖导入列表"""
        # 如果没有分析结果，先分析
        if not self.analyzed_modules:
            self.safe_log("🔍 正在分析依赖...")
            self._analyze_used(show_log=True, auto_add=False)
            if not self.analyzed_modules:
                self.safe_log("⚠️ 未发现可导入的模块")
                return

        # 找出未添加的模块
        new_modules = [m for m in self.analyzed_modules if m not in self.hidden_imports_list]

        # 根据是否有新模块执行不同逻辑
        if new_modules:
            # 有新模块：导入并写日志
            for m in new_modules:
                self.hidden_imports_list.append(m)
                self.hidden_listbox.insert(tk.END, m)

            self._update_hidden_count()
            self._update_auto_import_count()

            self.safe_log(f"✅ 已自动导入 {len(new_modules)} 个模块: {', '.join(new_modules[:5])}")
            if len(new_modules) > 5:
                self.safe_log(f"   ... 还有 {len(new_modules) - 5} 个模块")
        else:
            # 无新模块：只提示一次（通过标志位控制）
            if not hasattr(self, '_auto_import_no_new_logged'):
                self.safe_log("✅ 所有模块已在依赖导入列表中")
                self._auto_import_no_new_logged = True
            # 2秒后重置标志位，方便下次有新模块时重新提示
            self.root.after(2000, lambda: setattr(self, '_auto_import_no_new_logged', False))

        # 如果面板是折叠的，自动展开
        if not self.adv_visible:
            self._toggle_advanced()

    def _update_auto_import_count(self):
        """计数器2：自动导入 - 显示从分析结果自动导入的数量"""
        if not self.analyzed_modules:
            self._show_auto_import_button(False)
            return

        # 计算分析出的模块中有多少个已经导入到左侧列表
        auto_imported = len([m for m in self.analyzed_modules if m in self.hidden_imports_list])
        total = len(self.analyzed_modules)

        if auto_imported == 0:
            self._show_auto_import_button(True)
            self.auto_import_count.config(text=f"(0/{total})", foreground="orange")
        elif auto_imported == total:
            # 全部导入完成，显示绿色，但不隐藏按钮
            self._show_auto_import_button(True)
            self.auto_import_count.config(text=f"({auto_imported}/{total})", foreground="green")
        else:
            # 部分导入
            self._show_auto_import_button(True)
            self.auto_import_count.config(text=f"({auto_imported}/{total})", foreground="orange")

    def _show_auto_import_button(self, show=True):
        """显示或隐藏自动导入按钮"""
        if show:
            if not self.auto_import_btn.winfo_ismapped():
                self.auto_import_btn.pack(side=tk.LEFT, padx=(20, 5))
                self.auto_import_count.pack(side=tk.LEFT, padx=2)
        else:
            # 只有在 truly 需要隐藏时才隐藏（例如没有分析结果）
            if not self.analyzed_modules and self.auto_import_btn.winfo_ismapped():
                self.auto_import_btn.pack_forget()
                self.auto_import_count.pack_forget()

    

    def _find_default_py(self):
        """查找默认Python文件，优先选择入口文件"""
        # 优先级列表
        priority_files = ["main.py", "__main__.py", "run.py", "app.py", "launcher.py", "start.py"]

        # 1. 优先查找入口文件
        for priority in priority_files:
            priority_path = os.path.join(self.current_dir, priority)
            if os.path.exists(priority_path):
                return priority_path

        # 2. 查找其他py文件（排除自身）
        files = [f for f in os.listdir(self.current_dir)
                 if f.endswith(".py") and f != os.path.basename(__file__)]

        # 3. 如果有多个文件，返回第一个
        if files:
            return os.path.join(self.current_dir, files[0])

        return ""

    def _get_default_name(self):
        f = self.input_path.get()
        return os.path.splitext(os.path.basename(f))[0].replace(" ", "") if f and os.path.exists(f) else "我的应用程序"

    def _get_version(self):
        vf = os.path.join(self.current_dir, "version.txt")
        if os.path.exists(vf):
            try:
                with open(vf, "r", encoding="utf-8") as f:
                    m = re.search(r"StringStruct\(u'ProductVersion', u'([^']+)'\)", f.read())
                    if m: return m.group(1)
            except: pass
        return datetime.datetime.now().strftime("%Y.%m.%d.%H%M")


    def _update_python_btn(self):
        """根据当前 Python 路径是否为虚拟环境，更新按钮文字"""
        current = self.custom_python_path.get()
        if current and self._is_virtual_env_path(current):
            self.clear_switch_python_btn.config(text="🔄切换")
            self._add_tooltip(self.clear_switch_python_btn, "当前为虚拟环境，点击可切换回系统Python")
            # 虚拟环境模式：按钮显示"切换"，背景色改为橙色
            self.clear_switch_python_btn.config(text="🔄切换", bg="#ff9800", fg="#ffffff")
            self.clear_switch_python_btn.normal_bg = "#ff9800"
            self.clear_switch_python_btn.hover_bg = "#ffa726"
        else:
            self.clear_switch_python_btn.config(text="🗑清除")
            # 正常模式：按钮显示"清除"，恢复默认颜色
            self.clear_switch_python_btn.config(text="🗑清除", bg="#e8ecf1", fg="#333333")
            self.clear_switch_python_btn.normal_bg = "#e8ecf1"
            self.clear_switch_python_btn.hover_bg = "#4a8dd9"

    # 1. 去 .py 扩展名（模块级函数，类外定义）
    def strip_py_ext(self, filename):
        """去掉末尾连续的 .py（大小写不敏感）"""
        return re.sub(r'(\.[pP][yY])+$', '', filename)

    def parse_drop_path(self, data):
        if not data:        
            return ""
        # 去掉花括号（如果存在）
        if data.startswith('{') and data.endswith('}'):
            data = data[1:-1]
        # 直接处理完整路径，不要 split！
        path = data.strip().strip('"').strip("'")

        if path.startswith("file://"):
            path = path[7:]
        result = path.replace('/', os.sep)  
        return result

    # 2. 统一处理路径（类内方法）
    def _normalize_path(self, path):
        """
        统一处理路径（拖拽/选择通用）
        """
        if not path:
            return ""

        path = path.strip('{}')
        if path.startswith("file://"):
            path = path[7:]
        path = path.replace('/', os.sep)
        path = path.strip('"')

        return path

    # 4. 递归收集文件（类内方法）
    def _collect_files_recursive(self, path, pattern=None):
        """
        递归收集路径下的所有文件
        """
        files = []

        if os.path.isfile(path):
            if pattern is None or fnmatch.fnmatch(os.path.basename(path), pattern):
                files.append(path)
        elif os.path.isdir(path):
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if pattern is None or fnmatch.fnmatch(filename, pattern):
                        files.append(os.path.join(root, filename))

        return files

    def _find_all_python(self):
        """查找系统中所有可用的 Python 解释器（优化版）"""
        # 使用缓存，避免重复搜索
        if hasattr(self, '_python_list_cache') and time.time() - getattr(self, '_python_list_time', 0) < 300:
            return self._python_list_cache

        python_paths = set()

        # 1. 从 PATH 环境变量查找（快速）
        for d in os.environ.get("PATH", "").split(os.pathsep):
            for name in ['python.exe', 'python3.exe', 'python']:
                full = os.path.join(d, name)
                if os.path.exists(full):
                    try:
                        real_path = os.path.realpath(full)
                        python_paths.add(real_path)
                    except:
                        python_paths.add(full)

        # 2. 常见安装路径（快速）
        common_paths = [
            r"C:\Python312\python.exe", r"C:\Python311\python.exe",
            r"C:\Python310\python.exe", r"D:\Python312\python.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"),
            "/usr/bin/python3", "/usr/local/bin/python3",
        ]
        for p in common_paths:
            if os.path.exists(p):
                python_paths.add(p)

        # 3. 使用 where/which 命令（可能慢，放在最后）
        try:
            if sys.platform == "win32":
                result = subprocess.run(["where", "python"], capture_output=True, text=True, timeout=3)
                for line in result.stdout.splitlines():
                    if line.strip() and os.path.exists(line.strip()):
                        python_paths.add(line.strip())
            else:
                for name in ['python3', 'python']:
                    result = subprocess.run(["which", "-a", name], capture_output=True, text=True, timeout=3)
                    for line in result.stdout.splitlines():
                        if line.strip() and os.path.exists(line.strip()):
                            python_paths.add(line.strip())
        except:
            pass

        # 过滤虚拟环境
        python_list = sorted([p for p in python_paths if 'common_venv' not in p.lower()])

        # 缓存结果
        self._python_list_cache = python_list
        self._python_list_time = time.time()

        return python_list

    def _refresh_python_list(self):
        """异步刷新可用的 Python 路径列表"""
        # 显示加载提示
        self.python_path_combo.set("正在搜索...")

        def search():
            python_paths = self._find_all_python()
            self.root.after(0, lambda: self._update_python_list(python_paths))

        threading.Thread(target=search, daemon=True).start()

    def _update_python_list(self, python_paths):
        """更新下拉框列表（主线程）"""
        if python_paths:
            self.python_path_combo['values'] = python_paths
            current = self.custom_python_path.get()
            if current in python_paths:
                self.python_path_combo.set(current)
            elif python_paths:
                self.python_path_combo.set(python_paths[0])
                self.custom_python_path.set(python_paths[0])
        else:
            self.python_path_combo['values'] = []
            self.python_path_combo.set("未找到 Python")

    def _on_python_selected(self, event):
        """用户从下拉框选择 Python 路径时调用"""
        selected = self.python_path_combo.get()
        if selected and os.path.exists(selected):
            self.custom_python_path.set(selected)
            self._save_python_config()
            self._test_python()
            self._update_python_btn()

    def _get_python(self):
        """获取有效的 Python 解释器路径"""

        # 统一使用 ExePathManager.is_frozen() 判断打包环境
        is_frozen = ExePathManager.is_frozen()

        # 打包环境
        if is_frozen:
            # 1. 优先使用用户手动指定的路径
            custom = self.custom_python_path.get()
            if custom and os.path.exists(custom):
                if custom.lower().endswith('python.exe'):
                    if ExePathManager.is_temp_directory(custom):
                        self.safe_log(f"⚠️ 路径在临时目录，无效: {custom}")
                    elif os.path.abspath(custom).lower() == os.path.abspath(sys.executable).lower():
                        self.safe_log(f"⚠️ 路径指向程序自身，无效: {custom}")
                    else:
                        return custom
                else:
                    self.safe_log(f"⚠️ 路径不是 python.exe: {custom}")

            # 2. 使用系统命令查找
            system_python = self._find_system_python_by_cmd()
            if system_python:
                if not ExePathManager.is_temp_directory(system_python):
                    #self.safe_log(f"✅ 通过系统命令找到 Python: {system_python}")
                    self.root.after(0, lambda: self._set_python_path(system_python))
                    return system_python

            # 3. 都没找到，提示用户
            self.safe_log("❌ 未找到系统 Python，请手动指定 python.exe 路径")
            return None

        # 开发环境：正常自动检测
        if self.use_venv:
            vp = self._get_venv_python()
            if vp and os.path.exists(vp) and 'common_venv' not in vp.lower():
                return vp

        custom = self.custom_python_path.get()
        if custom and os.path.exists(custom) and 'common_venv' not in custom.lower():
            return custom

        if sys.executable and 'common_venv' not in sys.executable.lower():
            return sys.executable

        # 开发环境备选路径
        default_paths = []
        if sys.platform == 'win32':
            for version in ["313", "312", "311", "310"]:
                default_paths.append(f"C:\\Python{version}\\python.exe")
                default_paths.append(f"D:\\Python{version}\\python.exe")
            default_paths.append(os.path.expanduser(r"~\AppData\Local\Programs\Python\Python312\python.exe"))
        else:
            default_paths = ["/usr/bin/python3", "/usr/local/bin/python3"]

        for p in default_paths:
            if os.path.exists(p) and 'common_venv' not in p.lower():
                return p
        return None

    def _update_python_btn_state(self):
        """根据 Python 路径状态更新按钮颜色"""
        current_path = self.custom_python_path.get()

        if not current_path or not os.path.exists(current_path):
            # 路径为空或不存在：变黄
            self.test_python_btn.config(bg="#ff9800", fg="#ffffff")
            self.test_python_btn.normal_bg = "#ff9800"
            self.test_python_btn.hover_bg = "#ffa726"
            self.py_label.config(text="请选择Python路径", foreground="orange")
        else:
            # 路径存在，恢复默认颜色
            self.test_python_btn.config(bg="#4a8dd9", fg="#ffffff")
            self.test_python_btn.normal_bg = "#4a8dd9"
            self.test_python_btn.hover_bg = "#5a9de9"
           
    def _set_python_test_result(self, success, message, color="green"):
        """设置 Python 测试结果显示"""
        if success:
            self.py_label.config(text=message, foreground=color)
            # 测试成功：恢复系统默认颜色
            self.test_python_btn.config(bg="#e8ecf1", fg="#333333")
            self.test_python_btn.normal_bg = "#e8ecf1"
            self.test_python_btn.hover_bg = "#4a8dd9"
        else:
            self.py_label.config(text=message, foreground="red")
            # 测试失败：按钮变红
            self.test_python_btn.config(bg="#f44336", fg="#ffffff")
            self.test_python_btn.normal_bg = "#f44336"
            self.test_python_btn.hover_bg = "#e57373"

    def _update_python_ui_state(self):
        """根据当前 Python 路径更新测试按钮颜色"""
        current_path = self.custom_python_path.get()

        if not current_path:
            # 路径为空：按钮变黄
            self.test_python_btn.config(bg="#ff9800", fg="#ffffff")
            self.test_python_btn.normal_bg = "#ff9800"
            self.test_python_btn.hover_bg = "#ffa726"
            return

        if not os.path.exists(current_path):
            # 路径不存在：按钮变黄
            self.test_python_btn.config(bg="#ff9800", fg="#ffffff")
            self.test_python_btn.normal_bg = "#ff9800"
            self.test_python_btn.hover_bg = "#ffa726"
            return

        if not current_path.lower().endswith('python.exe'):
            # 路径不是 python.exe：按钮变红
            self.test_python_btn.config(bg="#f44336", fg="#ffffff")
            self.test_python_btn.normal_bg = "#f44336"
            self.test_python_btn.hover_bg = "#e57373"
            return

        # 路径有效：恢复默认颜色
        self.test_python_btn.config(bg="#e8ecf1", fg="#333333")
        self.test_python_btn.normal_bg = "#e8ecf1"
        self.test_python_btn.hover_bg = "#4a8dd9"

    def _on_python_path_change(self, *args):
        """Python 路径变化时更新 UI"""
        self._update_python_ui_state()

    def _get_venv_python(self):
        """获取虚拟环境中的 Python 路径（跨平台）"""
        venv_dir = os.path.join(self.current_dir, "common_venv")
        if sys.platform == 'win32':
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
        return python_path if os.path.exists(python_path) else None

    def _auto_detect_python(self):
        """自动检测系统Python"""
        # 使用 ExePathManager 判断打包环境
        if ExePathManager.is_frozen():
            return None
        return self._get_python()

    def _async_find_python(self):
        """后台线程查找Python"""
        python_path = self._auto_detect_python()

        if python_path and not self.custom_python_path.get():
            if ExePathManager.is_temp_directory(python_path):
                return
            if ExePathManager.is_frozen():
                if python_path.lower().endswith('python.exe') and 'common_venv' not in python_path.lower():
                    self.root.after(0, lambda: self._set_python_path(python_path))
            else:
                self.root.after(0, lambda: self._set_python_path(python_path))

    def _check_pyinstaller(self):
        py = self._get_python()
        # 打包环境：如果没有找到有效的 Python，直接返回
        if getattr(sys, 'frozen', False):
            if not py or not py.lower().endswith('python.exe'):
                return None, "未找到Python（请手动指定）"
            # 确保不是程序自身
            if os.path.abspath(py).lower() == os.path.abspath(sys.executable).lower():
                return None, "路径指向程序自身，请手动指定Python"

        if not py:
            return None, "未找到Python"

        try:
            r = subprocess.run([py, "-m", "PyInstaller", "--version"], capture_output=True, text=True,
                               timeout=5, startupinfo=get_startupinfo() if sys.platform == "win32" else None)
            return (py, r.stdout.strip()) if r.returncode == 0 else (py, "未安装")
        except:
            return py, "检测失败"

    def _detect_msvc(self):
        """检测 MSVC 编译器（跨平台）"""
        if sys.platform != "win32":
            return False

        # 方法1: 通过 vswhere 检测 Visual Studio
        for v in [r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe",
                  r"C:\Program Files\Microsoft Visual Studio\Installer\vswhere.exe"]:
            if os.path.exists(v):
                try:
                    r = subprocess.run([v, "-latest", "-property", "installationPath"],
                                       capture_output=True, text=True, timeout=5, startupinfo=get_startupinfo())
                    if r.returncode == 0 and r.stdout.strip():
                        return True
                except:
                    pass

        # 方法2: 查找 cl.exe，排除 MinGW/MSYS 目录
        try:
            r = subprocess.run(["where", "cl.exe"], capture_output=True, text=True, timeout=3,
                               startupinfo=get_startupinfo())
            if r.returncode == 0:
                paths = r.stdout.strip().split('\n')
                for path in paths:
                    path_lower = path.lower()
                    # 排除 MinGW/MSYS 目录
                    if 'mingw' in path_lower or 'msys' in path_lower:
                        continue
                    if os.path.exists(path):
                        return True
        except:
            pass

        return False

    def _detect_mingw(self):
        """检测 MinGW64 编译器（跨平台）"""
        import shutil

        # 方法1: 通过 PATH 查找 gcc
        gcc = shutil.which("gcc")
        if gcc:
            # 排除 MSVC 的 cl 伪装（非 Windows 不检查）
            if sys.platform == "win32":
                gcc_lower = gcc.lower()
                if 'mingw' in gcc_lower or 'msys' in gcc_lower:
                    return True, os.path.dirname(gcc)
                # 如果没有 mingw 特征，但确实是 gcc，也认为是 MinGW
                return True, os.path.dirname(gcc)
            else:
                # Linux/Mac 下 gcc 就是 GCC
                return True, os.path.dirname(gcc)

        # 方法2: 检查 tools 目录
        td = os.path.join(self.current_dir, "tools")
        if os.path.exists(td):
            for root, dirs, files in os.walk(td):
                if "gcc.exe" in files:
                    return True, os.path.dirname(os.path.join(root, "gcc.exe"))
                # 检查 mingw64/bin 目录
                if "mingw64" in dirs:
                    mingw_bin = os.path.join(root, "mingw64", "bin")
                    if os.path.exists(os.path.join(mingw_bin, "gcc.exe")):
                        return True, mingw_bin
        return False, None

    def _update_compiler_status(self):
        b = self.nuitka_backend.get()
        # 确保属性存在
        if not hasattr(self, 'has_msvc'):
            self.has_msvc = False
        if not hasattr(self, 'has_mingw'):
            self.has_mingw = False

        if b == "MinGW64":
            t, c = (("✓ MinGW64 已就绪", "green") if self.has_mingw else ("❌ MinGW64 未安装", "red"))
        elif b == "MSVC":
            t, c = (("✓ MSVC 已就绪", "green") if self.has_msvc else ("❌ MSVC 未安装", "red"))
        else:  # auto 模式
            # 优先显示 MinGW64
            if self.has_mingw:
                t, c = ("✓  MinGW64", "green")
            elif self.has_msvc:
                t, c = ("✓  MSVC", "green")
            else:
                t, c = ("⚠️ 将自动下载 MinGW64", "orange")

        self.compiler_label.config(text=t, foreground=c)

    def _toggle_help_about(self):
        """切换帮助/关于"""
        if self._help_about_mode == "help":
            # 显示帮助
            help_text = """使用帮助

    1. 选择Python文件
       - 点击「选择」按钮或拖拽.py文件（夹）
    2. 设置输出选项
       - 输出目录、输出名称（已默认）
    3. 选择打包器
       - PyInstaller：兼容性好
       - Nuitka：体积小，编译慢
    4. 虚拟环境
       - 开启后自动创建虚拟环境
       - 依赖库自动安装
    5. 开始打包
       - 点击「开始打包」按钮

    常见问题：
    • 打包后无法运行 → 添加隐藏导入
    • 打包体积大 → 启用UPX压缩
    • Python路径问题 → 手动指定python.exe
    """
            messagebox.showinfo("帮助", help_text)
            self.help_about_btn.config(text="ℹ️")
            self._help_about_mode = "about"
            self._add_tooltip(self.help_about_btn, "关于")
        else:
            # 显示关于
            version = self._get_version()
            about_text = f"""Python代码打包工具
    版本: {version}
 
    功能：（兼容Nuitka4.1）
    • 支持 PyInstaller、Nuitka、\n    Py2exe、Cx_Freeze等打包
    • 虚拟环境管理
    • 依赖自动分析
    • 跨多平台支持
    • 六种主题切换
    • 可音视频播放
    • 项目主页：\n    https://github.com/wcj6376

    © 2026 PyPackTool
    """
            messagebox.showinfo("关于", about_text)
            self.help_about_btn.config(text="❓")
            self._help_about_mode = "help"
            self._add_tooltip(self.help_about_btn, "帮助")

    def _toggle_music_panel(self):
        if self.music_visible:
            self.music_frame.pack_forget()
            self.music_toggle_btn.config(text="🎵🎬")
            self.music_visible = False
        else:
            self.music_frame.pack(side=tk.RIGHT, padx=5)
            self.music_toggle_btn.config(text="🎵✖🎬")
            self.music_visible = True

    def _music_choose_folder(self):
        folder = filedialog.askdirectory(title="选择音乐/视频文件夹")
        if not folder:
            return

        self.music_files = []
        # 支持更多音视频格式
        extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma',
                      '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.m4v')
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(extensions):
                    self.music_files.append(os.path.join(root, f))

        if not self.music_files:
            self.safe_log("⚠️ 未找到音视频文件")
            return

        import random
        random.shuffle(self.music_files)
        self.current_music_index = 0
        self.safe_log(f"🎵🎬 已加载 {len(self.music_files)} 个音视频文件")
        self._music_play_current()

    def _music_play_current(self):
        if not self.music_files:
            self.safe_log("⚠️ 请先选择音视频文件夹")
            return
        music_file = self.music_files[self.current_music_index]
        ext = os.path.splitext(music_file)[1].lower()
        icon = "🎵" if ext in ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma') else "🎬"
        self.music_label.config(text=f"{icon} {os.path.basename(music_file)[:20]}")
        self.music_play_btn.config(text="⏸")
        try:
            if sys.platform == "win32":
                os.startfile(music_file)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", music_file])
            else:
                subprocess.Popen(["xdg-open", music_file])
        except Exception as e:
            self.safe_log(f"❌ 播放失败: {e}")

    def _music_play_pause(self):
        self._music_stop()
        self._music_play_current()

    def _music_stop(self):
        if self.music_process and self.music_process.poll() is None:
            self.music_process.terminate()
            self.music_process = None
        self.music_play_btn.config(text="▶")
        self.music_label.config(text="")

    def _music_prev(self):
        if not self.music_files:
            return
        self._music_stop()
        self.current_music_index = (self.current_music_index - 1) % len(self.music_files)
        self._music_play_current()

    def _music_next(self):
        if not self.music_files:
            return
        self._music_stop()
        self.current_music_index = (self.current_music_index + 1) % len(self.music_files)
        self._music_play_current()

    def _get_installed(self):
        if self.installed_packages is not None:
            return self.installed_packages
        py, _ = self._check_pyinstaller()
        if not py:
            self.installed_packages = set()
            return set()
        try:
            r = subprocess.run([py, "-m", "pip", "list", "--format=freeze"], capture_output=True,
                              text=True, timeout=30, startupinfo=get_startupinfo())
            pkgs = set()
            for line in r.stdout.split("\n"):
                if "==" in line:
                    n = line.split("==")[0].lower()
                    pkgs.add(n)
                    pkgs.add(n.replace("-", "_"))
            self.installed_packages = pkgs
            self.safe_log(f"✓ 已获取 {len(pkgs)} 个包")
            return pkgs
        except Exception as e:
            self.safe_log(f"⚠️ 获取失败: {e}")
            self.installed_packages = set()
            return set()

    def _parse_imports(self, code):
        try:
            tree = ast.parse(code)
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
            return imports
        except: return set()

    def is_standard_module(module_name):
        """动态检测 + 预制列表结合判断标准库"""
        import importlib.util

        # 方法1: 动态检测模块位置
        try:
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                # 标准库不在 site-packages 中
                if 'site-packages' not in spec.origin and 'dist-packages' not in spec.origin:
                    return True
        except:
            pass

        # 方法2: Python 3.10+ 内置标准库列表
        if hasattr(sys, 'stdlib_module_names'):
            if module_name in sys.stdlib_module_names:
                return True

        # 方法3: 回退到预制列表（作为兜底）
        return module_name in STANDARD_LIBS

    def _get_package_name_from_module(self, module_name):
        """通过 pip 获取模块对应的包名（动态检测）"""
        import subprocess

        py = self._get_python()
        if not py:
            return MODULE_TO_PACKAGE.get(module_name, module_name)

        try:
            # 使用 pip show 查询
            r = subprocess.run([py, "-m", "pip", "show", module_name],
                               capture_output=True, text=True, timeout=5,
                               startupinfo=get_startupinfo() if sys.platform == "win32" else None)
            if r.returncode == 0:
                for line in r.stdout.split('\n'):
                    if line.startswith('Name:'):
                        return line.split(':', 1)[1].strip().lower()
        except:
            pass

        # 回退到映射表
        return MODULE_TO_PACKAGE.get(module_name, module_name)

    def _analyze_used(self, show_log=True, auto_add=True):
        f = self.input_path.get()
        if not f or not os.path.exists(f):
            if show_log:
                self.safe_log("⚠️ 未选择有效的Python文件")
            return set()

        all_imports = set()

        # ========== 自动判断：文件还是文件夹 ==========
        if os.path.isdir(f):
            # 文件夹模式：扫描所有 py 文件
            exclude_dirs = {"venv", "common_venv", "__pycache__", ".venv", "env", "dist", "build", "lib", "include",
                            "bin", "Scripts"}
            py_files = []
            for root, dirs, files in os.walk(f):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                for file in files:
                    if file.endswith(".py"):
                        py_files.append(os.path.join(root, file))

            if show_log:
                self.safe_log(f"📁 扫描到 {len(py_files)} 个 Python 文件")

            for pf in py_files:
                try:
                    with open(pf, "r", encoding="utf-8") as fobj:
                        content = fobj.read()
                    imports = self._parse_imports(content)
                    all_imports.update(imports)
                except Exception as e:
                    if show_log:
                        self.safe_log(f"   ⚠️ 分析 {os.path.basename(pf)} 失败: {e}")
        else:
            # 单文件模式
            try:
                with open(f, "r", encoding="utf-8") as fobj:
                    content = fobj.read()
                all_imports = self._parse_imports(content)
            except Exception as e:
                if show_log:
                    self.safe_log(f"❌ 分析失败: {e}")
                return set()
        # ============================================

        d = os.path.dirname(f)
        local = {f[:-3].lower() for f in os.listdir(d) if f.endswith(".py")}

        def is_standard_module(module_name):
            import importlib.util
            try:
                spec = importlib.util.find_spec(module_name)
                if spec and spec.origin:
                    if 'site-packages' not in spec.origin and 'dist-packages' not in spec.origin:
                        return True
            except:
                pass
            if hasattr(sys, 'stdlib_module_names'):
                if module_name in sys.stdlib_module_names:
                    return True
            return module_name in STANDARD_LIBS

        third_dict = {}
        has_tk = False

        for imp in all_imports:
            il = imp.lower()

            if il in ("tk", "tkinter"):
                has_tk = True
                continue

            if il in local:
                continue

            if is_standard_module(il):
                continue

            pkg_name = MODULE_TO_PACKAGE.get(imp, imp)

            if pkg_name not in third_dict:
                third_dict[pkg_name] = imp

        third = list(third_dict.values())

        if has_tk and "tk" not in third:
            third.append("tk")

        self.analyzed_modules = third
        self._update_auto_import_count()

        if show_log:
            if third:
                third_count = len([m for m in third if m != "tk"])
                tk_count = 1 if "tk" in third else 0

                third_preview = ', '.join([m for m in third[:5] if m != "tk"])
                if len(third) > 5:
                    third_preview += '...'

                if tk_count:
                    self.safe_log(
                        f"📊 分析完成，发现 {third_count} 个第三方模块: {third_preview}，1 个 tk 标准库")
                else:
                    self.safe_log(
                        f"📊 分析完成，发现 {third_count} 个第三方模块: {third_preview}")

                if auto_add:
                    added = []
                    for m in third:
                        if m not in self.hidden_imports_list:
                            self.hidden_imports_list.append(m)
                            self.hidden_listbox.insert(tk.END, m)
                            added.append(m)

                    if added:
                        self._update_hidden_count()
                        self.safe_log(f"✅ 已自动添加 {len(added)} 个模块到依赖导入列表")
                    else:
                        self.safe_log("✅ 所有模块已在依赖导入列表中")
                else:
                    pending = len([m for m in third if m not in self.hidden_imports_list])
                    if pending:
                        self.safe_log(f"💡 其中 {pending} 个模块尚未导入，点击'⚡ 自动导入'按钮添加")

            else:
                if has_tk:
                    self.safe_log("📊 分析完成，仅检测到 1 个 tk（标准库）")
                else:
                    self.safe_log("📊 分析完成，未发现第三方模块依赖")

        return set(third)
    
    def _analyze_missing(self):
        f = self.input_path.get()
        if not f:
            return []

        if os.path.isdir(f):
            return self._analyze_dir_missing(f)

        try:
            with open(f, "r", encoding="utf-8") as fobj:
                imports = self._parse_imports(fobj.read())
        except Exception:
            return []

        d = os.path.dirname(f)
        local = {f[:-3].lower() for f in os.listdir(d) if f.endswith(".py")}
        installed = self._get_installed()

        STANDARD_LIBS_EXCEPT_TK = STANDARD_LIBS - {"tkinter"}

        missing = []
        has_tk = False

        for imp in imports:
            il = imp.lower()

            if il in ("tk", "tkinter"):
                has_tk = True
                continue

            if il in STANDARD_LIBS_EXCEPT_TK or il in local or il in EXCLUDE_PACKAGES:
                continue

            if il in installed:
                continue

            pkg = MODULE_TO_PACKAGE.get(imp, imp)
            if pkg.lower() in installed:
                continue
            if pkg.lower().replace("-", "_") in installed:
                continue

            missing.append(pkg)

        # ✅ tkinter / tk 永远不参与 pip 安装
        if has_tk:
            self.safe_log("ℹ️ 检测到 tk（标准库，无需 pip 安装）")

        return list(set(missing))


    def _analyze_dir_missing(self, path):
        """分析文件夹中所有 Python 文件的依赖（返回所有第三方包，不管是否已安装）"""
        all_imp = set()
        exclude_dirs = {
            "venv", "common_venv", "__pycache__", ".venv",
            "env", "dist", "build", "lib", "include",
            "bin", "Scripts", "test", "tests", ".git", ".idea", ".vscode"
        }
        py_files = []

        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(root, file))

        self.safe_log(f"📁 扫描到 {len(py_files)} 个 Python 文件")

        for pf in py_files:
            try:
                with open(pf, "r", encoding="utf-8") as f:
                    code = f.read()
                imports = self._parse_imports(code)
                all_imp.update(imports)
            except Exception as e:
                self.safe_log(f"   ⚠️ 分析 {os.path.basename(pf)} 失败: {e}")

        local = set()
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                if f.endswith(".py"):
                    local.add(f[:-3].lower())
            for d in dirs:
                local.add(d.lower())

        STANDARD_LIBS_EXCEPT_TK = STANDARD_LIBS - {"tkinter"}

        third_party = []
        has_tk = False

        for imp in all_imp:
            il = imp.lower()

            if il in ("tk", "tkinter"):
                has_tk = True
                continue

            if il in STANDARD_LIBS_EXCEPT_TK or il in local or il in EXCLUDE_PACKAGES:
                continue

            pkg = MODULE_TO_PACKAGE.get(imp, imp)
            third_party.append(pkg)

        # ✅ 保证列表里只有 tk
        if has_tk and "tk" not in third_party:
            third_party.append("tk")

        third_party = list(set(third_party))
        self.safe_log(f"📦 需要的第三方包: {third_party}")
        return third_party
    
    def _toggle_exclude(self):
        if self.exclude_visible:
            self.exclude_frame.pack_forget()
            self.exclude_btn.config(text="▶ 排除选项")
        else:
            self.exclude_frame.pack(fill=tk.X, pady=5, after=self.folders_bar)
            self.exclude_btn.config(text="▼ 排除选项")
        self.exclude_visible = not self.exclude_visible

    def _toggle_advanced(self):
        if self.adv_visible:
            self.adv_frame.pack_forget()
            self.adv_btn.config(text="▶ 依赖数据")
        else:
            self.adv_frame.pack(fill=tk.BOTH, expand=True, pady=5, after=self.folders_bar)
            self.adv_btn.config(text="▼ 依赖数据")
        self.adv_visible = not self.adv_visible

    def _on_drop(self, event):
        """通用拖拽处理"""
        self._clear_all()
        files = self.parse_drop_path(event.data)

        if not files or not os.path.exists(files):
            return

        is_valid, error_msg = validate_path(files)
        if not is_valid:
            messagebox.showwarning("路径无效", error_msg)
            return

        if os.path.isfile(files) and files.lower().endswith(".py"):
            # 拖入的是 .py 文件
            base = os.path.basename(files)
            self.input_path.set(files)
            self.output_name.set(self.strip_py_ext(base))

            # ========== 新增：重置版本信息，使用新的文件名 ==========
            self._version_info_ready = False
            if hasattr(self, 'version_info') and self.version_info:
                self.version_info["ProductName"] = self.output_name.get()
                self._save_version_config()

            # 重新分析依赖
            threading.Thread(target=lambda: self._analyze_used(show_log=True, auto_add=True), daemon=True).start()
            self.safe_log(f"📁 拖拽Python文件: {base}")

        elif os.path.isdir(files):
            # 拖入的是文件夹
            py_files = self._collect_files_recursive(files, "*.py")

            if not py_files:
                messagebox.showwarning("未找到Python文件", f"文件夹内未找到 .py 文件：\n{files}")
                return

            # 找主文件
            main_names = {"main.py", "app.py", "run.py", "index.py", "start.py", "manage.py"}
            main_file = None
            for f in py_files:
                if os.path.basename(f).lower() in main_names:
                    main_file = f
                    break

            target = main_file or py_files[0]
            base = os.path.basename(target)
            self.input_path.set(target)
            self.output_name.set(self.strip_py_ext(base))

           
            self._version_info_ready = False
            if hasattr(self, 'version_info') and self.version_info:
                self.version_info["ProductName"] = self.output_name.get()
                self._save_version_config()

            hint = "主文件" if main_file else "首个Python文件"
            threading.Thread(target=lambda: self._analyze_used(show_log=True, auto_add=True), daemon=True).start()
            self.safe_log(f"📁 拖拽文件夹，自动识别{hint}: {base}")

            entry = self._find_entry(files)
            if entry and self.multi_switch.get():
                self._inject_single_instance(entry)

    def _set_input(self, path, log_msg):
        """统一设置输入路径和输出名"""
        base = os.path.basename(path)
        self.input_path.set(path)
        self.output_name.set(self.strip_py_ext(base))
        self.safe_log(log_msg)
        # 同步版本信息中的产品名称
        self._sync_version_product_name()
        self.safe_log(log_msg)

    def _find_entry(self, path):
        for e in ["main.py", "__main__.py", "run.py", "app.py", "launcher.py"]:
            p = os.path.join(path, e)
            if os.path.exists(p): return p
        py_files = [f for f in os.listdir(path) if f.endswith(".py")]
        return os.path.join(path, py_files[0]) if py_files else None

    def _on_pkg_switch(self, value):
        self.package_type.set("onefile" if value else "onedir")
        self.safe_log(f"📦 打包模式: {'单文件' if value else '文件夹'}")
    def _on_debug(self, value):
        self.use_venv = value
        if value:
            self.safe_log(" 已启用无控制台模式")
        else:
            self.safe_log(" 已启用控制台模式")

    def _on_upx(self, value):
        self.use_upx = value
        if value:
            self.safe_log(" 已启用upx压缩")
        else:
            self.safe_log(" 已禁用upx压缩")

    def on_upx_toggle(self):
        if hasattr(self, "upx_switch"):
            use_upx = self.upx_switch.get()
        else:
            use_upx = self.use_upx.get()

        if use_upx:
            # 关键：如果已有有效路径（用户手动指定过的），直接使用，不再自动查找
            current_path = self.upx_path.get()
            if current_path and os.path.exists(current_path):
                self.safe_log(f"✅ 使用已有UPX: {current_path}")
                return

            # 只有当路径为空或无效时，才尝试自动查找
            if not self._upx_auto_find_done:  # 避免重复查找
                self._upx_auto_find_done = True
                threading.Thread(target=self._async_find_upx, daemon=True).start()
        else:
            # 关闭开关时，不清空保存的路径，保存的配置不变
            self.upx_path.set("")

    def _on_workdir_switch(self, value):
        """工作目录开关：开启时注入工作目录代码，关闭时不注入"""
        self.workdir_enabled = value
        input_file = self.input_path.get()

        if value:
           self.safe_log("📁 路径设置已启用（打包时将自动注入）")
        else:
            if self._remove_workdir_code(input_file):
                self.safe_log("🔓 已移除路径设置代码")

    def multi_instance_switch(self, value):
        """防多开开关：开启时记录状态，关闭时立即移除"""
        self.multi_instance_enabled = value
        input_file = self.input_path.get()

        if not input_file or not os.path.exists(input_file):
            if value:
                self.safe_log("⚠️ 请先选择文件，再开启防多开开关")
                self.multi_switch.set(False)
                self.multi_instance_enabled = False
            return

        if value:
            # 开启：只记录状态，不自动注入（等打包时再注入）
            self.safe_log("🔒 防多开已启用（打包时将自动注入）")
        else:
            # 关闭：立即移除防多开代码
            if self._remove_single_instance(input_file):
                self.safe_log("🔓 已移除防多开代码")

    def _remove_single_instance(self, source_file):
        """移除注入的防多开代码（只检查前20行，只删除注入块）"""
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 只检查前20行
            first_20_lines = ''.join(lines[:20])
            if '# SINGLE_INSTANCE_GUARD' not in first_20_lines:
                return False

            # 查找注入代码块的起始和结束行
            start_idx = -1
            end_idx = -1

            for i, line in enumerate(lines[:20]):
                if '# SINGLE_INSTANCE_GUARD' in line:
                    start_idx = i
                if start_idx != -1 and '# END GUARD' in line:
                    end_idx = i
                    break

            # 如果找到了完整的代码块，删除它
            if start_idx != -1 and end_idx != -1:
                # 检查前后是否有空行（只删除因删除代码块产生的空行）
                # 如果前一行是空行，扩展删除范围
                if start_idx > 0 and lines[start_idx - 1].strip() == '':
                    start_idx = start_idx - 1
                # 如果后一行是空行，扩展删除范围
                if end_idx + 1 < len(lines) and lines[end_idx + 1].strip() == '':
                    end_idx = end_idx + 1

                # 删除从 start_idx 到 end_idx 的行
                new_lines = lines[:start_idx] + lines[end_idx + 1:]
                new_content = ''.join(new_lines)

                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                # 移除成功，关闭开关
                self.multi_switch.set(False)
                self.multi_instance_enabled = False

                return True
            else:
                self.safe_log("⚠️ 未找到完整的防多开代码块")
                return False

        except Exception as e:
            self.safe_log(f"❌ 移除失败: {e}")
            return False

    def inject_single_instance(self, source_file):
        """注入防多开代码（检查前20行）"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 只检查前20行
            first_20_lines = '\n'.join(content.split('\n')[:20])
            if '# SINGLE_INSTANCE_GUARD' in first_20_lines:
                self.safe_log("✅ 防多开代码已存在")
                return True

            code = '''# SINGLE_INSTANCE_GUARD - 防止多开
import sys, os, tempfile
_lock_file = os.path.join(tempfile.gettempdir(), f"{os.path.basename(sys.argv[0])}.lock")
try:
    if sys.platform == 'win32':
        import msvcrt
        _fd = open(_lock_file, 'w')
        msvcrt.locking(_fd.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        _fd = open(_lock_file, 'w')
        fcntl.flock(_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except:
    sys.exit(0)
# END GUARD
'''
            new_content = code + content
            with open(source_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            # 注入后计算行数
            new_content = code + content
            line_count = len(new_content.split('\n')) - len(content.split('\n'))
            self.safe_log(f"✅ 已注入防多开代码（第1-{line_count}行）")
            return True
        except Exception as e:
            self.safe_log(f"❌ 注入失败: {e}")
            return False

    def _on_venv_switch(self, value):
        self.use_venv = value
        if value:
            self.safe_log("🐍 已启用虚拟环境")
            if not getattr(self, '_loading_config', False):
                self.root.after(100, lambda: self._manage_venv(silent=True))
        else:
            self.safe_log("🐍 已禁用虚拟环境")
            self.venv_switch.set(False)
            self.use_venv = False

            # 只删除虚拟环境下的依赖库文件夹（保留虚拟环境核心结构）
            def clean_venv_lib():
                venv_dir = os.path.join(self.current_dir, "common_venv")
                if not os.path.exists(venv_dir):
                    return

                try:
                    # 确定 Lib/lib 文件夹路径（跨平台）
                    if sys.platform == "win32":
                        lib_dir = os.path.join(venv_dir, "Lib")
                    else:
                        lib_dir = os.path.join(venv_dir, "lib")

                    # 只删除依赖库文件夹（快速删除）
                    if os.path.exists(lib_dir):
                        self._fast_rmtree(lib_dir)
                        self.safe_log("🗑️已清理虚拟环境依赖库")
                    else:
                        # 如果没有 Lib/lib 目录，可能是损坏的环境，直接删除整个目录
                        self._rename_and_delete(venv_dir)
                        self.safe_log("🗑️已删除损坏的虚拟环境")

                except Exception as e:
                    self.safe_log(f"⚠️ 清理失败: {e}")

            threading.Thread(target=clean_venv_lib, daemon=True).start()

    def _preload_all_packers_version(self):
        """预加载所有打包器版本（启动时尝试，失败不阻塞）"""
        packer_pip_map = {
            'PyInstaller': 'pyinstaller',
            'Nuitka': 'nuitka',
            'Py2exe': 'py2exe',
            'Cx_Freeze': 'cx-freeze',
            'Pynsist': 'pynsist',
            'PyOxidizer': 'pyoxidizer',
            'py2app': 'py2app'
        }

        py = self._get_python()
        if not py:
            self._packer_versions = {name: None for name in packer_pip_map.keys()}
            return

        self._packer_versions = {}

        for packer_name, pip_name in packer_pip_map.items():
            try:
                r = subprocess.run([py, "-m", "pip", "show", pip_name],
                                   capture_output=True, text=True, timeout=5,
                                   startupinfo=get_startupinfo() if sys.platform == "win32" else None)

                if r.returncode == 0:
                    for line in r.stdout.split('\n'):
                        if line.startswith('Version:'):
                            self._packer_versions[packer_name] = line.split(':', 1)[1].strip()
                            break
                else:
                    self._packer_versions[packer_name] = None
            except Exception:
                self._packer_versions[packer_name] = None

    def _get_packer_version_sync(self, packer_name, pip_name):
        """同步获取单个打包器版本（打包环境也允许检测系统Python）"""
        py = self._get_python()

        # 如果获取到的 py 无效，尝试从 PATH 查找系统 Python
        if not py or not os.path.exists(py):
            import shutil
            py = shutil.which("python.exe")
            if not py:
                return None

        # 排除临时目录（Nuitka 解压目录）
        if 'temp' in py.lower() or 'onefile' in py.lower():
            return None

        # 打包环境下，确保获取的不是exe自身
        if getattr(sys, 'frozen', False):
            if os.path.abspath(py).lower() == os.path.abspath(sys.executable).lower():
                return None

        try:
            r = subprocess.run([py, "-m", "pip", "show", pip_name],
                               capture_output=True, text=True, timeout=5,
                               startupinfo=get_startupinfo() if sys.platform == "win32" else None)

            if r.returncode == 0:
                for line in r.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
            return None
        except Exception:
            return None

    def _on_packer_changed(self, event=None):
        packer = self.packer_type.get()
        self.clear_log()
        self.nuitka_frame.pack_forget()

        packer_pip_map = {
            'PyInstaller': 'pyinstaller',
            'Nuitka': 'nuitka',
            'Py2exe': 'py2exe',
            'Cx_Freeze': 'cx-freeze',
            'Pynsist': 'pynsist',
            'PyOxidizer': 'pyoxidizer',
            'py2app': 'py2app'
        }

        pip_name = packer_pip_map.get(packer, '')
        version = None

        # 先尝试从缓存获取
        if hasattr(self, '_packer_versions'):
            version = self._packer_versions.get(packer)

        # 如果缓存为空或为None，实时检测
        if not version:
            version = self._get_packer_version_sync(packer, pip_name)
            # 更新缓存
            if hasattr(self, '_packer_versions'):
                self._packer_versions[packer] = version

        # 构建版本字符串
        if version:
            version_str = f" (版本: {version})"
        else:
            version_str = " ⚠️ 未安装"

        # 显示打包器信息（您原有的代码不变）
        if packer == "Nuitka":
            self.nuitka_frame.pack(fill=tk.X, pady=2)
            self._update_compiler_status()

            # ========== 切换时自动检测并勾选 4.1 兼容模式 ==========
            def check_and_enable():
                py = self._get_python()
                if py:
                    installed, version = self._check_nuitka(py)
                    if installed and version and version.startswith("4.1"):
                        self.root.after(0, lambda: self._auto_enable_nuitka_compat(version))

            threading.Thread(target=check_and_enable, daemon=True).start()
            # ===================================================

            self.safe_log(
                "📌 Nuitka 模式：编译优化，体积小，需要 C 编译器。常用参数:\n    "
                + " ".join([
                    "python -m nuitka ",
                    "--onefile ",
                    "--standalone ",
                    "--windows-disable-console ",
                    "--include-data-dir=images=images ",
                    "--plugin-enable=pylint-warnings ",
                    "--windows-icon-from-ico=app.ico ",
                    "your_script.py",
                ])
            )
        elif packer == "PyInstaller":
            self.safe_log(
                f"📌 PyInstaller 模式{version_str}：最成熟，兼容性最好。常用参数:\n    "
                + " ".join(
                    [
                        "pyinstaller ",
                        "-F ",
                        "--noconsole ",
                        "--icon=app.ico ",
                        '--add-data "images;images" ',
                        "--hidden-import=pkg_resources ",
                        "--clean ",
                        "your_script.py",
                    ]
                )
            )
        elif packer == "Pynsist":
            self.safe_log(
                f"📌 Pynsist 模式{version_str}：生成 NSIS 安装程序，适合分发，需要安装Nsis 命令：pynsist_exe, cfg_path"
            )
        elif packer == "Py2exe":
            self.safe_log(
                f"📌 Py2exe 模式{version_str}：传统打包工具，兼容性好。命令： python setup.py py2exe"
            )
        elif packer == "Cx_Freeze":
            self.safe_log(
                f"📌 Cx_Freeze 模式{version_str}：跨平台打包。命令：cxfreeze your_script.py --target-dir dist"
            )
        elif packer == "PyOxidizer":
            self.safe_log(
                f"📌 PyOxidizer 模式{version_str}：嵌入解释器，启动快，需要 Rust 环境。命令：pyoxidizer build"
            )
            if version_str == " ⚠️ 未安装":
                self.safe_log("   首次使用需安装: https://rustup.rs/")
        elif packer == "py2app":
            self.safe_log(
                f"📌 py2app 模式{version_str}：能够创建符合 macOS 规范的应用程序包 (.app)。命令：python setup.py py2app"
            )

    def _auto_enable_nuitka_compat(self, version):
        """自动启用 Nuitka 4.1 兼容模式"""
        if not self.nuitka_compat_mode.get():
            self.nuitka_compat_mode.set(True)
            self.safe_log(f"⚠️ 检测到 Nuitka {version}，已自动启用兼容模式")
            #self.safe_log("💡 后端 auto 模式，将自动检测可用编译器")
            self.safe_log("   - --standalone → --deployment")
            self.safe_log("   - --windows-disable-console → --windows-console-mode=disable")
            #self.safe_log("   - --windows-icon-from-ico → --windows-icon")
    
    def _next_theme(self):
        self.theme_manager.next()

    def _select_input(self):
        f = filedialog.askopenfilename(title="选择Python文件", filetypes=[("Python", "*.py")],
                                       initialdir=self.current_dir)
        if f:
            self._clear_all()
            self.input_path.set(f)
            self.output_name.set(self.strip_py_ext(os.path.basename(f)))

            # ========== 新增：重置版本信息，使用新的文件名 ==========
            # 重置版本信息标志，让下次打开弹窗时使用新的默认值
            self._version_info_ready = False
            # 不清空 version_info，但标记为需要更新
            # 可选：自动更新产品名称为新的输出名称
            if hasattr(self, 'version_info') and self.version_info:
                # 只更新产品名称，保留其他设置
                self.version_info["ProductName"] = self.output_name.get()
                self._save_version_config()

            # 异步加载项目配置
            threading.Thread(target=self._async_load_config, daemon=True).start()
            # 异步分析依赖
            threading.Thread(target=lambda: self._analyze_used(show_log=True), daemon=True).start()

            self._on_packer_changed()

            if self.venv_switch.get():
                self.root.after(100, lambda: self._manage_venv(silent=True))

            self.safe_log(f"📁 已选择: {os.path.basename(f)}")

    def _select_output(self):
        d = filedialog.askdirectory(initialdir=self.output_path.get() if os.path.exists(self.output_path.get()) else self.current_dir)
        if d: self.output_path.set(d)
    
    def _select_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Icons", "*.ico")])
        if f:
            self.icon_path.set(f)
            self.icon_label.config(text=f"✓ {os.path.basename(f)}", foreground="green")

            # 联动显示：立即更新窗口左上角图标
            try:
                self.root.iconbitmap(f)
                self.safe_log(f"🖼️ 窗口图标已更新: {os.path.basename(f)}")
            except Exception as e:
                self.safe_log(f"⚠️ 图标预览失败: {e}")

    def _clear_icon(self):
        # 恢复默认图标
        default_icon = ExePathManager.get_resource_path("tool.ico")
        if os.path.exists(default_icon):
            try:
                self.root.iconbitmap(default_icon)
                self.icon_path.set(default_icon)  # 重新设置为默认图标路径
                self.icon_label.config(text=f"✓ {os.path.basename(default_icon)}", foreground="green")
                self.safe_log("🖼️ 已恢复默认窗口图标")
            except Exception as e:
                self.safe_log(f"⚠️ 恢复图标失败: {e}")
        else:
            self.icon_path.set("")
            self.icon_label.config(text="")
            self.safe_log("🗑 已清除所选图标")

    def _open_icon_maker(self):
        IconMakerDialog(self.root, self, lambda p: (self.icon_path.set(p), self.icon_label.config(
            text=f"✓ {os.path.basename(p)}", foreground="green")))

    def _is_virtual_env_path(self, python_path):
        """判断路径是否属于虚拟环境目录"""
        if not python_path:
            return False
        indicators = ['common_venv']
        for ind in indicators:
            if ind in python_path.lower():
                return True
        return False


    def _select_python(self):
        p = filedialog.askopenfilename(title="选择Python", filetypes=[("Python", "python.exe"), ("All", "*.*")],
                                      initialdir="C:\\" if sys.platform == "win32" else "/usr/bin/")
        if p:
            self.custom_python_path.set(p.lower())
            self._save_python_config()
            self._test_python()
            self._update_python_btn()
            self._update_python_btn()

    def _test_python(self):
        """测试Python版本（后台执行）"""
        self.clear_log()
        p = self._get_python()

        # 打包环境：拒绝不以 python.exe 结尾的路径，拒绝 exe 自身
        if getattr(sys, 'frozen', False):
            if not p:
                self.root.after(0, lambda: self.py_label.config(text="请手动选择 python.exe路径", foreground="orange"))
                return
            if not p.lower().endswith('python.exe'):
                self.root.after(0,
                                lambda: self.py_label.config(text="路径无效（需以 python.exe 结尾）", foreground="red"))
                return
            # 关键：拒绝 exe 自身
            if os.path.abspath(p).lower() == os.path.abspath(sys.executable).lower():
                self.root.after(0, lambda: self.py_label.config(text="不能使用程序自身", foreground="red"))
                self.safe_log("❌ 检测到路径指向程序自身，已拒绝")
                return

        if not p or not os.path.exists(p):
            self.root.after(0, lambda: self.py_label.config(text="未找到Python", foreground="red"))
            return

        def test():
            try:
                r = subprocess.run([p, "--version"], capture_output=True, text=True,
                                   timeout=5, startupinfo=get_startupinfo() if sys.platform == "win32" else None)
                if r.returncode == 0:
                    v = (r.stdout or r.stderr).strip().replace("Python ", "")
                    r2 = subprocess.run([p, "-m", "PyInstaller", "--version"], capture_output=True,
                                        text=True, timeout=5,
                                        startupinfo=get_startupinfo() if sys.platform == "win32" else None)
                    pi = r2.stdout.strip() if r2.returncode == 0 else "未安装"
                    status = f"{v} | {pi}"
                    color = "green" if r2.returncode == 0 else "orange"
                    self.root.after(0, lambda: self.py_label.config(text=status, foreground=color))
                    if r2.returncode == 0:
                        self.root.after(0, lambda: self._save_python_path_to_cache(p))
                else:
                    self.root.after(0, lambda: self.py_label.config(text="无效环境", foreground="red"))
            except Exception as e:
                self.root.after(0, lambda: self.py_label.config(text="测试失败", foreground="red"))
                self.safe_log(f"❌ 测试失败: {e}")
        self.safe_log(f"✅ 自动找到 Python: {p}")
        threading.Thread(target=test, daemon=True).start()

    def _save_python_path_to_cache(self, path):
        """保存Python路径到缓存并更新界面"""
        if not path or not os.path.exists(path):
            return

        # 统一扩展名为小写
        name, ext = os.path.splitext(path)
        if ext:
            ext = ext.lower()
        path = name + ext

        # 更新变量
        self.custom_python_path.set(path)
        self.custom_python_path.trace_add('write', self._on_python_path_change)
        # 保存到全局缓存
        self.global_cache['python'] = {
            'path': path,
            'timestamp': time.time()
        }
        self._save_global_cache()

        # 更新界面输入框
        if hasattr(self, 'python_path_entry'):
            try:
                self.python_path_entry.delete(0, tk.END)
                self.python_path_entry.insert(0, path)
            except:
                pass

        #self.safe_log(f"📁 已保存Python路径到缓存: {path}")

    def _clear_python(self):
        """智能清除/切换：如果是 common_venv 则切换，否则清除"""
        self.clear_log()
        if self.clear_switch_python_btn.cget("text") == "🔄切换":
            # 切换逻辑：弹出文件选择对话框，让用户自由选择 Python 解释器
            new_py = filedialog.askopenfilename(
                title="选择 Python 解释器（可选择虚拟环境或系统 Python）",
                filetypes=[("Python", "python.exe"), ("All", "*.*")]
            )
            if new_py and os.path.exists(new_py):
                self._set_python_path(new_py)
                self.safe_log(f"✅ 已切换到: {new_py}")
            else:
                self.safe_log("⚠️ 未选择，切换取消")
        else:
            # 清除逻辑
            self.custom_python_path.set("")
            if hasattr(self, 'python_path_entry'):
                self.python_path_entry.delete(0, tk.END)
            if 'python' in self.global_cache:
                del self.global_cache['python']
                self._save_global_cache()
            self.py_label.config(text="")
            self.safe_log("🗑 已清除Python路径")
        self._update_python_btn()

    def _select_upx(self):
        file_path = filedialog.askopenfilename(
            title="选择UPX可执行文件",
            filetypes=[("UPX", "upx.exe"), ("所有文件", "*.*")],
            initialdir=self.current_dir
        )
        if file_path:
            self.upx_path.set(file_path)
            self._save_upx_config()
            self._upx_auto_find_done = True  # 标记已手动指定，不再自动查找
            self.safe_log(f"✅ 已手动指定UPX: {file_path}")
        else:
            self.safe_log("⚠️ 未选择UPX文件")

    def _find_upx_path(self):
        """查找 UPX 路径（使用统一缓存）"""
        # 从统一缓存读取
        cached = self.global_cache.get('upx', {})
        cache_time = cached.get('timestamp', 0)
        if time.time() - cache_time < 2592000:  # 30天有效
            upx_path = cached.get('path', '')
            if upx_path and os.path.exists(upx_path):
                return upx_path

        # 实际查找
        upx_path = self._find_tool('upx')
        if upx_path:
            upx_dir = os.path.dirname(upx_path)
            # 保存到统一缓存
            self.global_cache['upx'] = {'path': upx_dir, 'timestamp': time.time()}
            self._save_global_cache()
            return upx_dir
        return None

    def _save_upx_config(self):
        """保存UPX路径到全局缓存"""
        self.global_cache['upx'] = {
            'path': self.upx_path.get(),
            'timestamp': time.time()
        }
        self._save_global_cache()

    def _load_upx_config(self):
        """加载UPX路径从全局缓存"""
        upx_data = self.global_cache.get('upx', {})
        upx_path = upx_data.get('path', '')
        if upx_path and os.path.exists(upx_path):
            self.upx_path.set(upx_path)
            if hasattr(self, 'upx_entry'):
                self.upx_entry.delete(0, tk.END)
                self.upx_entry.insert(0, upx_path)
            return True
        return False

    def _add_exclude(self):
        e = self.exclude_var.get().strip()
        if e and e not in self.exclude_list:
            self.exclude_list.append(e)
            self.exclude_listbox.insert(tk.END, e)
            self.exclude_var.set("")
            self._update_exclude_count()

    def _remove_exclude(self):
        sel = self.exclude_listbox.curselection()
        if sel:
            self.exclude_list.pop(sel[0])
            self.exclude_listbox.delete(sel[0])
            self._update_exclude_count()

    def _clear_excludes(self):
        if self.exclude_list and messagebox.askyesno("确认", f"清空 {len(self.exclude_list)} 个排除项？"):
            self.exclude_list.clear()
            self.exclude_listbox.delete(0, tk.END)
            self._update_exclude_count()

    def _open_exclude(self):
        used = self._analyze_used()
        installed = self._get_installed()
        ExcludeSelectorDialog(self.root, used, installed, self.exclude_list, self._update_exclude_list)

    def _add_recommended(self):
        rec = ["matplotlib", "numpy", "pandas", "scipy", "tensorflow", "torch", "keras",
               "opencv-python", "cv2", "django", "flask", "fastapi", "selenium", "scrapy",
               "pytest", "nose", "PyQt5", "PyQt6", "PySide2", "PySide6"]
        added = sum(1 for r in rec if r not in self.exclude_list and (self.exclude_list.append(r) or self.exclude_listbox.insert(tk.END, r) or True))
        self._update_exclude_count()
        if added: self.safe_log(f"📦 已添加 {added} 个推荐排除项")

    def _update_exclude_list(self, new):
        self.exclude_list = list(new)
        self.exclude_listbox.delete(0, tk.END)
        for e in self.exclude_list:
            self.exclude_listbox.insert(tk.END, e)
        self._update_exclude_count()

    def _update_exclude_count(self):
        """计数器1：排除选项 - 显示排除模块数量"""
        n = len(self.exclude_list)
        self.exclude_count.config(text=f"({n})")
        self.exclude_num.config(text=f"({n})",
                                foreground=("gray" if n == 0 else "green" if n <= 3 else "orange" if n <= 6 else "red"))

    def _add_hidden(self):
        m = self.hidden_var.get().strip()
        if m and m not in self.hidden_imports_list:
            self.hidden_imports_list.append(m)
            self.hidden_listbox.insert(tk.END, m)
            self.hidden_var.set("")
            self._update_hidden_count()

    def _remove_hidden(self):
        sel = self.hidden_listbox.curselection()
        if sel:
            self.hidden_imports_list.pop(sel[0])
            self.hidden_listbox.delete(sel[0])
            self._update_hidden_count()

    def _clear_hidden(self):
        self.hidden_imports_list.clear()
        self.hidden_listbox.delete(0, tk.END)
        self._update_hidden_count()

    def _add_recommended_hidden(self):
        if not self.analyzed_modules:
            # 如果还没有分析过，先分析再添加
            messagebox.showinfo("提示", "正在分析依赖...")
            self._analyze_used(show_log=True, auto_add=True)
            return

        added = sum(1 for m in self.analyzed_modules
                    if m not in self.hidden_imports_list
                    and (self.hidden_imports_list.append(m) or self.hidden_listbox.insert(tk.END, m) or True))
        if added:
            self._update_hidden_count()
            self.safe_log(f"✓ 已添加 {added} 个模块到隐藏导入")
            self.rec_label.config(text=f"已添加{added}个", foreground="green")
        else:
            self.safe_log("✅ 所有模块已在隐藏导入列表中")

    def _update_hidden_count(self):
        """左侧依赖导入列表变化时，更新自动导入计数器"""
        n = len(self.hidden_imports_list)
        self.hidden_num.config(text=f"({n})", foreground="green" if n > 0 else "gray")
        # 更新自动导入计数器
        self._update_auto_import_count()

    def _analyze_deps(self):
        f = self.input_path.get()
        if not f or not os.path.exists(f):
            messagebox.showwarning("提示", "请先选择有效的Python文件")
            return
        self.safe_log("="*50)
        self.safe_log("🔍 分析代码依赖...")
        missing = self._analyze_missing()
        if missing:
            self.safe_log(f"❌ 缺失: {len(missing)} 个")
            for m in missing[:10]:
                self.safe_log(f"   • {m}")
            if len(missing)>10:
                self.safe_log(f"   ... 还有 {len(missing)-10} 个")
            if messagebox.askyesno("安装依赖", f"发现 {len(missing)} 个缺失模块，是否一键安装？"):
                self._batch_install(missing)
            for m in missing:
                if m not in self.hidden_imports_list:
                    self.hidden_imports_list.append(m)
                    self.hidden_listbox.insert(tk.END, m)
            self._update_hidden_count()
        else:
            self.safe_log("🎉 所有依赖已安装！")
            self.rec_label.config(text="无需安装", foreground="green")

    def _batch_install(self, packages):
        py = self._get_python()
        if not py:
            self.safe_log("❌ 未找到Python环境")
            return
        success = fail = 0
        for i, pkg in enumerate(packages):
            self.safe_log(f"📦 安装 {pkg} ({i+1}/{len(packages)})...")
            try:
                r = subprocess.run([py, "-m", "pip", "install", pkg, "-i", MIRROR],
                                capture_output=True, text=True, timeout=120, startupinfo=get_startupinfo())
                if r.returncode == 0:
                    success += 1
                    self.safe_log(f"   ✅ {pkg} 安装成功")
                else:
                    fail += 1
                    self.safe_log(f"   ❌ {pkg} 安装失败")
            except Exception as e:
                fail += 1
                self.safe_log(f"   ❌ {pkg} 异常: {e}")
        self.safe_log(f"📊 完成: 成功 {success}, 失败 {fail}")
        self.installed_packages = None
        if success > 0:
            messagebox.showinfo("完成", f"成功安装 {success} 个包")

    def _auto_install(self):
        f = self.input_path.get()
        if not f:
            messagebox.showwarning("提示", "请先选择Python文件")
            return
        missing = self._analyze_missing()
        if not missing:
            messagebox.showinfo("完成", "所有依赖已安装！")
            return
        if messagebox.askyesno("安装依赖", f"发现 {len(missing)} 个缺失包，是否从清华源安装？"):
            self._batch_install(missing)

    def _export_req(self):
        py = self._get_python()
        if not py: return
        dialog = tk.Toplevel(self.root)
        dialog.title("导出依赖")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="选择导出类型:", font=("Arial", 12, "bold")).pack(pady=10)
        var = tk.StringVar(value="project")
        ttk.Radiobutton(dialog, text="项目依赖", variable=var, value="project").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(dialog, text="环境依赖", variable=var, value="env").pack(anchor=tk.W, padx=20)
        bf = ttk.Frame(dialog)
        bf.pack(fill=tk.X, pady=10)
        def do_export():
            dialog.destroy()
            if var.get() == "project":
                out = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"), "requirements.txt")
                os.makedirs(os.path.dirname(out), exist_ok=True)
                self._do_export_project(py, out)
            else:
                out = os.path.join(self.current_dir, "requirements_env.txt")
                self._do_export_env(py, out)
        ModernButton(bf, text="确定", command=do_export, width=10).pack(side=tk.RIGHT, padx=5)
        ModernButton(bf, text="取消", command=dialog.destroy, width=10).pack(side=tk.RIGHT, padx=5)

    def _do_export_env(self, py, path):
        try:
            r = subprocess.run([py, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=30, startupinfo=get_startupinfo())
            if r.returncode == 0:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(r.stdout)
                self.safe_log(f"✅ 环境依赖已导出: {path}")
                messagebox.showinfo("成功", f"已导出到:\n{path}")
            else:
                self.safe_log(f"❌ 导出失败")
        except Exception as e:
            self.safe_log(f"❌ 导出异常: {e}")

    def _do_export_project(self, py, path):
        f = self.input_path.get()
        if not f or not os.path.exists(f):
            return
        try:
            with open(f, "r", encoding="utf-8") as fobj:
                imports = self._parse_imports(fobj.read())
            r = subprocess.run([py, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=30, startupinfo=get_startupinfo())
            installed = {}
            for line in r.stdout.strip().split("\n"):
                if "==" in line:
                    pkg, ver = line.split("==", 1)
                    installed[pkg.lower()] = f"{pkg}=={ver}"
            pkgs = []
            for imp in imports:
                il = imp.lower()
                if il in installed:
                    pkgs.append(installed[il])
                elif imp in MODULE_TO_PACKAGE:
                    pn = MODULE_TO_PACKAGE[imp].lower()
                    if pn in installed:
                        pkgs.append(installed[pn])
            pkgs = sorted(set(pkgs))
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(pkgs))
            self.safe_log(f"✅ 项目依赖已导出: {path} ({len(pkgs)} 个包)")
            messagebox.showinfo("成功", f"已导出 {len(pkgs)} 个包到:\n{path}")
        except Exception as e:
            self.safe_log(f"❌ 导出失败: {e}")

    def _import_req(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("导入依赖")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        ttk.Label(dialog, text="选择导入类型:", font=("Arial", 12, "bold")).pack(pady=10)
        var = tk.StringVar(value="project")
        ttk.Radiobutton(dialog, text="项目依赖", variable=var, value="project").pack(anchor=tk.W, padx=20)
        ttk.Radiobutton(dialog, text="环境依赖", variable=var, value="env").pack(anchor=tk.W, padx=20)
        bf = ttk.Frame(dialog)
        bf.pack(fill=tk.X, pady=10)
        def do_import():
            dialog.destroy()
            if var.get() == "project":
                path = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"), "requirements.txt")
            else:
                path = os.path.join(self.current_dir, "requirements_env.txt")
            self._do_import(path)
        ModernButton(bf, text="确定", command=do_import, width=10).pack(side=tk.RIGHT, padx=5)
        ModernButton(bf, text="取消", command=dialog.destroy, width=10).pack(side=tk.RIGHT, padx=5)

    def _do_import(self, path):
        if not os.path.exists(path):
            messagebox.showerror("错误", f"未找到文件:\n{path}")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        except Exception as e:
            messagebox.showerror("错误", f"读取失败: {e}")
            return
        if not lines:
            messagebox.showwarning("警告", "文件中没有有效包名")
            return
        installed = self._get_installed()
        need = []
        for line in lines:
            pkg = line.split("==")[0].split(">=")[0].split("<=")[0].strip().lower()
            if pkg not in installed:
                need.append(line)
        self.safe_log(f"📊 需要安装: {len(need)}/{len(lines)}")
        if not need:
            messagebox.showinfo("完成", "所有依赖都已安装")
            return
        if messagebox.askyesno("确认安装", f"发现 {len(need)} 个未安装包，是否安装？"):
            self._batch_install(need)

    def _stop_venv(self):
        """停止虚拟环境创建"""
        self.stop_venv = True
        if self.venv_process and self.venv_process.poll() is None:
            self.venv_process.terminate()
            self.safe_log("🛑 用户停止虚拟环境创建")
        # 恢复打包按钮
        self.pack_btn.config(text="▶开始打包", command=self._toggle_pack)
        
    def _manage_venv(self, silent=False):
        f = self.input_path.get()
        if not f or not os.path.exists(f):
            if not silent:
                messagebox.showwarning("提示", "请先选择Python文件")
            return
        if not silent:
            if not messagebox.askyesno("虚拟环境", "将创建/更新虚拟环境，是否继续？"):
                return
        # 重置停止标志
        self.stop_venv = False
    
        # 显示停止按钮
        self.pack_btn.config(text="⏹停止创建", command=self._stop_venv)

        # 显示彩色进度条
        self.status_start("虚拟环境", color="blue")
        threading.Thread(target=self._do_manage_venv, daemon=True).start()

    def _get_site_packages_path(self, python_path):
        """根据 Python 路径获取 site-packages 目录（跨平台）"""
        if not python_path:
            return None

        python_dir = os.path.dirname(python_path)

        if sys.platform == "win32":
            # Windows
            if python_dir.endswith("Scripts"):
                base_dir = os.path.dirname(python_dir)
            else:
                base_dir = python_dir
            site_packages = os.path.join(base_dir, "Lib", "site-packages")
        else:
            # Linux/macOS
            if python_dir.endswith("bin"):
                base_dir = os.path.dirname(python_dir)
            else:
                base_dir = python_dir

            # 获取 Python 版本号（使用 subprocess 获取真实版本）
            try:
                r = subprocess.run([python_path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
                                   capture_output=True, text=True, timeout=5,
                                   startupinfo=get_startupinfo() if sys.platform == "win32" else None)
                if r.returncode == 0:
                    py_ver = r.stdout.strip()
                else:
                    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
            except:
                py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"

            # 尝试多个可能的路径
            candidates = [
                os.path.join(base_dir, "lib", f"python{py_ver}", "site-packages"),
                os.path.join(base_dir, "lib", f"python{py_ver}", "dist-packages"),
                os.path.join(base_dir, "lib64", f"python{py_ver}", "site-packages"),
                os.path.join(base_dir, "local", "lib", f"python{py_ver}", "site-packages"),
            ]

            for candidate in candidates:
                if os.path.exists(candidate):
                    return candidate

        # 检查路径是否存在
        if os.path.exists(site_packages):
            return site_packages

        # 备选路径
        alt_site = site_packages.replace("site-packages", "dist-packages")
        if os.path.exists(alt_site):
            return alt_site

        return None

    def _is_packed_exe(self):
        """判断是否在打包的 exe 中运行"""
        return getattr(sys, 'frozen', False) or hasattr(sys, '_MEIPASS') or getattr(sys, 'nuitka_is_frozen', False)

    def _install_to_venv_from_main(self, venv_python, venv_dir, modules, progress_callback=None):
        """从主环境复制模块到虚拟环境（支持模块名和包名）"""
        self.safe_log("=" * 40)
        self.safe_log("🔍 开始安装依赖")
        # 获取主环境的 Python 路径和 site-packages
        main_py = self._get_python()
        self.safe_log(f"   venv_dir: {venv_dir}")
        self.safe_log(f"   modules: {modules}")

        if not main_py:
            #self.safe_log("❌ 未找到主环境 Python")
            return [], modules

        main_site = self._get_site_packages_path(main_py)
        venv_site = self._get_site_packages_path(venv_python)

        #self.safe_log(f"   主环境 Python: {main_py}")
        #self.safe_log(f"   主环境 site-packages: {main_site}")
        #self.safe_log(f"   虚拟环境 site-packages: {venv_site}")

        if not main_site or not os.path.exists(main_site):
            #self.safe_log("❌ 主环境 site-packages 不存在")
            return [], modules

        os.makedirs(venv_site, exist_ok=True)

        success_list = []
        fail_list = []

        # ========== 提前获取目录列表 ==========
        main_site_items = list(os.listdir(main_site))  # 只调用一次
        total = len(modules)

        for idx, module in enumerate(modules):
            # 更新进度 (30% 到 60% 之间)
            if progress_callback and total > 0:
                progress = 30 + int((idx / total) * 30)
                progress_callback(progress, f"安装依赖 ({idx+1}/{total})")

            # 获取可能的包名（支持大小写、连字符、下划线等）
            possible_names = [
                module,
                MODULE_TO_PACKAGE.get(module, module),
                module.lower(),
                module.lower().replace('-', '_'),
                module.lower().replace('_', '-'),
                module.title(),
            ]
            possible_names = list(set(possible_names))  # 去重

            self.safe_log(f"📦 处理模块: {module} (可能的包名: {possible_names[:3]})")

            copied = False
            for item in main_site_items:  # 使用缓存的列表
                item_lower = item.lower()
                for pkg_name in possible_names:
                    pkg_lower = pkg_name.lower()
                    # 匹配包名或 dist-info 目录
                    if (item_lower == pkg_lower or
                            item_lower.startswith(pkg_lower + '-') or
                            item_lower == pkg_lower.replace('-', '_') or
                            (item_lower.endswith('.dist-info') and pkg_lower in item_lower)):
                        src = os.path.join(main_site, item)
                        dst = os.path.join(venv_site, item)
                        self.safe_log(f"   找到匹配项: {item}")
                        try:
                            if os.path.isdir(src):
                                shutil.copytree(src, dst, dirs_exist_ok=True)
                            else:
                                shutil.copy2(src, dst)
                            self.safe_log(f"   ✅ 安装成功: {item}")
                            success_list.append(module)
                            copied = True
                            break
                        except Exception as e:
                            self.safe_log(f"   ❌ 安装失败: {e}")
                    if copied:
                        break
                if copied:
                    break

            if not copied:
                self.safe_log(f"   ⚠️ 未找到匹配项: {module}")
                fail_list.append(module)

        self.safe_log(f"📊 安装结果: 成功 {len(success_list)}, 失败 {len(fail_list)}")
        self.safe_log("=" * 40)
        return success_list, fail_list

    def _fast_rmtree(self, path):
        """快速删除目录（跨平台）"""
        if not os.path.exists(path):
            return

        try:
            if sys.platform == "win32":
                # Windows: 使用 rmdir /s /q
                subprocess.run(f'rmdir /s /q "{path}"', shell=True, capture_output=True, timeout=30, startupinfo=get_startupinfo())
            else:
                # Linux/Mac: 使用 rm -rf
                subprocess.run(['rm', '-rf', path], capture_output=True, timeout=30)
        except:
            # 失败则用普通方式
            try:
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass

    def _rename_and_delete(self, path):
        """重命名后异步删除（跨平台，瞬间完成）"""
        if not os.path.exists(path):
            return False

        try:
            # 生成临时名称（跨平台兼容）
            import uuid
            temp_name = f"{path}_deleting_{uuid.uuid4().hex[:8]}"

            # 跨平台重命名
            os.rename(path, temp_name)

            # 后台异步删除重命名后的文件夹
            def background_delete():
                try:
                    # 等待一下再删除，避免文件锁定（跨平台）
                    import time
                    time.sleep(0.5)
                    self._fast_rmtree(temp_name)
                except Exception as e:
                    # 如果删除失败，记录但不影响主流程
                    if self.safe_log:
                        self.safe_log(f"⚠️ 后台清理失败: {e}")

            threading.Thread(target=background_delete, daemon=True).start()
            return True

        except Exception as e:
            # 重命名失败（可能是跨分区），直接删除
            if self.safe_log:
                self.safe_log(f"⚠️ 重命名失败，直接删除: {e}")
            self._fast_rmtree(path)
            return False

    def _do_manage_venv(self):
        try:
            tool_dir = self.current_dir
            venv_dir = os.path.join(tool_dir, "common_venv")
            py = self._get_python()
            if not py:
                self.safe_log("❌ 未找到系统 Python，无法创建虚拟环境")
                self.status_finish("失败")
                return

            self.safe_log("=" * 50)
            self.safe_log(f"📦 管理虚拟环境: {venv_dir}")

            # 使用重命名删除旧环境（瞬间完成，跨平台）
            if os.path.exists(venv_dir):
                if self.stop_venv:
                    self.safe_log("🛑 用户取消操作")
                    self.status_finish("已取消")
                    return
                self.safe_log("🗑️删除旧环境...")
                self.status_set_target(10, "删除旧环境", color="orange")
                self._rename_and_delete(venv_dir)

            if self.stop_venv:
                self.safe_log("🛑 用户取消操作")
                self.status_finish("已取消")
                return

            self.status_set_target(20, "创建虚拟环境", color="blue")
            self.safe_log("🔧 创建虚拟环境...")

            # 创建虚拟环境（跨平台）
            self.venv_process = subprocess.Popen(
                [py, "-m", "venv", venv_dir],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
                startupinfo=get_startupinfo() if sys.platform == "win32" else None
            )

            # 等待进程完成，同时检查停止标志
            if self.venv_process:
                while self.venv_process.poll() is None:
                    if self.stop_venv:
                        self.venv_process.terminate()
                        self.safe_log("🛑 用户停止虚拟环境创建")
                        self.venv_process = None
                        self.status_finish("已停止")
                        return
                    time.sleep(0.2)

                if self.venv_process.returncode != 0:
                    error_msg = self.venv_process.stderr.read() if self.venv_process.stderr else "未知错误"
                    self.safe_log(f"❌ 创建失败: {error_msg}")
                    self.venv_process = None
                    self.status_finish("创建失败")
                    return

            self.venv_process = None
            self.safe_log("✅ 虚拟环境创建成功")

            # 获取虚拟环境中的 Python 路径（跨平台）
            if sys.platform == "win32":
                venv_py = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_py = os.path.join(venv_dir, "bin", "python")

            # ========== 合并需要安装的模块 ==========
            analyzed = self.analyzed_modules if self.analyzed_modules else []
            manual = self.hidden_imports_list if self.hidden_imports_list else []
            all_modules = list(set(analyzed + manual))

            if all_modules:
                self.safe_log(f"📦 需要安装 {len(all_modules)} 个模块: {all_modules}")
                self.status_set_target(30, f"准备安装依赖 (0/{len(all_modules)})", color="purple")

                # 清空并重新填充隐藏导入列表
                self.hidden_imports_list.clear()
                self.hidden_listbox.delete(0, tk.END)
                for pkg in all_modules:
                    mod = PACKAGE_TO_MODULE.get(pkg, pkg)
                    if mod not in self.hidden_imports_list:
                        self.hidden_imports_list.append(mod)
                        self.hidden_listbox.insert(tk.END, mod)
                self._update_hidden_count()

                # 定义进度回调函数
                def update_progress(progress, text):
                    self.status_set_target(progress, text, color="purple")

                # 调用复制/安装方法（传入进度回调）
                success_list, fail_list = self._install_to_venv_from_main(
                    venv_py, venv_dir, all_modules, progress_callback=update_progress
                )
                success = len(success_list)
                fail = len(fail_list)

                self.status_set_target(60, f"复制完成: 成功 {success}, 失败 {fail}", color="green")

                # 对失败的包使用 pip 安装
                if fail_list:
                    self.safe_log(f"📦 尝试 pip 安装 {len(fail_list)} 个失败的包...")
                    total = len(fail_list)
                    new_fail_list = []

                    for i, pkg in enumerate(fail_list):
                        if self.stop_venv:
                            self.safe_log("🛑 用户取消安装")
                            self.status_finish("已取消")
                            return

                        pct = 60 + int((i + 1) / total * 35)
                        self.status_set_target(pct, f"pip 安装 {pkg} ({i+1}/{total})", color="orange")
                        self.safe_log(f"📥 pip 安装 {pkg} ({i+1}/{total})...")
                        try:
                            r = subprocess.run([venv_py, "-m", "pip", "install", pkg, "-i", MIRROR],
                                               capture_output=True, text=True, timeout=180,
                                               startupinfo=get_startupinfo() if sys.platform == "win32" else None)
                            if r.returncode == 0:
                                success += 1
                                self.safe_log(f"   ✅ {pkg} 安装成功")
                            else:
                                fail += 1
                                new_fail_list.append(pkg)
                                self.safe_log(f"   ❌ {pkg} 安装失败")
                        except Exception as e:
                            fail += 1
                            new_fail_list.append(pkg)
                            self.safe_log(f"   ❌ {pkg} 异常: {e}")

                    fail_list = new_fail_list
                    self.status_set_target(95, f"pip 安装完成: 成功 {success}, 失败 {len(fail_list)}", color="green")
                    self.safe_log(f"📊 最终: 成功 {success}, 失败 {len(fail_list)}")
                else:
                    self.status_set_target(95, "所有依赖安装成功", color="green")

            else:
                self.safe_log("✅ 未发现需要安装的依赖")
                self.status_set_target(95, "无依赖需要安装", color="green")

            self.status_set_target(100, "完成", color="green")
            self.safe_log(f"✅ 虚拟环境就绪: {venv_dir}")
            self.root.after(50, lambda: self.status_finish("就绪"))

        except Exception as e:
            self.safe_log(f"❌ 管理失败: {e}")
            self.status_set_target(100, "管理失败", color="red")
            self.status_finish("失败")
        finally:
            # 恢复按钮
            self.root.after(0, lambda: self.pack_btn.config(text="▶开始打包", command=self._toggle_pack))
            self.stop_venv = False
            self.venv_process = None

    def _launch_auto(self):
        try:
            subprocess.Popen(["auto-py-to-exe"], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
            self.safe_log("已启动 auto-py-to-exe")
        except FileNotFoundError:
            if messagebox.askyesno("未安装", "auto-py-to-exe 未安装，是否安装？"):
                subprocess.run([self._get_python(), "-m", "pip", "install", "auto-py-to-exe"], check=True)
                self.safe_log("安装完成，请再次点击")

    def _select_data_src(self):
        f = filedialog.askopenfilename()
        if f:
            self.data_src.set(f)
            if not self.data_tgt.get():
                self.data_tgt.set(os.path.basename(f))

    def _add_data(self):
        s = self.data_src.get().strip()
        t = self.data_tgt.get().strip()
        if not s or not os.path.exists(s):
            messagebox.showwarning("提示", "请选择有效的源文件")
            return
        if not t:
            t = os.path.basename(s)
        if (s, t) not in self.data_files_list:
            self.data_files_list.append((s, t))
            self.data_listbox.insert(tk.END, f"{os.path.basename(s)} -> {t}")
            self.data_src.set("")
            self.data_tgt.set("")
            self._update_data_count()

        self._update_data_count()

    def _remove_data(self):
        sel = self.data_listbox.curselection()
        if sel:
            self.data_files_list.pop(sel[0])
            self.data_listbox.delete(sel[0])
            self._update_data_count()
        self._update_data_count()

    def _clear_data(self):
        self.data_files_list.clear()
        self.data_listbox.delete(0, tk.END)
        self._update_data_count()

    def _update_data_count(self):
        """计数器3：依赖数据 - 显示右侧数据文件列表数量"""
        n = len(self.data_files_list)
        self.adv_count.config(text=f"({n})", foreground="green" if n > 0 else "gray")

    def _open_proj_dir(self):
        out = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"))
        if not os.path.exists(out):
            if messagebox.askyesno("目录不存在", f"创建并打开?\n{out}"):
                os.makedirs(out, exist_ok=True)
            else:
                return
        if sys.platform == "win32":
            os.startfile(out)
        elif sys.platform == "darwin":
            subprocess.run(["open", out])
        else:
            subprocess.run(["xdg-open", out])

    def _scan_data(self):
        f = self.input_path.get()
        if not f or not os.path.exists(f):
            messagebox.showwarning("提示", "请先选择Python文件")
            return
        out = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"))
        if not os.path.exists(out):
            os.makedirs(out, exist_ok=True)
        exts = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".txt", ".md",
                ".csv", ".db", ".sqlite", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico"}
        added = 0
        for item in os.listdir(out):
            p = os.path.join(out, item)
            if os.path.isdir(p) or p.endswith(".py"):
                continue
            ext = os.path.splitext(item)[1].lower()
            if ext in exts or "config" in item.lower():
                if not any(s == p for s, t in self.data_files_list):
                    self.data_files_list.append((p, item))
                    self.data_listbox.insert(tk.END, f"{item} -> {item}")
                    added += 1
                    self.safe_log(f"  ✓ 添加: {item}")
        self._update_data_count()
        if added:
            messagebox.showinfo("扫描完成", f"新添加 {added} 个数据文件")
        else:
            self.safe_log("ℹ️ 未发现新数据文件")

    def _on_data_drop(self, event):
        files = event.data
        if sys.platform == "win32":
            files = files.strip("{}").replace('"', "").split()[0]
        else:
            files = files.split()[0]
            if files.startswith("file://"):
                files = files[7:]
        if files and os.path.exists(files):
            t = os.path.basename(files)
            if (files, t) not in self.data_files_list:
                self.data_files_list.append((files, t))
                self.data_listbox.insert(tk.END, f"{os.path.basename(files)} -> {t}")
                self._update_data_count()

    def _on_log_drop(self, event):
        self._on_data_drop(event)

    def _clear_all(self):
        self.clear_hidden_imports()
        self.clear_data_files()
        self.clear_excludes()
        self.analyzed_modules = []
        self.rec_label.config(text="")
        self.icon_path.set("")
        self.icon_label.config(text="")
        # 更新计数显示
        self._update_hidden_count()
        self._update_data_count()
        self._update_exclude_count()

    def clear_hidden_imports(self):
        self.hidden_imports_list.clear()
        self.hidden_listbox.delete(0, tk.END)
        self._update_hidden_count()

    def clear_data_files(self):
        self.data_files_list.clear()
        self.data_listbox.delete(0, tk.END)
        self._update_data_count()

    def clear_excludes(self):
        self.exclude_list.clear()
        self.exclude_listbox.delete(0, tk.END)
        self._update_exclude_count()

    def clear_log(self):
        try:
            if self.log_text and self.log_text.winfo_exists():
                self.log_text.delete(1.0, tk.END)
        except: pass

    # ==================== 打包控制 ====================
    def _toggle_pack(self):
        if self.pack_btn["text"] == "▶开始打包":
            self._start_pack()
        else:
            self._stop_pack()

    def _start_pack(self):
        # 关闭可能还开着的弹窗
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                title = widget.title()
                if "版本信息" in title or "图标制作" in title:
                    widget.destroy()

        self.clear_log()
        if self.exclude_visible:
            self._toggle_exclude()
        if self.adv_visible:
            self._toggle_advanced()

        f = self.input_path.get()

        # ========== 统一处理防多开注入 ==========
        if getattr(self, 'multi_instance_enabled', False):
            self.safe_log("🔒 防多开已启用，正在注入代码...")
            if self.inject_single_instance(f):
                self.safe_log("✅ 防多开代码注入成功")
                self._injected_for_pack = True  # 标记已注入，打包完成后需要移除
            else:
                self.safe_log("⚠️ 防多开代码注入失败，继续打包...")

        # ========== 工作目录注入 ==========
        is_self_packing = False
        if not getattr(sys, 'frozen', False) and self.workdir_enabled and not is_self_packing:
            if not getattr(sys, 'frozen', False) and not is_self_packing:
                if self._inject_workdir_code(f):
                    self._workdir_injected = True

        # 编译日期注入（仅当是自己时）
        if f and os.path.abspath(f) == os.path.abspath(__file__):
            self._inject_build_date(f)

        self.start_time = time.time()
        self.pack_btn.config(text="⏹停止打包")
        self.pack_btn.normal_bg = "#dc4555"
        self.pack_btn.hover_bg = "#ec5565"
        self.pack_btn.configure(bg="#dc4555")
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.progress_label.pack(side=tk.LEFT, padx=5)
        self.timer_label.pack(side=tk.LEFT, padx=10)
        self.progress_var.set(0)
        self.progress_label.config(text="0% - 准备中...")
        self.timer_label.config(text="00:00")
        self._update_timer()

        out = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"))
        if os.path.exists(out):
            try:
                shutil.rmtree(out)
                self.safe_log("🗑️已删除旧输出")
            except:
                pass
        for d in ["build_temp", "__pycache__"]:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except:
                    pass

        threading.Thread(target=self._run_package, daemon=True).start()

    def _update_timer(self):
        if self.start_time and self.pack_btn["text"] == "⏹停止打包":
            e = int(time.time() - self.start_time)
            self.timer_label.config(text=f"{e//60:02d}:{e%60:02d}")
            self.root.after(1000, self._update_timer)

    def _stop_pack(self):
        if self.process and self.process is not None and self.process.poll() is None:
            self.process.terminate()
            self.safe_log("🛑 用户停止打包")

        # 同时停止虚拟环境创建
        self.stop_venv = True
        if self.venv_process and self.venv_process.poll() is None:
            self.venv_process.terminate()
            self.safe_log("🛑 用户停止虚拟环境创建")

        self._cleanup_injected_codes()
        self._pack_finish()

    def _pack_finish(self):
        # 清理临时版本文件
        if self._temp_version_file and os.path.exists(self._temp_version_file):
            try:
                os.remove(self._temp_version_file)
                self.safe_log("🗑已删除版本文件")
            except Exception as e:
                self.safe_log(f"⚠️ 删除版本文件失败: {e}")
            self._temp_version_file = None
        # ========== 打包完成后移除注入代码 ==========
        self._cleanup_injected_codes()

        if self.start_time:
            e = int(time.time() - self.start_time)
            self.safe_log(f"⏱️ 总耗时: {e // 60:02d}:{e % 60:02d}")
            self.start_time = None

        self.pack_btn.config(text="▶开始打包")
        self.pack_btn.normal_bg = "#4a8dd9"
        self.pack_btn.hover_bg = "#5a9de9"
        self.pack_btn.configure(bg="#4a8dd9")
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        self.timer_label.pack_forget()
        self.progress_var.set(0)
        self.progress_label.config(text="")
        self.timer_label.config(text="00:00")

    def _run_package(self):
        try:
            success = self._package_app()
            if success:
                self.safe_log("✅ 打包成功")
            else:
                self.safe_log("❌ 打包失败")
        except Exception as e:
            self.safe_log(f"❌ 打包异常: {e}")
            import traceback
            self.safe_log(traceback.format_exc())
        finally:
            self._cleanup_injected_codes()
            self.root.after(0, self._pack_finish)

    def _detect_gui(self, target):
        try:
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
            if "tkinter" in content and ("import tkinter" in content or "from tkinter" in content or "Tk()" in content):
                return "tk-inter"
            if "PyQt6" in content and ("import PyQt6" in content or "from PyQt6" in content):
                return "pyqt6"
            if "PySide6" in content and ("import PySide6" in content or "from PySide6" in content):
                return "pyside6"
            if "PyQt5" in content and ("import PyQt5" in content or "from PyQt5" in content):
                return "pyqt5"
            if "PySide2" in content and ("import PySide2" in content or "from PySide2" in content):
                return "pyside2"
        except: pass
        return None

    def _cleanup_injected_codes(self):
        """清理所有注入的代码（打包完成或失败时调用）"""
        input_file = self.input_path.get()
        if not input_file or not os.path.isfile(input_file):
            return

        # 撤销工作目录代码
        if self._workdir_injected:
            if self._remove_workdir_code(input_file):
                self.safe_log("✅ 已移除工作目录代码")
            self._workdir_injected = False
        # 撤销防多开代码
        
        if self._remove_single_instance(input_file):
            self.safe_log("🔓 已移除防多开代码")
            self._multi_injected = False

    def _inject_icon_code(self, source_file, icon_file):
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()
            if "# AUTO_INJECTED_ICON" in content:
                return
            icon_name = os.path.basename(icon_file)
            is_tk = "tkinter" in content or "Tk()" in content
            is_pyqt = "PyQt" in content or "QApplication" in content
            if is_tk:
                code = f'''
# AUTO_INJECTED_ICON
if getattr(sys, 'frozen', False):
    _base = sys._MEIPASS
else:
    _base = os.path.dirname(__file__)
_ip = os.path.join(_base, "{icon_name}")
if os.path.exists(_ip):
    try: self.root.iconbitmap(_ip)
    except: pass
# END AUTO_INJECTED_ICON
'''
            elif is_pyqt:
                code = f'''
# AUTO_INJECTED_ICON
if getattr(sys, 'frozen', False):
    _base = sys._MEIPASS
else:
    _base = os.path.dirname(__file__)
_ip = os.path.join(_base, "{icon_name}")
if os.path.exists(_ip):
    try: self.setWindowIcon(QIcon(_ip))
    except: pass
# END AUTO_INJECTED_ICON
'''
            else:
                return
            lines = content.split("\n")
            new_lines = []
            injected = False
            for line in lines:
                new_lines.append(line)
                if not injected and is_tk and ("= tk.Tk()" in line or "= Tk()" in line):
                    new_lines.append(code)
                    injected = True
                elif not injected and is_pyqt and ("setWindowTitle" in line or "setGeometry" in line):
                    new_lines.append(code)
                    injected = True
            if not injected:
                new_lines.append(code)
            with open(source_file, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines))
            self.safe_log("✅ 已注入图标代码")
        except Exception as e:
            self.safe_log(f"❌ 注入失败: {e}")

    def _inject_build_date(self, source_file, build_date=None):
        """更新源文件中的 BUILD_DATE 变量值（仅当新日期晚于旧日期）"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()

            if build_date is None:
                build_date = datetime.datetime.now().strftime("%Y-%m-%d")

            # 查找文件中的现有日期（只匹配引号内的内容）
            pattern = r'BUILD_DATE\s*=\s*["\']([\d\-]+)["\']'
            match = re.search(pattern, content)

            if match:
                old_date_str = match.group(1)
                try:
                    old_date = datetime.datetime.strptime(old_date_str, "%Y-%m-%d").date()
                    new_date = datetime.datetime.strptime(build_date, "%Y-%m-%d").date()

                    # 只有当新日期晚于旧日期时才替换
                    if new_date <= old_date:
                        #self.safe_log(f"📅 当前日期({build_date})不晚于文件日期({old_date_str})，跳过更新")
                        return True
                except:
                    pass

            # 精确替换：只替换引号内的日期字符串
            # 匹配 BUILD_DATE = "任意日期" 或 BUILD_DATE = '任意日期'
            pattern_replace = r'(BUILD_DATE\s*=\s*["\'])[\d\-]+(["\'])'

            def replace_date(m):
                return f'{m.group(1)}{build_date}{m.group(2)}'

            new_content = re.sub(pattern_replace, replace_date, content)

            # 如果没有找到匹配，在文件开头添加
            if new_content == content:
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('# -*- coding:') or line.startswith('# coding:'):
                        insert_pos = i + 1
                        break
                lines.insert(insert_pos, f'BUILD_DATE = "{build_date}"')
                new_content = '\n'.join(lines)

            with open(source_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            #self.safe_log(f"📅 更新 BUILD_DATE = {build_date}")
            return True
        except Exception as e:
            self.safe_log(f"⚠️ 注入日期失败: {e}")
            return False

    def _package_app(self):
        packer = self.packer_type.get()
        input_path = self.input_path.get()
        if os.path.isdir(input_path):
            entry = self._find_entry(input_path)
            if not entry:
                self.safe_log("❌ 文件夹中没有Python入口文件")
                return False
            self.safe_log(f"📁 文件夹模式，入口: {os.path.basename(entry)}")
        else:
            entry = input_path
        if packer == "Nuitka":
            return self._package_nuitka(entry)
        elif packer == "Py2exe":
            return self._package_py2exe(entry)
        elif packer == "Cx_Freeze":
            return self._package_cxfreeze(entry)
        elif packer == "PyOxidizer":
            return self._package_pyoxidizer(entry)
        elif packer == "Pynsist":
            return self._package_pynsist(entry)
        elif packer == "py2app":
            return self._package_py2app(entry)
        else:
            return self._package_pyinstaller(entry)

    def _inject_workdir_code(self, source_file):
        """注入工作目录代码（插在防多开代码后面）"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查前100行是否已有工作目录代码
            first_100_lines = '\n'.join(content.split('\n')[:100])
            if '# AUTO_INJECTED_WORKDIR' in first_100_lines:
                return True

            code = '''# AUTO_INJECTED_WORKDIR - 设置为exe所在目录
import os
import sys
import ctypes
import tempfile

class ExePathManager:
    @staticmethod
    def is_frozen() -> bool:
        frozen_flags = [
            getattr(sys, 'frozen', False),
            hasattr(sys, '_MEI_ARCHIVE'),
            getattr(sys, 'nuitka_is_frozen', False),
        ]
        if not any(frozen_flags):
            if sys.argv[0].lower().endswith('.exe'):
                return True
            if 'temp' in sys.executable.lower() or 'onefile' in sys.executable.lower():
                return True
            if sys.platform == 'win32':
                try:
                    buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                    ctypes.windll.kernel32.GetModuleFileNameW(
                        ctypes.wintypes.HMODULE(0),
                        buffer,
                        ctypes.wintypes.MAX_PATH
                    )
                    exe_path = buffer.value
                    if exe_path.lower().endswith('.exe'):
                        return True
                except:
                    pass
        return any(frozen_flags)

    @staticmethod
    def get_real_exe_path() -> str:
        if not ExePathManager.is_frozen():
            return os.path.abspath(__file__)
        if sys.platform == 'win32':
            try:
                buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.kernel32.GetModuleFileNameW(
                    ctypes.wintypes.HMODULE(0),
                    buffer,
                    ctypes.wintypes.MAX_PATH
                )
                real_path = buffer.value
                if os.path.exists(real_path) and os.path.isfile(real_path):
                    return real_path
            except:
                pass
        if hasattr(sys, '_MEIPASS'):
            return sys.executable
        return os.path.abspath(sys.argv[0])

    @staticmethod
    def get_exe_directory() -> str:
        return os.path.dirname(ExePathManager.get_real_exe_path())

    @staticmethod
    def is_temp_directory(path: str) -> bool:
        temp_dirs = [
            tempfile.gettempdir(),
            os.path.join(os.environ.get('TEMP', ''), ''),
            os.path.join(os.environ.get('TMP', ''), ''),
        ]
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(temp_dir) for temp_dir in temp_dirs if temp_dir)

if ExePathManager.is_frozen():
    exe_dir = ExePathManager.get_exe_directory()
    if os.path.exists(exe_dir):
        os.chdir(exe_dir)
# END AUTO_INJECTED_WORKDIR
'''
            # 查找防多开代码的结束位置
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines[:100]):
                if '# END GUARD' in line:
                    insert_pos = i + 1  # 插在 END GUARD 后面
                    break

            if insert_pos > 0:
                # 有防多开代码，插在后面
                lines.insert(insert_pos, code)
                new_content = '\n'.join(lines)
            else:
                # 没有防多开代码，直接插在第0行
                new_content = code + content

            with open(source_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            # 计算起始行号
            if insert_pos > 0:
                # 有防多开，从防多开结束后的下一行开始
                start_line = insert_pos + 1
            else:
              #无防多开，从第1行开始
                start_line = 1

            # 计算代码块行数
            code_lines = code.count('\n') + 1  # +1 因为最后一行没有换行符
            end_line = start_line + code_lines - 1

            self.safe_log(f"✅ 已注入工作目录代码（第{start_line}-{end_line}行）")
            return True
        except Exception as e:
            self.safe_log(f"⚠️ 注入失败: {e}")
            return False

    def _remove_workdir_code(self, source_file):
        """移除工作目录代码（前100行内查找）"""
        try:
            with open(source_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start_idx = -1
            end_idx = -1

            for i, line in enumerate(lines[:100]):
                if '# AUTO_INJECTED_WORKDIR' in line:
                    start_idx = i
                if start_idx != -1 and '# END AUTO_INJECTED_WORKDIR' in line:
                    end_idx = i
                    break

            if start_idx != -1 and end_idx != -1:
                new_lines = lines[:start_idx] + lines[end_idx + 1:]
                with open(source_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

                self.workdir_switch.set(False)
                self.workdir_enabled = False
                #self.safe_log("🔓 已关闭工作目录开关") 
   
                return True
            return False
        except Exception as e:
            return False

    def _package_pyinstaller(self, input_file):
        py, ver = self._check_pyinstaller()
        if not py:
            self.safe_log("❌ 未找到Python")
            return False
        if ver == "未安装":
            messagebox.showerror("错误", "请先安装 PyInstaller: pip install pyinstaller")
            return False
        self.safe_log(f"✅ 使用: {py} (PyInstaller {ver})")
        out_name = self.output_name.get()
        out_dir = os.path.join(self.output_path.get(), out_name.replace(" ", "_"))
        os.makedirs(out_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {out_dir}")

        cmd = [py, "-m", "PyInstaller", f"--name={out_name}", f"--distpath={out_dir}",
               "--workpath=build_temp", "--specpath=build_temp", "--noconfirm"]

        if os.path.isdir(self.input_path.get()):
            cmd.append(f"--paths={self.input_path.get()}")

        # 强制包含所有隐藏导入模块
        for imp in self.hidden_imports_list:
            cmd.append(f"--collect-all={imp}")
            self.safe_log(f"📦 包含模块: {imp}")

        # 如果虚拟环境开启，添加虚拟环境路径作为备用
        if self.use_venv:
            venv_py = self._get_venv_python()
            if venv_py:
                site_packages = self._get_site_packages_path(venv_py)
                if site_packages and os.path.exists(site_packages):
                    cmd.append(f"--paths={site_packages}")
                    self.safe_log(f"📦 已添加虚拟环境路径: {site_packages}")

        for src, tgt in self.data_files_list:
            cmd.append(f"--add-data={src}{os.pathsep}{tgt}")
        for exc in self.exclude_list:
            cmd.append(f"--exclude-module={exc}")

        cmd.append("--onefile" if self.package_type.get() == "onefile" else "--onedir")

        if self.upx_switch.get() and self.upx_path.get():
            cmd.append(f"--upx-dir={os.path.dirname(self.upx_path.get())}")
            self.safe_log("🗜️ 启用UPX压缩")

        if not self.debug_mode.get():
            cmd.append("--windowed")

        if self.icon_path.get():
            icon = self.icon_path.get()
            cmd.append(f"--icon={icon}")
            cmd.append(f"--add-data={icon}{os.pathsep}.")
            self._inject_icon_code(input_file, icon)

        # ========== 版本信息 ==========
        version_file = self._apply_version_to_pyinstaller(cmd)
        if version_file:
            self._temp_version_file = version_file  # 记录临时文件路径，打包后删除

        cmd.append(input_file)
        self.safe_log("🚀 开始 PyInstaller 打包...")
        self.root.update

        try:
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            for key in list(env.keys()):
                if isinstance(env[key], tuple):
                    env[key] = env[key][0] if env[key] else ""
                elif not isinstance(env[key], str):
                    env[key] = str(env[key])

            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True, bufsize=1, encoding="utf-8",
                                            errors="replace", startupinfo=get_startupinfo(),
                                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                                            env=env)

            # PyInstaller 阶段配置
            stage_config = {
                "analyzing": {"interval": 1.0, "text": "分析脚本...", "min": 1, "max": 20},
                "processing": {"interval": 2.0, "text": "处理资源...", "min": 21, "max": 50},
                "building": {"interval": 1.5, "text": "构建中...", "min": 51, "max": 85},
                "packaging": {"interval": 1.0, "text": "打包中...", "min": 86, "max": 95},
            }

            current_stage = "analyzing"
            self._start_fake_progress(
                update_interval=stage_config["analyzing"]["interval"],
                text=stage_config["analyzing"]["text"],
                min_progress=stage_config["analyzing"]["min"],
                max_progress=stage_config["analyzing"]["max"]
            )
            self.root.update_idletasks()

            def update_progress():
                nonlocal current_stage
                if self.process is None:
                    return
                for line in iter(self.process.stdout.readline, ""):
                    if line.strip():
                        self._stop_fake_progress()
                        self.safe_log(line.strip())
                        ll = line.lower()

                        new_stage = current_stage
                        if "Module search" in ll:
                            new_stage = "analyzing"
                        elif "Processing standard" in ll:
                            new_stage = "processing"
                        elif "Analyzing hidden" in ll:
                            new_stage = "building"
                        elif "Disabling UPX" in ll:
                            new_stage = "packaging"
                        elif "Build complete" in ll:
                            self.progress_var.set(100)
                            self.progress_label.config(text="100% - 完成!")
                            self.root.update_idletasks()
                            continue

                        if new_stage != current_stage:
                            cfg = stage_config.get(new_stage, stage_config["analyzing"])
                            self._start_fake_progress(
                                update_interval=cfg["interval"],
                                text=cfg["text"],
                                min_progress=cfg["min"],
                                max_progress=cfg["max"]
                            )
                            current_stage = new_stage

                        import re
                        match = re.search(r'(\d+)%', line)
                        if match:
                            pct = int(match.group(1))
                            if pct > self.progress_var.get():
                                self.progress_var.set(pct)
                                self.progress_label.config(text=f"{pct}% - {current_stage}...")
                                self.root.update_idletasks()

                    if self.pack_btn[
                        "text"] == "▶开始打包" and self.process is not None and self.process.poll() is None:
                        self.process.terminate()
                        break

            progress_thread = threading.Thread(target=update_progress, daemon=True)
            progress_thread.start()
            self.process.wait()

            self._stop_fake_progress()
            progress_thread.join(timeout=1)

            for d in ["build_temp", "__pycache__"]:
                if os.path.exists(d):
                    try:
                        shutil.rmtree(d)
                    except:
                        pass
            spec = os.path.join(self.current_dir, f"{out_name}.spec")
            if os.path.exists(spec):
                os.remove(spec)

            success = self.process.returncode == 0
            if success:
                self.safe_log(f"✅ PyInstaller 打包成功！输出: {out_dir}")
                self._save_config()
            else:
                self.safe_log("❌ PyInstaller 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _smooth_progress(self, target_pct, text, step=2, delay=0.03):
        """平滑过渡到目标进度"""
        current = int(self.progress_var.get())
        if current >= target_pct:
            self.progress_label.config(text=text)
            return

        def update():
            nonlocal current
            if current < target_pct:
                current = min(current + step, target_pct)
                self.progress_var.set(current)
                self.progress_label.config(text=f"{current}% - {text}")
                self.root.update_idletasks()
                if current < target_pct:
                    self.root.after(int(delay * 1000), update)

        self.root.after(0, update)

    def _start_stage_progress(self, start_pct, end_pct, text):
        """启动阶段进度条（从 start_pct 匀速增长到 end_pct）"""
        # 停止当前进度更新
        if hasattr(self, '_stage_progress_running'):
            self._stage_progress_running = False
        if hasattr(self, '_progress_update_id'):
            self.root.after_cancel(self._progress_update_id)

        self._stage_progress_running = True
        self._stage_start_pct = max(self.progress_var.get(), start_pct)
        self._stage_end_pct = end_pct
        self._stage_text = text
        self._stage_start_time = time.time()
        # 阶段内预计时长（固定值，不影响最终进度，只控制速度）
        self._stage_duration = 90  # 每个阶段最多30秒跑完

        def update():
            if not self._stage_progress_running:
                return
            elapsed = time.time() - self._stage_start_time
            ratio = min(1.0, elapsed / self._stage_duration)
            pct = self._stage_start_pct + int(ratio * (self._stage_end_pct - self._stage_start_pct))
            pct = min(pct, self._stage_end_pct)
            self.progress_var.set(pct)
            self.progress_label.config(text=f"{pct}% - {self._stage_text}")
            self.root.update_idletasks()
            if pct < self._stage_end_pct:
                self._progress_update_id = self.root.after(200, update)
            else:
                self._stage_progress_running = False

        self._progress_update_id = self.root.after(0, update)

    def _stop_stage_progress(self):
        """停止阶段进度条"""
        self._stage_progress_running = False
        if hasattr(self, '_progress_update_id'):
            self.root.after_cancel(self._progress_update_id)

    def _check_nuitka(self, py):
        """使用 pip show 检测 Nuitka 版本"""
        try:
            r = subprocess.run([py, "-m", "pip", "show", "nuitka"],
                               capture_output=True, text=True, timeout=10,
                               startupinfo=get_startupinfo())
            if r.returncode != 0:
                return False, None

            # 解析版本号
            for line in r.stdout.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    return True, version
            return False, None
        except Exception as e:
            self.safe_log(f"⚠️ 检测失败: {e}")
            return False, None

    def _on_nuitka_compat_toggle(self):
        if self.nuitka_compat_mode.get():
            self.safe_log("✅ 已启用 Nuitka 4.1 兼容模式")
        else:
            self.safe_log("✅ 已切换回 Nuitka 4.0.8 兼容模式")

    def _package_nuitka(self, input_file):
        py = self._get_python()
        if not py:
            self.safe_log("❌ 未找到Python")
            return False

        # Nuitka 版本检测
        version = None
        if hasattr(self, '_packer_versions'):
            version = self._packer_versions.get('Nuitka')

        if not version:
            installed, version = self._check_nuitka(py)
            if not installed:
                self.safe_log("⚠️ Nuitka 未安装，正在安装...")
                self._install_nuitka(py)
                installed, version = self._check_nuitka(py)
                if not installed:
                    self.safe_log("❌ Nuitka 安装失败")
                    return False
            if hasattr(self, '_packer_versions'):
                self._packer_versions['Nuitka'] = version
        else:
            installed, _ = self._check_nuitka(py)
            if not installed:
                self.safe_log("⚠️ Nuitka 未安装，正在安装...")
                self._install_nuitka(py)
                installed, version = self._check_nuitka(py)
                if not installed:
                    self.safe_log("❌ Nuitka 安装失败")
                    return False
                self._packer_versions['Nuitka'] = version

        self.safe_log(f"✅ Nuitka 版本: {version}")

        if version.startswith("4.1") and not self.nuitka_compat_mode.get():
            self.nuitka_compat_mode.set(True)

        out_name = self.output_name.get()
        out_dir = os.path.join(self.output_path.get(), out_name.replace(" ", "_"))
        os.makedirs(out_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {out_dir}")

        cmd = [py, "-m", "nuitka"]

        # ========== 使用新的版本信息==========
        self._apply_version_to_nuitka(cmd)

        jobs = self.nuitka_jobs.get()
        if jobs == "auto":
            jobs = str(self.cpu_count)
        self.safe_log(f"⚙️ 并行任务: {jobs}")

        # 编译器选择逻辑
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "zh_CN.UTF-8"
        env["LC_ALL"] = "zh_CN.UTF-8"

        backend = self.nuitka_backend.get()
        use_mingw = None

        if backend == "MinGW64":
            if not self.has_mingw and not self.mingw_path:
                self.safe_log("⚠️ 未检测到 MinGW64 编译器")
                if messagebox.askyesno("安装 MinGW64",
                                       "未检测到 MinGW64 编译器，是否打开下载页面？\n\n下载后解压到 tools/mingw64 目录即可"):
                    import webbrowser
                    webbrowser.open("https://github.com/niXman/mingw-builds-binaries/releases")
                    self.safe_log("💡 请下载 MinGW64 并解压到 tools/mingw64 目录")
                else:
                    self.safe_log("❌ 用户取消，请安装 MinGW64 或切换其他编译器")
                return False
            else:
                use_mingw = True
            self.safe_log("🔧 用户手动选择: MinGW64")

        elif backend == "MSVC":
            if not self.has_msvc:
                self.safe_log("⚠️ 未检测到 MSVC 编译器")
                if messagebox.askyesno("安装 MSVC",
                                       "未检测到 MSVC 编译器，是否打开下载页面？\n\n请安装 Visual Studio Build Tools 或 Visual Studio"):
                    import webbrowser
                    webbrowser.open("https://visualstudio.microsoft.com/zh-hans/downloads/")
                    self.safe_log("💡 请安装 Visual Studio Build Tools 后重试")
                else:
                    self.safe_log("❌ 用户取消，请安装 MSVC 或切换其他编译器")
                return False
            else:
                use_mingw = False
            self.safe_log("🔧 用户手动选择: MSVC")

        else:  # auto 模式
            has_mingw = self.has_mingw or self.mingw_path
            has_msvc = self.has_msvc

            if has_mingw and has_msvc:
                use_mingw = True
                self.safe_log("🔧 自动检测: MinGW64 和 MSVC 均可用，优先使用 MinGW64")
            elif has_mingw:
                use_mingw = True
                self.safe_log("🔧 自动检测: 使用 MinGW64")
            elif has_msvc:
                use_mingw = False
                self.safe_log("🔧 自动检测: 使用 MSVC")
            else:
                use_mingw = True
                self.safe_log("🔧 未检测到编译器，将自动下载 MinGW64")

        if use_mingw:
            if self.mingw_path:
                env["PATH"] = self.mingw_path + os.pathsep + env.get("PATH", "")
            cmd.append("--mingw64")
            self.safe_log(f"🔧 使用: MinGW64")
        else:
            cmd.append("--msvc=latest")
            self.safe_log(f"🔧 使用: MSVC")

        # GUI 插件
        gui_plugin = self.nuitka_gui_plugin.get()
        if gui_plugin == "auto":
            detected = self._detect_gui(input_file)
            if detected:
                cmd.append(f"--enable-plugin={detected}")
                self.safe_log(f"🎨 自动检测到 GUI: {detected}")
            else:
                cmd.append("--enable-plugin=tk-inter")
                self.safe_log("🎨 未检测到 GUI，默认启用 tk-inter 插件")
        else:
            cmd.append(f"--enable-plugin={gui_plugin}")
            self.safe_log(f"🎨 手动指定 GUI 插件: {gui_plugin}")

        cmd.extend(["--lto=no", "--nofollow-import-to=pytest", "--nofollow-import-to=unittest",
                    "--nofollow-import-to=_pytest", "--nofollow-import-to=hypothesis",
                    "--no-deployment-flag=no-python-dll", "--no-prefer-source-code"])

        if self.package_type.get() == "onefile":
            cmd.append("--onefile")
        else:
            if self.nuitka_compat_mode.get():
                cmd.append("--deployment")
            else:
                cmd.append("--standalone")

        cmd.extend([f"--jobs={jobs}", "--assume-yes-for-downloads", "--remove-output",
                    f"--output-dir={out_dir}", f"--output-filename={out_name}.exe"])

        if not self.debug_mode.get() and sys.platform == "win32":
            if self.nuitka_compat_mode.get():
                cmd.append("--windows-console-mode=disable")
            else:
                cmd.append("--windows-disable-console")

        if self.icon_path.get() and os.path.exists(self.icon_path.get()):
            cmd.append(f"--windows-icon-from-ico={self.icon_path.get()}")

        if self.upx_switch.get() and self.upx_path.get():
            upx_exe = self.upx_path.get()
            cmd.append("--enable-plugin=upx")
            cmd.append(f"--upx-binary={upx_exe}")
            self.safe_log(f"🗜️ 启用UPX压缩 {upx_exe}")

        for exc in self.exclude_list:
            cmd.append(f"--nofollow-import-to={exc}")

        for imp in self.hidden_imports_list:
            cmd.append(f"--include-module={imp}")
 
        for src, tgt in self.data_files_list:
            cmd.append(f"--include-data-files={src}={tgt}")

        cmd.append(input_file)
        self.safe_log("🚀 开始 Nuitka 编译（较慢，请耐心等待）...")
        self.root.update_idletasks()

        try:
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            env["LANG"] = "zh_CN.UTF-8"
            env["LC_ALL"] = "zh_CN.UTF-8"
            if self.mingw_path:
                env["PATH"] = self.mingw_path + os.pathsep + env.get("PATH", "")

            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            universal_newlines=True, bufsize=1,
                                            encoding='utf-8', errors="replace",
                                            startupinfo=get_startupinfo(), env=env)

            self.progress_var.set(5)
            self.progress_label.config(text="5% - 启动Nuitka...")
            self.root.update_idletasks()

            for line in iter(self.process.stdout.readline, ""):
                if line:
                    line = line.rstrip()
                    self.safe_log(line)
                    ll = line.lower()

                    if "starting python compilation" in ll:
                        self.progress_var.set(10)
                        self.progress_label.config(text="10% - 分析模块...")
                        self.root.update_idletasks()
                    elif "generating source code" in ll:
                        self.progress_var.set(25)
                        self.progress_label.config(text="25% - 生成C代码...")
                        self.root.update_idletasks()
                    elif "running c compilation" in ll or "c compilation" in ll:
                        self.progress_var.set(40)
                        self.progress_label.config(text="40% - 编译C代码...")
                        self.root.update_idletasks()

                        m = re.search(r"Compiled\s+(\d+)/(\d+)\s+C\s+files", line, re.I)
                        if m:
                            c, t = int(m.group(1)), int(m.group(2))
                            if t > 0:
                                pct = 40 + int(c / t * 45)
                                self.progress_var.set(pct)
                                self.progress_label.config(text=f"{pct}% - 编译C代码 ({c}/{t})...")
                                self.root.update_idletasks()
                    elif "Backend C" in ll:
                        self.progress_var.set(60)
                        self.progress_label.config(text="60% - 编译中...")
                        self.root.update_idletasks()
                    elif "Creating single file" in ll:
                        self.progress_var.set(70)
                        self.progress_label.config(text="70% - 构建中...")
                        self.root.update_idletasks()
                    elif "linking" in ll and "Backend" not in ll:
                        self.progress_var.set(80)
                        self.progress_label.config(text="80% - 链接中...")
                        self.root.update_idletasks()
                    elif "Using compression" in ll:
                        self.progress_var.set(90)
                        self.progress_label.config(text="90% - 打包中...")
                        self.root.update_idletasks()
                    elif "Removing" in ll:
                        self.progress_var.set(95)
                        self.progress_label.config(text="95% - 清理中...")
                        self.root.update_idletasks()
                    elif "successfully created" in ll:
                        self.progress_var.set(100)
                        self.progress_label.config(text="100% - 完成!")
                        self.root.update_idletasks()

            self.process.wait()
            success = self.process.returncode == 0

            if success:
                self.safe_log(f"\n✅ Nuitka 打包成功！输出: {out_dir}")
                self._save_config()
            else:
                self.safe_log(f"\n❌ Nuitka 失败，退出码: {self.process.returncode}")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            import traceback
            self.safe_log(traceback.format_exc())
            return False
        finally:
            self.process = None

    def _install_nuitka(self, py):
        self.safe_log("📦 安装 Nuitka...")
        try:
            r = subprocess.run([py, "-m", "pip", "install", "nuitka", "-i", MIRROR],
                            capture_output=True, text=True, timeout=300, startupinfo=get_startupinfo())
            if r.returncode == 0:
                self.safe_log("✅ Nuitka 安装成功")
                return True
            else:
                self.safe_log(f"❌ 安装失败: {r.stderr}")
                return False
        except Exception as e:
            self.safe_log(f"❌ 安装异常: {e}")
            return False

    def _package_py2exe(self, input_file):
        """使用 py2exe 打包"""
        python_cmd = self._get_python()
		
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False

        self.safe_log("⚠️ py2exe 对现代 Python 项目支持有限")

        input_file = self.input_path.get()
        output_name = self.output_name.get()
        base_output_dir = self.output_path.get()
        project_output_dir = os.path.join(
            base_output_dir, output_name.replace(" ", "_")
        )
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")

        # 生成 setup.py（三引号顶格）
        setup_content = f"""# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

setup(
    console=[{{"script": "{os.path.basename(input_file)}"}}],
    options={{'py2exe': {{
        'compressed': True,
        'optimize': 2,
        'bundle_files': 3,  # 改为 3（Python 3.12+ 必须）
        'includes': {self.hidden_imports_list},
        'excludes': {self.exclude_list}
    }}}},
    zipfile=None
)
"""

        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)

        # 复制源文件到输出目录
        shutil.copy2(input_file, project_output_dir)

        # 打包命令
        cmd = [python_cmd, "setup.py", "py2exe"]
        self.safe_log(f"🚀 开始 py2exe 打包...")
        self.safe_log(f"📝 命令: {' '.join(cmd)}")
        self.root.update()

        # 进度条初始化
        self.progress_var.set(5)
        self.progress_label.config(text="5% - 准备中...")
        self.root.update_idletasks()

        try:
            startupinfo = get_startupinfo()
            system_encoding = locale.getpreferredencoding()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding=system_encoding,
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )

            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1

                    # 根据输出行数更新进度
                    if "Copying" in line or "copying" in line.lower():
                        pct = min(20 + line_count // 2, 50)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 复制依赖...")
                        self.root.update_idletasks()
                    elif "Building" in line or "building" in line.lower():
                        pct = min(50 + line_count // 3, 80)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 构建中...")
                        self.root.update_idletasks()
                    elif "copy" in line.lower() and "dll" in line.lower():
                        pct = min(80 + line_count // 5, 95)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 复制DLL...")
                        self.root.update_idletasks()

                if (
                    self.pack_btn["text"] == "▶开始打包"
                    and self.process.poll() is None
                ):
                    self.process.terminate()
                    break

            self.process.wait()
            success = self.process.returncode == 0

            if success:
                self.progress_var.set(100)
                self.progress_label.config(text="100% - 完成!")
                self.root.update_idletasks()

                dist_dir = os.path.join(project_output_dir, "dist")
                if os.path.exists(dist_dir):
                    for item in os.listdir(dist_dir):
                        src = os.path.join(dist_dir, item)
                        dst = os.path.join(project_output_dir, item)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                self.safe_log(f"✅ py2exe 打包完成！输出位置: {project_output_dir}")
                self._save_config()
            else:
                self.safe_log("❌ py2exe 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _package_cxfreeze(self, input_file):
        """使用 cx_Freeze 打包"""
        python_cmd = self._get_python()
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False

        input_file = self.input_path.get()
        output_name = self.output_name.get()
        base_output_dir = self.output_path.get()
        project_output_dir = os.path.join(
            base_output_dir, output_name.replace(" ", "_")
        )
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")

        nocon = (
            not self.debug_switch.get()
            if hasattr(self, "debug_switch")
            else not self.debug_mode.get()
        )
        icon_file = self.icon_path.get()

        # 处理图标路径
        icon_param = ""
        if icon_file and os.path.exists(icon_file):
            icon_filename = os.path.basename(icon_file)
            shutil.copy2(icon_file, project_output_dir)
            icon_param = f', icon="{icon_filename}"'
        else:
            icon_param = ""

        # 生成 setup.py
        setup_content = f"""# -*- coding: utf-8 -*-
from cx_Freeze import setup, Executable
import sys, os

# 1、基础配置
build_exe_options = {{
    "packages": ["os", "sys"],# 包含的额外包
    "excludes": {self.exclude_list},# 排除的包
    "include_files": [], # 包含的额外文件或文件夹
    "optimize": 2, # 优化级别0,1,2
    }}
# 根据程序类型设置 base
base = None
#if sys.platform == "win32" and {nocon}:
    #base = "Win32GUI"
# 3、调用 setup 函数    
setup(
    name="{output_name}",
    version="1.0",
    description="打包程序",
    options={{"build_exe": build_exe_options}},
    executables=[Executable(
        "{os.path.basename(input_file)}",
        base=base,
        target_name="{output_name}.exe"{icon_param}
    )]
)
"""
        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)

        # 复制源文件和图标
        shutil.copy2(input_file, project_output_dir)
        if icon_file and os.path.exists(icon_file):
            shutil.copy2(icon_file, project_output_dir)

        # 构建命令
        cmd = [python_cmd, "setup.py", "build_exe"]
        self.safe_log("🚀 开始 cx_Freeze 打包...")
        self.root.update()

        # 进度条初始化
        self.progress_var.set(0)
        self.progress_label.config(text="0% - 准备中...")
        self.root.update_idletasks()

        # 进度计数
        step = 0

        try:
            startupinfo = get_startupinfo()
            system_encoding = locale.getpreferredencoding()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding=system_encoding,
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )

            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_lower = line.lower()

                    # 根据输出更新进度
                    if "copying" in line_lower:
                        step += 1
                        pct = min(step * 5, 80)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 复制文件...")
                        self.root.update_idletasks()
                    elif "building" in line_lower or "compiling" in line_lower:
                        self.progress_var.set(85)
                        self.progress_label.config(text="85% - 构建中...")
                        self.root.update_idletasks()
                    elif "writing" in line_lower:
                        self.progress_var.set(95)
                        self.progress_label.config(text="95% - 写入文件...")
                        self.root.update_idletasks()

                if (
                    self.pack_btn["text"] == "▶开始打包"
                    and self.process.poll() is None
                ):
                    self.process.terminate()
                    break
            self.process.wait()
            success = self.process.returncode == 0

            if success:
                self.progress_var.set(100)
                self.progress_label.config(text="100% - 完成!")
                self.root.update_idletasks()

                # 复制生成的文件
                build_dir = os.path.join(project_output_dir, "build")
                if os.path.exists(build_dir):
                    import glob

                    exe_dirs = glob.glob(os.path.join(build_dir, "exe.*"))
                    if exe_dirs:
                        exe_dir = exe_dirs[0]
                        for item in os.listdir(exe_dir):
                            src = os.path.join(exe_dir, item)
                            dst = os.path.join(project_output_dir, item)
                            if os.path.isdir(src):
                                if os.path.exists(dst):
                                    shutil.rmtree(dst)
                                shutil.copytree(src, dst)
                            else:
                                shutil.copy2(src, dst)
                self.safe_log(f"✅ cx_Freeze 打包完成！输出位置: {project_output_dir}")
                self._save_config()
            else:
                self.safe_log("❌ cx_Freeze 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None


    def _generic_setup_build(self, input_file, module, name):
        py = self._get_python()
        if not py:
            self.safe_log("❌ 未找到Python")
            return False
        try:
            r = subprocess.run([py, "-c", f"import {module}"], capture_output=True, text=True,
                            timeout=5, startupinfo=get_startupinfo())
            if r.returncode != 0:
                if messagebox.askyesno("提示", f"{name} 未安装，是否安装？"):
                    subprocess.run([py, "-m", "pip", "install", module, "-i", MIRROR],
                                  capture_output=True, timeout=300, startupinfo=get_startupinfo())
                else:
                    return False
        except:
            return False

        out_name = self.output_name.get()
        out_dir = os.path.join(self.output_path.get(), out_name.replace(" ", "_"))
        os.makedirs(out_dir, exist_ok=True)

        setup = f'''# -*- coding: utf-8 -*-
from distutils.core import setup
import {module}

setup(
    console=[{{"script": "{os.path.basename(input_file)}"}}],
    options={{{repr(module): {{"compressed": True, "optimize": 2, "bundle_files": 3,
        "includes": {self.hidden_imports_list}, "excludes": {self.exclude_list}}}}}},
    zipfile=None
)
'''
        with open(os.path.join(out_dir, "setup.py"), "w", encoding="utf-8") as f:
            f.write(setup)
        shutil.copy2(input_file, out_dir)

        try:
            self.process = subprocess.Popen([py, "setup.py", module], stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1,
                                           encoding=locale.getpreferredencoding(), errors="replace",
                                           startupinfo=get_startupinfo(), cwd=out_dir)
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
            self.process.wait()
            success = self.process.returncode == 0
            if success:
                self.safe_log(f"✅ {name} 打包成功: {out_dir}")
                self._save_config()
            else:
                self.safe_log(f"❌ {name} 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _find_rustc(self):
        """查找 rustc 可执行文件路径，返回路径或 None"""
        import os
        import shutil

        # 1. 先尝试 PATH 中直接查找
        rustc_path = shutil.which("rustc")
        if rustc_path:
            return rustc_path

        # 2. 检查常见安装路径
        common_paths = []

        if sys.platform == "win32":
            # Windows 常见路径
            user_profile = os.environ.get("USERPROFILE", "")
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            local_appdata = os.environ.get("LOCALAPPDATA", "")

            common_paths = [
                os.path.join(user_profile, ".cargo", "bin", "rustc.exe"),
                os.path.join(local_appdata, ".cargo", "bin", "rustc.exe"),
                os.path.join(program_files, "Rust", "bin", "rustc.exe"),
                r"C:\Users\{}\.cargo\bin\rustc.exe".format(os.environ.get("USERNAME", "")),
                r"C:\Rust\bin\rustc.exe",
            ]

            # 检查 RUSTUP_HOME 环境变量
            rustup_home = os.environ.get("RUSTUP_HOME")
            if rustup_home:
                common_paths.insert(0, os.path.join(rustup_home, "bin", "rustc.exe"))

            cargo_home = os.environ.get("CARGO_HOME")
            if cargo_home:
                common_paths.insert(0, os.path.join(cargo_home, "bin", "rustc.exe"))
        else:
            # Linux/macOS 常见路径
            home = os.path.expanduser("~")
            common_paths = [
                os.path.join(home, ".cargo", "bin", "rustc"),
                os.path.join(home, ".rustup", "bin", "rustc"),
                "/usr/local/cargo/bin/rustc",
                "/usr/local/rust/bin/rustc",
                "/opt/rust/bin/rustc",
            ]

            rustup_home = os.environ.get("RUSTUP_HOME")
            if rustup_home:
                common_paths.insert(0, os.path.join(rustup_home, "bin", "rustc"))

            cargo_home = os.environ.get("CARGO_HOME")
            if cargo_home:
                common_paths.insert(0, os.path.join(cargo_home, "bin", "rustc"))

        for path in common_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        return None

    def _clear_cargo_lock(self):
        """清理 Cargo 包缓存锁"""
        import glob

        # 1. 清理 Cargo 全局锁
        cargo_home = os.path.join(os.path.expanduser("~"), ".cargo")
        locks = [
            os.path.join(cargo_home, ".package-cache"),
            os.path.join(cargo_home, "registry", ".package-cache"),
        ]
        for lock in locks:
            if os.path.exists(lock):
                try:
                    os.remove(lock)
                    self.safe_log(f"🗑️ 清理 Cargo 锁: {lock}")
                except Exception as e:
                    self.safe_log(f"⚠️ 无法清理锁: {e}")

        # 2. 清理 PyOxidizer 临时目录锁
        temp_base = os.environ.get("TEMP", os.environ.get("TMP", "C:\\Windows\\Temp"))
        for tmp_dir in glob.glob(os.path.join(temp_base, "pyoxidizer*")):
            cargo_lock = os.path.join(tmp_dir, ".cargo-lock")
            if os.path.exists(cargo_lock):
                try:
                    os.remove(cargo_lock)
                    self.safe_log(f"🗑️ 清理临时锁: {cargo_lock}")
                except:
                    pass

    def _kill_residual_processes(self):
        """终止残留的构建进程"""
        try:
            import psutil
            import time

            killed = 0
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    name = proc.info['name']
                    if name in ['cargo.exe', 'rustc.exe']:
                        age = time.time() - proc.info['create_time']
                        if age > 600:  # 超过10分钟
                            self.safe_log(f"🗑️ 终止卡死进程: {name} (PID:{proc.info['pid']}, 运行{age:.0f}秒)")
                            proc.kill()
                            killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if killed > 0:
                self.safe_log(f"✅ 已清理 {killed} 个残留进程")
                time.sleep(2)
        except ImportError:
            pass  # psutil 没装就跳过

    def _setup_project_cargo_mirror(self, project_output_dir):
        """配置 Cargo 镜像（传统 git 格式，兼容旧版 Rust）"""
        cargo_dir = os.path.join(project_output_dir, ".cargo")
        os.makedirs(cargo_dir, exist_ok=True)

        config_path = os.path.join(cargo_dir, "config.toml")

        # 用传统 git registry，不用 sparse（兼容 Rust 1.66）
        config_content = """[source.crates-io]
replace-with = 'ustc'

[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"

[net]
git-fetch-with-cli = true
"""

        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)

        self.safe_log("✅ 已配置 Cargo 镜像 (ustc.edu.cn, git协议)")

    def _remove_pyoxidizer_old_rust(self):
        """删除 PyOxidizer 自带的旧版 Rust，强制使用系统 Rust"""
        pyoxidizer_rust_dir = os.path.join(
            os.path.expanduser("~"),
            "AppData", "Local", "pyoxidizer", "rust"
        )
        if os.path.exists(pyoxidizer_rust_dir):
            self.safe_log(f"🗑️ 清理 PyOxidizer 旧 Rust: {pyoxidizer_rust_dir}")
            import shutil
            shutil.rmtree(pyoxidizer_rust_dir, ignore_errors=True)

    def _package_pyoxidizer(self, input_file):
        """使用 PyOxidizer 打包（使用本地预下载的 Python 发行版）"""
        python_cmd = self._get_python()
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False

        # ========== 清理残留 ==========
        #self._clear_cargo_lock()
        self._kill_residual_processes()
        #self._remove_pyoxidizer_old_rust()

        # ========== 进度条初始化 ==========
        self.progress_var.set(0)
        self.progress_label.config(text="0% - 准备中...")
        self.root.update_idletasks()

        # ========== 检测 Rust ==========
        rustc_path = self._find_rustc()
        if not rustc_path:
            self.safe_log("⚠️ 未检测到 Rust 安装")
            messagebox.showinfo(
                "提示",
                "请先安装 Rust:\n\n"
                "Windows: 访问 https://rustup.rs/ 下载 rustup-init.exe\n"
                "Linux/macOS: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh\n\n"
                "安装后请重启程序以确保环境变量生效。"
            )
            return False

        self.safe_log(f"✅ 检测到 Rust: {rustc_path}")
        try:
            rust_result = subprocess.run(
                [rustc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                startupinfo=get_startupinfo(),
            )
            if rust_result.returncode == 0:
                self.safe_log(f"📦 {rust_result.stdout.strip()}")
        except Exception as e:
            self.safe_log(f"⚠️ 验证 Rust 版本时出错: {e}")

        self.progress_var.set(10)
        self.progress_label.config(text="10% - 准备配置文件...")
        self.root.update_idletasks()

        input_file = self.input_path.get()
        output_name = self.output_name.get()
        base_output_dir = self.output_path.get()
        project_output_dir = os.path.join(
            base_output_dir, output_name.replace(" ", "_")
        )
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")

        entry_module = os.path.basename(input_file).replace('.py', '')

        # 检查是否有 requirements.txt
        req_file = os.path.join(os.path.dirname(input_file), "requirements.txt")
        has_requirements = os.path.exists(req_file)

        # 构建 pip 安装语句
        pip_install_lines = []
        if has_requirements:
            pip_install_lines.append(f'    exe.add_python_resources(exe.pip_install(["-r", r"{req_file}"]))')
        pip_install_lines.append('    exe.add_python_resources(exe.pip_install(["Pillow", "requests"]))')
        pip_install_block = "\n".join(pip_install_lines)

        # ========== 本地缓存目录 ==========
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools", "pyoxidizer_cache")
        os.makedirs(cache_dir, exist_ok=True)

        self.safe_log(f"📦 缓存目录: {cache_dir}")

        # 发行版文件名
        dist_filename = "cpython-3.10.9+20221220-x86_64-pc-windows-msvc-shared-pgo-full.tar.zst"
        local_dist_path = os.path.join(cache_dir, dist_filename)

        # 如果没有本地缓存，尝试下载
        if not os.path.exists(local_dist_path):
            self.safe_log("⚠️ 未找到本地 Python 发行版缓存，尝试下载...")
            self.progress_var.set(12)
            self.progress_label.config(text="12% - 下载 Python 发行版...")
            self.root.update_idletasks()

            download_url = (
                "https://github.com/indygreg/python-build-standalone/"
                "releases/download/20221220/cpython-3.10.9%2B20221220-x86_64-pc-windows-msvc-shared-pgo-full.tar.zst"
            )

            mirror_urls = [
                f"https://ghproxy.com/{download_url}",
                f"https://mirror.ghproxy.com/{download_url}",
                download_url,
            ]

            downloaded = False
            for url in mirror_urls:
                try:
                    import urllib.request
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=120) as response:
                        with open(local_dist_path, 'wb') as f:
                            f.write(response.read())
                    downloaded = True
                    self.safe_log(f"✅ 下载成功")
                    break
                except Exception as e:
                    self.safe_log(f"⚠️ 下载失败: {e}")
                    continue

            if not downloaded:
                self.safe_log("❌ 无法下载 Python 发行版")
                messagebox.showerror(
                    "错误",
                    f"无法自动下载 Python 发行版。\n\n"
                    f"请手动下载：\n{dist_filename}\n\n"
                    f"放到目录：\n{cache_dir}\n\n"
                    f"下载地址：\n{download_url}"
                )
                return False

        # SHA256 校验值
        dist_sha256 = "9902a5cb5c3b8eb13fb49e8804d16929161c38aa6d64f004d2317ca7c37a06cb"

        # ========== 生成 bzl 配置 ==========
        bzl_content = (
            '# PyOxidizer 配置文件\n'
            '\n'
            'def make_exe():\n'
            f'    dist = PythonDistribution(\n'
            f'        sha256="{dist_sha256}",\n'
            f'        local_path=r"{local_dist_path}",\n'
            f'        flavor="standalone",\n'
            f'    )\n'
            '\n'
            '    policy = dist.make_python_packaging_policy()\n'
            '    policy.resources_location = "in-memory"\n'
            '    policy.resources_location_fallback = "filesystem-relative:prefix"\n'
            '    policy.extension_module_filter = "all"\n'
            '    policy.include_distribution_sources = True\n'
            '    policy.include_distribution_resources = True\n'
            '    policy.include_test = False\n'
            '\n'
            '    python_config = dist.make_python_interpreter_config()\n'
            f'    python_config.run_module = "{entry_module}"\n'
            '\n'
            f'    exe = dist.to_python_executable(\n'
            f'        name="{output_name}",\n'
            '        packaging_policy=policy,\n'
            '        config=python_config,\n'
            '    )\n'
            '\n'
            f'    exe.add_python_resources(exe.read_package_root(\n'
            f'        path=r"{project_output_dir}",\n'
            f'        packages=["{entry_module}"],\n'
            '    ))\n'
            '\n'
            f'{pip_install_block}\n'
            '\n'
            '    return exe\n'
            '\n'
            'def make_embedded_resources(exe):\n'
            '    return exe.to_embedded_resources()\n'
            '\n'
            'def make_install(exe):\n'
            '    files = FileManifest()\n'
            '    files.add_python_resource(".", exe)\n'
            '    return files\n'
            '\n'
            'def register_code_signers():\n'
            '    return\n'
            '\n'
            'register_code_signers()\n'
            'register_target("exe", make_exe)\n'
            'register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)\n'
            'register_target("install", make_install, depends=["exe"], default=True)\n'
            'resolve_targets()\n'
        )

        bzl_path = os.path.join(project_output_dir, "pyoxidizer.bzl")
        with open(bzl_path, "w", encoding="utf-8") as f:
            f.write(bzl_content)

        self.progress_var.set(15)
        self.progress_label.config(text="15% - 配置文件已生成")
        self.root.update_idletasks()

        # 复制源文件
        module_dir = os.path.join(project_output_dir, entry_module)
        os.makedirs(module_dir, exist_ok=True)

        shutil.copy2(input_file, os.path.join(module_dir, "__init__.py"))
        shutil.copy2(input_file, os.path.join(module_dir, "__main__.py"))

        if self.icon_path.get():
            shutil.copy2(self.icon_path.get(), project_output_dir)

        self.progress_var.set(20)
        self.progress_label.config(text="20% - 文件复制完成")
        self.root.update_idletasks()

        # ========== 配置 Cargo 镜像 ==========
        self._setup_project_cargo_mirror(project_output_dir)

        # ========== 构建命令 + 环境变量 ==========
        cmd = ["pyoxidizer", "build", "--path", project_output_dir]

        # 获取系统 Rust 目录，强制 PyOxidizer 使用系统 Rust
        rust_bin_dir = os.path.dirname(rustc_path)  # rustc.exe 所在目录

        env = os.environ.copy()

        # 关键：把系统 Rust/Cargo 放到 PATH 最前面，覆盖 PyOxidizer 自带的
        original_path = env.get("PATH", "")
        env["PATH"] = rust_bin_dir + os.pathsep + original_path

        # 设置 CARGO_HOME 为系统 cargo 目录（如果有）
        system_cargo_home = os.path.join(os.path.expanduser("~"), ".cargo")
        if os.path.exists(system_cargo_home):
            env["CARGO_HOME"] = system_cargo_home

        env["CARGO_REGISTRIES_CRATES_IO_PROTOCOL"] = "git"

        self.safe_log(f"🔧 使用系统 Rust PATH: {rust_bin_dir}")
        self.safe_log(f"🔧 CARGO_HOME: {env.get('CARGO_HOME', '默认')}")

        self.safe_log("🚀 开始 PyOxidizer 打包...")
        self.progress_var.set(25)
        self.progress_label.config(text="25% - 开始编译...")
        self.root.update_idletasks()

        try:
            startupinfo = get_startupinfo()
            system_encoding = locale.getpreferredencoding()

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding=system_encoding,
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
                env=env,
            )

            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1
                    line_lower = line.lower()

                    if "compiling" in line_lower:
                        pct = min(25 + line_count // 10, 70)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 编译中...")
                        self.root.update_idletasks()
                    elif "linking" in line_lower:
                        self.progress_var.set(80)
                        self.progress_label.config(text="80% - 链接中...")
                        self.root.update_idletasks()
                    elif "installing" in line_lower or "finished" in line_lower:
                        self.progress_var.set(90)
                        self.progress_label.config(text="90% - 安装中...")
                        self.root.update_idletasks()

                if (
                        self.pack_btn["text"] == "▶开始打包"
                        and self.process.poll() is None
                ):
                    self.process.terminate()
                    break

            self.process.wait()

            self.progress_var.set(95)
            self.progress_label.config(text="95% - 整理输出文件...")
            self.root.update_idletasks()

            # 查找 exe
            build_base = os.path.join(project_output_dir, "build")
            exe_file = None

            possible_paths = [
                os.path.join(build_base, "x86_64-pc-windows-msvc", "release", "exe", f"{output_name}.exe"),
                os.path.join(build_base, "x86_64-pc-windows-msvc", "release", "install", f"{output_name}.exe"),
                os.path.join(build_base, "x86_64-pc-windows-msvc", "debug", "exe", f"{output_name}.exe"),
                os.path.join(build_base, "x86_64-pc-windows-msvc", "debug", "install", f"{output_name}.exe"),
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    exe_file = path
                    break

            if exe_file:
                final_exe = os.path.join(project_output_dir, f"{output_name}.exe")
                shutil.copy2(exe_file, final_exe)
                self.safe_log(f"✅ 已复制可执行文件到: {final_exe}")

            success = self.process.returncode == 0
            if success:
                self.progress_var.set(100)
                self.progress_label.config(text="100% - 打包完成!")
                self.safe_log(f"✅ PyOxidizer 打包成功！输出位置: {project_output_dir}")
                self._save_config()
            else:
                self.safe_log("❌ PyOxidizer 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _package_pynsist(self, input_file):
        """使用 Pynsist 打包（生成安装程序）"""
        python_cmd = self._get_python()
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False

        # ========== 进度条初始化 ==========
        self.progress_var.set(0)
        self.progress_label.config(text="0% - 准备中...")
        self.root.update_idletasks()
        # =================================

        input_file = self.input_path.get()
        output_name = self.output_name.get()
        base_output_dir = self.output_path.get()
        project_output_dir = os.path.join(
            base_output_dir, output_name.replace(" ", "_")
        )
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")

        self.progress_var.set(5)
        self.progress_label.config(text="5% - 准备环境...")
        self.root.update_idletasks()

        # ========== 设置本地嵌入式 Python 包 ==========
        tools_dir = os.path.join(self.current_dir, "tools")
        embed_python_zip = os.path.join(tools_dir, "python-3.12.0-embed-amd64.zip")

        if os.path.exists(embed_python_zip):
            cache_dir = os.path.join(tools_dir, "pynsist_cache")
            os.makedirs(cache_dir, exist_ok=True)
            os.environ["PYNSIST_CACHE"] = cache_dir

            cached_zip = os.path.join(cache_dir, "python-3.12.0-embed-amd64.zip")
            if not os.path.exists(cached_zip):
                shutil.copy2(embed_python_zip, cached_zip)
                self.safe_log(f"✅ 已复制嵌入式 Python 到缓存")
            else:
                self.safe_log(f"✅ 嵌入式 Python 已存在于缓存")
        else:
            self.safe_log(f"⚠️ 未找到本地嵌入式 Python，将从官网下载")
        # ============================================

        self.progress_var.set(10)
        self.progress_label.config(text="10% - 准备配置文件...")
        self.root.update_idletasks()

        # 获取入口模块名
        entry_module = os.path.basename(input_file).replace(".py", "")

        # 获取 console 设置（默认 True）
        console_setting = (
            self.console_var.get() if hasattr(self, "console_var") else True
        )
        console_value = "true" if console_setting else "false"

        # 生成 installer.cfg 配置文件
        cfg_content = f"""[Application]
name={output_name}
version=1.0
entry_point={entry_module}:main
console={console_value}

[Python]
version=3.12.0
bitness=64

[Build]
directory=build
installer_name={output_name}_Setup.exe

[Include]
pypi_wheels =
files=
"""

        # 如果有图标
        if self.icon_path.get() and os.path.exists(self.icon_path.get()):
            cfg_content = cfg_content.replace(
                "[Include]",
                f"""[Include]
                icon={os.path.basename(self.icon_path.get())}
                """,
            )
            shutil.copy2(self.icon_path.get(), project_output_dir)

        # 写入配置文件
        cfg_path = os.path.join(project_output_dir, "installer.cfg")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(cfg_content)

        self.progress_var.set(15)
        self.progress_label.config(text="15% - 配置文件已生成")
        self.root.update_idletasks()

        # 复制源文件
        shutil.copy2(input_file, project_output_dir)

        # 复制数据文件
        for source, target in self.data_files_list:
            if os.path.exists(source):
                dest_path = os.path.join(project_output_dir, target)
                dest_dir = os.path.dirname(dest_path)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(source, dest_path)
                self.safe_log(f"  📄 复制数据文件: {source} -> {target}")

        self.progress_var.set(20)
        self.progress_label.config(text="20% - 文件复制完成")
        self.root.update_idletasks()

        # 获取 pynsist 命令路径
        pynsist_exe = os.path.join(os.path.dirname(python_cmd), "pynsist.exe")
        if os.path.exists(pynsist_exe):
            cmd = [pynsist_exe, cfg_path, "--no-makensis"]
        else:
            cmd = [python_cmd, "-m", "pynsist", cfg_path, "--no-makensis"]

        self.safe_log(f"🚀 开始生成 NSIS 脚本...")
        self.progress_var.set(25)
        self.progress_label.config(text="25% - 生成 NSIS 脚本...")
        self.root.update_idletasks()

        try:
            startupinfo = get_startupinfo()
            system_encoding = locale.getpreferredencoding()

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding=system_encoding,
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
                env=os.environ,
            )

            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1
                    # 根据输出行数估算进度（25% - 50%）
                    if line_count % 10 == 0:
                        pct = min(25 + line_count // 2, 50)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 生成 NSIS 脚本...")
                        self.root.update_idletasks()

            self.process.wait()

            if self.process.returncode != 0:
                self.safe_log("❌ 生成 NSIS 脚本失败")
                return False

            self.progress_var.set(50)
            self.progress_label.config(text="50% - NSIS 脚本已生成")
            self.root.update_idletasks()

            # ========== 修改生成的 NSIS 脚本，添加桌面快捷方式 ==========
            nsi_file = os.path.join(project_output_dir, "build", "installer.nsi")
            if os.path.exists(nsi_file):
                with open(nsi_file, "r", encoding="utf-8") as f:
                    nsi_content = f.read()

                # 根据 console 设置决定使用 .launch.py 还是 .launch.pyw
                launch_ext = ".launch.py" if console_setting else ".launch.pyw"
                launch_file = f"{output_name}{launch_ext}"

                # 快捷方式指向 python.exe + launch 文件
                python_exe = "$INSTDIR\\Python\\python.exe"

                shortcut_code = f'\n    CreateShortcut "$DESKTOP\\{output_name}.lnk" "{python_exe}" "$INSTDIR\\{launch_file}"\n'

                # 在开始菜单快捷方式后面插入桌面快捷方式
                if "CreateShortcut" in nsi_content:
                    lines = nsi_content.split("\n")
                    new_lines = []
                    inserted = False
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                        if (
                            not inserted
                            and "CreateShortcut" in line
                            and "$SMPROGRAMS" in line
                        ):
                            new_lines.append(shortcut_code)
                            inserted = True
                    if inserted:
                        nsi_content = "\n".join(new_lines)
                        self.safe_log(f"✅ 已添加桌面快捷方式，指向: {launch_file}")
                    else:
                        nsi_content = nsi_content.replace(
                            "SectionEnd", f"{shortcut_code}SectionEnd"
                        )
                        self.safe_log(f"✅ 已添加桌面快捷方式，指向: {launch_file}")
                else:
                    nsi_content = nsi_content.replace(
                        "SectionEnd", f"{shortcut_code}SectionEnd"
                    )
                    self.safe_log(f"✅ 已添加桌面快捷方式，指向: {launch_file}")

                # 写回修改后的 NSIS 脚本
                with open(nsi_file, "w", encoding="utf-8") as f:
                    f.write(nsi_content)

                self.progress_var.set(60)
                self.progress_label.config(text="60% - 已添加快捷方式")
                self.root.update_idletasks()

                # ========== 运行 makensis 编译安装程序 ==========
                # 优先从 tools 目录查找
                makensis_path = None
                tools_dir = os.path.join(self.current_dir, "tools")
                possible_paths = [
                    os.path.join(tools_dir, "NSIS", "makensis.exe"),
                    r"C:\Program Files (x86)\NSIS\makensis.exe",
                    r"C:\Program Files\NSIS\makensis.exe",
                ]

                for path in possible_paths:
                    if os.path.exists(path):
                        makensis_path = path
                        break

                if os.path.exists(makensis_path):
                    self.safe_log(f"🚀 开始编译安装程序...")
                    self.progress_var.set(70)
                    self.progress_label.config(text="70% - 编译安装程序...")
                    self.root.update_idletasks()

                    result = subprocess.run(
                        [makensis_path, nsi_file],
                        cwd=project_output_dir,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )

                    if result.returncode == 0:
                        self.safe_log(f"✅ 安装程序编译成功")
                        self.progress_var.set(90)
                        self.progress_label.config(text="90% - 编译完成")
                        self.root.update_idletasks()

                        # 查找生成的安装程序
                        setup_exe = os.path.join(
                            project_output_dir, "build", f"{output_name}_Setup.exe"
                        )
                        if os.path.exists(setup_exe):
                            self.safe_log(f"✅ 安装程序生成: {setup_exe}")
                            shutil.copy2(
                                setup_exe,
                                os.path.join(
                                    project_output_dir, f"{output_name}_Setup.exe"
                                ),
                            )
                            self.safe_log(
                                f"📦 安装程序大小: {os.path.getsize(setup_exe) / (1024 * 1024):.2f} MB"
                            )
                        else:
                            import glob

                            setup_files = glob.glob(
                                os.path.join(
                                    project_output_dir, "build", "**", "*_Setup.exe"
                                ),
                                recursive=True,
                            )
                            if setup_files:
                                for sf in setup_files:
                                    shutil.copy2(
                                        sf,
                                        os.path.join(
                                            project_output_dir, os.path.basename(sf)
                                        ),
                                    )
                                    self.safe_log(f"✅ 找到安装程序: {sf}")

                        self.progress_var.set(100)
                        self.progress_label.config(text="100% - 打包完成!")
                        self.root.update_idletasks()

                        self.safe_log(
                            f"✅ Pynsist 打包成功！输出位置: {project_output_dir}"
                        )
                        self._save_config()
                        return True
                    else:
                        self.safe_log(f"❌ 编译失败: {result.stderr}")
                        return False
                else:
                    self.safe_log(f"⚠️ 未找到 NSIS 编译器，请安装 NSIS")
                    self.safe_log(f"✅ NSIS 脚本已生成: {nsi_file}")
                    self.safe_log(f"💡 您可以手动修改后运行 makensis 编译")
                    self.progress_var.set(80)
                    self.progress_label.config(
                        text="80% - NSIS 脚本已生成（需手动编译）"
                    )
                    self.root.update_idletasks()
                    return True
            else:
                self.safe_log(f"❌ 未找到生成的 NSIS 脚本: {nsi_file}")
                return False

        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _package_py2app(self, input_file):
        """py2app 打包（仅 macOS）"""
        if sys.platform != "darwin":  # darwin 是 macOS 的内核名称
            self.safe_log("❌ py2app 只能在 macOS 系统上运行")
            self.safe_log("   当前系统: " + sys.platform)
            return False

        python_cmd = self._get_python()
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False

        self.safe_log("⚠️ py2app 创建符合 macOS 规范的应用程序包 (.app)。")

        input_file = self.input_path.get()
        output_name = self.output_name.get()
        base_output_dir = self.output_path.get()
        project_output_dir = os.path.join(
            base_output_dir, output_name.replace(" ", "_")
        )
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")

        # 生成 setup.py（三引号顶格）
        setup_content = f"""# -*- coding: utf-8 -*-
from distutils.core import setup
import py2app

setup(
    console=[{{"script": "{os.path.basename(input_file)}"}}],
        options={{'py2app': {{
            'compressed': True,
            'optimize': 2,
            'bundle_files': 3,  # 改为 3（Python 3.12+ 必须）
            'includes': {self.hidden_imports_list},
            'excludes': {self.exclude_list}
        }}}},
    zipfile=None
)
"""

        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)

        # 复制源文件到输出目录
        shutil.copy2(input_file, project_output_dir)

        # 打包命令
        cmd = [python_cmd, "setup.py", "py2app"]
        self.safe_log(f"🚀 开始 py2app 打包...")
        self.safe_log(f"📝 命令: {' '.join(cmd)}")
        self.root.update()

        # 进度条初始化
        self.progress_var.set(5)
        self.progress_label.config(text="5% - 准备中...")
        self.root.update_idletasks()

        try:
            startupinfo = get_startupinfo()
            system_encoding = locale.getpreferredencoding()
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding=system_encoding,
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )

            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1

                    # 根据输出行数更新进度
                    if "Copying" in line or "copying" in line.lower():
                        pct = min(20 + line_count // 2, 50)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 复制依赖...")
                        self.root.update_idletasks()
                    elif "Building" in line or "building" in line.lower():
                        pct = min(50 + line_count // 3, 80)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 构建中...")
                        self.root.update_idletasks()
                    elif "copy" in line.lower() and "dll" in line.lower():
                        pct = min(80 + line_count // 5, 95)
                        self.progress_var.set(pct)
                        self.progress_label.config(text=f"{pct}% - 复制DLL...")
                        self.root.update_idletasks()

                if (
                    self.pack_btn["text"] == "▶开始打包"
                    and self.process.poll() is None
                ):
                    self.process.terminate()
                    break

            self.process.wait()
            success = self.process.returncode == 0

            if success:
                self.progress_var.set(100)
                self.progress_label.config(text="100% - 完成!")
                self.root.update_idletasks()

                dist_dir = os.path.join(project_output_dir, "dist")
                if os.path.exists(dist_dir):
                    for item in os.listdir(dist_dir):
                        src = os.path.join(dist_dir, item)
                        dst = os.path.join(project_output_dir, item)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                self.safe_log(f"✅ py2app 打包完成！输出位置: {project_output_dir}")
                self._save_config()
            else:
                self.safe_log("❌ py2app 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            self.process = None

    def _start_fake_progress(self, update_interval=0.1, text="准备中...", min_progress=0, max_progress=80):
        """启动分段虚假模拟进度条（简化版）"""
        # 停止之前的
        self._stop_fake_progress()

        self._fake_running = True
        self._fake_current = min_progress

        def fake_progress():
            pct = min_progress
            max_pct = min(max_progress, 100)
            step = 1

            while self._fake_running and pct < max_pct:
                pct += step
                if pct > max_pct:
                    pct = max_pct
                self._fake_current = pct
                self.progress_var.set(pct)
                self.progress_label.config(text=f"{pct}% - {text}")
                self.root.update_idletasks()

                if pct >= max_pct:
                    break
                time.sleep(update_interval)

                # 动态调整步长
                if max_pct - min_progress <= 10:
                    step = 1
                elif max_pct - min_progress <= 30:
                    step = 2
                else:
                    step = 3

            self._fake_running = False

        self._fake_thread = threading.Thread(target=fake_progress, daemon=True)
        self._fake_thread.start()

    def _stop_fake_progress(self, inherit_progress=True):
        """停止虚假进度"""
        # 设置标志让线程退出
        self._fake_running = False

        # 等待线程结束
        if hasattr(self, '_fake_thread') and self._fake_thread and self._fake_thread.is_alive():
            self._fake_thread.join(timeout=0.5)

        current = getattr(self, '_fake_current', 0)

        if inherit_progress:
            return current
        return 0

    def _update_real_progress(self, pct, text=""):
        """更新真实进度"""
        current = self.progress_var.get()
        if pct > current:
            self.progress_var.set(pct)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()

    # ==================== 状态栏 ====================
    def status_start(self, text, color="gray"):
        colors = {"gray": "#9e9e9e", "red": "#f44336", "orange": "#ff9800", "green": "#4caf50",
                  "blue": "#2196f3", "purple": "#9c27b0", "cyan": "#00bcd4", "pink": "#e91e63"}
        self.status_color = colors.get(color, "#9e9e9e")
        self._target = 0
        self._current = 0
        self._smooth = False
        self._base = text
        def _start():
            self.status_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.status_canvas.delete("bar")
            self.status_canvas.update_idletasks()
            w = max(self.status_canvas.winfo_width(), 200)
            self.status_bar_id = self.status_canvas.create_rectangle(0, 0, 0, 14, fill=self.status_color, outline='', tags="bar")
            self.status_var.set(text)
            # 重新显示百分比标签
            self.status_pct.pack(side=tk.LEFT, padx=2)
            self.status_pct.config(text="0%")
        self.root.after(0, _start)

    def status_set_target(self, target, text=None, color=None):
        if color:
            self.status_set_color(color)
        if text:
            self._base = text
            self.status_var.set(text)
        self._target = min(target, 100)

        if getattr(self, '_smooth', False):
            return

        def smooth():
            self._smooth = True
            while self._current < 100:
                if self._current < self._target:
                    self._current += 1
                    self._update_progress(self._current)
                    time.sleep(0.03)
                else:
                    time.sleep(0.1)
            self._smooth = False

        threading.Thread(target=smooth, daemon=True).start()
        
    def status_set_color(self, color):
        colors = {"gray": "#9e9e9e", "red": "#f44336", "orange": "#ff9800", "green": "#4caf50",
                 "blue": "#2196f3", "purple": "#9c27b0", "cyan": "#00bcd4", "pink": "#e91e63",
                 "lightblue": "#64b5f6", "lightgreen": "#81c784", "lightpink": "#f06292"}
        c = colors.get(color, "#9e9e9e")
        def _set():
            if self.status_bar_id:
                self.status_canvas.itemconfig(self.status_bar_id, fill=c)
        self.root.after(0, _set)

    def _update_progress(self, value):
        def _do():
            if self.status_bar_id and self.status_canvas.winfo_exists():
                self.status_canvas.update_idletasks()
                # 获取 canvas 实际宽度
                canvas_width = self.status_canvas.winfo_width()
                if canvas_width <= 0:
                    canvas_width = 200  # 默认宽度
                bar_width = canvas_width if value >= 100 else int(canvas_width * value / 100)
                self.status_canvas.coords(self.status_bar_id, 0, 0, bar_width, 14)
            self.status_pct.config(text=f"{value}%")
        self.root.after(0, _do)

    def status_finish(self, text="就绪"):
        """完成并隐藏进度条"""
        def _finish():
            try:
                self.status_canvas.pack_forget()
                self.status_var.set(text)
                self.status_pct.config(text="")  # 清空百分比文字
                self.status_pct.pack_forget()   # 隐藏百分比标签
                self._current = 0
                self._target = 0
                self._smooth = False
                # 重置进度条宽度
                self.status_canvas.configure(width=0)
            except:
                pass

        # 先设置进度到100
        self.status_set_target(100, text, color="green")
        # 延迟1秒后隐藏
        self.root.after(1500, _finish)

    # ==================== 文件操作 ====================
    def _save_config(self):
        f = self.input_path.get()
        if not f:
            return
        out = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"))
        os.makedirs(out, exist_ok=True)
        cfg = os.path.join(out, f"{os.path.splitext(os.path.basename(f))[0].replace(' ', '_')}.json")
        data = {
            "input_file": f,
            "output_dir": self.output_path.get(),
            "output_name": self.output_name.get(),
            "icon_path": self.icon_path.get(),
            "package_type": self.package_type.get(),
            "packer_type": self.packer_type.get(),
            "nuitka_jobs": self.nuitka_jobs.get(),
            "nuitka_backend": self.nuitka_backend.get(),
            "target_platform": self.target_platform.get(),
            "debug_mode": self.debug_mode.get(),
            #"use_venv": self.use_venv,
            # ❌ 不保存这些全局配置
            # "use_upx": self.use_upx.get(),
            # "upx_path": self.upx_path.get(),
            # "python_path": self.custom_python_path.get(),
            "hidden_imports": self.hidden_imports_list,
            "data_files": self.data_files_list,
            "exclude_list": self.exclude_list,
        }
        try:
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.safe_log("✓ 项目配置已保存")
        except Exception as e:
            self.safe_log(f"❌ 保存配置失败: {e}")

    def _load_config(self):
        f = self.input_path.get()
        if not f:
            return
        cfg = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"),
                           f"{os.path.splitext(os.path.basename(f))[0].replace(' ', '_')}.json")
        if not os.path.exists(cfg):
            return
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 只加载项目相关配置（不加载全局配置）
            self.output_path.set(data.get("output_dir", self.dist_dir))
            self.output_name.set(data.get("output_name", self._get_default_name()))
            self.icon_path.set(data.get("icon_path", ""))
            self.package_type.set(data.get("package_type", "onefile"))
            self.packer_type.set(data.get("packer_type", "PyInstaller"))
            self.nuitka_jobs.set(data.get("nuitka_jobs", "auto"))
            self.nuitka_backend.set(data.get("nuitka_backend", "auto"))
            self.target_platform.set(data.get("target_platform", "current"))
            self.debug_mode.set(data.get("debug_mode", False))
            self.use_venv = data.get("use_venv", False)

            if hasattr(self, 'venv_switch'):
                self.venv_switch.set(self.use_venv)

            # 加载项目特有的隐藏导入、数据文件、排除列表
            self.clear_hidden_imports()
            for imp in data.get("hidden_imports", []):
                self.hidden_imports_list.append(imp)
                self.hidden_listbox.insert(tk.END, imp)

            self.clear_data_files()
            for item in data.get("data_files", []):
                if isinstance(item, list) and len(item) == 2:
                    s, t = item
                    if os.path.exists(s):
                        self.data_files_list.append((s, t))
                        self.data_listbox.insert(tk.END, f"{os.path.basename(s)} -> {t}")

            self.clear_excludes()
            for e in data.get("exclude_list", []):
                self.exclude_list.append(e)
                self.exclude_listbox.insert(tk.END, e)
            self._update_exclude_count()

            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                self.icon_label.config(text=f"✓ {os.path.basename(self.icon_path.get())}", foreground="green")

            self.safe_log("✓ 已加载项目配置")
            self._on_packer_changed()
        except Exception as e:
            self.safe_log(f"⚠️ 加载配置失败: {e}")

    def _async_load_config(self):
        """异步加载项目配置"""
        try:
            f = self.input_path.get()
            if not f:
                return

            cfg = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"),
                               f"{os.path.splitext(os.path.basename(f))[0].replace(' ', '_')}.json")

            if not os.path.exists(cfg):
                return

            with open(cfg, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 在主线程中更新UI
            self.root.after(0, lambda: self._apply_config(data))
        except Exception as e:
            self.root.after(0, lambda: self.safe_log(f"⚠️ 加载配置失败: {e}"))

    def _apply_config(self, data):
        """在主线程中应用配置"""
        try:
            self.output_path.set(data.get("output_dir", self.dist_dir))
            self.output_name.set(data.get("output_name", self._get_default_name()))
            self.icon_path.set(data.get("icon_path", ""))
            self.package_type.set(data.get("package_type", "onefile"))
            self.packer_type.set(data.get("packer_type", "PyInstaller"))
            self.nuitka_jobs.set(data.get("nuitka_jobs", "auto"))
            self.nuitka_backend.set(data.get("nuitka_backend", "auto"))
            self.target_platform.set(data.get("target_platform", "current"))
            self.debug_mode.set(data.get("debug_mode", False))
            #self.use_venv = data.get("use_venv", False)

            # 虚拟开关始终默认关闭，不加载保存的状态
            self.use_venv = False
            if hasattr(self, 'venv_switch'):
                self.venv_switch.set(False)

            # 加载隐藏导入
            for imp in data.get("hidden_imports", []):
                if imp not in self.hidden_imports_list:
                    self.hidden_imports_list.append(imp)
                    self.hidden_listbox.insert(tk.END, imp)

            # 加载数据文件
            for item in data.get("data_files", []):
                if isinstance(item, list) and len(item) == 2:
                    s, t = item
                    if os.path.exists(s) and (s, t) not in self.data_files_list:
                        self.data_files_list.append((s, t))
                        self.data_listbox.insert(tk.END, f"{os.path.basename(s)} -> {t}")

            # 加载排除列表
            for e in data.get("exclude_list", []):
                if e not in self.exclude_list:
                    self.exclude_list.append(e)
                    self.exclude_listbox.insert(tk.END, e)

            self._update_hidden_count()
            self._update_data_count()
            self._update_exclude_count()

            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                self.icon_label.config(text=f"✓ {os.path.basename(self.icon_path.get())}", foreground="green")

            self._on_packer_changed()
            self.safe_log("✓ 项目配置已加载")
        except Exception as e:
            self.safe_log(f"⚠️ 应用配置失败: {e}")

    def _save_python_config(self):
        """保存Python路径到全局缓存"""
        self.global_cache['python'] = {
            'path': self.custom_python_path.get(),
            'timestamp': time.time()
        }
        self._save_global_cache()

    def _load_python_config(self):
        """加载Python路径从全局缓存"""
        python_data = self.global_cache.get('python', {})
        python_path = python_data.get('path', '')
        if python_path and os.path.exists(python_path):
            self.custom_python_path.set(python_path)
            if hasattr(self, 'python_path_entry'):
                self.python_path_entry.delete(0, tk.END)
                self.python_path_entry.insert(0, python_path)
                self._update_python_btn()
            return True
        return False

    def _export_log(self):
        log = self.log_text.get(1.0, tk.END).strip()
        if not log:
            messagebox.showwarning("提示", "日志为空")
            return
        name = f"{self.output_name.get()}_打包日志_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=self.output_path.get() or self.current_dir,
                                           initialfile=name, filetypes=[("Text", "*.txt"), ("Log", "*.log")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"输入: {self.input_path.get()}\n输出: {self.output_path.get()}\n名称: {self.output_name.get()}\n")
                f.write(f"打包器: {self.packer_type.get()}\n模式: {self.package_type.get()}\n{'='*50}\n\n")
                f.write(log)
            self.safe_log(f"✅ 日志已导出: {path}")
            messagebox.showinfo("成功", f"已导出到:\n{path}")
        except Exception as e:
            self.safe_log(f"❌ 导出失败: {e}")

    def _open_output(self):
        base_path = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"))

        # 去掉可能的 .exe 后缀
        if base_path.lower().endswith('.exe'):
            base_path = base_path[:-4]

        # 优先打开文件夹
        folder_path = base_path
        if os.path.isdir(folder_path):
            dir_to_open = folder_path
        else:
            # 文件夹不存在，尝试打开父目录
            dir_to_open = self.output_path.get()

        # 确保打开的是目录
        if not os.path.isdir(dir_to_open):
            messagebox.showwarning("提示", f"目录不存在:\n{dir_to_open}")
            return

        # 使用 explorer 打开文件夹（Windows）
        if sys.platform == "win32":
            subprocess.run(f'explorer "{dir_to_open}"', shell=True)
        elif sys.platform == "darwin":
            subprocess.run(["open", dir_to_open])
        else:
            subprocess.run(["xdg-open", dir_to_open])

        self.safe_log(f"📂 已打开输出目录: {dir_to_open}")

    def _reset(self):
        default = self._find_default_py()
        if default:
            self.input_path.set(default)
            self.output_name.set(self._get_default_name())

            # 删除配置文件
            cfg_file = os.path.join(self.output_path.get(), self.output_name.get().replace(" ", "_"),
                                    f"{os.path.splitext(os.path.basename(default))[0].replace(' ', '_')}.json")
            if os.path.exists(cfg_file):
                try:
                    os.remove(cfg_file)
                except:
                    pass

        self.output_path.set(self.dist_dir)
        self.package_type.set("onefile")
        self.packer_type.set("PyInstaller")
        self.nuitka_jobs.set("auto")
        self.nuitka_backend.set("auto")
        self.target_platform.set("current")
        self.use_upx.set(True)
        self.debug_mode.set(False)
        self._clear_all()
        self._on_packer_changed()
        self.safe_log("✓ 已恢复默认设置")

    def _get_mingw_dir(self):
        if self.mingw_path:
            return self.mingw_path
        import shutil
        gcc = shutil.which("gcc")
        return os.path.dirname(gcc) if gcc else None

    def _get_msvc_dir(self):
        if self.msvc_path:
            return self.msvc_path
        import shutil
        cl = shutil.which("cl.exe")
        return os.path.dirname(cl) if cl else None

def main():
    # ========== 强制切换到 exe 所在目录 ==========
    if getattr(sys, 'frozen', False):
        try:
            if sys.platform == 'win32':
                import ctypes
                buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.kernel32.GetModuleFileNameW(
                    ctypes.wintypes.HMODULE(0),
                    buffer,
                    ctypes.wintypes.MAX_PATH
                )
                exe_dir = os.path.dirname(buffer.value)
            else:
                exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

            if os.path.exists(exe_dir):
                os.chdir(exe_dir)
        except:
            pass
    # ===========================================
    try:
        app = PackageGUI()
        app.root.mainloop()
    except Exception as e:
        pass
    finally:
        os._exit(0)

if __name__ == "__main__":
    main()