#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Python脚本打包工具 - PyQt6完整版 """
import sys, json, time, ast, shutil, subprocess, threading, multiprocessing, io
import tempfile, webbrowser, fnmatch, glob, ctypes, platform as sys_platform
import urllib.request, zipfile, traceback
from pathlib import Path
from datetime import datetime
from collections import Counter
import os, re, stat,unicodedata,textwrap,difflib,io,functools,psutil,datetime
from contextlib import redirect_stdout, redirect_stderr
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *  
from PIL import Image
try:
    from PyQt6.QtMultimedia import QMediaPlayer
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    MEDIA_AVAILABLE = True
except (ImportError, AttributeError):
    MEDIA_AVAILABLE = False
VERSION = "8.0.0"
BUILD_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
AUTHOR = "wcj6376"
# ==================== 镜像源 ====================
MIRRORS = [
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://mirrors.aliyun.com/pypi/simple/",
    "https://pypi.mirrors.ustc.edu.cn/simple/"
]
# 默认使用第一个
MIRROR = MIRRORS[0]
# ==================== 常量定义 ====================
STANDARD_LIBS = frozenset({
    'abc','argparse','array','ast','asyncio','atexit','base64','bdb','binascii',
    'bisect','builtins','bz2','calendar','cgi','cgitb','chunk','cmath','cmd',
    'code','codecs','codeop','collections','colorsys','compileall','concurrent',
    'configparser','contextlib','contextvars','copy','copyreg','csv','ctypes',
    'dataclasses','datetime','dbm','decimal','difflib','dis','email','encodings',
    'enum','faulthandler','fnmatch','fractions','ftplib','functools','fcntl','gc',
    'getopt','getpass','gettext','glob','graphlib','gzip','hashlib','heapq',
    'hmac','html','http','idlelib','imaplib','imghdr','importlib','inspect',
    'io','ipaddress','itertools','json','keyword','linecache','locale','logging',
    'lzma','mailbox','mailcap','marshal','math','mimetypes','mmap','modulefinder','msvcrt',
    'multiprocessing','netrc','nis','nntplib','numbers','operator','optparse',
    'os','ossaudiodev','pathlib','pdb','pickle','pickletools','pipes','pkgutil',
    'platform','plistlib','poplib','posix','posixpath','pprint','profile','pstats',
    'pty','pwd','py_compile','pyclbr','pydoc','queue','quopri','random','re',
    'readline','reprlib','resource','rlcompleter','runpy','sched','secrets',
    'select','selectors','shelve','shlex','shutil','signal','site','smtpd',
    'smtplib','sndhdr','socket','socketserver','spwd','sqlite3','ssl','stat',
    'statistics','string','stringprep','struct','subprocess','sunau','symtable',
    'sys','sysconfig','syslog','tabnanny','tarfile','telnetlib','tempfile',
    'termios','test','textwrap','threading','time','timeit','tkinter','token',
    'tokenize','trace','traceback','tracemalloc','tty','turtle','types','typing',
    'unicodedata','unittest','urllib','uu','uuid','venv','warnings','wave',
    'weakref','webbrowser','winreg','wsgiref','xml','xmlrpc','zipapp','zipfile',
    'zipimport','zlib','_thread','__future__','zoneinfo','tomllib','typing_extensions'
})
MODULE_TO_PACKAGE = {
    'cv2':'opencv-python','PIL':'Pillow','skimage':'scikit-image','sklearn':'scikit-learn',
    'bs4':'beautifulsoup4','yaml':'PyYAML','Image':'Pillow','ImageDraw':'Pillow','docx':'python-docx',
    'pyautogui':'PyAutoGUI','wx':'wxPython','qtpy':'QtPy','PySide2':'PySide2','clr': 'pythonnet',
    'PySide6':'PySide6','PyQt5':'PyQt5','PyQt6':'PyQt6','dateutil':'python-dateutil',
    'dotenv':'python-dotenv','jwt':'PyJWT','lxml':'lxml','OpenGL':'PyOpenGL',
    'redis':'redis','requests':'requests','selenium':'selenium','sqlalchemy':'SQLAlchemy',
    'matplotlib':'matplotlib','numpy':'numpy','pandas':'pandas','scipy':'scipy',
    'torch':'torch','tensorflow':'tensorflow','flask':'Flask','django':'Django',
    'fastapi':'fastapi','tornado':'tornado','aiohttp':'aiohttp','grpc':'grpcio',
    'protobuf':'protobuf','pydantic':'pydantic','typer':'typer','rich':'rich',
    'click':'click','jinja2':'Jinja2','markupsafe':'MarkupSafe','werkzeug':'Werkzeug',
    'itsdangerous':'itsdangerous','LibreHardwareMonitor': 'PyLibreHardwareMonitor',
    'win32api':'pywin32','win32con':'pywin32','win32gui':'pywin32','win32ui':'pywin32',
    'win32file':'pywin32','win32process':'pywin32','win32security':'pywin32',
    'win32service':'pywin32','win32net':'pywin32','win32event':'pywin32',
    'win32pipe':'pywin32','win32clipboard':'pywin32','win32console':'pywin32',
    'win32profile':'pywin32','win32cred':'pywin32','win32crypt':'pywin32',
    'win32job':'pywin32','win32ras':'pywin32','win32timezone':'pywin32',
    'win32wnet':'pywin32','win32com':'pywin32','win32com.client':'pywin32',
    'win32com.server':'pywin32','pywin32':'pywin32','dde':'pywin32','odbc':'pywin32',
    'win32help':'pywin32','win32inet':'pywin32','win32mail':'pywin32',
    'win32mapi':'pywin32','win32pdh':'pywin32','win32print':'pywin32',
    'win32trace':'pywin32','win32transaction':'pywin32','win32evtlog':'pywin32',
    'win32perf':'pywin32','win32ts':'pywin32','win32usb':'pywin32','win32verstamp':'pywin32'
}
EXCLUDE_PACKAGES = frozenset({
    '_pytest','astroid','asttokens','autopep8','backcall','black','build',
    'charset_normalizer','coverage','Cython','cython','debugpy','decorator','distribute',
    'executing','fancycompleter','flake8','ipykernel','ipython','ipywidgets','isort',
    'jedi','jupyter','jupyter_client','jupyter_core','jupyterlab','matplotlib-inline',
    'mccabe','mock','module','mypy','mypy_extensions','mypyc','nbconvert','nbformat',
    'nose','notebook','packaging','pathspec','pdbpp','pep517','pip','pkg_resources',
    'platformdirs','pluggy','prompt_toolkit','ptpython','pure_eval','py','pycodestyle',
    'pyflakes','pygments','pyi_hooks','pyi_hooks_contrib','pyinstaller',
    'pyinstaller-hooks-contrib','pylint','pyproject_hooks','pywin32_ctypes',
    'pytest','pywin32','qtconsole','stack_data','test','tests','tox','traitlets',
    'typed_ast','typeshed_client','unittest2','venv','virtualenv','wcwidth','wheel',
    'wmctrl','win32','win32con','yaml','pyyaml'
})
BASELINE_EXCLUDE = frozenset({
    # --- 测试框架 ---
    'pytest', '_pytest', 'py', 'nose', 'nose2', 'mock', 'unittest2', 'tox',
    'coverage', 'hypothesis', 'pytest_cov', 'pytest_xdist',
    # --- 代码质量 / 静态检查 ---
    'pylint', 'astroid', 'flake8', 'pycodestyle', 'pyflakes', 'mccabe',
    'black', 'isort', 'autopep8', 'yapf', 'bandit', 'pydocstyle',
    'mypy', 'mypy_extensions', 'mypyc', 'typed_ast', 'pathspec',
    # --- 交互式解释器 / Notebook（PyInstaller 分析重灾区）---
    'IPython', 'ipython', 'ipykernel', 'ipywidgets', 'jupyter',
    'jupyter_client', 'jupyter_core', 'jupyterlab', 'jupyterlab_server',
    'notebook', 'nbconvert', 'nbformat', 'nbclient', 'qtconsole',
    'traitlets', 'jedi', 'parso', 'prompt_toolkit', 'pygments', 'wcwidth',
    'backcall', 'pickleshare', 'matplotlib_inline', 'stack_data',
    'executing', 'asttokens', 'pure_eval', 'debugpy', 'pydevd',
    # --- 打包 / 构建工具链 ---
    'PyInstaller', 'pyinstaller', 'cx_Freeze', 'nuitka', 'py2exe', 'py2app',
    'pkg_resources', 'pip', 'wheel', 'build', 'pep517',
    'pyproject_hooks', 'virtualenv', 'pipenv', 'poetry', 'twine',
    'setuptools_scm', 'distutils_hack', '_distutils_hack',
    # --- 文档工具 ---
    'sphinx', 'docutils', 'alabaster', 'snowballstemmer', 'imagesize',
    'sphinxcontrib',
    # --- 重型科学计算（未被实际 import 时排除）---
    'scipy', 'matplotlib', 'sympy', 'numba', 'llvmlite', 'torch',
    'tensorflow', 'keras', 'sklearn', 'scikit_learn', 'seaborn', 'plotly',
    'bokeh', 'statsmodels', 'h5py', 'tables', 'numexpr', 'bottleneck',
    'pyarrow', 'fastparquet', 'dask', 'xarray', 'sqlalchemy',
    # --- GUI 框架（互斥，未被 import 时排除，否则体积暴涨）---
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'qtpy', 'wx', 'kivy', 'pygame',
    'PyQt5_sip', 'PyQt6_sip', 'shiboken2', 'shiboken6',
    # --- 网络 / Web 框架 ---
    'selenium', 'scrapy', 'django', 'flask', 'tornado', 'aiohttp', 'fastapi',
    # --- 标准库中的冗余部分 ---
    'lib2to3', 'pydoc_data', 'idlelib', 'turtledemo', 'tkinter.test',
    'test', 'tests', 'distutils.command.bdist_msi',
})
RUNTIME_SAFE_KEEP = frozenset({
    'six', 'typing_extensions', 'typing-extensions', 'packaging',
    'zipp', 'importlib_metadata', 'importlib-metadata',
    'importlib_resources', 'importlib-resources',
    'pytz', 'tzdata', 'tzlocal', 'python_dateutil', 'python-dateutil',
    'dateutil', 'certifi', 'idna', 'urllib3',
    'charset_normalizer', 'charset-normalizer',
    'et_xmlfile', 'et-xmlfile', 'attrs', 'attr',
    'pyparsing', 'setuptools_rust', 'cffi', 'pycparser',
})
DEPENDENCY_MAP = {
    'requests': ['urllib3', 'certifi', 'idna', 'charset_normalizer'],
    'openpyxl': ['et_xmlfile'],
    'pandas': ['numpy', 'pytz', 'python-dateutil', 'six', 'tzdata'],
    'python-dateutil': ['six'],
    'dateutil': ['six'],
    'docx': ['lxml', 'typing_extensions', 'python-docx'],
    'python-docx': ['lxml', 'typing_extensions', 'python-docx'],
    'matplotlib': ['numpy', 'pillow', 'kiwisolver', 'pyparsing'],
    'scikit-learn': ['numpy', 'scipy', 'joblib', 'threadpoolctl'],
    'sklearn': ['numpy', 'scipy', 'joblib', 'threadpoolctl'],
    'Image': ['pillow'],
    'opencv': ['opencv-python','numpy'],
    'cv2': ['opencv-python','numpy'],
    'GPUtil': ['setuptools', 'nvidia-ml-py'],
    'win32api': ['pywin32'],
    'win32con': ['pywin32'],
    'win32gui': ['pywin32'],
    'win32com': ['pywin32'],
    }
FILTER_MODULES = frozenset({
    'PyInstaller', 'module', 'pyi_hooks_contrib', 'pyi_hooks',
    'pip', 'wheel', 'distribute', 'pkg_resources',
    'unittest', 'test', 'tests', 'pythonwin', 'pywin32_system32',
    'pytest', 'nose', 'mock', 'tox', 'coverage',
    'pylint', 'flake8', 'black', 'mypy', 'isort', 'autopep8',
    'jupyter', 'ipython', 'notebook', 'ipykernel',
    'pyinstaller', 'pyinstaller-hooks-contrib', 'pywin32-ctypes',
    'build', 'packaging', 'pep517', 'pyproject_hooks',
    'yaml', 'pyyaml',
})
NEVER_PACK = frozenset({
    'pyinstaller', 'pyi_hooks_contrib', 'pyi_hooks',
    'pywin32_ctypes', 'pip', 'wheel', 'pkg_resources', 'distribute'
})
def get_startupinfo():
    """获取启动信息，隐藏控制台窗口"""
    if sys.platform == 'win32':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return si
    return None

def get_exe_directory():
    if getattr(sys, 'frozen', False) or os.environ.get('NUITKA_ONEFILE_PARENT') is not None:
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.dirname(os.path.abspath(__file__))
APP_BASE_PATH = get_exe_directory()

def _get_real_python():
    """获取真实的Python解释器路径"""
    import os
    import subprocess
    import sys
    # 源码模式
    if not getattr(sys, 'frozen', False):
        return sys.executable

    def is_same_file(path1, path2):
        """判断两个路径是否指向同一文件（跨平台）"""
        try:
            return os.path.samefile(path1, path2)
        except:
            return os.path.abspath(path1) == os.path.abspath(path2)

    def is_valid_python(path):
        """检查是否是有效的Python且不是当前exe"""
        if not path or not os.path.exists(path):
            return False
        if is_same_file(path, sys.executable):
            return False
        try:
            result = subprocess.run(
                [path, '--version'],
                capture_output=True, text=True, timeout=2,
                startupinfo=get_startupinfo()
            )
            return result.returncode == 0 and ('Python' in result.stdout or 'Python' in result.stderr)
        except:
            return False
        if sys.platform == 'win32':
            try:
                result = self._run_hidden(['py', '-c', 'import sys; print(sys.executable)'],
                                          capture_output=True, text=True, timeout=5,
                                          startupinfo=get_startupinfo())
                if result.returncode == 0 and result.stdout.strip():
                    py_path = result.stdout.strip()
                    if is_valid_python(py_path):
                        return py_path
            except Exception:
                pass
        for py_name in ['python3', 'python']:
            try:
                result = self._run_hidden([py_name, '-c', 'import sys; print(sys.executable)'],
                                          capture_output=True, text=True, timeout=5,
                                          startupinfo=get_startupinfo())
                if result.returncode == 0 and result.stdout.strip():
                    py_path = result.stdout.strip()
                    if is_valid_python(py_path):
                        return py_path
            except Exception:
                pass
        if sys.platform == 'win32':
            username = os.environ.get('USERNAME', '')
            default_paths = [
                r'C:\Python312\python.exe',
                r'C:\Python311\python.exe',
                r'C:\Python310\python.exe',
                r'C:\Python39\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python312\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python311\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python310\python.exe',
            ]
        elif sys.platform == 'darwin':
            default_paths = [
                '/usr/local/bin/python3',
                '/usr/bin/python3',
                '/opt/homebrew/bin/python3',
            ]
        else:
            default_paths = [
                '/usr/bin/python3',
                '/usr/local/bin/python3',
                '/usr/bin/python',
            ]
        for p in default_paths:
            if is_valid_python(p):
                return p
        if hasattr(sys, '_MEIPASS'):
            meipass = sys._MEIPASS
            search_dir = os.path.dirname(meipass)
            for root, dirs, files in os.walk(search_dir):
                for f in files:
                    if f.lower() in ('python.exe', 'python3.exe', 'python'):
                        p = os.path.join(root, f)
                        if is_valid_python(p):
                            return p
                if len(root) > len(search_dir) + 100:
                    break
        import shutil
        for cmd in ['python3', 'python']:
            p = shutil.which(cmd)
            if p and is_valid_python(p):
                return p
        return None

def get_cache_dir():
    """获取可写的缓存目录"""
    exe_dir = get_exe_directory()
    if os.access(exe_dir, os.W_OK):
        return exe_dir
    import tempfile
    fallback = os.path.join(tempfile.gettempdir(), "PyPackTool")
    os.makedirs(fallback, exist_ok=True)
    return fallback

def load_dep_map():
    """加载依赖映射表（独立配置文件，不影响原有缓存）"""
    global DEPENDENCY_MAP
    if os.path.exists(DEP_MAP_FILE):
        try:
            import tomllib
            with open(DEP_MAP_FILE, 'rb') as f:
                data = tomllib.load(f)
                if data:
                    DEPENDENCY_MAP = data
                    return
        except Exception:
            pass
    # ===== 不存在则用源码中的 DEPENDENCY_MAP 创建 =====
    try:
        with open(DEP_MAP_FILE, 'w', encoding='utf-8-sig') as f:
            for mod, deps in DEPENDENCY_MAP.items():
                deps_str = ', '.join([f'"{d}"' for d in deps])
                f.write(f'{mod} = [{deps_str}]\n')
    except Exception:
        pass

def load_cache():
    """加载缓存 - 优先内存"""
    global _memory_cache
    if _memory_cache is not None:
        return _memory_cache
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8-sig') as f:
                _memory_cache = json.load(f)
                return _memory_cache
    except:
        pass
    _memory_cache = {}
    return _memory_cache

def save_cache(cache):
    """保存缓存到文件并更新内存"""
    global _memory_cache
    _memory_cache = cache
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8-sig') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except:
        pass

def now_str():
    """返回当前时间的字符串格式 HH:MM:SS.mmm"""
    import datetime
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S") + f".{now.microsecond//1000:03d}"

def pip_install(python_exe, package, env=None, timeout=300, quiet=False):
    """
    安装包，失败时自动切换镜像源
    返回: (success, result)
    """
    global MIRROR
    if env is None:
        env = {'PATH': os.environ.get('PATH', '')}
        if sys.platform == 'win32':
            env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
    # 构建参数
    cmd = [python_exe, '-m', 'pip', 'install', package]
    if quiet:
        cmd.append('-q')
    cmd.append('--no-warn-script-location')
    for mirror in MIRRORS:
        try:
            # 每次用当前镜像
            cmd_with_mirror = cmd + ['-i', mirror]
            result = subprocess.run(
                cmd_with_mirror,
                capture_output=True, text=True,
                env=env,
                timeout=timeout
            )
            if result.returncode == 0:
                MIRROR = mirror
                return True, result
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return False, None
DEP_MAP_FILE = os.path.join(get_exe_directory(), ".dep_map.toml")
# ===== 全局内存缓存 =====
_memory_cache = None

class PythonInstallWorker(QThread):
    """后台静默安装 Python """
    finished_signal = pyqtSignal(bool, str)
    def __init__(self):
        super().__init__()
        self._cancel = False
        self._progress = 0

    def cancel(self):
        self._cancel = True

    def run(self):
        import urllib.request
        import ssl
        import tempfile
        import os
        import subprocess
        import time
        import sys
        try:
            version = "3.12.10"
            temp_dir = tempfile.gettempdir()
            has_python, version_str = check_python_installed()
            if has_python:
                self.finished_signal.emit(True, f"Python {version_str} 已安装")
                return
            if sys.platform == 'win32':
                filename = f"python-{version}-amd64.exe"
                mirrors = [
                    f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe",
                    f"https://mirrors.tuna.tsinghua.edu.cn/python/{version}/python-{version}-amd64.exe",
                    f"https://mirrors.aliyun.com/python/{version}/python-{version}-amd64.exe",
                    f"https://mirrors.ustc.edu.cn/python/{version}/python-{version}-amd64.exe",
                ]
            elif sys.platform == 'darwin':
                filename = f"python-{version}-macos11.pkg"
                mirrors = [
                    f"https://www.python.org/ftp/python/{version}/python-{version}-macos11.pkg",
                    f"https://mirrors.tuna.tsinghua.edu.cn/python/{version}/python-{version}-macos11.pkg",
                ]
            else:
                self.finished_signal.emit(False, "Linux请使用包管理器安装Python")
                return
            installer_path = os.path.join(temp_dir, filename)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            downloaded = False
            last_error = ""
            for i, url in enumerate(mirrors):
                if self._cancel:
                    self.finished_signal.emit(False, "已取消")
                    return
                try:
                    self.finished_signal.emit(False, f"下载中... 尝试镜像 {i+1}/{len(mirrors)}")
                    req = urllib.request.Request(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    with urllib.request.urlopen(req, context=ssl_context, timeout=60) as response:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded_size = 0
                        if os.path.exists(installer_path):
                            if total_size > 0 and os.path.getsize(installer_path) == total_size:
                                downloaded = True
                                break
                        with open(installer_path, 'wb') as f:
                            while not self._cancel:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                if total_size > 0:
                                    progress = int(downloaded_size * 100 / total_size)
                                    if progress != self._progress:
                                        self._progress = progress
                                        self.finished_signal.emit(False, f"下载中... {progress}%")
                    if os.path.exists(installer_path):
                        file_size = os.path.getsize(installer_path)
                        if file_size > 5 * 1024 * 1024:  
                            downloaded = True
                            self.finished_signal.emit(False, f"下载完成 ({file_size // 1024 // 1024}MB)")
                            break
                        else:
                            os.remove(installer_path)
                            last_error = f"文件太小 ({file_size} bytes)"
                except Exception as e:
                    last_error = str(e)
                    continue
            if self._cancel:
                self.finished_signal.emit(False, "已取消")
                return
            if not downloaded:
                self.finished_signal.emit(False, f"下载失败: {last_error}")
                return
            self.finished_signal.emit(False, "安装中... 请稍候")
            if sys.platform == 'win32':
                cmd = [
                    installer_path,
                    '/quiet',
                    'InstallAllUsers=1',
                    'PrependPath=1',
                    'Include_doc=0',
                    'Include_tcltk=0',
                    'Include_test=0',
                    'Include_tools=0',
                    'Include_pip=1',
                    'Include_setuptools=1',
                    'Include_symbols=0',
                    'Include_debug=0',
                    'InstallLauncherAllUsers=1',
                ]
            elif sys.platform == 'darwin':
                cmd = ['sudo', 'installer', '-pkg', installer_path, '-target', '/']
            else:
                self.finished_signal.emit(False, "不支持的操作系统")
                return
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            timeout_count = 0
            while process.poll() is None:
                if self._cancel:
                    process.terminate()
                    self.finished_signal.emit(False, "已取消")
                    return
                timeout_count += 1
                if timeout_count > 600:  
                    process.terminate()
                    self.finished_signal.emit(False, "安装超时")
                    return
                if timeout_count % 30 == 0:
                    progress = min(95, 50 + timeout_count // 6)
                    self.finished_signal.emit(False, f"安装中... {progress}%")
                self.msleep(500)
            try:
                os.remove(installer_path)
            except:
                pass
            if process.returncode == 0:
                self.finished_signal.emit(False, "验证安装...")
                time.sleep(3)  
                for attempt in range(5):
                    has_python, version_str = check_python_installed()
                    if has_python:
                        self.finished_signal.emit(True, f"Python {version_str} 安装成功！")
                        return
                    time.sleep(2)
                self.finished_signal.emit(False, "安装完成但验证失败，请手动安装")
            else:
                self.finished_signal.emit(False, f"安装失败 (返回码: {process.returncode})")
        except Exception as e:
            import traceback
            self.finished_signal.emit(False, f"错误: {str(e)}")

def check_python_installed():
    """检测系统是否安装了 Python"""
    import subprocess
    import sys
    import os
    import shutil
    import glob
    IS_FROZEN = getattr(sys, 'frozen', False)

    def is_valid_system_python(path):
        if not path or not os.path.exists(path):
            return False
        if IS_FROZEN:
            try:
                if os.path.samefile(path, sys.executable):
                    return False
            except:
                if path.lower() == sys.executable.lower():
                    return False
        path_lower = path.lower()
        if '_mei' in path_lower or 'onefile_' in path_lower or 'nuitka' in path_lower:
            return False
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True, text=True, timeout=3
                )
            if result.returncode == 0:
                output = result.stdout + result.stderr
                return 'Python' in output
        except:
            pass
        return False

    def get_python_version(path):
        """获取Python版本"""
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True, text=True, timeout=3
                )
            if result.returncode == 0:
                output = result.stdout.strip() or result.stderr.strip()
                return output
        except:
            pass
        return None
    if sys.platform == 'win32':
        try:
            result = subprocess.run(
                ['py', '--version'],
                capture_output=True, text=True, timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                return True, version
        except:
            pass
        try:
            result = subprocess.run(
                ['py', '-c', 'import sys; print(sys.executable)'],
                capture_output=True, text=True, timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                py_path = result.stdout.strip()
                if py_path and is_valid_system_python(py_path):
                    version = get_python_version(py_path)
                    if version:
                        return True, version
        except:
            pass
        try:
            result = subprocess.run(
                ['where', 'python'],
                capture_output=True, text=True, timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    py_path = line.strip()
                    if is_valid_system_python(py_path):
                        version = get_python_version(py_path)
                        if version:
                            return True, version
        except:
            pass
        try:
            import winreg
            for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    key = winreg.OpenKey(root, r'Software\Python\PythonCore')
                    i = 0
                    while True:
                        try:
                            version_key = winreg.EnumKey(key, i)
                            if version_key.startswith('3.'):
                                try:
                                    install_key = winreg.OpenKey(key, fr'{version_key}\InstallPath')
                                    install_path, _ = winreg.QueryValueEx(install_key, '')
                                    if install_path:
                                        py_path = os.path.join(install_path, 'python.exe')
                                        if os.path.exists(py_path) and is_valid_system_python(py_path):
                                            version = get_python_version(py_path)
                                            if version:
                                                return True, version
                                except:
                                    pass
                            i += 1
                        except WindowsError:
                            break
                except:
                    pass
        except:
            pass
    for cmd in ['python3', 'python']:
        py_path = shutil.which(cmd)
        if py_path and is_valid_system_python(py_path):
            version = get_python_version(py_path)
            if version:
                return True, version
    if sys.platform == 'win32':
        username = os.environ.get('USERNAME', '')
        search_patterns = [
            r'C:\Python3*',
            r'C:\Python3*\python.exe',
            rf'C:\Users\{username}\AppData\Local\Programs\Python\Python3*\python.exe',
            r'C:\Program Files\Python3*\python.exe',
            r'C:\Program Files (x86)\Python3*\python.exe',
        ]
        for pattern in search_patterns:
            for path in glob.glob(pattern):
                if os.path.isfile(path) and path.endswith('python.exe'):
                    if is_valid_system_python(path):
                        version = get_python_version(path)
                        if version:
                            return True, version
                elif os.path.isdir(path):
                    exe_path = os.path.join(path, 'python.exe')
                    if os.path.exists(exe_path) and is_valid_system_python(exe_path):
                        version = get_python_version(exe_path)
                        if version:
                            return True, version
    elif sys.platform == 'darwin':
        paths_to_check = [
            '/usr/local/bin/python3',
            '/usr/bin/python3',
            '/opt/homebrew/bin/python3',
            '/Library/Frameworks/Python.framework/Versions/3.*/bin/python3',
        ]
        for pattern in paths_to_check:
            for path in glob.glob(pattern):
                if os.path.exists(path) and is_valid_system_python(path):
                    version = get_python_version(path)
                    if version:
                        return True, version
    else:
        paths_to_check = [
            '/usr/bin/python3',
            '/usr/local/bin/python3',
            '/usr/bin/python',
            '/opt/python3/bin/python3',
        ]
        for path in paths_to_check:
            if os.path.exists(path) and is_valid_system_python(path):
                version = get_python_version(path)
                if version:
                    return True, version
    return False, None

def ensure_python_on_startup():
    """启动时检测 Python"""
    import sys
    import os
    if not getattr(sys, 'frozen', False):
        return True
    has_python, version = check_python_installed()
    if has_python:
        print(f"[Main] 检测到系统Python: {version}")
        return True
    print("[Main] 未检测到系统Python，后台静默安装...")
    if sys.platform == "win32":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[Main] 警告: 非管理员模式，安装可能失败")
        except:
            pass
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
    from PyQt6.QtCore import QTimer, Qt
    tip_widget = QWidget(None, Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
    tip_widget.setWindowTitle("安装 Python")
    tip_widget.setFixedSize(380, 140)
    tip_widget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    layout = QVBoxLayout(tip_widget)
    layout.setSpacing(8)
    status_label = QLabel("⏳ 正在后台静默安装 Python 3.12.10...")
    status_label.setStyleSheet("font-size: 13px; font-weight: bold;")
    status_label.setWordWrap(True)
    layout.addWidget(status_label)
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setTextVisible(True)
    layout.addWidget(progress_bar)
    btn_layout = QHBoxLayout()
    btn_layout.addStretch()
    hide_btn = QPushButton("最小化到托盘")
    hide_btn.setFixedWidth(100)
    btn_layout.addWidget(hide_btn)
    cancel_btn = QPushButton("取消")
    cancel_btn.setFixedWidth(60)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    tip_widget.show()
    worker = PythonInstallWorker()
    install_success = False

    def on_progress(success, msg):
        nonlocal install_success
        if success:
            install_success = True
            status_label.setText("✅ " + msg)
            progress_bar.setValue(100)
            hide_btn.setEnabled(False)
            cancel_btn.setEnabled(False)
            cancel_btn.setText("重启")
            cancel_btn.clicked.connect(lambda: restart_app())
            QTimer.singleShot(3000, tip_widget.close)
        else:
            if "下载" in msg or "安装" in msg:
                status_label.setText("⏳ " + msg)
                import re
                match = re.search(r'(\d+)%', msg)
                if match:
                    progress_bar.setValue(int(match.group(1)))
            else:
                status_label.setText("⏳ " + msg)
                cancel_btn.setText("关闭")
                cancel_btn.clicked.connect(tip_widget.close)

    def on_hide():
        """最小化到托盘或隐藏窗口"""
        tip_widget.hide()
        print("[Main] Python安装已在后台继续...")

    def on_cancel():
        """取消安装"""
        if worker.isRunning():
            worker.cancel()
            worker.wait()
        tip_widget.close()

    def restart_app():
        """重启程序"""
        import subprocess
        import sys
        tip_widget.close()
        subprocess.Popen([sys.executable] + sys.argv)
        sys.exit(0)
    worker.finished_signal.connect(on_progress)
    hide_btn.clicked.connect(on_hide)
    cancel_btn.clicked.connect(on_cancel)
    worker.start()
    return True

def patch_subprocess_hide_window():
    """ 所有 subprocess 调用默认隐藏 cmd 窗口（Windows）"""
    import subprocess
    import sys
    if sys.platform == "win32":
        _orig_run = subprocess.run
        _orig_popen = subprocess.Popen
        _orig_call = subprocess.call
        _orig_check_call = subprocess.check_call
        _orig_check_output = subprocess.check_output
        CREATE_NO_WINDOW = 0x08000000
        def _patched_run(*args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = CREATE_NO_WINDOW
            return _orig_run(*args, **kwargs)
        def _patched_popen(*args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = CREATE_NO_WINDOW
            return _orig_popen(*args, **kwargs)
        def _patched_call(*args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = CREATE_NO_WINDOW
            return _orig_call(*args, **kwargs)
        def _patched_check_call(*args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = CREATE_NO_WINDOW
            return _orig_check_call(*args, **kwargs)
        def _patched_check_output(*args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = CREATE_NO_WINDOW
            return _orig_check_output(*args, **kwargs)
        subprocess.run = _patched_run
        subprocess.Popen = _patched_popen
        subprocess.call = _patched_call
        subprocess.check_call = _patched_check_call
        subprocess.check_output = _patched_check_output

def get_short_path(self, path):
    """获取 Windows 短路径（8.3格式）"""
    if sys.platform != 'win32':
        return path
    try:
        import ctypes
        GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
        buffer_len = GetShortPathName(path, None, 0)
        if buffer_len == 0:
            return path
        buffer = ctypes.create_unicode_buffer(buffer_len)
        GetShortPathName(path, buffer, buffer_len)
        return buffer.value if buffer.value else path
    except Exception:
        return path

def show_msg(parent, title, text, timeout=0, buttons='ok'):
    """
    通用消息框（PyQt6）调用示例:
        show_msg(self, "提示", "操作完成")
        show_msg(self, "完成", "打包成功！", 3)
        if show_msg(self, "确认", "是否继续？", 3, 'yes_no'):
            self.do_continue()   # 点击"是" 或 超时 → 执行
        else:
            print("取消")        # 点击"否" → 跳过
        if show_msg(self, "提示", "确定要删除吗？", 5, 'ok_cancel'):
            self.do_delete()     # 点击"确定" 或 超时 → 执行
        else:
            print("取消删除")
        show_msg(None, "后台任务", "完成！", 2)
        QMessageBox.critical(self, "错误", "打包失败！")
    """
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtCore import QTimer
    btn_map = {
        'ok': QMessageBox.StandardButton.Ok,
        'ok_cancel': QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        'yes_no': QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    }
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(btn_map.get(buttons, QMessageBox.StandardButton.Ok))
    if timeout > 0:
        remaining = timeout
        msg.setText(f"{text}\n\n⏱️ {remaining}秒后自动...")
        timer = QTimer(msg)
        def update():
            nonlocal remaining
            remaining -= 1
            if remaining > 0:
                msg.setText(f"{text}\n\n⏱️ {remaining}秒后自动...")
            else:
                timer.stop()
        timer.timeout.connect(update)
        timer.start(1000)
        QTimer.singleShot(timeout * 1000, msg.accept)
    result = msg.exec()
    if buttons == 'ok':
        return True
    elif buttons == 'ok_cancel':
        return result == QMessageBox.StandardButton.Ok
    elif buttons == 'yes_no':
        return result == QMessageBox.StandardButton.Yes
    return False

class AnalyzeUsedThread(QThread):
    """后台执行 _analyze_used 的纯计算部分（无UI操作）"""
    finished = pyqtSignal(list, list, list, bool)  # result, real_imports, extra_deps, uses_tkinter
    error = pyqtSignal(str)
    def __init__(self, script_path):
        super().__init__()
        self.script_path = script_path

    def run(self):
        try:
            with open(self.script_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                source = f.read()
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit([], [], [], False)
            return
        imports = set()
        uses_tkinter = False
        # ===== 1. AST 解析所有 import =====
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split('.')[0]
                        if mod == 'tkinter':
                            uses_tkinter = True
                            imports.add('tk')
                        elif mod == 'tk':
                            imports.add('tk')
                        elif mod not in STANDARD_LIBS:
                            imports.add(mod)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split('.')[0]
                        if mod == 'tkinter':
                            uses_tkinter = True
                            imports.add('tk')
                        elif mod == 'tk':
                            imports.add('tk')
                        elif mod not in STANDARD_LIBS:
                            imports.add(mod)
        except Exception:
            import re
            for line in source.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    if 'tkinter' in line:
                        uses_tkinter = True
                        imports.add('tk')
                    else:
                        match = re.match(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', line)
                        if match:
                            mod = match.group(1) or match.group(2)
                            if mod:
                                mod = mod.split('.')[0]
                                if mod not in STANDARD_LIBS:
                                    imports.add(mod)
        # ===== 2. 过滤（使用全局 FILTER_MODULES） =====
        result = []
        for mod in sorted(imports):
            mod_clean = mod.split('==')[0].split(' ')[0].strip()
            if mod_clean and mod_clean not in FILTER_MODULES:
                if mod_clean not in result:
                    result.append(mod_clean)
        # ===== 3. 确保 tk 在结果中 =====
        if uses_tkinter and 'tk' not in result:
            result.append('tk')
        # ===== 4. 自动补充隐式依赖（使用全局 DEPENDENCY_MAP） =====
        real_imports = result.copy()
        extra_deps = set()
        for mod, deps in DEPENDENCY_MAP.items():
            if mod in result:
                for dep in deps:
                    if dep not in result:
                        result.append(dep)
                        extra_deps.add(dep)
        self.finished.emit(result, real_imports, list(extra_deps), uses_tkinter)

class PythonHighlighter(QSyntaxHighlighter):
    """Python 语法高亮器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'def', 'class', 'import', 'from', 'return', 'if', 'elif', 'else', 'for',
            'while', 'try', 'except', 'finally', 'with', 'as', 'pass', 'break',
            'continue', 'lambda', 'yield', 'assert', 'raise', 'del', 'global',
            'nonlocal', 'True', 'False', 'None', 'and', 'or', 'not', 'is', 'in',
            'async', 'await', '__init__', '__name__', '__main__', '__file__'
        ]
        self.rules = []
        for kw in keywords:
            pattern = QRegularExpression(r'\b' + kw + r'\b')
            self.rules.append((pattern, keyword_format))
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.rules.append((QRegularExpression(r'#.*'), comment_format))
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.rules.append((QRegularExpression(r'\b[0-9]+\b'), number_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

class CodePreviewDialog(QDialog):
    """代码修复预览对话框 - 左右双栏对比"""
    skip_preview = False
    def __init__(self, parent, original_content, new_content, changes, file_path, backup_path):
        super().__init__(parent)
        self.setWindowTitle("代码修复预览")
        self.setModal(True)
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.8)
        self.setMinimumSize(int(screen_width * 0.5), int(screen_height * 0.5))
        self.resize(window_width, window_height)
        self.original_content = original_content
        self.new_content = new_content
        self.changes = changes
        self.file_path = file_path
        self.backup_path = backup_path
        self.left_modified = False
        self.right_modified = False
        self._setup_ui()
        self._show_diff()
        self.setStyleSheet("")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # 顶部信息
        info = QHBoxLayout()
        info.addWidget(QLabel(f"📄 文件: {os.path.basename(self.file_path)}"))
        info.addStretch()
        info.addWidget(QLabel(f"📝 修改: {len(self.changes)} 处"))
        layout.addLayout(info)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_title = QLabel("🔴 原始代码")
        left_title.setStyleSheet("font-weight: bold; color: #c0392b; font-size: 12px;")
        left_layout.addWidget(left_title)
        self.left_edit = QPlainTextEdit()
        self.left_edit.setFont(QFont("Consolas", 11))
        self.left_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #fdf2f2;
                color: #1a0000;
                border: 2px solid #e74c3c;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #ffcccc;
            }
        """)
        self.left_edit.textChanged.connect(lambda: self._on_edit("left"))
        left_layout.addWidget(self.left_edit)
        splitter.addWidget(left_widget)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_title = QLabel("🟢 修复后代码")
        right_title.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 12px;")
        right_layout.addWidget(right_title)
        self.right_edit = QPlainTextEdit()
        self.right_edit.setFont(QFont("Consolas", 11))
        self.right_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #f0faf0;
                color: #001a00;
                border: 2px solid #2ecc71;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #a8e6cf;
            }
        """)
        self.right_edit.textChanged.connect(lambda: self._on_edit("right"))
        right_layout.addWidget(self.right_edit)
        splitter.addWidget(right_widget)
        splitter.setSizes([450, 450])
        layout.addWidget(splitter, stretch=1)
        layout.addWidget(QLabel("📋 修改详情:"))
        self.changes_list = QListWidget()
        self.changes_list.setMaximumHeight(120)
        self.changes_list.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        for change in self.changes:
            self.changes_list.addItem(change)
        layout.addWidget(self.changes_list)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        left_btns = QHBoxLayout()
        self.save_left_btn = QPushButton("💾 保存左侧")
        self.save_left_btn.setEnabled(False)
        self.save_left_btn.setStyleSheet("background: #e74c3c; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.save_left_btn.clicked.connect(lambda: self._save_side("left"))
        left_btns.addWidget(self.save_left_btn)
        self.revert_left_btn = QPushButton("↩️ 还原左侧")
        self.revert_left_btn.setStyleSheet("background: #95a5a6; color: white; padding: 6px 14px; border-radius: 4px;")
        self.revert_left_btn.clicked.connect(lambda: self._revert_side("left"))
        left_btns.addWidget(self.revert_left_btn)
        btn_layout.addLayout(left_btns)
        btn_layout.addStretch()
        right_btns = QHBoxLayout()
        self.save_right_btn = QPushButton("💾 保存右侧")
        self.save_right_btn.setEnabled(False)
        self.save_right_btn.setStyleSheet("background: #27ae60; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px;")
        self.save_right_btn.clicked.connect(lambda: self._save_side("right"))
        right_btns.addWidget(self.save_right_btn)
        self.revert_right_btn = QPushButton("↩️ 还原右侧")
        self.revert_right_btn.setStyleSheet("background: #95a5a6; color: white; padding: 6px 14px; border-radius: 4px;")
        self.revert_right_btn.clicked.connect(lambda: self._revert_side("right"))
        right_btns.addWidget(self.revert_right_btn)
        btn_layout.addLayout(right_btns)
        btn_layout.addStretch()
        self.btn_apply = QPushButton("✅ 应用修复")
        self.btn_apply.setStyleSheet("background: #2ecc71; color: white; font-weight: bold; padding: 8px 24px; border-radius: 6px; font-size: 12px;")
        self.btn_apply.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_apply)
        self.btn_cancel = QPushButton("❌ 取消")
        self.btn_cancel.setStyleSheet("background: #e74c3c; color: white; padding: 8px 24px; border-radius: 6px;")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        bottom_info = QHBoxLayout()
        bottom_info.addWidget(QLabel("💡 备份文件 (.bak.py) 将保留，可手动恢复"))
        bottom_info.addStretch()
        layout.addLayout(bottom_info)
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("border: 1px solid #ddd; padding: 2px 8px; background: #f8f9fa; border-radius: 4px;")
        layout.addWidget(self.status_label)
        self._update_status()

    def _show_diff(self):
        self.left_edit.setPlainText(self.original_content)
        self.right_edit.setPlainText(self.new_content)

    def _on_edit(self, side):
        if side == "left":
            self.left_modified = True
            self.save_left_btn.setEnabled(True)
        else:
            self.right_modified = True
            self.save_right_btn.setEnabled(True)
        self._update_status()

    def _save_side(self, side):
        content = self.left_edit.toPlainText() if side == "left" else self.right_edit.toPlainText()
        with open(self.backup_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        if side == "left":
            self.left_modified = False
            self.save_left_btn.setEnabled(False)
        else:
            self.right_modified = False
            self.save_right_btn.setEnabled(False)
        self._update_status()
        self.safe_log(f"✅ 已保存{'左侧' if side == 'left' else '右侧'}到备份")

    def _revert_side(self, side):
        if side == "left":
            self.left_edit.setPlainText(self.original_content)
            self.left_modified = False
            self.save_left_btn.setEnabled(False)
        else:
            self.right_edit.setPlainText(self.new_content)
            self.right_modified = False
            self.save_right_btn.setEnabled(False)
        self._update_status()

    def _update_status(self):
        self.status_label.setText(f"左侧: {'已修改' if self.left_modified else '未修改'} | 右侧: {'已修改' if self.right_modified else '未修改'}")

    def _log(self, msg):
        if self.parent() and hasattr(self.parent(), 'safe_log'):
            self.parent().safe_log(msg)

    def accept(self):
        """用户确认应用修复"""
        self.safe_log(f"✅ 修复已应用，备份保留: {os.path.basename(self.backup_path)}")
        super().accept()

    def reject(self):
        """从备份还原"""
        if os.path.exists(self.backup_path):
            try:
                shutil.copy2(self.backup_path, self.file_path)
                self.safe_log(f"↩️ 已从备份还原: {os.path.basename(self.file_path)}")
                self.safe_log(f"💡 备份保留: {os.path.basename(self.backup_path)}")
            except Exception as e:
                self.safe_log(f"⚠️ 还原失败: {e}")
        super().reject()

class CodeCompareDialog(QDialog):
    """增强版代码对比 - 4窗口 + 函数列表 + 同步滚动 + 模糊匹配 + 互覆盖"""
    def __init__(self, parent, left_file, right_file):
        super().__init__(parent)
        self.setWindowTitle(f"代码对比 - {os.path.basename(left_file)} ↔ {os.path.basename(right_file)}")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        self.setModal(True)
        self.left_file = left_file
        self.right_file = right_file
        self.view_mode = "func"
        self.current_func = None
        self.sync_mode = False
        self.left_modified = False
        self.right_modified = False
        self.highlight_active = False
        self.fuzzy_match_enabled = False  
        self._load_files()
        self._extract_functions()
        self._setup_ui()
        self._display_func_mode()
        self._update_status()
        self.sync_mode = True
        self._bind_sync()
        self.sync_btn.setText("🔗 滚动 (开)")
        self.sync_btn.setStyleSheet("background: #2ecc71; color: white;")
        if self.common_funcs:
            self._select_func(self.common_funcs[0])

    def _load_files(self):
        with open(self.left_file, 'r', encoding='utf-8-sig') as f:
            self.left_lines = f.readlines()
        with open(self.right_file, 'r', encoding='utf-8-sig') as f:
            self.right_lines = f.readlines()
        self.left_original = self.left_lines.copy()
        self.right_original = self.right_lines.copy()

    def _extract_functions(self):
        self.left_funcs = {}
        self.right_funcs = {}

        def extract(lines, func_dict):
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('def '):
                    match = re.match(r'def\s+(\w+)\s*\(', line)
                    if match:
                        name = match.group(1)
                        start = i
                        j = i + 1
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        while j < len(lines):
                            if lines[j].strip():
                                curr_indent = len(lines[j]) - len(lines[j].lstrip())
                                if curr_indent <= indent and lines[j].strip().startswith('def '):
                                    break
                            j += 1
                        end = j - 1
                        body = ''.join(lines[start:end+1])
                        func_dict[name] = {'start': start, 'end': end, 'body': body}
                        i = j
                    else:
                        i += 1
                else:
                    i += 1
        extract(self.left_lines, self.left_funcs)
        extract(self.right_lines, self.right_funcs)
        self.common_funcs = sorted(set(self.left_funcs.keys()) & set(self.right_funcs.keys()))

    def showEvent(self, event):
        """窗口显示时调整大小"""
        super().showEvent(event)
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            width = int(screen.width() * 0.8)
            height = int(screen.height() * 0.8)
            self.resize(width, height)
            self.setMinimumSize(int(screen.width() * 0.6), int(screen.height() * 0.4))
        except:
            pass

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # 工具栏
        toolbar = QWidget()
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(0,0,0,0)
        self.func_mode_btn = QPushButton("函数")
        self.func_mode_btn.setStyleSheet("background: #2ecc71; color: white;")
        self.func_mode_btn.clicked.connect(self._switch_to_func_mode)
        tb.addWidget(self.func_mode_btn)
        self.line_mode_btn = QPushButton("逐行")
        self.line_mode_btn.setStyleSheet("background: #95a5a6; color: white;")
        self.line_mode_btn.clicked.connect(self._switch_to_line_mode)
        tb.addWidget(self.line_mode_btn)
        tb.addWidget(QLabel("|"))
        # ===== 模糊匹配开关 =====
        self.fuzzy_match_cb = QCheckBox("🔍 模糊")
        self.fuzzy_match_cb.setChecked(False)
        self.fuzzy_match_cb.setToolTip("开启后，精确匹配不到的函数会尝试相似度匹配")
        self.fuzzy_match_cb.stateChanged.connect(self._refresh_func_mode)
        tb.addWidget(self.fuzzy_match_cb)
        tb.addWidget(QLabel("|"))
        # ===== 互覆盖按钮 =====
        self.copy_left_to_right_btn = QPushButton("左→右")
        self.copy_left_to_right_btn.setStyleSheet("background: #e74c3c; color: white;")
        self.copy_left_to_right_btn.setToolTip("将左侧选中的行覆盖到右侧对应位置")
        self.copy_left_to_right_btn.clicked.connect(self._copy_selected_left_to_right)
        tb.addWidget(self.copy_left_to_right_btn)
        self.copy_right_to_left_btn = QPushButton("右→左")
        self.copy_right_to_left_btn.setStyleSheet("background: #3498db; color: white;")
        self.copy_right_to_left_btn.setToolTip("将右侧选中的行覆盖到左侧对应位置")
        self.copy_right_to_left_btn.clicked.connect(self._copy_selected_right_to_left)
        tb.addWidget(self.copy_right_to_left_btn)
        tb.addWidget(QLabel("|"))
        self.highlight_btn = QPushButton("高亮")
        self.highlight_btn.clicked.connect(self._on_highlight_clicked)
        self.highlight_btn.setStyleSheet("background: #e67e22; color: white;")
        self.highlight_btn.setToolTip("在当前模式下高亮显示差异")
        tb.addWidget(self.highlight_btn)
        # === 清除高亮按钮（点击后变色） ===
        self.clear_highlight_btn = QPushButton("清除")
        self.clear_highlight_btn.clicked.connect(self._clear_highlights)
        self.clear_highlight_btn.setStyleSheet("background: #95a5a6; color: white;")
        self.clear_highlight_btn.setToolTip("清除所有差异高亮")
        tb.addWidget(self.clear_highlight_btn)
        tb.addWidget(QLabel("|"))
        self.sync_btn = QPushButton("🔗 滚动")
        self.sync_btn.clicked.connect(self._toggle_sync)
        self.sync_btn.setStyleSheet("background: #3498db; color: white;")
        tb.addWidget(self.sync_btn)
        tb.addStretch()
        self.save_left_btn = QPushButton("💾 存左")
        self.save_left_btn.setEnabled(False)
        self.save_left_btn.clicked.connect(lambda: self._save_side("left"))
        tb.addWidget(self.save_left_btn)
        self.revert_left_btn = QPushButton("↩️ 还左")
        self.revert_left_btn.clicked.connect(lambda: self._revert_side("left"))
        tb.addWidget(self.revert_left_btn)
        self.save_right_btn = QPushButton("💾 存右")
        self.save_right_btn.setEnabled(False)
        self.save_right_btn.clicked.connect(lambda: self._save_side("right"))
        tb.addWidget(self.save_right_btn)
        self.revert_right_btn = QPushButton("↩️ 还右")
        self.revert_right_btn.clicked.connect(lambda: self._revert_side("right"))
        tb.addWidget(self.revert_right_btn)
        tb.addWidget(QLabel("|"))
        self.export_btn = QPushButton("导出")
        self.export_btn.clicked.connect(self._export_report)
        self.export_btn.setStyleSheet("background: #1abc9c; color: white;")
        tb.addWidget(self.export_btn)
        self.reload_btn = QPushButton("加载")
        self.reload_btn.clicked.connect(self._reload_files)
        self.reload_btn.setStyleSheet("background: #f39c12; color: white;")
        tb.addWidget(self.reload_btn)
        self.select_btn = QPushButton("选择")
        self.select_btn.clicked.connect(self._select_files)
        self.select_btn.setStyleSheet("background: #9b59b6; color: white;")
        tb.addWidget(self.select_btn)
        layout.addWidget(toolbar)
        # 主分割：左侧函数列表 + 右侧4窗口
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        # 左侧函数列表
        left_frame = QWidget()
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("📋 函数列表"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索函数...")
        self.search_edit.textChanged.connect(self._filter_func_list)
        left_layout.addWidget(self.search_edit)
        self.func_list = QListWidget()
        self.func_list.itemClicked.connect(self._on_func_clicked)
        left_layout.addWidget(self.func_list)
        main_splitter.addWidget(left_frame)
        main_splitter.setSizes([200, 800])
        # 右侧4窗口
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        top_bottom = QSplitter(Qt.Orientation.Vertical)
        # 预览区
        preview_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_preview_frame = QFrame()
        left_preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_preview_layout = QVBoxLayout(left_preview_frame)
        left_preview_layout.addWidget(QLabel("📄 源文件 (预览)"))
        self.left_preview = QPlainTextEdit()
        self.left_preview.setReadOnly(True)
        self.left_preview.setFont(QFont("Consolas", 10))
        self.left_preview.setStyleSheet("background: #1e1e1e; color: #d4d4d4;")
        PythonHighlighter(self.left_preview.document())
        left_preview_layout.addWidget(self.left_preview)
        preview_splitter.addWidget(left_preview_frame)
        right_preview_frame = QFrame()
        right_preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_preview_layout = QVBoxLayout(right_preview_frame)
        right_preview_layout.addWidget(QLabel("📄 编译文件 (预览)"))
        self.right_preview = QPlainTextEdit()
        self.right_preview.setReadOnly(True)
        self.right_preview.setFont(QFont("Consolas", 10))
        self.right_preview.setStyleSheet("background: #1e1e1e; color: #d4d4d4;")
        PythonHighlighter(self.right_preview.document())
        right_preview_layout.addWidget(self.right_preview)
        preview_splitter.addWidget(right_preview_frame)
        preview_splitter.setSizes([400,400])
        top_bottom.addWidget(preview_splitter)
        # 编辑区
        edit_splitter = QSplitter(Qt.Orientation.Horizontal)
        left_edit_frame = QFrame()
        left_edit_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        left_edit_layout = QVBoxLayout(left_edit_frame)
        self.left_edit_title = QLabel("✏️ 源函数: 未选中")
        left_edit_layout.addWidget(self.left_edit_title)
        self.left_edit = QPlainTextEdit()
        self.left_edit.setFont(QFont("Consolas", 10))
        self.left_edit.setStyleSheet("background: #2b2b2b; color: #d4d4d4;")
        self.left_edit.textChanged.connect(lambda: self._on_edit("left"))
        PythonHighlighter(self.left_edit.document())
        left_edit_layout.addWidget(self.left_edit)
        edit_splitter.addWidget(left_edit_frame)
        right_edit_frame = QFrame()
        right_edit_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        right_edit_layout = QVBoxLayout(right_edit_frame)
        self.right_edit_title = QLabel("✏️ 编译函数: 未选中")
        right_edit_layout.addWidget(self.right_edit_title)
        self.right_edit = QPlainTextEdit()
        self.right_edit.setFont(QFont("Consolas", 10))
        self.right_edit.setStyleSheet("background: #2b2b2b; color: #d4d4d4;")
        self.right_edit.textChanged.connect(lambda: self._on_edit("right"))
        PythonHighlighter(self.right_edit.document())
        right_edit_layout.addWidget(self.right_edit)
        edit_splitter.addWidget(right_edit_frame)
        edit_splitter.setSizes([400,400])
        top_bottom.addWidget(edit_splitter)
        top_bottom.setSizes([400,400])
        right_layout.addWidget(top_bottom)
        main_splitter.addWidget(right_widget)
        layout.addWidget(main_splitter, stretch=1)
        # 状态栏
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        self.status_label = QLabel("就绪")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        self.status_func = QLabel("函数: 无")
        status_layout.addWidget(self.status_func)
        layout.addWidget(status_frame)

    def _refresh_func_mode(self):
        """刷新函数模式（切换模糊匹配后重新显示）"""
        if self.view_mode == "func":
            self._display_func_mode()

    def _find_matching_functions(self, left_name, right_names):
        """找到匹配的右侧函数名（优先精确匹配）"""
        import difflib
        if left_name in right_names:
            return left_name, "精确匹配"
        if not self.fuzzy_match_cb.isChecked():
            return None, None
        lower_map = {name.lower(): name for name in right_names}
        if left_name.lower() in lower_map:
            return lower_map[left_name.lower()], "忽略大小写"
        left_clean = left_name.strip('_')
        for right_name in right_names:
            right_clean = right_name.strip('_')
            if left_clean == right_clean:
                return right_name, "去前后缀"
            if left_clean.endswith(right_clean) or right_clean.endswith(left_clean):
                return right_name, "包含匹配"
        matches = difflib.get_close_matches(left_name, right_names, n=1, cutoff=0.7)
        if matches:
            return matches[0], f"相似度 {difflib.SequenceMatcher(None, left_name, matches[0]).ratio():.2f}"
        return None, None

    def _count_diff_lines(self, left_text, right_text):
        """统计两个文本的差异行数"""
        import difflib
        differ = difflib.SequenceMatcher(None, left_text.splitlines(), right_text.splitlines())
        added = 0
        removed = 0
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'replace':
                added += j2 - j1
                removed += i2 - i1
            elif tag == 'delete':
                removed += i2 - i1
            elif tag == 'insert':
                added += j2 - j1
        return added, removed

    def _get_display_funcs(self):
        """获取当前显示的匹配函数列表"""
        result = []
        left_names = list(self.left_funcs.keys())
        right_names = list(self.right_funcs.keys())
        for name in left_names:
            matched, _ = self._find_matching_functions(name, right_names)
            if matched:
                result.append(name)
        return sorted(result)

    def _get_selected_range(self, edit_widget):
        """获取选中区域的行范围"""
        cursor = edit_widget.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        if start == end:
            return None, None
        doc = edit_widget.document()
        start_block = doc.findBlock(start)
        end_block = doc.findBlock(end)
        return start_block.blockNumber(), end_block.blockNumber()

    def _copy_selected_left_to_right(self):
        """将左侧选中的行覆盖到右侧对应位置"""
        start, end = self._get_selected_range(self.left_edit)
        if start is None:
            show_msg(self, "提示", "请先在左侧选中要覆盖的行",1)
            return
        cursor = self.left_edit.textCursor()
        selected_text = cursor.selectedText()
        reply = QMessageBox.question(
            self, "确认覆盖",
            f"将左侧选中的 {end - start + 1} 行覆盖到右侧对应位置？\n\n右侧原有内容将被替换！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        right_cursor = self.right_edit.textCursor()
        right_cursor.setPosition(self.right_edit.document().findBlockByNumber(start).position())
        right_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        for _ in range(end - start):
            right_cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
            right_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        right_cursor.insertText(selected_text)
        self.right_modified = True
        self.save_right_btn.setEnabled(True)
        self._update_status()
        if self.parent() and hasattr(self.parent(), 'safe_log'):
            self.parent().safe_log(f"✅ 已从左侧覆盖 {end - start + 1} 行到右侧")

    def _copy_selected_right_to_left(self):
        """将右侧选中的行覆盖到左侧对应位置"""
        start, end = self._get_selected_range(self.right_edit)
        if start is None:
            show_msg(self, "提示", "请先在右侧选中要覆盖的行",1)
            return
        cursor = self.right_edit.textCursor()
        selected_text = cursor.selectedText()
        reply = QMessageBox.question(
            self, "确认覆盖",
            f"将右侧选中的 {end - start + 1} 行覆盖到左侧对应位置？\n\n左侧原有内容将被替换！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        left_cursor = self.left_edit.textCursor()
        left_cursor.setPosition(self.left_edit.document().findBlockByNumber(start).position())
        left_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        for _ in range(end - start):
            left_cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)
            left_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        left_cursor.insertText(selected_text)
        self.left_modified = True
        self.save_left_btn.setEnabled(True)
        self._update_status()
        if self.parent() and hasattr(self.parent(), 'safe_log'):
            self.parent().safe_log(f"✅ 已从右侧覆盖 {end - start + 1} 行到左侧")

    def _populate_func_list(self):
        self.func_list.clear()
        keyword = self.search_edit.text().strip().lower()
        display_funcs = self._get_display_funcs()
        for name in display_funcs:
            if keyword == "" or keyword in name.lower():
                self.func_list.addItem(name)

    def _on_func_clicked(self, item):
        func_name = item.text()
        right_names = list(self.right_funcs.keys())
        matched, _ = self._find_matching_functions(func_name, right_names)
        if matched:
            self._select_func(func_name, matched)
        else:
            self._select_func(func_name, None)

    def _select_func(self, left_name, right_name=None):
        """选择并显示函数对比"""
        self.current_func = left_name
        if right_name is None:
            right_name = left_name
            matched, _ = self._find_matching_functions(left_name, list(self.right_funcs.keys()))
            if matched:
                right_name = matched
        self.left_edit_title.setText(f"✏️ 源函数: {left_name}")
        self.right_edit_title.setText(f"✏️ 编译函数: {right_name}")
        self.left_edit.clear()
        self.right_edit.clear()
        if left_name in self.left_funcs:
            self.left_edit.setPlainText(self.left_funcs[left_name]['body'])
        if right_name in self.right_funcs:
            self.right_edit.setPlainText(self.right_funcs[right_name]['body'])
        self.left_modified = False
        self.right_modified = False
        self.save_left_btn.setEnabled(False)
        self.save_right_btn.setEnabled(False)
        self._update_status()
        if self.highlight_active:
            self._highlight_diffs()

    def _display_func_mode(self):
        self.view_mode = "func"
        self.func_mode_btn.setStyleSheet("background: #2ecc71; color: white;")
        self.line_mode_btn.setStyleSheet("background: #95a5a6; color: white;")
        self.left_preview.clear()
        self.right_preview.clear()
        left_names = list(self.left_funcs.keys())
        right_names = list(self.right_funcs.keys())
        matched_pairs = []
        used_right = set()
        for name in left_names:
            matched, match_type = self._find_matching_functions(name, right_names)
            if matched and matched not in used_right:
                matched_pairs.append((name, matched, match_type))
                used_right.add(matched)
            elif matched and matched in used_right:
                matched_pairs.append((name, None, "已被其他函数匹配"))
        for name, matched, match_type in matched_pairs:
            if matched:
                left_body = self.left_funcs[name]['body']
                right_body = self.right_funcs[matched]['body']
                left_num = len(left_body.splitlines())
                right_num = len(right_body.splitlines())
                added, removed = self._count_diff_lines(left_body, right_body)
                diff_info = f" [+{added} -{removed}]"
                label = f"函数: {name} ↔ {matched}{diff_info}"
                if match_type != "精确匹配":
                    label += f" [{match_type}]"
                self.left_preview.appendPlainText(f"\n{'='*60}\n{label}\n行数: {left_num}\n{'='*60}")
                self.left_preview.appendPlainText(left_body)
                self.right_preview.appendPlainText(f"\n{'='*60}\n{label}\n行数: {right_num}\n{'='*60}")
                self.right_preview.appendPlainText(right_body)
            else:
                self.left_preview.appendPlainText(f"\n{'='*60}\n函数: {name} (无匹配)\n{'='*60}")
                self.left_preview.appendPlainText(self.left_funcs[name]['body'])
                self.right_preview.appendPlainText(f"\n{'='*60}\n函数: {name} (无匹配)\n{'='*60}")
        self._populate_func_list()
        matched_count = len([p for p in matched_pairs if p[1] is not None])
        total_left = len(left_names)
        self.status_label.setText(f"匹配: {matched_count}/{total_left} 个函数")
        if self.highlight_active:
            self._highlight_diffs()

    def _switch_to_func_mode(self):
        if self.view_mode != "func":
            self._display_func_mode()
            if self.current_func:
                right_names = list(self.right_funcs.keys())
                matched, _ = self._find_matching_functions(self.current_func, right_names)
                if matched:
                    self._select_func(self.current_func, matched)
                else:
                    self._select_func(self.current_func, None)

    def _display_line_mode(self):
        self.view_mode = "line"
        self.func_mode_btn.setStyleSheet("background: #95a5a6; color: white;")
        self.line_mode_btn.setStyleSheet("background: #2ecc71; color: white;")
        self.left_preview.clear()
        self.right_preview.clear()
        differ = difflib.SequenceMatcher(None, self.left_lines, self.right_lines)
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    self.left_preview.appendPlainText(self.left_lines[i].rstrip())
                    self.right_preview.appendPlainText(self.right_lines[j1 + (i-i1)].rstrip())
            elif tag == 'replace':
                for i in range(i1, i2):
                    self.left_preview.appendPlainText("  " + self.left_lines[i].rstrip())
                for j in range(j1, j2):
                    self.right_preview.appendPlainText("  " + self.right_lines[j].rstrip())
            elif tag == 'delete':
                for i in range(i1, i2):
                    self.left_preview.appendPlainText("- " + self.left_lines[i].rstrip())
            elif tag == 'insert':
                for j in range(j1, j2):
                    self.right_preview.appendPlainText("+ " + self.right_lines[j].rstrip())
        # 逐行模式下也支持高亮
        if self.highlight_active:
            self._highlight_diffs()

    def _switch_to_func_mode(self):
        if self.view_mode != "func":
            self._display_func_mode()
            if self.current_func:
                self._select_func(self.current_func)

    def _switch_to_line_mode(self):
        if self.view_mode != "line":
            self._display_line_mode()

    def _on_edit(self, side):
        if side == "left":
            self.left_modified = True
            self.save_left_btn.setEnabled(True)
        else:
            self.right_modified = True
            self.save_right_btn.setEnabled(True)
        self._update_status()
        if self.highlight_active:
            self.highlight_active = False
            self.highlight_btn.setStyleSheet("background: #e67e22; color: white;")

    def _save_side(self, side):
        if side == "left":
            content = self.left_edit.toPlainText()
            if self.current_func and self.current_func in self.left_funcs:
                old = self.left_funcs[self.current_func]
                new_lines = content.splitlines(True)
                if new_lines and not new_lines[-1].endswith('\n'):
                    new_lines[-1] += '\n'
                self.left_lines[old['start']:old['end']+1] = new_lines
                with open(self.left_file, 'w', encoding='utf-8-sig') as f:
                    f.writelines(self.left_lines)
                self.left_funcs[self.current_func]['body'] = content
                self.left_funcs[self.current_func]['end'] = old['start'] + len(new_lines) - 1
                self.left_modified = False
                self.save_left_btn.setEnabled(False)
                self._refresh_preview()
        else:
            content = self.right_edit.toPlainText()
            if self.current_func and self.current_func in self.right_funcs:
                old = self.right_funcs[self.current_func]
                new_lines = content.splitlines(True)
                if new_lines and not new_lines[-1].endswith('\n'):
                    new_lines[-1] += '\n'
                self.right_lines[old['start']:old['end']+1] = new_lines
                with open(self.right_file, 'w', encoding='utf-8-sig') as f:
                    f.writelines(self.right_lines)
                self.right_funcs[self.current_func]['body'] = content
                self.right_funcs[self.current_func]['end'] = old['start'] + len(new_lines) - 1
                self.right_modified = False
                self.save_right_btn.setEnabled(False)
                self._refresh_preview()
        self._update_status()

    def _revert_side(self, side):
        if side == "left" and self.current_func in self.left_funcs:
            old = self.left_funcs[self.current_func]
            original = ''.join(self.left_original[old['start']:old['end']+1])
            self.left_edit.setPlainText(original.rstrip())
            self.left_funcs[self.current_func]['body'] = original.rstrip()
            self.left_lines[old['start']:old['end']+1] = self.left_original[old['start']:old['end']+1].copy()
            self.left_modified = False
            self.save_left_btn.setEnabled(False)
        elif side == "right" and self.current_func in self.right_funcs:
            old = self.right_funcs[self.current_func]
            original = ''.join(self.right_original[old['start']:old['end']+1])
            self.right_edit.setPlainText(original.rstrip())
            self.right_funcs[self.current_func]['body'] = original.rstrip()
            self.right_lines[old['start']:old['end']+1] = self.right_original[old['start']:old['end']+1].copy()
            self.right_modified = False
            self.save_right_btn.setEnabled(False)
        self._update_status()
        if self.view_mode == "func":
            self._refresh_preview()
        if self.highlight_active:
            self._highlight_diffs()

    def _refresh_preview(self):
        if self.view_mode != "func":
            return
        self.left_preview.clear()
        self.right_preview.clear()
        left_names = list(self.left_funcs.keys())
        right_names = list(self.right_funcs.keys())
        for name in left_names:
            matched, match_type = self._find_matching_functions(name, right_names)
            if matched:
                left_body = self.left_funcs[name]['body']
                right_body = self.right_funcs[matched]['body']
                left_num = len(left_body.splitlines())
                right_num = len(right_body.splitlines())
                label = f"函数: {name} ↔ {matched}"
                if match_type != "精确匹配":
                    label += f" [{match_type}]"
                self.left_preview.appendPlainText(f"\n{'='*60}\n{label}\n行数: {left_num}\n{'='*60}")
                self.left_preview.appendPlainText(left_body)
                self.right_preview.appendPlainText(f"\n{'='*60}\n{label}\n行数: {right_num}\n{'='*60}")
                self.right_preview.appendPlainText(right_body)
            else:
                self.left_preview.appendPlainText(f"\n{'='*60}\n函数: {name} (无匹配)\n{'='*60}")
                self.left_preview.appendPlainText(self.left_funcs[name]['body'])
                self.right_preview.appendPlainText(f"\n{'='*60}\n函数: {name} (无匹配)\n{'='*60}")

    def _on_highlight_clicked(self):
        """高亮差异按钮点击 - 切换高亮状态"""
        if self.highlight_active:
            self._clear_highlights()
            self.highlight_active = False
            self.highlight_btn.setStyleSheet("background: #e67e22; color: white;")
        else:
            self._highlight_diffs()
            self.highlight_active = True
            self.highlight_btn.setStyleSheet("background: #e67e22; color: white; font-weight: bold; border: 2px solid #ff6b00;")
        self.clear_highlight_btn.setStyleSheet("background: #95a5a6; color: white;")

    def _clear_highlights(self):
        self.left_edit.setExtraSelections([])
        self.right_edit.setExtraSelections([])
        self.status_label.setText("已清除高亮")
        self.highlight_active = False
        self.highlight_btn.setStyleSheet("background: #e67e22; color: white;")
        self.clear_highlight_btn.setStyleSheet("background: #f44336; color: white; font-weight: bold;")
        QTimer.singleShot(300, lambda: self.clear_highlight_btn.setStyleSheet("background: #95a5a6; color: white;"))

    def _highlight_diffs(self):
        """高亮差异 - 使用 ExtraSelections"""
        if self.view_mode == "func":
            self._highlight_func_diff()
        else:
            self._highlight_line_diff()

    def _highlight_func_diff(self):
        """函数模式下的高亮 - 只高亮当前选中的函数"""
        if not self.current_func:
            return
        right_name = self.current_func
        matched, _ = self._find_matching_functions(self.current_func, list(self.right_funcs.keys()))
        if matched:
            right_name = matched
        if self.current_func not in self.left_funcs or right_name not in self.right_funcs:
            return
        left_body = self.left_funcs[self.current_func]['body'].splitlines()
        right_body = self.right_funcs[right_name]['body'].splitlines()
        differ = difflib.SequenceMatcher(None, left_body, right_body)
        left_selections = []
        right_selections = []
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'equal':
                continue
            if tag in ('delete', 'replace'):
                for i in range(i1, i2):
                    if i < self.left_edit.document().blockCount():
                        cursor = self.left_edit.textCursor()
                        cursor.setPosition(self.left_edit.document().findBlockByNumber(i).position())
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                        fmt = QTextCharFormat()
                        fmt.setBackground(QColor("#5a2a2a"))
                        selection = QTextEdit.ExtraSelection()
                        selection.cursor = cursor
                        selection.format = fmt
                        left_selections.append(selection)
            if tag in ('insert', 'replace'):
                for j in range(j1, j2):
                    if j < self.right_edit.document().blockCount():
                        cursor = self.right_edit.textCursor()
                        cursor.setPosition(self.right_edit.document().findBlockByNumber(j).position())
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                        fmt = QTextCharFormat()
                        fmt.setBackground(QColor("#2a5a2a"))
                        selection = QTextEdit.ExtraSelection()
                        selection.cursor = cursor
                        selection.format = fmt
                        right_selections.append(selection)
        self.left_edit.setExtraSelections(left_selections)
        self.right_edit.setExtraSelections(right_selections)
        if left_selections or right_selections:
            self.status_label.setText(f"✅ 差异: 左侧 {len(left_selections)} 处, 右侧 {len(right_selections)} 处")
            self.status_func.setText(f"函数: {self.current_func} | 差异: L{len(left_selections)} R{len(right_selections)}")

    def _highlight_line_diff(self):
        """逐行模式下的高亮 - 高亮全文件差异"""
        differ = difflib.SequenceMatcher(None, self.left_lines, self.right_lines)
        left_selections = []
        right_selections = []
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'equal':
                continue
            if tag in ('delete', 'replace'):
                for i in range(i1, i2):
                    if i < self.left_edit.document().blockCount():
                        cursor = self.left_edit.textCursor()
                        cursor.setPosition(self.left_edit.document().findBlockByNumber(i).position())
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                        fmt = QTextCharFormat()
                        fmt.setBackground(QColor("#5a2a2a"))
                        selection = QTextEdit.ExtraSelection()
                        selection.cursor = cursor
                        selection.format = fmt
                        left_selections.append(selection)
            if tag in ('insert', 'replace'):
                for j in range(j1, j2):
                    if j < self.right_edit.document().blockCount():
                        cursor = self.right_edit.textCursor()
                        cursor.setPosition(self.right_edit.document().findBlockByNumber(j).position())
                        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                        fmt = QTextCharFormat()
                        fmt.setBackground(QColor("#2a5a2a"))
                        selection = QTextEdit.ExtraSelection()
                        selection.cursor = cursor
                        selection.format = fmt
                        right_selections.append(selection)
        self.left_edit.setExtraSelections(left_selections)
        self.right_edit.setExtraSelections(right_selections)
        if left_selections or right_selections:
            self.status_label.setText(f"✅ 差异: 左侧 {len(left_selections)} 处, 右侧 {len(right_selections)} 处")

    def _toggle_sync(self):
        self.sync_mode = not self.sync_mode
        if self.sync_mode:
            self._bind_sync()
            self.sync_btn.setText("🔗 滚动 (开)")
            self.sync_btn.setStyleSheet("background: #2ecc71; color: white;")
        else:
            self._unbind_sync()
            self.sync_btn.setText("🔗 滚动 (关)")
            self.sync_btn.setStyleSheet("background: #3498db; color: white;")

    def _bind_sync(self):
        all_texts = [self.left_preview, self.right_preview, self.left_edit, self.right_edit]
        for text in all_texts:
            text.wheelEvent = lambda e, t=text: self._on_wheel(e, t)

    def _unbind_sync(self):
        all_texts = [self.left_preview, self.right_preview, self.left_edit, self.right_edit]
        for text in all_texts:
            text.wheelEvent = None

    def _on_wheel(self, event, source):
        if not self.sync_mode:
            return
        delta = event.angleDelta().y()
        if delta == 0:
            return
        current = source.verticalScrollBar().value()
        new_pos = current - delta // 4
        all_texts = [self.left_preview, self.right_preview, self.left_edit, self.right_edit]
        for text in all_texts:
            text.verticalScrollBar().setValue(new_pos)
        event.accept()

    def _reload_files(self):
        self._load_files()
        self._extract_functions()
        if self.view_mode == "func":
            self._display_func_mode()
            if self.current_func:
                matched, _ = self._find_matching_functions(self.current_func, list(self.right_funcs.keys()))
                if matched:
                    self._select_func(self.current_func, matched)
                else:
                    self._select_func(self.current_func, None)
        else:
            self._display_line_mode()
        self.left_modified = False
        self.right_modified = False
        self._update_status()

    def _select_files(self):
        left = QFileDialog.getOpenFileName(self, "选择源文件", "", "Python文件 (*.py)")[0]
        if not left:
            return
        right = QFileDialog.getOpenFileName(self, "选择编译文件", "", "Python文件 (*.py)")[0]
        if not right:
            return
        self.left_file = left
        self.right_file = right
        self.setWindowTitle(f"代码对比 - {os.path.basename(left)} ↔ {os.path.basename(right)}")
        self._reload_files()

    def _export_report(self):
        path = QFileDialog.getSaveFileName(self, "导出报告", "", "文本文件 (*.txt)")[0]
        if not path:
            return
        report = ["=" * 60]
        report.append("代码对比报告")
        report.append(f"源文件: {os.path.basename(self.left_file)}")
        report.append(f"编译文件: {os.path.basename(self.right_file)}")
        report.append(f"时间: {datetime.now()}")
        report.append("=" * 60)
        left_names = list(self.left_funcs.keys())
        right_names = list(self.right_funcs.keys())
        matched_count = 0
        report.append("")
        report.append("📊 函数匹配统计:")
        report.append("-" * 40)
        for name in left_names:
            matched, match_type = self._find_matching_functions(name, right_names)
            if matched:
                matched_count += 1
                left_body = self.left_funcs[name]['body']
                right_body = self.right_funcs[matched]['body']
                ratio = difflib.SequenceMatcher(None, left_body, right_body).ratio() * 100
                added, removed = self._count_diff_lines(left_body, right_body)
                status = f"相似度: {ratio:.1f}%  [+{added} -{removed}]"
                if match_type != "精确匹配":
                    status += f" [{match_type}]"
                report.append(f"  {name} ↔ {matched}")
                report.append(f"    {status}")
        report.append("")
        report.append(f"匹配率: {matched_count}/{len(left_names)} ({matched_count/len(left_names)*100:.1f}%)" if left_names else "0/0")
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(report))
        self.status_label.setText(f"✅ 报告已导出: {os.path.basename(path)}")

    def _filter_func_list(self):
        self._populate_func_list()

    def _update_status(self):
        self.status_label.setText(f"函数: {self.current_func or '无'} | 左侧修改: {'是' if self.left_modified else '否'} | 右侧修改: {'是' if self.right_modified else '否'}")
        self.status_func.setText(f"函数: {self.current_func or '无'}")

class SystemMonitorThread(QThread):
    """系统资源监控线程"""
    status_updated = pyqtSignal(float, float, float, float, str)
    def __init__(self):
        super().__init__()
        self._is_running = True
        self._interval = 3000
        self._lhm_computer = None
        self._init_lhm()

    def _init_lhm(self):
        """初始化 LibreHardwareMonitor（Windows 最佳方案）"""
        if sys.platform != 'win32':
            return
        try:
            import clr
            dll_paths = [
                'LibreHardwareMonitorLib.dll',
                './LibreHardwareMonitorLib.dll',
                '../LibreHardwareMonitorLib.dll',
                os.path.join(os.path.dirname(__file__), 'LibreHardwareMonitorLib.dll'),
            ]
            dll_loaded = False
            for dll_path in dll_paths:
                if os.path.exists(dll_path):
                    clr.AddReference(dll_path)
                    dll_loaded = True
                    break
            if not dll_loaded:
                return
            from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType
            self._lhm_computer = Computer()
            self._lhm_computer.IsCpuEnabled = True
            self._lhm_computer.IsGpuEnabled = True
            self._lhm_computer.IsMotherboardEnabled = True
            self._lhm_computer.Open()
        except Exception:
            self._lhm_computer = None

    def _get_temp_lhm(self):
        """通过 LibreHardwareMonitor 获取温度（返回 float）"""
        if not self._lhm_computer:
            return None
        try:
            from LibreHardwareMonitor.Hardware import HardwareType, SensorType
            for hardware in self._lhm_computer.Hardware:
                if hardware.HardwareType == HardwareType.Cpu:
                    hardware.Update()
                    for sensor in hardware.Sensors:
                        if (sensor.SensorType == SensorType.Temperature and 
                            'package' in sensor.Name.lower()):
                            val = sensor.Value
                            if val is not None and -10 < val < 120:
                                return float(val)
                    for sensor in hardware.Sensors:
                        if sensor.SensorType == SensorType.Temperature:
                            val = sensor.Value
                            if val is not None and -10 < val < 120:
                                return float(val)
        except Exception:
            pass
        return None

    def _get_temp_psutil(self):
        """通过 psutil 获取温度（Linux/macOS 有效，返回 float）"""
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            if not temps:
                return None
            priority_keys = ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 
                             'acpitz', 'pch_skylake']
            for key in priority_keys:
                if key in temps:
                    entries = temps[key]
                    if entries:
                        for entry in entries:
                            if entry.current and 10 < entry.current < 120:
                                return float(entry.current)
            for name, entries in temps.items():
                if entries:
                    for entry in entries:
                        if entry.current and 10 < entry.current < 120:
                            return float(entry.current)
        except Exception:
            pass
        return None

    def _get_temp_wmic(self):
        """通过 wmic 命令获取温度（Windows 备用，返回 float）"""
        if sys.platform != 'win32':
            return None
        try:
            import subprocess
            result = subprocess.run(
                ['wmic', r'/namespace:\\root\wmi',
                 'PATH', 'MSAcpi_ThermalZoneTemperature', 
                 'GET', 'CurrentTemperature'],
                capture_output=True, text=True, timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            lines = [l.strip() for l in result.stdout.split('\n') 
                     if l.strip().replace('.', '').isdigit()]
            if lines:
                temp_k = float(lines[0]) / 10.0
                temp_c = temp_k - 273.15
                if -10 < temp_c < 120:
                    return float(temp_c)
        except Exception:
            pass
        return None

    def _get_temperature(self):
        """获取温度：按优先级尝试多种方案"""
        temp = self._get_temp_lhm()
        if temp is not None:
            return f"{temp:.1f}°C"
        temp = self._get_temp_psutil()
        if temp is not None:
            return f"{temp:.1f}°C"
        temp = self._get_temp_wmic()
        if temp is not None:
            return f"{temp:.1f}°C"
        return ""

    def _get_resource_color(self, percent, is_temp=False):
        """获取资源颜色（三色：绿→橙→红）"""
        if is_temp:
            if percent > 80:
                return "#F44336"
            elif percent > 65:
                return "#FF9800"
            else:
                return "#4CAF50"
        else:
            if percent > 80:
                return "#F44336"
            elif percent > 60:
                return "#FF9800"
            else:
                return "#4CAF50"

    def run(self):
        try:
            import psutil
        except ImportError:
            return
        while self._is_running:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                temp_str = self._get_temperature()
                self.status_updated.emit(
                    cpu_percent,
                    memory.percent,
                    memory.used / (1024 ** 3),
                    memory.total / (1024 ** 3),
                    temp_str
                )
            except Exception:
                pass
            if self._is_running:
                self.msleep(self._interval)

    def stop(self):
        self._is_running = False
        self.wait(1000)
        if self._lhm_computer:
            try:
                self._lhm_computer.Close()
            except Exception:
                pass

class PackThread(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_running = True
        self.process = None
        self._mock_progress = 0
        self._mock_timer = None
        self._real_progress_received = False
        self._output_buffer = []  

    def run(self):
        process = None
        try:
            self.log_signal.emit("🚀 开始打包...")
            cmd = self._build_command()
            process = self._popen_hidden(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True, 
                encoding="utf-8", 
                errors="replace", 
                startupinfo=get_startupinfo(),
                bufsize=1,
                universal_newlines=True
            )
            self.process = process
            self._real_progress_received = False
            self._mock_progress = 0
            self._start_mock_progress()
            import select
            import sys
            while self._is_running and process.poll() is None:
                try:
                    if sys.platform == 'win32':
                        # Windows使用timeout轮询
                        import time
                        time.sleep(0.1)
                        line = process.stdout.readline()
                        if line:
                            self._process_output_line(line)
                    else:
                        import select
                        if select.select([process.stdout], [], [], 0.1)[0]:
                            line = process.stdout.readline()
                            if line:
                                self._process_output_line(line)
                except Exception as e:
                    if self._is_running:
                        self.log_signal.emit(f"读取输出异常: {e}")
                    break
                if not self._is_running:
                    break
            if self._is_running:
                for line in process.stdout:
                    if not self._is_running:
                        break
                    self._process_output_line(line)
            if process.poll() is None:
                process.wait(timeout=30)
            returncode = process.returncode if process.poll() is not None else -1
            self._stop_mock_progress()
            if returncode == 0:
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "打包完成！")
            else:
                self.finished_signal.emit(False, f"返回码: {returncode}")
        except subprocess.TimeoutExpired:
            self._stop_mock_progress()
            self.finished_signal.emit(False, "打包超时")
        except Exception as e:
            self._stop_mock_progress()
            self.finished_signal.emit(False, str(e))
        finally:
            self._cleanup_process(process)

    def _process_output_line(self, line):
        """处理输出行"""
        if not line:
            return
        line = line.rstrip()
        if line:
            self.log_signal.emit(line)
            p = self._parse_progress(line)
            if p is not None:
                if not self._real_progress_received:
                    self._real_progress_received = True
                    self._stop_mock_progress()
                self.progress_signal.emit(p)

    def _start_mock_progress(self):
        """启动模拟进度"""
        self._mock_progress = 0
        self._real_progress_received = False
        self._mock_timer = QTimer()
        self._mock_timer.timeout.connect(self._update_mock_progress)
        self._mock_timer.start(2000)  

    def _update_mock_progress(self):
        """更新模拟进度（更慢的增长）"""
        if self._real_progress_received:
            self._stop_mock_progress()
            return
        if self._mock_progress < 5: 
            self._mock_progress += 1
            self.progress_signal.emit(self._mock_progress)

    def _stop_mock_progress(self):
        """停止模拟进度"""
        if self._mock_timer:
            self._mock_timer.stop()
            self._mock_timer.deleteLater()
            self._mock_timer = None

    def _cleanup_process(self, process):
        """彻底清理进程"""
        if process:
            try:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=2)
                if process.stdout:
                    process.stdout.close()
                if process.stderr:
                    process.stderr.close()
            except Exception as e:
                pass
            finally:
                self.process = None
                import gc
                gc.collect()

    def stop(self):
        """停止打包"""
        self._is_running = False
        self._stop_mock_progress()
        if self.process:
            try:
                if sys.platform == 'win32':
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                else:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
            except Exception as e:
                pass
            finally:
                self.process = None

class ContentLoader(QThread):
    """异步加载内容线程"""
    finished = pyqtSignal(str, str)  
    def __init__(self):
        super().__init__()

    def run(self):
        changelog = ""
        tutorial = ""
        try:
            if os.path.exists("CHANGELOG.txt"):
                with open("CHANGELOG.txt", "r", encoding="utf-8") as f:
                    changelog = f.read()
                    if not changelog.strip():
                        changelog = self.get_default_changelog()
            else:
                changelog = self.get_default_changelog()
        except Exception:
            changelog = self.get_default_changelog()
        try:
            if os.path.exists("TUTORIAL.txt"):
                with open("TUTORIAL.txt", "r", encoding="utf-8") as f:
                    tutorial = f.read()
                    if not tutorial.strip():
                        tutorial = self.get_default_tutorial()
            else:
                tutorial = self.get_default_tutorial()
        except Exception:
            tutorial = self.get_default_tutorial()
        self.finished.emit(changelog, tutorial)

    def get_default_changelog(self):
        """默认更新日志"""
        return f"""【版本 {VERSION}】- {BUILD_DATE}
═══════════════════════════════════
🚀 新功能
-----------
• 增加附属依赖可配置
• 增加是否自动排除选项
• 增加图标转base64
【版本 8.0.0】- 2026-08-01
═══════════════════════════════════
🚀 新功能
-----------
• 支持在线获取github源码
• 增加打包进度彩色显示
• 增加语法检查与修复
• 增加在数据文件处运行py功能
• 增加大小预估
🔧 优化改进
-----------
• 优化为异步秒启动
• 完善约九种打包器
• 完善 PyQt6 完整界面
【版本 5.0.0】- 2026-06-01
═══════════════════════════════════
🔧 优化改进
-----------
• 增加版本信息
• 优化界面，提升速度
• 完善各种悬停提示信息
• 更新虚拟环境打包
• 完善音视频播放器
🐛 修复已知问题
-----------
• 彻底防止多开
• 修复依赖库异常
【版本 4.0.0】- 2026-05-20
═══════════════════════════════════
🚀 新功能
-----------
• 支持PyQt6 完整界面支持
• 支持 Python 3.8+ 版本
• 完善本地打包和可在线打包
• 新增依赖管理模块
• 支持PyApp等打包
• 增加切换主题
【版本 3.0.0】- 2026-05-01
═══════════════════════════════════
🔧 优化改进
-----------
• 优化打包速度，提升 30%
• 改进TK界面响应性能
• 完善各种提示信息
• 增加简易音视频播放
🐛 修复问题
-----------
• 修复 Windows 路径兼容性问题
• 解决打包后中文乱码问题
• 修复多线程打包异常
【版本 2.0.0】- 2026-04-20
═══════════════════════════════════
• 新增自动检测 Python 环境
• 支持Nuitka打包
• 支持自定义图标
🔧 优化改进
-----------
• 优化依赖安装流程
• 改进打包日志输出
🐛 修复已知问题
-----------
【版本 1.0.0】- 2026-03-15
═══════════════════════════════════
• 初始版本发布
• 支持Pyinstaller打包功能
• 提供图形化界面
"""

    def get_default_tutorial(self):
        """默认教程"""
        return """📖 使用教程 - Python 代码打包工具
═══════════════════════════════════════
一、快速开始
─────────────────
1. 选择要打包的 Python 脚本文件
2. 设置打包参数（输出目录、图标等）
3. 点击「开始打包」按钮
4. 等待打包完成
5. 在输出目录找到生成的 exe 文件
二、详细步骤
─────────────────
1️⃣ 选择脚本文件
• 点击「选择文件」按钮
• 选择您的 .py 脚本文件
• 支持 Python 3.8+ 版本
• 支持拖拽文件到界面
2️⃣ 配置打包参数
• 输出目录：设置打包文件保存位置
• 应用程序名称：设置生成的 exe 名称
• 图标文件：可选，支持 .ico 格式
• 额外文件：添加需要打包的资源文件
3️⃣ 高级选项
• 打包模式：单文件/多文件
• 控制台窗口：显示/隐藏
• UPX 压缩：减小文件体积
• 依赖管理：自动/手动
4️⃣ 开始打包
• 点击「开始打包」按钮
• 查看打包进度和日志
• 打包完成后自动打开输出目录
三、常见问题
─────────────────
❓ 打包后程序无法运行
• 检查 Python 环境是否完整
• 确认所有依赖已正确安装
• 查看打包日志寻找错误
❓ 打包文件体积过大
• 使用 UPX 压缩选项
• 检查是否包含不必要的文件
• 使用多文件模式
❓ 中文显示乱码
• 确保使用 UTF-8 编码
• 在代码中添加编码声明
• 检查文件编码格式
四、技术支持
─────────────────
🌐 项目主页：https://github.com/wcj6376
═══════════════════════════════════════
更多信息请访问项目主页
"""

class AboutDialog(QDialog):
    """关于对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.parent = parent
        self.setWindowTitle("关于 - Python代码跨平台打包工具")
        # 获取屏幕大小并设置为80%
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.setMinimumSize(window_width, window_height)
        self.setModal(True)
        self.loader = None
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#closeBtn {
                background-color: #f44336;
            }
            QPushButton#closeBtn:hover {
                background-color: #da190b;
            }
            QPushButton#editBtn {
                background-color: #ff9800;
            }
            QPushButton#editBtn:hover {
                background-color: #e68900;
            }
            QLabel#titleLabel {
                color: #2196F3;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #2196F3;
            }
        """)
        self.init_ui()
        self.load_content_async()  
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)
        # 顶部标题区域 
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setSpacing(8)
        # 主标题
        title_label = QLabel("🐍 Python 代码跨平台打包工具")
        title_label.setObjectName("titleLabel")
        title_label.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        # 版本信息
        version_label = QLabel(f"版本: {VERSION} |  编译日期: {BUILD_DATE}  |  作者: {AUTHOR}")
        version_label.setFont(QFont("Microsoft YaHei", 10))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666;")
        title_layout.addWidget(version_label)
        if self.should_show_dev_mode():
            dev_label = QLabel("💡 开发模式：编辑 CHANGELOG.txt 和 TUTORIAL.txt 可更新内容")
            dev_label.setFont(QFont("Microsoft YaHei", 8))
            dev_label.setStyleSheet("color: #ff6b00; background-color: #fff3e0; padding: 4px 10px; border-radius: 4px;")
            dev_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(dev_label)
        main_layout.addWidget(title_widget)
        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0; max-height: 2px;")
        main_layout.addWidget(separator)
        # ========== 左右分栏 ==========
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        # ----- 左侧：更新日志 -----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 10, 0)
        left_layout.setSpacing(8)
        # 左侧标题栏
        left_header = QWidget()
        left_header_layout = QHBoxLayout(left_header)
        left_header_layout.setContentsMargins(0, 0, 0, 0)
        left_title = QLabel("📝 更新日志")
        left_title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        left_title.setStyleSheet("color: #2196F3;")
        left_header_layout.addWidget(left_title)
        left_header_layout.addStretch()
        if self.should_show_dev_mode():
            refresh_btn = QPushButton("🔄")
            refresh_btn.setFixedSize(30, 30)
            refresh_btn.setToolTip("重新加载内容")
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #666;
                    border: 1px solid #d0d0d0;
                    border-radius: 15px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #2196F3;
                }
            """)
            refresh_btn.clicked.connect(self.refresh_content)
            left_header_layout.addWidget(refresh_btn)
            left_layout.addWidget(left_header)
        # 左侧文本编辑框
        self.changelog_text = QTextEdit()
        self.changelog_text.setFont(QFont("Consolas", 10))
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setFrameShape(QFrame.Shape.NoFrame)
        self.changelog_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.changelog_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.changelog_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                line-height: 1.6;
            }
        """)
        self.changelog_text.setText("⏳ 正在加载更新日志...")
        left_layout.addWidget(self.changelog_text)
        splitter.addWidget(left_widget)
        # ----- 右侧：使用教程 -----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        right_layout.setSpacing(8)
        right_title = QLabel("📖 使用教程")
        right_title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        right_title.setStyleSheet("color: #4CAF50;")
        right_layout.addWidget(right_title)
        # 右侧文本编辑框
        self.tutorial_text = QTextEdit()
        self.tutorial_text.setFont(QFont("Microsoft YaHei", 10))
        self.tutorial_text.setReadOnly(True)
        self.tutorial_text.setFrameShape(QFrame.Shape.NoFrame)
        self.tutorial_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tutorial_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tutorial_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                line-height: 1.8;
            }
        """)
        self.tutorial_text.setText("⏳ 正在加载使用教程...")
        right_layout.addWidget(self.tutorial_text)
        splitter.addWidget(right_widget)
        # 设置左右比例（各占一半，让内容区更大）
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter, 1)  # stretch=1 让splitter占据更多空间
        # ========== 底部按钮区域 ==========
        btn_widget = QWidget()
        btn_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #e0e0e0;
                padding: 10px 0;
            }
        """)
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setSpacing(12)
        btn_layout.setContentsMargins(5, 5, 5, 5)
        # 左侧按钮组
        left_btn_layout = QHBoxLayout()
        left_btn_layout.setSpacing(10)
        # 项目主页
        home_btn = QPushButton("🌐 项目主页")
        home_btn.setFixedWidth(130)
        home_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        home_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/wcj6376")))
        left_btn_layout.addWidget(home_btn)
        update_btn = QPushButton("🔄 更新源码")
        update_btn.setFixedWidth(130)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        update_btn.clicked.connect(self.update_source_code)
        left_btn_layout.addWidget(update_btn)
        # 在左侧按钮组 left_btn_layout 中添加
        btn_dep_mgr = QPushButton("📦 维护依赖")
        btn_dep_mgr.setFixedWidth(130)
        btn_dep_mgr.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_dep_mgr.clicked.connect(self._open_dep_manager)
        left_btn_layout.addWidget(btn_dep_mgr)
        # 编辑内容按钮 - 始终显示（源码运行时）
        if self.should_show_dev_mode():
            edit_btn = QPushButton("📁 编辑内容")
            edit_btn.setObjectName("editBtn")
            edit_btn.setFixedWidth(130)
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            edit_btn.clicked.connect(self.open_about_files)
            left_btn_layout.addWidget(edit_btn)
        btn_layout.addLayout(left_btn_layout)
        btn_layout.addStretch()
        # 右侧关闭按钮
        close_btn = QPushButton("✕ 关闭")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedWidth(130)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        main_layout.addWidget(btn_widget)

    def _open_dep_manager(self):
        """打开依赖管理对话框（非模态）"""
        main_window = self.main_window
        self.accept()
        if self.main_window:
            QTimer.singleShot(100, lambda: self._show_dep_manager(main_window))

    def _show_dep_manager(self, main_window):
        """延迟打开依赖管理窗口"""
        dlg = DepManagerDialog(main_window)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

    def update_source_code(self):
        """从 GitHub 下载最新源码"""
        import os
        import sys
        import tempfile
        import shutil
        import threading
        import urllib.request
        import time
        from PyQt6.QtCore import QTimer, QObject, pyqtSignal
        self.accept()
        # ===== 获取主窗口实例 =====
        main_window = None
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, PackageMainWindow):
                main_window = widget
                break
        if not main_window:
            return
        # ===== 定义信号类（用于线程安全通信） =====
        class DownloadSignals(QObject):
            progress = pyqtSignal(int, str)      
            finished = pyqtSignal(bool, str)     
        signals = DownloadSignals()
        # ===== 状态栏初始化（主线程） =====
        main_window.status_label.setText("⏳ 正在连接服务器...")
        main_window.status_progress.setVisible(True)
        main_window.status_pct.setVisible(True)
        main_window.status_progress.setValue(0)
        main_window.status_pct.setText("0%")
        # ===== 信号槽：在主线程更新界面 =====

        def on_progress(value, text):
            main_window.status_progress.setValue(value)
            main_window.status_pct.setText(f"{value}%")
            main_window.status_label.setText(text)

        def on_finished(success, msg):
            if success:
                main_window.status_progress.setValue(100)
                main_window.status_pct.setText("100%")
                main_window.status_label.setText("✅ 下载完成")
                def reset():
                    main_window.status_progress.setVisible(False)
                    main_window.status_pct.setVisible(False)
                    main_window.status_label.setText("就绪")
                QTimer.singleShot(2000, reset)
                QMessageBox.information(main_window, "下载成功", msg)
            else:
                main_window.status_progress.setVisible(False)
                main_window.status_pct.setVisible(False)
                main_window.status_label.setText("❌ 下载失败")
                def reset():
                    main_window.status_label.setText("就绪")
                QTimer.singleShot(1000, reset)
                QMessageBox.critical(main_window, "下载失败", msg)
        signals.progress.connect(on_progress)
        signals.finished.connect(on_finished)
        # ===== 模拟进度（后台线程） =====
        sim_progress = 0
        stop_sim = threading.Event()

        def sim_progress_loop():
            nonlocal sim_progress
            while not stop_sim.is_set() and sim_progress < 95:
                sim_progress += 1
                signals.progress.emit(sim_progress, f"⏳ 下载中... {sim_progress}%")
                time.sleep(0.3)
        sim_thread = threading.Thread(target=sim_progress_loop, daemon=True)
        sim_thread.start()

        def download():
            try:
                is_frozen = getattr(sys, 'frozen', False)
                target_dir = os.path.dirname(sys.executable) if is_frozen else os.path.dirname(os.path.abspath(__file__))
                target_path = os.path.join(target_dir, "PyPackTool_Qt6.py")
                # 备份旧文件
                if os.path.exists(target_path):
                    bak_path = os.path.join(target_dir, "PyPackTool_Qt6.bak.py")
                    if os.path.exists(bak_path):
                        os.remove(bak_path)
                    os.rename(target_path, bak_path)
                url = "https://raw.githubusercontent.com/wcj6376/PyPackTool/refs/heads/main/PyPackTool_Qt6.py"
                temp_file = os.path.join(tempfile.gettempdir(), "PyPackTool_Qt6_new.py")
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                stop_sim.set()  
                with urllib.request.urlopen(req, timeout=30) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    chunk_size = 8192
                    with open(temp_file, 'wb') as f:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                real_percent = int(downloaded * 100 / total_size)
                                signals.progress.emit(real_percent, f"⏳ 下载中... {real_percent}%")
                                sim_progress = real_percent  
                shutil.copy2(temp_file, target_path)
                os.remove(temp_file)
                mode = "EXE" if is_frozen else "源码"
                tip = "💡 请重启程序生效。" if mode == "EXE" else "💡 可直接运行新文件。"
                show_msg(self, f"✅ {mode} 已下载到：\n{target_path}\n\n{tip}",2)
            except Exception as e:
                stop_sim.set()
                show_msg(self, f"❌ 下载失败：{str(e)}",1)
        threading.Thread(target=download, daemon=True).start()

    def should_show_dev_mode(self):
        """判断是否显示开发模式"""
        import sys
        import os
        if hasattr(sys, '_MEIPASS'):
            return False
        if '__compiled__' in globals():
            return False
        if getattr(sys, 'frozen', False):
            return False
        exe_path = sys.argv[0]
        if exe_path.endswith('.exe') and not exe_path.endswith('.py.exe'):
            py_file = exe_path[:-4] + '.py'
            if not os.path.exists(py_file):
                return False
        return True

    def load_content_async(self):
        """异步加载内容"""
        if self.loader and self.loader.isRunning():
            return
        self.loader = ContentLoader()
        self.loader.finished.connect(self.on_content_loaded)
        self.loader.start()

    def on_content_loaded(self, changelog, tutorial):
        """内容加载完成"""
        self.changelog_text.setText(changelog)
        self.tutorial_text.setText(tutorial)
        self.changelog_text.moveCursor(self.changelog_text.textCursor().MoveOperation.Start)
        self.tutorial_text.moveCursor(self.tutorial_text.textCursor().MoveOperation.Start)

    def refresh_content(self):
        """刷新内容"""
        self.changelog_text.setText("⏳ 正在重新加载更新日志...")
        self.tutorial_text.setText("⏳ 正在重新加载使用教程...")
        self.load_content_async()

    def send_email(self):
        """发送邮件"""
        try:
            webbrowser.open("mailto:your-email@example.com?subject=Python打包工具反馈")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开邮件客户端: {str(e)}")

    def open_about_files(self):
        """打开编辑内容文件"""
        try:
            if not os.path.exists("CHANGELOG.txt"):
                with open("CHANGELOG.txt", "w", encoding="utf-8") as f:
                    f.write(ContentLoader.get_default_changelog(ContentLoader))
                show_msg(self, "提示", "已创建 CHANGELOG.txt 示例文件",1)
            if not os.path.exists("TUTORIAL.txt"):
                with open("TUTORIAL.txt", "w", encoding="utf-8") as f:
                    f.write(ContentLoader.get_default_tutorial(ContentLoader))
                show_msg(self, "提示", "已创建 TUTORIAL.txt 示例文件",1)
            # 打开文件
            if sys_platform.system() == 'Windows':
                if os.path.exists("CHANGELOG.txt"):
                    os.startfile("CHANGELOG.txt")
                if os.path.exists("TUTORIAL.txt"):
                    os.startfile("TUTORIAL.txt")
            else:
                import subprocess
                if os.path.exists("CHANGELOG.txt"):
                    self._popen_hidden(["xdg-open", "CHANGELOG.txt"])
                if os.path.exists("TUTORIAL.txt"):
                    self._popen_hidden(["xdg-open", "TUTORIAL.txt"])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件: {str(e)}")

    def closeEvent(self, event):
        """关闭事件 - 清理资源"""
        if hasattr(self, 'loader') and self.loader is not None:
            if self.loader.isRunning():
                self.loader.quit()
                self.loader.wait()
            self.loader = None
        event.accept()

class DepManagerDialog(QDialog):
    """附属依赖管理对话框（非模态）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("维护附属依赖映射")
        self.setMinimumSize(700, 500)
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.dep_map = DEPENDENCY_MAP.copy()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        tip = QLabel(
            "💡 当打包后提示 'No module named xxx' 时，\n"
            "在这里添加 模块名 → 依赖包 的映射关系即可解决。\n"
            "修改后保存，重启程序生效。"
        )
        tip.setStyleSheet("color: #555; background: #f0f4f8; padding: 8px; border-radius: 4px;")
        layout.addWidget(tip)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["模块名 (import)", "依赖包列表 (逗号分隔)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ 添加")
        btn_add.clicked.connect(self._add_row)
        btn_layout.addWidget(btn_add)
        btn_del = QPushButton("🗑️ 删除选中")
        btn_del.clicked.connect(self._delete_selected)
        btn_layout.addWidget(btn_del)
        btn_layout.addStretch()
        btn_save = QPushButton("💾 保存")
        btn_save.setStyleSheet("background: #27ae60; color: white; font-weight: bold;")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _load_data(self):
        self.dep_map = DEPENDENCY_MAP.copy()
        self.table.setRowCount(len(self.dep_map))
        for row, (mod, deps) in enumerate(self.dep_map.items()):
            self.table.setItem(row, 0, QTableWidgetItem(mod))
            self.table.setItem(row, 1, QTableWidgetItem(", ".join(deps)))

    def _add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(""))
        self.table.editItem(self.table.item(row, 0))

    def _delete_selected(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _save(self):
        new_map = {}
        for row in range(self.table.rowCount()):
            mod_item = self.table.item(row, 0)
            deps_item = self.table.item(row, 1)
            if mod_item and deps_item:
                mod = mod_item.text().strip()
                deps = [d.strip() for d in deps_item.text().split(",") if d.strip()]
                if mod and deps:
                    new_map[mod] = deps

        def do_save():
            global DEPENDENCY_MAP
            try:
                with open(DEP_MAP_FILE, 'w', encoding='utf-8-sig') as f:
                    for mod, deps in new_map.items():
                        deps_str = ', '.join([f'"{d}"' for d in deps])
                        f.write(f'{mod} = [{deps_str}]\n')
                DEPENDENCY_MAP = new_map
                QMetaObject.invokeMethod(
                    self,
                    "_save_finished",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(int, len(new_map))
                )
            except Exception as e:
                QMetaObject.invokeMethod(
                    self,
                    "_save_error",
                    Qt.ConnectionType.QueuedConnection,
                    Q_ARG(str, str(e))
                )
        threading.Thread(target=do_save, daemon=True).start()
        self.accept()
    @pyqtSlot(int)

    def _save_finished(self, count):
        QMessageBox.information(self, "保存成功", f"已保存 {count} 项映射\n\n重启程序后生效。")
    @pyqtSlot(str)

    def _save_error(self, error):
        QMessageBox.critical(self, "保存失败", error)

class StripedProgressBar(QProgressBar):
    """彩色条纹进度条 - 色彩丰富"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #f0f2f5;
                text-align: center;
                color: #1a1a2e;
                font-weight: bold;
                font-size: 10px;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #ff6b6b,
                    stop: 0.2 #feca57,
                    stop: 0.4 #48dbfb,
                    stop: 0.6 #1dd1a1,
                    stop: 0.8 #5f27cd,
                    stop: 1 #ff6b6b
                );
            }
        """)
        self.setValue(0)

    def setValue(self, value):
        super().setValue(value)
        if value < 30:
            self.setFormat(f"🔍 分析中... {value}%")
        elif value < 60:
            self.setFormat(f"⚙️ 编译中... {value}%")
        elif value < 90:
            self.setFormat(f"🚀 打包中... {value}%")
        else:
            self.setFormat(f"✅ 完成！ {value}%")

class EmojiProgressBar(QProgressBar):
    """表情动画进度条 - 简洁风格"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(24)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid #0984e3;
                border-radius: 12px;
                background-color: #dfe6e9;
                text-align: center;
                color: #2d3436;
                font-weight: bold;
                font-size: 11px;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #00cec9,
                    stop: 1 #0984e3
                );
            }
        """)
        self.setValue(0)

    def setValue(self, value):
        super().setValue(value)
        if value < 20:
            self.setFormat(f"🌙 初始化... {value}%")
        elif value < 40:
            self.setFormat(f"📦 收集依赖... {value}%")
        elif value < 60:
            self.setFormat(f"⚡ 编译中... {value}%")
        elif value < 80:
            self.setFormat(f"🎯 打包中... {value}%")
        else:
            self.setFormat(f"✨ 完成！ {value}%")

class WaveProgressBar(QWidget):
    """波浪进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setFixedHeight(60)
        self.offset = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(50)
        self._format = ""
        self.setValue(0)

    def setValue(self, value):
        self._value = value

    def value(self):
        return self._value

    def setMinimum(self, value):
        """兼容 QProgressBar 接口"""
        pass

    def setMaximum(self, value):
        pass

    def setFormat(self, format_str):
        self._format = format_str
        if '%' in format_str:
            self._format = format_str.replace('%', f'{self._value}%')
        self.update()

    def setMinimumHeight(self, height):
        self.setFixedHeight(height)
        return self

    def _animate(self):
        self.offset += 5
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor(240, 240, 240))
        wave_width = self._value / 100 * w
        path = QPainterPath()
        path.moveTo(0, h)
        for x in range(0, int(wave_width) + 10, 10):
            y = h - 20 + 10 * (x / 30 + self.offset / 20)
            path.lineTo(x, y)
        path.lineTo(wave_width, h)
        path.closeSubpath()
        gradient = QLinearGradient(0, 0, wave_width, 0)
        gradient.setColorAt(0, QColor(76, 217, 100))
        gradient.setColorAt(1, QColor(52, 199, 89))
        painter.fillPath(path, gradient)
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor(51, 51, 51))
        if self._format:
            display_text = self._format
        else:
            display_text = f"{self._value}%"
        painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, display_text)

class DotProgressBar(QWidget):
    """点阵进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setFixedHeight(30)
        self._format = ""
        self.setValue(0)

    def setValue(self, value):
        self._value = value
        self.update()

    def value(self):
        return self._value

    def setMinimum(self, value):
        pass

    def setMaximum(self, value):
        pass

    def setFormat(self, format_str):
        self._format = format_str
        self.update()

    def setMinimumHeight(self, height):
        self.setFixedHeight(height)
        return self

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # ===== 根据宽度自适应点阵数量 =====
        dot_radius = 6
        dot_spacing = dot_radius * 3  
        dot_count = max(10, int((w - 20) / dot_spacing))  
        total_width = w - 20  
        actual_spacing = total_width / max(dot_count, 1)
        start_x = 10  
        filled = int(self._value / 100 * dot_count)
        for i in range(dot_count):
            x = start_x + i * actual_spacing + actual_spacing / 2
            y = h / 2
            radius = dot_radius
            if i < filled:
                gradient = QRadialGradient(x, y, radius)
                gradient.setColorAt(0, QColor(76, 217, 100))
                gradient.setColorAt(1, QColor(52, 199, 89))
                painter.setBrush(gradient)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x, y), radius, radius)
            else:
                painter.setBrush(QColor(200, 200, 200))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x, y), radius, radius)
        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(51, 51, 51))

class GreenProgressBar(QProgressBar):
    """薄荷绿进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #c8e6c9;
                text-align: center;
                color: #1b5e20;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background-color: #4caf50;
            }
        """)
        self.setValue(0)

    def setValue(self, value):
        super().setValue(value)
        self.setFormat(f"🌿 {value}%")

class PinkProgressBar(QProgressBar):
    """樱花粉进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #f8bbd0;
                text-align: center;
                color: #880e4f;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background-color: #e91e63;
            }
        """)

    def setValue(self, value):
        super().setValue(value)
        self.setFormat(f"🌸 {value}%")

class PurpleProgressBar(QProgressBar):
    """星际紫进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #e9d5ff;
                text-align: center;
                color: #4a1a7a;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #9333ea,
                    stop: 1 #a855f7
                );
            }
        """)
        self.setValue(0)

    def setValue(self, value):
        super().setValue(value)
        self.setFormat(f"🌌 {value}%")

class BlueProgressBar(QProgressBar):
    """深海蓝进度条"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #bbdefb;
                text-align: center;
                color: #0d47a1;
                font-weight: bold;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #2196f3,
                    stop: 1 #42a5f5
                );
            }
        """)
        self.setValue(0)

    def setValue(self, value):
        super().setValue(value)
        self.setFormat(f"🌊 {value}%")

class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.is_collapsed = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.header = QFrame()
        self.header.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)
        self.header.setStyleSheet("QFrame{background-color:#f0f0f0;border:1px solid #ccc;border-radius:4px}")
        hl = QHBoxLayout(self.header)
        hl.setContentsMargins(8,4,8,4)
        self.toggle_btn = QToolButton()
        self.toggle_btn.setText(f"▶ {title}")
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.clicked.connect(self.toggle)
        hl.addWidget(self.toggle_btn)
        hl.addStretch()
        layout.addWidget(self.header)
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(8,4,8,4)
        self.content_layout.setSpacing(4)
        layout.addWidget(self.content_area)

    def toggle(self):
        self.is_collapsed = not self.is_collapsed
        self.content_area.setVisible(not self.is_collapsed)
        t = self.toggle_btn.text().replace("▶ ","").replace("▼ ","")
        self.toggle_btn.setText(f"{'▼' if not self.is_collapsed else '▶'} {t}")

    def add_widget(self, w): self.content_layout.addWidget(w)

    def add_layout(self, l): self.content_layout.addLayout(l)

class EmojiButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        font_name = "Segoe UI Emoji" if sys.platform == "win32" else (
            "Apple Color Emoji" if sys.platform == "darwin" else "Noto Color Emoji")
        self.setFont(QFont(font_name, 10))
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumWidth(60)
        self._tooltip_text = ""
        self.setMouseTracking(True)

    def setToolTip(self, text):
        self._tooltip_text = text
        super().setToolTip(text)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self._tooltip_text:
            # 立即显示，不延迟
            QToolTip.showText(event.globalPosition().toPoint(), self._tooltip_text, self)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        QToolTip.hideText()

class DragDropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("可拖拽文件到此处...")
        self._drag_enabled = False

    def enable_drag_drop(self):
        """延迟启用拖拽功能"""
        if not self._drag_enabled:
            self.setAcceptDrops(True)
            self._drag_enabled = True

    def dragEnterEvent(self, e):
        if self._drag_enabled and e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        if not self._drag_enabled:
            return
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            normalized = os.path.normpath(path)
            self.setText(normalized)
            self.textChanged.emit(normalized)

class LogTextEdit(QPlainTextEdit):
    files_dropped = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setAcceptDrops(True)
        self.setPlaceholderText("可将数据文件拖拽到此区域自动添加\n\n打包日志将显示在这里...")
        # ========== 添加滚动条 ==========
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("""
                    QPlainTextEdit {
                        font-family: Consolas;
                        font-size: 12px;
                    }
                    QScrollBar:vertical {
                        background: #f0f0f0;
                        width: 12px;
                    }
                    QScrollBar::handle:vertical {
                        background: #c0c0c0;
                        min-height: 20px;
                        border-radius: 6px;
                    }
                """)

    def append_log(self, msg):
        """添加日志到GUI（线程安全，批量刷新）"""
        try:
            self.appendPlainText(msg)
            scrollbar = self.verticalScrollBar()
            # 只在接近底部时自动滚动，不强制processEvents
            if scrollbar.value() >= scrollbar.maximum() - 100:
                scrollbar.setValue(scrollbar.maximum())
        except Exception:
            pass

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if urls:
            files = []
            for u in urls:
                path = u.toLocalFile()
                if path and os.path.exists(path):
                    files.append(path)
                    self.append_log(f"📎 添加文件: {os.path.basename(path)}")
            if files:
                self.files_dropped.emit(files)
            e.acceptProposedAction()
        else:
            super().dropEvent(e)

class PackageWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    time_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_running = True
        self.process = None
        self._use_msvc = False 
        self._downloading = False  
        # 日志标志，防止重复打印
        self._cache_logged = False
        self._mingw_logged = False
        self._local_logged = False
        self._incomplete_logged = False
        self._msvc_logged = False
        self._msvc_ok_logged = False
        self._download_logged = False
        # ===== 新增：日志缓冲系统 =====
        self._log_buffer = []
        self._last_log_flush = 0
        import threading
        self._log_lock = threading.Lock()
    # ===== 类级别缓存（所有实例共享）=====
    _ccache_cache = None
    _ccache_cache_time = 0
    _CCACHE_TTL = 300  # 5分钟

    def _find_best_ccache_cached(self, project_dir=None):
        """带缓存的ccache查找，避免每次打包都遍历文件系统"""
        import time
        now = time.time()
        if (PackageWorker._ccache_cache is not None and 
            now - PackageWorker._ccache_cache_time < self._CCACHE_TTL):
            return PackageWorker._ccache_cache
        result = self._find_best_ccache(project_dir)
        PackageWorker._ccache_cache = result
        PackageWorker._ccache_cache_time = now
        return result

    def _buffered_log(self, msg):
        """缓冲日志，200ms批量发射一次，减少Qt信号开销"""
        import time
        with self._log_lock:
            self._log_buffer.append(msg)
        now = time.time()
        if now - self._last_log_flush > 0.2:
            self._flush_log()

    def _flush_log(self):
        """强制刷新日志缓冲"""
        import time
        with self._log_lock:
            if self._log_buffer:
                batch = "\n".join(self._log_buffer)
                self._log_buffer.clear()
                self._last_log_flush = time.time()
                try:
                    self.log_signal.emit(batch)
                except Exception:
                    pass

    def _cleanup_process(self, process):
        """彻底清理进程（无延迟版）"""
        if not process:
            return
        try:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except Exception:
                    process.kill()
                    try:
                        process.wait(timeout=1)
                    except Exception:
                        pass
        except Exception:
            pass
        finally:
            try:
                if process.stdout:
                    process.stdout.close()
            except Exception:
                pass
            try:
                if process.stderr:
                    process.stderr.close()
            except Exception:
                pass
            self.process = None

    def safe_log(self, msg):
        """发送日志信号"""
        self.log_signal.emit(msg)

    def run(self):
        process = None
        packer = self.config.get('packer', 'PyInstaller')
        try:
            self.log_signal.emit("🚀 开始打包...")
            cmd = self._build_command()
            target_python = self.config.get('target_python', sys.executable)
            use_venv = self.config.get('use_venv', False)
            # ===== 构建环境变量 =====
            if use_venv:
                env = {}
                # 1. 系统变量
                system_keys = [
                    'SYSTEMROOT', 'TEMP', 'TMP', 'USERPROFILE',
                    'HOMEDRIVE', 'HOMEPATH', 'COMSPEC', 'WINDIR',
                    'ProgramFiles', 'CommonProgramFiles', 'ALLUSERSPROFILE'
                ]
                for key in system_keys:
                    if key in os.environ:
                        env[key] = os.environ[key]
                # 2. PATH：虚拟环境自己的目录
                python_dir = os.path.dirname(target_python)
                path_dirs = [
                    python_dir,  
                    os.path.join(python_dir, 'Scripts'),  
                ]
                # 加上Windows系统目录
                system_paths = [
                    r'C:\Windows\System32',
                    r'C:\Windows',
                    r'C:\Windows\System32\Wbem',
                    r'C:\Windows\System32\WindowsPowerShell\v1.0',
                ]
                for p in system_paths:
                    if os.path.exists(p) and p not in path_dirs:
                        path_dirs.append(p)
                env['PATH'] = os.pathsep.join(path_dirs)
                # 3. 构建 PYTHONPATH（只包含虚拟环境自己的路径，不包含系统）
                pythonpath_dirs = []
                venv_site_packages = self.config.get('venv_site_packages')
                if venv_site_packages and os.path.exists(venv_site_packages):
                    pythonpath_dirs.append(venv_site_packages)
                # Python 标准库 Lib（虚拟环境自己的）
                python_lib = os.path.join(python_dir, 'Lib')
                if os.path.exists(python_lib) and python_lib not in pythonpath_dirs:
                    pythonpath_dirs.append(python_lib)
                # Python DLLs（虚拟环境自己的）
                python_dlls = os.path.join(python_dir, 'DLLs')
                if os.path.exists(python_dlls) and python_dlls not in pythonpath_dirs:
                    pythonpath_dirs.append(python_dlls)
                # Python 根目录（虚拟环境自己的）
                if os.path.exists(python_dir) and python_dir not in pythonpath_dirs:
                    pythonpath_dirs.append(python_dir)
                if pythonpath_dirs:
                    env['PYTHONPATH'] = os.pathsep.join(pythonpath_dirs)
                # 4. 阻止访问系统
                env['PYTHONNOUSERSITE'] = '1'
                env['PYTHONSAFEPATH'] = '1'
                # 5. 清除系统Python变量
                for key in ['PYTHONHOME', 'VIRTUAL_ENV', 'PYTHONPATH_OLD',
                            'PYTHONSTARTUP', 'PYTHONEXECUTABLE']:
                    env.pop(key, None)
                # 6. 编码
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
                if sys.platform == 'win32':
                    env['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'
                self.log_signal.emit(f"📁 使用虚拟环境隔离模式: {target_python}")
            else:
                # ===== 非虚拟环境：使用当前环境，只清理干扰项 =====
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
                if sys.platform == 'win32':
                    env['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'
                env.pop('PYTHONHOME', None)
            # 打印命令
            if 'response_file' in self.config and self.config['response_file']:
                try:
                    with open(self.config['response_file'], 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                except:
                    pass
            startupinfo = get_startupinfo()
            process = self._popen_hidden(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
                env=env
            )
            self.process = process
            for line in iter(process.stdout.readline, ""):
                if not self._is_running:
                    process.terminate()
                    import time
                    time.sleep(0.3)
                    if process.poll() is None:
                        process.kill()
                    return
                if line:
                    line = line.rstrip()
                    if line:
                        try:
                            self.log_signal.emit(line)
                        except:
                            self.log_signal.emit(
                                line.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
                        try:
                            p = self._parse_progress(line)
                            if p is not None:
                                self.progress_signal.emit(p)
                        except:
                            pass
            process.wait()
            returncode = process.returncode
            if returncode == 0:
                try:
                    upx_result = self._manual_upx_compress()
                    if upx_result:
                        self.log_signal.emit(f"✅ {upx_result}")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ UPX压缩异常: {e}")
                self.finished_signal.emit(True, "打包完成！")
            else:
                self.finished_signal.emit(False, f"返回码: {returncode}")
        except Exception as e:
            self.finished_signal.emit(False, str(e))
        finally:
            if hasattr(self, '_temp_packers_installed') and self._temp_packers_installed:
                venv_python = self.config.get('venv_python')
                if venv_python and os.path.exists(venv_python):
                    for pkg in self._temp_packers_installed:
                        if pkg in ['pyinstaller', 'nuitka']:
                            continue
                        self._uninstall_temp_packer(venv_python, pkg)
                self._temp_packers_installed = []
            if process:
                try:
                    if process.poll() is None:
                        process.terminate()
                        import time
                        time.sleep(0.5)
                        if process.poll() is None:
                            process.kill()
                            time.sleep(0.2)
                except:
                    pass
                try:
                    if process.stdout:
                        process.stdout.close()
                except:
                    pass
                try:
                    if process.stderr:
                        process.stderr.close()
                except:
                    pass
            self.process = None
            import gc
            gc.collect()

    def _manual_upx_compress(self):
        try:
            upx_path = self.config.get('upx_path', '')
            if not upx_path or not os.path.exists(upx_path):
                return None
            compress_level = self.config.get('compress_level', '默认')
            if compress_level == '不压':
                return None
            # 获取exe路径
            exe_path = self._get_exe_path()
            if not exe_path or not os.path.exists(exe_path):
                return None
            # ===== 确保UPX在PATH中 =====
            upx_dir = os.path.dirname(upx_path)
            current_path = os.environ.get('PATH', '')
            if upx_dir not in current_path:
                os.environ['PATH'] = upx_dir + os.pathsep + current_path
            # 清空环境变量
            os.environ.pop('UPX', None)
            os.environ.pop('UPX_FLAGS', None)
            # UPX 参数
            upx_args = {
                '最快': '-1',
                '默认': '-7',
                '最好': '--best',
                '极致': '--ultra-brute'
            }.get(compress_level, '-7')
            upx_args = f'{upx_args} --force'
            original_size = os.path.getsize(exe_path)
            try:
                self._run_hidden(
                    [upx_path, '-d', exe_path],
                    capture_output=True, timeout=60,
                    startupinfo=get_startupinfo()
                )
            except:
                pass
            # ===== 执行压缩 =====
            result = self._run_hidden(
                [upx_path] + upx_args.split() + [exe_path],
                capture_output=True, text=True, timeout=300,
                startupinfo=get_startupinfo()
            )
            if result.returncode == 0:
                new_size = os.path.getsize(exe_path)
                saved = original_size - new_size
                saved_percent = (saved / original_size * 100) if original_size > 0 else 0
            else:
                return None
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            self.log_signal.emit(f"⚠️ UPX异常: {e}")
            return None

    def __del__(self):
        """析构函数，确保进程被清理（无sleep）"""
        if hasattr(self, 'process') and self.process:
            try:
                if self.process.poll() is None:
                    self.process.kill()
                    try:
                        self.process.wait(timeout=1)
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                if self.process.stdout:
                    self.process.stdout.close()
            except Exception:
                pass
            try:
                if self.process.stderr:
                    self.process.stderr.close()
            except Exception:
                pass
            self.process = None

    def _run_hidden(self, args, **kwargs):
        """隐藏窗口运行命令（兼容所有调用）"""
        if sys.platform == 'win32':
            if 'startupinfo' not in kwargs:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = si
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess.run(args, **kwargs)

    def _popen_hidden(self, args, **kwargs):
        """隐藏窗口运行命令（Popen）- 支持编码"""
        if sys.platform == 'win32':
            if 'startupinfo' not in kwargs:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = si
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            if 'text' not in kwargs and 'encoding' not in kwargs:
                kwargs['text'] = True
                kwargs['encoding'] = 'utf-8'
                kwargs['errors'] = 'replace'
        return subprocess.Popen(args, **kwargs)

    def _get_exe_path(self):
        """获取 exe 路径"""
        try:
            script = self.config.get('script', '')
            if not script:
                return None
            project_name = os.path.splitext(os.path.basename(script))[0]
            output_dir = self.config.get('output', os.path.join(os.path.dirname(script), 'dist'))
            possible_paths = [
                os.path.join(output_dir, f'{project_name}.exe'),
                os.path.join(output_dir, project_name, f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', project_name, f'{project_name}.exe'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            return None
        except:
            return None

    def _format_size(self, size):
        """格式化大小显示"""
        try:
            if size <= 0:
                return "0 B"
            if size < 1024:
                return f"{int(size)} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.2f} KB ({int(size)} B)"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.2f} MB ({int(size / 1024):,} KB)"
            else:
                return f"{size / (1024 * 1024 * 1024):.3f} GB ({int(size / (1024 * 1024)):,} MB)"
        except Exception:
            return "0 B"

    def _build_command(self):
        cfg = self.config
        cmd = []
        packer = cfg.get('packer', 'PyInstaller')
        script = cfg.get('script', '')
        use_venv = cfg.get('use_venv', False)
        target_python = cfg.get('target_python', sys.executable)
        venv_python = cfg.get('venv_python')
        version_file = cfg.get('version_file')
        version_info = cfg.get('version_info', {})
        # ===== 获取所有选项 =====
        platform = cfg.get('platform', 'current')
        log_level = cfg.get('log_level', 'INFO')
        collect = cfg.get('collect', '')
        copy_metadata = cfg.get('copy_metadata', '')
        # ===== 虚拟模式：处理临时打包器 =====
        if venv_python and os.path.exists(venv_python):
            packer_map = {
                'PyInstaller-spec': 'pyinstaller',
                'PyInstaller-cmd': 'pyinstaller',
                'Nuitka': 'nuitka',
                'PyApp': 'pyapp',
                'Py2exe': 'py2exe',
                'Cx_Freeze': 'cx-freeze',
                'Pynsist': 'pynsist',
                'PyOxidizer': 'pyoxidizer',
                'Py2app': 'py2app',
            }
            packer_name = packer_map.get(packer)
            if packer_name and packer_name not in ['pyinstaller', 'nuitka']:
                self._install_temp_packer(venv_python, packer_name)
                if not hasattr(self, '_temp_packers_installed'):
                    self._temp_packers_installed = []
                if packer_name not in self._temp_packers_installed:
                    self._temp_packers_installed.append(packer_name)

        def quote_path(p):
            if not p:
                return p
            if ' ' in p:
                return f'"{p}"'
            return p
        # ========== PyInstaller-spec 模式 ==========
        if packer == 'PyInstaller-spec' or script.lower().endswith('.spec'):
            spec_dir = os.path.dirname(script)
            build_dir = os.path.join(spec_dir, 'build')
            if use_venv:
                cmd = [target_python, '-S', '-m', 'PyInstaller',
                       '--distpath', spec_dir,
                       '--workpath', build_dir]
            else:
                cmd = [target_python, '-m', 'PyInstaller',
                       '--distpath', spec_dir,
                       '--workpath', build_dir]
            compress_level = cfg.get('compress_level', '默认')
            upx_path = cfg.get('upx_path', '')
            if upx_path and os.path.exists(upx_path) and compress_level != '不压':
                upx_dir = os.path.dirname(upx_path)
                cmd.append('--upx-dir')
                cmd.append(upx_dir)
                current_path = os.environ.get('PATH', '')
                if upx_dir not in current_path:
                    os.environ['PATH'] = upx_dir + os.pathsep + current_path
                UPX_FLAGS = ''
                if compress_level == '最快':
                    os.environ['UPX_FLAGS'] = '-1'
                elif compress_level == '默认':
                    os.environ['UPX_FLAGS'] = '-7'
                elif compress_level == '最好':
                    os.environ['UPX_FLAGS'] = '--best'
                elif compress_level == '极致':
                    os.environ['UPX_FLAGS'] = '--ultra-brute'
                self.log_signal.emit(f"🗜️ UPX压缩: {compress_level}模式 {os.environ['UPX_FLAGS']} ")
            if cfg.get('clean', False):
                cmd.append('--clean')
            if cfg.get('extra_args'):
                extra = cfg['extra_args']
                if isinstance(extra, str):
                    cmd.extend(extra.split())
                else:
                    cmd.extend(extra)
            cmd.append(script)
            return cmd
        # ========== Nuitka 模式 ==========
        if packer == 'Nuitka':
            cmd = [target_python, '-m', 'nuitka']
            version_file = cfg.get('version_file')
            version_info = cfg.get('version_info', {})
            if not version_info and version_file and os.path.exists(version_file):
                try:
                    with open(version_file, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    import re
                    product_name_match = re.search(r"StringStruct\(u?'ProductName', u?'([^']+)'\)", content)
                    company_match = re.search(r"StringStruct\(u?'CompanyName', u?'([^']+)'\)", content)
                    file_version_match = re.search(r"StringStruct\(u?'FileVersion', u?'([^']+)'\)", content)
                    product_version_match = re.search(r"StringStruct\(u?'ProductVersion', u?'([^']+)'\)", content)
                    if product_name_match:
                        version_info['product_name'] = product_name_match.group(1)
                    if company_match:
                        version_info['company'] = company_match.group(1)
                    if file_version_match:
                        version_info['file_version'] = file_version_match.group(1)
                    if product_version_match:
                        version_info['product_version'] = product_version_match.group(1)
                except:
                    pass
                # 应用版本信息
            if version_info:
                if version_info.get('product_name'):
                    cmd.append(f"--product-name={version_info['product_name']}")
                if version_info.get('company'):
                    cmd.append(f"--company-name={version_info['company']}")
                if version_info.get('file_version'):
                    cmd.append(f"--file-version={version_info['file_version']}")
                if version_info.get('product_version'):
                    cmd.append(f"--product-version={version_info['product_version']}")
                if version_info.get('product_name'):
                    cmd.append(f"--file-description={version_info['product_name']}")
                if version_info.get('company'):
                    cmd.append(f"--copyright=Copyright (c) {datetime.datetime.now().year} {version_info['company']}")
                 #self.safe_log(f"📋 已应用版本信息: {version_info.get('product_name', '')} v{version_info.get('product_version', '')}")
            compat_mode = cfg.get('nuitka_compat', False)
            backend = cfg.get('backend', 'auto')
            mingw_path = cfg.get('mingw_path', '')
            msvc_path = cfg.get('msvc_path', '')
            has_mingw = cfg.get('has_mingw', False)
            has_msvc = cfg.get('has_msvc', False)
            optimize = cfg.get('optimize', '平衡')
            disable_ccache = cfg.get('disable_ccache', False)
            if not disable_ccache:
                ccache_path = self._find_best_ccache_cached()
                if ccache_path:
                    os.environ['NUITKA_CCACHE_BINARY'] = ccache_path
                    self.safe_log(f"✅ ccache: {ccache_path}")
                else:
                    self.safe_log("⚠️ 未找到ccache")
            else:
                self.safe_log("🚫 已禁用ccache")
            # ===== 【直接使用 cfg 中的 excludes】 =====
            hidden_imports = cfg.get('hidden_imports', [])
            exclude_list = cfg.get('excludes', [])
            has_cryptography = any(mod.lower() in ['cryptography', 'crypto', 'pycryptodome'] for mod in hidden_imports)
            if not has_cryptography and 'cryptography' not in exclude_list:
                exclude_list.append('cryptography')
            if exclude_list:
                # 用逗号分隔所有排除的包
                cmd.append(f'--nofollow-import-to={",".join(exclude_list)}')
                #self.safe_log(f"🚫 排除 {len(exclude_list)} 个包")
            # ===== 输出模式 =====
            if cfg.get('onefile', True):
                if compat_mode:
                    cmd.append('--standalone')
                    cmd.append('--onefile')
                else:
                    cmd.append('--onefile')
            else:
                cmd.append('--standalone')
            # ===== 控制台 =====
            if not cfg.get('debug', False):
                if compat_mode:
                    cmd.append('--windows-console-mode=disable')
                else:
                    cmd.append('--disable-console')
            else:
                if compat_mode:
                    cmd.append('--windows-console-mode=attach')
            # ===== 名称和输出 =====
            if cfg.get('name'):
                cmd.append(f'--output-filename={cfg["name"]}')
            if cfg.get('output'):
                cmd.append(f'--output-dir={cfg["output"]}')
            # ===== 图标 =====
            if cfg.get('icon'):
                icon_path = cfg['icon']
                icon_name = os.path.basename(icon_path)
                if compat_mode:
                    cmd.append(f'--windows-icon-from-ico={icon_path}')
                else:
                    cmd.append(f'--icon={icon_path}')
                cmd.append(f'--include-data-file={icon_path}={icon_name}')
            # ===== 并行编译 =====
            jobs = cfg.get('jobs', 'auto')
            if jobs == 'auto':
                import multiprocessing
                auto_jobs = max(1, multiprocessing.cpu_count())
                cmd.append(f'--jobs={auto_jobs}')
                self.safe_log(f"🔧 自动并行编译: {auto_jobs} 核")
            else:
                cmd.append(f'--jobs={jobs}')
                self.safe_log(f"🔧 并行编译: {jobs} 核")
            # ===== 编译器后端 =====
            backend = cfg.get('backend', 'auto')
            if backend == 'auto':
                if has_mingw:
                    cmd.append('--mingw64')
                elif has_msvc:
                    cmd.append('--msvc=latest')
                else:
                    cmd.append('--mingw64')
            elif backend == 'MinGW64':
                cmd.append('--mingw64')
            elif backend == 'MSVC':
                cmd.append('--msvc=latest')
            # ===== GUI插件 =====
            plugin = cfg.get('gui_plugin', 'auto')
            lto = cfg.get('lto', 'no')
            if optimize == "速度优先":
                if lto == 'yes' or lto == 'thin':
                    self.safe_log("⚡ 速度优先模式：禁用LTO")
                    lto = 'no'
            if lto == 'yes':
                cmd.append('--lto=yes')
                self.safe_log("🔗 已启用LTO 优化")
            elif lto == 'thin':
                cmd.append('--lto=thin')
                self.safe_log("🔗 已启用Thin LTO 优化")
            else:
                cmd.append('--lto=no')
                self.safe_log("🔗 LTO 已禁用")
            # ===== 优化：一次集合运算检测所有插件（O(n) -> O(1)）=====
            imports_lower = {m.lower() for m in hidden_imports}
            has_qt = bool(imports_lower & {'pyqt6', 'pyqt5', 'pyside6', 'pyside2'})
            has_sf = bool(imports_lower & {'torch', 'numpy', 'pandas', 'matplotlib', 'tensorflow'})
            has_tk = bool(imports_lower & {'tkinter', 'tk', 'tkinterdnd2'})
            has_wx = 'wx' in imports_lower
            plugin_args = set()
            if has_sf:
                if 'torch' in imports_lower:
                    plugin_args.add('--enable-plugin=torch')
                if 'tensorflow' in imports_lower:
                    plugin_args.add('--enable-plugin=tensorflow')
                if imports_lower & {'numpy', 'pandas', 'matplotlib'}:
                    plugin_args.add('--enable-plugin=numpy')
            if has_qt:
                plugin_args.add('--include-qt-plugins=platforms,styles,imageformats')
                qt_map = {'pyqt6': 'pyqt6', 'pyqt5': 'pyqt5', 'pyside6': 'pyside6', 'pyside2': 'pyside2'}
                for mod, plugin in qt_map.items():
                    if mod in imports_lower:
                        plugin_args.add(f'--enable-plugin={plugin}')
            if has_tk:
                plugin_args.add('--enable-plugin=tk-inter')
            if has_wx:
                plugin_args.add('--enable-plugin=wx-python')
            cmd.extend(list(plugin_args))
            # ===== UPX压缩 =====
            upx_path = cfg.get('upx_path', '')
            compress_level = cfg.get('compress_level', '默认')
            if optimize == "速度优先":
                upx_enabled = False
                self.safe_log("⚡ 速度优先模式：禁用UPX压缩")
            else:
                upx_enabled = upx_path and os.path.exists(upx_path) and compress_level != '不压'
            if upx_enabled:
                if 'UPX' in os.environ:
                    del os.environ['UPX']
                if sys.platform == 'win32':
                    try:
                        import ctypes
                        GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
                        GetShortPathName.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
                        buffer = ctypes.create_unicode_buffer(260)
                        GetShortPathName(upx_path, buffer, 260)
                        short_path = buffer.value
                        if short_path:
                            upx_path = short_path
                    except:
                        pass
                cmd.append('--enable-plugin=upx')
                cmd.append(f'--upx-binary={upx_path}')
                if compress_level == '最好':
                    cmd.append('--optimize=1')
                elif compress_level == '极致':
                    cmd.append('--optimize=2')
                elif compress_level == '最快':
                    cmd.append('--optimize=0')
                self.safe_log(f"🗜️ UPX压缩: {compress_level}模式")
            # ===== 兼容模式 =====
            if compat_mode:
                cmd.append('--assume-yes-for-downloads')
            # ===== 去除符号 =====
            if cfg.get('strip', True):
                if optimize == "速度优先":
                    self.safe_log("⚡ 速度优先模式：保留调试符号以加快链接")
                else:
                    cmd.append('--remove-output')
            else:
                if not compat_mode:
                    cmd.append('--unstripped')
            # ===== 低内存 =====
            if cfg.get('low_memory', False):
                cmd.append('--low-memory')
                self.safe_log("🧠 已启用低内存模式")
            # ===== 实验性 =====
            if cfg.get('experimental', False):
                cmd.append('--experimental')
            # ===== 缓存目录（如果配置中有） =====
            cache_dir = cfg.get('cache_dir')
            if cache_dir:
                os.environ['NUITKA_CACHE_DIR'] = cache_dir
            # ===== 额外参数 =====
            if cfg.get('extra_args'):
                extra = cfg['extra_args']
                if isinstance(extra, str):
                    cmd.extend(extra.split())
                else:
                    cmd.extend(extra)
            # ===== 脚本 =====
            cmd.append(script)
            # ===== 打包外部脚本 =====
            pack_scripts = cfg.get('pack_scripts', [])
            for script_path in pack_scripts:
                if os.path.exists(script_path):
                    script_name = os.path.basename(script_path)
                    cmd.append(f'--include-data-file={script_path}={script_name}')
                    self.safe_log(f"📦 打包外部脚本: {script_name}")
            return cmd
        # ========== PyInstaller cmd 模式 ==========
        if use_venv:
            cmd = [target_python, '-S', '-m', 'PyInstaller']
        else:
            cmd = [target_python, '-m', 'PyInstaller']
        cmd.append('--onefile' if cfg.get('onefile', True) else '--onedir')
        # ===== 使用已生成的版本文件 =====
        if version_file and os.path.exists(version_file):
            cmd.append(f'--version-file={version_file}')
        for mod in cfg.get('hidden_imports', []):
            cmd.extend(['--hidden-import', mod])
        for mod in cfg.get('excludes', []):
            cmd.extend(['--exclude-module', mod])
        # ===== 添加日志级别 =====
        log_level = cfg.get('log_level', 'INFO')
        if log_level and log_level != 'INFO':
            cmd.extend(['--log-level', log_level])
        # 平台
        if platform and platform != 'current':
            cmd.extend(['--target-arch', platform])
        # 收集
        if collect:
            cmd.extend(['--collect-all', collect])
        # 元数据
        if copy_metadata:
            cmd.extend(['--copy-metadata', copy_metadata])
        if not cfg.get('debug', False):
            cmd.append('--noconsole')
        if cfg.get('clean', False):
            cmd.append('--clean')
        if cfg.get('strip', True):
            cmd.append('--strip')
        if cfg.get('name'):
            cmd.extend(['--name', cfg['name']])
        if cfg.get('output'):
            cmd.extend(['--distpath', cfg['output']])
        if cfg.get('icon'):
            cmd.extend(['--icon', cfg['icon']])
        compress_level = cfg.get('compress_level', '默认')
        upx_path = cfg.get('upx_path', '')
        if upx_path and os.path.exists(upx_path) and compress_level != '不压':
            upx_dir = os.path.dirname(upx_path)
            cmd.append('--upx-dir')
            cmd.append(upx_dir)
            current_path = os.environ.get('PATH', '')
            if upx_dir not in current_path:
                os.environ['PATH'] = upx_dir + os.pathsep + current_path
            UPX_FLAGS = ''
            if compress_level == '最快':
                os.environ['UPX_FLAGS'] = '-1'
            elif compress_level == '默认':
                os.environ['UPX_FLAGS'] = '-7'
            elif compress_level == '最好':
                os.environ['UPX_FLAGS'] = '--best'
            elif compress_level == '极致':
                os.environ['UPX_FLAGS'] = '--ultra-brute'
            self.log_signal.emit(f"🗜️ UPX压缩: {compress_level}模式 {os.environ['UPX_FLAGS']}")
        else:
            cmd.append('--noupx')
            if compress_level != '不压':
                self.log_signal.emit("⚠️ UPX未找到，使用 --noupx")
        for src, dst in cfg.get('data_files', []):
            sep = ';' if sys.platform == 'win32' else ':'
            cmd.extend(['--add-data', f'{src}{sep}{dst}'])
        if cfg.get('extra_args'):
            extra = cfg['extra_args']
            if isinstance(extra, str):
                cmd.extend(extra.split())
            else:
                cmd.extend(extra)
        cmd.append(script)
        pack_scripts = cfg.get('pack_scripts', [])
        for script_path in pack_scripts:
            if os.path.exists(script_path):
                script_name = os.path.basename(script_path)
                sep = ';' if sys.platform == 'win32' else ':'
                already = False
                for src, dst in cfg.get('data_files', []):
                    if src == script_path:
                        already = True
                        break
                if not already:
                    cmd.extend(['--add-data', f'{script_path}{sep}.'])
                    self.log_signal.emit(f"📦 打包外部脚本: {script_name}")
        return cmd

    def _fix_dir_permissions(dir_path):
        """递归修复目录下所有exe/dll文件的执行权限（Windows用icacls）"""
        if not os.path.isdir(dir_path):
            return
        try:
            subprocess.run(['icacls', dir_path, '/grant', 'Everyone:(OI)(CI)RX', '/T'],
                           capture_output=True, timeout=30)
        except:
            pass
        for root, dirs, files in os.walk(dir_path):
            for f in files:
                if f.endswith(('.exe', '.dll')):
                    p = os.path.join(root, f)
                    if os.path.isfile(p):
                        try:
                            subprocess.run(['powershell', '-Command', f'Unblock-File -Path "{p}"'],
                                           capture_output=True, timeout=5)
                        except:
                            pass
                        if not os.access(p, os.X_OK):
                            try:
                                os.chmod(p, 0o755)
                            except:
                                pass

    def _find_best_ccache(self, project_dir=None):
        """找版本最新的ccache，返回路径或None。"""
        exe = 'ccache.exe' if sys.platform == 'win32' else 'ccache'
        candidates = []

        def _add_candidate(p):
            if not os.path.isfile(p):
                return
            if not os.access(p, os.X_OK):
                try:
                    os.chmod(p, 0o755)
                except:
                    pass
            if os.access(p, os.X_OK):
                candidates.append(p)
        for d in os.environ.get('PATH', '').split(os.pathsep):
            d = d.strip('"').strip("'")
            if d:
                _add_candidate(os.path.join(d, exe))
        if sys.platform == 'win32':
            try:
                r = subprocess.run(['where', 'ccache'], capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    for line in r.stdout.strip().splitlines():
                        p = line.strip()
                        if 'Nuitka' in p and 'Cache' in p:
                            try:
                                nuitka_dir = p
                                while nuitka_dir and os.path.basename(nuitka_dir) != 'Nuitka':
                                    parent = os.path.dirname(nuitka_dir)
                                    if parent == nuitka_dir:
                                        break
                                    nuitka_dir = parent
                                if os.path.basename(nuitka_dir) == 'Nuitka':
                                    parent = os.path.dirname(nuitka_dir)
                                    if os.path.basename(parent) == 'Nuitka':
                                        nuitka_dir = parent
                                self._fix_dir_permissions(nuitka_dir)
                            except:
                                pass
                        _add_candidate(p)
            except:
                pass
        w = shutil.which('ccache')
        if w:
            _add_candidate(w)
        if not candidates:
            return None
        best_path, best_ver = None, (0,)
        for p in dict.fromkeys(candidates):
            try:
                if project_dir:
                    try:
                        if os.path.commonpath([os.path.normcase(os.path.abspath(p)),
                                               os.path.normcase(os.path.abspath(project_dir))]) == os.path.normcase(
                            os.path.abspath(project_dir)):
                            continue
                    except ValueError:
                        pass
                r = subprocess.run([p, '--version'], capture_output=True, text=True, timeout=5)
                if r.returncode != 0:
                    cdir = os.path.dirname(p)
                    env = os.environ.copy()
                    if cdir not in env.get('PATH', ''):
                        env['PATH'] = cdir + os.pathsep + env.get('PATH', '')
                    r = subprocess.run([p, '--version'], capture_output=True, text=True, timeout=5, cwd=cdir, env=env)
                if r.returncode == 0:
                    m = re.search(r'[Vv]ersion\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?', r.stdout)
                    if not m:
                        m = re.search(r'ccache\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?', r.stdout)
                    if not m:
                        m = re.search(r'(\d+)\.(\d+)(?:\.(\d+))?', r.stdout)
                    if m:
                        ver = tuple(int(x) if x else 0 for x in m.groups())
                        if ver > best_ver:
                            best_ver, best_path = ver, p
            except:
                continue
        return best_path if best_path else (candidates[0] if candidates else None)

    def _parse_progress(self, line):
        """解析真实进度 - 增加完成检测和通用百分比"""
        if not line or not isinstance(line, str):
            return None
        try:
            import re
            packer = self.config.get('packer')
            line_lower = line.lower()
            # ===== 优先检测完成信号（所有打包器通用） =====
            complete_keywords = [
                'completed successfully',
                'successfully completed',
                'building complete',
                'finished successfully',
                'done!',
                'exe built',
                'completed.',
                'success',
                'complete!',
                'finished!',
                'build complete',
                'successfully built',
            ]
            for kw in complete_keywords:
                if kw in line_lower:
                    return 100
            # ===== PyInstaller =====
            if packer.startswith('PyInstaller'):
                if 'INFO:' in line:
                    if "开始打包" in line:
                        return 5
                    if 'Analysis' in line:
                        return 10
                    if 'PYZ' in line:
                        return 30
                    if 'PKG' in line:
                        return 50
                    if 'EXE' in line:
                        return 80
                    if 'Complete' in line or 'completed' in line_lower:
                        return 95
                    if "打包完成" in line:
                        return 100    
            # ===== Nuitka =====
            elif packer == 'Nuitka':
                if 'Used command line options' in line:
                    return 1              
                if 'Starting Python compilation' in line:
                    return 5
                if 'Completed Python level compilation' in line or 'optimization' in line_lower:
                    return 10
                if 'Generating source code for C backend' in line:
                    return 20
                if 'Running data composer tool' in line:
                    return 30
                if 'Running C compilation via Scons' in line:
                    return 40
                if 'Backend C compiler' in line:
                    self.safe_log("⏳ 正在编译C代码，这可能需要较长时间...")
                    return 50
                if 'Slow C compilation detected' in line:
                    return 55
                if 'Backend C linking' in line:
                    return 60
                if 'Compiled' in line and 'C files' in line:
                    # 解析编译进度
                    match = re.search(r'Compiled\s+(\d+)\s+C files', line)
                    if match:
                        compiled = int(match.group(1))
                        # 假设总共约150个文件，计算进度
                        progress = min(50 + int(compiled / 150 * 30), 80)
                        return progress
                if 'Onefile: Creating single file' in line or 'Creating single file' in line:
                    return 85
                if 'Onefile payload compression' in line:
                    return 90
                if 'Onefile C linking' in line:
                    return 92
                if 'Removing onefile build directory' in line or 'removing onefile build' in line_lower:
                    return 95
                if 'Removing build directory' in line or 'removing build directory' in line_lower:
                    return 98
                if 'Successfully created' in line:
                    return 100
            # ===== Py2exe =====
            elif packer == 'Py2exe':
                if 'running' in line_lower or 'py2exe' in line_lower:
                    return 10
                if 'copying' in line_lower:
                    return 30
                if 'building' in line_lower:
                    return 50
                if 'dll' in line_lower:
                    return 70
                if 'complete' in line_lower:
                    return 100
            # ===== cx_Freeze =====
            elif packer == 'Cx_Freeze':
                if 'running build_exe' in line_lower:
                    return 10
                if 'running egg_info' in line_lower:
                    return 15
                if 'creating directory' in line_lower:
                    return 20
                if 'copying data from package' in line_lower:
                    return 30
                if 'copying' in line_lower and ('.pyd' in line_lower or '.dll' in line_lower):
                    return 50
                if 'writing zip file' in line_lower:
                    return 70
                if 'Missing dependencies' in line:
                    return 85
                if '打包完成' in line or 'cx_Freeze 打包完成' in line:
                    return 100
            # ===== PyApp =====
            elif packer == 'PyApp':
                if 'generating wheel' in line_lower or '正在生成' in line_lower:
                    return 10
                if 'wheel 包生成成功' in line_lower or 'wheel package' in line_lower:
                    return 20
                if '找到 cargo' in line_lower or 'found cargo' in line_lower:
                    return 25
                if 'fresh' in line_lower and ('unicode' in line_lower or 'proc-macro' in line_lower):
                    return 30
                if 'compiling' in line_lower and 'pyapp' in line_lower:
                    return 50
                if 'running' in line_lower and 'rustc' in line_lower:
                    return 60
                if 'finished release' in line_lower:
                    return 80
                if '已复制' in line_lower or 'copied' in line_lower:
                    return 90
                if '打包成功' in line_lower or 'success' in line_lower:
                    return 100
            # ===== PyOxidizer =====
            elif packer == 'PyOxidizer':
                if 'compiling' in line_lower:
                    return 20
                if 'linking' in line_lower:
                    return 60
                if 'finished' in line_lower:
                    return 80
                if 'success' in line_lower:
                    return 100
            # ===== Pynsist =====
            elif packer == 'Pynsist':
                if 'generating' in line_lower:
                    return 30
                if 'compiling' in line_lower:
                    return 60
                if 'success' in line_lower:
                    return 100
            # ===== Py2app =====
            elif packer == 'Py2app':
                if 'copying' in line_lower:
                    return 30
                if 'building' in line_lower:
                    return 60
                if 'creating' in line_lower:
                    return 80
                if 'complete' in line_lower:
                    return 100
            # ===== 通用百分比解析（兜底） =====
            match = re.search(r'(\d+)%', line)
            if match:
                pct = int(match.group(1))
                if 0 <= pct <= 100:
                    return pct
            # ===== 额外完成检测（兜底） =====
            if 'Building' in line and ('success' in line_lower or 'complete' in line_lower):
                return 100
            if 'Success' in line and ('exe' in line_lower or 'built' in line_lower):
                return 100
        except Exception as e:
            pass
        return None

    def stop(self):
        """停止打包"""
        self._is_running = False
        if self.process:
            packer = self.config.get('packer', '') if hasattr(self, 'config') else ''
            if packer == 'Nuitka':
                # Nuitka用terminate()优雅终止，
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=1)
                except Exception:
                    pass
            else:
                try:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                except Exception:
                    pass
            self.process = None

    def _install_temp_packer(self, venv_python, packer_name):
        """临时安装打包器"""
        import subprocess
        clean_env = {'PATH': os.environ.get('PATH', '')}
        if sys.platform == 'win32':
            clean_env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
        try:
            check = subprocess.run(
                [venv_python, '-m', 'pip', 'show', packer_name],
                capture_output=True, text=True, env=clean_env, timeout=5
            )
            if check.returncode == 0:
                return True
            self.log_signal.emit(f"📥 临时安装打包器: {packer_name}")
            success, result = pip_install(venv_python, packer_name, env=clean_env, quiet=True)
            if success:
                self.log_signal.emit(f"✅ {packer_name} 临时安装成功")
                return True
            else:
                self.log_signal.emit(f"❌ {packer_name} 安装失败")
                return False
        except Exception as e:
            self.log_signal.emit(f"❌ 临时安装异常: {e}")
            return False

    def _uninstall_temp_packer(self, venv_python, packer_name):
        """卸载临时打包器"""
        import subprocess
        if packer_name in ['pyinstaller', 'nuitka']:
            return
        clean_env = {'PATH': os.environ.get('PATH', '')}
        if sys.platform == 'win32':
            clean_env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
        try:
            self.log_signal.emit(f"📤 卸载临时打包器: {packer_name}")
            subprocess.run(
                [venv_python, '-m', 'pip', 'uninstall', '-y', packer_name],
                capture_output=True, text=True, env=clean_env, timeout=60
            )
            self.log_signal.emit(f"✅ {packer_name} 已卸载")
        except Exception as e:
            self.log_signal.emit(f"⚠️ 卸载 {packer_name} 失败: {e}")

class VersionInfoDialog(QDialog):
    """版本信息设置对话框"""
    def __init__(self, parent=None, version_data=None, app_name="", output_dir=""):
        super().__init__(parent)
        self.setWindowTitle("版本信息设置")
        self.setMinimumSize(400, 250)
        self.parent_window = parent
        self.app_name = app_name
        self.output_dir = output_dir
        self.version_data = version_data or {}
        # 产品名称从主界面自动获取
        if app_name and not self.version_data.get("product_name"):
            self.version_data["product_name"] = app_name
        self.setAcceptDrops(True)  
        self._build_ui()
        self._load_from_file()

    def dragEnterEvent(self, e):
        """拖拽进入事件"""
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        """拖拽放下事件 - 解析version.txt"""
        urls = e.mimeData().urls()
        if not urls:
            return
        file_path = urls[0].toLocalFile()
        if file_path and file_path.lower().endswith('.txt'):
            self._parse_version_file(file_path)
            if self.parent_window:
                self.parent_window.safe_log(f"📄 从文件导入版本信息: {os.path.basename(file_path)}")

    def _build_ui(self):
        """构建界面"""
        layout = QVBoxLayout(self)
        tip = QLabel("💡 可将 version.txt 拖入窗口自动解析")
        tip.setStyleSheet("color: gray; font-size: 9px;")
        layout.addWidget(tip)
        form = QFormLayout()
        fields = [
            ("product_name", "产品名称", self.app_name or "我的应用程序"),
            ("company", "产品制作", "WCJ6376"),
            ("file_version", "文件版本", "1.0.0.0"),
            ("product_version", "产品版本", self._default_version()),
        ]
        self.fields = {}
        for key, label, default in fields:
            edit = QLineEdit()
            edit.setText(str(self.version_data.get(key, default)))
            form.addRow(f"{label}:", edit)
            self.fields[key] = edit
        layout.addLayout(form)
        # 按钮
        bl = QHBoxLayout()
        bl.addStretch()
        # 添加导入按钮
        import_btn = QPushButton("📂 导入")
        import_btn.clicked.connect(self._import_version_file)
        bl.addWidget(import_btn)
        default_btn = QPushButton("默认")
        default_btn.clicked.connect(self._reset_default)
        bl.addWidget(default_btn)
        bl.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self._on_ok)
        bl.addWidget(btn_ok)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        bl.addWidget(btn_cancel)
        layout.addLayout(bl)

    def _default_version(self):
        """基于当前时间生成默认版本号"""
        now = datetime.datetime.now()
        time_part = now.strftime("%H%M").lstrip("0") or "0"
        return f"{now.year}.{now.month}.{now.day}.{time_part}"

    def _normalize_version(self, v):
        """规范化版本号为 x.x.x.x 格式"""
        parts = re.findall(r'\d+', str(v)) if v else []
        clean = [str(int(p)) if p.isdigit() else "0" for p in parts[:4]]
        while len(clean) < 4:
            clean.append("0")
        return ".".join(clean)

    def _project_dir(self):
        """计算项目输出目录"""
        name = re.sub(r'[\\/:*?"<>|]', '_', self.app_name or "app").replace(" ", "_")
        return os.path.join(self.output_dir or ".", name)

    def _version_file_path(self):
        """版本文件完整路径"""
        return os.path.join(self._project_dir(), "version.txt")

    def _load_from_file(self):
        """从项目文件加载已有版本信息"""
        path = self._version_file_path()
        if not os.path.exists(path):
            return
        self._parse_version_file(path)

    def _parse_version_file(self, file_path):
        """解析 version.txt 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            mapping = {
                "ProductName": "product_name",
                "CompanyName": "company",
                "FileVersion": "file_version",
                "ProductVersion": "product_version",
            }
            for old_key, new_key in mapping.items():
                pattern = rf"StringStruct\(u?'{old_key}', u?'([^']+)'\)"
                m = re.search(pattern, content)
                if m and new_key in self.fields:
                    self.fields[new_key].setText(m.group(1))
            if self.parent_window:
                self.parent_window.safe_log(f"✅ 已从 {os.path.basename(file_path)} 导入版本信息")
        except Exception as e:
            show_msg(self, "导入失败", f"解析失败: {e}",1)

    def _import_version_file(self):
        """导入版本文件按钮"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择版本文件", "", "Text Files (*.txt);;Version Files (version.txt)"
        )
        if file_path:
            self._parse_version_file(file_path)

    def _reset_default(self):
        """恢复默认值"""
        now = datetime.datetime.now()
        time_str = now.strftime("%H%M").lstrip("0") or "0"
        self.fields["product_name"].setText(self.app_name or "我的应用程序")
        self.fields["company"].setText("WCJ6376")
        self.fields["file_version"].setText("1.0.0.0")
        self.fields["product_version"].setText(f"{now.year}.{now.month}.{now.day}.{time_str}")

    def _on_ok(self):
        """确定按钮：先保存再关闭"""
        self._save_to_file()
        self.accept()

    def get_result(self):
        """获取用户输入的结果字典"""
        result = {k: v.text() for k, v in self.fields.items()}
        result["file_version"] = self._normalize_version(result.get("file_version", "1.0.0.0"))
        result["product_version"] = self._normalize_version(result.get("product_version", "1.0.0.0"))
        return result

    def _save_to_file(self):
        """保存为 PyInstaller 可用的 version.txt"""
        info = self.get_result()
        os.makedirs(self._project_dir(), exist_ok=True)
        path = self._version_file_path()

        def parse_vers(key):
            parts = info.get(key, "1.0.0.0").split(".")
            return ",".join(str(int(p)) if p.isdigit() else "0" for p in (parts + ["0"] * 4)[:4])
        internal_name = re.sub(r'[^A-Za-z0-9_]', '_', info.get("product_name", "app"))
        original_filename = f"{internal_name}.exe"
        content = f'''VSVersionInfo(
ffi=FixedFileInfo(
    filevers=({parse_vers("file_version")}),
    prodvers=({parse_vers("product_version")}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
),
kids=[
    StringFileInfo([
    StringTable(u'040904B0', [
        StringStruct(u'CompanyName', u'{info.get("company", "")}'),
        StringStruct(u'FileDescription', u'{info.get("product_name", "")}'),
        StringStruct(u'FileVersion', u'{info.get("file_version", "")}'),
        StringStruct(u'InternalName', u'{internal_name}'),
        StringStruct(u'LegalCopyright', u'Copyright (c) {datetime.datetime.now().year} {info.get("company", "PyPackTool")}'),
        StringStruct(u'OriginalFilename', u'{original_filename}'),
        StringStruct(u'ProductName', u'{info.get("product_name", "")}'),
        StringStruct(u'ProductVersion', u'{info.get("product_version", "")}')
    ])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
]
)'''
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='\n') as f:
                f.write(content)
        except Exception as e:
            show_msg(self, "保存失败", f"无法保存版本文件:\n{e}",1)
        return path

    def apply_to_pyinstaller(self, cmd):
        """将版本信息应用到 PyInstaller 命令"""
        path = self._save_to_file()
        if path and os.path.exists(path):
            cmd.append(f"--version-file={path}")
            return path
        return None

    def apply_to_nuitka(self, cmd):
        """将版本信息应用到 Nuitka 命令"""
        info = self.get_result()
        cmd.extend([
            f"--product-name={info.get('product_name', '')}",
            f"--product-version={info.get('product_version', '')}",
            f"--file-version={info.get('file_version', '')}",
            f"--company-name={info.get('company', '')}",
            f"--file-description={info.get('description', '')}",
            f"--copyright={info.get('copyright', '')}",
        ])

class IconMakerDialog(QDialog):
    SHAPES = {"圆角": 0.18, "方形": 0, "圆形": -1, "心形": -2}
    def __init__(self, parent=None, app=None, callback=None):
        super().__init__(parent)
        self.app = app
        self.callback = callback
        self.setWindowTitle("图标制作")
        self.setMinimumSize(500, 400)
        self.mode = "text"  # text 或 image
        self._setup_ui()
        self.img_path = None
        self.qimage = None  # 当前处理的 QImage
        self.zoom = 1.0

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # 模式选择
        mode_layout = QHBoxLayout()
        self.btn_text_mode = QPushButton("📝 文字生成")
        self.btn_text_mode.setCheckable(True)
        self.btn_text_mode.setChecked(True)
        self.btn_text_mode.clicked.connect(lambda: self._switch_mode("text"))
        self.btn_image_mode = QPushButton("🖼️ 图片处理")
        self.btn_image_mode.setCheckable(True)
        self.btn_image_mode.clicked.connect(lambda: self._switch_mode("image"))
        mode_layout.addWidget(self.btn_text_mode)
        mode_layout.addWidget(self.btn_image_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        # ========== 文字生成面板 ==========
        self.text_panel = QWidget()
        text_layout = QVBoxLayout(self.text_panel)
        text_layout.addWidget(QLabel("输入文字生成图标"))
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("输入图标文字...")
        self.text_input.textChanged.connect(self._refresh_text_preview)
        text_layout.addWidget(self.text_input)
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("背景色:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(30, 20)
        self.bg_color_btn.setStyleSheet("background: #0078FF")
        self.bg_color_btn.clicked.connect(self._pick_bg_color)
        color_layout.addWidget(self.bg_color_btn)
        color_layout.addWidget(QLabel("文字色:"))
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedSize(30, 20)
        self.text_color_btn.setStyleSheet("background: #FFFFFF")
        self.text_color_btn.clicked.connect(self._pick_text_color)
        color_layout.addWidget(self.text_color_btn)
        color_layout.addStretch()
        text_layout.addLayout(color_layout)
        layout.addWidget(self.text_panel)
        # ========== 图片处理面板 ==========
        self.image_panel = QWidget()
        self.image_panel.setVisible(False)
        image_layout = QHBoxLayout(self.image_panel)
        self.preview = QLabel("暂无图片")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet("background: white; border: 1px solid gray;")
        self.preview.setMinimumSize(200, 200)
        image_layout.addWidget(self.preview, stretch=1)
        ctrl_layout = QVBoxLayout()
        self.btn_open_image = QPushButton("📂 打开图片")
        self.btn_open_image.clicked.connect(self._load_image)
        ctrl_layout.addWidget(self.btn_open_image)
        ctrl_layout.addWidget(QLabel("形状:"))
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(list(self.SHAPES.keys()))
        self.shape_combo.setCurrentText("圆角")
        self.shape_combo.currentTextChanged.connect(self._refresh_image)
        ctrl_layout.addWidget(self.shape_combo)
        ctrl_layout.addWidget(QLabel("缩放 (%):"))
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(50, 200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self._refresh_image)
        ctrl_layout.addWidget(self.scale_slider)
        ctrl_layout.addStretch()
        image_layout.addLayout(ctrl_layout)
        layout.addWidget(self.image_panel)
        # ========== Base64 转换 ==========
        self.btn_base64 = QPushButton("📋 转Base64代码")
        self.btn_base64.setToolTip("将当前图片转为Base64字符串，生成Python代码")
        self.btn_base64.clicked.connect(self._generate_base64_code)
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_base64)
        self.btn_generate = QPushButton("✨ 生成")
        self.btn_generate.clicked.connect(self._generate)
        btn_layout.addWidget(self.btn_generate)
        btn_cancel = QPushButton("❌ 取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def _switch_mode(self, mode):
        self.mode = mode
        self.btn_text_mode.setChecked(mode == "text")
        self.btn_image_mode.setChecked(mode == "image")
        self.text_panel.setVisible(mode == "text")
        self.image_panel.setVisible(mode == "image")
        if mode == "text":
            self.btn_generate.setText("✨ 生成")
            self._refresh_text_preview()
        else:
            self.btn_generate.setText("💾 保存")
            self._refresh_image()

    def _pick_bg_color(self):
        color = QColorDialog.getColor(QColor("#0078FF"), self)
        if color.isValid():
            self.bg_color_btn.setStyleSheet(f"background: {color.name()}")
            if self.mode == "text":
                self._refresh_text_preview()

    def _pick_text_color(self):
        color = QColorDialog.getColor(QColor("#FFFFFF"), self)
        if color.isValid():
            self.text_color_btn.setStyleSheet(f"background: {color.name()}")
            if self.mode == "text":
                self._refresh_text_preview()

    def _get_color_from_btn(self, btn):
        style = btn.styleSheet()
        match = re.search(r'background:\s*#([0-9A-Fa-f]{6})', style)
        if match:
            hex_color = match.group(1)
            return QColor(
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16)
            )
        return QColor(0, 120, 255)

    def _refresh_text_preview(self):
        """纯Qt文字图标预览"""
        text = self.text_input.text() or "App"
        size = 256
        bg_color = self._get_color_from_btn(self.bg_color_btn)
        text_color = self._get_color_from_btn(self.text_color_btn)
        pixmap = QPixmap(size, size)
        pixmap.fill(bg_color)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 画文字
        font = QFont("Microsoft YaHei", 80, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(text_color)
        rect = painter.boundingRect(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.end()
        self.qimage = pixmap.toImage()
        # 预览缩略图
        thumb = pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview.setPixmap(thumb)
        self.preview.setText("")

    def _load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if file_path:
            self.img_path = file_path
            self._refresh_image()

    def _refresh_image(self):
        """纯Qt图片处理预览（裁剪、缩放、形状遮罩）"""
        if not self.img_path:
            return
        # 加载原图
        img = QImage(self.img_path)
        if img.isNull():
            if self.app and hasattr(self.app, 'safe_log'):
                self.app.safe_log("⚠️ 无法加载图片")
            return
        size = 256
        self.zoom = self.scale_slider.value() / 100.0
        # 1. 裁剪为正方形（中心裁剪）
        w, h = img.width(), img.height()
        if w != h:
            s = min(w, h)
            x = (w - s) // 2
            y = (h - s) // 2
            img = img.copy(x, y, s, s)
        # 2. 缩放到 256x256
        img = img.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # 3. 缩放处理（如果zoom != 1.0）
        if self.zoom != 1.0:
            ns = int(size * self.zoom)
            scaled = img.scaled(ns, ns, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            # 居中放到新画布
            canvas = QImage(size, size, QImage.Format.Format_ARGB32)
            canvas.fill(Qt.GlobalColor.transparent)
            p = QPainter(canvas)
            p.drawImage((size - ns) // 2, (size - ns) // 2, scaled)
            p.end()
            img = canvas
        # 4. 形状遮罩
        shape = self.shape_combo.currentText()
        mask = QImage(size, size, QImage.Format.Format_ARGB32)
        mask.fill(Qt.GlobalColor.transparent)
        p = QPainter(mask)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(Qt.GlobalColor.white))
        p.setPen(Qt.PenStyle.NoPen)
        if shape == "圆形":
            p.drawEllipse(0, 0, size, size)
        elif shape == "心形":
            path = QPainterPath()
            # 心形贝塞尔曲线
            path.moveTo(size * 0.5, size * 0.25)
            path.cubicTo(size * 0.5, size * 0.1, size * 0.15, 0, size * 0.15, size * 0.3)
            path.cubicTo(size * 0.15, size * 0.55, size * 0.5, size * 0.85, size * 0.5, size * 0.85)
            path.cubicTo(size * 0.5, size * 0.85, size * 0.85, size * 0.55, size * 0.85, size * 0.3)
            path.cubicTo(size * 0.85, 0, size * 0.5, size * 0.1, size * 0.5, size * 0.25)
            p.drawPath(path)
        elif shape == "圆角":
            p.drawRoundedRect(0, 0, size, size, size * 0.18, size * 0.18)
        else:  # 方形
            p.drawRect(0, 0, size, size)
        p.end()
        # 应用遮罩
        result = QImage(size, size, QImage.Format.Format_ARGB32)
        result.fill(Qt.GlobalColor.transparent)
        p = QPainter(result)
        p.drawImage(0, 0, img)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        p.drawImage(0, 0, mask)
        p.end()
        self.qimage = result
        # 显示预览
        thumb = QPixmap.fromImage(result).scaled(
            180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.preview.setPixmap(thumb)
        self.preview.setText("")

    def _generate(self):
        if self.mode == "text":
            self._save_icon(self.qimage)
        else:
            if self.qimage is None or self.qimage.isNull():
                QMessageBox.warning(self, "提示", "请先打开图片")
                return
            self._save_icon(self.qimage)

    def _save_icon(self, img):
        """保存图标（支持ICO和PNG）"""
        if img is None or img.isNull():
            QMessageBox.warning(self, "提示", "没有可保存的图片")
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图标", "icon.ico", 
            "Icon Files (*.ico);;PNG Files (*.png)"
        )
        if not file_path:
            return
        if file_path.endswith('.ico'):
            # 生成多尺寸ICO
            sizes = [256, 128, 64, 32, 16]
            # Qt不直接支持ICO多尺寸，我们保存为PNG，然后提示用户
            # 或者用 pillow 如果可用，否则保存最大尺寸PNG并提示
            pixmap = QPixmap.fromImage(img)
            # 尝试用 pillow 保存多尺寸ICO
            try:
                from PIL import Image
                # QImage转PIL
                buffer = QBuffer()
                buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                img.save(buffer, "PNG")
                pil_img = Image.open(io.BytesIO(buffer.data()))
                # 生成多尺寸
                ico_images = []
                for s in sizes:
                    ico_img = pil_img.resize((s, s), Image.Resampling.LANCZOS)
                    # 确保RGBA模式
                    if ico_img.mode != 'RGBA':
                        ico_img = ico_img.convert('RGBA')
                    ico_images.append(ico_img)
                ico_images[0].save(file_path, format='ICO', sizes=[(s, s) for s in sizes])
                show_msg(self, "完成", f"多尺寸图标已保存: {file_path}", 1)
            except ImportError:
                # 无Pillow，保存为PNG并提示
                png_path = file_path.replace('.ico', '.png')
                img.save(png_path)
                QMessageBox.information(
                    self, "提示", 
                    f"未安装 Pillow，无法生成 .ico 多尺寸文件。\n已保存为 PNG: {png_path}\n\n"
                    f"如需ICO格式，请安装: pip install Pillow"
                )
                file_path = png_path
        else:
            img.save(file_path)
            show_msg(self, "完成", f"图标已保存: {file_path}", 1)
        if self.callback:
            self.callback(file_path)
        self.accept()

    def _generate_base64_code(self):
        """生成图片的Base64代码"""
        import base64
        from io import BytesIO
        # 获取当前图片
        if self.mode == "text":
            self._refresh_text_preview()  # 确保最新
        img = self.qimage
        if img is None or img.isNull():
            QMessageBox.warning(self, "提示", "没有可转换的图片")
            return
        # QImage转PNG字节
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.ReadWrite)
        img.save(buffer, "PNG")
        img_bytes = bytes(buffer.data())
        b64_str = base64.b64encode(img_bytes).decode('ascii')
        var_name = "ICON_BASE64" if self.mode == "text" else "IMAGE_BASE64"
        code_lines = [
            f"# -*- coding: utf-8 -*-",
            f"# 图片Base64编码，可直接嵌入Python代码",
            f"{var_name} = \"\"\"",
        ]
        for i in range(0, len(b64_str), 76):
            code_lines.append(b64_str[i:i+76])
        code_lines.append("\"\"\"")
        code_lines.append("")
        code_lines.append("# 使用示例：")
        code_lines.append("import base64")
        code_lines.append("from io import BytesIO")
        code_lines.append("from PyQt6.QtGui import QImage, QPixmap")
        code_lines.append(f"img_data = base64.b64decode({var_name})")
        code_lines.append("image = QImage()")
        code_lines.append("image.loadFromData(img_data)")
        code_lines.append("pixmap = QPixmap.fromImage(image)")
        code_lines.append("# 使用: label.setPixmap(pixmap)")
        full_code = "\n".join(code_lines)
        dlg = QDialog(self)
        dlg.setWindowTitle("Base64 代码生成器")
        dlg.setMinimumSize(600, 400)
        layout = QVBoxLayout(dlg)
        edit = QPlainTextEdit()
        edit.setPlainText(full_code)
        edit.setFont(QFont("Consolas", 10))
        layout.addWidget(edit)
        bl = QHBoxLayout()
        bl.addStretch()
        btn_copy = QPushButton("📋 复制全部")

        def do_copy():
            QApplication.clipboard().setText(full_code)
            btn_copy.setText("✅ 已复制")
            QTimer.singleShot(1500, lambda: btn_copy.setText("📋 复制全部"))
        btn_copy.clicked.connect(do_copy)
        bl.addWidget(btn_copy)
        btn_insert = QPushButton("📝 插入到当前脚本")
        btn_insert.clicked.connect(lambda: self._insert_code_to_script(full_code, dlg))
        bl.addWidget(btn_insert)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(dlg.accept)
        bl.addWidget(btn_close)
        layout.addLayout(bl)
        dlg.exec()

    def _insert_code_to_script(self, code, dialog):
        """将代码插入到主窗口当前打开的脚本末尾"""
        main_window = self.parent()
        if not main_window or not hasattr(main_window, 'input_file'):
            QMessageBox.warning(self, "提示", "无法获取主窗口脚本路径")
            return
        script_path = main_window.input_file.text()
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "提示", "主窗口未选择有效的Python脚本")
            return
        try:
            with open(script_path, 'a', encoding='utf-8-sig') as f:
                f.write("\n\n# ===== 自动插入的图片Base64代码 =====\n")
                f.write(code)
                f.write("\n# ===== 插入结束 =====\n")
            if hasattr(main_window, 'safe_log'):
                main_window.safe_log(f"✅ 已插入Base64代码到: {os.path.basename(script_path)}")
            QMessageBox.information(self, "完成", "代码已插入到脚本末尾！")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"插入失败: {e}")

class ExcludeSelectorDialog(QDialog):
    def __init__(self, parent=None, modules=None, installed=None):
        super().__init__(parent)
        self.setWindowTitle("智能排除模块")
        self.setMinimumSize(500, 400)
        self.modules = modules or []
        self.installed = installed or []
        self.selected = []
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索模块...")
        self.search.textChanged.connect(self._filter)
        layout.addWidget(self.search)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(self.list_widget)
        self._populate()
        bl = QHBoxLayout()
        btn_select_all = QPushButton("全选")
        btn_select_all.clicked.connect(self._select_all)
        bl.addWidget(btn_select_all)
        btn_select_none = QPushButton("全不选")
        btn_select_none.clicked.connect(self._select_none)
        bl.addWidget(btn_select_none)
        bl.addStretch()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self._confirm)
        bl.addWidget(btn_ok)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        bl.addWidget(btn_cancel)
        layout.addLayout(bl)

    def _populate(self):
        for mod in self.modules[:500]:
            item = QListWidgetItem(mod)
            if mod in self.installed:
                item.setForeground(QColor("green"))
                item.setToolTip("已安装")
            self.list_widget.addItem(item)

    def _filter(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _select_all(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if not item.isHidden(): item.setSelected(True)

    def _select_none(self):
        for i in range(self.list_widget.count()): self.list_widget.item(i).setSelected(False)

    def _confirm(self):
        self.selected = [item.text() for item in self.list_widget.selectedItems()]
        self.accept()

    def get_selected(self): return self.selected

class InjectSelectorDialog(QDialog):
    def __init__(self, parent=None, selected=None):
        super().__init__(parent)
        self.setWindowTitle("代码注入选项")
        self.setMinimumSize(300, 200)
        self.parent_window = parent  # 保存父窗口引用
        self.selected = selected or {
            'single_instance': False, 
            'workdir': False, 
            'resource_path': False,
        }
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("选择要注入的代码:"))
        self.chk_single = QCheckBox("防多开 (Single Instance)")
        self.chk_single.setChecked(self.selected.get('single_instance', False))
        layout.addWidget(self.chk_single)
        self.chk_workdir = QCheckBox("工作目录切换")
        self.chk_workdir.setChecked(self.selected.get('workdir', False))
        layout.addWidget(self.chk_workdir)
        self.chk_resource = QCheckBox("资源路径处理")
        self.chk_resource.setChecked(self.selected.get('resource_path', False))
        layout.addWidget(self.chk_resource)
        layout.addStretch()
        # ===== 按钮布局 =====
        bl = QHBoxLayout()
        bl.addStretch()
        # 注入版本按钮
        btn_inject_version = QPushButton("📋 版本")
        btn_inject_version.setStyleSheet("background: #2196F3; color: white; font-weight: bold;")
        btn_inject_version.clicked.connect(self._inject_version)
        bl.addWidget(btn_inject_version)
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self._confirm)
        bl.addWidget(btn_ok)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        bl.addWidget(btn_cancel)
        layout.addLayout(bl)

    def _inject_version(self):
        """直接调用父窗口的版本注入功能"""
        if self.parent_window and hasattr(self.parent_window, '_inject_version_to_exe'):
            self.parent_window._inject_version_to_exe()
        else:
            show_msg(self, "提示", "无法执行版本注入，请确保主窗口已初始化",1)

    def _confirm(self):
        self.selected = {
            'single_instance': self.chk_single.isChecked(),
            'workdir': self.chk_workdir.isChecked(),
            'resource_path': self.chk_resource.isChecked(),
        }
        self.accept()

    def get_selected(self):
        return self.selected

class HookManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("钩子管理")
        self.setMinimumSize(600, 450)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("管理 PyInstaller 钩子文件"))
        self.hook_table = QTableWidget()
        self.hook_table.setColumnCount(3)
        self.hook_table.setHorizontalHeaderLabels(["钩子名称", "状态", "路径"])
        self.hook_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.hook_table)
        btn_refresh = QPushButton("🔄 刷新列表")
        btn_refresh.clicked.connect(self._refresh)
        layout.addWidget(btn_refresh)
        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        self._refresh()

    def _refresh(self):
        self.hook_table.setRowCount(0)
        hook_dirs = []
        try:
            import PyInstaller
            hook_dirs.append(os.path.join(os.path.dirname(PyInstaller.__file__), 'hooks'))
        except: pass
        try:
            import pyi_hooks_contrib
            hook_dirs.append(os.path.join(os.path.dirname(pyi_hooks_contrib.__file__), 'hooks'))
        except: pass
        row = 0
        for hook_dir in hook_dirs:
            if os.path.exists(hook_dir):
                for f in sorted(os.listdir(hook_dir)):
                    if f.endswith('.py') and f.startswith('hook-'):
                        self.hook_table.insertRow(row)
                        self.hook_table.setItem(row, 0, QTableWidgetItem(f[5:-3]))
                        self.hook_table.setItem(row, 1, QTableWidgetItem("✓"))
                        self.hook_table.setItem(row, 2, QTableWidgetItem(hook_dir))
                        row += 1

class PyOxidizerWorker(QThread):
    """PyOxidizer 打包工作线程"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    progress_text_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_running = True
        self.process = None
        self._current_progress = 25  # 跟踪当前进度

    def run(self):
        try:
            self.log_signal.emit("🚀 开始 PyOxidizer 编译...")
            pyoxidizer = self.config.get('pyoxidizer')
            out_dir = self.config.get('out_dir')
            output_name = self.config.get('output_name')
            env = self.config.get('env', os.environ.copy())
            # PyOxidizer 可能在构建过程中生成新的 Cargo.toml
            import time
            time.sleep(1)  # 等待文件生成
            for root, dirs, files in os.walk(out_dir):
                if 'Cargo.toml' in files:
                    cargo_toml = os.path.join(root, 'Cargo.toml')
                    self._fix_cargo_toml_in_worker(cargo_toml)
            temp_dir = os.environ.get('TEMP', os.environ.get('TMP', ''))
            if temp_dir:
                for root, dirs, files in os.walk(temp_dir):
                    if 'pyoxidizer' in root and 'Cargo.toml' in files:
                        cargo_toml = os.path.join(root, 'Cargo.toml')
                        self._fix_cargo_toml_in_worker(cargo_toml)
                    if root.count(os.sep) > temp_dir.count(os.sep) + 3:
                        break
            self.process = self._popen_hidden(
                [pyoxidizer, "build", "--release", "--path", out_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                cwd=out_dir,
                env=env,
            )
            for line in iter(self.process.stdout.readline, ""):
                if not self._is_running:
                    self.process.terminate()
                    self.log_signal.emit("⏹️ 已停止")
                    self.finished_signal.emit(False)
                    return
                if line.strip():
                    self.log_signal.emit(line.rstrip())
                    low = line.lower()
                    if "compiling" in low:
                        self._current_progress = min(70, self._current_progress + 2)
                        self.progress_signal.emit(self._current_progress)
                        self.progress_text_signal.emit(f"{self._current_progress}% - 编译中...")
                    elif "linking" in low:
                        self._current_progress = 80
                        self.progress_signal.emit(80)
                        self.progress_text_signal.emit("80% - 链接中...")
                    elif "finished" in low or "installing" in low:
                        self._current_progress = 90
                        self.progress_signal.emit(90)
                        self.progress_text_signal.emit("90% - 安装中...")
            self.process.wait()
            success = self.process.returncode == 0
            if success:
                # 查找生成的 exe
                build_dir = os.path.join(out_dir, "build")
                exe_found = False
                if os.path.exists(build_dir):
                    for root, dirs, files in os.walk(build_dir):
                        for f in files:
                            if f.lower() == f"{output_name}.exe".lower():
                                src_exe = os.path.join(root, f)
                                dst_exe = os.path.join(out_dir, f"{output_name}.exe")
                                shutil.copy2(src_exe, dst_exe)
                                self.log_signal.emit(f"✅ 已复制: {dst_exe}")
                                exe_found = True
                                break
                        if exe_found:
                            break
                self.progress_signal.emit(100)
                self.progress_text_signal.emit("100% - 完成!")
                self.log_signal.emit(f"✅ PyOxidizer 打包成功！输出位置: {out_dir}")
                self.finished_signal.emit(True)
            else:
                self.log_signal.emit("❌ PyOxidizer 打包失败")
                self.finished_signal.emit(False)
        except Exception as e:
            self.log_signal.emit(f"❌ 打包出错: {e}")
            self.finished_signal.emit(False)
        finally:
            self.process = None

    def _fix_cargo_toml_in_worker(self, cargo_toml_path):
        """修复 Cargo.toml 中 edition 字段格式问题"""
        try:
            with open(cargo_toml_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            modified = False
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('edition') and '=' in stripped:
                    parts = stripped.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if value.isdigit() and not (value.startswith('"') or value.startswith("'")):
                            indent = line[:len(line) - len(line.lstrip())]
                            new_line = f'{indent}edition = "{value}"\n'
                            new_lines.append(new_line)
                            modified = True
                            continue
                new_lines.append(line)
            if modified:
                with open(cargo_toml_path, 'w', encoding='utf-8-sig') as f:
                    f.writelines(new_lines)
                self.log_signal.emit(f"🔧 已修复 edition 字段: {cargo_toml_path}")
        except Exception as e:
            self.log_signal.emit(f"⚠️ 修复 Cargo.toml 失败: {e}")

    def stop(self):
        self._is_running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass
            self.process = None

class InstallDepsThread(QThread):
    """后台安装依赖线程"""
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)
    def __init__(self, venv_python, script_path, hidden_imports_list):
        super().__init__()
        self.venv_python = venv_python
        self.script_path = script_path
        self.hidden_imports_list = hidden_imports_list 
        self._is_running = True

    def stop(self):
        self._is_running = False

    def _get_installed_packages(self, python_exe):
        """获取指定Python环境的已安装包列表（彻底隔离环境）"""
        if not python_exe or not os.path.exists(python_exe):
            return set()
        # ===== 如果开启虚拟，强制用 common_venv =====
        if hasattr(self, 'parent') and self.parent():
            if hasattr(self.parent(), 'use_venv') and self.parent().use_venv:
                venv_python = self.parent()._get_venv_python()
                if venv_python and os.path.exists(venv_python):
                    python_exe = venv_python
        import subprocess
        clean_env = {
            'PATH': os.environ.get('PATH', ''),
            'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
            'SystemRoot': os.environ.get('SystemRoot', ''),
            'COMSPEC': os.environ.get('COMSPEC', ''),
        }
        for key in list(os.environ.keys()):
            if key.upper().startswith('PYTHON') or key.upper() in ('VIRTUAL_ENV', 'CONDA_PREFIX'):
                continue
        clean_env['PYTHONNOUSERSITE'] = '1'
        clean_env['PYTHONSAFEPATH'] = '1'
        startupinfo = None
        creationflags = 0
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
        try:
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True,
                env=clean_env,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                installed = {item['name'].lower() for item in data}
                return installed
        except Exception as e:
            self.log_signal.emit(f"⚠️ 获取包列表失败: {e}")
        return set()

    def _analyze_imports(self, script_path):
        """分析脚本导入"""
        imports = set()
        try:
            with open(script_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                source = f.read()
            import ast
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split('.')[0]
                        if mod not in STANDARD_LIBS:
                            imports.add(mod)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split('.')[0]
                        if mod not in STANDARD_LIBS:
                            imports.add(mod)
        except Exception as e:
            self.log_signal.emit(f"⚠️ 分析导入失败: {e}")
        return list(imports)

    def run(self):
        try:
            # 分析脚本依赖
            used_modules = self._analyze_imports(self.script_path)
            all_needed = set(used_modules)
            for mod in self.hidden_imports_list:
                if mod not in STANDARD_LIBS:
                    all_needed.add(mod)
            # 过滤出需要安装的第三方包
            packages_to_check = []
            for mod in all_needed:
                if mod in STANDARD_LIBS:
                    continue
                if mod in {'PyInstaller', 'pyi_hooks_contrib', 'pyi_hooks'}:
                    continue
                pkg = MODULE_TO_PACKAGE.get(mod, mod)
                #if pkg.lower() == 'pil':
                    #pkg = 'pillow'
                if mod == 'et_xmlfile':
                    pkg = 'et_xmlfile'
                if mod == 'urllib3':
                    pkg = 'urllib3'
                if mod == 'certifi':
                    pkg = 'certifi'
                elif mod in ('tk', 'tkinter'):
                    pkg = 'tk'
                if pkg not in packages_to_check:
                    packages_to_check.append(pkg)
            if not packages_to_check:
                self.log_signal.emit("✅ 没有第三方包需要检查")
                self.finished_signal.emit(True)
                return
            # ===== 获取虚拟环境中已安装的包 =====
            installed = self._get_installed_packages(self.venv_python)
            # 找出缺失的包
            missing_packages = []
            for pkg in packages_to_check:
                if not self._is_running:
                    self.log_signal.emit("⏹️ 用户取消")
                    self.finished_signal.emit(False)
                    return
                if pkg.lower() in installed:
                    pass
                else:
                    self.log_signal.emit(f"   ❌ {pkg} 缺失")
                    missing_packages.append(pkg)
            if not missing_packages:
                self.log_signal.emit("✅ 所有依赖已满足")
                self.finished_signal.emit(True)
                return
            # 安装缺失的包
            self.log_signal.emit(f"📦 需要安装 {len(missing_packages)} 个包: {', '.join(missing_packages)}")
            success_count = 0
            for i, pkg in enumerate(missing_packages):
                if not self._is_running:
                    self.log_signal.emit("⏹️ 用户取消")
                    self.finished_signal.emit(False)
                    return
                progress = int((i + 1) / len(missing_packages) * 100)
                self.progress_signal.emit(progress)
                self.status_signal.emit(f"安装 {pkg} ({i+1}/{len(missing_packages)})")
                self.log_signal.emit(f"📥 安装 {pkg} ({i+1}/{len(missing_packages)})...")
                try:
                    import subprocess
                    env = os.environ.copy()
                    env.pop('PYTHONPATH', None)
                    env.pop('PYTHONHOME', None)
                    env.pop('VIRTUAL_ENV', None)
                    startupinfo = None
                    creationflags = 0
                    if sys.platform == 'win32':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        startupinfo.wShowWindow = subprocess.SW_HIDE
                        creationflags = subprocess.CREATE_NO_WINDOW
                    # 先尝试镜像源
                    success, result = pip_install(self.venv_python, pkg, env=env, timeout=180)
                    if success:
                        self.log_signal.emit(f"   ✅ {pkg} 安装成功")
                        success_count += 1
                    else:
                        # ===== 尝试包名映射 =====
                        mapped_pkg = MODULE_TO_PACKAGE.get(pkg, pkg)
                        if mapped_pkg != pkg:
                            self.log_signal.emit(f"   🔄 尝试映射包名: {mapped_pkg}")
                            success2, _ = pip_install(self.venv_python, mapped_pkg, env=env, timeout=180)
                            if success2:
                                self.log_signal.emit(f"   ✅ {mapped_pkg} 安装成功")
                                success_count += 1
                            else:
                                # ===== 最终兜底：从系统拷贝 =====
                                self.log_signal.emit(f"   ⚠️ 尝试从系统拷贝 {pkg} ...")
                                copied = False
                                if hasattr(self, 'parent') and self.parent and hasattr(self.parent, '_copy_package_from_system'):
                                    system_python = self.parent.python_path.currentText()
                                    if system_python and os.path.exists(system_python):
                                        copied = self.parent._copy_package_from_system(
                                            self.venv_python, pkg, system_python
                                        )
                                if copied:
                                    self.log_signal.emit(f"   ✅ {pkg} 从系统拷贝成功")
                                    success_count += 1
                                else:
                                    self.log_signal.emit(f"   ❌ {pkg} 安装失败")
                        else:
                            self.log_signal.emit(f"   ❌ {pkg} 安装失败")
                except subprocess.TimeoutExpired:
                    self.log_signal.emit(f"   ❌ {pkg} 安装超时")
                except Exception as e:
                    self.log_signal.emit(f"   ❌ {pkg} 安装异常: {e}")
            self.progress_signal.emit(100)
            self.status_signal.emit("完成")
            self.log_signal.emit(f"📊 依赖安装完成: {success_count}/{len(missing_packages)} 成功")
            self.finished_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"❌ 依赖安装异常: {e}")
            self.finished_signal.emit(False)

class PackageMainWindow(QMainWindow):
    """主窗口"""
    SPECIAL_BLOCKS = [
        'def ', 'async def ', 'class ', 'if __name__',
        'def main(', 'def run(', 'def start(', 'def init(',
        'def setup(', 'def execute(', 'def process(', 'def handle(',
        'def __init__(', 'def __new__(', 'def __del__(', 'def __call__(',
        'def __enter__(', 'def __exit__(', 'def __str__(', 'def __repr__(',
        'def __eq__(', 'def __hash__(', 'def __iter__(', 'def __next__(',
        'def __getitem__(', 'def __setitem__(', 'def __len__(', 'def __contains__(',
        'def on_', 'def callback', 'def hook',
        'def test_', 'def setUp(', 'def tearDown(',
        'def decorator', 'def wrapper',
        'async def main(', 'async def run(',
    ]
    venv_log_signal = pyqtSignal(str)
    venv_progress_signal = pyqtSignal(int, str)
    venv_finish_signal = pyqtSignal(bool)
    packer_ver_signal = pyqtSignal(str, str)  # packer_display, version
    def _run_hidden(self, args, **kwargs):
        """隐藏窗口运行命令（兼容所有调用）"""
        if sys.platform == 'win32':
            if 'startupinfo' not in kwargs:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = si
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess.run(args, **kwargs)

    def _popen_hidden(self, args, **kwargs):
        """隐藏窗口运行命令（Popen）"""
        if sys.platform == 'win32':
            if 'startupinfo' not in kwargs:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                si.wShowWindow = subprocess.SW_HIDE
                kwargs['startupinfo'] = si
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
        return subprocess.Popen(args, **kwargs)

    def _get_python_env_id(self, python_exe):
        """生成当前Python环境的唯一标识返回: 'system', 'venv', 'common_venv', 或路径hash"""
        if not python_exe:
            return 'default'
        py_lower = python_exe.lower().replace('\\', '/')
        # common_venv 优先判断
        if 'common_venv' in py_lower:
            return 'common_venv'
        # 项目级 .venv 或 venv
        if '/.venv/' in py_lower or '/venv/' in py_lower:
            # 提取venv所在项目名作为标识的一部分
            parts = py_lower.split('/')
            for i, p in enumerate(parts):
                if p in ('.venv', 'venv') and i > 0:
                    return f"venv:{parts[i-1]}"
            return 'venv'
        # 系统Python
        if 'program files' in py_lower or 'users/' in py_lower or '/usr/bin' in py_lower:
            # 用版本号区分不同系统Python
            try:
                ver = self.python_version.text() or ''
                ver_clean = ver.replace('Python ', '').replace('.', '_').strip()
                if ver_clean:
                    return f"system:{ver_clean}"
            except Exception:
                pass
            return 'system'
        # 其他未知环境，用路径MD5前8位
        import hashlib
        short_hash = hashlib.md5(py_lower.encode()).hexdigest()[:8]
        return f"custom:{short_hash}"

    def _get_project_cache_path(self):
        """获取当前项目的缓存文件路径"""
        script = self.input_file.text()
        if not script:
            return None
        base_name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
        base_name = re.sub(r'[\\/:*?"<>|]', '_', base_name)
        # output_dir 是 dist，项目输出是 dist/项目名
        output_dir = self.output_dir.text()
        if not output_dir:
            script_dir = os.path.dirname(script)
            output_dir = os.path.join(script_dir, "dist")
        project_output = os.path.join(output_dir, base_name)
        os.makedirs(project_output, exist_ok=True)
        cache_file = os.path.join(project_output, ".pypack_cache.json")
        return cache_file

    def _load_project_cache(self):
        """加载当前环境的项目缓存（比较包列表快照，一致则恢复，不一致则重新分析）返回: dict 或 None"""
        cache_path = self._get_project_cache_path()
        if not cache_path or not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, 'r', encoding='utf-8-sig') as f:
                cache = json.load(f)
            python_exe = self.python_path.currentText() or sys.executable
            env_id = self._get_python_env_id(python_exe)
            env_cache = cache.get('environments', {}).get(env_id)
            if env_cache is None:
                #self.safe_log(f"ℹ️ 缓存中无环境 [{env_id}]")
                return None
            # 获取当前环境的已安装包列表
            installed_map = self._get_installed_packages(python_exe)
            installed_set = set(installed_map.keys())
            # 获取缓存中的包列表快照
            cached_packages = set(env_cache.get('installed_packages', []))
            # 比较包列表是否一致
            if installed_set != cached_packages:
                diff_added = installed_set - cached_packages
                diff_removed = cached_packages - installed_set
                if diff_added:
                    self.safe_log(f"📦 新增包: {', '.join(list(diff_added)[:5])}{'...' if len(diff_added) > 5 else ''}")
                if diff_removed:
                    self.safe_log(f"📦 移除包: {', '.join(list(diff_removed)[:5])}{'...' if len(diff_removed) > 5 else ''}")
                #self.safe_log(f"🔄 环境包列表变化，缓存失效 [{env_id}]")
                return None
            #self.safe_log(f"📦 加载缓存 [{env_id}] (包列表一致: {len(installed_set)} 个包)")
            return env_cache
        except Exception as e:
            #self.safe_log(f"⚠️ 加载项目缓存失败: {e}")
            return None

    def _save_project_cache(self, analyze_result=None):
        """保存项目级缓存（按Python环境隔离，记录包列表快照）"""
        cache_path = self._get_project_cache_path()
        if not cache_path:
            return
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            cache = {}
            if os.path.exists(cache_path):
                try:
                    with open(cache_path, 'r', encoding='utf-8-sig') as f:
                        cache = json.load(f)
                except Exception:
                    pass
            if 'environments' not in cache:
                cache['environments'] = {}
            python_exe = self.python_path.currentText() or sys.executable
            env_id = self._get_python_env_id(python_exe)
            script = self.input_file.text()
            # 获取当前环境的已安装包列表（快照）
            installed_map = self._get_installed_packages(python_exe)
            installed_snapshot = list(installed_map.keys())
            env_cache = {
                'timestamp': time.time(),
                'hidden_imports': self.hidden_imports_list.copy(),
                'exclude_list': self.exclude_list.copy(),
                'manual_exclude_list': getattr(self, 'manual_exclude_list', []).copy(),
                'data_files': self.data_files_list.copy(),
                'python_path': python_exe,
                'python_version': self.python_version.text() or '',
                'installed_packages': installed_snapshot,  # 包列表快照
            }
            if analyze_result:
                result, real_imports, extra_deps, uses_tkinter = analyze_result
                env_cache['analyzed_modules'] = result
                env_cache['real_imports'] = real_imports
                env_cache['extra_deps'] = extra_deps
                env_cache['uses_tkinter'] = uses_tkinter
            cache['environments'][env_id] = env_cache
            temp_path = cache_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, cache_path)
            self.safe_log(f"💾 保存缓存 [{env_id}] (包列表快照: {len(installed_snapshot)} 个包)")
        except Exception as e:
            pass
            #self.safe_log(f"⚠️ 保存项目缓存失败: {e}")

    def _init_from_cache(self):
        """同步读取缓存，用于UI初始化"""
        self._cached_upx = ""
        self._cached_python = ""
        self._cached_python_ver = ""
        self._cached_backend = "auto"
        try:
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
                upx = cache.get('upx', {})
                if upx.get('path') and os.path.exists(upx['path']):
                    self._cached_upx = upx['path']
                    upx_path = upx['path']
                    import re
                    upx_path = re.sub(r'\.exe$', '.exe', upx_path, flags=re.IGNORECASE)
                    self.upx_path.setText(upx_path)
                py = cache.get('python', {})
                if py.get('path') and os.path.exists(py['path']):
                    self._cached_python = py['path']
                    self._cached_python_ver = py.get('version', '')
                self._cached_backend = cache.get('compiler_backend', 'auto')
        except:
            pass

    def _open_inject_selector(self):
        """打开注入代码选择器"""
        dialog = InjectSelectorDialog(self, self.inject_selected)  # 传入 self
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.inject_selected = dialog.get_selected()
            self.safe_log(f"💉 注入选项: {self.inject_selected}")

    def _auto_fix_formatting_preview(self, file_path):
        backup_path = self._backup_file(file_path)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            original_content = f.read()
            lines = original_content.split('\n')
        original_count = len(lines)
        changes = []
        # ===== 获取需要插入的位置 =====
        try:
            tree = ast.parse(original_content)
        except SyntaxError as e:
            self.safe_log(f"⚠️ 语法错误，跳过修复: {e}")
            return original_content, original_content, ["语法错误，无法修复"], backup_path
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        insert_positions = self._get_insert_original_lines(tree)
        # ===== 删除所有空行 =====
        deleted_count = 0
        non_empty_lines = []
        for line in lines:
            if line.strip() == '':
                deleted_count += 1
            else:
                non_empty_lines.append(line.rstrip('\n'))
        # ===== 计算新行号映射 =====
        line_mapping = {}
        new_line_no = 1
        for i, line in enumerate(lines):
            if line.strip() != '':
                line_mapping[i + 1] = new_line_no
                new_line_no += 1
        # ===== 转换插入位置 =====
        insert_new_positions = set()
        for original_lineno in insert_positions:
            if original_lineno in line_mapping:
                insert_new_positions.add(line_mapping[original_lineno])
        # ===== 重建代码，插入空行 =====
        result = []
        inserted_count = 0
        for i, line in enumerate(non_empty_lines):
            new_line_no = i + 1
            if new_line_no in insert_new_positions:
                if result and result[-1] != '':
                    result.append('')
                    inserted_count += 1
            result.append(line)
        # ===== 清理末尾 =====
        while len(result) > 1 and result[-1] == '':
            result.pop()
        new_content = '\n'.join(result)
        new_count = len(result)
        # ===== 提示信息 =====
        net_change = new_count - original_count
        changes.append(f"删除空行: {deleted_count} 行")
        changes.append(f"插入空行: {inserted_count} 行")
        changes.append(f"行数变化: {original_count} → {new_count} 行 ({'+' if net_change > 0 else ''}{net_change})")
        # 写回文件
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        self.safe_log(f"   ✅ 空行修复: {original_count} → {new_count} 行 (减少 {deleted_count - inserted_count} 行)")
        return original_content, new_content, changes, backup_path

    def _get_insert_original_lines(self, tree):
        """获取需要插入空行的原始行号"""
        insert_lines = set()

        def is_function_def(node):
            return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))

        def is_class_def(node):
            return isinstance(node, ast.ClassDef)

        def is_nested_function(node):
            """判断是否是嵌套函数（父节点是函数或类）"""
            parent = getattr(node, 'parent', None)
            return parent is not None and (is_function_def(parent) or is_class_def(parent))

        def is_method(node):
            """判断是否是类中的方法"""
            parent = getattr(node, 'parent', None)
            return parent is not None and is_class_def(parent) and is_function_def(node)
        # ===== 1. 模块级函数/类之间 =====
        module_body = tree.body
        prev_node = None
        for node in module_body:
            if is_function_def(node) or is_class_def(node):
                if prev_node is not None:
                    insert_lines.add(node.lineno)
                prev_node = node
        # ===== 2. 遍历所有函数和类 =====
        for node in ast.walk(tree):
            # ===== 类内部的方法之间 =====
            if is_class_def(node):
                body = getattr(node, 'body', [])
                prev_method = None
                for item in body:
                    if is_method(item):
                        if prev_method is not None:
                            insert_lines.add(item.lineno)
                        prev_method = item
            # ===== 函数/类内部的嵌套函数前 =====
            if is_function_def(node):
                body = getattr(node, 'body', [])
                # 检查body中是否有嵌套函数
                for item in body:
                    if is_function_def(item):
                        # 嵌套函数前插入空行
                        if is_nested_function(item):
                            insert_lines.add(item.lineno)
            # ===== 类内部的嵌套函数前 =====
            if is_class_def(node):
                body = getattr(node, 'body', [])
                for item in body:
                    if is_function_def(item):
                        if not is_method(item):
                            insert_lines.add(item.lineno)
        # ===== 3. if __name__ == '__main__' 前 =====
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                # 检查是否是 if __name__ == '__main__'
                if isinstance(node.test, ast.Compare):
                    if (isinstance(node.test.left, ast.Name) and
                            node.test.left.id == '__name__'):
                        # 检查是否在模块顶层
                        parent = getattr(node, 'parent', None)
                        if parent is None or isinstance(parent, ast.Module):
                            insert_lines.add(node.lineno)
        return insert_lines

    def _apply_fix(self, file_path):
        """应用修复（已由预览对话框确认）"""

    def _update_cache_upx(self, upx_path):
        try:
            cache = {}
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
            cache['upx'] = {'path': upx_path, 'time': time.time()}
            with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _update_cache_python(self, py_path):
        try:
            cache = {}
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
            version = ""
            try:
                result = self._run_hidden([py_path, '--version'], capture_output=True, text=True,
                                        startupinfo=get_startupinfo())
                version = result.stdout.strip() or result.stderr.strip()
            except:
                pass
            cache['python'] = {'path': py_path, 'version': version, 'time': time.time()}
            with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _update_cache_backend(self, backend):
        try:
            cache = {}
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
            cache['compiler_backend'] = backend
            with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _load_all_backend_cache(self, cache):
        """从缓存加载所有后端信息"""
        compiler = cache.get('compiler', {})
        self._cached_has_msvc = compiler.get('msvc', False)
        self._cached_has_mingw = compiler.get('mingw', False)
        self._cached_msvc_path = compiler.get('msvc_path', '')
        self._cached_mingw_path = compiler.get('mingw_path', '')
        self._cached_msvc_version = compiler.get('msvc_version', '')
        self._cached_mingw_version = compiler.get('mingw_version', '')
        rust = cache.get('rust_compiler', {})
        self._cached_has_cargo = rust.get('has_cargo', False)
        self._cached_has_rustc = rust.get('has_rustc', False)
        self._cached_cargo_path = rust.get('cargo_path', '')
        self._cached_rustc_path = rust.get('rustc_path', '')
        self._cached_rust_version = rust.get('rust_version', '')
        nsis = cache.get('nsis', {})
        self._cached_has_nsis = nsis.get('has_nsis', False)
        self._cached_nsis_path = nsis.get('nsis_path', '')
        self._cached_nsis_version = nsis.get('nsis_version', '')
        # ===== 加载packer_versions（保留全部） =====
        self._packer_versions_cache = cache.get('packer_versions', {})

    def _save_all_backend_cache(self):
        """保存所有后端到缓存"""
        self.save_cache()

    def _load_all_cached_data(self):
        """从缓存加载数据（强制排序）"""
        self._load_config()
        if not os.path.exists(self.global_cache_file):
            return
        try:
            with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                cache = json.load(f)
            # ===== 1. 加载Python列表（强制排序） =====
            python_list = cache.get('python_list', [])
            QTimer.singleShot(100, self._filter_python_list)
            if python_list:
                # ===== 强制排序：项目venv → 系统 → common_venv =====
                project_venv = []
                system_py = []
                common_venv = []
                for path in python_list:
                    path_lower = path.lower()
                    if 'common_venv' in path_lower:
                        common_venv.append(path)
                    elif '.venv' in path_lower:
                        project_venv.append(path)
                    else:
                        system_py.append(path)
                python_list = project_venv + system_py + common_venv
                self.python_path.clear()
                for p in python_list:
                    if os.path.exists(p):
                        self.python_path.addItem(p)
                py = cache.get('python', {})
                cached_path = py.get('path')
                if cached_path and os.path.exists(cached_path):
                    idx = self.python_path.findText(cached_path)
                    if idx >= 0:
                        self.python_path.setCurrentIndex(idx)
                        ver = py.get('version', '')
                        if ver:
                            self.python_version.setText(ver)
                            python_types = cache.get('python_types', {})
                            ptype = python_types.get(cached_path, "Python")
                            self.status_python.setText(f"🐍 {ptype}: {ver}")
            # ===== 2. 加载打包器版本（只加载到内存） =====
            packer_versions = cache.get('packer_versions', {})
            if packer_versions:
                self._packer_versions_cache = packer_versions
                self._packer_versions_detected = True
                self._packer_cache_loaded = True
            # ===== 3. 加载编译器（只加载到内存） =====
            compiler = cache.get('compiler', {})
            if compiler:
                self._cached_has_msvc = compiler.get('msvc', False)
                self._cached_has_mingw = compiler.get('mingw', False)
                self._cached_msvc_path = compiler.get('msvc_path', '')
                self._cached_mingw_path = compiler.get('mingw_path', '')
                self._cached_msvc_version = compiler.get('msvc_version', '')
                self._cached_mingw_version = compiler.get('mingw_version', '')
            # ===== 4. 加载Rust =====
            rust = cache.get('rust_compiler', {})
            if rust:
                self._cached_has_cargo = rust.get('has_cargo', False)
                self._cached_has_rustc = rust.get('has_rustc', False)
                self._cached_cargo_path = rust.get('cargo_path', '')
                self._cached_rustc_path = rust.get('rustc_path', '')
                self._cached_rust_version = rust.get('rust_version', '')
            # ===== 5. 加载NSIS =====
            nsis = cache.get('nsis', {})
            if nsis:
                self._cached_has_nsis = nsis.get('has_nsis', False)
                self._cached_nsis_path = nsis.get('nsis_path', '')
                self._cached_nsis_version = nsis.get('nsis_version', '')
            # ===== 6. 加载主题 =====
            theme_idx = cache.get('theme_index', 0)
            if 0 <= theme_idx < len(self.themes):
                self.current_theme_idx = theme_idx
                self._apply_theme()
                if hasattr(self, 'theme_btn'):
                    self.theme_btn.setText(self.themes[theme_idx])
            # ===== 7. 加载UPX =====
            upx = cache.get('upx', {})
            if upx.get('path') and os.path.exists(upx['path']):
                self.upx_path.setText(upx['path'])
                formatted_path = self._format_path(upx_path)
                self.upx_path.setText(formatted_path)
                self._set_upx_environment(upx_path)
            else:
                # ===== 缓存中没有UPX，异步查找 =====
                threading.Thread(target=self._async_find_upx, daemon=True).start()
            # ===== 8. 后端选择 =====
            backend = cache.get('compiler_backend', 'auto')
            if hasattr(self, 'nuitka_backend_combo') and self.nuitka_backend_combo is not None:
                idx = self.nuitka_backend_combo.findText(backend)
                if idx >= 0:
                    self.nuitka_backend_combo.setCurrentIndex(idx)
            # ===== 9.加载清理阈值 =====
            threshold = cache.get('clean_threshold', 100)
            if hasattr(self, 'clean_threshold_spin'):
                self.clean_threshold_spin.setValue(threshold)
        except Exception as e:
            pass

    def _load_cache_fast(self):
        """快速加载缓存 - 只加载显示需要的数据"""
        try:
            if not os.path.exists(self.global_cache_file):
                return
            with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                cache = json.load(f)
            # ===== 1. 加载Python列表（快速） =====
            python_list = cache.get('python_list', [])
            if python_list:
                self.python_path.clear()
                for p in python_list:
                    if os.path.exists(p):
                        self.python_path.addItem(p)
                py = cache.get('python', {})
                cached_path = py.get('path')
                if cached_path and os.path.exists(cached_path):
                    idx = self.python_path.findText(cached_path)
                    if idx >= 0:
                        self.python_path.setCurrentIndex(idx)
                        ver = py.get('version', '')
                        if ver:
                            self.python_version.setText(ver)
                            python_types = cache.get('python_types', {})
                            ptype = python_types.get(cached_path, "Python")
                            self.status_python.setText(f"🐍 {ptype}: {ver}")
            # ===== 2. 加载打包器版本（只显示当前） =====
            packer_versions = cache.get('packer_versions', {})
            if packer_versions:
                self._packer_versions_cache = packer_versions
                self._packer_versions_detected = True
                self._packer_cache_loaded = True
                current = self.packer_combo.currentText()
                display = self._get_packer_display_name(current)
                python_exe = self.python_path.currentText()
                if python_exe:
                    cache_key = f"{display}@{python_exe}"
                    version = packer_versions.get(cache_key)
                    if version:
                        self._update_packer_status(display, version)
            # ===== 3. 加载编译器状态（只保存数据，不更新UI） =====
            compiler = cache.get('compiler', {})
            if compiler:
                self._cached_has_msvc = compiler.get('msvc', False)
                self._cached_has_mingw = compiler.get('mingw', False)
                self._cached_msvc_path = compiler.get('msvc_path', '')
                self._cached_mingw_path = compiler.get('mingw_path', '')
                self._cached_msvc_version = compiler.get('msvc_version', '')
                self._cached_mingw_version = compiler.get('mingw_version', '')
            # ===== 4. 加载主题 =====
            theme_idx = cache.get('theme_index', 0)
            if 0 <= theme_idx < len(self.themes):
                self.current_theme_idx = theme_idx
                self._apply_theme()
                if hasattr(self, 'theme_btn'):
                    self.theme_btn.setText(self.themes[theme_idx])
            # ===== 5. 加载UPX =====
            upx = cache.get('upx', {})
            if upx.get('path') and os.path.exists(upx['path']):
                self.upx_path.setText(upx['path'])
            # ===== 6. 后端选择（只保存，不更新UI） =====
            backend = cache.get('compiler_backend', 'auto')
            if hasattr(self, 'nuitka_backend_combo') and self.nuitka_backend_combo is not None:
                idx = self.nuitka_backend_combo.findText(backend)
                if idx >= 0:
                    self.nuitka_backend_combo.setCurrentIndex(idx)
            # ===== 延迟加载剩余功能 =====
            QTimer.singleShot(300, self._load_remaining_cache)
        except Exception as e:
            pass

    def _load_remaining_cache(self):
        """加载剩余的缓存数据（延迟执行）"""
        try:
            if not os.path.exists(self.global_cache_file):
                return
            with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                cache = json.load(f)
            # ===== Rust =====
            rust = cache.get('rust_compiler', {})
            if rust:
                self._cached_has_cargo = rust.get('has_cargo', False)
                self._cached_has_rustc = rust.get('has_rustc', False)
                self._cached_cargo_path = rust.get('cargo_path', '')
                self._cached_rustc_path = rust.get('rustc_path', '')
                self._cached_rust_version = rust.get('rust_version', '')
            # ===== NSIS =====
            nsis = cache.get('nsis', {})
            if nsis:
                self._cached_has_nsis = nsis.get('has_nsis', False)
                self._cached_nsis_path = nsis.get('nsis_path', '')
                self._cached_nsis_version = nsis.get('nsis_version', '')
            self._display_compiler_status()
            QTimer.singleShot(100, self._enable_all_drag_drop)
            QTimer.singleShot(200, self._auto_detect_current_dir)
            QTimer.singleShot(300, self._refresh_nuitka_gui_display)
        except Exception as e:
            pass

    def _apply_cached_paths(self):
        """启动时从缓存加载所有配置"""
        try:
            cache = load_cache()
            self._load_all_backend_cache(cache)
            # Python路径加载
            python_list = cache.get('python_list', [])
            python_types = cache.get('python_types', {})
            py = cache.get('python', {})
            if python_list:
                self.python_path.clear()
                for p in python_list:
                    if os.path.exists(p):
                        self.python_path.addItem(p)
                cached_path = py.get('path')
                if cached_path and os.path.exists(cached_path):
                    idx = self.python_path.findText(cached_path)
                    if idx >= 0:
                        self.python_path.setCurrentIndex(idx)
                        self.python_version.setText(py.get('version', ''))
                        ptype = python_types.get(cached_path, "Python")
                        ver = py.get('version', '')
                        if ver:
                            self.status_python.setText(f"🐍 {ptype}: {ver}")
                        else:
                            self.status_python.setText(f"🐍 {ptype}: {cached_path}")
                        QTimer.singleShot(100, self._on_python_selected)
                    elif self.python_path.count() > 0:
                        self.python_path.setCurrentIndex(0)
                        py_path = self.python_path.currentText()
                        if py_path and os.path.exists(py_path):
                            try:
                                result = self._run_hidden([py_path, '--version'], capture_output=True, text=True, timeout=2)
                                ver = result.stdout.strip() or result.stderr.strip()
                                if ver:
                                    self.python_version.setText(ver)
                                    ptype = python_types.get(py_path, "Python")
                                    self.status_python.setText(f"🐍 {ptype}: {ver}")
                            except:
                                pass
                elif py.get('path') and os.path.exists(py['path']):
                    idx = self.python_path.findText(py['path'])
                    if idx < 0:
                        self.python_path.addItem(py['path'])
                        idx = self.python_path.findText(py['path'])
                    if idx >= 0:
                        self.python_path.setCurrentIndex(idx)
                        self.python_version.setText(py.get('version', ''))
                        self.status_python.setText(f"🐍 Python: {py.get('version', '')}")
                        QTimer.singleShot(100, self._on_python_selected)
            # ===== UPX =====
            upx = cache.get('upx', {})
            if upx.get('path') and os.path.exists(upx['path']):
                self.upx_path.setText(upx['path'])
                formatted_path = self._format_path(upx_path)
                self.upx_path.setText(formatted_path)
                self._set_upx_environment(upx_path)
            else:
                # ===== 缓存中没有UPX，异步查找 =====
                threading.Thread(target=self._async_find_upx, daemon=True).start()
            backend = cache.get('compiler_backend', 'auto')
            if hasattr(self, 'nuitka_backend_combo') and self.nuitka_backend_combo is not None:
                idx = self.nuitka_backend_combo.findText(backend)
                if idx >= 0:
                    self.nuitka_backend_combo.setCurrentIndex(idx)
            # 打包器版本
            self._packer_versions_cache = cache.get('packer_versions', {})
            if self._packer_versions_cache:
                self._packer_versions_detected = True
            # 主题
            theme_idx = cache.get('theme_index', 0)
            if 0 <= theme_idx < len(self.themes):
                self.current_theme_idx = theme_idx
                self._apply_theme()
                if hasattr(self, 'theme_btn'):
                    self.theme_btn.setText(self.themes[theme_idx])
            QTimer.singleShot(100, self._update_all_backend_ui)
            python_exe = self.python_path.currentText()
            if python_exe and os.path.exists(python_exe):
                has_cache = False
                for key in self._packer_versions_cache.keys():
                    if key.endswith(python_exe):
                        has_cache = True
                        break
                if not has_cache and not self._packer_versions_detected:
                    QTimer.singleShot(500, self._detect_all_packer_versions_async)
                    # ===== 只检测编译器 =====
                    QTimer.singleShot(100, self._detect_compilers_async)
            # ===== 新增：恢复虚拟环境状态 =====
            if cache.get('venv_enabled', False):
                venv_python = cache.get('venv_python')
                if venv_python and os.path.exists(venv_python):
                    self.venv_mode.blockSignals(True)
                    self.venv_mode.setChecked(True)
                    self.use_venv = True
                    self.venv_mode.blockSignals(False)
                    display_path = self._format_path(venv_python)
                    if self.python_path.findText(display_path) < 0:
                        self.python_path.addItem(display_path)
                    self.python_path.setCurrentText(display_path)
                    try:
                        result = self._run_hidden([venv_python, '--version'], capture_output=True, text=True, timeout=2)
                        ver = result.stdout.strip() or result.stderr.strip()
                        if ver:
                            self.python_version.setText(ver)
                            self.status_python.setText(f"🐍 {ver} (venv)")
                    except:
                        pass
                    self.safe_log(f"✅ 已恢复虚拟环境: {venv_python}")
        except Exception as e:
            self.safe_log(f"⚠️ 加载缓存失败: {e}")

    def save_cache(self):
        """保存完整缓存到文件（从 python_list 重建 python_types，并排序）"""
        old_cache = {}
        if os.path.exists(self.global_cache_file):
            try:
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    old_cache = json.load(f)
            except:
                pass
        cache = {}
        # 1. 保留 upx 字段
        if old_cache.get('upx'):
            cache['upx'] = old_cache['upx']
        # 2. 合并 python_list 并排序
        merged_list = old_cache.get('python_list', [])
        current_list = [self.python_path.itemText(i) for i in range(self.python_path.count())] if self.python_path else []
        for p in current_list:
            if p not in merged_list:
                merged_list.append(p)
        # ===== 强制排序：项目venv → 系统 → common_venv =====
        project_venv = []
        system_py = []
        common_venv = []
        for path in merged_list:
            path_lower = path.lower()
            if 'common_venv' in path_lower:
                common_venv.append(path)
            elif '.venv' in path_lower:
                project_venv.append(path)
            else:
                system_py.append(path)
        merged_list = project_venv + system_py + common_venv
        cache['python_list'] = merged_list
        # 3. 从 merged_list 重建 python_types
        merged_types = {}
        for path in merged_list:
            path_lower = path.lower()
            if 'common_venv' in path_lower:
                merged_types[path] = 'common_venv'
            elif '.venv' in path_lower or 'venv' in path_lower:
                merged_types[path] = 'venv'
            else:
                merged_types[path] = 'system'
        cache['python_types'] = merged_types
        # 4. 更新当前选中的 Python
        if self.python_path and self.python_path.count() > 0:
            current_path = self.python_path.currentText()
            if current_path:
                cache['python'] = {
                    'path': current_path,
                    'version': self.python_version.text() if self.python_version else '',
                    'time': time.time()
                }
        # 5. 保留 compiler 字段
        if old_cache.get('compiler'):
            cache['compiler'] = old_cache['compiler']
        elif self._cached_has_msvc or self._cached_has_mingw:
            cache['compiler'] = {
                'msvc': self._cached_has_msvc,
                'mingw': self._cached_has_mingw,
                'msvc_path': self._cached_msvc_path,
                'mingw_path': self._cached_mingw_path,
                'msvc_version': self._cached_msvc_version,
                'mingw_version': self._cached_mingw_version,
            }
        # 6. 保留 rust_compiler 字段
        if old_cache.get('rust_compiler'):
            cache['rust_compiler'] = old_cache['rust_compiler']
        elif self._cached_has_cargo or self._cached_has_rustc:
            cache['rust_compiler'] = {
                'has_cargo': self._cached_has_cargo,
                'has_rustc': self._cached_has_rustc,
                'cargo_path': self._cached_cargo_path,
                'rustc_path': self._cached_rustc_path,
                'rust_version': self._cached_rust_version,
            }
        # 7. 保留 nsis 字段
        if old_cache.get('nsis'):
            cache['nsis'] = old_cache['nsis']
        elif self._cached_has_nsis:
            cache['nsis'] = {
                'has_nsis': self._cached_has_nsis,
                'nsis_path': self._cached_nsis_path,
                'nsis_version': self._cached_nsis_version,
            }
        # 8. 保留 packer_versions
        if old_cache.get('packer_versions'):
            cache['packer_versions'] = old_cache['packer_versions']
        elif self._packer_versions_cache:
            cache['packer_versions'] = self._packer_versions_cache
        # 9. compiler_backend
        if hasattr(self, 'nuitka_backend_combo') and self.nuitka_backend_combo:
            cache['compiler_backend'] = self.nuitka_backend_combo.currentText()
        elif old_cache.get('compiler_backend'):
            cache['compiler_backend'] = old_cache['compiler_backend']
        else:
            cache['compiler_backend'] = 'auto'
        # 10. theme_index
        cache['theme_index'] = self.current_theme_idx
        # ===== 写入文件 =====
        if cache:
            try:
                temp_file = self.global_cache_file + '.tmp'
                with open(temp_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
                os.replace(temp_file, self.global_cache_file)
            except Exception as e:
                pass

    def _display_compiler_status(self):
        """显示编译器状态（从缓存）- 只用于Nuitka"""
        if not hasattr(self, 'nuitka_backend_combo') or self.nuitka_backend_combo is None:
            return
        backend = self.nuitka_backend_combo.currentText()
        if backend == "MSVC":
            if self._cached_has_msvc and self._cached_msvc_version:
                self.status_compiler.setText(f"🔧 MSVC: {self._cached_msvc_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 MSVC: 未安装")
                self.status_compiler.setStyleSheet("color: red;")
        elif backend == "MinGW64":
            if self._cached_has_mingw and self._cached_mingw_version:
                self.status_compiler.setText(f"🔧 MinGW: {self._cached_mingw_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 MinGW: 未安装")
                self.status_compiler.setStyleSheet("color: red;")
        else:
            if self._cached_has_mingw and self._cached_mingw_version:
                self.status_compiler.setText(f"🔧 MinGW: {self._cached_mingw_version}")
                self.status_compiler.setStyleSheet("color: green;")
            elif self._cached_has_msvc and self._cached_msvc_version:
                self.status_compiler.setText(f"🔧 MSVC: {self._cached_msvc_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 编译器: 未安装")
                self.status_compiler.setStyleSheet("color: red;")

    def _display_rust_status(self):
        """显示Rust状态（从缓存）- 只用于PyOxidizer和PyApp"""
        if self._cached_has_cargo and self._cached_has_rustc:
            self.status_compiler.setText(f"🔧 Rust: {self._cached_rust_version}")
            self.status_compiler.setStyleSheet("color: green;")
        elif self._cached_has_cargo:
            self.status_compiler.setText("🔧 Rust: 缺少 rustc")
            self.status_compiler.setStyleSheet("color: orange;")
        elif self._cached_has_rustc:
            self.status_compiler.setText("🔧 Rust: 缺少 cargo")
            self.status_compiler.setStyleSheet("color: orange;")
        else:
            self.status_compiler.setText("🔧 Rust: 未安装")
            self.status_compiler.setStyleSheet("color: red;")

    def _display_nsis_status(self):
        """显示NSIS状态（从缓存）"""
        if self._cached_has_nsis:
            self.status_compiler.setText(f"🔧 NSIS: {self._cached_nsis_version}")
            self.status_compiler.setStyleSheet("color: green;")
        else:
            self.status_compiler.setText("🔧 NSIS: 未安装")
            self.status_compiler.setStyleSheet("color: orange;")

    def _display_packer_version_from_cache(self, packer):
        """从缓存显示打包器版本（不触发检测）"""
        if not hasattr(self, 'python_path') or self.python_path is None:
            return
        if not hasattr(self, 'packer_combo') or self.packer_combo is None:
            return
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.status_packer.setText("📦 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            return
        display = self._get_packer_display_name(packer)
        cache_key = f"{display}@{python_exe}"
        # 先查内存缓存
        version = self._packer_versions_cache.get(cache_key)
        # 内存没有，查文件缓存
        if version is None:
            try:
                if os.path.exists(self.global_cache_file):
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        cache_data = json.load(f)
                    packer_versions = cache_data.get('packer_versions', {})
                    version = packer_versions.get(cache_key)
                    if version is not None:
                        self._packer_versions_cache[cache_key] = version
                        self._packer_cache_loaded = True
            except Exception as e:
                pass
        # 有版本直接显示，不触发检测
        if version is not None:
            self._update_packer_status(display, version or "")
            return
        # 缓存中没有，显示"未检测"并触发后台检测
        self.status_packer.setText(f"📦 {display}: 未检测")
        self.status_packer.setStyleSheet("color: orange;")
        # 只在有Python且未在检测中时触发
        if not self._detecting_packer_versions and python_exe and os.path.exists(python_exe):
            QTimer.singleShot(100, self._detect_all_packer_versions_async)

    def _update_all_backend_ui(self):
        """从缓存更新所有后端UI + 打包器版本"""
        packer = self.packer_combo.currentText()
        if self._ui_updated:
            return 
        # ===== 清空状态栏 =====
        self.status_compiler.setText("")
        self.status_compiler.setStyleSheet("")
        # ===== 更新后端状态 =====
        if packer == "Nuitka":
            self.status_compiler.setVisible(True)
            self._display_compiler_status()
            if hasattr(self, 'backend_display_label'):
                self._update_backend_display(self.nuitka_backend_combo.currentText())
        elif packer in ["PyOxidizer", "PyApp"]:
            self.status_compiler.setVisible(True)
            self._display_rust_status()
        elif packer == "Pynsist":
            self.status_compiler.setVisible(True)
            self._display_nsis_status()
        else:
            self.status_compiler.setVisible(False)
            self.status_compiler.setText("")
        # ===== 更新打包器版本 =====
        self._display_packer_version_from_cache(packer)

    def _save_backend_to_cache(self, backend):
        """保存后端选择到缓存"""
        try:
            if not hasattr(self, 'nuitka_backend_combo') or self.nuitka_backend_combo is None:
                return
            cache = {}
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
            cache['compiler_backend'] = backend
            with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _add_tooltip(self, widget, text):
        """为控件添加鼠标悬停提示"""
        if widget:
            widget.setToolTip(text)

    def _check_single_instance(self):
        """检查是否已有实例运行（允许源码和EXE同时运行）"""
        import socket
        import hashlib
        # 判断当前运行模式
        is_frozen = getattr(sys, 'frozen', False)
        # ===== 源码和EXE用完全不同的端口段 =====
        if is_frozen:
            # EXE模式：使用 28000-28999 段
            program_name = os.path.basename(sys.executable).replace('.exe', '')
            port_hash = int(hashlib.md5(program_name.encode()).hexdigest()[:6], 16)
            port = 28000 + (port_hash % 1000)
        else:
            # 源码模式：使用 29000-29999 段（与EXE完全不同）
            # 用当前脚本路径做hash，不同项目源码互不干扰
            script_path = os.path.abspath(__file__)
            port_hash = int(hashlib.md5(script_path.encode()).hexdigest()[:6], 16)
            port = 29000 + (port_hash % 1000)
        self.port = port
        self.sock = None
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(('127.0.0.1', port))
            return True
        except socket.error:
            return False

    def __init__(self):
        super().__init__()
        self.about_dialog = None
        self.is_frozen = getattr(sys, 'frozen', False)
        if not self._check_single_instance():
            sys.exit(0)
        if getattr(sys, 'frozen', False):
            QTimer.singleShot(100, self._async_find_system_python)
        else:
            QTimer.singleShot(100, self._async_find_python)
        self.current_dir = get_exe_directory()
        self.dist_dir = os.path.join(self.current_dir, "dist")
        self.config_file = os.path.join(self.current_dir, "pack_config.json")
        self.global_cache_file = os.path.join(self.current_dir, ".global_cache.json")
        self.is_building = False
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.start_time = None
        self.use_venv = False
        self.version_info = None
        self.analyzed_modules = []
        self.installed_packages = None
        self.process = None
        self.hidden_imports_list = []
        self.data_files_list = []
        self.exclude_list = []
        self.manual_exclude_list = []
        self.inject_selected = {'single_instance': False, 'workdir': False, 'resource_path': False}
        self._auto_detected = False
        self._venv_finishing = False
        self._injected_this_build = False
        self._compiler_cache = None
        self._compiler_cache_time = 0
        self._packer_version_cache = {}
        self._spec_monitor_timer = None
        self._stop_logging = False
        self._building_exclude = False
        # ===== 从缓存文件加载数据到内存（不重置为空） =====
        self._packages_cache = {}  
        self._packages_cache_time = {}
        self._cached_has_msvc = False
        self._cached_has_mingw = False
        self._cached_msvc_path = ""
        self._cached_mingw_path = ""
        self._cached_msvc_version = ""
        self._cached_mingw_version = ""
        self._cached_has_cargo = False
        self._cached_has_rustc = False
        self._cached_cargo_path = ""
        self._cached_rustc_path = ""
        self._cached_rust_version = ""
        self._cached_has_nsis = False
        self._cached_nsis_path = ""
        self._cached_nsis_version = ""
        self._packer_versions_cache = {}
        self._nuitka_compat_notified = False
        self._ui_updated = False
        self._detecting_packer_versions = False
        self._packer_versions_detected = False
        self._packer_cache_loaded = False
        self._syntax_cache = None 
        self._analyze_done = False  
        self._last_non_venv_python = ""  
        # ===== 读取缓存文件到内存 =====
        if os.path.exists(self.global_cache_file):
            try:
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache_data = json.load(f)
                    # 加载打包器版本
                    if 'packer_versions' in cache_data:
                        self._packer_versions_cache = cache_data['packer_versions']
                        self._packer_versions_detected = True
                        self._packer_cache_loaded = True
                    # 加载编译器
                    compiler = cache_data.get('compiler', {})
                    if compiler:
                        self._cached_has_msvc = compiler.get('msvc', False)
                        self._cached_has_mingw = compiler.get('mingw', False)
                        self._cached_msvc_path = compiler.get('msvc_path', '')
                        self._cached_mingw_path = compiler.get('mingw_path', '')
                        self._cached_msvc_version = compiler.get('msvc_version', '')
                        self._cached_mingw_version = compiler.get('mingw_version', '')
                    # 加载Rust
                    rust = cache_data.get('rust_compiler', {})
                    if rust:
                        self._cached_has_cargo = rust.get('has_cargo', False)
                        self._cached_has_rustc = rust.get('has_rustc', False)
                        self._cached_cargo_path = rust.get('cargo_path', '')
                        self._cached_rustc_path = rust.get('rustc_path', '')
                        self._cached_rust_version = rust.get('rust_version', '')
                    # 加载NSIS
                    nsis = cache_data.get('nsis', {})
                    if nsis:
                        self._cached_has_nsis = nsis.get('has_nsis', False)
                        self._cached_nsis_path = nsis.get('nsis_path', '')
                        self._cached_nsis_version = nsis.get('nsis_version', '')
            except Exception as e:
                pass
        self.exclude_from_pack = []
        try:
            self.cpu_count = multiprocessing.cpu_count()
        except:
            self.cpu_count = 4
        self.job_options = ["auto"] + [str(j) for j in [1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64] if j <= self.cpu_count]
        self.music_visible = False
        self.music_files = []
        self.current_music_index = 0
        self.music_process = None
        self.music_play_btn = None
        self.player_widget = None
        self.player_container = None
        self.log_splitter = None
        self.themes = ["🌞 默认主题", "🌅 暗夜深邃", "☁️ 云淡风轻", "🌿 薄荷绿意", "🌸 樱花粉嫩", "🌌 星际紫韵",
                       "🌊 深海蔚蓝"]
        self.current_theme_idx = 0
        self.theme_progress_styles = {
            "🌞 默认主题": "striped",
            "🌅 暗夜深邃": "emoji",
            "☁️ 云淡风轻": "striped",
            "🌿 薄荷绿意": "green",
            "🌸 樱花粉嫩": "pink",
            "🌌 星际紫韵": "purple",
            "🌊 深海蔚蓝": "blue",
        }
        self._init_ui_attributes()
        self._init_ui()
        self.setWindowTitle(f"Python代码打包工具 - 跨平台支持 {BUILD_DATE}")
        screen = QApplication.primaryScreen().geometry()
        screen_w, screen_h = screen.width(), screen.height()
        win_w = max(min(int(screen_w * 0.9), 1500), 975)
        win_h = max(min(int(screen_h * 0.8), 1000), 650)
        self.setMinimumSize(600, 400)
        self.resize(win_w, win_h)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        QTimer.singleShot(10, self._apply_theme)
        self.input_file.textChanged.connect(self._on_input_file_changed)
        self.show()
        QApplication.processEvents()
        # ===== 窗口显示后再加载数据 =====
        QTimer.singleShot(50, self._load_all_cached_data)
        self.venv_log_signal.connect(self.safe_log)
        self.venv_progress_signal.connect(self._on_venv_progress)
        self.venv_finish_signal.connect(self._on_venv_finish)
        self.packer_ver_signal.connect(self._update_packer_status)
        FILTER_MODULES = {'PyInstaller', 'module', 'pyi_hooks_contrib', 'pyi_hooks'}
        self.hidden_imports_list = [m for m in self.hidden_imports_list if m not in FILTER_MODULES]
        self.hidden_listbox.clear()
        for mod in self.hidden_imports_list:
            self.hidden_listbox.addItem(mod)
        self._update_hidden_count()
        self._packer_panel_initialized = False
        self._last_system_python = sys.executable
        if getattr(sys, 'frozen', False):
            self._last_system_python = self._find_system_python() or sys.executable
        self.packer_combo.setCurrentIndex(0)
        QTimer.singleShot(100, self._set_window_icon)              
        QTimer.singleShot(150, self._init_progress_bar)            
        QTimer.singleShot(200, self._enable_all_drag_drop)         
        QTimer.singleShot(350, self._check_current_packer_after_init)  
        QTimer.singleShot(550, self._init_packer_panel_visibility)     
        QTimer.singleShot(750, self._auto_detect_current_dir) 
        QTimer.singleShot(800, self._filter_python_list)
        self.monitor_thread = SystemMonitorThread()
        self.monitor_thread.status_updated.connect(self._on_system_status_updated)
        self.monitor_thread.start()

        def showEvent(self, event):
            super().showEvent(event)
            QTimer.singleShot(1000, self._background_prepare_environment)
        load_dep_map()

    def _filter_python_list(self):
        """过滤掉非 python 的 exe保持顺序，同步删除缓存"""
        if not getattr(sys, 'frozen', False):
            return
        removed = []
        for i in range(self.python_path.count() - 1, -1, -1):
            path = self.python_path.itemText(i)
            basename = os.path.basename(path).lower()
            if basename.endswith('.exe') and 'python' not in basename:
                removed.append(path)
                self.python_path.removeItem(i)
            elif getattr(sys, 'frozen', False):
                try:
                    if os.path.samefile(path, sys.executable):
                        removed.append(path)
                        self.python_path.removeItem(i)
                except:
                    if path.lower() == sys.executable.lower():
                        removed.append(path)
                        self.python_path.removeItem(i)
        if not removed:
            return
        try:
            cache = load_cache()
            python_list = cache.get('python_list', [])
            new_python_list = []
            for p in python_list:
                basename = os.path.basename(p).lower()
                is_self = False
                if getattr(sys, 'frozen', False):
                    try:
                        if os.path.samefile(p, sys.executable):
                            is_self = True
                    except:
                        if p.lower() == sys.executable.lower():
                            is_self = True
                if (basename.endswith('.exe') and 'python' not in basename) or is_self:
                    pass
                else:
                    new_python_list.append(p)
            cache['python_list'] = new_python_list
            save_cache(cache)
        except Exception as e:
           pass

    def _on_system_status_updated(self, cpu_percent, mem_percent, mem_used_gb, mem_total_gb, temp_str=""):
        try:
            # ===== CPU（三色） =====
            cpu_text = f"CPU: {cpu_percent:.0f}%"
            if hasattr(self, 'status_cpu'):
                self.status_cpu.setText(cpu_text)
                # 颜色判断
                if cpu_percent > 80:
                    cpu_color = "#F44336"
                elif cpu_percent > 60:
                    cpu_color = "#FF9800"
                else:
                    cpu_color = "#4CAF50"
                self.status_cpu.setStyleSheet(f"color: {cpu_color}; font-weight: bold;")
            # ===== 内存（三色） =====
            mem_text = f"内存: {mem_percent:.0f}%"
            if hasattr(self, 'status_memory'):
                self.status_memory.setText(mem_text)
                if mem_percent > 80:
                    mem_color = "#F44336"
                elif mem_percent > 60:
                    mem_color = "#FF9800"
                else:
                    mem_color = "#4CAF50"
                self.status_memory.setStyleSheet(f"color: {mem_color}; font-weight: bold;")
            # ===== 温度（三色） =====
            temp_value = None
            if temp_str and hasattr(self, 'status_temp'):
                import re
                match = re.search(r'(\d+\.?\d*)', temp_str)
                if match:
                    temp_value = float(match.group(1))
                    if temp_value > 80:
                        temp_color = "#F44336"
                        temp_emoji = "🔥"
                    elif temp_value > 65:
                        temp_color = "#FF9800"
                        temp_emoji = "🌡️"
                    else:
                        temp_color = "#4CAF50"
                        temp_emoji = "❄️"
                    self.status_temp.setStyleSheet(f"color: {temp_color}; font-weight: bold;")
                self.status_temp.setText(f"{temp_emoji}{temp_str}")
        except Exception as e:
            pass

    def _get_resource_color(self, percent):
        """根据使用率返回对应的颜色"""
        if percent < 50:
            return "#4CAF50"  # 绿色
        elif percent < 75:
            return "#FF9800"  # 橙色
        else:
            return "#F44336"  # 红色

    def _init_progress_bar(self):
        """初始化进度条样式 - 等待布局完成后刷新"""
        if hasattr(self, 'progress_bar'):
            if self.progress_bar.width() <= 0:
                QTimer.singleShot(50, self._init_progress_bar)
                return
            value = self.progress_bar.value()
            self.progress_bar.setValue(0 if value == 0 else value)
            self.progress_bar.setValue(value)
            self.progress_bar.update()

    def _lazy_init(self):
        """延迟初始化"""
        self._load_config()
        QApplication.processEvents()
        QTimer.singleShot(500, self._enable_all_drag_drop)
        QTimer.singleShot(1000, self._check_current_packer_after_init)
        QTimer.singleShot(2000, self._load_packer_versions_from_cache_only)
        QTimer.singleShot(10, self._load_remaining)
        QTimer.singleShot(300, self._init_packer_panel_visibility)

    def _replace_with_drag_drop(self):
        """将输入框替换为支持拖拽的版本"""
        if not hasattr(self, 'input_file'):
            return
        current_text = self.input_file.text()
        parent_layout = self.input_file.parentWidget().layout()
        if not parent_layout:
            return
        index = -1
        for i in range(parent_layout.count()):
            item = parent_layout.itemAt(i)
            if item and item.widget() == self.input_file:
                index = i
                break
        if index < 0:
            return
        # 创建新的 DragDropLineEdit
        new_input = DragDropLineEdit()
        new_input.setText(current_text)
        new_input.setPlaceholderText("可拖拽文件到此处...")
        parent_layout.replaceWidget(self.input_file, new_input)
        self.input_file.deleteLater()
        self.input_file = new_input
        self.safe_log("✅ 拖拽功能已启用")

    def _retry_detect_packer_version(self, display_name):
        """重试检测打包器版本"""
        python_exe = self.python_path.currentText()
        if python_exe and os.path.exists(python_exe):
            self._show_packer_version_from_cache(display_name, python_exe)
        else:
            self.status_packer.setText(f"📦 {display_name}: 检测中...")
            QTimer.singleShot(2000, lambda: self._retry_detect_packer_version(display_name))

    def _enable_all_drag_drop(self):
        """窗口显示后启用所有拖拽功能"""
        if hasattr(self, 'input_file') and hasattr(self.input_file, 'enable_drag_drop'):
            self.input_file.enable_drag_drop()
        else:
            if hasattr(self, 'input_file'):
                self.input_file.setAcceptDrops(True)
        if hasattr(self, 'log_text'):
            self.log_text.setAcceptDrops(True)
        if hasattr(self, 'adv_frame'):
            self.adv_frame.setAcceptDrops(True)
        if hasattr(self, 'data_listbox'):
            self.data_listbox.setAcceptDrops(True)

    def _load_remaining(self):
        """加载剩余内容"""
        QTimer.singleShot(100, self._auto_detect_current_dir)
        cache = load_cache()
        if 'python' not in cache:
            threading.Thread(target=self._async_find_python, daemon=True).start()
        if 'upx' not in cache:
            threading.Thread(target=self._async_find_upx, daemon=True).start()
        if 'compiler' not in cache:
            QTimer.singleShot(500, self._detect_compilers_async)
        QTimer.singleShot(800, self._preload_packer_versions)

    def _on_custom_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.progress_label.setText(text)
        QApplication.processEvents()

    def _garbage_collect(self):
        """定期回收内存"""
        import gc
        gc.collect()

    def _update_time(self):
        """更新时间显示"""
        if self.pack_start_time:
            elapsed = time.time() - self.pack_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            if elapsed > 600:  # 超过10分钟
                color = "#e74c3c"  # 红色
            elif elapsed > 300:  # 超过5分钟
                color = "#f39c12"  # 橙色
            else:
                color = "#2ecc71"  # 绿色
            self.time_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
            self.time_label.setText(f"⏰ {minutes:02d}:{seconds:02d}")

    def _load_packer_versions_from_cache_only(self):
        """只从缓存加载打包器版本，不触发检测"""
        if self._packer_cache_loaded:
            return
        try:
            cache = load_cache()
            packer_versions = cache.get('packer_versions', {})
            if packer_versions:
                for key, version in packer_versions.items():
                    if key not in self._packer_versions_cache:
                        self._packer_versions_cache[key] = version
                self._packer_cache_loaded = True
        except Exception as e:
            self.safe_log(f"⚠️ 加载打包器缓存失败: {e}")

    def _on_input_file_changed(self, text):
        """输入文件改变时自动更新输出名称（带项目级环境隔离缓存）"""
        if not text or not os.path.exists(text):
            return
        # 1. 停止旧线程
        if hasattr(self, '_analyze_thread') and self._analyze_thread is not None:
            if self._analyze_thread.isRunning():
                self._analyze_thread.quit()
                self._analyze_thread.wait(300)
        # 2. 立即更新基础UI
        text = os.path.normpath(text)
        fixed_path = self._auto_fix_filename_spaces(text)
        if fixed_path and fixed_path != text:
            self.input_file.blockSignals(True)
            self.input_file.setText(self._format_path(fixed_path))
            self.input_file.blockSignals(False)
            text = fixed_path
        base_name = os.path.splitext(os.path.basename(text))[0]
        if not base_name:
            return
        self.app_name.setText(base_name)
        if hasattr(self, 'version_info') and self.version_info:
            self.version_info["product_name"] = base_name
        script_dir = os.path.dirname(text)
        output_dir = os.path.join(script_dir, "dist")
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir.setText(self._format_path(output_dir))
        # 3. 先尝试加载项目缓存（按环境隔离）
        self.status_label.setText("📦 检查缓存...")
        QApplication.processEvents()
        cache = self._load_project_cache()
        if cache:
            # 缓存命中！直接恢复
            self._restore_from_project_cache(cache, text, base_name)
            return
        # 4. 缓存未命中，走正常分析流程
        self.hidden_imports_list.clear()
        self.hidden_listbox.clear()
        self.exclude_list.clear()
        self.exclude_listbox.clear()
        self.data_files_list.clear()
        self.data_listbox.clear()
        self._update_data_count()
        self._update_hidden_count()
        self._update_exclude_count()
        self.status_label.setText("🔍 分析依赖中...")
        self._pending_analyze_file = text
        self._pending_analyze_base = base_name
        self._analyze_thread = AnalyzeUsedThread(text)
        self._analyze_thread.finished.connect(self._on_analyze_used_finished)
        self._analyze_thread.error.connect(
            lambda msg: self.safe_log(f"⚠️ 分析依赖失败: {msg}")
        )
        self._analyze_thread.start()
        # 延迟依赖检查标记
        self._deps_check_pending = True

    def _restore_from_project_cache(self, cache, script_path, base_name):
        """从项目缓存恢复状态（环境隔离）"""
        self.status_label.setText("✅ 缓存命中")
        # 恢复隐藏导入
        cached_hidden = cache.get('hidden_imports', [])
        self.hidden_imports_list = cached_hidden.copy()
        self.hidden_listbox.clear()
        self.hidden_listbox.setUpdatesEnabled(False)
        try:
            for mod in cached_hidden:
                item = QListWidgetItem(mod)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.hidden_listbox.addItem(item)
        finally:
            self.hidden_listbox.setUpdatesEnabled(True)
        self._update_hidden_count()
        # 恢复排除列表
        cached_excludes = cache.get('exclude_list', [])
        self.exclude_list = cached_excludes.copy()
        self.manual_exclude_list = cache.get('manual_exclude_list', []).copy()
        self._update_exclude_count()
        self._update_exclude_listbox()
        # 恢复数据文件
        cached_data = cache.get('data_files', [])
        self.data_files_list = cached_data.copy()
        self.data_listbox.clear()
        for src, dst in cached_data:
            self.data_listbox.addItem(f"{os.path.basename(src)} -> {dst}")
        self._update_data_count()
        # 恢复分析结果
        self.analyzed_modules = cache.get('analyzed_modules', [])
        self.real_imports = cache.get('real_imports', [])
        self.extra_deps = cache.get('extra_deps', [])
        uses_tkinter = cache.get('uses_tkinter', False)
        # 恢复GUI插件设置
        if uses_tkinter and hasattr(self, 'nuitka_gui_plugin_combo'):
            if self.nuitka_gui_plugin_combo.currentText() == 'auto':
                self.nuitka_gui_plugin_combo.blockSignals(True)
                self.nuitka_gui_plugin_combo.setCurrentText('tk-inter')
                self.nuitka_gui_plugin_combo.blockSignals(False)
        # 恢复自动导入计数
        self._update_auto_import_count()
        # 其他UI更新
        self._auto_load_tool_icon(script_path, base_name)
        self._pending_analyze_file = script_path
        self._pending_analyze_base = base_name
        env_id = self._get_python_env_id(self.python_path.currentText() or sys.executable)
        self.safe_log(f"✅ 已从缓存恢复 [{env_id}]: {len(cached_hidden)} 个隐藏导入, {len(cached_excludes)} 个排除")
        self.status_label.setText("就绪")
        # 延迟检查依赖（后台）
        self._deps_check_pending = True

    def _lazy_check_deps(self):
        """延迟依赖检查，避免频繁切换文件时重复检查（后台执行）"""
        if not getattr(self, '_deps_check_pending', False):
            return
        self._deps_check_pending = False
        script = getattr(self, '_pending_analyze_file', '') or self.input_file.text()
        if not script or not os.path.exists(script):
            return
        # 只在后台做轻量级检查，不阻塞UI
        if not self.use_venv:
            # 非虚拟环境：只检查，不自动安装（避免阻塞）
            threading.Thread(target=self._check_deps_only, args=(script,), daemon=True).start()
        elif self.venv_mode.isChecked():
            venv_python = self._get_venv_python()
            if venv_python and os.path.exists(venv_python):
                # 虚拟环境也改为后台，且只在真正缺失时才提示
                threading.Thread(
                    target=self._check_venv_deps_only, 
                    args=(venv_python, script), 
                    daemon=True
                ).start()

    def _check_deps_only(self, script_path):
        """纯检查模式，不自动安装（避免阻塞打包）"""
        # 这里可以复用你原有的分析逻辑，但只做对比不调用pip install
        # 如果需要安装，在点击打包按钮时再执行
        pass

    def _check_venv_deps_only(self, venv_python, script_path):
        """虚拟环境纯检查模式"""
        # 同样只做检查，安装放到打包前
        pass

    def _on_analyze_used_finished(self, result, real_imports, extra_deps, uses_tkinter):
        """分析完成回调（保存项目级环境隔离缓存）"""
        script_path = getattr(self, '_pending_analyze_file', '') or self.input_file.text()
        base_name = getattr(self, '_pending_analyze_base', '') or self.app_name.text()
        if not script_path:
            return
        self.status_label.setText("就绪")
        self.analyzed_modules = result
        self.real_imports = real_imports
        self.extra_deps = extra_deps
        self._last_analyzed_file = script_path
        self._last_analyzed_time = time.time()
        # 自动设置 Nuitka 插件
        if uses_tkinter:
            if hasattr(self, 'nuitka_gui_plugin_combo'):
                if self.nuitka_gui_plugin_combo.currentText() != 'tk-inter':
                    self.nuitka_gui_plugin_combo.setCurrentText('tk-inter')
        # 批量添加到隐藏导入
        existing_lower = {mod.lower() for mod in self.hidden_imports_list}
        new_items = []
        for mod in result:
            if mod.lower() not in existing_lower:
                self.hidden_imports_list.append(mod)
                existing_lower.add(mod.lower())
                new_items.append(mod)
        if new_items:
            self.hidden_listbox.setUpdatesEnabled(False)
            try:
                for mod in new_items:
                    item = QListWidgetItem(mod)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.hidden_listbox.addItem(item)
            finally:
                self.hidden_listbox.setUpdatesEnabled(True)
        self._update_hidden_count()
        # 显示日志
        if real_imports:
            imports_display = ', '.join(real_imports[:10])
            if len(real_imports) > 10:
                imports_display += f' ... 等 {len(real_imports)} 个'
        if extra_deps:
            extra_display = ', '.join(sorted(extra_deps)[:10])
            if len(extra_deps) > 10:
                extra_display += f' ... 等 {len(extra_deps)} 个'
            self.safe_log(f"📦 附属依赖 {len(extra_deps)} 个: {extra_display}")
        # 构建排除列表
        self._build_exclude_list_from_analysis()
        self._update_auto_import_count()
        # 后续操作
        self._auto_load_tool_icon(script_path, base_name)
        QTimer.singleShot(10, self._detect_gui_from_hidden)
        QTimer.singleShot(50, self._refresh_nuitka_gui_display)
        # ===== 关键：保存项目级环境隔离缓存 =====
        self._save_project_cache((result, real_imports, extra_deps, uses_tkinter))
        self.safe_log("✅ 依赖分析完成")

    def _refresh_nuitka_gui_display(self):
        """强制刷新Nuitka GUI插件显示（用于重新选择文件或切换打包器时）"""
        if not hasattr(self, 'nuitka_gui_plugin_combo') or self.nuitka_gui_plugin_combo is None:
            return
        current_text = self.nuitka_gui_plugin_combo.currentText()
        if current_text is None:
            return
        self._update_gui_display(current_text)

    def _auto_detect_and_set_gui_plugin(self, script_path):
        """异步检测并设置GUI插件 - 直接使用 hidden_imports_list"""
        if not hasattr(self, 'nuitka_gui_plugin_combo') or self.nuitka_gui_plugin_combo is None:
            return
        if self.nuitka_gui_plugin_combo.currentText() != 'auto':
            return

        def detect():
            try:
                detected = None
                # ===== 直接使用 hidden_imports_list =====
                if hasattr(self, 'hidden_imports_list') and self.hidden_imports_list:
                    # ===== 统一转为小写比较 =====
                    imports_lower = {m.lower() for m in self.hidden_imports_list}
                    if 'pyqt6' in imports_lower:
                        detected = 'pyqt6'
                    elif 'pyqt5' in imports_lower:
                        detected = 'pyqt5'
                    elif 'pyside6' in imports_lower:
                        detected = 'pyside6'
                    elif 'pyside2' in imports_lower:
                        detected = 'pyside2'
                    elif 'tkinter' in imports_lower or 'tk' in imports_lower:
                        detected = 'tk-inter'
                    elif 'wx' in imports_lower:
                        detected = 'wxpython'
                    elif 'kivy' in imports_lower:
                        detected = 'kivy'
                if detected is None and script_path and os.path.exists(script_path):
                    try:
                        imports = self._analyze_used(script_path, auto_add=False)
                        # ===== 统一转为小写比较 =====
                        imports_lower = {m.lower() for m in imports}
                        if 'pyqt6' in imports_lower:
                            detected = 'pyqt6'
                        elif 'pyqt5' in imports_lower:
                            detected = 'pyqt5'
                        elif 'pyside6' in imports_lower:
                            detected = 'pyside6'
                        elif 'pyside2' in imports_lower:
                            detected = 'pyside2'
                        elif 'tkinter' in imports_lower or 'tk' in imports_lower:
                            detected = 'tk-inter'
                        elif 'wx' in imports_lower:
                            detected = 'wxpython'
                        elif 'kivy' in imports_lower:
                            detected = 'kivy'
                    except Exception as e:
                        self.safe_log(f"⚠️ 重新分析依赖失败: {e}")
                # ===== 更新 UI =====
                if detected:
                    def update_ui():
                        if hasattr(self, 'nuitka_gui_plugin_combo') and self.nuitka_gui_plugin_combo is not None:
                            if self.nuitka_gui_plugin_combo.currentText() == 'auto':
                                self.nuitka_gui_plugin_combo.blockSignals(True)
                                self.nuitka_gui_plugin_combo.setCurrentText(detected)
                                self.nuitka_gui_plugin_combo.blockSignals(False)
                                if hasattr(self, 'gui_display_label') and self.gui_display_label is not None:
                                    self.gui_display_label.setText(f"✅ {detected}")
                                    self.gui_display_label.setStyleSheet("color: green; font-size: 9px;")
                                if hasattr(self, 'nuitka_gui_plugin_combo'):
                                    self.nuitka_gui_plugin_combo.currentTextChanged.emit(detected)
                                self.safe_log(f"🔄 自动切换到GUI插件: {detected}")
                    QTimer.singleShot(0, update_ui)
                else:
                    def update_ui():
                        if hasattr(self, 'gui_display_label') and self.gui_display_label is not None:
                            if self.nuitka_gui_plugin_combo.currentText() == 'auto':
                                self.gui_display_label.setText("✗ 未检测到")
                                self.gui_display_label.setStyleSheet("color: orange; font-size: 9px;")
                    QTimer.singleShot(0, update_ui)
            except Exception as e:
                pass
        threading.Thread(target=detect, daemon=True).start()

    def _init_ui_attributes(self):
        """初始化所有UI控件属性"""
        self.input_file = None
        self.output_dir = None
        self.app_name = None
        self.icon_label = None
        self.python_path = None
        self.python_version = None
        self.platform_combo = None
        self.packer_combo = None
        self.single_mode = None
        self.venv_mode = None
        self.debug_mode = None
        self.uv_mode = None
        self.compress_combo = None
        self.upx_path = None
        self.packer_box = None
        self.exclude_btn = None
        self.exclude_count_label = None
        self.exclude_frame = None
        self.exclude_input = None
        self.exclude_listbox = None
        self.exclude_num_label = None
        self.auto_import_btn = None
        self.auto_import_count_label = None
        self.adv_btn = None
        self.adv_count_label = None
        self.adv_frame = None
        self.hidden_input = None
        self.hidden_listbox = None
        self.hidden_num_label = None
        self.rec_label = None
        self.data_src_input = None
        self.data_tgt_input = None
        self.data_listbox = None
        self.progress_bar = None
        self.progress_label = None
        self.time_label = None
        self.log_text = None
        self.status_label = None
        self.status_python = None
        self.status_packer = None
        self.status_compiler = None
        self.music_frame = None
        self.music_toggle_btn = None
        self.music_label = None
        self.help_about_btn = None
        self.status_bar = None
        # Nuitka 控件
        self.nuitka_jobs_combo = None
        self.nuitka_backend_combo = None
        self.nuitka_gui_plugin_combo = None
        self.nuitka_lto_combo = None
        self.nuitka_compat_cb = None
        self.nuitka_strip_cb = None
        self.nuitka_exp_cb = None
        self.nuitka_lowmem_cb = None
        self.compiler_label = None
        self.gui_detect_label = None
        # PyInstaller 控件
        self.pyi_strip_cb = None
        self.use_response_file_cb = None
        self.pyi_log_level_combo = None
        self.pyi_collect_input = None
        self.pyi_metadata_input = None
        self.extra_args_input = None
        self._packer_version_cache = {}  
        self._pending_spec_file = None   

    def _init_ui(self):
        """创建UI骨架 """
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        # 输入文件行
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("输入文件:"))
        self.input_file = DragDropLineEdit()
        # ===== 阻塞信号，避免创建时触发 textChanged =====
        self.input_file.blockSignals(True)
        self.input_file.setPlaceholderText("可拖拽文件到此处...")
        self.input_file.blockSignals(False)
        r1.addWidget(self.input_file, stretch=1)
        btn_select = EmojiButton("📥 选择")
        btn_select.clicked.connect(self._select_input)
        r1.addWidget(btn_select)
        main_layout.addLayout(r1)
        # 输出目录行
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("输出目录:"))
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("正在初始化...")
        r2.addWidget(self.output_dir, stretch=1)
        btn_output = EmojiButton("⚙️ 设置")
        btn_output.clicked.connect(self._select_output)
        r2.addWidget(btn_output)
        main_layout.addLayout(r2)
        # 程序名称行
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("程序名称:"))
        self.app_name = QLineEdit()
        self.app_name.setPlaceholderText("自动识别...")
        r3.addWidget(self.app_name, stretch=1)
        self.icon_label = QLabel("")
        self.icon_label.setStyleSheet("color: gray; font-size: 9px;")
        r3.addWidget(self.icon_label)
        btn_clear_icon = EmojiButton("✂️ 清除")
        btn_clear_icon.clicked.connect(self._clear_icon)
        r3.addWidget(btn_clear_icon)
        btn_make_icon = EmojiButton("🎨 制图")
        btn_make_icon.clicked.connect(self._open_icon_maker)
        r3.addWidget(btn_make_icon)
        btn_select_icon = EmojiButton("🖼️ 选图")
        btn_select_icon.clicked.connect(self._select_icon)
        r3.addWidget(btn_select_icon)
        main_layout.addLayout(r3)
        # Python路径行
        r4 = QHBoxLayout()
        r4.addWidget(QLabel("Python  :"))
        self.python_path = QComboBox()
        self.python_path.setEditable(True)
        self.python_path.setMinimumWidth(300)
        # ===== 连接信号：Python路径变化时更新缓存和检测打包器版本 =====
        self.python_path.currentTextChanged.connect(self._on_python_path_changed)
        r4.addWidget(self.python_path, stretch=1)
        btn_refresh_py = EmojiButton("🔄")
        btn_refresh_py.clicked.connect(self._refresh_python_list)
        r4.addWidget(btn_refresh_py)
        self.python_version = QLabel("")
        self.python_version.setStyleSheet("color: blue; font-family: Consolas;")
        r4.addWidget(self.python_version)
        btn_browse_py = EmojiButton("🔍 浏览")
        btn_browse_py.clicked.connect(self._select_python)
        r4.addWidget(btn_browse_py)
        btn_test_py = EmojiButton("🧪 测试")
        btn_test_py.clicked.connect(self._test_python)
        r4.addWidget(btn_test_py)
        btn_clear_py = EmojiButton("🗑️ 清空")
        btn_clear_py.clicked.connect(self._clear_python)
        r4.addWidget(btn_clear_py)
        main_layout.addLayout(r4)
        # 拖拽高亮层
        self.drop_highlight = QFrame(central)
        self.drop_highlight.setStyleSheet("""
            QFrame {
                background: rgba(0, 184, 148, 0.2);
                border: 2px dashed #00b894;
                border-radius: 8px;
            }
        """)
        self.drop_highlight.setVisible(False)
        self.drop_highlight.raise_()
        central.setAcceptDrops(True)
        central.dragEnterEvent = self._central_drag_enter
        central.dragLeaveEvent = self._central_drag_leave
        central.dropEvent = self._central_drop
        # 第5行：打包选项
        r5 = QHBoxLayout()
        r5.addWidget(QLabel("平台:"))
        self.platform_combo = QComboBox()
        self.platform_combo.setStyleSheet("QComboBox { width: 50px; }")
        self.platform_combo.addItems(["current", "Windows", "Linux", "macOS"])
        r5.addWidget(self.platform_combo)
        r5.addWidget(QLabel("打包:"))
        self.packer_combo = QComboBox()
        self.packer_combo.setStyleSheet("QComboBox { width: 90px; }")
        self.packer_combo.addItems([
            "PyInstaller-spec","PyInstaller-cmd", "Nuitka", "PyApp",
            "Py2exe", "Cx_Freeze", "Pynsist", "PyOxidizer", "Py2app"
        ])
        self.packer_combo.currentTextChanged.connect(self._on_packer_changed)
        r5.addWidget(self.packer_combo)
        self.single_mode = QCheckBox("单模")
        self.single_mode.setChecked(True)
        r5.addWidget(self.single_mode)
        self.venv_mode = QCheckBox("虚拟")
        self.venv_mode.stateChanged.connect(self._on_venv_switch)
        r5.addWidget(self.venv_mode)
        self.debug_mode = QCheckBox("调试")
        r5.addWidget(self.debug_mode)
        self.uv_mode = QCheckBox("uv加速")
        self.uv_mode.stateChanged.connect(self._on_uv_switch)
        r5.addWidget(self.uv_mode)
        # ===== 新增：自动排除复选框 =====
        self.auto_exclude_cb = QCheckBox("排除")
        self.auto_exclude_cb.setChecked(True)  # 默认开启
        self.auto_exclude_cb.setToolTip("勾选后自动排除不需要的模块，减小打包体积")
        self.auto_exclude_cb.stateChanged.connect(self._on_auto_exclude_toggled)
        r5.addWidget(self.auto_exclude_cb)
        r5.addWidget(QLabel("压缩:"))
        self.compress_combo = QComboBox()
        self.compress_combo.addItems(["默认", "不压", "最快", "最好", "极致"])
        self.compress_combo.setCurrentText("默认")
        r5.addWidget(self.compress_combo)
        r5.addWidget(QLabel("UPX:"))
        self.upx_path = QLineEdit()
        self.upx_path.setPlaceholderText("UPX路径")
        self.upx_path.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        r5.addWidget(self.upx_path)
        btn_upx = EmojiButton("📌 指定")
        btn_upx.clicked.connect(self._select_upx)
        r5.addWidget(btn_upx)
        main_layout.addLayout(r5)
        # 打包器面板（延迟创建，只占位）
        self._setup_packer_panel(main_layout)
        # 功能按钮栏
        r6 = QHBoxLayout()
        self.exclude_btn = EmojiButton("▶ 排除")
        self.exclude_btn.clicked.connect(self._toggle_exclude)
        r6.addWidget(self.exclude_btn)
        self.exclude_count_label = QLabel("(0)")
        r6.addWidget(self.exclude_count_label)
        self.restore_exclude_btn = EmojiButton("↩️ 恢复")
        self.restore_exclude_btn.clicked.connect(self._show_excluded_packages_dialog)
        self.restore_exclude_btn.setToolTip("从排除列表中恢复需要的包")
        r6.addWidget(self.restore_exclude_btn)
        self.auto_import_btn = EmojiButton("⚡ 自导")
        self.auto_import_btn.clicked.connect(self._auto_import_modules)
        r6.addWidget(self.auto_import_btn)
        self.auto_import_count_label = QLabel("")
        r6.addWidget(self.auto_import_count_label)
        self.adv_btn = EmojiButton("▶ 数据")
        self.adv_btn.clicked.connect(self._toggle_advanced)
        r6.addWidget(self.adv_btn)
        self.adv_count_label = QLabel("(0)")
        r6.addWidget(self.adv_count_label)
        r6.addWidget(QLabel("进度:"))
        self.progress_style_combo = QComboBox()
        self.progress_style_combo.addItems(["🌈 七彩虹", "😊 点阵图", "🌿 薄荷绿", "🌸 樱花粉", "🌌 星际紫", "🌊 深海蓝"])
        self.progress_style_combo.currentTextChanged.connect(self._on_progress_style_changed)
        r6.addWidget(self.progress_style_combo)
        r6.addStretch()
        btn_kill_multi = EmojiButton("🔫 结束多开")
        btn_kill_multi.clicked.connect(self._kill_multi_instances)
        r6.addWidget(btn_kill_multi)
        self._add_tooltip(btn_kill_multi, "结束多开的程序实例")
        btn_estimate = EmojiButton("🧠 预估大小")
        btn_estimate.clicked.connect(self._estimate_size)
        r6.addWidget(btn_estimate)
        btn_inject = EmojiButton("💉 注入代码")
        btn_inject.clicked.connect(self._open_inject_selector)
        r6.addWidget(btn_inject)
        btn_syntax = EmojiButton("✅ 语法检查")
        btn_syntax.clicked.connect(self._check_syntax)
        r6.addWidget(btn_syntax)
        btn_compare = EmojiButton("📊 对比代码")
        btn_compare.clicked.connect(self._compare_files)
        r6.addWidget(btn_compare)
        self._add_tooltip(btn_compare, "对比两个Python文件的差异")
        btn_version = EmojiButton("ℹ️ 版本更新")
        btn_version.clicked.connect(self._open_version_dialog)
        r6.addWidget(btn_version)
        main_layout.addLayout(r6)
        # 排除选项折叠面板
        self.exclude_frame = QFrame()
        self.exclude_frame.setVisible(False)
        self.exclude_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        #self.exclude_frame.setMaximumHeight(200)
        el = QVBoxLayout(self.exclude_frame)
        er = QHBoxLayout()
        er.addWidget(QLabel("排除模块:"))
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("输入模块名，逗号分隔")
        er.addWidget(self.exclude_input, stretch=1)
        for text, cmd in [("🔄 清空", self._clear_excludes), ("➖ 移除", self._remove_exclude),
                          ("➕ 添加", self._add_exclude), ("🔍 智选", self._open_exclude),
                          ("⚡ 推荐", self._add_recommended)]:
            btn = EmojiButton(text)
            btn.clicked.connect(cmd)
            er.addWidget(btn)
        self.exclude_num_label = QLabel("(0)")
        er.addWidget(self.exclude_num_label)
        btn_del_selected = EmojiButton("🗑️ 删选")
        btn_del_selected.clicked.connect(self._remove_selected_excludes)
        er.addWidget(btn_del_selected)
        el.addLayout(er)
        # 排除列表（带复选框）
        self.exclude_listbox = QListWidget()
        self.exclude_listbox.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)  # 禁止选中行
        self.exclude_listbox.setStyleSheet("""
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #e8f0fe;
            }
        """)
        self.exclude_listbox.setMaximumHeight(200)
        el.addWidget(self.exclude_listbox)
        main_layout.addWidget(self.exclude_frame)
        # 依赖数据折叠面板
        self.adv_frame = QFrame()
        self.adv_frame.setVisible(False)
        self.adv_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.adv_frame.setAcceptDrops(True)
        self.adv_frame.dragEnterEvent = self._data_panel_drag_enter
        self.adv_frame.dropEvent = self._data_panel_drop
        avl = QVBoxLayout(self.adv_frame)
        adv_splitter = QSplitter(Qt.Orientation.Horizontal)
        # 左侧隐藏导入
        hw = QWidget()
        hl = QVBoxLayout(hw)
        hh = QHBoxLayout()
        hh.addWidget(QLabel("📦 隐藏导入"))
        self.hidden_num_label = QLabel("(0)")
        hh.addWidget(self.hidden_num_label)
        hh.addStretch()
        hl.addLayout(hh)
        hi = QHBoxLayout()
        self.hidden_input = QLineEdit()
        self.hidden_input.setPlaceholderText("输入模块名")
        hi.addWidget(self.hidden_input, stretch=1)
        btn_add_hidden = EmojiButton("➕ 添加")
        btn_add_hidden.clicked.connect(self._add_hidden)
        hi.addWidget(btn_add_hidden)
        hl.addLayout(hi)
        hb = QHBoxLayout()
        for text, cmd in [("🔬 分析", self._analyze_deps), ("📎 推荐", self._add_recommended_hidden),
                          ("📦 安装", self._auto_install), ("📝 导出", self._export_req),
                          ("📂 导入", self._import_req)]:
            btn = EmojiButton(text)
            btn.clicked.connect(cmd)
            hb.addWidget(btn)
        self.rec_label = QLabel("")
        hb.addWidget(self.rec_label)
        hb.addStretch()
        hl.addLayout(hb)
        self.hidden_listbox = QListWidget()
        # ===== 启用复选框模式，禁止选中行 =====
        self.hidden_listbox.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.hidden_listbox.setStyleSheet("""
            QListWidget::item {
                #padding: 4px 8px;
                background-color: #0078d7;
                color: white;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.hidden_listbox.setMaximumHeight(100)
        hl.addWidget(self.hidden_listbox)
        hbot = QHBoxLayout()
        for text, cmd in [("🗑 删除", self._remove_hidden), ("🔁 清空", self._clear_hidden),
                          ("💾 保存", self._save_config), ("🐍 虚拟", self._manage_venv),
                          ("🌐 autoexe", self._launch_auto)]:
            btn = EmojiButton(text)
            btn.clicked.connect(cmd)
            hbot.addWidget(btn)
        hbot.addStretch()
        hl.addLayout(hbot)
        adv_splitter.addWidget(hw)
        # 右侧数据文件
        dw = QWidget()
        dw.setAcceptDrops(True)
        dw.dragEnterEvent = self._data_panel_drag_enter
        dw.dropEvent = self._data_panel_drop
        dl = QVBoxLayout(dw)
        dl.addWidget(QLabel("📁 数据文件"))
        ds = QHBoxLayout()
        ds.addWidget(QLabel("源径:"))
        self.data_src_input = QLineEdit()
        ds.addWidget(self.data_src_input, stretch=1)
        btn_browse_data = EmojiButton("🔍 浏览")
        btn_browse_data.clicked.connect(self._select_data_src)
        ds.addWidget(btn_browse_data)
        dl.addLayout(ds)
        dt = QHBoxLayout()
        dt.addWidget(QLabel("目标:"))
        self.data_tgt_input = QLineEdit()
        dt.addWidget(self.data_tgt_input, stretch=1)
        btn_add_data = EmojiButton("➕ 添加")
        btn_add_data.clicked.connect(self._add_data)
        dt.addWidget(btn_add_data)
        dl.addLayout(dt)
        self.data_listbox = QListWidget()
        self.data_listbox.setStyleSheet("""
            QListWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e67e22;
            }
        """)
        self.data_listbox.setMaximumHeight(80)
        self.data_listbox.setAcceptDrops(True)
        self.data_listbox.setDragEnabled(False)
        self.data_listbox.dragEnterEvent = self._data_listbox_drag_enter
        self.data_listbox.dragMoveEvent = self._data_listbox_drag_move
        self.data_listbox.dropEvent = self._data_listbox_drop
        dl.addWidget(self.data_listbox)
        dbot = QHBoxLayout()
        for text, cmd in [("❌删除", self._remove_data), ("🔄清空", self._clear_data),
                          ("📁打开", self._open_proj_dir), ("📁扫描", self._scan_data)]:
            btn = EmojiButton(text)
            btn.clicked.connect(cmd)
            dbot.addWidget(btn)
        btn_run_py = EmojiButton("▶智选")
        btn_run_py.clicked.connect(self._run_selected_data_py)
        dbot.addWidget(btn_run_py)
        btn_exclude_pack = EmojiButton("🚫排除")
        btn_exclude_pack.clicked.connect(self._toggle_data_py_exclude)
        dbot.addWidget(btn_exclude_pack)
        self.external_tool_cb = QCheckBox("传参")
        self.external_tool_cb.setChecked(False)
        self.external_tool_cb.setToolTip("勾选后，运行数据文件中的py时将弹出参数选择窗口")
        dbot.addWidget(self.external_tool_cb)
        # ===== 阈值设置 =====
        threshold_widget = QWidget()
        threshold_layout = QHBoxLayout(threshold_widget)
        threshold_layout.setContentsMargins(0, 0, 0, 0)
        threshold_layout.setSpacing(4)
        # 已安装包数量（只读）
        self.venv_pkg_count_label = QLabel("0")
        self.venv_pkg_count_label.setStyleSheet("color: #2196F3; font-weight: bold; min-width: 30px;")
        threshold_layout.addWidget(QLabel("包:"))
        threshold_layout.addWidget(self.venv_pkg_count_label)
        threshold_layout.addWidget(QLabel("/"))
        # 阈值输入框（可编辑，无按钮）
        self.clean_threshold_spin = QSpinBox()
        self.clean_threshold_spin.setRange(10, 500)
        self.clean_threshold_spin.setValue(100)
        self.clean_threshold_spin.setToolTip("虚拟环境包数量超过此值时会自动清理")
        self.clean_threshold_spin.setMaximumWidth(60)
        self.clean_threshold_spin.setKeyboardTracking(True)
        self.clean_threshold_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        threshold_layout.addWidget(self.clean_threshold_spin)
        # 保存按钮
        btn_save_threshold = EmojiButton("💾")
        btn_save_threshold.setFixedSize(28, 28)
        btn_save_threshold.setToolTip("保存阈值")
        btn_save_threshold.clicked.connect(self._save_clean_threshold)
        threshold_layout.addWidget(btn_save_threshold)
        dbot.addWidget(threshold_widget)
        dbot.addStretch()
        dl.addLayout(dbot)
        dl.addWidget(QLabel("💡 配置文件放项目下，点扫描或拖拽添加"))
        adv_splitter.addWidget(dw)
        adv_splitter.setSizes([500, 500])
        avl.addWidget(adv_splitter)
        main_layout.addWidget(self.adv_frame)
        # 底部操作栏
        bb = QHBoxLayout()
        self.progress_container = QWidget(self)
        self.progress_container.setVisible(False)
        lb = QHBoxLayout(self.progress_container)
        lb.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = self._create_progress_bar_by_theme()
        self.progress_bar.setParent(self.progress_container)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        lb.addWidget(self.progress_bar, stretch=2)
        self.progress_label = QLabel("", self.progress_container)
        lb.addWidget(self.progress_label)
        self.time_label = QLabel("⏰ 00:00", self.progress_container)
        self.time_label.setStyleSheet("font-weight: bold; color: #2ecc71; font-size: 12px;")
        lb.addWidget(self.time_label)
        bb.addWidget(self.progress_container, stretch=2)
        self.placeholder_widget = QWidget(self)
        self.placeholder_widget.setVisible(True)
        self.placeholder_widget.setFixedHeight(30)
        self.placeholder_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        bb.addWidget(self.placeholder_widget, stretch=2)
        rb = QHBoxLayout()
        self.btn_build = EmojiButton("▶ 开始打包")
        self.btn_build.clicked.connect(self._toggle_build)
        rb.addWidget(self.btn_build)
        for text, cmd in [("📂 编译目录", self._open_output), ("📋 导出日志", self._export_log),
                          ("🧹 清空日志", self._clear_log), ("🔄 恢复默认", self._reset)]:
            btn = EmojiButton(text)
            btn.clicked.connect(cmd)
            rb.addWidget(btn)
        self.theme_btn = EmojiButton("🎨 主题切换")
        self.theme_btn.clicked.connect(self._next_theme)
        rb.addWidget(self.theme_btn)
        bb.addLayout(rb)
        main_layout.addLayout(bb)
        # 日志区域
        log_group = QGroupBox("📋 打包日志")
        log_group.setStyleSheet("""
            QGroupBox {
                font-size: 10px;
                font-weight: bold;
                padding-top: 2px;
                margin-top: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 4px;
                padding: 0 2px;
            }
        """)
        log_group_layout = QVBoxLayout(log_group)
        log_group_layout.setContentsMargins(2, 0, 2, 2)
        log_group_layout.setSpacing(2)
        log_tip = QLabel("💡 拖拽文件到日志区域添加 | 🎵 点击状态栏按钮展开/收起播放器")
        log_tip.setStyleSheet("color: gray; font-size: 8px; padding: 0px;")
        log_tip.setMaximumHeight(14)
        log_tip.setWordWrap(False)
        log_group_layout.addWidget(log_tip)
        self.log_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.log_splitter.setChildrenCollapsible(False)
        self.log_text = LogTextEdit()
        self.log_text.files_dropped.connect(self._on_log_drop)
        self.log_splitter.addWidget(self.log_text)
        self.log_text.setAcceptDrops(True)
        self.player_container = QFrame()
        self.player_container.setVisible(False)
        self.player_container.setFrameStyle(QFrame.Shape.NoFrame)
        self.player_container.setMinimumWidth(180)
        self.log_splitter.addWidget(self.player_container)
        self.log_splitter.setSizes([10000, 0])
        log_group_layout.addWidget(self.log_splitter)
        main_layout.addWidget(log_group, stretch=3)
        # 底部状态栏
        sw = QWidget()
        sl = QHBoxLayout(sw)
        sl.setContentsMargins(4, 2, 4, 2)
        self.status_label = QLabel("就绪")
        sl.addWidget(self.status_label)
        sl.addStretch()
        self.status_progress = QProgressBar()
        self.status_progress.setMinimumHeight(14)
        self.status_progress.setVisible(False)
        self.status_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #e0e0e0;
                text-align: center;
                color: white;
                font-size: 6px;
            }
            QProgressBar::chunk {
                border-radius: 6px;
            }
        """)
        sl.addWidget(self.status_progress, stretch=1)
        self.status_pct = QLabel("")
        self.status_pct.setFixedWidth(40)
        self.status_pct.setVisible(False)
        sl.addWidget(self.status_pct)
        sl.addWidget(QLabel(" | "))
        self.status_cpu = QLabel("CPU: 0%")
        self.status_cpu.setFixedWidth(80)
        self.status_cpu.setStyleSheet("font-weight: bold;")
        sl.addWidget(self.status_cpu)
        self.status_memory = QLabel("内存: 0%")
        self.status_memory.setFixedWidth(80)
        self.status_memory.setStyleSheet("font-weight: bold;")
        sl.addWidget(self.status_memory)
        self.status_temp = QLabel("")
        self.status_temp.setFixedWidth(70)
        sl.addWidget(self.status_temp)
        sl.addWidget(QLabel(" | "))
        self.status_python = QLabel("🐍 Python: 未检测")
        sl.addWidget(self.status_python)
        self.status_packer = QLabel("📦 打包器: 未检测")
        sl.addWidget(self.status_packer)
        self.status_compiler = QLabel("")
        sl.addWidget(self.status_compiler)
        self.music_frame = QFrame()
        self.music_frame.setVisible(False)
        ml = QHBoxLayout(self.music_frame)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(2)
        btn_choose = EmojiButton("📁")
        btn_choose.clicked.connect(self._music_choose_folder)
        ml.addWidget(btn_choose)
        btn_prev = EmojiButton("⏮")
        btn_prev.clicked.connect(self._music_prev)
        ml.addWidget(btn_prev)
        self.music_play_btn = EmojiButton("▶")
        self.music_play_btn.clicked.connect(self._music_play_pause)
        ml.addWidget(self.music_play_btn)
        btn_stop = EmojiButton("⏹")
        btn_stop.clicked.connect(self._music_stop)
        ml.addWidget(btn_stop)
        btn_next = EmojiButton("⏭")
        btn_next.clicked.connect(self._music_next)
        ml.addWidget(btn_next)
        self.music_label = QLabel("")
        self.music_label.setMaximumWidth(100)
        ml.addWidget(self.music_label)
        sl.addWidget(self.music_frame)
        self.music_toggle_btn = EmojiButton("🎵🎬")
        self.music_toggle_btn.setCheckable(True)
        self.music_toggle_btn.setChecked(False)
        self.music_toggle_btn.setToolTip("音视频播放器")
        self.music_toggle_btn.clicked.connect(self._toggle_music_panel)
        sl.addWidget(self.music_toggle_btn)
        self.help_about_btn = EmojiButton("❓")
        self.help_about_btn.clicked.connect(self._toggle_help_about)
        sl.addWidget(self.help_about_btn)
        self._add_tooltip(self.help_about_btn, "关于/帮助")
        self.debug_exe_btn = EmojiButton("🩺")
        self.debug_exe_btn.clicked.connect(self._debug_current_exe)
        sl.addWidget(self.debug_exe_btn)
        self._add_tooltip(self.debug_exe_btn, "调试EXE文件")
        main_layout.addWidget(sw)
        # 为每个按钮添加提示
        self._add_tooltip(self.btn_build, "开始/停止打包")
        self._add_tooltip(btn_select, "选择Python脚本文件")
        self._add_tooltip(btn_output, "选择输出目录")
        self._add_tooltip(btn_clear_icon, "清除当前图标")
        self._add_tooltip(btn_make_icon, "打开图标制作工具")
        self._add_tooltip(btn_select_icon, "选择图标文件")
        self._add_tooltip(btn_refresh_py, "刷新Python列表")
        self._add_tooltip(btn_browse_py, "浏览选择Python解释器")
        self._add_tooltip(btn_test_py, "测试Python解释器")
        self._add_tooltip(btn_clear_py, "清除Python路径")
        self._add_tooltip(btn_upx, "选择UPX可执行文件")
        self._add_tooltip(btn_estimate, "预估打包后文件大小")
        self._add_tooltip(btn_inject, "注入防多开等代码")
        self._add_tooltip(btn_syntax, "检查Python语法错误，支持简单修护")
        self._add_tooltip(btn_version, "设置exe版本信息")
        self._add_tooltip(self.exclude_btn, "设置需要排除的模块")
        self._add_tooltip(self.auto_import_btn, "自动分析并导入依赖模块")
        self._add_tooltip(self.adv_btn, "管理隐藏导入和数据文件")
        self._add_tooltip(self.theme_btn, "切换界面主题")

    def _add_exclude_item(self, mod):
        """添加排除项（带复选框）"""
        item = QListWidgetItem(mod)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Unchecked)
        item.setData(Qt.ItemDataRole.UserRole, mod)
        self.exclude_listbox.addItem(item)

    def _save_clean_threshold(self):
        """保存清理阈值到缓存"""
        threshold = self.clean_threshold_spin.value()
        cache = load_cache()
        cache['clean_threshold'] = threshold
        save_cache(cache)
        self.safe_log(f"✅ 清理阈值已保存: {threshold}")

    def _debug_current_exe(self):
        """调试当前生成的EXE """
        try:
            exe_path = self._find_exe()
            if not exe_path:
                self.safe_log("❌ 未找到EXE文件")
                return
            if not os.path.exists(exe_path):
                self.safe_log(f"❌ 文件不存在: {exe_path}")
                return
            self.log_text.clear()
            self.safe_log("=" * 60)
            self.safe_log(f"🔍 调试EXE: {os.path.basename(exe_path)}")
            self.safe_log(f"📁 路径: {exe_path}")
            self.safe_log("=" * 60)
            size = os.path.getsize(exe_path)
            size_mb = size / (1024 * 1024)
            self.safe_log(f"📦 文件大小: {size_mb:.2f} MB")
            self.safe_log("")
            self.safe_log("🚀 正在启动EXE...")
            if sys.platform == 'win32':
                os.startfile(exe_path)
                self.safe_log("✅ EXE已启动 (os.startfile)")
            else:
                import subprocess
                subprocess.Popen(
                    [exe_path],
                    cwd=os.path.dirname(exe_path),
                    start_new_session=True
                )
                self.safe_log("✅ EXE已启动")
            self.safe_log("=" * 60)
        except Exception as e:
            self.safe_log(f"❌ 启动失败: {e}")

    def _find_exe(self):
        """查找当前项目的EXE文件"""
        script = self.input_file.text()
        if script and os.path.exists(script):
            project_name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
            script_dir = os.path.dirname(script)
            exe_path = os.path.join(script_dir, 'dist', project_name, f'{project_name}.exe')
            if os.path.exists(exe_path):
                return exe_path
            else:
                self.safe_log(f"⚠️ 未找到EXE: {exe_path}")
        exe_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要调试的EXE文件",
            self.output_dir.text() if self.output_dir.text() else "",
            "可执行文件 (*.exe);;所有文件 (*.*)"
        )
        return exe_path

    def _show_excluded_packages_dialog(self):
        """显示所有被排除的包（保留原始名称）"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            QMessageBox.warning(self, "提示", "请先选择Python脚本")
            return
        if not self.analyzed_modules:
            self._analyze_used(script, auto_add=False)
        self._build_exclude_list_from_analysis()
        # 注意：self.exclude_list 现在保留原始名称
        exclude_list = set(self.exclude_list)
        if not exclude_list:
            show_msg(self, "提示", "当前没有排除任何包", 1)
            return
        exclude_list = {p for p in exclude_list if p.lower() not in NEVER_PACK}
        if not exclude_list:
            show_msg(self, "提示", "没有发现需要恢复的包", 1)
            return
        # 分类：代码中用到的 和 没用到的（忽略大小写比较）
        used_packages_lower = {p.lower() for p in self.analyzed_modules}
        used_excluded = set()
        not_used_excluded = set()
        for pkg in exclude_list:
            pkg_lower = pkg.lower()
            if pkg_lower in used_packages_lower:
                used_excluded.add(pkg)  # 保留原始名称
            else:
                not_used_excluded.add(pkg)  # 保留原始名称
        # 排序：代码中用到的排前面
        sorted_list = sorted(used_excluded) + sorted(not_used_excluded)
        # ===== 创建对话框 =====
        dialog = QDialog(self)
        dialog.setWindowTitle("恢复排除的包")
        dialog.setMinimumSize(600, 500)
        dialog.setModal(False)
        dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        layout = QVBoxLayout(dialog)
        # 顶部信息
        info_text = (
            f"📦 共排除 {len(exclude_list)} 个包\n"
            f"🟧 其中 {len(used_excluded)} 个是代码中用到的（排前面）\n\n"
            f"💡 勾选需要恢复的包，点击「恢复勾选的包」即可加入打包"
        )
        info = QLabel(info_text)
        info.setStyleSheet("color: #333; font-size: 12px; padding: 8px; background-color: #e3f2fd; border-radius: 4px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("输入包名搜索...")
        search_layout.addWidget(search_edit)
        layout.addLayout(search_layout)
        # 列表
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 4px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #e8f0fe;
            }
        """)
        for pkg in sorted_list:
            item = QListWidgetItem()
            if pkg in used_excluded:
                item.setText(f"🟧 {pkg}")
                item.setBackground(QColor("#fff3cd"))
            else:
                item.setText(f"📦 {pkg}")
            item.setData(Qt.ItemDataRole.UserRole, pkg)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        # 统计
        count_label = QLabel(f"共 {len(sorted_list)} 个包，已勾选 0 个")
        count_label.setStyleSheet("color: #333; font-size: 12px; padding: 4px;")
        layout.addWidget(count_label)
        # 按钮行
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("✅ 全选")
        select_all_btn.clicked.connect(lambda: self._check_all_items(list_widget, True))
        select_layout.addWidget(select_all_btn)
        select_none_btn = QPushButton("⬜ 取消全选")
        select_none_btn.clicked.connect(lambda: self._check_all_items(list_widget, False))
        select_layout.addWidget(select_none_btn)
        select_used_btn = QPushButton("🟧 选中代码用到的")
        select_used_btn.clicked.connect(lambda: self._check_used_items(list_widget))
        select_layout.addWidget(select_used_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_restore = QPushButton("✅ 恢复勾选的包")
        btn_restore.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        btn_restore.clicked.connect(lambda: self._restore_checked_packages(list_widget, dialog))
        btn_layout.addWidget(btn_restore)
        btn_restore_all = QPushButton("📦 恢复全部")
        btn_restore_all.setStyleSheet("""
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2d9249;
            }
        """)
        btn_restore_all.clicked.connect(lambda: self._restore_all_packages_fast(list_widget, dialog))
        btn_layout.addWidget(btn_restore_all)
        btn_layout.addStretch()
        btn_close = QPushButton("关闭")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #f1f3f4;
                color: #3c4043;
                border: 1px solid #dadce0;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
        """)
        btn_close.clicked.connect(dialog.close)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        def update_count():
            checked = 0
            for i in range(list_widget.count()):
                if list_widget.item(i).checkState() == Qt.CheckState.Checked:
                    checked += 1
            count_label.setText(f"共 {list_widget.count()} 个包，已勾选 {checked} 个")
        list_widget.itemChanged.connect(lambda item: update_count())

        def filter_list(text):
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())
        search_edit.textChanged.connect(filter_list)
        update_count()
        dialog.show()

    def _check_all_items(self, list_widget, checked):
        """全选/取消全选"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def _check_used_items(self, list_widget):
        """勾选所有代码中用到的包（黄色标记的）"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if "代码中用到的" in item.text() and not item.isHidden():
                item.setCheckState(Qt.CheckState.Checked)

    def _restore_checked_packages(self, list_widget, dialog):
        """恢复勾选的包（保留原始名称）"""
        restored = []
        items_to_remove = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                pkg = item.data(Qt.ItemDataRole.UserRole)
                if pkg:
                    items_to_remove.append(i)
                    restored.append(pkg)
        if not restored:
            show_msg(self, "提示", "请先勾选要恢复的包", 1)
            return
        # 获取当前隐藏导入的小写集合
        existing_hidden_lower = {mod.lower() for mod in self.hidden_imports_list}
        # 获取当前排除列表的小写集合
        existing_exclude_lower = {mod.lower() for mod in self.exclude_list}
        added_count = 0
        for pkg in restored:
            pkg_lower = pkg.lower()
            # 从排除列表移除（忽略大小写）
            if pkg_lower in existing_exclude_lower:
                for orig in self.exclude_list[:]:
                    if orig.lower() == pkg_lower:
                        self.exclude_list.remove(orig)
                        break
                existing_exclude_lower.remove(pkg_lower)
            # 添加到隐藏导入（忽略大小写去重）
            if pkg_lower not in existing_hidden_lower:
                self.hidden_imports_list.append(pkg)  # 保留原始名称
                existing_hidden_lower.add(pkg_lower)
                list_item = QListWidgetItem(pkg)  # 显示原始名称
                list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                list_item.setCheckState(Qt.CheckState.Unchecked)
                self.hidden_listbox.addItem(list_item)
                added_count += 1
        # 从对话框移除
        for i in reversed(items_to_remove):
            list_widget.takeItem(i)
        self._update_hidden_count()
        self._update_exclude_count()
        self._update_exclude_listbox()
        if added_count > 0:
            self.safe_log(f"📦 已恢复 {added_count} 个包到隐藏导入")
        if list_widget.count() == 0:
            dialog.close()
        else:
            show_msg(self, "完成", f"已恢复 {added_count} 个包", 1)

    def _restore_all_packages_fast(self, list_widget, dialog):
        """恢复全部包"""
        restored = []
        for i in range(list_widget.count() - 1, -1, -1):
            item = list_widget.item(i)
            pkg = item.data(Qt.ItemDataRole.UserRole)
            if pkg:
                if pkg in self.exclude_list:
                    self.exclude_list.remove(pkg)
                if pkg not in self.hidden_imports_list:
                    self.hidden_imports_list.append(pkg)
                    list_item = QListWidgetItem(pkg)
                    list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    list_item.setCheckState(Qt.CheckState.Unchecked)
                    self.hidden_listbox.addItem(list_item)
                restored.append(pkg)
                list_widget.takeItem(i)
        if restored:
            self._update_hidden_count()
            self._update_exclude_count()
            self.safe_log(f"📦 已恢复全部 {len(restored)} 个包")
            dialog.close()

    def _restore_all_packages_fast(self, list_widget, dialog):
        """快速恢复所有包"""
        restored = []
        for i in range(list_widget.count() - 1, -1, -1):
            item = list_widget.item(i)
            pkg = item.data(Qt.ItemDataRole.UserRole)
            if pkg:
                if pkg in self.exclude_list:
                    self.exclude_list.remove(pkg)
                if pkg not in self.hidden_imports_list:
                    self.hidden_imports_list.append(pkg)
                    self.hidden_listbox.addItem(pkg)
                restored.append(pkg)
                list_widget.takeItem(i)
        if restored:
            self._update_hidden_count()
            self._update_exclude_count()
            self.safe_log(f"📦 已恢复全部 {len(restored)} 个包")
            dialog.close()

    def _get_installed_packages_for_restore(self, python_exe):
        """获取已安装的包列表（用于恢复功能）"""
        packages = set()
        try:
            result = self._run_hidden(
                [python_exe, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True, timeout=30,
                startupinfo=get_startupinfo()
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for item in data:
                    packages.add(item['name'].lower())
        except Exception as e:
            self.safe_log(f"⚠️ 获取包列表失败: {e}")
        return packages

    def _get_installed_packages(self, python_exe):
        """获取指定Python环境的已安装包列表（返回小写->原始名称映射）"""
        if not python_exe or not os.path.exists(python_exe):
            return {}  # ← 只返回空字典
        import subprocess
        import json
        # 清理环境变量
        clean_env = {
            'PATH': os.environ.get('PATH', ''),
            'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
            'SystemRoot': os.environ.get('SystemRoot', ''),
            'COMSPEC': os.environ.get('COMSPEC', ''),
        }
        for key in list(os.environ.keys()):
            if key.upper().startswith('PYTHON') or key.upper() in ('VIRTUAL_ENV', 'CONDA_PREFIX'):
                continue
        clean_env['PYTHONNOUSERSITE'] = '1'
        clean_env['PYTHONSAFEPATH'] = '1'
        startupinfo = None
        creationflags = 0
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
        try:
            result = subprocess.run(
                [python_exe, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True,
                env=clean_env,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                # 返回小写->原始名称映射
                installed_lower_map = {item['name'].lower(): item['name'] for item in data}
                #self.safe_log(f"📋 已安装 {len(installed_lower_map)} 个包")
                return installed_lower_map
            else:
                self.safe_log(f"⚠️ pip list 失败: {result.stderr[:100] if result.stderr else '未知错误'}")
        except Exception as e:
            self.safe_log(f"⚠️ 获取包列表失败: {e}")
        return {}  # ← 只返回空字典

    def _get_needed_packages_from_hidden(self):
        """从 hiddenimports 中提取需要的包"""
        needed = set()
        for mod in self.hidden_imports_list:
            if mod in STANDARD_LIBS:
                continue
            pkg = MODULE_TO_PACKAGE.get(mod, mod.lower())
            if pkg == 'pil':
                pkg = 'pillow'
            if pkg == 'opencv':
                pkg = 'opencv-python'
            needed.add(pkg)
        if 'PyQt6' in self.hidden_imports_list:
            needed.add('pyqt6')
        if 'PyQt5' in self.hidden_imports_list:
            needed.add('pyqt5')
        if 'PySide6' in self.hidden_imports_list:
            needed.add('pyside6')
        if 'PySide2' in self.hidden_imports_list:
            needed.add('pyside2')
        if 'PIL' in self.hidden_imports_list or 'Image' in self.hidden_imports_list:
            needed.add('pillow')
        return needed

    def _build_restore_exclude_list(self, all_installed, needed_packages):
        """构建排除列表（用于恢复对话框）"""
        exclude_list = []
        std_lib_names = set(STANDARD_LIBS)
        for pkg in all_installed:
            if pkg in std_lib_names or pkg.startswith('_'):
                continue
            if pkg not in needed_packages:
                exclude_list.append(pkg)
        for mod in self.exclude_list:
            if mod not in exclude_list:
                exclude_list.append(mod)
        return exclude_list

    def _restore_selected_packages_ui(self, list_widget, dialog):
        """恢复选中的包（支持多选）"""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选中要恢复的包（按住 Ctrl 或 Shift 多选）")
            return
        restored = []
        for item in selected_items:
            pkg = item.text()
            if pkg in self.exclude_list:
                self.exclude_list.remove(pkg)
            if pkg not in self.hidden_imports_list:
                self.hidden_imports_list.append(pkg)
                self.hidden_listbox.addItem(pkg)
            restored.append(pkg)
            list_widget.takeItem(list_widget.row(item))
        if restored:
            self._update_hidden_count()
            self._update_exclude_count()
            self.safe_log(f"📦 已恢复 {len(restored)} 个包: {', '.join(restored)}")
            if list_widget.count() == 0:
                show_msg(self, "完成", "所有包已恢复",1)
                dialog.accept()
            else:
                show_msg(self, "完成", f"已恢复 {len(restored)} 个包",1)

    def _restore_used_packages(self, list_widget, dialog):
        """一键恢复所有代码中用到的包（黄色标记的）"""
        restored = []
        items_to_remove = []
        for i in range(list_widget.count() - 1, -1, -1):
            item = list_widget.item(i)
            if item.isHidden():
                continue
            pkg = item.text()
            if item.background().color().name() == "#fff3cd":
                if pkg in self.exclude_list:
                    self.exclude_list.remove(pkg)
                if pkg not in self.hidden_imports_list:
                    self.hidden_imports_list.append(pkg)
                    self.hidden_listbox.addItem(pkg)
                restored.append(pkg)
                items_to_remove.append(i)
        for i in sorted(items_to_remove, reverse=True):
            list_widget.takeItem(i)
        if restored:
            self._update_hidden_count()
            self._update_exclude_count()
            self.safe_log(f"📦 已恢复 {len(restored)} 个代码中用到的包")
            if list_widget.count() == 0:
                show_msg(self, "完成", "所有用到的包已恢复",1)
                dialog.accept()
            else:
                show_msg(self, "完成", f"已恢复 {len(restored)} 个代码中用到的包",1)
        else:
            show_msg(self, "提示", "没有代码中用到的包需要恢复",1)

    def _restore_all_excludes_ui(self, list_widget, dialog):
        """恢复所有排除的包"""
        if list_widget.count() == 0:
            show_msg(self, "提示", "没有包需要恢复",1)
            return
        reply = QMessageBox.question(
            self,
            "确认恢复",
            f"确定要恢复所有 {list_widget.count()} 个包吗？\n（包括代码中未检测到的）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        restored = []
        for i in range(list_widget.count() - 1, -1, -1):
            item = list_widget.item(i)
            pkg = item.text()
            if pkg in self.exclude_list:
                self.exclude_list.remove(pkg)
            if pkg not in self.hidden_imports_list:
                self.hidden_imports_list.append(pkg)
                self.hidden_listbox.addItem(pkg)
            restored.append(pkg)
            list_widget.takeItem(i)
        if restored:
            self._update_hidden_count()
            self._update_exclude_count()
            self.safe_log(f"📦 已恢复全部 {len(restored)} 个包")
            dialog.accept()

    def _refresh_data_list(self):
        """刷新数据文件列表（保留排除标记状态）"""
        self.data_listbox.clear()
        exclude_from_pack = getattr(self, 'exclude_from_pack', [])
        for src, dst in self.data_files_list:
            if src in exclude_from_pack:
                self.data_listbox.addItem(f"🚫 {os.path.basename(src)} -> {dst}")
            else:
                self.data_listbox.addItem(f"{os.path.basename(src)} -> {dst}")
        self._update_data_count()

    def _run_selected_data_py(self):
        """智能运行 - 支持py和exe文件"""
        py_files = []
        exe_files = []
        for src, dst in self.data_files_list:
            if os.path.exists(src):
                if src.endswith('.py'):
                    py_files.append(src)
                elif src.endswith('.exe'):
                    exe_files.append(src)
        # ===== 如果没有py也没有exe =====
        if not py_files and not exe_files:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择要运行的文件",
                "",
                "可执行文件 (*.py *.exe);;Python文件 (*.py);;EXE文件 (*.exe);;所有文件 (*.*)"
            )
            if file_path:
                self._run_file(file_path)
            else:
                self.safe_log("⚠️ 未选择文件")
            return
        all_files = py_files + exe_files
        if len(all_files) == 1:
            self._run_file(all_files[0])
            return
        items = []
        file_map = {}
        for f in all_files:
            ext = os.path.splitext(f)[1].lower()
            icon = "🐍" if ext == '.py' else "📦"
            display = f"{icon} {os.path.basename(f)}"
            items.append(display)
            file_map[display] = f
        script_name, ok = QInputDialog.getItem(
            self,
            "选择要运行的文件",
            "请选择要运行的文件:",
            items,
            0,
            False
        )
        if not ok:
            return
        selected_file = file_map.get(script_name)
        if selected_file:
            self._run_file(selected_file)

    def _run_file(self, file_path):
        """运行单个文件（py或exe）"""
        if not file_path or not os.path.exists(file_path):
            self.safe_log(f"⚠️ 文件不存在: {file_path}")
            return
        ext = os.path.splitext(file_path)[1].lower()
        # ===== 判断是否勾选了外部工具 =====
        use_external_tool = self.external_tool_cb.isChecked()
        if ext == '.exe':
            self.safe_log(f"▶ 运行EXE: {os.path.basename(file_path)}")
            if use_external_tool:
                self._run_exe_with_params(file_path)
            else:
                self._run_exe_direct(file_path)
            return
        # ===== 如果是py =====
        if ext == '.py':
            if use_external_tool:
                # 外部工具模式：传递参数
                self.safe_log(f"📤 外部工具模式 - 目标脚本: {os.path.basename(file_path)}")
                self._run_with_external_tool([file_path])
            else:
                # 直接运行
                self._execute_py_script(file_path)
            return
        # ===== 其他文件 =====
        self.safe_log(f"⚠️ 不支持的文件类型: {ext}")

    def _run_exe_direct(self, exe_path):
        """直接运行EXE - 使用 _popen_hidden"""

        def run():
            try:
                self.safe_log(f"▶ 启动EXE: {os.path.basename(exe_path)}")
                if sys.platform == 'win32':
                    import ctypes
                    ctypes.windll.shell32.ShellExecuteW(
                        None,
                        "open",
                        exe_path,
                        None,
                        os.path.dirname(exe_path),
                        1  # SW_SHOWNORMAL - 正常显示GUI
                    )
                    self.safe_log(f"✅ EXE已启动")
                else:
                    subprocess.Popen(
                        [exe_path],
                        cwd=os.path.dirname(exe_path),
                        start_new_session=True
                    )
                    self.safe_log(f"✅ EXE已启动")
            except Exception as e:
                self.safe_log(f"❌ 运行EXE失败: {e}")
        threading.Thread(target=run, daemon=True).start()

    def _run_exe_with_params(self, exe_path):
        """外部工具模式运行EXE - 隐藏控制台"""

        def run():
            try:
                # ===== 构建参数 =====
                packer = self.packer_combo.currentText()
                main_script = self.input_file.text()
                params = {
                    'python_version': self.python_version.text() or sys.version.split()[0],
                    'python_exe': self.python_path.currentText() or sys.executable,
                    'packer': packer,
                    'main_script': main_script,
                    'target_exe': exe_path,
                    'exe_temp_path': self._get_target_temp_path(packer, exe_path),
                    'output_dir': self.output_dir.text(),
                    'project_name': self.app_name.text(),
                    'onefile': self.single_mode.isChecked(),
                    'debug': self.debug_mode.isChecked(),
                    'use_venv': self.venv_mode.isChecked(),
                    'hidden_imports': self.hidden_imports_list,
                    'excludes': self.exclude_list,
                    'data_files': self.data_files_list,
                    'compress_level': self.compress_combo.currentText(),
                    'icon_path': self.icon_label.toolTip() if self.icon_label.text() else '',
                }
                import tempfile
                config_file = os.path.join(tempfile.gettempdir(), 'external_tool_config.json')
                with open(config_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(params, f, ensure_ascii=False, indent=2, default=str)
                self.safe_log(f"📤 外部工具模式 - 目标EXE: {os.path.basename(exe_path)}")
                # ===== 隐藏控制台启动 =====
                if sys.platform == 'win32':
                    subprocess.Popen(
                        [exe_path, f'--config={config_file}', '--from-main'],
                        cwd=os.path.dirname(exe_path),
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                else:
                    subprocess.Popen(
                        [exe_path, f'--config={config_file}', '--from-main'],
                        cwd=os.path.dirname(exe_path),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        start_new_session=True
                    )
                self.safe_log(f"✅ EXE已启动 (外部工具模式)")
            except Exception as e:
                self.safe_log(f"❌ 运行EXE失败: {e}")
        threading.Thread(target=run, daemon=True).start()

    def _run_py_direct(self, py_files):
        """原有模式 - 直接运行"""
        if len(py_files) > 1:
            items = [os.path.basename(f) for f in py_files]
            script_name, ok = QInputDialog.getItem(
                self,
                "选择脚本",
                "请选择要运行的脚本:",
                items,
                0,
                False
            )
            if not ok:
                return
            script_path = None
            for src, dst in self.data_files_list:
                if os.path.basename(src) == script_name:
                    script_path = src
                    break
            if script_path:
                self._execute_py_script(script_path)
            return
        self._execute_py_script(py_files[0])

    def _run_with_external_tool(self, py_files):
        """外部工具模式 - 传递参数给外部py"""
        if len(py_files) > 1:
            items = [os.path.basename(f) for f in py_files]
            script_name, ok = QInputDialog.getItem(
                self,
                "选择目标脚本",
                "请选择要传递给外部工具的脚本:",
                items,
                0,
                False
            )
            if not ok:
                return
            script_path = None
            for src, dst in self.data_files_list:
                if os.path.basename(src) == script_name:
                    script_path = src
                    break
        else:
            script_path = py_files[0]
        if not script_path:
            return
        packer = self.packer_combo.currentText()
        main_script = self.input_file.text()
        target_exe = self._get_target_exe_path(packer, main_script)
        exe_temp_path = self._get_target_temp_path(packer, target_exe)
        if not exe_temp_path:
            output_dir = self.output_dir.text()
            if output_dir:
                exe_temp_path = os.path.join(output_dir, 'extracted')
            else:
                import tempfile
                exe_temp_path = os.path.join(tempfile.gettempdir(), 'pyinstxtractor_extracted')
        # ===== 构建参数 =====
        params = {
            'python_version': self.python_version.text() or sys.version.split()[0],
            'python_exe': self.python_path.currentText() or sys.executable,
            'packer': packer,
            'main_script': main_script,
            'target_script': script_path,
            'target_exe': target_exe,
            'exe_temp_path': exe_temp_path,  # 现在一定有值
            'output_dir': self.output_dir.text(),
            'project_name': self.app_name.text(),
            'onefile': self.single_mode.isChecked(),
            'debug': self.debug_mode.isChecked(),
            'use_venv': self.venv_mode.isChecked(),
            'hidden_imports': self.hidden_imports_list,
            'excludes': self.exclude_list,
            'data_files': self.data_files_list,
            'compress_level': self.compress_combo.currentText(),
            'icon_path': self.icon_label.toolTip() if self.icon_label.text() else '',
        }
        # ===== 写入JSON =====
        import tempfile
        config_file = os.path.join(tempfile.gettempdir(), 'external_tool_config.json')
        with open(config_file, 'w', encoding='utf-8-sig') as f:
            json.dump(params, f, ensure_ascii=False, indent=2, default=str)
        self.safe_log(f"📤 外部工具模式 - 目标脚本: {os.path.basename(script_path)}")
        self.safe_log(f"📦 打包器: {packer}")
        self.safe_log(f"📁 临时路径: {exe_temp_path}")
        self.safe_log(f"📋 配置文件: {config_file}")
        # ===== 调用外部脚本 =====
        self._execute_external_py(script_path, config_file, params)

    def _get_target_exe_path(self, packer, main_script):
        """根据打包器获取目标EXE路径"""
        if not main_script or not os.path.exists(main_script):
            return ""
        base_name = os.path.splitext(os.path.basename(main_script))[0]
        output_dir = self.output_dir.text()
        script_dir = os.path.dirname(main_script)
        # 根据打包器确定exe位置
        if packer.startswith('PyInstaller'):
            possible_paths = [
                os.path.join(output_dir, f'{base_name}.exe'),
                os.path.join(output_dir, base_name, f'{base_name}.exe'),
                os.path.join(script_dir, 'dist', f'{base_name}.exe'),
                os.path.join(script_dir, 'dist', base_name, f'{base_name}.exe'),
            ]
        elif packer == 'Nuitka':
            possible_paths = [
                os.path.join(output_dir, f'{base_name}.exe'),
                os.path.join(output_dir, base_name, f'{base_name}.exe'),
                os.path.join(script_dir, f'{base_name}.exe'),
                os.path.join(script_dir, 'dist', f'{base_name}.exe'),
            ]
        else:
            possible_paths = [
                os.path.join(output_dir, f'{base_name}.exe'),
                os.path.join(script_dir, 'dist', f'{base_name}.exe'),
            ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return os.path.join(output_dir, f'{base_name}.exe')

    def _get_target_temp_path(self, packer, target_exe):
        """获取目标EXE运行时自身的临时解压路径"""
        import tempfile
        temp_base = tempfile.gettempdir()
        # ===== 获取主脚本名 =====
        main_script = self.input_file.text()
        if not main_script or not os.path.exists(main_script):
            return temp_base
        base_name = os.path.splitext(os.path.basename(main_script))[0]
        # ===== PyInstaller: 运行时解压到 Temp\_MEIxxxxx =====
        if packer.startswith('PyInstaller'):
            # PyInstaller 运行时会在 Temp 目录创建 _MEIxxxxx 文件夹
            for item in os.listdir(temp_base):
                if item.startswith('_MEI') and os.path.isdir(os.path.join(temp_base, item)):
                    temp_dir = os.path.join(temp_base, item)
                    # 检查是否包含目标exe相关的文件
                    try:
                        # _MEI 目录通常包含 python 相关文件
                        if any(f.endswith('.dll') or f.endswith('.pyd') for f in os.listdir(temp_dir) if
                               os.path.isfile(os.path.join(temp_dir, f))):
                            return temp_dir
                    except:
                        pass
            # 如果没找到，返回可能的路径
            return os.path.join(temp_base, f"_MEI_{base_name}")
        # ===== Nuitka: 运行时解压到 Temp\onefile_xxxxx =====
        elif packer == 'Nuitka':
            # Nuitka onefile 运行时会在 Temp 目录创建 onefile_xxxxx 文件夹
            for item in os.listdir(temp_base):
                if item.startswith('onefile_') and os.path.isdir(os.path.join(temp_base, item)):
                    temp_dir = os.path.join(temp_base, item)
                    try:
                        if any(f.endswith('.py') for f in os.listdir(temp_dir) if
                               os.path.isfile(os.path.join(temp_dir, f))):
                            return temp_dir
                    except:
                        pass
            return os.path.join(temp_base, f"onefile_{base_name}")
        else:
            return temp_base

    def _execute_external_py(self, target_script, config_file, params):
        """执行外部脚本（带参数）- 启动时直接隐藏控制台"""

        def run():
            try:
                python_exe = self.python_path.currentText()
                if not python_exe or not os.path.exists(python_exe):
                    python_exe = sys.executable
                cmd = [python_exe, target_script, '--from-main', f'--config={config_file}']
                self.safe_log(f"▶ 启动外部脚本: {os.path.basename(target_script)}")
                # ===== Windows: 彻底隐藏控制台 =====
                if sys.platform == 'win32':
                    # 方法1: 使用 CREATE_NO_WINDOW
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        cwd=os.path.dirname(target_script)
                    )
                else:
                    # Linux/macOS
                    subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True,
                        cwd=os.path.dirname(target_script)
                    )
                self.safe_log(f"✅ 外部脚本已启动")
            except Exception as e:
                self.safe_log(f"❌ 运行出错: {e}")
        threading.Thread(target=run, daemon=True).start()

    def _get_temp_path(self):
        """获取临时解压路径"""
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS  # PyInstaller
            elif hasattr(sys, '__compiled__'):
                return os.environ.get('NUITKA_ONEFILE_TEMP', '')  # Nuitka
            else:
                return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))

    def _execute_py_script(self, script_path):
        """执行Python脚本 - 使用 _popen_hidden 或新建控制台"""

        def run():
            try:
                python_exe = self.python_path.currentText()
                if not python_exe or not os.path.exists(python_exe):
                    python_exe = sys.executable
                main_args = sys.argv[1:] if len(sys.argv) > 1 else []
                cmd = [python_exe, script_path] + main_args
                self.safe_log(f"▶ 运行: {os.path.basename(script_path)}")
                if main_args:
                    self.safe_log(f"📋 参数: {' '.join(main_args)}")
                # ===== 判断是否显示控制台 =====
                show_console = self.show_console_cb.isChecked() if hasattr(self, 'show_console_cb') else False
                if sys.platform == 'win32':
                    if show_console:
                        # 显示控制台（使用 CREATE_NEW_CONSOLE）
                        subprocess.Popen(
                            cmd,
                            cwd=os.path.dirname(script_path),
                            creationflags=subprocess.CREATE_NEW_CONSOLE
                        )
                        self.safe_log(f"✅ 脚本已启动 (显示控制台)")
                    else:
                        # ===== 使用 _popen_hidden 完全隐藏 =====
                        self._popen_hidden(
                            cmd,
                            cwd=os.path.dirname(script_path),
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        self.safe_log(f"✅ 脚本已启动 (后台运行)")
                else:
                    # Linux/macOS
                    subprocess.Popen(
                        cmd,
                        cwd=os.path.dirname(script_path),
                        start_new_session=True
                    )
                    self.safe_log(f"✅ 脚本已启动")
            except Exception as e:
                self.safe_log(f"❌ 运行出错: {e}")
        threading.Thread(target=run, daemon=True).start()

    def _toggle_data_py_exclude(self):
        """标记/取消标记选中的文件不随exe打包"""
        current = self.data_listbox.currentRow()
        if current < 0:
            self.safe_log("⚠️ 请先在数据文件列表中选中一个文件")
            QMessageBox.warning(self, "提示", "请先在数据文件列表中选中一个文件")
            return
        item_text = self.data_listbox.currentItem().text()
        display_name = item_text.replace("🚫 ", "")
        src_part = display_name.split(" -> ")[0]
        file_path = None
        for src, dst in self.data_files_list:
            if os.path.basename(src) == src_part:
                file_path = src
                break
        if not file_path:
            self.safe_log(f"⚠️ 找不到文件: {src_part}")
            return
        if not os.path.exists(file_path):
            self.safe_log(f"⚠️ 文件不存在: {file_path}")
            return
        if not hasattr(self, 'exclude_from_pack'):
            self.exclude_from_pack = []
        item = self.data_listbox.currentItem()
        if file_path in self.exclude_from_pack:
            # 取消排除（恢复打包）
            self.exclude_from_pack.remove(file_path)
            item.setText(f"{os.path.basename(file_path)} -> .")
            self.safe_log(f"📦 恢复打包: {os.path.basename(file_path)}")
        else:
            # 标记排除
            self.exclude_from_pack.append(file_path)
            item.setText(f"🚫 {os.path.basename(file_path)} -> .")
            self.safe_log(f"🚫 排除打包: {os.path.basename(file_path)}")

    def _compare_files(self):
        """启动代码对比"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            # 没有当前脚本，让用户选择
            left_file = QFileDialog.getOpenFileName(self, "选择源文件（原始）", "", "Python文件 (*.py)")[0]
            if not left_file:
                return
            right_file = QFileDialog.getOpenFileName(self, "选择编译文件（修改后）", "", "Python文件 (*.py)")[0]
            if not right_file:
                return
        else:
            backup = os.path.splitext(script)[0] + '.bak.py'
            if os.path.exists(backup):
                left_file = backup  
                right_file = script  
            else:
                # 无备份，左右都使用当前脚本（用户可手动更改）
                left_file = script
                right_file = script
        dlg = CodeCompareDialog(self, left_file, right_file)
        dlg.exec()

    def _toggle_help_about(self):
        """切换关于窗口"""
        if hasattr(self, 'about_dialog') and self.about_dialog is not None:
            if self.about_dialog.isVisible():
                self.about_dialog.close()
                self.about_dialog.deleteLater()
                self.about_dialog = None
                return
        # 创建独立窗口
        self.about_dialog = AboutDialog(self)
        self.about_dialog.setWindowFlags(Qt.WindowType.Window)
        self.about_dialog.setModal(False)  # ← 关键：显式设置为非模态
        self.about_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.about_dialog.destroyed.connect(lambda: setattr(self, 'about_dialog', None))
        self.about_dialog.show()

    def _launch_auto(self):
        try:
            self._popen_hidden(["auto-py-to-exe"], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform=="win32" else 0)
            self.safe_log("已启动 auto-py-to-exe")
        except FileNotFoundError:
            if messagebox.askyesno("未安装", "auto-py-to-exe 未安装，是否安装？"):
                self._run_hidden([self._get_python(), "-m", "pip", "install", "auto-py-to-exe"], check=True)
                self.safe_log("安装完成，请再次点击")

    def status_start(self, text, color="gray"):
        self.status_progress.setFormat("")
        """开始进度条"""
        colors = {"gray": "#9e9e9e", "red": "#f44336", "orange": "#ff9800", "green": "#4caf50",
                "blue": "#2196f3", "purple": "#9c27b0"}
        self.status_color = colors.get(color, "#9e9e9e")
        self.status_progress.setVisible(True)
        self.status_pct.setVisible(True)
        self.status_label.setText(text[:8])  # 限制文字长度
        self.status_pct.setText("0%")
        self.status_progress.setValue(0)
        self.status_progress.setStyleSheet(f"""
            QProgressBar {{ border: none; border-radius: 8px; background-color: #e0e0e0; }}
            QProgressBar::chunk {{ background-color: {self.status_color}; border-radius: 8px; }}
        """)

    def _data_listbox_drag_move(self, event):
        """数据列表拖拽移动"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _data_listbox_drag_enter(self, event):
        """数据列表拖拽进入"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 高亮效果
            self.data_listbox.setStyleSheet("QListWidget { background-color: #e8f5e9; }")
        else:
            event.ignore()

    def _data_panel_drag_enter(self, event):
        """数据面板拖拽进入"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _data_panel_drop(self, event):
        """数据面板拖拽放下 - 整个右边面板都响应"""
        # 恢复样式
        urls = event.mimeData().urls()
        if not urls:
            event.ignore()
            return
        files = []
        for u in urls:
            path = u.toLocalFile()
            if path and os.path.exists(path):
                files.append(path)
        if files:
            self.safe_log(f"📁 数据面板接收到 {len(files)} 个文件")
            self._on_data_drop(files)
            event.acceptProposedAction()
        else:
            self.safe_log("⚠️ 拖拽的文件无效或不存在")
            event.ignore()

    def _data_listbox_drop(self, event):
        """数据列表拖拽放下"""
        # 恢复样式
        self.data_listbox.setStyleSheet("")
        urls = event.mimeData().urls()
        if not urls:
            event.ignore()
            return
        files = []
        for u in urls:
            path = u.toLocalFile()
            if path and os.path.exists(path):
                files.append(path)
        if files:
            # 先显示拖拽提示
            self.safe_log(f"📁 检测到拖拽 {len(files)} 个文件/文件夹到数据区")
            self._on_data_drop(files)
            event.acceptProposedAction()
        else:
            self.safe_log("⚠️ 拖拽的文件无效或不存在")
            event.ignore()

    def _on_data_drop(self, files):
        """处理数据文件拖拽（带去重）"""
        self.safe_log(f"📁 开始处理数据区拖拽，共 {len(files)} 个项目")
        added_count = 0
        skipped_count = 0
        for f in files:
            if not os.path.exists(f):
                self.safe_log(f"⚠️ 文件/文件夹不存在: {f}")
                skipped_count += 1
                continue
            # 检查是否已存在相同的源文件路径
            existing = [src for src, _ in self.data_files_list if src == f]
            if existing:
                self.safe_log(f"⚠️ 已存在，跳过: {os.path.basename(f)}")
                skipped_count += 1
                continue
            # 如果是文件夹，递归添加所有文件（也带去重）
            if os.path.isdir(f):
                self.safe_log(f"📁 处理文件夹: {os.path.basename(f)}")
                count = self._add_directory_files(f)
                added_count += count
                if count > 0:
                    self.safe_log(f"✅ 从文件夹添加了 {count} 个文件")
                else:
                    self.safe_log(f"📌 文件夹中没有新文件: {os.path.basename(f)}")
            else:
                # 单个文件
                self.data_files_list.append((f, "."))
                self.data_listbox.addItem(f"{os.path.basename(f)} -> .")
                self.safe_log(f"✅ 已添加数据文件: {os.path.basename(f)}")
                added_count += 1
        # 输出汇总信息
        self.safe_log(f"📊 数据区拖拽完成: 新增 {added_count} 个文件, 跳过 {skipped_count} 个")
        if added_count == 0 and skipped_count > 0:
            self.safe_log("💡 提示: 所有文件都已存在，如需重新添加请先删除现有项")
        self._update_data_count()

    def _add_directory_files(self, directory, target_dir="."):
        """递归添加目录中的所有文件（带去重）"""
        count = 0
        for root, dirs, files in os.walk(directory):
            # 跳过常见的忽略目录
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'dist', 'build'}]
            for file in files:
                src = os.path.join(root, file)
                # 检查是否已存在
                existing = [s for s, _ in self.data_files_list if s == src]
                if existing:
                    continue
                # 计算相对路径
                rel_path = os.path.relpath(root, directory)
                if rel_path == ".":
                    tgt = target_dir
                else:
                    tgt = os.path.join(target_dir, rel_path).replace("\\", "/")
                self.data_files_list.append((src, tgt))
                self.data_listbox.addItem(f"{os.path.basename(src)} -> {tgt}")
                count += 1
        if count > 0:
            self.safe_log(f"✅ 从目录添加了 {count} 个文件: {os.path.basename(directory)}")
        return count

    def status_set_target(self, target, text=None, color=None):
        """设置进度"""
        if color:
            colors = {"gray": "#9e9e9e", "red": "#f44336", "orange": "#ff9800", "green": "#4caf50",
                    "blue": "#2196f3", "purple": "#9c27b0"}
            self.status_color = colors.get(color, "#9e9e9e")
            self.status_progress.setStyleSheet(f"""
                QProgressBar {{ border: none; border-radius: 8px; background-color: #e0e0e0; }}
                QProgressBar::chunk {{ background-color: {self.status_color}; border-radius: 8px; }}
            """)
        if text:
            self.status_label.setText(text[:8])  # 限制文字长度
        self.status_progress.setValue(target)
        self.status_pct.setText(f"{target}%")

    def status_finish(self, text="就绪"):
        """完成并隐藏进度条"""
        self.status_progress.setVisible(False)
        self.status_pct.setVisible(False)
        self.status_label.setText(text)
        # 重置进度条值
        self.status_progress.setValue(0)

    def _on_progress_style_changed(self, text):
        """手动切换进度条样式"""
        style_map = {
            "🌈 七彩虹": "striped",
            "😊 表情图": "emoji",
            "😊 波浪纹": "wave",
            "😊 点阵图": "dot",
            "🌿 薄荷绿": "green",
            "🌸 樱花粉": "pink",
            "🌌 星际紫": "purple",
            "🌊 深海蓝": "blue",
        }
        style = style_map.get(text, "striped")
        self._switch_progress_bar_by_style(style)

    def _switch_progress_bar_by_style(self, style):
        """根据样式名称切换进度条"""
        current_value = self.progress_bar.value()
        parent_layout = self.progress_bar.parent().layout()
        # 找到进度条位置
        index = -1
        for i in range(parent_layout.count()):
            if parent_layout.itemAt(i).widget() == self.progress_bar:
                index = i
                break
        if index == -1:
            return
        # 移除旧进度条
        old_bar = self.progress_bar
        parent_layout.removeWidget(old_bar)
        old_bar.deleteLater()
        # 创建新进度条
        if style == "striped":
            self.progress_bar = StripedProgressBar()
        elif style == "emoji":
            self.progress_bar = EmojiProgressBar()
        elif style == "wave":
            self.progress_bar = WaveProgressBar()
        elif style == "dot":
            self.progress_bar = DotProgressBar()
        elif style == "green":
            self.progress_bar = GreenProgressBar()
        elif style == "pink":
            self.progress_bar = PinkProgressBar()
        elif style == "purple":
            self.progress_bar = PurpleProgressBar()
        else:
            self.progress_bar = BlueProgressBar()
        # ===== 关键：设置 sizePolicy 让进度条填满宽度 =====
        from PyQt6.QtWidgets import QSizePolicy
        self.progress_bar.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # 水平方向拉伸
            QSizePolicy.Policy.Fixed  # 垂直方向固定
        )
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        # ===== 修复：先设置值，再插入布局 =====
        self.progress_bar.setValue(current_value)
        parent_layout.insertWidget(index, self.progress_bar)
        # ===== 强制应用样式表（修复启动时样式不显示） =====
        self.progress_bar.style().polish(self.progress_bar)
        self.progress_bar.update()
        self.progress_bar.repaint()
        # ===== 强制刷新布局 =====
        parent_layout.activate()
        import gc
        gc.collect()

    def _create_progress_bar_by_theme(self):
        """根据当前主题创建对应的进度条"""
        current_theme = self.themes[self.current_theme_idx]
        style = self.theme_progress_styles.get(current_theme, "striped")
        if style == "striped":
            return StripedProgressBar()
        elif style == "emoji":
            return EmojiProgressBar()
        elif style == "green":
            return GreenProgressBar()
        elif style == "pink":
            return PinkProgressBar()
        elif style == "purple":
            return PurpleProgressBar()
        elif style == "blue":
            return BlueProgressBar()
        else:
            return StripedProgressBar()

    def _switch_progress_bar(self):
        """切换进度条样式"""
        try:
            # 保存当前进度值
            current_value = self.progress_bar.value()
            # 获取父布局 - 进度条在 progress_container 的布局中
            parent_widget = self.progress_bar.parent()
            if parent_widget is None:
                return
            parent_layout = parent_widget.layout()
            if parent_layout is None:
                return
            # 找到进度条在布局中的位置
            index = -1
            for i in range(parent_layout.count()):
                item = parent_layout.itemAt(i)
                if item and item.widget() == self.progress_bar:
                    index = i
                    break
            if index == -1:
                return
            # 移除旧进度条
            old_bar = self.progress_bar
            parent_layout.removeWidget(old_bar)
            old_bar.deleteLater()
            # ===== 关键：设置 sizePolicy 让进度条填满宽度 =====
            from PyQt6.QtWidgets import QSizePolicy
            self.progress_bar.setSizePolicy(
                 QSizePolicy.Policy.Expanding,  # 水平方向拉伸
                 QSizePolicy.Policy.Fixed       # 垂直方向固定
            )
            # 创建新进度条
            self.progress_bar = self._create_progress_bar_by_theme()
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(current_value)
            # 插入到原位置
            parent_layout.insertWidget(index, self.progress_bar)
        except Exception as e:
            self.safe_log(f"⚠️ 切换进度条样式失败: {e}")

    def _restore_original_script(self):
        """恢复原始源码（保留备份，不删除）"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            return
        # ===== 修复：使用正确的变量名 script =====
        backup_path = os.path.splitext(script)[0] + '.bak.py'
        if os.path.exists(backup_path):
            try:
                # 恢复但不删除备份
                shutil.copy2(backup_path, script)
                self.safe_log("✅ 已从备份恢复原始源码（备份保留）")
                return True
            except Exception as e:
                self.safe_log(f"⚠️ 恢复源码失败: {e}")
                return False
        else:
            self.safe_log("ℹ️ 没有备份文件，无需恢复")
            return False

    def _smart_inject_code_to_script(self, script_path):
        """智能注入：检测源码中是否已有相关实现，没有才注入"""
        try:
            with open(script_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            # 备份
            backup_path = os.path.splitext(script_path)[0] + '.bak.py'
            if not os.path.exists(backup_path):
                with open(backup_path, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
            inject_blocks = []
            replaced_count = 0
            # --- 防多开 ---
            if self.inject_selected.get('single_instance', False):
                if '_check_single_instance' not in content:
                    inject_blocks.append(textwrap.dedent('''\
                        # --- 防多开注入开始 ---
                        import socket
                        import sys
                        def _check_single_instance():
                            try:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.bind(('127.0.0.1', 28374))
                                return True
                            except socket.error:
                                return False
                        if not _check_single_instance():
                            sys.exit(0)
                        # --- 防多开注入结束 ---
                    '''))
            # --- 工作目录切换 ---
            if self.inject_selected.get('workdir', False):
                if '_set_workdir' not in content:
                    inject_blocks.append(textwrap.dedent('''\
                        # --- 工作目录切换注入开始 ---
                        import os
                        import sys
                        def _set_workdir():
                            if hasattr(sys, '_MEIPASS'):
                                base = os.path.dirname(sys.executable)
                            else:
                                base = os.path.dirname(os.path.abspath(__file__))
                            os.chdir(base)
                            return base
                        _set_workdir()
                        # --- 工作目录切换注入结束 ---
                    '''))
            # --- 资源路径处理 ---
            if self.inject_selected.get('resource_path', False):
                if 'resource_path' not in content:
                    # 检测是否有资源加载调用
                    if re.search(r'(QIcon|QPixmap|open)\s*\(\s*["\'][^"\']+\.(?:ico|png|jpg|json|txt)', content):
                        inject_blocks.append(textwrap.dedent('''\
                            # --- 资源路径处理注入开始 ---
                            import os
                            import sys
                            def resource_path(relative_path):
                                if hasattr(sys, '_MEIPASS'):
                                    return os.path.join(sys._MEIPASS, relative_path)
                                return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
                            import builtins
                            builtins.resource_path = resource_path
                            # --- 资源路径处理注入结束 ---
                        '''))
                        # 替换资源加载调用
                        def replace_func(match):
                            nonlocal replaced_count
                            func = match.group(1)
                            quote = match.group(2)
                            path = match.group(3)
                            replaced_count += 1
                            return f'{func}(resource_path({quote}{path}{quote}))'
                        content = re.sub(
                            r'(QIcon|QPixmap|QImage|open)\s*\(\s*(["\'])([^"\']+\.(?:ico|png|jpg|jpeg|bmp|gif|svg|json|txt|xml))\2\s*\)',
                            replace_func, content
                        )
            # --- 异常捕获 ---
            if self.inject_selected.get('exception_handler', False):
                if 'sys.excepthook' not in content:
                    inject_blocks.append(textwrap.dedent('''\
                        # --- 异常捕获注入开始 ---
                        import sys
                        import traceback
                        def _global_exception_handler(exc_type, exc_value, exc_tb):
                            try:
                                with open('error.log', 'a', encoding='utf-8-sig') as f:
                                    f.write('--- Exception ---\\n')
                                    traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
                            except:
                                pass
                            sys.__excepthook__(exc_type, exc_value, exc_tb)
                        sys.excepthook = _global_exception_handler
                        # --- 异常捕获注入结束 ---
                    '''))
            if not inject_blocks:
                return False, 0
            # 插入代码
            lines = content.splitlines(keepends=True)
            import_pattern = re.compile(r'^\s*(?:import|from)\s+')
            insert_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not import_pattern.match(line):
                    insert_idx = i
                    break
            new_lines = lines[:insert_idx] + ['\n'] + [block + '\n' for block in inject_blocks] + ['\n'] + lines[
                                                                                                        insert_idx:]
            with open(script_path, 'w', encoding='utf-8-sig') as f:
                f.write(''.join(new_lines))
            return True, replaced_count
        except Exception as e:
            self.safe_log(f"❌ 源码注入失败: {e}")
            return False, 0
    # ==== 打包控制 ====

    def _fix_spec_indentation(self, spec_file):
        """自动修复spec文件的缩进问题"""
        try:
            with open(spec_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            lines = content.splitlines()
            new_lines = []
            in_exe = False
            exe_indent = 0
            exe_params_start = -1
            for i, line in enumerate(lines):
                stripped = line.strip()
                # 检测 EXE( 行
                if 'exe = EXE(' in stripped or stripped == 'exe = EXE(':
                    in_exe = True
                    exe_indent = len(line) - len(line.lstrip())
                    exe_params_start = i + 1
                    new_lines.append(line)
                    continue
                # 在 EXE 内部
                if in_exe:
                    # 检测是否已退出 EXE 括号
                    if stripped == ')' or stripped == '),':
                        in_exe = False
                        new_lines.append(line)
                        continue
                    # 跳过空行
                    if not stripped:
                        new_lines.append(line)
                        continue
                    # 计算当前行缩进
                    current_indent = len(line) - len(line.lstrip())
                    expected_indent = exe_indent + 4
                    # 如果缩进不正确，修正它
                    if current_indent != expected_indent and stripped:
                        # 确保行以逗号结尾或包含参数
                        new_line = ' ' * expected_indent + stripped
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                    continue
                new_lines.append(line)
            # 写回文件
            with open(spec_file, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(new_lines))
            self.safe_log("🔧 已自动修复spec缩进")
            return True
        except Exception as e:
            self.safe_log(f"⚠️ 自动修复spec缩进失败: {e}")
            return False

    def _get_venv_python(self):
        """获取虚拟环境的Python路径"""
        exe_dir = get_exe_directory()
        venv_dir = os.path.join(exe_dir, "common_venv")
        if sys.platform == 'win32':
            venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(venv_dir, 'bin', 'python')
        return venv_python if os.path.exists(venv_python) else None

    def _get_venv_site_packages(self):
        """获取虚拟环境的site-packages路径"""
        exe_dir = get_exe_directory()
        venv_dir = os.path.join(exe_dir, "common_venv")
        if sys.platform == 'win32':
            venv_site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
        else:
            venv_site_packages = os.path.join(venv_dir, 'lib',
                                              f'python{sys.version_info.major}.{sys.version_info.minor}',
                                              'site-packages')
        return venv_site_packages if os.path.exists(venv_site_packages) else None

        def _generate_version_file(self, output_dir, version_info):
            """生成版本文件（不弹窗）"""
            import re
            import datetime
            try:
                os.makedirs(output_dir, exist_ok=True)
                def parse_vers(key):
                    parts = version_info.get(key, "1.0.0.0").split(".")
                    return ",".join(str(int(p)) if p.isdigit() else "0" for p in (parts + ["0"] * 4)[:4])
                product_name = version_info.get('product_name', 'MyApp')
                company = version_info.get('company', 'WCJ6376')
                internal_name = re.sub(r'[^A-Za-z0-9_]', '_', product_name)
                original_filename = f"{internal_name}.exe"
                content = f'''VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=({parse_vers("file_version")}),
        prodvers=({parse_vers("product_version")}),
        mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)
    ),
    kids=[
        StringFileInfo([
        StringTable(u'040904B0', [
            StringStruct(u'CompanyName', u'{company}'),
            StringStruct(u'FileDescription', u'{product_name}'),
            StringStruct(u'FileVersion', u'{version_info.get("file_version", "1.0.0.0")}'),
            StringStruct(u'InternalName', u'{internal_name}'),
            StringStruct(u'LegalCopyright', u'Copyright (c) {datetime.datetime.now().year} {company}'),
            StringStruct(u'OriginalFilename', u'{original_filename}'),
            StringStruct(u'ProductName', u'{product_name}'),
            StringStruct(u'ProductVersion', u'{version_info.get("product_version", "1.0.0.0")}')
        ])
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
    )'''
                version_file = os.path.join(output_dir, 'version.txt')
                with open(version_file, 'w', encoding='utf-8-sig', newline='\n') as f:
                    f.write(content)
                return version_file
            except Exception as e:
                self.safe_log(f"⚠️ 生成版本文件失败: {e}")
                return None

    def _run_build(self):
        import re
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            QMessageBox.warning(self, "警告", "请选择有效的Python脚本！")
            self._reset_build_button()
            return
        #self._install_missing_deps_only(script)
        # ===== 智能源码注入 =====
        if any(self.inject_selected.values()):
            injected, replaced_count = self._smart_inject_code_to_script(script)
            if injected:
                self._injected_this_build = True
                self.safe_log(f"💉 已注入代码，替换 {replaced_count} 处资源加载调用")
            else:
                self._injected_this_build = False
                self.safe_log("ℹ️ 无需注入（已存在类似实现或未检测到需要修改的代码）")
        else:
            self._injected_this_build = False
        proj_name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
        proj_name = re.sub(r'[\\/:*?"<>|]', '_', proj_name)
        output_path = os.path.join(self.output_dir.text(), proj_name)
        os.makedirs(output_path, exist_ok=True)
        # ===== 查找已生成的版本文件 =====
        version_file = None
        version_info = {}
        # 1. 检查项目目录下是否有 version.txt
        version_file_path = os.path.join(output_path, 'version.txt')
        if os.path.exists(version_file_path):
            version_file = version_file_path
            self.safe_log(f"📋 找到版本文件: {version_file}")
            # 尝试解析版本信息
            try:
                with open(version_file_path, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                import re
                product_name_match = re.search(r"StringStruct\(u?'ProductName', u?'([^']+)'\)", content)
                company_match = re.search(r"StringStruct\(u?'CompanyName', u?'([^']+)'\)", content)
                file_version_match = re.search(r"StringStruct\(u?'FileVersion', u?'([^']+)'\)", content)
                product_version_match = re.search(r"StringStruct\(u?'ProductVersion', u?'([^']+)'\)", content)
                if product_name_match:
                    version_info['product_name'] = product_name_match.group(1)
                if company_match:
                    version_info['company'] = company_match.group(1)
                if file_version_match:
                    version_info['file_version'] = file_version_match.group(1)
                if product_version_match:
                    version_info['product_version'] = product_version_match.group(1)
            except:
                pass
        else:
            # 2. 检查内存中是否有版本信息（用户通过版本信息对话框设置的）
            if hasattr(self, 'version_info') and self.version_info:
                version_info = self.version_info.copy()
                # 如果有版本信息但没有 version.txt，生成一个（不弹窗）
                try:
                    # 直接调用 _save_to_file 的逻辑，不创建对话框
                    version_file = self._generate_version_file(output_path, version_info)
                    if version_file:
                        self.safe_log(f"📋 已生成版本文件: {version_file}")
                except Exception as e:
                    self.safe_log(f"⚠️ 生成版本文件失败: {e}")
        packer = self.packer_combo.currentText()
        # ===== 初始化虚拟环境变量 =====
        venv_site_packages = None
        # ===== 直接使用界面选中的Python =====
        if self.use_venv:
            exe_dir = get_exe_directory()
            venv_dir = os.path.join(exe_dir, "common_venv")
            if sys.platform == 'win32':
                target_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                target_python = os.path.join(venv_dir, "bin", "python")
            if not os.path.exists(target_python):
                target_python = self.python_path.currentText()
                self.safe_log("⚠️ 虚拟环境不存在，使用界面Python")
            else:
                self.safe_log(f"🐍 使用虚拟环境Python: {target_python}")
                # 获取虚拟环境的site-packages
                if sys.platform == 'win32':
                    venv_site_packages = os.path.join(venv_dir, "Lib", "site-packages")
                else:
                    venv_site_packages = os.path.join(venv_dir, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}", "site-packages")
                if os.path.exists(venv_site_packages):
                    self.safe_log(f"📁 虚拟环境site-packages: {venv_site_packages}")
        else:
            target_python = self.python_path.currentText()
            if not target_python or not os.path.exists(target_python):
                target_python = sys.executable
            self.safe_log(f"🐍 Python: {target_python}")
        # 自定义打包器
        if packer in ["Py2exe", "Cx_Freeze", "PyOxidizer", "Pynsist", "Py2app", "PyApp"]:
            self._run_custom_packager(packer, script, output_path, proj_name)
            return
        # ===== 过滤掉标记为排除打包的文件 =====
        exclude_from_pack = getattr(self, 'exclude_from_pack', [])
        filtered_data_files = []
        for src, dst in self.data_files_list:
            if src in exclude_from_pack:
                self.safe_log(f"🚫 排除打包: {os.path.basename(src)}")
            else:
                filtered_data_files.append((src, dst))
        # ===== 读取界面最新状态 =====
        final_hidden_imports = set(self.hidden_imports_list)
        needed_packages = set(final_hidden_imports)
        # ===== 判断是否启用自动排除 =====
        auto_exclude_enabled = self.auto_exclude_cb.isChecked() if hasattr(self, 'auto_exclude_cb') else True
        if auto_exclude_enabled:
             exclude_list = self.exclude_list.copy()
             self.safe_log(f"🚫 自动排除已启用，排除 {len(exclude_list)} 个包")
        else:
            exclude_list = self.manual_exclude_list.copy()  # 仅用户手动添加
            self.safe_log(f"🚫 自动排除已禁用，仅手动排除 {len(exclude_list)} 个包")
        self.safe_log(f"📦 最终隐藏导入: {len(final_hidden_imports)} 个")
        # ===== PyInstaller spec 模式 =====
        if packer == 'PyInstaller-spec':
            project_dir = output_path
            spec_file = os.path.join(project_dir, os.path.basename(script).replace('.py', '.spec'))
            self._spec_build_dir = os.path.join(project_dir, 'build')
            self._spec_project_dir = project_dir
            os.makedirs(project_dir, exist_ok=True)
            def normalize_path(p):
                return p.replace('\\', '/') if p else p
            name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
            icon = self.icon_label.toolTip() if self.icon_label.text() else ''
            onefile = self.single_mode.isChecked()
            console = self.debug_mode.isChecked()
            upx_enabled = self.compress_combo.currentText() != '不压'
            script_path = normalize_path(script)
            icon_path = normalize_path(icon)
            datas_list = []
            for src, dst in self.data_files_list:
                src = normalize_path(src)
                datas_list.append((src, dst))
            version_file = os.path.join(project_dir, 'version.txt')
            if os.path.exists(version_file):
                version_file_path = normalize_path(version_file)
                datas_list.append((version_file_path, '.'))
                has_version = True
            else:
                has_version = False
            # spec 模式需要 pathex 指向虚拟环境
            pathex_list = []
            # 如果是虚拟环境，添加虚拟环境的 site-packages 路径
            if self.use_venv and venv_site_packages:
                pathex_list.append(normalize_path(venv_site_packages))
                # ===== 构建 datas_list =====
                datas_list = []
                for src, dst in self.data_files_list:
                    if src not in getattr(self, 'exclude_from_pack', []):
                        datas_list.append((normalize_path(src), dst))
                if sys.platform == 'win32' and self.use_venv and venv_site_packages:                
                    win32_imports = [imp for imp in self.hidden_imports_list
                                     if imp.lower().startswith('win32') or imp.lower() == 'pywin32']
                    if win32_imports:
                        # 1. pywin32_system32 基础 dll
                        system32_dir = os.path.join(venv_site_packages, 'pywin32_system32')
                        if os.path.exists(system32_dir):
                            for f in os.listdir(system32_dir):
                                if f.endswith('.dll'):
                                    src = os.path.join(system32_dir, f)
                                    if not any(src == s for s, _ in datas_list):
                                        datas_list.append((src, 'pywin32_system32'))               
                        # 2. win32 目录下只添加被导入的模块对应的 .pyd
                        win32_dir = os.path.join(venv_site_packages, 'win32')
                        if os.path.exists(win32_dir):
                            needed = set()
                            for imp in win32_imports:
                                if imp.lower() != 'pywin32':  
                                    needed.add(imp.lower() + '.pyd')
                                if imp.lower() == 'win32api':
                                    needed.add('win32api.pyd') 
                            for f in os.listdir(win32_dir):
                                if f.endswith('.pyd') and f.lower() in needed:
                                    src = os.path.join(win32_dir, f)
                                    if not any(src == s for s, _ in datas_list):
                                        datas_list.append((src, 'win32'))
                                       
            upx_flags_str = ''
            compress_level = self.compress_combo.currentText()
            if compress_level != '不压':
                if compress_level == '最快':
                    upx_flags_str = "    upx_flags=['-1'],"
                elif compress_level == '默认':
                    upx_flags_str = "    upx_flags=['-7'],"
                elif compress_level == '最好':
                    upx_flags_str = "    upx_flags=['--best'],"
                elif compress_level == '极致':
                    upx_flags_str = "    upx_flags=['--ultra-brute'],"
            strip_enabled = self.pyi_strip_cb.isChecked() if hasattr(self, 'pyi_strip_cb') else True
            spec_lines = [
                "# -*- mode: python ; coding: utf-8 -*-",
                "import sys",
                "",
                "a = Analysis(",
                f"    ['{script_path}'],",
                f"    pathex={pathex_list},",
                "    binaries=[],",
                f"    datas={datas_list},",
                f"    hiddenimports={list(final_hidden_imports)},",
                "    hookspath=[],",
                "    hooksconfig={},",
                "    runtime_hooks=[],",
                f"    excludes={exclude_list},",
                f"    strip={strip_enabled},",
                f"    upx={upx_enabled},",
                "    noarchive=False,",
                ")",
                "pyz = PYZ(a.pure, a.zipped_data)",
                "exe = EXE(",
                "    pyz,",
                "    a.scripts,",
                "    a.binaries,",
                "    a.zipfiles,",
                "    a.datas,",
                "    [],",
                f"    name='{name}',",
                f"    debug={self.debug_mode.isChecked()},",
                f"    console={console},",
                f"    upx={upx_enabled},",
            ]
            if upx_flags_str:
                spec_lines.append(f"{upx_flags_str}")
            if icon_path:
                spec_lines.append(f"    icon='{icon_path}',")
            if has_version:
                spec_lines.append("    version='version.txt',")
            spec_lines.append(")")
            if not onefile:
                spec_lines.extend([
                    "coll = COLLECT(",
                    "    exe,",
                    "    a.binaries,",
                    "    a.zipfiles,",
                    "    a.datas,",
                    f"    strip={strip_enabled},",
                    f"    upx={upx_enabled},",
                    f"    name='{name}',",
                    ")",
                ])
            spec_template = "\n".join([line for line in spec_lines if line])
            with open(spec_file, 'w', encoding='utf-8-sig') as f:
                f.write(spec_template)
            self.safe_log(f"✅ spec文件已生成: {spec_file}")
            if self.edit_spec_cb.isChecked():
                self.safe_log(f"✏️ 打开编辑器: {spec_file}")
                if sys.platform == 'win32':
                    os.startfile(spec_file)
                else:
                    self._popen_hidden(['xdg-open', spec_file])
                reply = QMessageBox.question(self, "编辑spec", "编辑完成后点击Yes继续打包")
                if reply != QMessageBox.StandardButton.Yes:
                    self._reset_build_button()
                    return
            extra_args = self.extra_args_input.text() if self.extra_args_input else ''
            config = {
                'script': spec_file,
                'output': project_dir,
                'name': name,
                'packer': 'PyInstaller-spec',
                'clean': True,
                'compress_level': self.compress_combo.currentText(),
                'upx_path': self.upx_path.text(),
                'extra_args': extra_args.split() if extra_args else [],
                'target_python': target_python,
                'venv_python': target_python if self.use_venv else None,
                'use_venv': self.use_venv,
                'venv_site_packages': venv_site_packages,
                'data_files': filtered_data_files,
                'hidden_imports': list(final_hidden_imports),
                'excludes': exclude_list,
                'strip': strip_enabled,
                'version_file': version_file,
                'version_info': version_info,
            }
            self._kill_worker()
            self.is_building = True
            self.worker = PackageWorker(config)
            self.worker.log_signal.connect(self.log_text.append_log)
            self.worker.progress_signal.connect(self._update_progress)
            self.worker.finished_signal.connect(self._on_spec_build_finished)
            self.worker.start()
            return
        # ===== PyInstaller cmd 模式和 Nuitka =====
        extra_args = self.extra_args_input.text() if self.extra_args_input else ''
        extra_args_list = extra_args.split() if extra_args else []
        # ===== 确保 extra_args_list 是列表 =====
        if extra_args_list is None:
            extra_args_list = []
        # ===== 响应文件自动启用检查（仅PyInstaller-cmd） =====
        response_file = None
        if packer == 'PyInstaller-cmd':
            # 确保变量是列表
            if exclude_list is None:
                exclude_list = []
            if final_hidden_imports is None:
                final_hidden_imports = set()
            if extra_args_list is None:
                extra_args_list = []
            exclude_count = len(exclude_list)
            hidden_count = len(final_hidden_imports)
            total_len = 0
            # 安全计算长度
            if extra_args_list:
                total_len += sum(len(str(arg)) + 1 for arg in extra_args_list if arg is not None)
            if final_hidden_imports:
                total_len += sum(len(str(mod)) + 1 for mod in final_hidden_imports if mod is not None)
            if exclude_list:
                total_len += sum(len(str(mod)) + 1 for mod in exclude_list if mod is not None)
            # 判断是否启用响应文件
            use_response = (exclude_count > 20 or total_len > 4000)
            if use_response:
                self.use_response_file_cb.setChecked(True)  # 自动勾选
            # 如果用户手动勾选，也使用
            if self.use_response_file_cb.isChecked():
                # 生成响应文件...
                response_file = os.path.join(output_path, 'pyinstaller_args.rsp')
        try:
            with open(response_file, 'w', encoding='utf-8-sig') as f:
                # ---- 辅助函数1：获取目录的短路径（不包含文件名） ----
                def get_short_dir_path(path):
                    """获取路径所在目录的短路径，保持文件名完整"""
                    if not path or sys.platform != 'win32':
                        return path
                    try:
                        import ctypes
                        dir_path = os.path.dirname(path)
                        filename = os.path.basename(path)
                        if not dir_path or not os.path.exists(dir_path):
                            return path
                        GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
                        buffer_len = GetShortPathName(dir_path, None, 0)
                        if buffer_len == 0:
                            return path
                        buffer = ctypes.create_unicode_buffer(buffer_len)
                        GetShortPathName(dir_path, buffer, buffer_len)
                        short_dir = buffer.value if buffer.value else dir_path
                        return os.path.join(short_dir, filename) if short_dir else path
                    except Exception:
                        return path
                # ---- 辅助函数2：格式化路径 ----
                def format_path(p):
                    if not p:
                        return p
                    p = str(p)
                    if ' ' in p:
                        short = get_short_dir_path(p)
                        if short and short != p:
                            return short
                    if ' ' in p and not (p.startswith('"') and p.endswith('"')):
                        return f'"{p}"'
                    return p
                # ---- 辅助函数3：格式化名称（有空格加引号） ----
                def format_name(name):
                    if not name:
                        return name
                    name = str(name)
                    if ' ' in name and not (name.startswith('"') and name.endswith('"')):
                        return f'"{name}"'
                    return name
                # ---- 辅助函数4：写参数和值（分开两行） ----
                def write_param(name, value, format_type='path'):
                    """写参数：参数名一行，值一行"""
                    if value is None or value == '':
                        return
                    f.write(f'{name}\n')
                    if format_type == 'name':
                        f.write(f'{format_name(value)}\n')
                    else:
                        f.write(f'{format_path(value)}\n')
                # ---- 辅助函数5：写无值参数（只需一行） ----
                def write_flag(name, condition):
                    if condition:
                        f.write(f'{name}\n')
                # 1. 主要参数（无值参数）
                write_flag('--onefile', self.single_mode.isChecked())
                write_flag('--onedir', not self.single_mode.isChecked())
                write_flag('--noconsole', not self.debug_mode.isChecked())
                write_flag('--console', self.debug_mode.isChecked())
                write_flag('--clean', True)
                write_flag('--strip', self.pyi_strip_cb.isChecked() if hasattr(self, 'pyi_strip_cb') else True)
                # 2. 名称（有值参数，分行写）
                if self.app_name.text():
                    write_param('--name', self.app_name.text(), 'name')
                # 3. 输出目录
                if output_path:
                    write_param('--distpath', output_path)
                # 4. 图标
                if self.icon_label.toolTip() and self.icon_label.text():
                    write_param('--icon', self.icon_label.toolTip())
                # 5. 隐藏导入（分行写）
                if final_hidden_imports:
                    for mod in final_hidden_imports:
                        if mod:
                            write_param('--hidden-import', mod)
                # 6. 排除模块（分行写）
                if exclude_list:
                    for mod in exclude_list:
                        if mod:
                            write_param('--exclude-module', mod)
                # 7. UPX
                compress_level = self.compress_combo.currentText()
                upx_path = self.upx_path.text()
                if upx_path and os.path.exists(upx_path) and compress_level != '不压':
                    upx_dir = os.path.dirname(upx_path)
                    write_param('--upx-dir', upx_dir)
                else:
                    write_flag('--noupx', True)
                # 8. 数据文件（分行写）
                sep = ';' if sys.platform == 'win32' else ':'
                if filtered_data_files:
                    for src, dst in filtered_data_files:
                        if src:
                            write_param('--add-data', f'{format_path(src)}{sep}{format_path(dst)}')
                # 9. 额外参数（分行写）
                if extra_args_list:
                    for arg in extra_args_list:
                        if arg:
                            arg_str = str(arg)
                            if ' ' in arg_str:
                                f.write(f'"{arg_str}"\n')
                            else:
                                f.write(f'{arg_str}\n')
                # 10. 脚本路径
                f.write(format_path(script) + '\n')
            self.safe_log(f"📄 响应文件已生成: {response_file}")
        except Exception as e:
            response_file = None
        # ===== 构建 config 时确保所有值都是有效类型 =====
        config = {
            'script': script,
            'output': output_path,
            'name': self.app_name.text() or os.path.splitext(os.path.basename(script))[0],
            'packer': packer,
            'onefile': self.single_mode.isChecked(),
            'debug': self.debug_mode.isChecked(),
            'clean': True,
            'strip': True,
            'icon': self.icon_label.toolTip() if self.icon_label.text() else '',
            'upx_path': self.upx_path.text() or '',
            'compress_level': self.compress_combo.currentText(),
            'platform': self.platform_combo.currentText(),
            'hidden_imports': list(final_hidden_imports) if final_hidden_imports else [],
            'excludes': exclude_list if exclude_list else [],
            'extra_args': extra_args_list if extra_args_list else [],
            'target_python': target_python,
            'data_files': filtered_data_files if filtered_data_files else [],
            'needed_packages': list(needed_packages) if needed_packages else [],
            'response_file': response_file,
            'version_file': version_file,
            'version_info': version_info,
        }
        if packer == 'Nuitka':
            jobs = self.nuitka_jobs_combo.currentText() if self.nuitka_jobs_combo else 'auto'
            max_jobs = max(1, self.cpu_count)
            if jobs != 'auto':
                try:
                    job_num = int(jobs)
                    if job_num > max_jobs:
                        self.safe_log(f"⚠️ 并行核心数从 {job_num} 限制为 {max_jobs} ")
                        job_num = max_jobs
                    final_jobs = str(job_num)
                except ValueError:
                    final_jobs = jobs
            else:
                final_jobs = str(max_jobs)
                self.safe_log(f"🔧 使用 {max_jobs}/{self.cpu_count} 个核心并行编译")
            low_memory = self.nuitka_lowmem_cb.isChecked() if self.nuitka_lowmem_cb else False
            if not low_memory and self.cpu_count >= 8:
                low_memory = True
                self.safe_log(f"🧠 自动启用低内存模式 (CPU: {self.cpu_count}核)")
            if low_memory:
                self.safe_log(f"🧠 低内存模式已启用")
            optimize = self.nuitka_optimize_combo.currentText() if hasattr(self, 'nuitka_optimize_combo') else "平衡"
            nuitka_extra_args = extra_args_list.copy() if extra_args_list else []
            if optimize == "速度优先":
                if '--no-annotations' not in nuitka_extra_args:
                    nuitka_extra_args.append('--no-annotations')
                self.safe_log("⚡ 速度优先模式：禁用注解以加快编译")
            elif optimize == "体积优先":
                if '--enable-plugin=upx' not in nuitka_extra_args:
                    nuitka_extra_args.append('--enable-plugin=upx')
                self.safe_log("📦 体积优先模式：启用UPX压缩")
            elif optimize == "极致优化":
                if '--enable-plugin=upx' not in nuitka_extra_args:
                    nuitka_extra_args.append('--enable-plugin=upx')
                if '--lto=yes' not in nuitka_extra_args:
                    nuitka_extra_args.append('--lto=yes')
                self.safe_log("🔥 极致优化模式：编译时间最长，效果最好")
            else:
                self.safe_log("⚖️ 平衡模式")
            # 使用稳定的缓存目录
            cache_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Nuitka', 'Nuitka', 'Cache')
            os.makedirs(cache_dir, exist_ok=True)
            os.environ['NUITKA_CACHE_DIR'] = cache_dir
            # ccache 也固定位置
            ccache_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Nuitka', 'Nuitka', 'ccache')
            os.makedirs(ccache_dir, exist_ok=True)
            os.environ['CCACHE_DIR'] = ccache_dir
            backend = self.nuitka_backend_combo.currentText() if self.nuitka_backend_combo else 'auto'
            mingw_path = getattr(self, '_cached_mingw_path', '')
            msvc_path = getattr(self, '_cached_msvc_path', '')
            has_mingw = getattr(self, '_cached_has_mingw', False)
            has_msvc = getattr(self, '_cached_has_msvc', False)
            if not has_mingw and not has_msvc:
                try:
                    cache_file = os.path.join(get_exe_directory(), ".global_cache.json")
                    if os.path.exists(cache_file):
                        with open(cache_file, 'r', encoding='utf-8-sig') as f:
                            cache_data = json.load(f)
                            compiler = cache_data.get('compiler', {})
                            if compiler.get('mingw', False):
                                has_mingw = True
                                mingw_path = compiler.get('mingw_path', '')
                            if compiler.get('msvc', False):
                                has_msvc = True
                                msvc_path = compiler.get('msvc_path', '')
                except Exception as e:
                    self.safe_log(f"⚠️ 读取编译器缓存失败: {e}")
            if not has_mingw and not has_msvc:
                threading.Thread(target=self._detect_compilers_async, daemon=True).start()
            #if backend in ['MinGW64', 'auto'] and has_mingw:
                #self.safe_log(f"🔧 使用 MinGW64: {mingw_path}")
            #elif backend in ['MSVC', 'auto'] and has_msvc:
                #self.safe_log(f"🔧 使用 MSVC: {msvc_path}")
            config.update({
                'jobs': final_jobs,
                'backend': backend,
                'gui_plugin': self.nuitka_gui_plugin_combo.currentText() if self.nuitka_gui_plugin_combo else 'auto',
                'lto': self.nuitka_lto_combo.currentText() if self.nuitka_lto_combo else 'no',
                'strip': self.nuitka_strip_cb.isChecked() if self.nuitka_strip_cb else True,
                'low_memory': low_memory,
                'experimental': self.nuitka_exp_cb.isChecked() if self.nuitka_exp_cb else False,
                'nuitka_compat': self.nuitka_compat_cb.isChecked() if self.nuitka_compat_cb else False,
                'mingw_path': mingw_path if has_mingw else '',
                'msvc_path': msvc_path if has_msvc else '',
                'has_mingw': has_mingw,
                'has_msvc': has_msvc,
                'extra_args': nuitka_extra_args,
                'cache_dir': cache_dir,
                'optimize': optimize,
                'version_file': version_file,
                'version_info': version_info,
                'needed_packages': list(needed_packages) if needed_packages else [],
                'disable_ccache': getattr(self, 'disable_ccache_cb', None) and self.disable_ccache_cb.isChecked() if hasattr(self, 'disable_ccache_cb') else False,
            })
        if packer == 'PyInstaller-cmd':
            config.update({
                'use_response_file': self.use_response_file_cb.isChecked() if self.use_response_file_cb else False,
                'log_level': self.pyi_log_level_combo.currentText() if self.pyi_log_level_combo else 'INFO',
                'collect': self.pyi_collect_input.text() if self.pyi_collect_input else '',
                'copy_metadata': self.pyi_metadata_input.text() if self.pyi_metadata_input else '',
            })
        try:
            self._kill_worker()
            self.is_building = True
            self.worker = PackageWorker(config)
            self.worker.log_signal.connect(self.log_text.append_log)
            self.worker.progress_signal.connect(self._update_progress)
            self.worker.finished_signal.connect(self._on_build_finished)
            self.worker.start()
        except Exception as e:
            self.safe_log(f"❌ 启动打包失败: {e}")
            self._reset_build_button()

    def _get_packer_display_name(self, packer):
        """统一打包器显示名称"""
        return "PyInstaller" if packer.startswith("PyInstaller") else packer

    def _check_packer_version(self, packer, python_exe):
        """同步检测单个打包器版本，返回版本字符串或None"""
        if not python_exe or not os.path.exists(python_exe):
            return None
        display = self._get_packer_display_name(packer)
        # ===== 打包器pip名称映射（pip show用，注意大小写）=====
        pip_map = {
            "PyInstaller": "pyinstaller",
            "Nuitka": "nuitka",
            "PyApp": "pyapp",
            "Py2exe": "py2exe",
            "Cx_Freeze": "cx_freeze",
            "Pynsist": "pynsist",
            "PyOxidizer": "pyoxidizer",
            "Py2app": "py2app",
        }
        pip_name = pip_map.get(display)
        if not pip_name:
            return None
        # ===== 方法1: pip show=====
        try:
            r = self._run_hidden(
                [python_exe, "-m", "pip", "show", pip_name],
                capture_output=True, text=True, timeout=8,
                startupinfo=get_startupinfo()
            )
            if r.returncode == 0:
                for line in r.stdout.split("\n"):
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        return version
        except Exception:
            pass
        # ===== 方法2: python -m 模块 --version =====
        module_map = {
            "PyInstaller": "pyinstaller",
            "Nuitka": "nuitka",
            "Cx_Freeze": "cx_Freeze",
            "Pynsist": "pynsist",
            "Py2app": "py2app",
            "Py2exe": "py2exe",
            "PyOxidizer": "pyoxidizer",
            "Py2app": "py2app",
        }
        mod = module_map.get(display)
        if mod:
            try:
                r = self._run_hidden(
                    [python_exe, "-m", mod, "--version"],
                    capture_output=True, text=True, timeout=8,
                    startupinfo=get_startupinfo()
                )
                out = (r.stdout or r.stderr or "").strip()
                if out:
                    import re
                    match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)?)', out)
                    if match:
                        return match.group(1)
                    parts = out.split()
                    for part in parts:
                        if re.match(r'^\d+\.\d+', part):
                            return part
            except Exception:
                pass
        # ===== 方法3: 直接命令 --version（PyOxidizer、PyApp等）=====
        if display in ("PyOxidizer", "PyApp"):
            cmd = display.lower()
            import shutil
            if shutil.which(cmd):
                try:
                    r = self._run_hidden(
                        [cmd, "--version"],
                        capture_output=True, text=True, timeout=5
                    )
                    out = (r.stdout or r.stderr or "").strip()
                    import re
                    match = re.search(r'(\d+\.\d+\.\d+(?:\.\d+)?)', out)
                    if match:
                        return match.group(1)
                except Exception:
                    pass
        return None

    def _check_current_packer(self):
        """检测当前选中的打包器版本（完全异步，不阻塞UI）"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.status_packer.setText("📦 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            return
        packer = self.packer_combo.currentText()
        self._display_packer_version_from_cache(packer)

    def _show_packer_from_cache(self):
        """从缓存显示当前打包器版本（启动时快速显示）"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            # Python路径还没加载，显示等待状态
            self.status_packer.setText("📦 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            return
        packer = self.packer_combo.currentText()
        display = self._get_packer_display_name(packer)
        cache_key = f"{display}@{python_exe}"
        # 先查内存缓存
        version = self._packer_version_cache.get(cache_key)
        # 内存没有，查文件缓存
        if version is None:
            try:
                if os.path.exists(self.global_cache_file):
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        cache_data = json.load(f)
                    packer_versions = cache_data.get('packer_versions', {})
                    version = packer_versions.get(cache_key)
                    if version:
                        # 加载到内存缓存
                        self._packer_version_cache[cache_key] = version
            except:
                pass
        if version:
            self._update_packer_status(display, version)
        else:
            # 缓存中没有，显示检测中，触发后台检测
            self.status_packer.setText(f"📦 {display}: 检测中...")
            self.status_packer.setStyleSheet("color: orange;")
            self._check_current_packer()

    def _update_packer_status(self, display, version):
        """统一更新打包器状态栏（线程安全，通过信号调用）"""
        if version and str(version).strip():
            self.status_packer.setText(f"📦 {display}: {version}")
            self.status_packer.setStyleSheet("color: green;")
            if display == "Nuitka":
                self._auto_set_nuitka_compat(version)
        else:
            self.status_packer.setText(f"📦 {display}: 未安装")
            self.status_packer.setStyleSheet("color: red;")

    def _check_current_packer_after_init(self):
        """初始化完成后检测当前打包器版本（延迟异步执行）"""
        # ===== 添加空值检查 =====
        if not hasattr(self, 'python_path') or self.python_path is None:
            QTimer.singleShot(500, self._check_current_packer_after_init)
            return
        if not hasattr(self, 'packer_combo') or self.packer_combo is None:
            QTimer.singleShot(500, self._check_current_packer_after_init)
            return
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.status_packer.setText("📦 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            QTimer.singleShot(500, self._check_current_packer_after_init)
            return
        # 直接调用 _display_packer_version_from_cache，不触发检测
        current_packer = self.packer_combo.currentText()
        self._display_packer_version_from_cache(current_packer)

    def _preload_all_packer_versions_with_cache(self):
        """后台预加载所有打包器版本，并写入文件缓存"""
        # ===== 防止重复调用 =====
        if self._packer_cache_loaded:
            return
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            return
        # ===== 如果已经检测过，不再重复 =====
        if self._packer_versions_detected:
            self._packer_cache_loaded = True
            return

        def load_all():
            updated = False
            cache_data = {}
            try:
                if os.path.exists(self.global_cache_file):
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        cache_data = json.load(f)
            except:
                pass
            if 'packer_versions' not in cache_data:
                cache_data['packer_versions'] = {}
            packers = ["PyInstaller", "Nuitka", "PyApp", "Py2exe",
                       "Cx_Freeze", "Pynsist", "PyOxidizer", "Py2app"]
            detected_count = 0
            for packer in packers:
                cache_key = f"{packer}@{python_exe}"
                if cache_key not in self._packer_versions_cache:
                    # 先检查文件缓存
                    if cache_key in cache_data['packer_versions']:
                        version = cache_data['packer_versions'][cache_key]
                        self._packer_versions_cache[cache_key] = version
                        if version:
                            detected_count += 1
                    else:
                        version = self._check_packer_version(packer, python_exe)
                        self._packer_versions_cache[cache_key] = version
                        cache_data['packer_versions'][cache_key] = version
                        updated = True
                        if version:
                            detected_count += 1
            if updated:
                try:
                    with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                except:
                    pass
            self._packer_versions_detected = True
            self._packer_cache_loaded = True  # ===== 关键：标记已加载 =====
            # 更新当前显示的打包器
            current = self.packer_combo.currentText()
            display = self._get_packer_display_name(current)
            cache_key = f"{display}@{python_exe}"
            version = self._packer_versions_cache.get(cache_key)
            if version is not None:
                QTimer.singleShot(0, lambda: self.packer_ver_signal.emit(display, version or ""))
        threading.Thread(target=load_all, daemon=True).start()

    def _on_spec_build_finished(self, success, msg):
        """spec打包完成后的回调"""
        import subprocess
        # 清理build目录
        if hasattr(self, '_spec_build_dir') and os.path.exists(self._spec_build_dir):
            try:
                shutil.rmtree(self._spec_build_dir)
                self.safe_log(f"🧹 已清理build目录")
            except Exception as e:
                self.safe_log(f"⚠️ 清理build目录失败: {e}")
        # 清理临时属性
        if hasattr(self, '_spec_project_dir'):
            delattr(self, '_spec_project_dir')
        if hasattr(self, '_spec_build_dir'):
            delattr(self, '_spec_build_dir')
        self._on_build_finished(success, msg)
        # ===== 恢复源码（仅在注入了代码时） =====
        if hasattr(self, '_injected_this_build') and self._injected_this_build:
            try:
                self._restore_original_script()
            except Exception as e:
                self.safe_log(f"⚠️ 恢复源码出错: {e}")
            finally:
                self._injected_this_build = False       

    def _update_custom_progress(self):
        """模拟进度条递增"""
        if self.custom_progress_value < 90:
            self.custom_progress_value += 5
            self.progress_bar.setValue(self.custom_progress_value)
            self.progress_label.setText(f"{self.custom_progress_value}% - 打包中...")
            QApplication.processEvents()

    def _hide_custom_progress(self):
        """隐藏进度条"""
        self.progress_container.setVisible(False)

        def _generate_text_icon(self):
            """文字生成图标"""
            try:
                from PIL import Image, ImageDraw, ImageFont
                text = self.text_input.text() or "App"
                size = (256, 256)
                # 获取颜色
                bg_color = self._get_color_from_btn(self.bg_color_btn)
                text_color = self._get_color_from_btn(self.text_color_btn)
                img = Image.new('RGBA', size, bg_color)
                draw = ImageDraw.Draw(img)
                try:
                    # 尝试加载系统字体
                    font = ImageFont.truetype("arial.ttf", 120)
                except:
                    # 降级使用默认字体
                    font = ImageFont.load_default()
                # 计算文字位置居中
                bbox = draw.textbbox((0, 0), text, font=font)
                x = (size[0] - (bbox[2] - bbox[0])) // 2
                y = (size[1] - (bbox[3] - bbox[1])) // 2
                draw.text((x, y), text, fill=text_color, font=font)
                self._save_icon(img)
            except ImportError:
                QMessageBox.warning(self, "错误", "需要安装 Pillow: pip install Pillow")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

        def _adjust_function_indent(self, func_name, offset):
            """调整单个函数的缩进"""
            if not func_name:
                QMessageBox.warning(self, "提示", "请输入函数名")
                return False
            script_path = self.input_file.text()
            if not script_path or not os.path.exists(script_path):
                #QMessageBox.warning(self, "提示", "请先选择Python脚本")
                return False
            try:
                with open(script_path, 'r', encoding='utf-8-sig') as f:
                    lines = f.readlines()
                # 备份
                backup = os.path.splitext(script_path)[0] + '.bak.py'
                if not os.path.exists(backup_path):
                    with open(backup_path, 'w', encoding='utf-8-sig') as f:
                        f.writelines(lines)
                # 查找函数
                range_info = self._find_function_range(lines, func_name)
                if not range_info:
                    QMessageBox.warning(self, "提示", f"未找到函数 '{func_name}'")
                    return False
                start, end = range_info
                new_lines = lines[:]
                for i in range(start, end + 1):
                    if lines[i].strip():
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        new_indent = max(0, current_indent + offset)
                        new_lines[i] = ' ' * new_indent + lines[i].lstrip()
                with open(script_path, 'w', encoding='utf-8-sig') as f:
                    f.writelines(new_lines)
                self.safe_log(f"✅ 已调整函数 '{func_name}' 缩进 {offset:+d} 个空格")
                show_msg(self, "完成", f"已调整函数 '{func_name}' 缩进 {offset:+d} 个空格",1)
                return True
            except Exception as e:
                self.safe_log(f"❌ 缩进调整失败: {e}")
                QMessageBox.critical(self, "错误", f"调整失败: {e}")
                return False

    def _reset_build_button(self):
        """重置打包按钮状态"""
        self.btn_build.setText("▶ 开始打包")
        self.btn_build.setStyleSheet("")
        self.is_building = False
        self.progress_container.setVisible(False)

    def _toggle_build(self):
        current = self.btn_build.text()
        if "开始" in current:
            self.btn_build.setText("⏹ 停止打包")
            self.progress_container.setVisible(True)
            self.is_building = True
            self._start_build()
        else:
            self.btn_build.setText("▶ 开始打包")
            self.progress_container.setVisible(False)
            #self.is_building = False
            self._stop_build()

    def _start_build(self):
        worker = getattr(self, 'worker', None)
        if worker is not None and worker.isRunning():
            self.safe_log("⚠️ 已有打包任务正在运行，请先点击「停止打包」后再试")
            return
        # 打包前清理内存
        import gc
        gc.collect()
        # 清空日志
        self.log_text.clear()
        self.btn_build.setText("⏹ 停止打包")
        self.btn_build.setStyleSheet("background: #d63031; color: white;")
        self.progress_container.setVisible(True)
        self.placeholder_widget.setVisible(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("")
        self.start_time = time.time()
        self.pack_start_time = time.time()
        self.time_label.setText("⏰ 00:00")
        self.time_label.setStyleSheet("font-weight: bold; color: #2ecc71; font-size: 12px;")
        QApplication.processEvents()
        self.time_timer.start(1000)
        # ========== 确保这里启动了打包 ==========
        self._run_build()

    def _run_custom_packager(self, packer, script, output_path, proj_name):
        self.log_text.clear()
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("")
        self.pack_start_time = time.time()
        self.time_label.setText("⏰ 00:00")
        self.time_label.setStyleSheet("font-weight: bold; color: #2ecc71; font-size: 12px;")
        self.time_timer.start(1000)
        self.is_building = True
        self.btn_build.setText("⏹ 停止打包")
        self.btn_build.setStyleSheet("background: #d63031; color: white;")
        QApplication.processEvents()
        success = False
        try:
            if packer == "Py2exe":
                success = self._package_py2exe(script)
            elif packer == "Cx_Freeze":
                success = self._package_cxfreeze(script)
            elif packer == "PyOxidizer":
                #success = self._package_pyoxidizer(script)
                self._package_pyoxidizer(script)
                return
            elif packer == "Pynsist":
                success = self._package_pynsist(script)
            elif packer == "Py2app":
                success = self._package_py2app(script)
            elif packer == "PyApp":
                success = self._package_pyapp(script)
        except Exception as e:
            self.safe_log(f"❌ 打包异常: {e}")
            success = False
        self.time_timer.stop()
        self.progress_bar.setValue(100)
        self.progress_label.setText("100% - 完成")
        QApplication.processEvents()
        QTimer.singleShot(1000, lambda: self.progress_container.setVisible(False))
        self.is_building = False
        self.btn_build.setText("▶ 开始打包")
        self.btn_build.setStyleSheet("")
        if success:
            self.safe_log("✅ 打包完成！")
        else:
            self.safe_log("❌ 打包失败")

    def _kill_worker(self):
        """【修复】彻底终止正在运行的打包 worker 及其子进程树
        根因：原 _stop_build 只重置按钮，未杀掉后台 PyInstaller 子进程。
        用户点\"停止\"后旧进程仍在跑；再点\"开始\"会起新进程，
        多个 PyInstaller 共享同一 --workpath + --clean，互相 rmtree
        导致 base_library.zip 目录被删、FileNotFoundError。
        """
        worker = getattr(self, 'worker', None)
        if worker is None:
            return
        try:
            worker._is_running = False
        except Exception:
            pass
        proc = getattr(worker, 'process', None)
        if proc is not None:
            pid = None
            try:
                pid = proc.pid
            except Exception:
                pid = None
            # Windows 下用 taskkill 杀掉整个进程树（PyInstaller 会派生子进程）
            if pid is not None and sys.platform == 'win32':
                try:
                    subprocess.run(
                        ['taskkill', '/PID', str(pid), '/T', '/F'],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                except Exception:
                    pass
            # 兜底：直接 terminate / kill
            try:
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        # 断开信号，避免日志刷屏
        try:
            worker.log_signal.disconnect()
            worker.progress_signal.disconnect()
            worker.finished_signal.disconnect()
        except Exception:
            pass
        # 结束 worker 线程
        try:
            worker.quit()
            worker.wait(2000)
        except Exception:
            pass
        try:
            worker.terminate()
            worker.wait(1000)
        except Exception:
            pass
        self.worker = None

    def _stop_build(self):
        self.time_timer.stop()
        self.pack_start_time = None
        self._kill_worker()
        self.btn_build.setText("▶ 开始打包")
        self.btn_build.setStyleSheet("")
        self.progress_container.setVisible(False)
        self.is_building = False
        # ===== 恢复源码（仅当本次注入了代码） =====
        if self._injected_this_build:
            self._restore_original_script()
            self._injected_this_build = False     

    def _build_finished(self):
        """打包完成回调"""
        self.btn_build.setText("▶ 开始打包")
        self.btn_build.setStyleSheet("")
        self.progress_container.setVisible(False)
        # ===== 恢复源码（仅当本次注入了代码） =====
        if self._injected_this_build:
            self._restore_original_script()
            self._injected_this_build = False

    def _update_drop_highlight(self):
        """计算 r1-r4 的实际位置"""
        central = self.centralWidget()
        # r1 的顶部 = contents margin top = 8
        # r4 的底部 = r1.y + r1.height + spacing + r2.height + spacing + r3.height + spacing + r4.height
        # 更简单：用 mapTo 算
        y1 = self.input_file.mapTo(central, self.input_file.rect().topLeft()).y() - 6  # 留边距
        y4 = self.python_path.mapTo(central, self.python_path.rect().bottomRight()).y() + 6
        self.drop_highlight.setGeometry(4, y1, central.width() - 8, y4 - y1)

    def _central_drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._update_drop_highlight()
            self.drop_highlight.setVisible(True)

    def _central_drag_leave(self, event):
        self.drop_highlight.setVisible(False)

    def _central_drop(self, event):
        self.drop_highlight.setVisible(False)
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        for path in paths:
            path = os.path.normpath(path)
            fixed_path = self._auto_fix_filename_spaces(path)
            if not fixed_path or not os.path.exists(fixed_path):
                continue
            path = fixed_path
            if os.path.isfile(path) and path.endswith('.py'):
                self.input_file.setText(path)
                base = os.path.splitext(os.path.basename(path))[0]
                self.app_name.setText(base)
                # ===== 【修复】清空所有列表（包括排除列表） =====
                self.hidden_imports_list.clear()
                self.hidden_listbox.clear()
                self.exclude_list.clear()
                self.exclude_listbox.clear()
                self.data_files_list.clear()
                self.data_listbox.clear()
                self._update_data_count()
                self._update_hidden_count()
                self._update_exclude_count()
                # ============================================
                # 重新分析依赖
                self._analyze_used(path, auto_add=True)
                self._update_hidden_count()
                self._update_auto_import_count()
                # 创建项目子目录
                proj_name = re.sub(r'[\\/:*?"<>|]', '_', base)
                script_dir = os.path.dirname(path)
                dist_dir = os.path.join(script_dir, "dist")
                output_path = os.path.join(dist_dir, proj_name)
                os.makedirs(output_path, exist_ok=True)
                self.output_dir.setText(dist_dir)
                if hasattr(self, 'version_info') and self.version_info:
                    self.version_info["product_name"] = base
                QTimer.singleShot(10, lambda p=path: self._detect_gui_from_hidden())
                self.safe_log(f"📄 文件: {path}")
                self._auto_load_tool_icon(path, base)
                self._auto_create_venv_for_script(path)
            elif os.path.isdir(path):
                py_files = [f for f in os.listdir(path) if f.endswith('.py')]
                if not py_files:
                    self.safe_log("⚠️ 文件夹内没有 .py 文件")
                    continue
                candidates = ['main.py', 'app.py', 'run.py', 'start.py', 'index.py',
                              'manage.py', 'server.py', 'entry.py', 'cli.py', '__main__.py']
                main_file = None
                for cand in candidates:
                    if cand in py_files:
                        main_file = os.path.join(path, cand)
                        break
                if not main_file:
                    from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
                    dialog = QDialog(self)
                    dialog.setWindowTitle("选择入口文件")
                    dialog.setModal(True)
                    layout = QVBoxLayout(dialog)
                    layout.addWidget(QLabel("请选择入口文件:"))
                    list_widget = QListWidget()
                    for f in py_files:
                        list_widget.addItem(f)
                    list_widget.setCurrentRow(0)
                    layout.addWidget(list_widget)
                    btn_layout = QHBoxLayout()
                    btn_ok = QPushButton("确定")
                    btn_cancel = QPushButton("取消")
                    btn_layout.addStretch()
                    btn_layout.addWidget(btn_ok)
                    btn_layout.addWidget(btn_cancel)
                    layout.addLayout(btn_layout)
                    selected_file = None
                    def on_ok():
                        nonlocal selected_file
                        if list_widget.currentItem():
                            selected_file = list_widget.currentItem().text()
                        dialog.accept()
                    def on_cancel():
                        dialog.reject()
                    btn_ok.clicked.connect(on_ok)
                    btn_cancel.clicked.connect(on_cancel)
                    if dialog.exec() == QDialog.DialogCode.Accepted and selected_file:
                        main_file = os.path.join(path, selected_file)
                    else:
                        continue
                if not main_file:
                    continue
                self.input_file.setText(main_file)
                base = os.path.splitext(os.path.basename(main_file))[0]
                self.app_name.setText(base)
                # 创建项目子目录
                proj_name = re.sub(r'[\\/:*?"<>|]', '_', base)
                dist_dir = os.path.join(path, "dist")
                output_path = os.path.join(dist_dir, proj_name)
                os.makedirs(output_path, exist_ok=True)
                self.output_dir.setText(dist_dir)
                self.safe_log(f"📁 项目: {path}")
                self.safe_log(f"🎯 主文件: {os.path.basename(main_file)}")
                # 清空之前的列表
                self.hidden_imports_list.clear()
                self.hidden_listbox.clear()
                self.data_files_list.clear()
                self.data_listbox.clear()
                self._update_data_count()
                self._update_hidden_count()
                # 自动分析并导入
                self._analyze_used(main_file, auto_add=True)
                self._update_hidden_count()
                self._update_auto_import_count()
                # ===== 检测GUI =====
                QTimer.singleShot(10, lambda p=main_file: self._detect_gui_from_hidden())
                # ==================
                self._auto_load_tool_icon(main_file, base)
                self._auto_create_venv_for_script(main_file)
        event.acceptProposedAction()

    def _refresh_temp_path(self):
        """刷新临时PATH"""
        if hasattr(self, '_temp_path_setup_done'):
            self._temp_path_setup_done = False
        # 重新设置
        self._setup_temp_path()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'drop_highlight') and self.drop_highlight.isVisible():
            self._update_drop_highlight()

    def _setup_packer_panel(self, main_layout):
        """设置打包器选项面板 - 延迟创建"""
        self.packer_opt_row = QWidget()
        pol = QHBoxLayout(self.packer_opt_row)
        pol.setContentsMargins(0, 0, 0, 0)
        pol.setSpacing(4)
        # ===== 只创建占位标签，不创建具体控件 =====
        self._packer_panel_initialized = False
        self._packer_panel_layout = pol
        self._packer_panel_main_layout = main_layout
        placeholder = QLabel("打包器选项（切换Nuitka/PyInstaller时加载）")
        placeholder.setStyleSheet("color: gray; font-size: 9px;")
        pol.addWidget(placeholder)
        pol.addStretch()
        main_layout.addWidget(self.packer_opt_row)
        self.packer_opt_row.setVisible(False)
        self.packer_combo.currentTextChanged.connect(self._update_packer_ui)

    def _init_packer_panel_controls(self):
        """延迟初始化打包器面板控件（首次显示时）"""
        if getattr(self, '_packer_panel_initialized', False):
            return
        pol = self._packer_panel_layout
        while pol.count():
            item = pol.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.nuitka_jobs_combo = QComboBox()
        self.nuitka_jobs_combo.addItems(self.job_options)
        default_jobs = str(max(1, self.cpu_count - 1))
        idx = self.nuitka_jobs_combo.findText(default_jobs)
        if idx >= 0:
            self.nuitka_jobs_combo.setCurrentIndex(idx)
        else:
            idx = self.nuitka_jobs_combo.findText("auto")
            if idx >= 0:
                self.nuitka_jobs_combo.setCurrentIndex(idx)
        self.nuitka_backend_combo = QComboBox()
        self.nuitka_backend_combo.addItems(["auto", "MinGW64", "MSVC"])
        self.backend_display_label = QLabel("")
        self.backend_display_label.setStyleSheet("color: #666; font-size: 9px;")
        self.nuitka_backend_combo.currentTextChanged.connect(self._update_backend_display)
        self.nuitka_backend_combo.currentTextChanged.connect(self._on_backend_changed)
        self.compiler_label = QLabel("")
        self.nuitka_gui_plugin_combo = QComboBox()
        self.nuitka_gui_plugin_combo.addItems(
            ["auto", "tk-inter", "pyqt5", "pyqt6", "pyside2", "pyside6", "wxpython", "kivy"])
        self.nuitka_gui_plugin_combo.currentTextChanged.connect(self._update_gui_display)
        self.gui_display_label = QLabel("")
        self.gui_display_label.setStyleSheet("color: #666; font-size: 9px;")
        self.gui_detect_label = QLabel("")
        self.nuitka_lto_combo = QComboBox()
        self.nuitka_lto_combo.addItems(["no", "yes", "thin"])
        self.nuitka_compat_cb = QCheckBox("4.X兼容")
        self.nuitka_strip_cb = QCheckBox("去符号")
        self.nuitka_strip_cb.setChecked(True)
        self.nuitka_exp_cb = QCheckBox("实验性")
        self.nuitka_lowmem_cb = QCheckBox("低内存")
        self.nuitka_optimize_combo = QComboBox()
        self.nuitka_optimize_combo.addItems(["平衡", "速度优先", "体积优先", "极致优化"])
        self.nuitka_optimize_combo.setCurrentText("平衡")
        self.nuitka_optimize_combo.setToolTip("编译优化策略：速度优先可加快编译，体积优先可减小exe大小")
        self.nuitka_widgets = [
            QLabel("并行:"), self.nuitka_jobs_combo, QLabel(f"(CPU {self.cpu_count} 核)"),
            QLabel("后端:"), self.nuitka_backend_combo, self.backend_display_label, self.compiler_label,
            QLabel("GUI插件:"), self.nuitka_gui_plugin_combo, self.gui_display_label, self.gui_detect_label,
            QLabel("LTO:"), self.nuitka_lto_combo,
            QLabel("优化:"), self.nuitka_optimize_combo,
            self.nuitka_compat_cb, self.nuitka_strip_cb, self.nuitka_exp_cb, self.nuitka_lowmem_cb,
        ]
        for w in self.nuitka_widgets:
            w.setVisible(False)
            pol.addWidget(w)
        self.btn_hooks = EmojiButton("🪝 钩子管理")
        self.btn_hooks.clicked.connect(self._open_hook_manager)
        self.btn_edit_spec = EmojiButton("✏️ 编辑spec")
        self.btn_edit_spec.clicked.connect(self._edit_spec_file)
        self.edit_spec_cb = QCheckBox("是否编辑spec")
        self.edit_spec_cb.setChecked(False)
        self.pyi_strip_cb = QCheckBox("去除符号")
        self.pyi_strip_cb.setChecked(True)
        self.pyi_base_widgets = [
            self.btn_hooks, self.btn_edit_spec, self.edit_spec_cb, self.pyi_strip_cb,
        ]
        for w in self.pyi_base_widgets:
            w.setVisible(False)
            pol.addWidget(w)
        self.use_response_file_cb = QCheckBox("响应文件")
        self.pyi_log_level_combo = QComboBox()
        self.pyi_log_level_combo.addItems(["DEBUG", "INFO", "WARN", "ERROR"])
        self.pyi_collect_input = QLineEdit()
        self.pyi_collect_input.setPlaceholderText("--collect-all")
        self.pyi_collect_input.setMaximumWidth(80)
        self.pyi_metadata_input = QLineEdit()
        self.pyi_metadata_input.setPlaceholderText("--copy-metadata")
        self.pyi_metadata_input.setMaximumWidth(80)
        self.extra_args_input = QLineEdit()
        self.extra_args_input.setPlaceholderText("自定义额外参数")
        self.extra_args_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.pyi_cmd_widgets = [
            self.use_response_file_cb,
            QLabel("日志:"), self.pyi_log_level_combo,
            QLabel("收集:"), self.pyi_collect_input,
            QLabel("元数据:"), self.pyi_metadata_input,
            QLabel("额外参数:"), self.extra_args_input,
        ]
        for w in self.pyi_cmd_widgets:
            w.setVisible(False)
            pol.addWidget(w)
        pol.addStretch()
        self.nuitka_backend_combo.currentTextChanged.connect(self._save_backend_to_cache)
        self._packer_panel_initialized = True

    def _update_gui_display(self, text):
        """更新GUI插件显示"""
        if text == "auto":
            # 从 hidden_imports_list 检测
            detected = None
            if hasattr(self, 'hidden_imports_list') and self.hidden_imports_list:
                imports_lower = {m.lower() for m in self.hidden_imports_list}
                if 'pyqt6' in imports_lower:
                    detected = 'pyqt6'
                elif 'pyqt5' in imports_lower:
                    detected = 'pyqt5'
                elif 'pyside6' in imports_lower:
                    detected = 'pyside6'
                elif 'pyside2' in imports_lower:
                    detected = 'pyside2'
                elif 'tkinter' in imports_lower or 'tk' in imports_lower:
                    detected = 'tk-inter'
                elif 'wx' in imports_lower:
                    detected = 'wxpython'
                elif 'kivy' in imports_lower:
                    detected = 'kivy'
            if detected:
                self.nuitka_gui_plugin_combo.blockSignals(True)
                self.nuitka_gui_plugin_combo.setCurrentText(detected)
                self.nuitka_gui_plugin_combo.blockSignals(False)
                self.gui_display_label.setText(f"✅ {detected}")
                self.gui_display_label.setStyleSheet("color: green; font-size: 9px;")
            else:
                self.gui_display_label.setText("✗ 未检测到")
                self.gui_display_label.setStyleSheet("color: orange; font-size: 9px;")
        else:
            self.gui_display_label.setText(f"✅ {text}")
            self.gui_display_label.setStyleSheet("color: #2196F3; font-size: 9px;")

    def _on_gui_plugin_changed(self, text):
        """GUI插件选择变化处理"""
        if text == "auto":
            self.gui_display_label.setText("⏳ 检测中...")
            self.gui_display_label.setStyleSheet("color: orange; font-size: 9px;")
            QTimer.singleShot(50, self._update_gui_display_from_hidden)
        else:
            self.gui_display_label.setText(f"✅ {text}")
            self.gui_display_label.setStyleSheet("color: #2196F3; font-size: 9px;")

    def _update_backend_display(self, text):
        """更新后端显示"""
        if text == "auto":
            # 显示实际检测到的编译器
            if self._cached_has_mingw:
                self.backend_display_label.setText("✅ MinGW64")
                self.backend_display_label.setStyleSheet("color: green; font-size: 9px;")
            elif self._cached_has_msvc:
                self.backend_display_label.setText("✅ MSVC")
                self.backend_display_label.setStyleSheet("color: green; font-size: 9px;")
            else:
                self.backend_display_label.setText("✗ 无")
                self.backend_display_label.setStyleSheet("color: orange; font-size: 9px;")
        else:
            self.backend_display_label.setText(f"✅ {text}")
            self.backend_display_label.setStyleSheet("color: #2196F3; font-size: 9px;")

    def _package_py2exe(self, input_file):
        """使用 py2exe 打包"""
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        base_output_dir = self.output_dir.text()
        project_output_dir = os.path.join(base_output_dir, output_name.replace(" ", "_"))
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")
        # ===== 您原来的 setup.py =====
        setup_lines = [
            "# -*- coding: utf-8 -*-",
            "from distutils.core import setup",
            "import py2exe",
            "",
            "setup(",
            f"    console=[{{'script': '{os.path.basename(input_file)}'}}],",
            "    options={'py2exe': {",
            "        'compressed': True,",
            "        'optimize': 2,",
            "        'bundle_files': 3,",
            f"        'includes': {self.hidden_imports_list},",
            f"        'excludes': {self.exclude_list}",
            "    }},",
            "    zipfile=None",
            ")",
        ]
        setup_content = "\n".join(setup_lines)
        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)
        shutil.copy2(input_file, project_output_dir)
        cmd = [python_cmd, "-u", "setup.py", "py2exe"]
        self.safe_log(f"🚀 开始 py2exe 打包...")
        self.safe_log(f"📝 命令: {' '.join(cmd)}")
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"
            process = self._popen_hidden(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                cwd=project_output_dir,
                env=env,
            )
            for line in iter(process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.rstrip())
                    QApplication.processEvents()
            process.wait()
            success = process.returncode == 0
            if success:
                dist_dir = os.path.join(project_output_dir, "dist")
                if os.path.exists(dist_dir):
                    for item in os.listdir(dist_dir):
                        src = os.path.join(dist_dir, item)
                        dst = os.path.join(project_output_dir, item)
                        if os.path.isdir(src):
                            if os.path.exists(dst):
                                shutil.rmtree(dst)
                            shutil.copytree(src, dst)
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

    def _package_cxfreeze(self, input_file):
        """使用 cx_Freeze 打包"""
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        base_output_dir = self.output_dir.text()
        project_output_dir = os.path.join(base_output_dir, output_name.replace(" ", "_"))
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")
        icon_file = self.icon_label.toolTip() if self.icon_label.text() else ""
        icon_param = ""
        if icon_file and os.path.exists(icon_file):
            icon_filename = os.path.basename(icon_file)
            shutil.copy2(icon_file, project_output_dir)
            icon_param = f', icon="{icon_filename}"'
        # ===== 您原来的 setup.py =====
        setup_lines = [
            "# -*- coding: utf-8 -*-",
            "from cx_Freeze import setup, Executable",
            "import sys, os",
            "",
            "build_exe_options = {",
            '    "packages": ["os", "sys"],',
            f"    'excludes': {self.exclude_list},",
            '    "include_files": [],',
            '    "optimize": 2,',
            "}",
            "",
            "base = None",
            "",
            "setup(",
            f'    name="{output_name}",',
            '    version="1.0",',
            '    description="打包程序",',
            '    options={"build_exe": build_exe_options},',
            "    executables=[Executable(",
            f'        "{os.path.basename(input_file)}",',
            "        base=base,",
            f'        target_name="{output_name}.exe"{icon_param}',
            "    )]",
            ")",
        ]
        setup_content = "\n".join(setup_lines)
        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)
        shutil.copy2(input_file, project_output_dir)
        if icon_file and os.path.exists(icon_file):
            shutil.copy2(icon_file, project_output_dir)
        cmd = [python_cmd, "setup.py", "build_exe"]
        self.safe_log("🚀 开始 cx_Freeze 打包...")
        try:
            startupinfo = get_startupinfo()
            self.process = self._popen_hidden(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                if self.btn_build.text() == "▶ 开始打包" and self.process.poll() is None:
                    self.process.terminate()
                    break
            self.process.wait()
            success = self.process.returncode == 0
            if success:
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

    def _download_pyoxidizer_dist(self, dist_name, cache_dir):
        """从国内镜像下载 PyOxidizer 发行版"""
        import urllib.request
        # ===== 国内镜像列表 =====
        mirrors = [
            # 清华镜像
            f"https://mirrors.tuna.tsinghua.edu.cn/github-release/indygreg/python-build-standalone/20221220/{dist_name}",
            # 中科大镜像
            f"https://mirrors.ustc.edu.cn/github-release/indygreg/python-build-standalone/20221220/{dist_name}",
            # 阿里云镜像（GitHub 代理）
            f"https://ghproxy.com/https://github.com/indygreg/python-build-standalone/releases/download/20221220/{dist_name}",
            # 原生 GitHub（最后尝试）
            f"https://github.com/indygreg/python-build-standalone/releases/download/20221220/{dist_name}",
        ]
        os.makedirs(cache_dir, exist_ok=True)
        dist_path = os.path.join(cache_dir, dist_name)

        def report_hook(block_num, block_size, total_size):
            """下载进度回调"""
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, int(downloaded * 100 / total_size))
                self.safe_log(f"📥 下载进度: {percent}%")
                self.progress_bar.setValue(5 + int(percent * 0.3))
                self.progress_label.setText(f"{5 + int(percent * 0.3)}% - 下载中...")
                QApplication.processEvents()
        for url in mirrors:
            try:
                self.safe_log(f"📥 尝试下载: {url}")
                urllib.request.urlretrieve(url, dist_path, report_hook)
                if os.path.exists(dist_path) and os.path.getsize(dist_path) > 0:
                    self.safe_log(f"✅ 下载成功: {dist_path}")
                    return dist_path
            except Exception as e:
                self.safe_log(f"⚠️ 下载失败: {e}")
                continue
        return None

    def _package_pyoxidizer(self, input_file):
        """使用 PyOxidizer 打包"""
        import shutil
        import glob
        # ===== 获取 Python 路径 =====
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        # ===== 清理残留进程和锁 =====
        try:
            if sys.platform == 'win32':
                self._run_hidden(['taskkill', '/f', '/im', 'cargo.exe'], capture_output=True)
                self._run_hidden(['taskkill', '/f', '/im', 'rustc.exe'], capture_output=True)
                self.safe_log("🧹 已清理 cargo/rustc 进程")
        except:
            pass
        # 清理系统 cargo 缓存锁
        cargo_home = os.path.expanduser(r"~\.cargo")
        for lock_name in [".package-cache", ".package-cache-mutate"]:
            lock_path = os.path.join(cargo_home, lock_name)
            if os.path.exists(lock_path):
                try:
                    os.remove(lock_path)
                except:
                    pass
        self.safe_log("=" * 50)
        self.safe_log("📦 PyOxidizer 打包模式")
        # ===== 准备目录 =====
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        out_dir = os.path.join(self.output_dir.text(), output_name.replace(" ", "_"))
        os.makedirs(out_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {out_dir}")
        # ===== 确定入口模块 =====
        if os.path.isdir(input_file):
            entry_file = self._find_entry(input_file)
        else:
            entry_file = input_file
        if not entry_file or not os.path.exists(entry_file):
            self.safe_log("❌ 入口文件不存在")
            return False
        module_name = os.path.splitext(os.path.basename(entry_file))[0]
        self.safe_log(f"📄 入口模块: {module_name}")
        # ===== 找 standalone 发行版 =====
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
        cache_dir = os.path.join(base, "pyoxidizer_cache")
        dist_name = "cpython-3.10.9+20221220-x86_64-pc-windows-msvc-shared-pgo-full.tar.zst"
        sha256 = "9902a5cb5c3b8eb13fb49e8804d16929161c38aa6d64f004d2317ca7c37a06cb"
        dist_path = None
        for fp in glob.glob(os.path.join(base, "*.tar.zst")):
            n = os.path.basename(fp)
            if "msvc" in n:
                dist_path = fp
                break
        if not dist_path:
            p = os.path.join(cache_dir, dist_name)
            if os.path.exists(p):
                dist_path = p
        if not dist_path:
            self.safe_log("⚠️ 未找到 MSVC standalone 发行版")
            QMessageBox.warning(self, "错误", f"请确保 {cache_dir}\\{dist_name} 存在")
            return False
        self.safe_log(f"✅ 发行版: {dist_path}")
        # ===== 配置 Cargo 镜像 =====
        cargo_home = os.path.expanduser(r"~\.cargo")
        os.makedirs(cargo_home, exist_ok=True)
        # 删除旧配置，避免冲突
        old_config = os.path.join(cargo_home, "config")
        if os.path.exists(old_config):
            try:
                os.remove(old_config)
                self.safe_log("🧹 已删除旧版 Cargo config")
            except:
                pass
        config_path = os.path.join(cargo_home, "config.toml")
        # 使用 USTC sparse 镜像
        config_lines = [
            "[source.crates-io]",
            'replace-with = "ustc"',
            "",
            "[source.ustc]",
            'registry = "sparse+https://mirrors.ustc.edu.cn/crates.io-index/"',
            "",
            "[net]",
            "git-fetch-with-cli = true",
            "retry = 3",
        ]
        config_content = "\n".join(config_lines) + "\n"
        # 强制写入配置
        try:
            with open(config_path, 'w', encoding='utf-8-sig') as f:
                f.write(config_content)
            self.safe_log("📁 已配置 USTC sparse 镜像")
        except Exception as e:
            self.safe_log(f"⚠️ 写入 Cargo 配置失败: {e}")
        # ===== 查找系统 Rust 工具链 =====
        rustup_home = os.path.expanduser(r"~\.rustup")
        cargo_bin = os.path.join(rustup_home, r"toolchains\stable-x86_64-pc-windows-msvc\bin\cargo.exe")
        rustc_bin = os.path.join(rustup_home, r"toolchains\stable-x86_64-pc-windows-msvc\bin\rustc.exe")
        if not os.path.exists(cargo_bin):
            toolchain_dir = os.path.join(rustup_home, r"toolchains")
            if os.path.exists(toolchain_dir):
                for tc in os.listdir(toolchain_dir):
                    if "x86_64-pc-windows-msvc" in tc:
                        c = os.path.join(toolchain_dir, tc, "bin", "cargo.exe")
                        r = os.path.join(toolchain_dir, tc, "bin", "rustc.exe")
                        if os.path.exists(c) and os.path.exists(r):
                            cargo_bin = c
                            rustc_bin = r
                            self.safe_log(f"🔧 使用 Rust 工具链: {tc}")
                            break
        if os.path.exists(cargo_bin):
            self.safe_log(f"✅ 系统 Cargo: {cargo_bin}")
            self.safe_log(f"✅ 系统 Rustc: {rustc_bin}")
        else:
            self.safe_log("⚠️ 未找到系统 Rust，将使用 PyOxidizer 内置版本")
        # ===== 生成 pyoxidizer.bzl =====
        bzl_lines = [
            'def make_exe():',
            '    dist = PythonDistribution(',
            f'        local_path=r"{dist_path}",',
            f'        sha256="{sha256}",',
            '        flavor="standalone"',
            '    )',
            '    policy = dist.make_python_packaging_policy()',
            '    policy.resources_location = "in-memory"',
            '    policy.resources_location_fallback = "filesystem-relative:prefix"',
            '    policy.extension_module_filter = "all"',
            '    policy.include_distribution_sources = True',
            '    policy.include_test = False',
            '    python_config = dist.make_python_interpreter_config()',
            f'    python_config.run_module = "{module_name}"',
            '    exe = dist.to_python_executable(',
            f'        name="{output_name}",',
            '        packaging_policy=policy,',
            '        config=python_config,',
            '    )',
            f'    exe.add_python_resources(exe.read_package_root(path=r"{out_dir}", packages=["{module_name}"]))',
            '    return exe',
            '',
            'def make_embedded_resources(exe):',
            '    return exe.to_embedded_resources()',
            '',
            'def make_install(exe):',
            '    files = FileManifest()',
            '    files.add_python_resource(".", exe)',
            '    return files',
            '',
            'register_target("exe", make_exe)',
            'register_target("resources", make_embedded_resources, depends=["exe"], default_build_script=True)',
            'register_target("install", make_install, depends=["exe"], default=True)',
            'resolve_targets()',
        ]
        with open(os.path.join(out_dir, "pyoxidizer.bzl"), "w", encoding="utf-8") as f:
            f.write("\n".join(bzl_lines))
        # ===== 复制源文件 =====
        module_dir = os.path.join(out_dir, module_name)
        os.makedirs(module_dir, exist_ok=True)
        shutil.copy2(entry_file, os.path.join(module_dir, "__init__.py"))
        shutil.copy2(entry_file, os.path.join(module_dir, "__main__.py"))
        for src, dst in self.data_files_list:
            if os.path.exists(src):
                dst_path = os.path.join(out_dir, dst)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src, dst_path)
                self.safe_log(f"📁 复制数据文件: {os.path.basename(src)} -> {dst}")
        icon_path = self.icon_label.toolTip() if hasattr(self, 'icon_label') else ""
        if icon_path and os.path.exists(icon_path):
            shutil.copy2(icon_path, out_dir)
        # ===== 查找 pyoxidizer =====
        pyoxidizer = shutil.which("pyoxidizer")
        if not pyoxidizer:
            self.safe_log("❌ 未找到 pyoxidizer")
            self.safe_log("💡 请安装: pip install pyoxidizer")
            QMessageBox.warning(self, "错误", "未找到 PyOxidizer\n请安装: pip install pyoxidizer")
            return False
        if pyoxidizer.lower().endswith('.exe'):
            pyoxidizer = pyoxidizer[:-4] + '.exe'
        self.safe_log(f"✅ 找到 PyOxidizer: {pyoxidizer}")
        # ===== 构建环境变量 =====
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["CARGO_HOME"] = cargo_home
        if os.path.exists(cargo_bin):
            env["CARGO"] = cargo_bin
            env["RUSTC"] = rustc_bin
            env["RUSTUP_TOOLCHAIN"] = "stable"
            env["PYOXIDIZER_SYSTEM_RUST"] = "1"
        # ===== 关键修复：先运行 pyoxidizer 生成 Cargo.toml，然后修补 edition 字段 =====
        self.safe_log("🚀 开始 PyOxidizer 编译（后台运行）...")
        self.progress_bar.setValue(25)
        self.progress_label.setText("25% - 生成项目文件...")
        QApplication.processEvents()
        # 先执行 pyoxidizer build 生成项目文件（可能会失败，但我们只关心生成的文件）
        # 或者使用 pyoxidizer generate 来生成项目文件
        try:
            # 尝试生成项目文件
            gen_cmd = [pyoxidizer, "generate", "--path", out_dir]
            gen_process = self._popen_hidden(
                gen_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                cwd=out_dir,
                env=env,
            )
            gen_output, _ = gen_process.communicate(timeout=30)
            if gen_output:
                self.safe_log(gen_output)
        except Exception as e:
            self.safe_log(f"⚠️ 生成项目文件时出错（可能已存在）: {e}")
        # 查找并修复 Cargo.toml
        cargo_toml_paths = [
            os.path.join(out_dir, "Cargo.toml"),
            os.path.join(out_dir, "test1", "Cargo.toml"),
            os.path.join(out_dir, output_name, "Cargo.toml"),
        ]
        # 也搜索临时目录
        temp_dir = os.environ.get('TEMP', os.environ.get('TMP', ''))
        if temp_dir:
            for root, dirs, files in os.walk(temp_dir):
                if "pyoxidizer" in root and "Cargo.toml" in files:
                    cargo_toml_paths.append(os.path.join(root, "Cargo.toml"))
                # 限制搜索深度
                if root.count(os.sep) > temp_dir.count(os.sep) + 3:
                    break
        for cargo_toml in cargo_toml_paths:
            if os.path.exists(cargo_toml):
                self._fix_cargo_toml_edition(cargo_toml)
        # ===== 使用 QThread 执行实际构建 =====
        config = {
            'pyoxidizer': pyoxidizer,
            'out_dir': out_dir,
            'output_name': output_name,
            'env': env,
        }
        self.pyoxidizer_worker = PyOxidizerWorker(config)
        self.pyoxidizer_worker.log_signal.connect(self.safe_log)
        self.pyoxidizer_worker.progress_signal.connect(self.progress_bar.setValue)
        self.pyoxidizer_worker.progress_text_signal.connect(self.progress_label.setText)
        self.pyoxidizer_worker.finished_signal.connect(self._on_pyoxidizer_finished)
        self.pyoxidizer_worker.start()
        return True

    def _fix_cargo_toml_edition(self, cargo_toml_path):
        """修复 Cargo.toml 中的 edition 字段兼容性问题"""
        try:
            with open(cargo_toml_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            original = content
            # 修复各种 edition 格式问题
            # 1. edition = 2018 (数字) -> edition = "2018" (字符串)
            import re
            # 匹配 edition = 2018 或 edition = 2021 (没有引号的数字)
            content = re.sub(r'edition\s*=\s*(\d{4})\s*$', r'edition = "\1"', content, flags=re.MULTILINE)
            # 匹配 edition = 2018 (行内，后面有逗号)
            content = re.sub(r'edition\s*=\s*(\d{4})\s*,', r'edition = "\1",', content)
            # 匹配 edition = { workspace = true } 等复杂情况（如果存在）
            # 确保 edition 是字符串或有效的继承格式
            if content != original:
                with open(cargo_toml_path, 'w', encoding='utf-8-sig') as f:
                    f.write(content)
                self.safe_log(f"🔧 已修复 Cargo.toml edition 字段: {cargo_toml_path}")
                return True
            else:
                # 检查是否已经是正确的格式
                if 'edition = "2018"' in content or 'edition = "2021"' in content:
                    self.safe_log(f"✅ Cargo.toml edition 字段格式正确")
                    return True
                return False
        except Exception as e:
            self.safe_log(f"⚠️ 修复 Cargo.toml 失败: {e}")
            return False

    def _on_pyoxidizer_finished(self, success):
        """PyOxidizer 完成回调"""
        # 停止计时器
        if hasattr(self, 'time_timer') and self.time_timer.isActive():
            self.time_timer.stop()
        # 更新时间
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.time_label.setText(f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}")
            self.start_time = None
        # 更新进度
        if success:
            self.safe_log("✅ PyOxidizer 打包完成！")
            self.progress_bar.setValue(100)
            self.progress_label.setText("100% - 完成!")
            self._save_config()
            show_msg(self, "完成", "PyOxidizer 打包成功！",1)
        else:
            self.safe_log("❌ PyOxidizer 打包失败")
            self.progress_bar.setValue(0)
            self.progress_label.setText("打包失败")
            QMessageBox.critical(self, "错误", "PyOxidizer 打包失败，请查看日志")
        # ===== 隐藏进度条容器 =====
        self.progress_container.setVisible(False)
        self.placeholder_widget.setVisible(True)
        # 重置按钮状态
        self.btn_build.setText("▶ 开始打包")
        self.btn_build.setStyleSheet("")
        self.is_building = False
        self.pyoxidizer_worker = None
        # 强制刷新
        QApplication.processEvents()

    def clean_pyapp_build(self, pyapp_src_dir: str = None) -> None:
        """清理 pyapp_src 的编译缓存，保留源码和配置"""
        if pyapp_src_dir is None:
            pyapp_src_dir = os.path.join(self.current_dir, "tools", "pyapp_src")
        project = Path(pyapp_src_dir).resolve()
        # 删除 target 目录（兼容 Windows 文件锁定）
        target = project / "target"
        if target.exists():
            def _handle_remove(func, path, exc_info):
                """解除只读属性后重试删除"""
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception:
                    pass
            deleted = False
            for i in range(3):
                try:
                    # Python 3.12+ 用 onexc，旧版用 onerror
                    if sys.version_info >= (3, 12):
                        shutil.rmtree(target, onexc=_handle_remove)
                    else:
                        shutil.rmtree(target, onerror=_handle_remove)
                    deleted = True
                    break
                except Exception:
                    time.sleep(0.5)
            if deleted:
                self.safe_log("🧹 已清理编译缓存: target/")
            else:
                # Windows 终极方案：rd /s /q
                if os.name == 'nt':
                    os.system(f'rd /s /q "{target}" 2>nul')
                    self.safe_log("🧹 已强制清理编译缓存: target/")
                else:
                    self.safe_log("⚠️ 清理编译缓存失败（可能被占用）")
        # 删除 Cargo.lock
        lock = project / "Cargo.lock"
        if lock.exists():
            try:
                lock.unlink()
                self.safe_log("🧹 已清理: Cargo.lock")
            except Exception as e:
                self.safe_log(f"⚠️ 清理 Cargo.lock 失败: {e}")

    def _read_cargo_output(self):
        data = self.cargo_process.readAllStandardOutput()
        line = bytes(data).decode('utf-8', errors='replace').strip()
        if line:
            self.safe_log(line)

    def _package_pyapp(self, input_file):
        """使用 PyApp 打包"""
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        self.safe_log("=" * 50)
        self.safe_log("📦 PyApp 打包模式")
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        base_output_dir = self.output_dir.text()
        out_dir = os.path.join(base_output_dir, output_name.replace(" ", "_"))
        os.makedirs(out_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {out_dir}")
        # 确定项目目录和入口文件
        if os.path.isdir(input_file):
            project_dir = input_file
            entry_file = self._find_entry(project_dir)
            if not entry_file:
                self.safe_log("❌ 未找到入口文件")
                return False
        else:
            project_dir = os.path.dirname(input_file)
            entry_file = input_file
        module_name = os.path.splitext(os.path.basename(entry_file))[0]
        self.safe_log(f"📄 入口模块: {module_name}")
        # 生成 Wheel 包
        wheel_path = self._build_wheel_for_project(project_dir, output_name)
        if not wheel_path:
            self.safe_log("❌ 生成 Wheel 包失败")
            return False
        self.safe_log(f"📦 Wheel 包: {wheel_path}")
        # 检查 cargo
        tools_dir = os.path.join(self.current_dir, "tools")
        cargo_path = None
        for p in [
            os.path.join(tools_dir, ".cargo", "bin", "cargo.exe"),
            os.path.join(tools_dir, "cargo", "bin", "cargo.exe"),
            shutil.which("cargo"),
        ]:
            if p and os.path.exists(p):
                cargo_path = p
                break
        if not cargo_path:
            self.safe_log("❌ 未找到 Cargo，请安装 Rust")
            QMessageBox.warning(self, "缺少依赖", "PyApp 需要 Rust，请安装 Rust: https://rustup.rs/")
            return False
        if cargo_path:
            # 统一转为小写后缀
            if cargo_path.lower().endswith('.exe'):
                cargo_path = cargo_path[:-4] + '.exe'
                self.safe_log(f"✅ 找到 Cargo: {cargo_path}")
        # 克隆或更新 pyapp 源码
        pyapp_src = os.path.join(tools_dir, "pyapp_src")
        if not os.path.exists(pyapp_src):
            self.safe_log("📥 克隆 PyApp 源码...")
            git = shutil.which("git")
            if not git:
                self.safe_log("❌ 未找到 git")
                return False
            self._run_hidden([git, "clone", "https://github.com/ofek/pyapp.git", pyapp_src], capture_output=True)
        if not os.path.exists(pyapp_src):
            self.safe_log("❌ PyApp 源码获取失败")
            return False
        # 设置环境变量
        env = os.environ.copy()
        env["PYAPP_PROJECT_NAME"] = output_name
        env["PYAPP_PROJECT_VERSION"] = "1.0.0"
        env["PYAPP_PROJECT_PATH"] = wheel_path
        env["PYAPP_EXEC_MODULE"] = module_name
        env["PYTHONUNBUFFERED"] = "1"
        env["RUST_LOG"] = "info"
        self.safe_log(f"🔧 PYAPP_PROJECT_PATH={wheel_path}")
        self.safe_log(f"🔧 PYAPP_EXEC_MODULE={module_name}")
        # 修复：定义 build_temp 变量
        build_temp = os.path.join(out_dir, "build_temp")
        try:
            # 使用无缓冲模式
            process = self._popen_hidden(
                [cargo_path, "build", "--release", "--verbose"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,
                bufsize=0,
                cwd=pyapp_src,
                env=env,
            )
            # 实时读取字节并解码
            while True:
                line_bytes = process.stdout.readline()
                if not line_bytes:
                    break
                try:
                    line = line_bytes.decode('utf-8', errors='replace').rstrip()
                except:
                    line = str(line_bytes)
                if line:
                    self.safe_log(line)
                    QApplication.processEvents()
            process.wait()
            success = process.returncode == 0
            if success:
                # 复制生成的 exe
                src_exe = os.path.join(pyapp_src, "target", "release", "pyapp.exe")
                dst_exe = os.path.join(out_dir, f"{output_name}.exe")
                if os.path.exists(src_exe):
                    shutil.copy2(src_exe, dst_exe)
                    self.safe_log(f"✅ 已复制: {dst_exe}")
                else:
                    for root, dirs, files in os.walk(os.path.join(pyapp_src, "target")):
                        for f in files:
                            if f == "pyapp.exe":
                                shutil.copy2(os.path.join(root, f), dst_exe)
                                self.safe_log(f"✅ 已复制: {dst_exe}")
                                break
                self.safe_log(f"✅ PyApp 打包成功！输出位置: {out_dir}")
                self._save_config()
            else:
                self.safe_log("❌ PyApp 打包失败")
            return success
        except Exception as e:
            self.safe_log(f"❌ 打包出错: {e}")
            return False
        finally:
            if build_temp and os.path.exists(build_temp):
                shutil.rmtree(build_temp, ignore_errors=True)
                self.safe_log("🧹 已清理临时目录: build_temp")

    def _install_pyinstaller(self):
        """安装 PyInstaller"""
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        try:
            self.safe_log("📦 正在安装 PyInstaller...")
            process = self._popen_hidden(
                [python_cmd, '-m', 'pip', 'install', 'pyinstaller', '-i', MIRROR],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace',
                startupinfo=get_startupinfo()
            )
            for line in process.stdout:
                if line.strip():
                    self.safe_log(f"  {line.strip()}")
            process.wait()
            if process.returncode == 0:
                self.safe_log("✅ PyInstaller 安装成功")
                return True
            else:
                self.safe_log("❌ PyInstaller 安装失败")
                return False
        except Exception as e:
            self.safe_log(f"❌ 安装异常: {e}")
            return False

    def _build_wheel_for_project(self, project_dir, out_name):
        """为项目生成 Wheel 包"""
        self.safe_log("📦 正在生成 Wheel 包...")
        py = self.python_path.currentText()
        if not py or not os.path.exists(py):
            py = sys.executable
        input_file = self.input_file.text()
        if os.path.isdir(input_file):
            entry_file = self._find_entry(input_file)
        else:
            entry_file = input_file
        if not entry_file or not os.path.exists(entry_file):
            self.safe_log("❌ 入口文件不存在")
            return None
        module_name = os.path.splitext(os.path.basename(entry_file))[0]
        original_module_name = module_name
        # ===== 检测并自动重命名 =====
        new_module_name = module_name
        need_rename = False
        # 检查是否以数字开头
        if module_name and module_name[0].isdigit():
            new_module_name = 'app_' + module_name
            need_rename = True
            self.safe_log(f"⚠️ 文件名 '{module_name}.py' 以数字开头，自动重命名为 '{new_module_name}.py'，打包完成后可手动改为 {module_name}.py")
        # 检查是否包含非法字符（只允许字母、数字、下划线）
        if re.search(r'[^a-zA-Z0-9_]', new_module_name):
            new_module_name = re.sub(r'[^a-zA-Z0-9_]', '_', new_module_name)
            need_rename = True
            self.safe_log(f"⚠️ 文件名包含非法字符，自动重命名为 '{new_module_name}.py'")
        # ===== 如果名称变了，更新 module_name =====
        if need_rename:
            module_name = new_module_name
            entry_file_dir = os.path.dirname(entry_file)
            temp_entry = os.path.join(entry_file_dir, f"{module_name}.py")
            shutil.copy2(entry_file, temp_entry)
            entry_file = temp_entry
            self.safe_log(f"✅ 已创建临时副本: {module_name}.py")
        # ===== 清理项目名称 =====
        clean_name = re.sub(r'[()\[\]{}<>]', '', out_name)
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', clean_name)
        if clean_name and clean_name[0].isdigit():
            clean_name = '_' + clean_name
        out_dir = os.path.join(self.output_dir.text(), clean_name.replace(" ", "_"))
        build_dir = os.path.join(out_dir, "build_temp")
        shutil.rmtree(build_dir, ignore_errors=True)
        os.makedirs(build_dir, exist_ok=True)
        # ===== 复制入口文件 =====
        with open(entry_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        # 如果没有 main() 函数，自动添加
        if 'def main()' not in content and 'def main(' not in content:
            content += f'''
    def main():
        """程序入口"""
        print("{original_module_name} 启动")
        if 'run' in globals():
            run()
        elif 'start' in globals():
            start()
    '''
            self.safe_log("✅ 已添加 main() 函数")
        # 保存为新的模块名
        with open(os.path.join(build_dir, f"{module_name}.py"), 'w', encoding='utf-8-sig') as f:
            f.write(content)
        # ===== 生成 __init__.py =====
        with open(os.path.join(build_dir, "__init__.py"), 'w', encoding='utf-8-sig') as f:
            f.write(f'# {clean_name} package\n')
        # ===== 构建 pyproject.toml =====
        toml_lines = [
            "[build-system]",
            'requires = ["setuptools>=61.0", "wheel"]',
            'build-backend = "setuptools.build_meta"',
            "",
            "[project]",
            f'name = "{clean_name}"',
            'version = "1.0.0"',
            'description = "Packaged with PyApp"',
            'requires-python = ">=3.8"',
            "",
            "[project.scripts]",
            f'{clean_name} = "{module_name}:main"',  # 使用新的 module_name
            "",
            "[tool.setuptools]",
            "packages = []",
            f'py-modules = ["{module_name}"]',  # 使用新的 module_name
        ]
        content = "\n".join(toml_lines)
        pyproject_path = os.path.join(build_dir, "pyproject.toml")
        with open(pyproject_path, 'w', encoding='utf-8-sig') as f:
            f.write(content)
        self.safe_log(f"📄 模块名: {module_name}")
        self.safe_log(f"📄 项目名: {clean_name}")
        self._run_hidden([py, "-m", "pip", "install", "build", "--quiet"], capture_output=True)
        result = self._run_hidden(
            [py, "-m", "build", "--wheel"],
            cwd=build_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            self.safe_log(f"❌ 构建失败: {result.stderr[:500]}")
            return None
        dist_dir = os.path.join(build_dir, "dist")
        whl_files = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]
        if not whl_files:
            self.safe_log("❌ 未找到 wheel 文件")
            return None
        wheel_path = os.path.join(dist_dir, whl_files[0])
        self.safe_log(f"✅ Wheel 包生成成功: {os.path.basename(wheel_path)}")
        # ===== 清理临时文件 =====
        if need_rename and os.path.exists(temp_entry):
            try:
                os.remove(temp_entry)
                self.safe_log(f"🧹 已清理临时文件: {os.path.basename(temp_entry)}")
            except:
                pass
        return wheel_path

    def _find_entry(self, path):
        """查找入口文件"""
        for e in ["main.py", "__main__.py", "run.py", "app.py", "launcher.py", "start.py"]:
            p = os.path.join(path, e)
            if os.path.exists(p):
                return p
        py_files = [f for f in os.listdir(path) if f.endswith(".py")]
        return os.path.join(path, py_files[0]) if py_files else None

    def _package_pynsist(self, input_file):
        """使用 Pynsist 打包（生成安装程序）"""
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        self.progress_bar.setValue(0)
        self.progress_label.setText("0% - 准备中...")
        QApplication.processEvents()
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        base_output_dir = self.output_dir.text()
        project_output_dir = os.path.join(base_output_dir, output_name.replace(" ", "_"))
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")
        self.progress_bar.setValue(5)
        self.progress_label.setText("5% - 准备环境...")
        QApplication.processEvents()
        # 设置本地嵌入式 Python 包
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
        self.progress_bar.setValue(10)
        self.progress_label.setText("10% - 准备配置文件...")
        QApplication.processEvents()
        entry_module = os.path.basename(input_file).replace(".py", "")
        console_value = "true" if self.debug_mode.isChecked() else "false"
        # 直接构建 installer.cfg
        cfg_lines = [
            "[Application]",
            f"name={output_name}",
            "version=1.0",
            f"entry_point={entry_module}:main",
            f"console={console_value}",
            "[Python]",
            "version=3.12.0",
            "bitness=64",
            "[Build]",
            "directory=build",
            f"installer_name={output_name}_Setup.exe",
            "[Include]",
            "pypi_wheels =",
            "files=",
        ]
        icon_file = self.icon_label.toolTip() if self.icon_label.text() else ""
        if icon_file and os.path.exists(icon_file):
            cfg_lines.insert(12, f"icon={os.path.basename(icon_file)}")
            shutil.copy2(icon_file, project_output_dir)
        cfg_content = "\n".join(cfg_lines)
        cfg_path = os.path.join(project_output_dir, "installer.cfg")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(cfg_content)
        self.progress_bar.setValue(15)
        self.progress_label.setText("15% - 配置文件已生成")
        QApplication.processEvents()
        shutil.copy2(input_file, project_output_dir)
        for source, target in self.data_files_list:
            if os.path.exists(source):
                dest_path = os.path.join(project_output_dir, target)
                dest_dir = os.path.dirname(dest_path)
                if dest_dir and not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(source, dest_path)
                self.safe_log(f"  📄 复制数据文件: {source} -> {target}")
        self.progress_bar.setValue(20)
        self.progress_label.setText("20% - 文件复制完成")
        QApplication.processEvents()
        pynsist_exe = os.path.join(os.path.dirname(python_cmd), "pynsist.exe")
        if os.path.exists(pynsist_exe):
            cmd = [pynsist_exe, cfg_path, "--no-makensis"]
        else:
            cmd = [python_cmd, "-m", "pynsist", cfg_path, "--no-makensis"]
        self.safe_log(f"🚀 开始生成 NSIS 脚本...")
        self.progress_bar.setValue(25)
        self.progress_label.setText("25% - 生成 NSIS 脚本...")
        QApplication.processEvents()
        try:
            startupinfo = get_startupinfo()
            self.process = self._popen_hidden(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )
            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1
                    if line_count % 10 == 0:
                        pct = min(25 + line_count // 2, 50)
                        self.progress_bar.setValue(pct)
                        self.progress_label.setText(f"{pct}% - 生成 NSIS 脚本...")
                        QApplication.processEvents()
            self.process.wait()
            if self.process.returncode != 0:
                self.safe_log("❌ 生成 NSIS 脚本失败")
                return False
            self.progress_bar.setValue(50)
            self.progress_label.setText("50% - NSIS 脚本已生成")
            QApplication.processEvents()
            nsi_file = os.path.join(project_output_dir, "build", "installer.nsi")
            if os.path.exists(nsi_file):
                with open(nsi_file, "r", encoding="utf-8") as f:
                    nsi_content = f.read()
                launch_ext = ".launch.py" if self.debug_mode.isChecked() else ".launch.pyw"
                launch_file = f"{output_name}{launch_ext}"
                python_exe = "$INSTDIR\\Python\\python.exe"
                shortcut_code = f'\n    CreateShortcut "$DESKTOP\\{output_name}.lnk" "{python_exe}" "$INSTDIR\\{launch_file}"\n'
                if "CreateShortcut" in nsi_content:
                    lines = nsi_content.split("\n")
                    new_lines = []
                    inserted = False
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                        if not inserted and "CreateShortcut" in line and "$SMPROGRAMS" in line:
                            new_lines.append(shortcut_code)
                            inserted = True
                    if inserted:
                        nsi_content = "\n".join(new_lines)
                        self.safe_log(f"✅ 已添加桌面快捷方式，指向: {launch_file}")
                else:
                    nsi_content = nsi_content.replace("SectionEnd", f"{shortcut_code}SectionEnd")
                    self.safe_log(f"✅ 已添加桌面快捷方式，指向: {launch_file}")
                with open(nsi_file, "w", encoding="utf-8") as f:
                    f.write(nsi_content)
                self.progress_bar.setValue(60)
                self.progress_label.setText("60% - 已添加快捷方式")
                QApplication.processEvents()
                makensis_path = None
                possible_paths = [
                    os.path.join(tools_dir, "NSIS", "makensis.exe"),
                    r"C:\Program Files (x86)\NSIS\makensis.exe",
                    r"C:\Program Files\NSIS\makensis.exe",
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        makensis_path = path
                        break
                if makensis_path and os.path.exists(makensis_path):
                    self.safe_log(f"🚀 开始编译安装程序...")
                    self.progress_bar.setValue(70)
                    self.progress_label.setText("70% - 编译安装程序...")
                    QApplication.processEvents()
                    result = self._run_hidden(
                        [makensis_path, nsi_file],
                        cwd=project_output_dir,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if result.returncode == 0:
                        self.safe_log(f"✅ 安装程序编译成功")
                        self.progress_bar.setValue(90)
                        self.progress_label.setText("90% - 编译完成")
                        QApplication.processEvents()
                        setup_exe = os.path.join(project_output_dir, "build", f"{output_name}_Setup.exe")
                        if os.path.exists(setup_exe):
                            self.safe_log(f"✅ 安装程序生成: {setup_exe}")
                            shutil.copy2(setup_exe, os.path.join(project_output_dir, f"{output_name}_Setup.exe"))
                            self.safe_log(f"📦 安装程序大小: {os.path.getsize(setup_exe) / (1024 * 1024):.2f} MB")
                        else:
                            import glob
                            setup_files = glob.glob(os.path.join(project_output_dir, "build", "**", "*_Setup.exe"),
                                                    recursive=True)
                            if setup_files:
                                for sf in setup_files:
                                    shutil.copy2(sf, os.path.join(project_output_dir, os.path.basename(sf)))
                                    self.safe_log(f"✅ 找到安装程序: {sf}")
                        self.progress_bar.setValue(100)
                        self.progress_label.setText("100% - 打包完成!")
                        QApplication.processEvents()
                        self.safe_log(f"✅ Pynsist 打包成功！输出位置: {project_output_dir}")
                        self._save_config()
                        return True
                    else:
                        self.safe_log(f"❌ 编译失败: {result.stderr}")
                        return False
                else:
                    self.safe_log(f"⚠️ 未找到 NSIS 编译器，请安装 NSIS")
                    self.safe_log(f"✅ NSIS 脚本已生成: {nsi_file}")
                    self.progress_bar.setValue(80)
                    self.progress_label.setText("80% - NSIS 脚本已生成（需手动编译）")
                    QApplication.processEvents()
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
        if sys.platform != "darwin":
            self.safe_log("❌ py2app 只能在 macOS 系统上运行")
            self.safe_log("   当前系统: " + sys.platform)
            return False
        python_cmd = self.python_path.currentText()
        if not python_cmd or not os.path.exists(python_cmd):
            python_cmd = sys.executable
        if not python_cmd:
            self.safe_log("❌ 未找到 Python")
            return False
        self.safe_log("⚠️ py2app 创建符合 macOS 规范的应用程序包 (.app)。")
        input_file = self.input_file.text()
        output_name = self.app_name.text()
        base_output_dir = self.output_dir.text()
        project_output_dir = os.path.join(base_output_dir, output_name.replace(" ", "_"))
        os.makedirs(project_output_dir, exist_ok=True)
        self.safe_log(f"📁 输出目录: {project_output_dir}")
        # 直接构建 setup.py
        setup_lines = [
            "# -*- coding: utf-8 -*-",
            "from distutils.core import setup",
            "import py2app",
            "",
            "setup(",
            f"    console=[{{'script': '{os.path.basename(input_file)}'}}],",
            "    options={'py2app': {",
            "        'compressed': True,",
            "        'optimize': 2,",
            "        'bundle_files': 3,",
            f"        'includes': {self.hidden_imports_list},",
            f"        'excludes': {self.exclude_list}",
            "    }},",
            "    zipfile=None",
            ")",
        ]
        setup_content = "\n".join(setup_lines)
        setup_path = os.path.join(project_output_dir, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(setup_content)
        shutil.copy2(input_file, project_output_dir)
        cmd = [python_cmd, "setup.py", "py2app"]
        self.safe_log(f"🚀 开始 py2app 打包...")
        self.safe_log(f"📝 命令: {' '.join(cmd)}")
        QApplication.processEvents()
        self.progress_bar.setValue(5)
        self.progress_label.setText("5% - 准备中...")
        QApplication.processEvents()
        try:
            startupinfo = get_startupinfo()
            self.process = self._popen_hidden(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                cwd=project_output_dir,
            )
            line_count = 0
            for line in iter(self.process.stdout.readline, ""):
                if line.strip():
                    self.safe_log(line.strip())
                    line_count += 1
                    if "Copying" in line or "copying" in line.lower():
                        pct = min(20 + line_count // 2, 50)
                        self.progress_bar.setValue(pct)
                        self.progress_label.setText(f"{pct}% - 复制依赖...")
                        QApplication.processEvents()
                    elif "Building" in line or "building" in line.lower():
                        pct = min(50 + line_count // 3, 80)
                        self.progress_bar.setValue(pct)
                        self.progress_label.setText(f"{pct}% - 构建中...")
                        QApplication.processEvents()
                if self.btn_build.text() == "▶ 开始打包" and self.process.poll() is None:
                    self.process.terminate()
                    break
            self.process.wait()
            success = self.process.returncode == 0
            if success:
                self.progress_bar.setValue(100)
                self.progress_label.setText("100% - 完成!")
                QApplication.processEvents()
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

    def _update_packer_ui(self, packer):
        """切换打包器时显示/隐藏对应控件"""
        if not getattr(self, '_packer_panel_initialized', False):
            self._init_packer_panel_controls()
        # 全部隐藏
        for w in self.nuitka_widgets:
            w.setVisible(False)
        for w in self.pyi_base_widgets:
            w.setVisible(False)
        for w in self.pyi_cmd_widgets:
            w.setVisible(False)
        show = False
        if packer == "Nuitka":
            for w in self.nuitka_widgets:
                w.setVisible(True)
            show = True
            self.status_compiler.setVisible(True)
            self._display_compiler_status()
            python_exe = self.python_path.currentText()
            if python_exe and os.path.exists(python_exe):
                cache_key = f"Nuitka@{python_exe}"
                version = self._packer_versions_cache.get(cache_key)
                if version:
                    self._auto_set_nuitka_compat(version)
            if not self._cached_has_msvc and not self._cached_has_mingw:
                QTimer.singleShot(100, self._detect_compilers_async)
            # ===== 切换到Nuitka时，自动检测当前py文件的GUI插件 =====
            script = self.input_file.text()
            if script and os.path.exists(script):
                QTimer.singleShot(50, lambda: self._auto_detect_and_set_gui_plugin(script))
        elif packer in ["PyOxidizer", "PyApp"]:
            show = True
            self.status_compiler.setVisible(True)
            self._display_rust_status()
            if not self._cached_has_cargo and not self._cached_has_rustc:
                QTimer.singleShot(100, self._detect_rust_async)
        elif packer == "Pynsist":
            show = True
            self.status_compiler.setVisible(True)
            self._display_nsis_status()
            if not self._cached_has_nsis:
                QTimer.singleShot(100, self._detect_nsis_async)
        elif packer in ["PyInstaller-spec", "PyInstaller-cmd"]:
            for w in self.pyi_base_widgets:
                w.setVisible(True)
            if packer == "PyInstaller-cmd":
                for w in self.pyi_cmd_widgets:
                    w.setVisible(True)
            show = True
            self.status_compiler.setVisible(False)
            self.status_compiler.setText("")
        else:
            show = False
            self.status_compiler.setVisible(False)
            self.status_compiler.setText("")
        if hasattr(self, 'packer_opt_row'):
            self.packer_opt_row.setVisible(show)

    def _install_packer_async(self, python_exe, packer_name):
        """后台安装打包器"""
        try:
            self.safe_log(f"📦 正在安装 {packer_name} ...")
            success, result = pip_install(python_exe, packer_name, quiet=True)
            if success:
                self.safe_log(f"✅ {packer_name} 安装成功")
                self._packer_versions_cache = {}
                QTimer.singleShot(100, self._detect_all_packer_versions_async)
            else:
                self.safe_log(f"❌ {packer_name} 安装失败")
        except Exception as e:
            self.safe_log(f"❌ 安装异常: {e}")

    def _on_packer_changed(self, packer):
        """切换打包器 """
        self._clear_log()
        python_exe = self.python_path.currentText()
        if python_exe and os.path.exists(python_exe):
            packer_name = self._get_packer_display_name(packer)
            # 检查是否已安装
            try:
                result = subprocess.run(
                    [python_exe, '-m', 'pip', 'show', packer_name.lower()],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode != 0:
                    self.safe_log(f"⚠️ {packer_name} 未安装，正在安装...")
                    # 后台安装
                    threading.Thread(
                        target=self._install_packer_async,
                        args=(python_exe, packer_name.lower()),
                        daemon=True
                    ).start()
            except:
                pass
        if packer == "Nuitka":
            if hasattr(self, 'auto_exclude_cb'):
                self.auto_exclude_cb.setChecked(False)
            #script = self.input_file.text()
            #if script and os.path.exists(script):
                #self._analyze_used(script, auto_add=False)
            self.safe_log(
                "📌 Nuitka 模式：编译为C代码，体积小，启动快，需要C编译器\n"
                "   安装: pip install -U nuitka\n"
                "   常用命令: python -m nuitka --standalone --onefile --windows-disable-console your_script.py\n"
                "   参数说明:\n"
                "     --standalone      : 独立运行（包含依赖）\n"
                "     --onefile         : 打包成单个exe文件\n"
                "     --windows-disable-console : 无控制台窗口（GUI程序）\n"
                "     --windows-icon-from-ico=app.ico : 设置图标\n"
                "     --enable-plugin=pyqt6 : Qt6应用\n"
                "     --enable-plugin=tk-inter : tkinter应用\n"
                "     --jobs=4          : 并行编译核心数（建议CPU-1）\n"
                "     --low-memory      : 低内存模式（8核以上自动启用）\n"
                "   ⚠️ 需要安装C编译器: MinGW64 或 MSVC"
            )
        elif packer == "PyInstaller-spec":
            self.safe_log(
                "📌 PyInstaller-spec 模式：使用.spec配置文件打包，可定制性强\n"
                "   安装: pip install pyinstaller\n"
                "   生成spec: pyi-makespec -F --noconsole your_script.py\n"
                "   编辑spec后打包: pyinstaller your_script.spec\n"
                "   优势: 可精确控制打包细节，适合复杂项目"
            )
        elif packer == "PyInstaller-cmd":
            self.safe_log(
                "📌 PyInstaller-cmd 模式：命令行直接打包，简单快捷\n"
                "   安装: pip install pyinstaller\n"
                "   常用命令: pyinstaller -F --noconsole --icon=app.ico your_script.py\n"
                "   常用参数:\n"
                "     -F, --onefile     : 打包成单个exe文件\n"
                "     -D, --onedir      : 打包成文件夹（含依赖）\n"
                "     --noconsole       : 无控制台窗口（GUI程序）\n"
                "     --icon=app.ico    : 设置图标\n"
                "     --add-data src;dst: 添加数据文件 (Windows用; Linux用:)\n"
                "     --hidden-import=模块名 : 添加隐藏导入\n"
                "     --exclude-module=模块名 : 排除不需要的模块\n"
                "     --upx-dir=路径    : 启用UPX压缩\n"
                "     --clean           : 清理临时文件"
            )
        elif packer == "PyOxidizer":
            self.safe_log(
                "📌 PyOxidizer 模式：嵌入Python解释器，启动快，内存占用低\n"
                "   安装: pip install pyoxidizer\n"
                "   或: cargo install pyoxidizer\n"
                "   常用命令: pyoxidizer build --release\n"
                "   ⚠️ 需要Rust环境: https://rustup.rs/\n"
                "   💡 特点: 生成单个exe，启动速度快，适合大型应用"
            )
        elif packer == "Pynsist":
            self.safe_log(
                "📌 Pynsist 模式：生成NSIS安装程序，适合分发给终端用户\n"
                "   安装: pip install pynsist\n"
                "   配置: 创建 installer.cfg 配置文件\n"
                "   生成NSIS脚本: pynsist installer.cfg\n"
                "   编译安装程序: makensis installer.nsi\n"
                "   ⚠️ 需要安装NSIS: https://nsis.sourceforge.io/Download\n"
                "   💡 特点: 生成专业安装包，支持桌面快捷方式"
            )
        elif packer == "Py2exe":
            self.safe_log(
                "📌 Py2exe 模式：经典Windows打包工具，兼容性好\n"
                "   安装: pip install py2exe\n"
                "   配置: 创建 setup.py 文件\n"
                "   打包: python setup.py py2exe\n"
                "   ⚠️ 仅支持Windows，Python 3.8+ 支持有限\n"
                "   💡 适合: 老旧项目维护"
            )
        elif packer == "Cx_Freeze":
            self.safe_log(
                "📌 Cx_Freeze 模式：跨平台打包工具，支持Windows/Linux/macOS\n"
                "   安装: pip install cx-freeze\n"
                "   配置: 创建 setup.py 文件\n"
                "   打包: python setup.py build_exe\n"
                "   常用参数: cxfreeze your_script.py --target-dir dist\n"
                "   💡 特点: 跨平台支持好，配置灵活"
            )
        elif packer == "Py2app":
            self.safe_log(
                "📌 Py2app 模式：macOS专用打包工具，生成.app应用包\n"
                "   安装: pip install py2app\n"
                "   配置: 创建 setup.py 文件\n"
                "   打包: python setup.py py2app\n"
                "   ⚠️ 仅支持macOS系统\n"
                "   💡 适合: macOS应用分发"
            )
        elif packer == "PyApp":
            self.safe_log(
                "📌 PyApp 模式：Rust编写的Python应用打包工具\n"
                "   安装: pip install pyapp\n"
                "   或: cargo install pyapp-cli\n"
                "   配置: 创建 pyapp.toml 配置文件\n"
                "   打包: pyapp build --release\n"
                "   ⚠️ 需要Rust环境: https://rustup.rs/\n"
                "   💡 特点: 启动速度快，体积小，跨平台"
            )
        self._update_packer_ui(packer)
        show = packer in ["Nuitka", "PyInstaller-spec", "PyInstaller-cmd"]
        if hasattr(self, 'packer_opt_row'):
            self.packer_opt_row.setVisible(show)
        # ===== 直接从缓存更新UI =====
        self._update_all_backend_ui()

    def _update_nsis_status(self):
        """检测 NSIS 是否可用（Pynsist 需要）- 先读缓存，没有才检测"""
        # ===== 从缓存读取 =====
        cache = load_cache()
        nsis_cache = cache.get('nsis', {})
        has_nsis = nsis_cache.get('has_nsis', False)
        nsis_path = nsis_cache.get('nsis_path', '')
        nsis_version = nsis_cache.get('nsis_version', '')
        # ===== 有缓存直接使用 =====
        if has_nsis:
            self._update_nsis_status_result(has_nsis, nsis_path, nsis_version)
            return
        # ===== 没有缓存才检测 =====
        self.status_compiler.setText("⏳ 检测NSIS...")
        self.status_compiler.setStyleSheet("color: orange;")

        def detect():
            has_nsis, nsis_path = self._check_nsis_with_path()
            nsis_version = self._get_nsis_version(nsis_path) if has_nsis else ""
            cache = load_cache()
            cache['nsis'] = {
                'has_nsis': has_nsis,
                'nsis_path': nsis_path,
                'nsis_version': nsis_version,
            }
            save_cache(cache)
            QTimer.singleShot(0, lambda: self._update_nsis_status_result(
                has_nsis, nsis_path, nsis_version
            ))
        threading.Thread(target=detect, daemon=True).start()

    def _update_nsis_status_result(self, has_nsis, nsis_path="", nsis_version=""):
        """更新 NSIS 状态UI（主线程）"""
        self._cached_has_nsis = has_nsis
        self._cached_nsis_path = nsis_path
        if has_nsis:
            self.status_compiler.setText(f"🔧 NSIS: {nsis_version}")
            self.status_compiler.setStyleSheet("color: green;")
            if nsis_path:
                self.status_compiler.setToolTip(f"NSIS路径: {nsis_path}")
        else:
            self.status_compiler.setText("🔧 NSIS: 未安装")
            self.status_compiler.setStyleSheet("color: orange;")
            self.status_compiler.setToolTip(
                "Pynsist 需要 NSIS 生成安装程序\n下载: https://nsis.sourceforge.io/Download")

    def _detect_nsis_async(self):
        """异步检测NSIS（Pynsist需要）"""
        self.status_compiler.setText("⏳ 检测NSIS...")
        self.status_compiler.setStyleSheet("color: orange;")

        def detect():
            has_nsis, nsis_path = self._check_nsis_with_path()
            nsis_version = self._get_nsis_version(nsis_path) if has_nsis else ""
            self._cached_has_nsis = has_nsis
            self._cached_nsis_path = nsis_path
            self._cached_nsis_version = nsis_version
            self._save_all_backend_cache()
            QTimer.singleShot(0, self._display_nsis_status)
            if has_nsis:
                self.safe_log(f"✅ NSIS: {nsis_version}")
            else:
                self.safe_log("⚠️ NSIS未安装，Pynsist需要NSIS生成安装程序")
        threading.Thread(target=detect, daemon=True).start()

    def _check_nsis_with_path(self):
        """检测 NSIS 是否可用，并返回路径"""
        # 1. 检查 makensis.exe 是否在 PATH 中
        makensis_path = shutil.which("makensis.exe")
        if makensis_path and os.path.exists(makensis_path):
            return True, makensis_path
        # 2. 检查常见安装路径
        if sys.platform == 'win32':
            nsis_paths = [
                r"C:\Program Files (x86)\NSIS\makensis.exe",
                r"C:\Program Files\NSIS\makensis.exe",
                os.path.join(get_exe_directory(), "tools", "NSIS", "makensis.exe"),
            ]
            for path in nsis_paths:
                if os.path.exists(path):
                    return True, path
        else:
            # Linux/macOS: NSIS 不常用，但可通过 wine 运行
            makensis_path = shutil.which("makensis")
            if makensis_path:
                return True, makensis_path
        return False, ""

    def _get_nsis_version(self, nsis_path):
        """获取 NSIS 版本号"""
        try:
            # makensis.exe -version 输出示例: v3.08
            result = self._run_hidden(
                [nsis_path, "-version"],
                capture_output=True, text=True, timeout=5,
                startupinfo=get_startupinfo()
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                import re
                # 匹配 v3.08 或 3.08
                match = re.search(r'v?(\d+\.\d+)', output)
                if match:
                    return match.group(1)
            return "已安装"
        except Exception:
            return "已安装"

    def _check_nuitka_version_async(self):
        """异步检测Nuitka版本，不阻塞UI"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.status_packer.setText("📦 Nuitka: 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            return
        cache_key = f"Nuitka@{python_exe}"
        # ===== 先读内存缓存 =====
        if cache_key in self._packer_version_cache:
            version = self._packer_version_cache[cache_key]
            self._update_nuitka_status(version or "")
            return
        # ===== 再读文件缓存 =====
        try:
            cache = load_cache()
            packer_versions = cache.get('packer_versions', {})
            version = packer_versions.get(cache_key)
            if version is not None:
                self._packer_version_cache[cache_key] = version
                self._update_nuitka_status(version or "")
                return
        except:
            pass
        # ===== 缓存未命中，显示检测中 =====
        self.status_packer.setText("📦 Nuitka: 检测中...")
        self.status_packer.setStyleSheet("color: orange;")

        def detect():
            # 使用 pip show 检测
            version = self._check_packer_version("Nuitka", python_exe)
            # 保存到缓存
            self._packer_version_cache[cache_key] = version
            try:
                cache = load_cache()
                if 'packer_versions' not in cache:
                    cache['packer_versions'] = {}
                cache['packer_versions'][cache_key] = version
                save_cache(cache)
            except:
                pass
            # 更新UI
            QTimer.singleShot(0, lambda: self._update_nuitka_status(version or ""))
        threading.Thread(target=detect, daemon=True).start()

    def _update_nuitka_status(self, version):
        """主线程更新Nuitka状态"""
        if version:
            self.status_packer.setText(f"📦 Nuitka: {version}")
            self.status_packer.setStyleSheet("color: green;")
            # 自动检测兼容模式
            self._auto_set_nuitka_compat(version)
        else:
            self.status_packer.setText("📦 Nuitka: 未安装")
            self.status_packer.setStyleSheet("color: red;")

    def _auto_set_nuitka_compat(self, version):
        """自动设置Nuitka兼容模式"""
        try:
            if not version:
                return
            # ===== 检查控件是否存在 =====
            if not hasattr(self, 'nuitka_compat_cb'):
                return
            version_parts = version.split('.')
            major = int(version_parts[0]) if version_parts else 0
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            # 4.1 及以上版本需要兼容模式
            should_check = (major > 4 or (major == 4 and minor >= 1))
            # ===== 检查当前状态 =====
            current_state = self.nuitka_compat_cb.isChecked()
            if should_check:
                if not current_state:
                    self.nuitka_compat_cb.setChecked(True)
                    # 只输出一次日志
                    if not self._nuitka_compat_notified:
                        self.safe_log(f"✅ Nuitka {version} 已自动启用兼容模式")
                        self._nuitka_compat_notified = True
            else:
                if current_state:
                    self.nuitka_compat_cb.setChecked(False)
                    # 只输出一次日志
                    if not self._nuitka_compat_notified:
                        self.safe_log(f"✅ Nuitka {version} 使用原参数")
                        self._nuitka_compat_notified = True
        except Exception as e:
            self.safe_log(f"⚠️ 自动设置兼容模式失败: {e}")

    def _apply_theme(self):
        themes = {
            "🌞 默认主题": """
                QMainWindow{background-color:#f5f6fa}
                QGroupBox{font-weight:bold;border:1px solid #dfe6e9;border-radius:4px;margin-top:8px;padding:8px}
                QLineEdit{border:1px solid #b2bec3;border-radius:3px;padding:4px;background:white}
                QPushButton{border:1px solid #b2bec3;border-radius:3px;padding:4px 12px;background:#dfe6e9}
                QPushButton:hover{background:#b2bec3}
                QPlainTextEdit{border:1px solid #b2bec3;border-radius:3px;background:#2d3436;color:#dfe6e9}
            """,
            "🌅 暗夜深邃": """
                QMainWindow{background-color:#2d3436}
                QWidget{color:#dfe6e9}
                QGroupBox{color:#dfe6e9;border:1px solid #636e72}
                QLineEdit{background:#2d3436;color:#dfe6e9;border:1px solid #636e72}
                QPushButton{background:#636e72;color:white}
                QPlainTextEdit{background:#1e272e;color:#dfe6e9}
            """,
            "☁️ 云淡风轻": """
                QMainWindow{background-color:#ffffff}
                QLineEdit{border:1px solid #e0e0e0}
                QPushButton{background:#f5f5f5}
                QPlainTextEdit{background:#fafafa}
            """,
            "🌿 薄荷绿意": """
                QMainWindow{background-color:#c7edcc}
                QGroupBox{color:#2d5016;border:1px solid #a8d5a2}
                QLineEdit{background:#e8f5e9}
                QPushButton{background:#dcedc8}
                QPlainTextEdit{background:#1b5e20;color:#e8f5e9}
            """,
            "🌸 樱花粉嫩": """
                QMainWindow{background-color:#fce4ec}
                QGroupBox{color:#880e4f;border:1px solid #f06292}
                QLineEdit{background:#f48fb1;color:#880e4f;border:1px solid #f06292}
                QPushButton{background:#f8bbd0;color:#880e4f;border:1px solid #f06292}
                QPushButton:hover{background:#f48fb1}
                QPlainTextEdit{background:#fce4ec;color:#880e4f;border:1px solid #f06292}
            """,
            "🌌 星际紫韵": """
                QMainWindow{background-color:#f3e8ff}
                QGroupBox{color:#4a1a7a;border:1px solid #c084fc}
                QLineEdit{background:#d8b4fe;color:#4a1a7a;border:1px solid #c084fc}
                QPushButton{background:#e9d5ff;color:#4a1a7a;border:1px solid #c084fc}
                QPushButton:hover{background:#d8b4fe}
                QPlainTextEdit{background:#2d1b4e;color:#e9d5ff;border:1px solid #c084fc}
            """,
            "🌊 深海蔚蓝": """
                QMainWindow{background-color:#e3f2fd}
                QGroupBox{color:#0d47a1;border:1px solid #64b5f6}
                QLineEdit{background:#90caf9;color:#0d47a1;border:1px solid #64b5f6}
                QPushButton{background:#bbdefb;color:#0d47a1;border:1px solid #64b5f6}
                QPushButton:hover{background:#90caf9}
                QPlainTextEdit{background:#e3f2fd;color:#1565c0;border:1px solid #64b5f6}
            """,
        }
        self.setStyleSheet(themes.get(self.themes[self.current_theme_idx], themes["🌞 默认主题"]))

    def _async_init(self):
        threading.Thread(target=self._async_find_upx, daemon=True).start()
        threading.Thread(target=self._async_find_python, daemon=True).start()
        threading.Thread(target=self._async_load_config, daemon=True).start()
        threading.Thread(target=self._detect_compilers_async, daemon=True).start()
        threading.Thread(target=self._preload_packer_versions, daemon=True).start()

    def _preload_packer_versions(self):
        """启动时预加载所有打包器版本到缓存"""
        self._preload_all_packer_versions_with_cache()

    def _async_find_upx(self):
        """异步查找UPX - 有缓存就用，没有才扫"""
        cache = load_cache()
        if 'upx' in cache:
            upx_path = cache['upx'].get('path')
            if upx_path and os.path.exists(upx_path):
                self._set_upx_environment(upx_path)
                self.upx_path.setText(self._format_path(upx_path))
                return
        found_path = None
        # 1. 从 PATH 中查找
        for cmd in ['upx', 'upx.exe']:
            path = shutil.which(cmd)
            if path and os.path.exists(path):
                found_path = path
                break
        # 2. Windows: 使用 where 命令
        if not found_path and sys.platform == 'win32':
            try:
                result = self._run_hidden(['where', 'upx'], capture_output=True, text=True, timeout=3,
                                        startupinfo=get_startupinfo())
                if result.returncode == 0 and result.stdout.strip():
                    found_path = result.stdout.strip().split('\n')[0]
            except:
                pass
        # 3. Linux/macOS: 使用 which 命令
        if not found_path:
            try:
                result = self._run_hidden(['which', 'upx'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0 and result.stdout.strip():
                    found_path = result.stdout.strip()
            except:
                pass
        # 4. 常见默认路径
        if not found_path:
            common_paths = []
            if sys.platform == 'win32':
                common_paths = [
                    r'C:\upx\upx.exe',
                    r'C:\Program Files\upx\upx.exe',
                    os.path.join(get_exe_directory(), 'tools', 'upx', 'upx.exe'),
                ]
            else:
                common_paths = [
                    '/usr/bin/upx',
                    '/usr/local/bin/upx',
                    '/opt/homebrew/bin/upx',
                ]
            for path in common_paths:
                if os.path.exists(path):
                    found_path = path
                    break
        if found_path:
            # 统一后缀
            if sys.platform == 'win32' and found_path.lower().endswith('.exe'):
                base, ext = os.path.splitext(found_path)
                found_path = base + '.exe'
            self._set_upx_environment(found_path)
            formatted_path = self._format_path(found_path)
            self.upx_path.setText(formatted_path)
            cache['upx'] = {'path': formatted_path}
            save_cache(cache)
        else:
            self.safe_log("⚠️ 未找到UPX，请手动指定路径")

    def _set_upx_path(self, path):
        """在主线程中设置UPX路径（跨平台）"""
        if path and os.path.exists(path):
            # 统一将 .EXE 后缀转为 .exe
            if path.lower().endswith('.exe'):
                base = path[:-4]
                path = base + '.exe'
            self.upx_path.setText(path)
            self.upx_path.setPlaceholderText("")
            self.upx_path.setToolTip(f"UPX: {path}")
        else:
            self.upx_path.setText("")

    def _set_upx_environment(self, upx_path):
        """设置 UPX 环境变量（当前进程生效）"""
        if not upx_path or not os.path.exists(upx_path):
            return
        upx_dir = os.path.dirname(upx_path)
        # 设置 UPX 相关环境变量
        os.environ['UPX'] = upx_path
        os.environ['UPX_DIR'] = upx_dir
        # 添加到 PATH（临时，当前进程生效）
        current_path = os.environ.get('PATH', '')
        if upx_dir not in current_path:
            os.environ['PATH'] = upx_dir + os.pathsep + current_path

    def _is_valid_python(self, exe_path):
        """统一的Python验证函数"""
        if not exe_path or not os.path.exists(exe_path):
            return False
        basename = os.path.basename(exe_path).lower()
        # ===== 1. 文件名必须包含 python =====
        if basename.endswith('.exe') and 'python' not in basename:
            return False
        # ===== 2. 排除自身 =====
        if getattr(sys, 'frozen', False):
            try:
                if os.path.samefile(exe_path, sys.executable):
                    return False
            except:
                if exe_path.lower() == sys.executable.lower():
                    return False
        # ===== 3. 排除临时解压目录（增强版） =====
        path_lower = exe_path.lower()
        # PyInstaller
        if '_mei' in path_lower:
            return False
        # Nuitka onefile
        if 'onefile_' in path_lower:
            return False
        # Nuitka 的其他临时目录
        if 'nuitka' in path_lower and ('temp' in path_lower or 'cache' in path_lower):
            return False
        # 排除当前 exe 所在目录下的所有 .exe（除了 python.exe）
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable).lower()
            try:
                if os.path.normcase(os.path.dirname(exe_path)) == os.path.normcase(exe_dir):
                    # 同目录下，只有 python*.exe 才是 Python
                    if not basename.startswith('python'):
                        return False
            except:
                pass
        # ===== 4. 执行 --version 验证 =====
        try:
            if sys.platform == 'win32':
                result = subprocess.run(
                    [exe_path, '--version'],
                    capture_output=True, text=True, timeout=2,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                result = subprocess.run(
                    [exe_path, '--version'],
                    capture_output=True, text=True, timeout=2
                )
            return result.returncode == 0 and ('Python' in result.stdout or 'Python' in result.stderr)
        except:
            return False

    def _async_find_python(self):
        """异步查找Python - 含调试日志"""
        import shutil
        import re
        import glob
        import time
        from collections import OrderedDict

        def is_valid_python(exe_path):
            if not exe_path or not os.path.exists(exe_path):
                return False
            if getattr(sys, 'frozen', False):
                try:
                    if os.path.samefile(exe_path, sys.executable):
                        return False
                except:
                    if exe_path.lower() == sys.executable.lower():
                        return False
            basename = os.path.basename(exe_path).lower()
            if sys.platform == 'win32':
                pattern = r'^python\d*(?:\.\d+)?\.exe$'
            else:
                pattern = r'^python\d*(?:\.\d+)?$'
            if re.match(pattern, basename):
                return True
            try:
                result = self._run_hidden([exe_path, '--version'],
                                          capture_output=True, text=True, timeout=2)
                return result.returncode == 0 and ('Python' in result.stdout or 'Python' in result.stderr)
            except:
                return False

        def get_python_version(py_path):
            try:
                result = self._run_hidden([py_path, '--version'],
                                          capture_output=True, text=True, timeout=2)
                return result.stdout.strip() or result.stderr.strip()
            except:
                return ""
        python_dict = OrderedDict()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        common_venv_path = None
        # ===== 1. 查找 common_venv =====
        exe_dir = get_exe_directory()
        common_venv_dir = os.path.join(exe_dir, "common_venv")
        if sys.platform == 'win32':
            common_venv_exe = os.path.join(common_venv_dir, "Scripts", "python.exe")
        else:
            common_venv_exe = os.path.join(common_venv_dir, "bin", "python")
        if os.path.exists(common_venv_exe) and is_valid_python(common_venv_exe):
            common_venv_path = common_venv_exe
            ver = get_python_version(common_venv_exe)
            python_dict[common_venv_exe] = (ver, "common_venv")
        # ===== 2. 查找项目 venv/.venv =====
        for base_dir in [script_dir, current_dir]:
            venv_paths = [
                os.path.join(base_dir, '.venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, '.venv', 'bin', 'python'),
                os.path.join(base_dir, 'venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, 'venv', 'bin', 'python'),
            ]
            for path in venv_paths:
                if is_valid_python(path) and path not in python_dict:
                    if path != common_venv_path:
                        ver = get_python_version(path)
                        python_dict[path] = (ver, "venv")
        # ===== 3. 查找系统Python =====
        if sys.platform == 'win32':
            for cmd in ['python', 'python3']:
                try:
                    result = self._run_hidden(['where', cmd], capture_output=True, text=True, timeout=3)
                    if result.returncode == 0 and result.stdout.strip():
                        for line in result.stdout.strip().split('\n'):
                            line = line.strip()
                            if is_valid_python(line) and line not in python_dict:
                                if line != common_venv_path:
                                    ver = get_python_version(line)
                                    if 'venv' in line.lower() or '.venv' in line.lower():
                                        python_dict[line] = (ver, "venv")
                                    else:
                                        python_dict[line] = (ver, "system")
                except:
                    pass
            username = os.environ.get('USERNAME', '')
            search_patterns = [
                r'C:\Python*',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python*',
                r'C:\Program Files\Python*',
            ]
            for pattern in search_patterns:
                for path in glob.glob(pattern):
                    if os.path.isdir(path):
                        exe = os.path.join(path, 'python.exe')
                        if is_valid_python(exe) and exe not in python_dict:
                            if exe != common_venv_path:
                                ver = get_python_version(exe)
                                python_dict[exe] = (ver, "system")
        else:
            for cmd in ['python3', 'python']:
                try:
                    result = self._run_hidden(['which', cmd], capture_output=True, text=True, timeout=3)
                    if result.returncode == 0 and result.stdout.strip():
                        path = result.stdout.strip()
                        if is_valid_python(path) and path not in python_dict:
                            if path != common_venv_path:
                                ver = get_python_version(path)
                                if 'venv' in path.lower() or '.venv' in path.lower():
                                    python_dict[path] = (ver, "venv")
                                else:
                                    python_dict[path] = (ver, "system")
                except:
                    pass
            common_paths = [
                '/usr/bin/python3', '/usr/bin/python',
                '/usr/local/bin/python3', '/usr/local/bin/python',
                '/opt/homebrew/bin/python3', '/opt/homebrew/bin/python',
            ]
            for path in common_paths:
                if is_valid_python(path) and path not in python_dict:
                    if path != common_venv_path:
                        ver = get_python_version(path)
                        python_dict[path] = (ver, "system")
        # ===== 4. 源码模式添加当前 Python =====
        if not getattr(sys, 'frozen', False):
            if is_valid_python(sys.executable) and sys.executable not in python_dict:
                if sys.executable != common_venv_path:
                    ver = get_python_version(sys.executable)
                    if 'venv' in sys.executable.lower() or '.venv' in sys.executable.lower():
                        python_dict[sys.executable] = (ver, "venv")
                    else:
                        python_dict[sys.executable] = (ver, "current")
        # ===== 5. 如果 common_venv 被漏掉了，强制加入 =====
        if common_venv_path and common_venv_path not in python_dict:
            ver = get_python_version(common_venv_path)
            python_dict[common_venv_path] = (ver, "common_venv")
        if python_dict:
            def update_ui():
                if not hasattr(self, 'python_path') or self.python_path is None:
                    QTimer.singleShot(100, update_ui)
                    return
                # ===== 强制排序并打印分类过程 =====
                project_venv = []
                system_py = []
                common_venv = []
                for path, (ver, ptype) in python_dict.items():
                    path_lower = path.lower()
                    if 'common_venv' in path_lower:
                        common_venv.append((path, ver, "common_venv"))
                    elif '.venv' in path_lower:
                        project_venv.append((path, ver, "venv"))
                    else:
                        system_py.append((path, ver, "system"))
                # 排序：项目 venv → 系统 → common_venv
                sorted_items = project_venv + system_py + common_venv
                self.python_path.clear()
                for path, ver, ptype in sorted_items:
                    if not self._is_valid_python(path):
                         continue 
                    self.python_path.addItem(path)
                if sorted_items:
                    self.python_path.setCurrentIndex(0)
                    selected_path, selected_ver, selected_type = sorted_items[0]
                    if selected_ver:
                        self.python_version.setText(selected_ver)
                        type_label = {
                            "venv": "venv",
                            "current": "当前",
                            "common_venv": "公用虚拟环境",
                            "system": "系统"
                        }.get(selected_type, "Python")
                        self.status_python.setText(f"🐍 {type_label}: {selected_ver}")
                        self.safe_log(f"✅ 自动选择 {type_label}: {selected_path} ({selected_ver})")
                    else:
                        self.status_python.setText(f"🐍 Python: {selected_path}")
                        self.safe_log(f"✅ 自动选择Python: {selected_path}")
                self._python_types_cache = {p: t for p, (_, t) in python_dict.items()}
                self.save_cache()
                self._on_python_selected()
            QTimer.singleShot(0, update_ui)
        else:
            self.safe_log("⚠️ 未找到任何有效的 Python 解释器")

    def _add_python_to_list(self, python_path, version):
        """把Python添加到下拉列表（不选中）"""
        from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
        if not self._is_valid_python(python_path):
            return

        def do_add():
            index = self.python_path.findText(python_path)
            if index < 0:
                self.python_path.addItem(python_path)
        if QThread.currentThread() != QApplication.instance().thread():
            QMetaObject.invokeMethod(self, "_add_python_to_list_safe",
                                     Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(str, python_path))
        else:
            do_add()

    def _add_python_to_list_safe(self, python_path):
        """线程安全地添加Python到列表（由 invokeMethod 调用）"""
        if not self._is_valid_python(python_path):
            return
        index = self.python_path.findText(python_path)
        if index < 0:
            # ===== 如果是 venv，插入到最前面 =====
            if '.venv' in python_path.lower() or 'venv' in python_path.lower():
                self.python_path.insertItem(0, python_path)
                self.python_path.setCurrentIndex(0)
            else:
                self.python_path.addItem(python_path)

    def _set_python_ui(self, python_path, version):
        """设置Python UI（主线程执行）"""
        if not self._is_valid_python(python_path):
            return
        # ===== 保存缓存 =====
        cache = load_cache()
        cache['python'] = {'path': python_path, 'version': version, 'time': time.time()}
        save_cache(cache)
        index = self.python_path.findText(python_path)
        if index < 0:
            self.python_path.addItem(python_path)
            index = self.python_path.findText(python_path)
        if index >= 0:
            self.python_path.setCurrentIndex(index)
        self.python_version.setText(version)
        self.status_python.setText(f"🐍 Python: {version}")
        self.safe_log(f"✅ 自动选择Python: {python_path}")
        # ===== 触发后续逻辑 =====
        self._on_python_selected()

    def _update_python_found(self, python_path, version):
        """主线程中更新Python找到后的UI"""
        # ===== 先检查是否已存在 =====
        if not self._is_valid_python(python_path):
            return
        index = self.python_path.findText(python_path)
        if index >= 0:
            self.python_path.setCurrentIndex(index)
        else:
            self.python_path.addItem(python_path)
            self.python_path.setCurrentText(python_path)
        self.python_version.setText(version)
        self.status_python.setText(f"🐍 Python: {version}")
        self.safe_log(f"✅ 自动选择Python: {python_path}")
        # ===== 保存缓存 =====
        cache = load_cache()
        cache['python'] = {'path': python_path, 'version': version, 'time': time.time()}
        save_cache(cache)
        # ===== 触发后续逻辑 =====
        self._on_python_selected()

    def _detect_rust_async(self):
        """异步检测Rust"""
        self.status_compiler.setText("⏳ 检测Rust...")
        self.status_compiler.setStyleSheet("color: orange;")

        def detect():
            has_cargo, cargo_path = self._check_cargo_with_path()
            has_rustc, rustc_path = self._check_rustc_with_path()
            rust_version = self._get_rust_version(rustc_path) if has_rustc else ""
            self._cached_has_cargo = has_cargo
            self._cached_has_rustc = has_rustc
            self._cached_cargo_path = cargo_path
            self._cached_rustc_path = rustc_path
            self._cached_rust_version = rust_version
            self.save_cache()
            self.safe_log(f"💾 已保存Rust信息")
            QTimer.singleShot(0, self._display_rust_status)
        threading.Thread(target=detect, daemon=True).start()

    def _async_find_system_python(self):
        """异步查找系统Python（打包模式）"""
        import shutil
        import glob
        import time
        import re
        from collections import OrderedDict

        def is_valid_python(path):
            if not path or not os.path.exists(path):
                return False
            if getattr(sys, 'frozen', False):
                try:
                    if os.path.samefile(path, sys.executable):
                        return False
                except:
                    if path.lower() == sys.executable.lower():
                        return False
            try:
                import subprocess
                if sys.platform == 'win32':
                    result = subprocess.run(
                        [path, '--version'],
                        capture_output=True, text=True, timeout=2,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        [path, '--version'],
                        capture_output=True, text=True, timeout=2
                    )
                return result.returncode == 0 and ('Python' in result.stdout or 'Python' in result.stderr)
            except:
                return False

        def get_python_version(py_path):
            try:
                import subprocess
                if sys.platform == 'win32':
                    result = subprocess.run(
                        [py_path, '--version'],
                        capture_output=True, text=True, timeout=2,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    result = subprocess.run(
                        [py_path, '--version'],
                        capture_output=True, text=True, timeout=2
                    )
                return result.stdout.strip() or result.stderr.strip()
            except:
                return ""
        python_dict = OrderedDict()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        for base_dir in [script_dir, current_dir]:
            venv_paths = [
                os.path.join(base_dir, '.venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, '.venv', 'bin', 'python'),
                os.path.join(base_dir, 'venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, 'venv', 'bin', 'python'),
            ]
            for path in venv_paths:
                if is_valid_python(path) and path not in python_dict:
                    ver = get_python_version(path)
                    python_dict[path] = (ver, "venv")
        if sys.platform == 'win32':
            for cmd in ['python', 'python3']:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['where', cmd],
                        capture_output=True, text=True, timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        for line in result.stdout.strip().split('\n'):
                            line = line.strip()
                            if is_valid_python(line) and line not in python_dict:
                                ver = get_python_version(line)
                                python_dict[line] = (ver, "system")
                except:
                    pass
            username = os.environ.get('USERNAME', '')
            search_patterns = [
                r'C:\Python*',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python*',
                r'C:\Program Files\Python*',
            ]
            for pattern in search_patterns:
                for path in glob.glob(pattern):
                    if os.path.isdir(path):
                        exe = os.path.join(path, 'python.exe')
                        if is_valid_python(exe) and exe not in python_dict:
                            ver = get_python_version(exe)
                            python_dict[exe] = (ver, "system")
        else:
            for cmd in ['python3', 'python']:
                try:
                    import subprocess
                    result = subprocess.run(
                        ['which', cmd],
                        capture_output=True, text=True, timeout=3
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        path = result.stdout.strip()
                        if is_valid_python(path) and path not in python_dict:
                            ver = get_python_version(path)
                            python_dict[path] = (ver, "system")
                except:
                    pass
            common_paths = [
                '/usr/bin/python3', '/usr/bin/python',
                '/usr/local/bin/python3', '/usr/local/bin/python',
                '/opt/homebrew/bin/python3', '/opt/homebrew/bin/python',
            ]
            for path in common_paths:
                if is_valid_python(path) and path not in python_dict:
                    ver = get_python_version(path)
                    python_dict[path] = (ver, "system")
        if python_dict:
            def update_ui():
                self.python_path.clear()
                for path, (ver, ptype) in python_dict.items():
                    self.python_path.addItem(path)
                self.python_path.setCurrentIndex(0)
                selected_path = list(python_dict.keys())[0]
                selected_ver, selected_type = python_dict[selected_path]
                if selected_ver:
                    self.python_version.setText(selected_ver)
                    type_label = "venv" if selected_type == "venv" else "Python"
                    self.status_python.setText(f"🐍 {type_label}: {selected_ver}")
                    self.safe_log(f"✅ 自动选择 {type_label}: {selected_path} ({selected_ver})")
                else:
                    self.status_python.setText(f"🐍 Python: {selected_path}")
                    self.safe_log(f"✅ 自动选择Python: {selected_path}")
                venv_count = len([p for p, (_, t) in python_dict.items() if t == "venv"])
                total_count = len(python_dict)
                self.safe_log(f"📋 找到 {total_count} 个Python (其中 {venv_count} 个 venv)")
                self._python_types_cache = {p: t for p, (_, t) in python_dict.items()}
                self.save_cache()
                self._on_python_selected()
            QTimer.singleShot(0, update_ui)
        else:
            self.safe_log("⚠️ 未找到任何有效的 Python 解释器")

    def _set_system_python_ui(self, py_path):
        """设置系统Python到UI（主线程调用）"""
        if not py_path or not os.path.exists(py_path):
            return
        # 保存到实例变量
        self.python_exe = py_path
        # 添加到下拉列表
        if not self._is_valid_python(py_path):
            return
        idx = self.python_path.findText(py_path)
        if idx < 0:
            self.python_path.addItem(py_path)
            idx = self.python_path.findText(py_path)
        if idx >= 0:
            self.python_path.setCurrentIndex(idx)
        # 获取版本
        try:
            result = self._run_hidden([py_path, '--version'], capture_output=True, text=True, timeout=3)
            ver = result.stdout.strip() or result.stderr.strip()
            if ver:
                self.python_version.setText(ver)
                self.status_python.setText(f"🐍 {ver}")
                self.safe_log(f"✅ 找到系统Python: {py_path} ({ver})")
            else:
                self.safe_log(f"✅ 找到系统Python: {py_path}")
        except Exception as e:
            self.safe_log(f"✅ 找到系统Python: {py_path}")
        # 保存到缓存
        cache = load_cache()
        cache['python'] = {'path': py_path, 'version': self.python_version.text()}
        save_cache(cache)
        # 触发后续逻辑
        self._on_python_selected()

    def _find_system_python(self):
        """查找系统Python（打包模式专用，优先venv）"""
        import shutil

        def is_valid_python(path):
            if not path or not os.path.exists(path):
                return False
            if getattr(sys, 'frozen', False):
                try:
                    if os.path.samefile(path, sys.executable):
                        return False
                except:
                    if path.lower() == sys.executable.lower():
                        return False
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True, text=True, timeout=2,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                return result.returncode == 0 and ('Python' in result.stdout or 'Python' in result.stderr)
            except:
                return False
        # ===== 1. 优先找 venv/.venv =====
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        for base_dir in [script_dir, current_dir]:
            venv_paths = [
                os.path.join(base_dir, '.venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, '.venv', 'bin', 'python'),
                os.path.join(base_dir, 'venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, 'venv', 'bin', 'python'),
            ]
            for path in venv_paths:
                if is_valid_python(path):
                    return path
        # ===== 2. Windows: py launcher =====
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['py', '-c', 'import sys; print(sys.executable)'],
                    capture_output=True, text=True, timeout=3,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0 and result.stdout.strip():
                    py_path = result.stdout.strip()
                    if is_valid_python(py_path):
                        return py_path
            except:
                pass
        # ===== 3. PATH 中的 python =====
        for cmd in ['python3', 'python']:
            path = shutil.which(cmd)
            if path and is_valid_python(path):
                return path
        # ===== 4. 扫描常见安装路径 =====
        if sys.platform == 'win32':
            username = os.environ.get('USERNAME', '')
            default_paths = [
                r'C:\Python312\python.exe',
                r'C:\Python311\python.exe',
                r'C:\Python310\python.exe',
                r'C:\Python39\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python312\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python311\python.exe',
                rf'C:\Users\{username}\AppData\Local\Programs\Python\Python310\python.exe',
            ]
            # 使用 glob 扫描
            import glob
            for pattern in [r'C:\Python*', rf'C:\Users\{username}\AppData\Local\Programs\Python\Python*']:
                for p in glob.glob(pattern):
                    if os.path.isdir(p):
                        exe = os.path.join(p, 'python.exe')
                        if is_valid_python(exe):
                            return exe
        elif sys.platform == 'darwin':
            default_paths = [
                '/usr/local/bin/python3',
                '/usr/bin/python3',
                '/opt/homebrew/bin/python3',
            ]
        else:
            default_paths = [
                '/usr/bin/python3',
                '/usr/local/bin/python3',
                '/usr/bin/python',
            ]
        for path in default_paths:
            if is_valid_python(path):
                return path
        return None

    def _async_load_config(self):
        try:
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
                    python_path = cache.get('python_path', '')
                    if python_path and os.path.exists(python_path):
                        self._set_python_path(python_path)
        except: pass

    def _check_packer_version_async(self, packer_name):
        """通用异步检测打包器版本"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.status_packer.setText(f"📦 {packer_name}: 等待Python...")
            self.status_packer.setStyleSheet("color: orange;")
            return
        # ===== 统一打包器显示名称 =====
        display = self._get_packer_display_name(packer_name)
        cache_key = f"{display}@{python_exe}"
        # ===== 先读内存缓存 =====
        if cache_key in self._packer_version_cache:
            version = self._packer_version_cache[cache_key]
            self._update_packer_status(display, version or "")
            return
        # ===== 再读文件缓存 =====
        try:
            cache = load_cache()
            packer_versions = cache.get('packer_versions', {})
            version = packer_versions.get(cache_key)
            if version is not None:
                self._packer_version_cache[cache_key] = version
                self._update_packer_status(display, version or "")
                return
        except:
            pass
        # ===== 缓存未命中，显示检测中 =====
        self.status_packer.setText(f"📦 {display}: 检测中...")
        self.status_packer.setStyleSheet("color: orange;")

        def detect():
            version = self._check_packer_version(packer_name, python_exe)
            self._packer_version_cache[cache_key] = version
            # 保存到文件缓存
            try:
                cache = load_cache()
                if 'packer_versions' not in cache:
                    cache['packer_versions'] = {}
                cache['packer_versions'][cache_key] = version
                save_cache(cache)
            except:
                pass
            # 更新UI
            QTimer.singleShot(0, lambda: self._update_packer_status(display, version or ""))
        threading.Thread(target=detect, daemon=True).start()

    def _update_rust_compiler_status(self):
        """更新 Rust 编译器状态 - 先读缓存，没有才检测"""
        # ===== 从缓存读取 =====
        cache = load_cache()
        compiler_cache = cache.get('rust_compiler', {})
        has_cargo = compiler_cache.get('has_cargo', False)
        has_rustc = compiler_cache.get('has_rustc', False)
        cargo_path = compiler_cache.get('cargo_path', '')
        rustc_path = compiler_cache.get('rustc_path', '')
        # ===== 有缓存直接使用 =====
        if has_cargo or has_rustc:
            self._update_rust_compiler_status_result(has_cargo, has_rustc, cargo_path, rustc_path)
            return
        # ===== 没有缓存才检测 =====
        self.status_compiler.setText("⏳ 检测Rust...")
        self.status_compiler.setStyleSheet("color: orange;")

        def detect():
            has_cargo, cargo_path = self._check_cargo_with_path()
            has_rustc, rustc_path = self._check_rustc_with_path()
            rust_version = self._get_rust_version(rustc_path) if has_rustc else ""
            self._cached_has_cargo = has_cargo
            self._cached_has_rustc = has_rustc
            self._cached_cargo_path = cargo_path
            self._cached_rustc_path = rustc_path
            self._cached_rust_version = rust_version
            self._save_all_backend_cache()
            QTimer.singleShot(0, lambda: self._update_rust_compiler_status_result(
                has_cargo, has_rustc, cargo_path, rustc_path
            ))
        threading.Thread(target=detect, daemon=True).start()

    def _check_cargo_with_path(self):
        """检测 Cargo 是否可用，并返回路径（跨平台）"""
        # 1. 检查 cargo 是否在 PATH 中
        cargo_path = shutil.which("cargo")
        if cargo_path and os.path.exists(cargo_path):
            # ===== 统一后缀为小写 =====
            if sys.platform == 'win32' and cargo_path.lower().endswith('.exe'):
                cargo_path = cargo_path[:-4] + '.exe'
            return True, cargo_path
        # 2. 检查常见安装路径
        if sys.platform == 'win32':
            # Windows 常见路径
            username = os.environ.get('USERNAME', '')
            cargo_paths = [
                rf"C:\Users\{username}\.cargo\bin\cargo.exe",
                r"C:\Program Files\Rust stable GNU 1.70\bin\cargo.exe",
                r"C:\Program Files\Rust stable MSVC 1.70\bin\cargo.exe",
                os.path.join(get_exe_directory(), "tools", "cargo", "bin", "cargo.exe"),
            ]
            for path in cargo_paths:
                if os.path.exists(path):
                    return True, path
        else:
            # Linux/macOS 常见路径
            username = os.environ.get('USER', '')
            cargo_paths = [
                '/usr/bin/cargo',
                '/usr/local/bin/cargo',
                '/opt/homebrew/bin/cargo',  # macOS Homebrew
                f'/home/{username}/.cargo/bin/cargo',
            ]
            for path in cargo_paths:
                if os.path.exists(path):
                    return True, path
        # 3. 尝试用 cargo --version 检测
        try:
            result = self._run_hidden(
                ['cargo', '--version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                cargo_path = shutil.which("cargo")
                if cargo_path:
                    return True, cargo_path
        except:
            pass
        return False, ""

    def _check_rustc_with_path(self):
        """检测 Rustc 是否可用，并返回路径（跨平台）"""
        # 1. 检查 rustc 是否在 PATH 中
        rustc_path = shutil.which("rustc")
        if rustc_path and os.path.exists(rustc_path):
            # ===== 统一后缀为小写 =====
            if sys.platform == 'win32' and rustc_path.lower().endswith('.exe'):
                rustc_path = rustc_path[:-4] + '.exe'
            return True, rustc_path
        # 2. 检查常见安装路径
        if sys.platform == 'win32':
            username = os.environ.get('USERNAME', '')
            rustc_paths = [
                rf"C:\Users\{username}\.cargo\bin\rustc.exe",
                r"C:\Program Files\Rust stable GNU 1.70\bin\rustc.exe",
                r"C:\Program Files\Rust stable MSVC 1.70\bin\rustc.exe",
                os.path.join(get_exe_directory(), "tools", "cargo", "bin", "rustc.exe"),
            ]
            for path in rustc_paths:
                if os.path.exists(path):
                    return True, path
        else:
            username = os.environ.get('USER', '')
            rustc_paths = [
                '/usr/bin/rustc',
                '/usr/local/bin/rustc',
                '/opt/homebrew/bin/rustc',  # macOS Homebrew
                f'/home/{username}/.cargo/bin/rustc',
            ]
            for path in rustc_paths:
                if os.path.exists(path):
                    return True, path
        # 3. 尝试用 rustc --version 检测
        try:
            result = self._run_hidden(
                ['rustc', '--version'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                rustc_path = shutil.which("rustc")
                if rustc_path:
                    return True, rustc_path
        except:
            pass
        return False, ""

    def _detect_compilers_async(self):
        """后台检测编译器"""
        if self._cached_has_msvc or self._cached_has_mingw:
            self._display_compiler_status()
            return
        cache = load_cache()
        compiler_cache = cache.get('compiler', {})
        if compiler_cache:
            has_msvc = compiler_cache.get('msvc', False)
            has_mingw = compiler_cache.get('mingw', False)
            msvc_path = compiler_cache.get('msvc_path', '')
            mingw_path = compiler_cache.get('mingw_path', '')
            self._cached_has_msvc = has_msvc
            self._cached_has_mingw = has_mingw
            self._cached_msvc_path = msvc_path
            self._cached_mingw_path = mingw_path
            self._update_compiler_status_result(has_msvc, has_mingw, msvc_path, mingw_path)
            return

        def detect():
            has_msvc, msvc_path = self._check_msvc_with_path()
            has_mingw, mingw_path = self._check_mingw_with_path()
            msvc_version = self._get_compiler_version(msvc_path, "msvc") if has_msvc else ""
            mingw_version = self._get_compiler_version(mingw_path, "mingw") if has_mingw else ""
            self._cached_has_msvc = has_msvc
            self._cached_has_mingw = has_mingw
            self._cached_msvc_path = msvc_path
            self._cached_mingw_path = mingw_path
            self._cached_msvc_version = msvc_version
            self._cached_mingw_version = mingw_version
            self.save_cache()
            QTimer.singleShot(0, lambda: self._update_compiler_status_result(
                has_msvc, has_mingw, msvc_path, mingw_path
            ))
        threading.Thread(target=detect, daemon=True).start()

    def _update_compiler_status_result(self, has_msvc, has_mingw, msvc_path="", mingw_path="", backend=None):
        """更新编译器状态UI（主线程）- 直接设置 status_compiler"""
        self._cached_has_msvc = has_msvc
        self._cached_has_mingw = has_mingw
        self._cached_msvc_path = msvc_path
        self._cached_mingw_path = mingw_path
        # ===== 如果未传入backend，从下拉框获取 =====
        if backend is None:
            backend = self.nuitka_backend_combo.currentText() if self.nuitka_backend_combo else "auto"
        # ===== 获取编译器版本 =====
        msvc_version = ""
        mingw_version = ""
        if has_msvc and msvc_path:
            msvc_version = self._get_compiler_version(msvc_path, "msvc")
        if has_mingw and mingw_path:
            mingw_version = self._get_compiler_version(mingw_path, "mingw")
        self._cached_msvc_version = msvc_version
        self._cached_mingw_version = mingw_version
        # ===== 直接设置 status_compiler =====
        if backend == "MSVC":
            if has_msvc and msvc_version:
                self.status_compiler.setText(f"🔧 MSVC: {msvc_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 MSVC: 未安装")
                self.status_compiler.setStyleSheet("color: red;")
        elif backend == "MinGW64":
            if has_mingw and mingw_version:
                self.status_compiler.setText(f"🔧 MinGW: {mingw_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 MinGW: 未安装")
                self.status_compiler.setStyleSheet("color: red;")
        else:  # auto
            if has_mingw and mingw_version:
                self.status_compiler.setText(f"🔧 MinGW: {mingw_version}")
                self.status_compiler.setStyleSheet("color: green;")
            elif has_msvc and msvc_version:
                self.status_compiler.setText(f"🔧 MSVC: {msvc_version}")
                self.status_compiler.setStyleSheet("color: green;")
            else:
                self.status_compiler.setText("🔧 编译器: 未安装")
                self.status_compiler.setStyleSheet("color: red;")

    def _on_backend_changed(self, backend):
        """用户切换后端时立即更新（从缓存读取）"""
        packer = self.packer_combo.currentText()
        if packer == "Nuitka":
            self._display_compiler_status()
            self._save_all_backend_cache()
            self.safe_log(f"🔧 切换后端: {backend}")

    def _detect_single_packer_async(self, packer_name):
        """只检测单个打包器（首次使用时）"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            return
        display = self._get_packer_display_name(packer_name)
        cache_key = f"{display}@{python_exe}"
        if cache_key in self._packer_versions_cache:
            return
        self.status_packer.setText(f"📦 {display}: 检测中...")
        self.status_packer.setStyleSheet("color: orange;")

        def detect():
            version = self._check_packer_version(packer_name, python_exe)
            self._packer_versions_cache[cache_key] = version
            self._save_all_backend_cache()
            QTimer.singleShot(0, lambda: self._update_packer_status(display, version or ""))
        threading.Thread(target=detect, daemon=True).start()

    def _detect_all_backends_async(self):
        """后台一次性检测所有后端"""

        def detect():
            # ===== 检测编译器 =====
            has_msvc, msvc_path = self._check_msvc_with_path()
            has_mingw, mingw_path = self._check_mingw_with_path()
            # ===== 关键修复：传入正确的路径获取版本 =====
            msvc_version = ""
            mingw_version = ""
            if has_msvc and msvc_path:
                msvc_version = self._get_compiler_version(msvc_path, "msvc")
            if has_mingw and mingw_path:
                mingw_version = self._get_compiler_version(mingw_path, "mingw")
            self._cached_has_msvc = has_msvc
            self._cached_has_mingw = has_mingw
            self._cached_msvc_path = msvc_path
            self._cached_mingw_path = mingw_path
            self._cached_msvc_version = msvc_version
            self._cached_mingw_version = mingw_version
            # ===== 检测Rust =====
            has_cargo, cargo_path = self._check_cargo_with_path()
            has_rustc, rustc_path = self._check_rustc_with_path()
            rust_version = ""
            if has_rustc and rustc_path:
                rust_version = self._get_rust_version(rustc_path)
            self._cached_has_cargo = has_cargo
            self._cached_has_rustc = has_rustc
            self._cached_cargo_path = cargo_path
            self._cached_rustc_path = rustc_path
            self._cached_rust_version = rust_version
            # ===== 检测NSIS =====
            has_nsis, nsis_path = self._check_nsis_with_path()
            nsis_version = ""
            if has_nsis and nsis_path:
                nsis_version = self._get_nsis_version(nsis_path)
            self._cached_has_nsis = has_nsis
            self._cached_nsis_path = nsis_path
            self._cached_nsis_version = nsis_version
            # ===== 检测所有打包器版本 =====
            python_exe = self.python_path.currentText()
            if python_exe and os.path.exists(python_exe):
                for packer in ["PyInstaller", "Nuitka", "PyApp", "Py2exe",
                               "Cx_Freeze", "Pynsist", "PyOxidizer", "Py2app"]:
                    cache_key = f"{packer}@{python_exe}"
                    if cache_key not in self._packer_versions_cache:
                        version = self._check_packer_version(packer, python_exe)
                        self._packer_versions_cache[cache_key] = version
            # ===== 保存所有缓存 =====
            self._save_all_backend_cache()
            QTimer.singleShot(0, self._update_all_backend_ui)
        threading.Thread(target=detect, daemon=True).start()

    def _show_packer_version_from_cache(self, display, python_path):
        """从缓存显示打包器版本"""
        cache_key = f"{display}@{python_path}"
        version = self._packer_versions_cache.get(cache_key)
        if version:
            self._update_packer_status(display, version)

    def _get_compiler_version(self, compiler_path, compiler_type="mingw"):
        """获取编译器版本号"""
        try:
            if compiler_type == "mingw":
                result = self._run_hidden(
                    [compiler_path, "--version"],
                    capture_output=True, text=True, timeout=10,
                    startupinfo=get_startupinfo()
                )
                output = result.stdout.strip() or result.stderr.strip()
                if output:
                    import re
                    match = re.search(r'(\d+\.\d+\.\d+)', output)
                    if match:
                        return match.group(1)
                return "已安装"
            elif compiler_type == "msvc":
                # ===== 方法1：运行 cl.exe 获取版本（优先） =====
                try:
                    result = self._run_hidden(
                        [compiler_path],
                        capture_output=True, text=True, timeout=10,
                        startupinfo=get_startupinfo()
                    )
                    output = result.stderr.strip() or result.stdout.strip()
                    if output:
                        import re
                        # 匹配中文 "编译器 19.44.35227"
                        match = re.search(r'编译器\s+(\d+\.\d+\.\d+)', output)
                        if match:
                            return match.group(1)
                        # 匹配 "Version 19.44.35227"
                        match = re.search(r'[Vv]ersion\s+(\d+\.\d+\.\d+)', output)
                        if match:
                            return match.group(1)
                        # 匹配纯数字
                        match = re.search(r'(\d+\.\d+\.\d+)', output)
                        if match:
                            return match.group(1)
                except Exception as e:
                    self.safe_log(f"⚠️ 运行MSVC失败: {e}")
                # ===== 方法2：从路径提取版本号（备选） =====
                import re
                match = re.search(r'MSVC[\\/](\d+\.\d+\.\d+)', compiler_path, re.IGNORECASE)
                if match:
                    return match.group(1)
                return "已安装"
        except Exception as e:
            self.safe_log(f"⚠️ 获取编译器版本失败: {e}")
            return "已安装"
        return "已安装"

    def _update_rust_compiler_status_result(self, has_cargo, has_rustc, cargo_path="", rustc_path=""):
        """更新 Rust 编译器状态UI（主线程）- 显示版本"""
        # 保存到实例变量
        self._cached_has_cargo = has_cargo
        self._cached_has_rustc = has_rustc
        self._cached_cargo_path = cargo_path
        self._cached_rustc_path = rustc_path
        # ===== 获取 Rust 版本 =====
        rust_version = ""
        if has_rustc and rustc_path:
            rust_version = self._get_rust_version(rustc_path)
        if has_cargo and has_rustc:
            self.compiler_label.setText(f"🔧 Rust: {rust_version}")
            self.compiler_label.setStyleSheet("color: green;")
            if cargo_path and rustc_path:
                self.compiler_label.setToolTip(f"Cargo: {cargo_path}\nRustc: {rustc_path}")
        elif has_cargo:
            self.compiler_label.setText("🔧 Rust: 缺少 rustc")
            self.compiler_label.setStyleSheet("color: orange;")
            self.compiler_label.setToolTip("Cargo 已安装，但 rustc 未找到")
        elif has_rustc:
            self.compiler_label.setText("🔧 Rust: 缺少 cargo")
            self.compiler_label.setStyleSheet("color: orange;")
            self.compiler_label.setToolTip("Rustc 已安装，但 cargo 未找到")
        else:
            self.compiler_label.setText("🔧 Rust: 未安装")
            self.compiler_label.setStyleSheet("color: red;")
            self.compiler_label.setToolTip("请安装 Rust: https://rustup.rs/")

    def _get_rust_version(self, rustc_path):
        """获取 Rust 版本号"""
        try:
            # rustc --version 输出示例: rustc 1.80.0 (051478957 2024-07-21)
            result = self._run_hidden(
                [rustc_path, "--version"],
                capture_output=True, text=True, timeout=5,
                startupinfo=get_startupinfo()
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                import re
                # 匹配 rustc 1.80.0
                match = re.search(r'rustc\s+(\d+\.\d+\.\d+)', output, re.IGNORECASE)
                if match:
                    return match.group(1)
                # 匹配 1.80.0
                match = re.search(r'(\d+\.\d+\.\d+)', output)
                if match:
                    return match.group(1)
            return "已安装"
        except Exception:
            return "已安装"

    def _detect_msvc(self):
        try:
            result = self._run_hidden(['cl'], capture_output=True, text=True, startupinfo=get_startupinfo())
            if result.returncode == 0 or 'Microsoft' in result.stderr:
                self.safe_log("🔧 检测到MSVC编译器")
                self.status_compiler.setText("🔧 编译器: MSVC ✓")
                self.status_compiler.setStyleSheet("color: green;")
        except: pass

    def _detect_mingw(self):
        try:
            result = self._run_hidden(['gcc', '--version'], capture_output=True, text=True, startupinfo=get_startupinfo())
            if result.returncode == 0:
                self.safe_log("🔧 检测到MinGW编译器")
                if "MSVC" not in self.status_compiler.text():
                    self.status_compiler.setText("🔧 编译器: MinGW ✓")
                    self.status_compiler.setStyleSheet("color: green;")
        except: pass

    def _update_compiler_status(self):
        """更新编译器状态 - 先读缓存，没有才检测"""
        backend = self.nuitka_backend_combo.currentText() if self.nuitka_backend_combo else "auto"
        # ===== 从缓存读取 =====
        cache = load_cache()
        compiler_cache = cache.get('compiler', {})
        has_msvc = compiler_cache.get('msvc', False)
        has_mingw = compiler_cache.get('mingw', False)
        msvc_path = compiler_cache.get('msvc_path', '')
        mingw_path = compiler_cache.get('mingw_path', '')
        msvc_version = compiler_cache.get('msvc_version', '')
        mingw_version = compiler_cache.get('mingw_version', '')
        # 保存到实例变量
        self._cached_has_msvc = has_msvc
        self._cached_has_mingw = has_mingw
        self._cached_msvc_path = msvc_path
        self._cached_mingw_path = mingw_path
        self._cached_msvc_version = msvc_version
        self._cached_mingw_version = mingw_version
        # ===== 有缓存直接使用 =====
        if has_msvc or has_mingw:
            self._update_compiler_status_result(has_msvc, has_mingw, msvc_path, mingw_path, backend)
            return
        # ===== 没有缓存才检测 =====
        self.status_compiler.setText("⏳ 检测编译器...")
        self.status_compiler.setStyleSheet("color: orange;")

        def detect():
            has_msvc, msvc_path = self._check_msvc_with_path()
            has_mingw, mingw_path = self._check_mingw_with_path()
            msvc_version = self._get_compiler_version(msvc_path, "msvc") if has_msvc else ""
            mingw_version = self._get_compiler_version(mingw_path, "mingw") if has_mingw else ""
            self._cached_has_msvc = has_msvc
            self._cached_has_mingw = has_mingw
            self._cached_msvc_path = msvc_path
            self._cached_mingw_path = mingw_path
            self._cached_msvc_version = msvc_version
            self._cached_mingw_version = mingw_version
            self._save_all_backend_cache()
            QTimer.singleShot(0, lambda: self._update_compiler_status_result(
                has_msvc, has_mingw, msvc_path, mingw_path, backend
            ))
        threading.Thread(target=detect, daemon=True).start()

    def _check_msvc(self):
        """检测 MSVC 是否可用（旧接口，复用新函数）"""
        has_msvc, _ = self._check_msvc_with_path()
        return has_msvc

    def _check_mingw(self):
        """检测 MinGW 是否可用（旧接口，复用新函数）"""
        has_mingw, _ = self._check_mingw_with_path()
        return has_mingw

    def _check_msvc_with_path(self):
        """检测 MSVC 是否可用，并返回路径（跨平台）"""
        # Windows 平台检测
        if sys.platform == 'win32':
            # 1. 检查 cl.exe 是否在 PATH 中
            cl_path = shutil.which("cl.exe")
            if cl_path and os.path.exists(cl_path):
                return True, cl_path
            # 2. 检查 Visual Studio 安装路径
            vs_paths = [
                r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
                r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC",
                r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC",
                r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Tools\MSVC",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Tools\MSVC",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC",
            ]
            for vs_path in vs_paths:
                if os.path.exists(vs_path):
                    for version_dir in os.listdir(vs_path):
                        # 尝试不同的架构
                        for arch in ["Hostx64", "Hostx86"]:
                            for target in ["x64", "x86"]:
                                cl_exe = os.path.join(vs_path, version_dir, "bin", arch, target, "cl.exe")
                                if os.path.exists(cl_exe):
                                    return True, cl_exe
            # 3. 尝试用 vswhere 查找
            try:
                result = self._run_hidden(
                    ['vswhere', '-latest', '-find', '**/cl.exe'],
                    capture_output=True, text=True, timeout=10,
                    startupinfo=get_startupinfo()
                )
                if result.returncode == 0 and result.stdout.strip():
                    cl_path = result.stdout.strip().split('\n')[0]
                    if os.path.exists(cl_path):
                        return True, cl_path
            except:
                pass
            # 4. 尝试用 cl 命令检测
            try:
                result = self._run_hidden(
                    ['cl.exe'],
                    capture_output=True, text=True, timeout=5,
                    startupinfo=get_startupinfo()
                )
                # cl 无参数时返回非0，但输出包含 Microsoft
                if 'Microsoft' in (result.stdout + result.stderr):
                    cl_path = shutil.which("cl.exe")
                    if cl_path:
                        return True, cl_path
            except:
                pass
            return False, ""
        # Linux/macOS：MSVC 不可用
        else:
            return False, ""

    def _check_mingw_with_path(self):
        """检测 MinGW 是否可用，并返回路径和版本"""
        import subprocess
        import re
        gcc_path = None
        # Windows 平台检测
        if sys.platform == 'win32':
            # 1. 检查 gcc.exe 是否在 PATH 中
            gcc_path = shutil.which("gcc.exe")
            if gcc_path and os.path.exists(gcc_path):
                pass
            else:
                # 2. 检查常见 MinGW 安装路径
                mingw_paths = [
                    os.path.join(get_exe_directory(), "tools", "mingw64", "bin", "gcc.exe"),
                    r"C:\MinGW\bin\gcc.exe",
                    r"C:\msys64\mingw64\bin\gcc.exe",
                    r"C:\msys64\mingw32\bin\gcc.exe",
                    r"C:\msys64\ucrt64\bin\gcc.exe",
                    r"C:\msys64\clang64\bin\gcc.exe",
                    r"C:\Program Files\mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\bin\gcc.exe",
                    r"C:\Program Files\mingw-w64\x86_64-8.1.0-win32-seh-rt_v6-rev0\mingw64\bin\gcc.exe",
                    os.path.join(get_exe_directory(), "tools", "mingw", "bin", "gcc.exe"),
                ]
                for path in mingw_paths:
                    if os.path.exists(path):
                        gcc_path = path
                        break
        else:
            # Linux/macOS
            gcc_path = shutil.which("gcc")
            if not gcc_path:
                for version in ['13', '12', '11', '10', '9']:
                    gcc_path = shutil.which(f"gcc-{version}")
                    if gcc_path:
                        break
            if not gcc_path:
                linux_paths = [
                    '/usr/bin/gcc',
                    '/usr/local/bin/gcc',
                    '/opt/homebrew/bin/gcc',
                ]
                for path in linux_paths:
                    if os.path.exists(path):
                        gcc_path = path
                        break
        if not gcc_path or not os.path.exists(gcc_path):
            return False, "", ""
        version = ""
        try:
            # 方法1: gcc -dumpversion
            result = subprocess.run(
                [gcc_path, '-dumpversion'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                ver = result.stdout.strip()
                # 确保是完整版本号 (x.x.x)
                if re.match(r'\d+\.\d+\.\d+', ver):
                    version = ver
                elif re.match(r'\d+\.\d+', ver):
                    version = ver + ".0"
                else:
                    # 方法2: gcc --version
                    result = subprocess.run(
                        [gcc_path, '--version'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
                        if match:
                            version = match.group(1)
                        else:
                            match = re.search(r'(\d+\.\d+)', result.stdout)
                            if match:
                                version = match.group(1) + ".0"
        except:
            pass
        # 如果获取版本失败，从路径提取
        if not version:
            match = re.search(r'(\d+\.\d+\.\d+)', gcc_path)
            if match:
                version = match.group(1)
            else:
                version = "15.2.0"  # 默认
        return True, gcc_path, version
    # ==================== 日志和状态 ====================

    def safe_log(self, msg):
        """安全输出日志到GUI区域（线程安全）"""
        # ===== 停止时跳过日志 =====
        if getattr(self, '_stop_logging', False):
            return
        try:
            if hasattr(self, 'log_text') and self.log_text:
                def do_log():
                    try:
                        self.log_text.appendPlainText(msg)
                        scrollbar = self.log_text.verticalScrollBar()
                        scrollbar.setValue(scrollbar.maximum())
                    except Exception:
                        pass
                if QThread.currentThread() != QApplication.instance().thread():
                    from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
                    QMetaObject.invokeMethod(self.log_text, "appendPlainText",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(str, msg))
                    QMetaObject.invokeMethod(self.log_text.verticalScrollBar(), "setValue",
                                             Qt.ConnectionType.QueuedConnection,
                                             Q_ARG(int, self.log_text.verticalScrollBar().maximum()))
                else:
                    do_log()
        except Exception:
            pass

    def _clear_log(self): self.log_text.clear()

    def _export_log(self):
        """导出日志"""
        from datetime import datetime
        try:
            log_content = self.log_text.toPlainText()
            if not log_content.strip():
                QMessageBox.warning(self, "警告", "日志为空，无法导出")
                return
            # 获取项目名称
            project_name = self.app_name.text()
            if project_name:
                project_name = re.sub(r'[\\/:*?"<>|]', '_', project_name)
                default_name = f"{project_name}_build_log_{datetime.now().strftime('%Y%m%d')}.txt"
            else:
                default_name = f"build_log{datetime.now().strftime('%Y%m%d')}.txt"
            # 直接保存，不询问覆盖
            file_path = os.path.join(os.path.dirname(self.output_dir.text()), default_name)
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(log_content)
            self.safe_log(f"📋 日志已导出: {file_path}")
        except Exception as e:
            self.safe_log(f"❌ 导出日志失败: {e}")
            QMessageBox.warning(self, "错误", f"导出失败: {e}")

    def _select_input(self):
        self._clear_log()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Python脚本", "", "Python Files (*.py);;All Files (*.*)")
        if file_path:
            file_path = self._auto_fix_filename_spaces(file_path)
            if not file_path or not os.path.exists(file_path):
                return
            normalized = os.path.normpath(file_path)
            self.input_file.blockSignals(True)
            self.input_file.setText(self._format_path(normalized))
            self.input_file.blockSignals(False)
            base_name = os.path.splitext(os.path.basename(normalized))[0]
            self.app_name.setText(base_name)
            script_dir = os.path.dirname(normalized)
            dist_dir = os.path.join(script_dir, "dist")
            self.output_dir.setText(self._format_path(dist_dir))
            proj_name = re.sub(r'[\\/:*?"<>|]', '_', base_name)
            output_path = os.path.join(dist_dir, proj_name)
            os.makedirs(output_path, exist_ok=True)
            # ===== 【修复】清空所有列表（包括排除列表） =====
            self.hidden_imports_list.clear()
            self.hidden_listbox.clear()
            self.exclude_list.clear()
            self.exclude_listbox.clear()
            self.data_files_list.clear()
            self.data_listbox.clear()
            self._update_data_count()
            self._update_hidden_count()
            self._update_exclude_count()
            # ============================================
            self._analyze_used(normalized, auto_add=True)
            self._update_hidden_count()
            self._update_auto_import_count()
            QTimer.singleShot(10, lambda: self._detect_gui_from_hidden())
            QTimer.singleShot(100, lambda: self._auto_load_tool_icon(normalized, base_name))
            QTimer.singleShot(100, lambda: self._auto_create_venv_for_script(normalized))

    def _format_path(self, path):
        """将路径格式化为Windows风格的反斜杠显示"""
        if not path:
            return path
        # 统一使用反斜杠
        return path.replace('/', '\\')

    def _normalize_path(self, path):
        """标准化路径（内部使用正斜杠，显示用反斜杠）"""
        if not path:
            return path
        # 标准化路径
        path = os.path.normpath(path)
        return path

    def _init_packer_panel_visibility(self):
        """初始化打包器高级面板的可见性（不触发版本检测）"""
        current_packer = self.packer_combo.currentText()
        # 判断是否需要显示高级面板
        show = current_packer in ["Nuitka", "PyInstaller-spec", "PyInstaller-cmd"]
        if hasattr(self, 'packer_opt_row'):
            self.packer_opt_row.setVisible(show)
            if show:
                # 强制更新UI控件可见性（不检测版本）
                self._update_packer_ui(current_packer)
        # ===== Nuitka版本检测延迟到后台 =====
        if current_packer == "Nuitka":
            QTimer.singleShot(200, self._check_nuitka_version_async)
        else:
            QTimer.singleShot(200, self._check_current_packer)

    def _auto_load_tool_icon(self, script_path, base_name):
        """自动加载图标"""
        # 获取当前运行的主程序文件（非系统Python）
        main_file = sys.modules['__main__'].__file__
        main_name = os.path.splitext(os.path.basename(main_file))[0]
        # 判断选择的py是否与当前主程序同名
        if main_name.lower() == base_name.lower():
            script_dir = os.path.dirname(script_path)
            icon_path = os.path.join(script_dir, "tool.ico")
            if os.path.exists(icon_path):
                icon_name = os.path.basename(icon_path)
                self.icon_label.setText(icon_name)
                self.icon_label.setToolTip(self._format_path(icon_path))
                self.icon_label.setStyleSheet("color: #4caf50; font-size: 10px;")
                self._set_window_icon(icon_path)
                existing = [src for src, _ in self.data_files_list if src == icon_path]
                if not existing:
                    self.data_files_list.append((icon_path, "."))
                    self.data_listbox.addItem(f"{icon_name} -> .")
                    self._update_data_count()
                return
        self.icon_label.setText("")
        self.icon_label.setStyleSheet("color: gray; font-size: 10px;")

    def _set_icon_display(self, icon_name, icon_path):
        """延迟设置图标显示（确保UI刷新）"""
        try:
            self.icon_label.setText(icon_name)
            self.icon_label.setToolTip(self._format_path(icon_path))
            self.icon_label.setStyleSheet("color: #4caf50; font-size: 10px;")
            # 强制刷新
            self.icon_label.update()
            self.icon_label.repaint()
            self.safe_log(f"✅ 图标标签已更新: {icon_name}")
        except Exception as e:
            self.safe_log(f"⚠️ 设置图标标签失败: {e}")

    def _auto_create_venv_for_script(self, script_path):
        """用户勾选虚拟时，触发创建/切换，并安装依赖"""
        if not self.venv_mode.isChecked():
            return
        # 确保虚拟环境已创建并切换
        self._on_venv_switch(Qt.CheckState.Checked.value)
        # 安装缺失依赖（使用当前选中的Python，即虚拟环境）
        self._install_missing_deps_only(script_path)

    def _on_deps_progress(self, value):
        """依赖安装进度更新"""
        self.progress_bar.setValue(value)
        self.status_set_target(value)

    def _on_deps_status(self, text):
        """依赖安装状态更新"""
        self.progress_label.setText(f"{text}")
        self.status_label.setText(text[:8])

    def _on_deps_finished(self, success):
        """依赖安装完成"""
        if success:
            self.progress_bar.setValue(100)
            self.progress_label.setText("100% - 完成")
            self.status_finish("就绪")
            self.safe_log("✅ 依赖已安装完成")
            QTimer.singleShot(300, self._update_venv_pkg_count)
        else:
            self.status_finish("失败")
            self.safe_log("❌ 依赖安装失败")
        # 无论成功还是失败，都延迟隐藏状态栏进度条
        QTimer.singleShot(500, lambda: self.status_progress.setVisible(False))
        QTimer.singleShot(500, lambda: self.status_pct.setVisible(False))
        self.deps_thread = None

    def _async_create_venv(self, venv_dir, venv_python, script_path):
        """在后台线程创建虚拟环境"""
        try:
            import shutil
            py = None
            # 只排除 common_venv
            for i in range(self.python_path.count()):
                path = self.python_path.itemText(i)
                if path and os.path.exists(path):
                    if 'common_venv' not in path.lower():
                        py = path
                        break
            if not py:
                for cmd in ['python', 'python3']:
                    p = shutil.which(cmd)
                    if p and os.path.exists(p) and 'common_venv' not in p.lower():
                        py = p
                        break
            if not py:
                if sys.platform == 'win32':
                    default_paths = [
                        r'C:\Python312\python.exe',
                        r'C:\Python311\python.exe',
                        r'C:\Python310\python.exe',
                    ]
                    for p in default_paths:
                        if os.path.exists(p):
                            py = p
                            break
                else:
                    py = '/usr/bin/python3'
            if not py or not os.path.exists(py):
                self.safe_log("❌ 未找到系统 Python")
                self.venv_finish_signal.emit(False)
                return
            self.safe_log(f"🔧 使用系统Python创建虚拟环境: {py}")
            self.safe_log(f"🔧 目标目录: {self._format_path(venv_dir)}")
            self.venv_progress_signal.emit(20, "创建虚拟环境")
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            if os.path.exists(venv_dir):
                self.safe_log(f"🗑️ 删除旧虚拟环境...")
                if sys.platform == 'win32':
                    self._run_hidden(['cmd', '/c', 'rmdir', '/s', '/q', venv_dir], capture_output=True)
                else:
                    shutil.rmtree(venv_dir, ignore_errors=True)
            result = self._run_hidden(
                [py, "-m", "venv", venv_dir],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                startupinfo=get_startupinfo(),
                env=env
            )
            if result.returncode != 0:
                self.safe_log(f"❌ 创建失败: {result.stderr}")
                self.venv_finish_signal.emit(False)
                return
            self.safe_log("✅ 虚拟环境创建成功")
            self.venv_progress_signal.emit(40, "创建完成")
            if not os.path.exists(venv_python):
                self.safe_log(f"❌ 虚拟环境Python不存在: {venv_python}")
                self.venv_finish_signal.emit(False)
                return
            # ===== 安装依赖（带进度） =====
            self.venv_progress_signal.emit(50, "安装依赖...")
            # 在主线程中执行安装
            QTimer.singleShot(0, lambda: self._install_dependencies_for_script(venv_python, script_path))
            # ===== 复制 Tkinter（如果需要） =====
            if 'tk' in self.hidden_imports_list or 'tkinter' in self.hidden_imports_list:
                self._copy_tkinter_to_venv(venv_python)
            # ===== 所有操作完成 =====
            self.safe_log(f"✅ 公用虚拟环境就绪: {self._format_path(venv_dir)}")
            self.venv_progress_signal.emit(100, "完成")
            self.venv_finish_signal.emit(True)
        except Exception as e:
            self.safe_log(f"❌ 创建虚拟环境异常: {e}")
            self.venv_finish_signal.emit(False)

    def _get_target_python(self):
        """获取目标Python"""
        # 始终返回界面选中的Python
        return self.python_path.currentText()

    def _batch_install_in_venv(self, venv_python, modules):
        """在虚拟环境中安装依赖（用原版逻辑）"""
        total = len(modules)
        for i, mod in enumerate(modules):
            pkg = MODULE_TO_PACKAGE.get(mod, mod)
            progress = int((i + 1) / total * 100)
            self.venv_progress_signal.emit(progress, f"安装 {pkg} ({i + 1}/{total})")
            self.safe_log(f"📦 安装 {pkg}...")
            try:
                success, result = pip_install(venv_python, pkg)
                self.safe_log(f"{'✅' if success else '❌'} {pkg}")
                if not success and result and result.stderr:
                    self.safe_log(f"   错误: {result.stderr[:200]}")
            except Exception as e:
                self.safe_log(f"❌ 安装异常: {e}")
        self.venv_progress_signal.emit(100, "安装完成")

    def _get_installed_in_venv(self, venv_python):
        """获取虚拟环境中已安装的包列表"""
        try:
            result = self._run_hidden(
                [venv_python, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True,
                startupinfo=get_startupinfo(),
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {item['name'].lower() for item in data}
        except Exception as e:
            self.safe_log(f"⚠️ 获取虚拟环境包列表失败: {e}")
        return set()

    def _check_and_install_missing_deps(self, venv_python, script_path):
        """检查虚拟环境中缺失的依赖"""
        try:
            self.safe_log("📦 检查虚拟环境依赖...")
            installed_in_venv = self._get_installed_in_venv(venv_python)
            # ===== 判断是否需要处理 tkinter =====
            if 'tk' in self.hidden_imports_list:
                if 'tk' not in installed_in_venv:
                    self.safe_log("📦 安装 tk 包...")
                    try:
                        success, _ = pip_install(venv_python, 'tk', quiet=True, timeout=180)
                        if success:
                            self.safe_log("   ✅ tk 安装成功")
                            installed_in_venv.add('tk')
                        else:
                            self.safe_log("   ❌ tk 安装失败")
                    except Exception as e:
                        self.safe_log(f"   ❌ tk 安装异常: {e}")
                # 2. 复制 Tkinter 到虚拟环境
                self._copy_tkinter_to_venv(venv_python)
            self._analyze_used(script_path, auto_add=False)
            needed_modules = self.analyzed_modules
            missing_packages = []
            for mod in needed_modules:
                if mod not in STANDARD_LIBS and mod != 'tkinter' and mod != 'tk':
                    pkg = MODULE_TO_PACKAGE.get(mod, mod)
                    pkg_lower = pkg.lower()
                    if pkg_lower not in installed_in_venv:
                        missing_packages.append(pkg)
            # 安装缺失的第三方包
            if missing_packages:
                self.safe_log(f"📦 发现 {len(missing_packages)} 个缺失依赖")
                for i, pkg in enumerate(missing_packages):
                    progress = 50 + int((i + 1) / len(missing_packages) * 40)
                    self.venv_progress_signal.emit(progress, f"安装 {pkg} ({i + 1}/{len(missing_packages)})")
                    try:
                        success, _ = pip_install(venv_python, pkg, quiet=True, timeout=180)
                        if success:
                            self.safe_log(f"   ✅ {pkg} 安装成功")
                        else:
                            self.safe_log(f"   ❌ {pkg} 安装失败")
                    except Exception as e:
                        self.safe_log(f"   ❌ {pkg} 安装异常: {e}")
            else:
                self.safe_log("✅ 所有依赖已安装")
        except Exception as e:
            self.safe_log(f"❌ 依赖检查异常: {e}")

    def _install_dependencies_for_script(self, venv_python, script_path):
        """异步安装依赖到虚拟环境"""
        self.safe_log(f"📦 开始安装依赖到虚拟环境...")
        # 显示进度条
        self.status_start("安装依赖", color="blue")
        self.progress_container.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("0% - 准备安装...")
        # 保存线程引用
        self.deps_thread = InstallDepsThread(venv_python, script_path, self.hidden_imports_list)
        self.deps_thread.log_signal.connect(self.safe_log)
        self.deps_thread.progress_signal.connect(self._on_deps_progress)
        self.deps_thread.status_signal.connect(self._on_deps_status)
        self.deps_thread.finished_signal.connect(self._on_deps_finished)
        self.deps_thread.start()

    def _copy_tkinter_to_venv(self, venv_python):
        """将系统 Tkinter 完整复制到虚拟环境（包括 _tkinter.pyd 和 tk 库）"""
        try:
            import shutil
            # ===== 1. 获取系统 Python =====
            system_python = sys.executable
            if getattr(sys, 'frozen', False):
                system_python = self._find_system_python() or sys.executable
            self.safe_log(f"🔧 系统 Python: {system_python}")
            # ===== 2. 获取虚拟环境 site-packages 路径 =====
            result = self._run_hidden(
                [venv_python, '-c', 'import sys; print([p for p in sys.path if "site-packages" in p][0])'],
                capture_output=True, text=True, timeout=5,
                startupinfo=get_startupinfo()
            )
            if result.returncode != 0 or not result.stdout.strip():
                result = self._run_hidden(
                    [venv_python, '-c', 'import site; print(site.getsitepackages()[0])'],
                    capture_output=True, text=True, timeout=5,
                    startupinfo=get_startupinfo()
                )
            if result.returncode != 0:
                self.safe_log("⚠️ 无法获取虚拟环境 site-packages 路径")
                return False
            venv_site_packages = result.stdout.strip()
            if not venv_site_packages or not os.path.exists(venv_site_packages):
                self.safe_log(f"⚠️ 虚拟环境 site-packages 不存在: {venv_site_packages}")
                return False
            self.safe_log(f"📁 虚拟环境 site-packages: {venv_site_packages}")
            # ===== 3. 获取 tkinter 模块路径（主动 import，仅用于获取路径） =====
            result = self._run_hidden(
                [system_python, '-c', 'import tkinter; print(tkinter.__file__)'],
                capture_output=True, text=True, timeout=5,
                startupinfo=get_startupinfo()
            )
            if result.returncode != 0:
                return False
            tkinter_file = result.stdout.strip()
            if not tkinter_file or not os.path.exists(tkinter_file):
                return False
            # ===== 4. 复制 tkinter 目录 =====
            tkinter_dir = os.path.dirname(tkinter_file)
            tkinter_name = os.path.basename(tkinter_dir)
            dest_dir = os.path.join(venv_site_packages, tkinter_name)
            if os.path.exists(dest_dir):
                if sys.platform == 'win32':
                    self._run_hidden(['cmd', '/c', 'rmdir', '/s', '/q', dest_dir], capture_output=True)
                else:
                    shutil.rmtree(dest_dir, ignore_errors=True)
            shutil.copytree(tkinter_dir, dest_dir)
            # ===== 5. 获取 Python 的 DLLs 目录 =====
            python_dir = os.path.dirname(system_python)
            python_dlls_dir = os.path.join(python_dir, 'DLLs')
            if not os.path.exists(python_dlls_dir):
                python_dlls_dir = os.path.join(python_dir, 'Lib', 'DLLs')
            # ===== 6. 复制 _tkinter.pyd 和 tk 相关库 =====
            copied_files = []
            # 从 DLLs 目录复制
            if os.path.exists(python_dlls_dir):
                for file in os.listdir(python_dlls_dir):
                    file_lower = file.lower()
                    if file_lower.startswith('_tkinter') or file_lower.startswith('tcl') or file_lower.startswith('tk'):
                        src_file = os.path.join(python_dlls_dir, file)
                        dest_file = os.path.join(venv_site_packages, file)
                        if not os.path.exists(dest_file):
                            shutil.copy2(src_file, dest_file)
                            copied_files.append(file)
            # ===== 7. 也从 Python 根目录查找 =====
            for file in os.listdir(python_dir):
                file_lower = file.lower()
                if file_lower.startswith('_tkinter') or file_lower.startswith('tcl') or file_lower.startswith('tk'):
                    if file.endswith('.pyd') or file.endswith('.dll') or file.endswith('.lib'):
                        src_file = os.path.join(python_dir, file)
                        dest_file = os.path.join(venv_site_packages, file)
                        if not os.path.exists(dest_file):
                            shutil.copy2(src_file, dest_file)
                            copied_files.append(file)
            # ===== 8. 复制 tcl 目录到虚拟环境根目录 =====
            if sys.platform == 'win32':
                tcl_paths = []
                # 在 Python 安装目录下查找
                for item in os.listdir(python_dir):
                    if item.startswith('tcl') and os.path.isdir(os.path.join(python_dir, item)):
                        tcl_paths.append(os.path.join(python_dir, item))
                # 也在 Lib 目录下查找
                lib_dir = os.path.join(python_dir, 'Lib')
                if os.path.exists(lib_dir):
                    for item in os.listdir(lib_dir):
                        if item.startswith('tcl') and os.path.isdir(os.path.join(lib_dir, item)):
                            tcl_paths.append(os.path.join(lib_dir, item))
                for tcl_path in tcl_paths:
                    if os.path.exists(tcl_path) and os.path.isdir(tcl_path):
                        venv_dir = os.path.dirname(venv_python)
                        venv_tcl = os.path.join(venv_dir, os.path.basename(tcl_path))
                        if os.path.exists(venv_tcl):
                            shutil.rmtree(venv_tcl, ignore_errors=True)
                        shutil.copytree(tcl_path, venv_tcl)
                        break
            # ===== 9. 验证复制结果 =====
            for f in copied_files[:10]:
                self.safe_log(f"   - {f}")
            if len(copied_files) > 10:
                self.safe_log(f"   ... 还有 {len(copied_files) - 10} 个文件")
            # 测试导入
            test_result = self._run_hidden(
                [venv_python, '-c', 'import tkinter; print("Tkinter OK")'],
                capture_output=True, text=True, timeout=5,
                startupinfo=get_startupinfo()
            )
            if test_result.returncode == 0:
                return True
            else:
                return False
        except Exception as e:
            import traceback
            self.safe_log(traceback.format_exc())
            return False

    def _switch_to_venv_python(self, venv_python, project_name):
        """切换到虚拟环境的Python"""
        if not os.path.exists(venv_python):
            return
        # 保存当前选中的系统Python（用于恢复）
        current_py = self.python_path.currentText()
        if current_py and os.path.exists(current_py):
            # 检查是否是虚拟环境Python
            venv_dir = os.path.join(get_exe_directory(), "common_venv")
            if sys.platform == 'win32':
                venv_check = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_check = os.path.join(venv_dir, "bin", "python")
            if current_py != self._format_path(venv_check):
                # 保存系统Python路径供恢复使用
                self._last_system_python = current_py
        display_path = self._format_path(venv_python)
        idx = self.python_path.findText(display_path)
        if idx >= 0:
            self.python_path.setCurrentIndex(idx)
        else:
            self.python_path.addItem(display_path)
            self.python_path.setCurrentText(display_path)
        try:
            result = self._run_hidden(
                [venv_python, '--version'],
                capture_output=True, text=True,
                startupinfo=get_startupinfo()
            )
            ver = result.stdout.strip() or result.stderr.strip()
            if ver:
                self.python_version.setText(ver)
                self.status_python.setText(f"🐍 {ver} (公用venv)")
                self.safe_log(f"🐍 已切换到公用虚拟环境Python: {ver}")
        except:
            pass

    def _install_packers_in_venv(self, venv_python):
        """在虚拟环境中安装打包器"""
        packer = self.packer_combo.currentText()
        packer_map = {
            'PyInstaller-spec': 'pyinstaller',
            'PyInstaller-cmd': 'pyinstaller',
            'Nuitka': 'nuitka',
            'PyApp': 'pyapp',
            'Py2exe': 'py2exe',
            'Cx_Freeze': 'cx-freeze',
            'Pynsist': 'pynsist',
            'PyOxidizer': 'pyoxidizer',
            'Py2app': 'py2app',
        }
        packer_name = packer_map.get(packer, 'pyinstaller')
        threading.Thread(
            target=self._async_install_packer_in_venv,
            args=(venv_python, packer_name),
            daemon=True
        ).start()

    def _async_install_packer_in_venv(self, venv_python, packer_name):
        """在后台线程安装打包器到虚拟环境"""
        try:
            result = self._run_hidden(
                [venv_python, '-m', 'pip', 'show', packer_name],
                capture_output=True, text=True,
                startupinfo=get_startupinfo()
            )
            if result.returncode == 0:
                self.safe_log(f"✅ 打包器 {packer_name} 已在虚拟环境中")
                return
        except:
            pass
        self.safe_log(f"📦 正在安装打包器到虚拟环境: {packer_name}")
        try:
            self._run_hidden(
                [venv_python, '-m', 'pip', 'install', packer_name, '-q'],
                capture_output=True,
                startupinfo=get_startupinfo()
            )
            self.safe_log(f"✅ 打包器 {packer_name} 已安装到虚拟环境")
        except Exception as e:
            self.safe_log(f"⚠️ 打包器安装失败: {e}")

    def _do_manage_venv_project(self, venv_dir, script):
        """为项目创建独立的虚拟环境"""
        try:
            py = self.python_path.currentText() if self.python_path.currentText() else sys.executable
            if not py or not os.path.exists(py):
                self._venv_log("❌ 未找到 Python")
                self._venv_finish(False)
                return
            self._venv_log(f"📦 创建项目虚拟环境: {self._format_path(venv_dir)}")
            # 删除旧环境
            if os.path.exists(venv_dir):
                if self.stop_venv:
                    self._venv_log("🛑 用户取消操作")
                    self._venv_finish(False)
                    return
                self._venv_progress(10, "删除旧环境")
                self._rename_and_delete(venv_dir)
            if self.stop_venv:
                self._venv_log("🛑 用户取消操作")
                self._venv_finish(False)
                return
            self._venv_progress(20, "创建虚拟环境")
            self._venv_log("🔧 创建虚拟环境...")
            result = self._run_hidden(
                [py, "-m", "venv", venv_dir],
                capture_output=True, text=True,
                startupinfo=get_startupinfo()
            )
            if result.returncode != 0:
                self._venv_log(f"❌ 创建失败: {result.stderr}")
                self._venv_finish(False)
                return
            self._venv_log("✅ 虚拟环境创建成功")
            self._venv_progress(30, "创建完成")
            # 获取虚拟环境中的 Python 路径
            if sys.platform == "win32":
                venv_py = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_py = os.path.join(venv_dir, "bin", "python")
            # 切换到虚拟环境Python
            base_name = os.path.splitext(os.path.basename(script))[0]
            self._switch_to_venv_python(venv_py, base_name)
            # 获取需要安装的模块
            all_modules = list(set(self.analyzed_modules + self.hidden_imports_list))
            if all_modules:
                self._venv_log(f"📦 需要安装 {len(all_modules)} 个模块")
                for i, pkg in enumerate(all_modules):
                    if self.stop_venv:
                        self._venv_log("🛑 用户取消安装")
                        self._venv_finish(False)
                        return
                    progress = 30 + int((i + 1) / len(all_modules) * 65)
                    install_pkg = MODULE_TO_PACKAGE.get(pkg, pkg)
                    self._venv_progress(progress, f"安装 {install_pkg} ({i + 1}/{len(all_modules)})")
                    self._venv_log(f"📥 安装 {install_pkg}...")
                    install_cmd = [venv_py, "-m", "pip", "install", install_pkg, "-i",
                                "https://pypi.tuna.tsinghua.edu.cn/simple", "-q"]
                    result = self._run_hidden(install_cmd, capture_output=True, text=True, timeout=180)
                    if result.returncode == 0:
                        self._venv_log(f"   ✅ {install_pkg} 安装成功")
                    else:
                        self._venv_log(f"   ❌ {install_pkg} 安装失败")
            # 安装当前打包器到虚拟环境
            self._install_packers_in_venv(venv_py)
            self._venv_progress(100, "完成")
            self._venv_log(f"✅ 项目虚拟环境就绪: {self._format_path(venv_dir)}")
            self._venv_finish(True)
        except Exception as e:
            self._venv_log(f"❌ 管理失败: {e}")
            self._venv_finish(False)

    def _select_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录", self.dist_dir)
        if dir_path: self.output_dir.setText(self._format_path(dir_path))

    def _select_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图标", "",
                                                "Icon Files (*.ico *.icns);;Image Files (*.png *.jpg *.bmp)")
        if file_path:
            self.icon_label.setText(os.path.basename(file_path))
            self.icon_label.setToolTip(self._format_path(file_path))
            self.icon_label.setStyleSheet("color: green; font-size: 9px;")
            self._set_window_icon(file_path)
            existing = [src for src, _ in self.data_files_list if src == file_path]
            if not existing:
                self.data_files_list.append((file_path, "."))
                self.data_listbox.addItem(f"{os.path.basename(file_path)} -> .")
                self._update_data_count()
                self.safe_log(f"✅ 图标已自动添加到数据文件列表: {os.path.basename(file_path)}")
            else:
                self.safe_log(f"ℹ️ 图标已在数据文件列表中: {os.path.basename(file_path)}")

    def _clear_icon(self):
        icon_path = self.icon_label.toolTip()
        self.icon_label.setText("")
        self.icon_label.setToolTip("")
        self.icon_label.setStyleSheet("color: gray; font-size: 9px;")
        if icon_path:
            icon_path_normalized = icon_path.replace('\\', '/')
            for i, (src, dst) in enumerate(self.data_files_list):
                src_normalized = src.replace('\\', '/')
                if src_normalized == icon_path_normalized or src == icon_path:
                    self.data_files_list.pop(i)
                    self.data_listbox.takeItem(i)
                    self.safe_log(f"🗑️ 已从数据文件列表移除图标: {os.path.basename(icon_path)}")
                    break
            self._update_data_count()
        default_icon = os.path.join(get_exe_directory(), "tool.ico")
        if os.path.exists(default_icon):
            self._set_window_icon(default_icon)
        else:
            self.setWindowIcon(QIcon())

    def _open_icon_maker(self):
        dialog = IconMakerDialog(self, self, lambda p: (
            self.icon_label.setText(f"✓ {os.path.basename(p)}"),
            self.icon_label.setToolTip(self._format_path(p)),
            self.icon_label.setStyleSheet("color: green; font-size: 9px; font-weight: bold;"),
            self.icon_label.update(),
            self.icon_label.repaint(),
            self._set_window_icon(p)
        ))
        dialog.exec()

    def _select_python(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择Python解释器", "",
                                                "Python Executable (python.exe python3 python);;All Files (*.*)")
        if file_path:
            # 显示为反斜杠
            display_path = self._format_path(file_path)
            self.python_path.addItem(display_path)
            self.python_path.setCurrentText(display_path)
            self._on_python_path_changed(path)

    def _select_upx(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择UPX", "", "UPX (upx.exe upx);;All Files (*.*)")
        if file_path:
            # 统一将后缀转为 .exe
            import re
            file_path = re.sub(r'\.exe$', '.exe', file_path, flags=re.IGNORECASE)
            formatted_path = self._format_path(file_path)
            self.upx_path.setText(formatted_path)
            self._set_upx_environment(file_path)
            # 保存缓存
            cache = load_cache()
            cache['upx'] = {'path': formatted_path}
            save_cache(cache)
            self.safe_log(f"🗜️ UPX路径已设置: {formatted_path}")

    def _open_output(self):
        """打开输出目录（只打开文件夹，不打开文件）"""
        script = self.input_file.text()
        if script:
            base_name = os.path.splitext(os.path.basename(script))[0]
            proj_name = re.sub(r'[\\/:*?"<>|]', '_', base_name)
            path = os.path.join(self.output_dir.text(), proj_name)
        else:
            path = self.output_dir.text()
        # ===== 如果路径不存在，尝试创建 =====
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                self.safe_log(f"⚠️ 创建目录失败: {e}")
                # 创建失败，尝试打开父目录
                path = os.path.dirname(path)
        # ===== 修复：优先检查文件夹 =====
        # 如果路径存在且是文件夹，直接打开
        if os.path.isdir(path):
            target_path = path
        else:
            # 如果是文件，改为打开所在文件夹
            target_path = os.path.dirname(path)
            # 如果所在文件夹不存在，尝试创建
            if not os.path.exists(target_path):
                try:
                    os.makedirs(target_path, exist_ok=True)
                except:
                    pass
        # ===== 如果仍然不存在，尝试打开 dist 目录 =====
        if not os.path.exists(target_path):
            fallback_path = self.output_dir.text()
            if os.path.exists(fallback_path):
                target_path = fallback_path
            else:
                self.safe_log(f"⚠️ 目录不存在: {target_path}")
                QMessageBox.warning(self, "提示", f"目录不存在:\n{target_path}")
                return
        # ===== 安全打开 =====
        try:
            self.safe_log(f"📂 打开目录: {target_path}")
            if sys.platform == 'win32':
                # 使用 explorer 打开，确保路径正确
                subprocess.Popen(['explorer', target_path], shell=False,
                                 creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', target_path])
            else:
                subprocess.Popen(['xdg-open', target_path])
        except Exception as e:
            self.safe_log(f"❌ 打开目录失败: {e}")
            QMessageBox.warning(self, "错误", f"无法打开目录:\n{target_path}\n\n{str(e)}")

    def _find_all_python(self):
        """同步查找所有有效的 Python 解释器 - 强制排序：项目venv → 系统 → common_venv"""
        import shutil
        import re
        import glob
        # 存储所有找到的路径
        found_paths = []
        # 1. 查找项目 venv/.venv
        script_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.getcwd()
        for base_dir in [script_dir, current_dir]:
            venv_paths = [
                os.path.join(base_dir, '.venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, '.venv', 'bin', 'python'),
                os.path.join(base_dir, 'venv', 'Scripts', 'python.exe'),
                os.path.join(base_dir, 'venv', 'bin', 'python'),
            ]
            for path in venv_paths:
                if self._is_valid_python(path) and path not in found_paths:  # ← 用统一的
                    found_paths.append(path)
        # 2. 查找 common_venv
        exe_dir = get_exe_directory()
        common_venv_dir = os.path.join(exe_dir, "common_venv")
        if sys.platform == 'win32':
            common_venv_exe = os.path.join(common_venv_dir, "Scripts", "python.exe")
        else:
            common_venv_exe = os.path.join(common_venv_dir, "bin", "python")
        if self._is_valid_python(common_venv_exe) and common_venv_exe not in found_paths:  # ← 用统一的
            found_paths.append(common_venv_exe)
        # 3. 查找系统Python
        if sys.platform == 'win32':
            for cmd in ['python', 'python3']:
                try:
                    w = self._run_hidden(['where', cmd], capture_output=True, text=True, startupinfo=get_startupinfo())
                    if w.returncode == 0:
                        for line in w.stdout.strip().split('\n'):
                            line = line.strip()
                            if self._is_valid_python(line) and line not in found_paths:  # ← 用统一的
                                found_paths.append(line)
                except:
                    pass
            username = os.environ.get('USERNAME', '')
            for pattern in [r'C:\Python*', rf'C:\Users\{username}\AppData\Local\Programs\Python\Python*',
                            r'C:\Program Files\Python*']:
                for path in glob.glob(pattern):
                    if os.path.isdir(path):
                        exe = os.path.join(path, 'python.exe')
                        if self._is_valid_python(exe) and exe not in found_paths:  # ← 用统一的
                            found_paths.append(exe)
        else:
            for cmd in ['python3', 'python']:
                try:
                    result = self._run_hidden(['which', cmd], capture_output=True, text=True)
                    if result.returncode == 0 and result.stdout.strip():
                        path = result.stdout.strip()
                        if self._is_valid_python(path) and path not in found_paths:  # ← 用统一的
                            found_paths.append(path)
                except:
                    pass
            common_paths = [
                '/usr/bin/python3', '/usr/bin/python',
                '/usr/local/bin/python3', '/usr/local/bin/python',
                '/opt/homebrew/bin/python3', '/opt/homebrew/bin/python',
            ]
            for path in common_paths:
                if self._is_valid_python(path) and path not in found_paths:  # ← 用统一的
                    found_paths.append(path)
        # 4. 源码模式添加当前 Python
        if not getattr(sys, 'frozen', False):
            if self._is_valid_python(sys.executable) and sys.executable not in found_paths:  # ← 用统一的
                found_paths.append(sys.executable)
        # 6. 强制排序：项目 venv → 系统 → common_venv
        project_venv = []
        system_py = []
        common_venv = []
        for path in found_paths:
            path_lower = path.lower()
            if 'common_venv' in path_lower:
                common_venv.append(path)
            elif '.venv' in path_lower:
                project_venv.append(path)
            else:
                system_py.append(path)
        sorted_paths = project_venv + system_py + common_venv
        # 7. 更新UI
        self.python_path.clear()
        for py in sorted_paths:
            self.python_path.addItem(py)
        if sorted_paths:
            self.python_path.setCurrentIndex(0)
            self.safe_log(f"🐍 优先选中: {sorted_paths[0]}")
            self.safe_log(f"✅ 找到 {len(sorted_paths)} 个 Python 解释器")
        self._on_python_selected()

    def _refresh_python_list(self):
        self.safe_log("🔄 刷新Python列表...")
        self._find_all_python()
        self._filter_python_list()
        # ===== 强制排序：从当前列表中读取所有路径，重新排序 =====
        all_paths = []
        for i in range(self.python_path.count()):
            all_paths.append(self.python_path.itemText(i))
        # 分类排序
        project_venv = []
        system_py = []
        common_venv = []
        for path in all_paths:
            path_lower = path.lower()
            if 'common_venv' in path_lower:
                common_venv.append(path)
            elif '.venv' in path_lower:
                project_venv.append(path)
            else:
                system_py.append(path)
        sorted_paths = project_venv + system_py + common_venv
        # 重新填充列表
        self.python_path.clear()
        for path in sorted_paths:
            self.python_path.addItem(path)
        # 优先选中项目 venv（第一个）
        if sorted_paths:
            self.python_path.setCurrentIndex(0)
        QTimer.singleShot(50, self._on_python_path_delayed)

    def _on_python_path_delayed(self):
        """延迟处理Python路径变化（用于刷新列表后）"""
        python_exe = self.python_path.currentText()
        if python_exe and os.path.exists(python_exe):
            self._on_python_path_changed(python_exe)

    def _set_python_path(self, path, fast=False):
        """快速设置Python路径"""
        idx = self.python_path.findText(path)
        if idx >= 0:
            self.python_path.setCurrentIndex(idx)
        else:
            self.python_path.addItem(path)
            self.python_path.setCurrentText(path)
        if not fast:
            self._on_python_selected()
        else:
            # 快速模式：显示默认文本，稍后更新
            self.python_version.setText("检测中...")
            self.status_python.setText("🐍 Python: 检测中...")

    def _on_python_path_changed(self,  new_path=None):
        """Python路径变化时：立即替换 sys.path"""
        if not new_path or not os.path.exists(new_path):
            return
        if hasattr(self, '_last_python_path') and self._last_python_path == new_path:
            return
        self._last_python_path = new_path
        # ===== 核心：立即替换 sys.path，只保留选定Python的路径 =====
        python_dir = os.path.dirname(new_path)
        python_lib = os.path.join(python_dir, 'Lib')
        python_dlls = os.path.join(python_dir, 'DLLs')
        # 获取site-packages
        site_packages = None
        try:
            result = self._run_hidden(
                [new_path, '-c', 'import site; print(site.getsitepackages()[0])'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                site_packages = result.stdout.strip()
        except:
            pass
        if not site_packages or not os.path.exists(site_packages):
            for sp in [os.path.join(python_dir, 'Lib', 'site-packages'),
                       os.path.join(python_dir, 'lib', 'site-packages')]:
                if os.path.exists(sp):
                    site_packages = sp
                    break
        # 构建新的 sys.path（只包含选定Python的路径）
        new_sys_path = []
        # 1. 当前脚本目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir and os.path.exists(script_dir):
            new_sys_path.append(script_dir)
        # 2. Python Lib 目录
        if python_lib and os.path.exists(python_lib):
            new_sys_path.append(python_lib)
        # 3. Python DLLs 目录
        if python_dlls and os.path.exists(python_dlls):
            new_sys_path.append(python_dlls)
        # 4. Python 根目录
        if python_dir and os.path.exists(python_dir):
            new_sys_path.append(python_dir)
        # 5. site-packages（选定Python的）
        if site_packages and os.path.exists(site_packages):
            new_sys_path.append(site_packages)
        # 6. 如果开启了虚拟环境，添加虚拟环境的site-packages
        if self.use_venv:
            venv_site = self._get_venv_site_packages()
            if venv_site and os.path.exists(venv_site) and venv_site not in new_sys_path:
                new_sys_path.append(venv_site)
        # ===== 替换 sys.path =====
        import sys
        sys.path = new_sys_path
        # 保存缓存
        self._update_cache_python(new_path)
        # 获取Python版本
        try:
            result = self._run_hidden([new_path, '--version'], capture_output=True, text=True, timeout=5)
            ver = result.stdout.strip() or result.stderr.strip()
            if ver:
                self.python_version.setText(ver)
                self.status_python.setText(f"🐍 {ver}")
        except:
            pass
        # 检测打包器版本
        self._packer_versions_detected = False
        self._detecting_packer_versions = False
        QTimer.singleShot(100, self._detect_all_packer_versions_async)
        current_packer = self.packer_combo.currentText()
        QTimer.singleShot(200, lambda: self._display_packer_version_from_cache(current_packer))

    def _on_python_selected(self):
        """用户选择了Python路径（保留用于按钮点击兼容）"""
        if getattr(self, '_refreshing', False):
            return
        path = self.python_path.currentText()
        if path and os.path.exists(path):
            try:
                result = self._run_hidden([path, '--version'], capture_output=True, text=True,
                                          startupinfo=get_startupinfo())
                ver = result.stdout.strip() or result.stderr.strip()
                if ver:
                    self.python_version.setText(ver)
                    self.status_python.setText(f"🐍 {ver}")
                    # ===== 更新当前打包器版本显示（从缓存或触发检测）=====
                    current_packer = self.packer_combo.currentText()
                    self._display_packer_version_from_cache(current_packer)
                    # ===== 如果当前打包器无缓存，触发后台检测 =====
                    display = self._get_packer_display_name(current_packer)
                    cache_key = f"{display}@{path}"
                    if cache_key not in self._packer_versions_cache:
                        QTimer.singleShot(100, self._detect_all_packer_versions_async)
            except Exception:
                pass

    def _detect_all_packer_versions_async(self):
        """检测当前Python环境下的所有打包器版本（只在缓存没有时检测）"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            return
        if self._detecting_packer_versions:
            return
        # ===== 检查是否所有打包器都有缓存了 =====
        packers = ["PyInstaller", "Nuitka", "PyApp", "Py2exe", "Cx_Freeze", "Pynsist", "PyOxidizer", "Py2app"]
        all_cached = True
        for packer in packers:
            cache_key = f"{packer}@{python_exe}"
            if cache_key not in self._packer_versions_cache:
                all_cached = False
                break
        # ===== 如果都有缓存，直接显示，不检测 =====
        if all_cached:
            current = self.packer_combo.currentText()
            display = self._get_packer_display_name(current)
            cache_key = f"{display}@{python_exe}"
            version = self._packer_versions_cache.get(cache_key)
            if version is not None:
                self._update_packer_status(display, version or "")
            return
        self._detecting_packer_versions = True

        def detect():
            try:
                detected_count = 0
                results = {}
                # 保留其他Python环境的缓存
                try:
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        old_cache = json.load(f)
                        old_versions = old_cache.get('packer_versions', {})
                        for key, value in old_versions.items():
                            if '@' in key:
                                py_path = key.split('@', 1)[1]
                                if py_path != python_exe:
                                    results[key] = value
                except Exception:
                    pass
                # ===== 只检测缺失的打包器 =====
                missing_packers = []
                for packer in packers:
                    cache_key = f"{packer}@{python_exe}"
                    if cache_key not in self._packer_versions_cache:
                        missing_packers.append(packer)
                if not missing_packers:
                    self._detecting_packer_versions = False
                    return
                for packer in missing_packers:
                    cache_key = f"{packer}@{python_exe}"
                    version = self._check_packer_version(packer, python_exe)
                    results[cache_key] = version
                    if version:
                        detected_count += 1
                        self.safe_log(f"  ✅ {packer}: {version}")
                    else:
                        self.safe_log(f"  ❌ {packer}: 未安装")
                # 更新内存缓存
                self._packer_versions_cache.update(results)
                self._packer_versions_detected = True
                self._packer_cache_loaded = True
                # 保存到文件缓存
                try:
                    cache_data = {}
                    if os.path.exists(self.global_cache_file):
                        with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                            cache_data = json.load(f)
                    if 'packer_versions' not in cache_data:
                        cache_data['packer_versions'] = {}
                    cache_data['packer_versions'].update(results)
                    with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
                # 更新UI
                current = self.packer_combo.currentText()
                display = self._get_packer_display_name(current)
                cache_key = f"{display}@{python_exe}"
                version = results.get(cache_key)
                if version is not None:
                    self.packer_ver_signal.emit(display, version or "")
            except Exception as e:
                self.safe_log(f"❌ 检测打包器版本失败: {e}")
            finally:
                self._detecting_packer_versions = False
        threading.Thread(target=detect, daemon=True).start()

    def _test_python(self):
        path = self.python_path.currentText()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "警告", "请选择有效的Python路径")
            return
        try:
            result = self._run_hidden([path, '-c', 'import sys; print(sys.version); print(sys.executable)'],
                                    capture_output=True, text=True, startupinfo=get_startupinfo())
            if result.returncode == 0: show_msg(self, "Python测试", result.stdout,1)
            else: QMessageBox.critical(self, "错误", result.stderr)
        except Exception as e: QMessageBox.critical(self, "错误", str(e))

    def _clear_python(self):
        """清除Python路径 - 最简单版"""
        try:
            self.python_path.setEditText("")
            self.python_version.setText("")
            self.status_python.setText("🐍 Python: 未设置")
            self.safe_log("🗑 已清除Python路径")
        except:
            pass
    # ==================== 依赖分析 ====================

    def _parse_imports(self, script_path):
        imports = set()
        try:
            with open(script_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                source = f.read()
            # 1. AST分析静态导入
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
            # 2. 正则检测动态导入（__import__, importlib.import_module）
            dynamic_patterns = [
                r'__import__\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)',  # __import__('module')
                r'import_module\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)',  # import_module('module')
                r'exec\s*\(\s*[\'"]import\s+([a-zA-Z_][a-zA-Z0-9_]*)',  # exec("import module")
                r'__builtins__\s*\[\s*[\'"]__import__[\'"]\s*\]\s*\(\s*[\'"]([a-zA-Z_][a-zA-Z0-9_]*)',  # __builtins__['__import__']('module')
            ]
            for pattern in dynamic_patterns:
                for match in re.finditer(pattern, source):
                    mod = match.group(1)
                    if mod and mod not in STANDARD_LIBS:
                        imports.add(mod)
            # 3. 检测字符串中的模块名（启发式）
            string_pattern = r'[\'"]([a-zA-Z_][a-zA-Z0-9_]*(?:[-_][a-zA-Z_][a-zA-Z0-9_]*)+)[\'"]'
            for match in re.finditer(string_pattern, source):
                mod = match.group(1).replace('-', '_')
                if mod not in STANDARD_LIBS and len(mod) > 3:
                    if mod in MODULE_TO_PACKAGE or mod.lower() in [k.lower() for k in MODULE_TO_PACKAGE]:
                        imports.add(mod)
        except Exception as e:
            self.safe_log(f"⚠️ 解析导入失败: {e}")
        return imports

    def _build_exclude_list_from_analysis(self):
        """构建排除列表（保留原始大小写，显示完整信息）"""
        if self._building_exclude:
            return
        self._building_exclude = True
        try:
            if not self.analyzed_modules:
                return
            # ===== 获取用户手动排除的 =====
            manual_excludes_lower = set()
            if hasattr(self, 'manual_exclude_list'):
                for pkg in self.manual_exclude_list:
                    manual_excludes_lower.add(pkg.lower())
            # ===== 获取已安装的包 =====
            python_exe = self.python_path.currentText()
            if not python_exe or not os.path.exists(python_exe):
                python_exe = sys.executable
            installed_lower_map = self._get_installed_packages(python_exe)
            if not installed_lower_map:
                self.safe_log("⚠️ 无法获取已安装包列表，跳过排除构建")
                return
            # ===== 获取真实导入和附属依赖 =====
            real_imports = self.real_imports if hasattr(self, 'real_imports') else []
            extra_deps = self.extra_deps if hasattr(self, 'extra_deps') else []
            # ===== 需要自动保留的包 =====
            needed_lower = set()
            # 1. 从 real_imports 添加
            for mod in real_imports:
                if mod in STANDARD_LIBS:
                    continue
                mod_lower = mod.lower()
                if mod_lower in DEPENDENCY_MAP:
                    for pkg in DEPENDENCY_MAP[mod_lower]:
                        needed_lower.add(pkg.lower())
                else:
                    pkg = MODULE_TO_PACKAGE.get(mod, mod)
                    needed_lower.add(pkg.lower())
                needed_lower.add(mod_lower)
            # 2. 从 extra_deps 添加
            for dep in extra_deps:
                dep_lower = dep.lower()
                if dep_lower in DEPENDENCY_MAP:
                    for pkg in DEPENDENCY_MAP[dep_lower]:
                        needed_lower.add(pkg.lower())
                else:
                    pkg = MODULE_TO_PACKAGE.get(dep, dep)
                    needed_lower.add(pkg.lower())
                needed_lower.add(dep_lower)
            # 3. 从 hidden_imports_list 添加
            for mod in self.hidden_imports_list:
                if mod in STANDARD_LIBS:
                    continue
                mod_lower = mod.lower()
                if mod_lower in DEPENDENCY_MAP:
                    for pkg in DEPENDENCY_MAP[mod_lower]:
                        needed_lower.add(pkg.lower())
                else:
                    pkg = MODULE_TO_PACKAGE.get(mod, mod)
                    needed_lower.add(pkg.lower())
                needed_lower.add(mod_lower)
            # 4. 从 analyzed_modules 添加（兜底）
            for mod in self.analyzed_modules:
                if mod in STANDARD_LIBS:
                    continue
                mod_lower = mod.lower()
                if mod_lower in DEPENDENCY_MAP:
                    for pkg in DEPENDENCY_MAP[mod_lower]:
                        needed_lower.add(pkg.lower())
                else:
                    pkg = MODULE_TO_PACKAGE.get(mod, mod)
                    needed_lower.add(pkg.lower())
                needed_lower.add(mod_lower)
            # 5. RUNTIME_SAFE_KEEP
            for keep in RUNTIME_SAFE_KEEP:
                needed_lower.add(keep.lower())
                needed_lower.add(keep.lower().replace('_', '-'))
                needed_lower.add(keep.lower().replace('-', '_'))
            def _is_needed(pkg_lower):
                return (pkg_lower in needed_lower
                        or pkg_lower.replace('-', '_') in needed_lower
                        or pkg_lower.replace('_', '-') in needed_lower)
            auto_exclude_enabled = self.auto_exclude_cb.isChecked() if hasattr(self, 'auto_exclude_cb') else True
            exclude = []
            keep_packages = {}
            other_packages = []
            real_imports_lower = {r.lower() for r in real_imports}
            extra_deps_lower = {e.lower() for e in extra_deps}
            module_to_package_lower = {v.lower() for v in MODULE_TO_PACKAGE.values()}
            if auto_exclude_enabled:
                for pkg_lower, pkg_original in installed_lower_map.items():
                    if pkg_lower in STANDARD_LIBS or pkg_lower.startswith('_'):
                        continue
                    if pkg_lower in NEVER_PACK:
                        other_packages.append(pkg_original)
                        continue
                    if pkg_lower in manual_excludes_lower:
                        exclude.append(pkg_original)
                        continue
                    if _is_needed(pkg_lower):
                        reasons = set()
                        # ===== 1. 导入依赖 =====
                        if pkg_lower in real_imports_lower:
                            reasons.add("导入依赖")
                        else:
                            for mod in real_imports:
                                if MODULE_TO_PACKAGE.get(mod, '').lower() == pkg_lower:
                                    reasons.add("导入依赖")
                                    break
                        # ===== 2. 附属依赖 =====
                        if "导入依赖" not in reasons:
                            if pkg_lower in extra_deps_lower:
                                reasons.add("附属依赖")
                            else:
                                for dep in extra_deps:
                                    if MODULE_TO_PACKAGE.get(dep, '').lower() == pkg_lower:
                                        reasons.add("附属依赖")
                                        break
                        # ===== 3. 其他保留原因 =====
                        if "导入依赖" not in reasons and "附属依赖" not in reasons:
                            if pkg_lower in RUNTIME_SAFE_KEEP or pkg_lower.replace('-', '_') in RUNTIME_SAFE_KEEP:
                                reasons.add("运行必需")
                            for mod, deps in DEPENDENCY_MAP.items():
                                if pkg_lower in [d.lower() for d in deps]:
                                    reasons.add(f"依赖关联({mod})")
                                    break
                            if pkg_lower in module_to_package_lower:
                                reasons.add("包名映射")
                        if not reasons:
                            reasons.add("预制保留")
                        keep_packages[pkg_original] = reasons
                        continue
                    exclude.append(pkg_original)
            else:
                for pkg_lower in manual_excludes_lower:
                    if pkg_lower in installed_lower_map:
                        exclude.append(installed_lower_map[pkg_lower])
            # ===== 按原因分类统计 =====
            keep_by_reason = {}
            for pkg, reasons in keep_packages.items():
                for reason in reasons:
                    if reason not in keep_by_reason:
                        keep_by_reason[reason] = []
                    keep_by_reason[reason].append(pkg)
            # ===== 更新界面 =====
            exclude_unique = list(set(exclude))
            self.exclude_list = exclude_unique
            self.exclude_listbox.clear()
            for m in sorted(exclude_unique):
                item = QListWidgetItem(m)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.exclude_listbox.addItem(item)
            self._update_exclude_count()
            # ===== 计算总数 =====
            total_installed = len(installed_lower_map)
            total_excluded = len(exclude_unique)
            total_kept = len(keep_packages)
            total_other = len(other_packages)
            total_manual = len(manual_excludes_lower)
            total_auto = total_excluded - total_manual
            # ===== 自洽修正 =====
            diff = total_installed - (total_excluded + total_kept + total_other)
            if diff != 0:
                # 把差值归入"其他未分类"
                if "其他分类" not in keep_by_reason:
                    keep_by_reason["其他分类"] = []
                classified_packages = set(exclude_unique) | set(keep_packages.keys()) | set(other_packages)
                for pkg_lower, pkg_original in installed_lower_map.items():
                    if pkg_original not in classified_packages:
                        keep_by_reason["其他分类"].append(pkg_original)
                        if pkg_original not in keep_packages:
                            keep_packages[pkg_original] = {"其他分类"}
                total_kept = len(keep_packages)
                total_other = len(other_packages)
            # ===== 显示日志 =====
            if real_imports:
                self.safe_log(f"📦 导入依赖 {len(real_imports)} 个: {', '.join(sorted(real_imports))}")
            if extra_deps:
                self.safe_log(f"📦 附属依赖 {len(extra_deps)} 个: {', '.join(sorted(extra_deps))}")
            if total_manual > 0:
                self.safe_log(f"📊 手动排除 {total_manual} 个包")
            #if auto_exclude_enabled and total_auto > 0:
                #self.safe_log(f"📊 自动排除 {total_auto} 个包")
            if keep_by_reason:
                #self.safe_log(f"📋 保留包分类 ({total_kept} 个):")
                reason_order = ["导入依赖", "附属依赖", "运行必需", "依赖关联", "包名映射", "预制保留", "其他分类"]
                for reason in reason_order:
                    if reason in keep_by_reason:
                        unique_packages = list(set(keep_by_reason[reason]))
                        display = ', '.join(sorted(unique_packages)[:10])
                        if len(unique_packages) > 10:
                            display += f' ... 等 {len(unique_packages)} 个'
                        #self.safe_log(f"   📌 {reason}: {len(unique_packages)} 个: {display}")
                #self.safe_log(f"📊 总计保留: {total_kept} 个包（去重后）")
            if other_packages:
                display = ', '.join(sorted(other_packages)[:10])
                if len(other_packages) > 10:
                    display += f' ... 等 {len(other_packages)} 个'
                #self.safe_log(f"📌 预排列表 (NEVER_PACK): {len(other_packages)} 个: {display}")
            # ===== 最终自洽验证 =====
            final_total = total_excluded + len(keep_packages) + len(other_packages)
            #self.safe_log(f"📊 自洽验证: 已安装 {total_installed} = 排除 {total_excluded} + 保留 {len(keep_packages)} + 其他 {len(other_packages)}")
            if total_installed == final_total:
                pass
                #self.safe_log(f"✅ 数量完全自洽")
            else:
                # 极端情况：如果还不自洽，强制修正
                remaining = total_installed - total_excluded - len(other_packages)
                if remaining > 0:
                    if "其他分类" not in keep_by_reason:
                        keep_by_reason["其他分类"] = []
                    classified = set(exclude_unique) | set(keep_packages.keys()) | set(other_packages)
                    for pkg_lower, pkg_original in installed_lower_map.items():
                        if pkg_original not in classified:
                            keep_by_reason["其他分类"].append(pkg_original)
                            if pkg_original not in keep_packages:
                                keep_packages[pkg_original] = {"其他分类"}
                #self.safe_log(f"✅ 已自动修正，数量完全自洽")
            if exclude_unique:
                preview = ', '.join(sorted(exclude_unique)[:20])
                if len(exclude_unique) > 20:
                    preview += f' ... 等 {len(exclude_unique)} 个'
                self.safe_log(f"🚫 排除列表: {preview}")
        finally:
            self._building_exclude = False

    def _on_auto_exclude_toggled(self, state):
        """排除开关切换时，刷新排除列表"""
        script = self.input_file.text()
        if script and os.path.exists(script):
            # 如果还没有分析结果，先分析
            if not self.analyzed_modules:
                self._analyze_used(script, auto_add=False)
            self._build_exclude_list_from_analysis()
            self.safe_log(f"🔄 排除开关: {'启用' if state else '禁用'}")

    def _analyze_used(self, script_path, auto_add=True):
        """分析脚本依赖 - 返回 (result, real_imports, extra_deps, uses_tkinter)"""
        # ===== 防止短时间内重复分析同一个文件 =====
        current_time = time.time()
        if hasattr(self, '_last_analyzed_file') and self._last_analyzed_file == script_path:
            if current_time - getattr(self, '_last_analyzed_time', 0) < 2:
                return self.analyzed_modules
        self._last_analyzed_file = script_path
        self._last_analyzed_time = current_time
        try:
            with open(script_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                source = f.read()
        except:
            return []
        imports = set()
        uses_tkinter = False
        # ===== 1. AST 解析所有 import =====
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        mod = alias.name.split('.')[0]
                        if mod == 'tkinter':
                            uses_tkinter = True
                            imports.add('tk')
                        elif mod == 'tk':
                            imports.add('tk')
                        elif mod not in STANDARD_LIBS:
                            imports.add(mod)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        mod = node.module.split('.')[0]
                        if mod == 'tkinter':
                            uses_tkinter = True
                            imports.add('tk')
                        elif mod == 'tk':
                            imports.add('tk')
                        elif mod not in STANDARD_LIBS:
                            imports.add(mod)
        except Exception as e:
            self.safe_log(f"⚠️ AST解析失败: {e}")
            import re
            for line in source.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    if 'tkinter' in line:
                        uses_tkinter = True
                        imports.add('tk')
                    else:
                        match = re.match(r'(?:from\s+(\S+)\s+import|import\s+(\S+))', line)
                        if match:
                            mod = match.group(1) or match.group(2)
                            if mod:
                                mod = mod.split('.')[0]
                                if mod not in STANDARD_LIBS:
                                    imports.add(mod)
        result = []
        for mod in sorted(imports):
            mod_clean = mod.split('==')[0].split(' ')[0].strip()
            if mod_clean and mod_clean not in FILTER_MODULES:
                if mod_clean not in result:
                    result.append(mod_clean)
        # ===== 3. 确保 tk 在结果中 =====
        if uses_tkinter and 'tk' not in result:
            result.append('tk')
        # ===== 4. 自动补充隐式依赖 =====
        # 保存真实导入（原始 result）
        real_imports = result.copy()
        # 添加附属依赖到 result
        extra_deps = set()
        for mod, deps in DEPENDENCY_MAP.items():
            if mod in result:
                for dep in deps:
                    if dep not in result:
                        result.append(dep)
                        extra_deps.add(dep)
        self.analyzed_modules = result
        self.real_imports = real_imports
        self.extra_deps = list(extra_deps)
        # ===== 5. 自动设置 Nuitka 插件 =====
        if uses_tkinter:
            if hasattr(self, 'nuitka_gui_plugin_combo'):
                if self.nuitka_gui_plugin_combo.currentText() != 'tk-inter':
                    self.nuitka_gui_plugin_combo.setCurrentText('tk-inter')
        # ===== 6. 添加到隐藏导入列表 =====
        if auto_add:
            self.hidden_imports_list = result.copy()
            self.hidden_listbox.clear()
            for mod in result:
                item = QListWidgetItem(mod)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.hidden_listbox.addItem(item)
            self._update_hidden_count()
            # ===== 显示导入信息 =====
            if result:
                if real_imports:
                    imports_display = ', '.join(real_imports[:10])
                    if len(real_imports) > 10:
                        imports_display += f' ... 等 {len(real_imports)} 个'
                    self.safe_log(f"📦 导入依赖 {len(real_imports)} 个: {imports_display}")
                if extra_deps:
                    extra_display = ', '.join(sorted(extra_deps)[:10])
                    if len(extra_deps) > 10:
                        extra_display += f' ... 等 {len(extra_deps)} 个'
                    self.safe_log(f"📦 附属依赖 {len(extra_deps)} 个: {extra_display}")
                total = len(result)
                self.safe_log(f"📦 隐藏导入总计 {total} 个")
                if not self.use_venv:
                    self._check_and_install_missing_deps()
        self._build_exclude_list_from_analysis()
        self._update_auto_import_count()
        return result

    def _check_and_install_missing_deps(self):
        """检查并安装缺失的依赖"""
        if hasattr(self, '_deps_installing') and self._deps_installing:
            return
        # ===== 获取当前选中的 Python =====
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            python_exe = sys.executable
        self.safe_log(f"🔍 使用Python: {python_exe}")
        self._deps_installing = True
        self.status_start("检查依赖", color="blue")
        # ===== 获取已安装的包 =====
        installed_lower_map = self._get_installed_packages(python_exe)
        if not installed_lower_map:
            self.safe_log("⚠️ 无法获取已安装包列表")
            self._deps_installing = False
            return
        # ===== 构建需要的包列表 =====
        needed = set()
        real_imports = self.real_imports if hasattr(self, 'real_imports') else []
        for mod in real_imports:
            if mod in STANDARD_LIBS:
                continue
            mod_lower = mod.lower()
            if mod_lower in DEPENDENCY_MAP:
                for pkg in DEPENDENCY_MAP[mod_lower]:
                    if pkg:
                        needed.add(pkg)
            else:
                pkg = MODULE_TO_PACKAGE.get(mod, mod)
                needed.add(pkg.lower())
        for mod in self.hidden_imports_list:
            if mod in STANDARD_LIBS:
                continue
            mod_lower = mod.lower()
            if mod_lower in DEPENDENCY_MAP:
                for pkg in DEPENDENCY_MAP[mod_lower]:
                    if pkg:
                        needed.add(pkg)
            else:
                pkg = MODULE_TO_PACKAGE.get(mod, mod)
                needed.add(pkg.lower())
        # ===== 找出缺失的 =====
        missing = []
        for pkg_lower in needed:
            if pkg_lower not in installed_lower_map:
                missing.append(pkg_lower)
        if not missing:
            self.safe_log("✅ 所有依赖已安装")
            self._deps_installing = False
            self.status_finish("就绪")
            return
        self.safe_log(f"📦 安装 {len(missing)} 个缺失依赖: {', '.join(missing)}")
        # ===== 安装线程 =====
        class InstallDepsThread(QThread):
            log_signal = pyqtSignal(str)
            progress_signal = pyqtSignal(int)
            status_signal = pyqtSignal(str)
            finished_signal = pyqtSignal(bool)
            def __init__(self, python_exe, packages):
                super().__init__()
                self.python_exe = python_exe
                self.packages = packages

            def run(self):
                clean_env = {'PATH': os.environ.get('PATH', '')}
                if sys.platform == 'win32':
                    clean_env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
                total = len(self.packages)
                for i, pkg_lower in enumerate(self.packages):
                    install_pkg = pkg_lower
                    if pkg_lower == 'pylibrehardwaremonitor':
                        install_pkg = 'PyLibreHardwareMonitor'
                    elif pkg_lower == 'pylibrehardwaremonitorlib':
                        install_pkg = 'PyLibreHardwareMonitorLib'
                    elif pkg_lower == 'pythonnet':
                        install_pkg = 'pythonnet'
                    elif pkg_lower == 'pillow':
                        install_pkg = 'Pillow'
                    elif pkg_lower == 'pyqt6':
                        install_pkg = 'PyQt6'
                    elif pkg_lower == 'psutil':
                        install_pkg = 'psutil'
                    elif pkg_lower == 'docx':
                        install_pkg = 'python-docx'
                    self.status_signal.emit(f"安装 {install_pkg} ({i+1}/{total})")
                    self.log_signal.emit(f"   📥 安装 {install_pkg}...")
                    progress = int((i + 1) / total * 100)
                    self.progress_signal.emit(progress)
                    try:
                        success, result = pip_install(self.python_exe, install_pkg, env=clean_env, timeout=300)
                        if success:
                            self.log_signal.emit(f"   ✅ {install_pkg} 安装成功")
                        else:
                            self.log_signal.emit(f"   ❌ {install_pkg} 安装失败: {result.stderr[:100] if result else '未知错误'}")
                    except subprocess.TimeoutExpired:
                        self.log_signal.emit(f"   ❌ {install_pkg} 安装超时")
                    except Exception as e:
                        self.log_signal.emit(f"   ❌ {install_pkg} 安装异常: {e}")
                self.progress_signal.emit(100)
                self.status_signal.emit("完成")
                self.finished_signal.emit(True)
        self.deps_thread = InstallDepsThread(python_exe, missing)
        self.deps_thread.log_signal.connect(self.safe_log)
        self.deps_thread.progress_signal.connect(self._on_deps_progress)
        self.deps_thread.status_signal.connect(self._on_deps_status)
        self.deps_thread.finished_signal.connect(self._on_deps_finished)
        self.deps_thread.start()

    def _refresh_after_env_change(self):
        """虚拟环境切换后，后台异步刷新分析和排除列表"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            return
        if getattr(self, '_refreshing', False):
            return
        self._refreshing = True

        def async_refresh():
            try:
                self._analyze_used(script, auto_add=False)
            except Exception as e:
                pass
            finally:
                self._refreshing = False
        threading.Thread(target=async_refresh, daemon=True).start()

    def _update_progress_ui(self, value):
        """更新进度UI（主线程）"""
        self.status_progress.setValue(value)
        self.status_pct.setText(f"{value}%")
        QApplication.processEvents()

    def _finish_refresh_ui(self):
        """刷新完成UI（主线程）"""
        self.status_progress.setVisible(False)
        self.status_pct.setVisible(False)
        self.status_label.setText("就绪")
        self.status_progress.setValue(0)
        self.safe_log("✅ 环境分析完成，排除列表已更新")

    def _detect_gui_from_hidden(self):
        """从隐藏导入列表检测GUI框架并强制更新下拉框"""
        if not hasattr(self, 'nuitka_gui_plugin_combo'):
            return
        if not self.hidden_imports_list:
            if hasattr(self, 'gui_display_label'):
                self.gui_display_label.setText("")
            return
        # GUI框架映射
        gui_map = {
            'PyQt6': 'pyqt6',
            'PyQt5': 'pyqt5',
            'PySide6': 'pyside6',
            'PySide2': 'pyside2',
            'tkinter': 'tk-inter',
            'tk': 'tk-inter',
            'wx': 'wxpython',
            'kivy': 'kivy',
        }
        detected = None
        for mod in self.hidden_imports_list:
            if mod in gui_map:
                detected = gui_map[mod]
                break
        if detected:
            self.nuitka_gui_plugin_combo.blockSignals(True)
            self.nuitka_gui_plugin_combo.setCurrentText(detected)
            self.nuitka_gui_plugin_combo.blockSignals(False)
            if hasattr(self, 'gui_display_label'):
                self.gui_display_label.setText(f"✅ {detected}")
                self.gui_display_label.setStyleSheet("color: green")
            self.safe_log(f"🔄 GUI已更新为: {detected}")
        else:
            if hasattr(self, 'gui_display_label'):
                self.gui_display_label.setText("")

    def _detect_gui_framework(self, mod, gui_flags):
        """检测模块是否属于GUI框架"""
        mod_lower = mod.lower()
        # PyQt6
        if mod_lower == 'pyqt6' or mod_lower.startswith('pyqt6.'):
            gui_flags['pyqt6'] = True
        # PyQt5
        elif mod_lower == 'pyqt5' or mod_lower.startswith('pyqt5.'):
            gui_flags['pyqt5'] = True
        # PySide6
        elif mod_lower == 'pyside6' or mod_lower.startswith('pyside6.'):
            gui_flags['pyside6'] = True
        # PySide2
        elif mod_lower == 'pyside2' or mod_lower.startswith('pyside2.'):
            gui_flags['pyside2'] = True
        # PySide (通用)
        elif mod_lower == 'pyside' or mod_lower.startswith('pyside.'):
            gui_flags['pyside'] = True
        # tkinter
        elif mod_lower == 'tkinter' or mod_lower.startswith('tkinter.'):
            gui_flags['tk-inter'] = True
        elif mod_lower == 'tk':
            gui_flags['tk-inter'] = True
        # wxPython
        elif mod_lower == 'wx' or mod_lower.startswith('wx.'):
            gui_flags['wx'] = True
        # Kivy
        elif mod_lower == 'kivy' or mod_lower.startswith('kivy.'):
            gui_flags['kivy'] = True

    def _auto_update_gui_plugin(self, gui_flags):
        """根据检测到的GUI框架自动更新Nuitka GUI插件"""
        if not hasattr(self, 'nuitka_gui_plugin_combo'):
            return
        # ===== 映射：检测标志 -> 下拉框值 =====
        plugin_map = {
            'pyqt6': 'pyqt6',
            'pyside6': 'pyside6',
            'pyqt5': 'pyqt5',
            'pyside2': 'pyside2',
            'tkinter': 'tk-inter',
            'tk': 'tk-inter',
            'wx': 'wxpython',
            'kivy': 'kivy',
        }
        # ===== 按优先级检测 =====
        detected = None
        plugin_name = None
        # 优先级：PyQt6 > PySide6 > PyQt5 > PySide2 > Tkinter > wxPython > Kivy
        if gui_flags.get('pyqt6', False):
            detected = 'PyQt6'
            plugin_name = 'pyqt6'
        elif gui_flags.get('pyside6', False):
            detected = 'PySide6'
            plugin_name = 'pyside6'
        elif gui_flags.get('pyqt5', False):
            detected = 'PyQt5'
            plugin_name = 'pyqt5'
        elif gui_flags.get('pyside2', False):
            detected = 'PySide2'
            plugin_name = 'pyside2'
        elif gui_flags.get('pyside', False):
            # 检测到通用的PySide，默认使用PySide6
            detected = 'PySide'
            plugin_name = 'pyside6'
            self.safe_log("⚠️ 检测到 PySide，默认使用 PySide6 插件")
        elif gui_flags.get('tkinter', False):
            detected = 'tkinter'
            plugin_name = 'tk-inter'
        elif gui_flags.get('tk', False):
            detected = 'tk'
            plugin_name = 'tk-inter'
        elif gui_flags.get('wx', False):
            detected = 'wxPython'
            plugin_name = 'wxpython'
        elif gui_flags.get('kivy', False):
            detected = 'Kivy'
            plugin_name = 'kivy'
        # ===== 更新UI =====
        if plugin_name:
            # 检查下拉框中是否存在该值
            index = self.nuitka_gui_plugin_combo.findText(plugin_name)
            if index < 0:
                self.safe_log(f"⚠️ 插件 '{plugin_name}' 不在下拉列表中")
                return
            # 只有当前是 'auto' 或者与检测到的不一致时才更新
            current = self.nuitka_gui_plugin_combo.currentText()
            if current == 'auto' or current != plugin_name:
                self.nuitka_gui_plugin_combo.blockSignals(True)
                self.nuitka_gui_plugin_combo.setCurrentIndex(index)
                self.nuitka_gui_plugin_combo.blockSignals(False)
                # 更新显示标签
                if hasattr(self, 'gui_display_label'):
                    self.gui_display_label.setText(f"✅ {detected}")
                    self.gui_display_label.setStyleSheet("color: green; font-weight: bold;")
                self.safe_log(f"🔄 GUI插件已自动更新为: {plugin_name} ({detected})")
            else:
                if hasattr(self, 'gui_display_label'):
                    self.gui_display_label.setText(f"✅ {detected}")
                    self.gui_display_label.setStyleSheet("color: green;")
        else:
            # 没有检测到GUI框架
            if hasattr(self, 'gui_display_label'):
                self.gui_display_label.setText("ℹ️ 未检测到GUI框架")
                self.gui_display_label.setStyleSheet("color: gray;")
            # 如果当前是 'auto'，保持不变
            if self.nuitka_gui_plugin_combo.currentText() == 'auto':
                pass

    def _update_gui_plugin_for_nuitka(self):
        """在Nuitka打包前，确保GUI插件正确设置"""
        if not hasattr(self, 'nuitka_gui_plugin_combo'):
            return
        if self.nuitka_gui_plugin_combo.currentText() == 'auto':
            script = self.input_file.text()
            if script and os.path.exists(script):
                self.safe_log("🔍 自动检测GUI框架...")
                self._analyze_used(script, auto_add=False)
            else:
                self.safe_log("⚠️ 未选择脚本，无法自动检测GUI")

    def _check_tkinter_usage(self, script_path):
        """检测脚本是否真正使用了 tkinter """
        try:
            with open(script_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                source = f.read()
            import re
            uses_tkinter = False
            for line in source.split('\n'):
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line.startswith('import tkinter') or line.startswith('from tkinter'):
                    uses_tkinter = True
                    break
            if uses_tkinter:
                self.safe_log("🖥️ 检测到 tkinter import")
                if 'tk' not in self.hidden_imports_list:
                    self.hidden_imports_list.append('tk')
                    self.hidden_listbox.addItem('tk')
                    self._update_hidden_count()
                if hasattr(self, 'nuitka_gui_plugin_combo'):
                    if self.nuitka_gui_plugin_combo.currentText() != 'tk-inter':
                        self.nuitka_gui_plugin_combo.setCurrentText('tk-inter')
                return True
            return False
        except Exception as e:
            self.safe_log(f"⚠️ tkinter 检测失败: {e}")
            return False

    def _is_internal_module(self, mod):
        """判断是否是Python内部模块（跨平台）"""
        if sys.platform == 'win32':
            win_modules = {'winreg', 'msvcrt', 'ctypes.wintypes', 'pywin32', 'win32api', 'win32con'}
            if mod in win_modules:
                return True
        if sys.platform.startswith('linux'):
            linux_modules = {'fcntl', 'grp', 'pwd', 'resource', 'syslog'}
            if mod in linux_modules:
                return True
        if sys.platform == 'darwin':
            mac_modules = {'Carbon', 'Cocoa', 'Quartz', 'ScriptingBridge', 'pyobjc'}
            if mod in mac_modules:
                return True
        return False

    def _analyze_missing(self, script_path):
        used = self._analyze_used(script_path)
        installed = self._get_installed()
        # ===== 自动补充依赖关系 =====
        if 'openpyxl' in used:
            used.append('et_xmlfile')
        if 'requests' in used:
            used.append('urllib3')
            used.append('certifi')
        missing = []
        for mod in used:
            if mod in STANDARD_LIBS:
                continue
            pkg = MODULE_TO_PACKAGE.get(mod, mod)
            if pkg.lower() not in installed:
                missing.append(mod)
        return missing

    def _get_installed(self):
        if self.installed_packages is not None:
            return self.installed_packages
        # 获取目标Python解释器
        target_python = getattr(self, '_last_target_python', sys.executable)
        try:
            result = self._run_hidden(
                [target_python, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True, startupinfo=get_startupinfo()
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                self.installed_packages = {item['name'].lower() for item in data}
                return self.installed_packages
        except Exception as e:
            self.safe_log(f"⚠️ 获取已安装包列表失败: {e}")
        self.installed_packages = set()
        return self.installed_packages

    def _analyze_deps(self):
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            #QMessageBox.warning(self, "警告", "请先选择Python脚本")
            return
        # 确定目标Python解释器（供后续安装使用）
        target_python = sys.executable
        if self.use_venv:
            venv_dir = os.path.join(self.current_dir, "common_venv")
            if sys.platform == 'win32':
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")
            if os.path.exists(venv_python):
                target_python = venv_python
        # 保存供其他方法使用
        self._last_target_python = target_python
        self.safe_log("🔬 分析依赖...")
        used = self._analyze_used(script)
        # ===== 自动补充依赖关系 =====
        if 'openpyxl' in used:
            used.append('et_xmlfile')
        if 'requests' in used:
            used.append('urllib3')
            used.append('certifi')
        missing = self._analyze_missing(script)
        self.safe_log(f"📦 使用模块: {', '.join(used) if used else '无'}")
        for mod in used:
            if mod not in self.hidden_imports_list:
                self.hidden_imports_list.append(mod)
                self.hidden_listbox.addItem(mod)
        self._update_hidden_count()
        if missing:
            reply = QMessageBox.question(self, "安装依赖", f"检测到缺失模块: {', '.join(missing)}\\n\\n是否自动安装？")
            if reply == QMessageBox.StandardButton.Yes:
                self._batch_install(missing)

    def _batch_install(self, modules):
        # 获取目标Python解释器（从config或当前环境）
        target_python = getattr(self, '_last_target_python', sys.executable)
        for mod in modules:
            # 获取正确的包名
            pkg = MODULE_TO_PACKAGE.get(mod, mod)
            # et_xmlfile 特殊处理
            if mod == 'et_xmlfile':
                pkg = 'et_xmlfile'
            if mod == 'urllib3':
                pkg = 'urllib3'
            if mod == 'certifi':
                pkg = 'certifi'
            self.safe_log(f"📦 安装 {pkg}...")
            try:
                if use_uv:
                    # 使用 uv 加速安装
                    cmd = [target_python, '-m', 'uv', 'pip', 'install', pkg, '-i', MIRROR]
                else:
                    cmd = [target_python, '-m', 'pip', 'install', pkg, '-i', MIRROR]
                result = self._run_hidden(
                    cmd,
                    capture_output=True, text=True, startupinfo=get_startupinfo(), timeout=180
                )
                self.safe_log(f"{'✅' if result.returncode == 0 else '❌'} {pkg}")
            except Exception as e:
                self.safe_log(f"❌ 安装异常: {e}")

    def _auto_install(self):
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            #QMessageBox.warning(self, "警告", "请先选择Python脚本")
            return
        missing = self._analyze_missing(script)
        if missing: self._batch_install(missing)
        else: show_msg(self, "信息", "所有依赖已安装",1)

    def _export_req(self):
        script = self.input_file.text()
        if not script:
            #QMessageBox.warning(self, "警告", "请先选择Python脚本")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "导出requirements", "requirements.txt", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                for mod in self._analyze_used(script):
                    f.write(f"{MODULE_TO_PACKAGE.get(mod, mod)}\n")
            self.safe_log(f"📄 已导出到 {file_path}")

    def _import_req(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入requirements", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.hidden_imports_list.append(line)
                        self.hidden_listbox.addItem(line)
            self._update_hidden_count()
            self.safe_log(f"📂 已从 {file_path} 导入")

    def _auto_import_modules(self):
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            QMessageBox.warning(self, "警告", "请先选择Python脚本")
            return
        if hasattr(self, '_last_analyzed_file') and self._last_analyzed_file == script:
            # 检查时间，如果15秒内分析过，跳过
            if time.time() - getattr(self, '_last_analyzed_time', 0) < 15:
                self.safe_log("⏭️ 跳过重复分析 (15秒内已分析)")
                return
        used = self._analyze_used(script, auto_add=True)
        added = 0
        for mod in used:
            if mod not in self.hidden_imports_list:
                self.hidden_imports_list.append(mod)
                # ===== 创建带复选框的项 =====
                item = QListWidgetItem(mod)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.hidden_listbox.addItem(item)
                added += 1
        self._update_hidden_count()
        if added > 0:
            self.safe_log(f"⚡ 自动导入 {added} 个模块")
    # ==================== 排除模块 ====================

    def _toggle_exclude(self):
        """切换排除面板"""
        if hasattr(self, 'exclude_frame'):
            # 如果排除面板要展开
            if not self.exclude_frame.isVisible():
                # 隐藏数据面板
                if hasattr(self, 'adv_frame') and self.adv_frame.isVisible():
                    self.adv_frame.setVisible(False)
                    self.adv_btn.setText("▶ 数据")
                self.exclude_frame.setVisible(True)
                self.exclude_btn.setText("▼ 排除")
            else:
                self.exclude_frame.setVisible(False)
                self.exclude_btn.setText("▶ 排除")

    def _toggle_advanced(self):
        """切换数据面板"""
        if hasattr(self, 'adv_frame'):
            # 如果数据面板要展开
            if not self.adv_frame.isVisible():
                # 隐藏排除面板
                if hasattr(self, 'exclude_frame') and self.exclude_frame.isVisible():
                    self.exclude_frame.setVisible(False)
                    self.exclude_btn.setText("▶ 排除")
                self.adv_frame.setVisible(True)
                self.adv_btn.setText("▼ 数据")
            else:
                self.adv_frame.setVisible(False)
                self.adv_btn.setText("▶ 数据")

    def _add_exclude(self):
        """添加排除项（用户手动添加）"""
        text = self.exclude_input.text().strip()
        if text:
            existing_lower = {mod.lower() for mod in self.exclude_list}
            added_count = 0
            for mod in text.split(','):
                mod = mod.strip()
                if mod and mod.lower() not in existing_lower:
                    self.exclude_list.append(mod)
                    self.manual_exclude_list.append(mod)  # ← 同时记录手动添加的
                    existing_lower.add(mod.lower())
                    item = QListWidgetItem(mod)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.exclude_listbox.addItem(item)
                    added_count += 1
            self.exclude_input.clear()
            self._update_exclude_count()
            if added_count > 0:
                self.safe_log(f"✅ 已添加 {added_count} 个排除项")

    def _update_exclude_listbox(self):
        """刷新排除列表 UI（保留原始名称）"""
        self.exclude_listbox.clear()
        for mod in sorted(set(self.exclude_list)):  # 用 set 去重，保留原始名称
            item = QListWidgetItem(mod)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, mod)
            self.exclude_listbox.addItem(item)
        self._update_exclude_count()

    def _remove_selected_excludes(self):
        """删除勾选的排除项"""
        checked_items = []
        for i in range(self.exclude_listbox.count()):
            item = self.exclude_listbox.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_items.append((i, item.text()))
        if not checked_items:
            show_msg(self, "提示", "请先勾选要删除的排除项", 1)
            return
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 {len(checked_items)} 个排除项吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        removed = []
        for i, name in reversed(checked_items):
            if name in self.exclude_list:
                self.exclude_list.remove(name)
                removed.append(name)
            self.exclude_listbox.takeItem(i)
        self._update_exclude_count()
        self.safe_log(f"📦 已删除 {len(removed)} 个排除项: {', '.join(removed)}")

    def _remove_exclude(self):
        """从排除列表中移除"""
        current = self.exclude_listbox.currentRow()
        if current >= 0:
            item = self.exclude_listbox.takeItem(current)
            mod = item.text()
            if mod in self.exclude_list:
                self.exclude_list.remove(mod)
            if mod in self.manual_exclude_list:
                self.manual_exclude_list.remove(mod)  # ← 同时从手动列表移除
            self.safe_log(f"📌 已从排除列表移除: {mod}")
            self._update_exclude_count()

    def _clear_excludes(self):
        self.exclude_list.clear()
        self.manual_exclude_list.clear()
        self.exclude_listbox.clear()
        self._update_exclude_count()

    def _open_exclude(self):
        all_modules = list(STANDARD_LIBS) + list(MODULE_TO_PACKAGE.keys())
        installed = list(self._get_installed())
        dialog = ExcludeSelectorDialog(self, all_modules, installed)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            for mod in dialog.get_selected():
                if mod not in self.exclude_list:
                    self.exclude_list.append(mod)
                    # ===== 添加带复选框的项 =====
                    item = QListWidgetItem(mod)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.exclude_listbox.addItem(item)
            self._update_exclude_count()

    def _add_recommended(self):
        for pkg in EXCLUDE_PACKAGES:
            if pkg not in self.exclude_list:
                self.exclude_list.append(pkg)
                # ===== 添加带复选框的项 =====
                item = QListWidgetItem(pkg)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.exclude_listbox.addItem(item)
        self._update_exclude_count()

    def _update_exclude_count(self):
        count = len(self.exclude_list)
        self.exclude_count_label.setText(f"({count})")
        self.exclude_num_label.setText(f"({count})")

    def _add_hidden(self):
        """添加隐藏导入（带复选框）"""
        text = self.hidden_input.text().strip()
        if text:
            for mod in text.split(','):
                mod = mod.strip()
                if mod and mod not in self.hidden_imports_list:
                    self.hidden_imports_list.append(mod)
                    item = QListWidgetItem(mod)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.hidden_listbox.addItem(item)
            self.hidden_input.clear()
            self._update_hidden_count()
            self._update_auto_import_count()

    def _remove_hidden(self):
        """删除所有勾选的隐藏导入，并自动添加到排除列表"""
        checked_items = []
        for i in range(self.hidden_listbox.count()):
            item = self.hidden_listbox.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                checked_items.append((i, item.text()))
        if not checked_items:
            show_msg(self, "提示", "请先在模块前勾选要删除的项",1)
            return
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除 {len(checked_items)} 个模块吗？\n\n{', '.join([name for _, name in checked_items])}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        # ===== 从后往前删除（避免索引变化） =====
        removed_names = []
        for i, name in reversed(checked_items):
            if name in self.hidden_imports_list:
                self.hidden_imports_list.remove(name)
                removed_names.append(name)
                # 自动添加到排除列表
                if name not in self.exclude_list:
                    self.exclude_list.append(name)
                    self.exclude_listbox.addItem(name)
            self.hidden_listbox.takeItem(i)
        self._update_hidden_count()
        self._update_exclude_count()
        self._update_auto_import_count()
        if removed_names:
            self.safe_log(
                f"📌 已删除 {len(removed_names)} 个模块并添加到排除列表: {', '.join(removed_names[:5])}{'...' if len(removed_names) > 5 else ''}")

    def _clear_hidden(self):
        """清空所有隐藏导入，并自动添加到排除列表"""
        if not self.hidden_imports_list:
            return
        reply = QMessageBox.question(
            self,
            "确认清空",
            f"确定要清空所有 {len(self.hidden_imports_list)} 个隐藏导入吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        added = 0
        for mod in self.hidden_imports_list[:]:
            if mod not in self.exclude_list:
                self.exclude_list.append(mod)
                self.exclude_listbox.addItem(mod)
                added += 1
        if added > 0:
            self.safe_log(f"📌 已自动将 {added} 个模块添加到排除列表")
            self._update_exclude_count()
        self.hidden_imports_list.clear()
        self.hidden_listbox.clear()
        self._update_hidden_count()
        self._update_auto_import_count()

    def _add_recommended_hidden(self):
        script = self.input_file.text()
        if script and os.path.exists(script):
            for mod in self._analyze_used(script):
                if mod not in self.hidden_imports_list:
                    self.hidden_imports_list.append(mod)
                    # ===== 创建带复选框的项 =====
                    item = QListWidgetItem(mod)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.hidden_listbox.addItem(mod)
            self._update_hidden_count()

    def _update_hidden_count(self):
        count = len(self.hidden_imports_list)
        self.hidden_num_label.setText(f"({count})")
        self._update_auto_import_count()

    def _update_auto_import_count(self):
        """更新自动导入按钮旁边的数字"""
        if not self.analyzed_modules:
            self.auto_import_count_label.setText("")
            return
        imported = 0
        for m in self.analyzed_modules:
            if m in self.hidden_imports_list:
                imported += 1
        total = len(self.analyzed_modules)
        self.auto_import_count_label.setText(f"({imported}/{total})")
        if imported == total:
            self.auto_import_count_label.setStyleSheet("color: green;")
        else:
            self.auto_import_count_label.setStyleSheet("color: orange;")

    def _select_data_src(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "All Files (*.*)")
        if file_path:
            # 显示为反斜杠
            self.data_src_input.setText(self._format_path(file_path))

    def _add_data(self):
        """手动添加数据文件（带去重）"""
        src = self.data_src_input.text().strip()
        tgt = self.data_tgt_input.text().strip() or "."
        if not src:
            QMessageBox.warning(self, "提示", "请选择数据文件")
            return
        if not os.path.exists(src):
            QMessageBox.warning(self, "提示", f"文件不存在: {src}")
            return
        # 检查是否已存在
        existing = [s for s, _ in self.data_files_list if s == src]
        if existing:
            self.safe_log(f"⚠️ 文件已存在，跳过: {os.path.basename(src)}")
            self.data_src_input.clear()
            return
        self.data_files_list.append((src, tgt))
        # 显示路径用反斜杠
        display_src = self._format_path(src)
        self.data_listbox.addItem(f"{os.path.basename(src)} -> {tgt}")
        self.data_src_input.clear()
        self._refresh_data_list()  # ← 改用这个
        self.safe_log(f"✅ 已添加数据文件: {os.path.basename(src)}")

    def _remove_data(self):
        """删除选中的数据文件"""
        current = self.data_listbox.currentRow()
        if current >= 0:
            item_text = self.data_listbox.currentItem().text()
            display_name = item_text.replace("🚫 ", "")
            src_part = display_name.split(" -> ")[0]
            for i, (src, tgt) in enumerate(self.data_files_list):
                if os.path.basename(src) == src_part:
                    # 从排除列表中移除
                    if hasattr(self, 'exclude_from_pack') and src in self.exclude_from_pack:
                        self.exclude_from_pack.remove(src)
                    self.data_files_list.pop(i)
                    self.safe_log(f"🗑️ 已删除: {src_part}")
                    break
            self._refresh_data_list()  # ← 改用这个

    def _clear_data(self):
        self.data_files_list.clear()
        if hasattr(self, 'exclude_from_pack'):
            self.exclude_from_pack.clear()
        self._refresh_data_list()  # ← 改用这个

    def _open_proj_dir(self):
        """打开项目目录（脚本所在目录）"""
        script = self.input_file.text()
        if script and os.path.exists(script):
            dir_path = os.path.dirname(script)
        else:
            # 如果没有脚本，尝试打开输出目录
            dir_path = self.output_dir.text()
        if not dir_path or not os.path.exists(dir_path):
            self.safe_log(f"⚠️ 目录不存在: {dir_path}")
            return
        # ===== 确保是目录 =====
        if os.path.isfile(dir_path):
            dir_path = os.path.dirname(dir_path)
        try:
            display_path = self._format_path(dir_path)
            self.safe_log(f"📂 打开目录: {display_path}")
            if sys.platform == 'win32':
                try:
                    os.startfile(dir_path)
                except:
                    subprocess.Popen(['explorer', dir_path], shell=False,
                                     creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', dir_path])
            else:
                subprocess.Popen(['xdg-open', dir_path])
        except Exception as e:
            self.safe_log(f"❌ 打开目录失败: {e}")
            QMessageBox.warning(self, "错误", f"无法打开目录:\n{dir_path}\n\n{str(e)}")

    def _scan_data(self):
        """扫描项目目录中的数据文件（带去重）"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            current_dir = self.output_dir.text()
            if not os.path.exists(current_dir):
                QMessageBox.warning(self, "警告", "请先选择Python脚本或设置输出目录")
                return
        else:
            current_dir = os.path.dirname(script)
        data_exts = {'.json', '.yaml', '.yml', '.xml', '.ini', '.conf', '.txt',
                    '.csv', '.db', '.sqlite', '.png', '.jpg', '.gif', '.bmp',
                    '.ico', '.ttf', '.otf', '.wav', '.mp3', '.ogg'}
        found = 0
        skipped = 0
        for root, dirs, files in os.walk(current_dir):
            if any(skip in root for skip in ['dist', 'build', '__pycache__', '.git', 'venv', '.venv']):
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in data_exts:
                    src = os.path.join(root, f)
                    # 检查是否已存在
                    existing = [s for s, _ in self.data_files_list if s == src]
                    if existing:
                        skipped += 1
                        continue
                    rel_path = os.path.relpath(root, current_dir)
                    if rel_path == '.':
                        tgt = '.'
                    else:
                        tgt = rel_path.replace('\\', '/')
                    self.data_files_list.append((src, tgt))
                    # 显示路径用反斜杠
                    display_src = self._format_path(src)
                    self.data_listbox.addItem(f"{os.path.basename(src)} -> {tgt}")
                    found += 1
        self._update_data_count()
        self._refresh_data_list()  
        self.safe_log(f"📁 扫描完成: 新增 {found} 个文件, 跳过 {skipped} 个已存在文件")
        if found == 0 and skipped == 0:
            self.safe_log("💡 提示：支持的数据文件类型: " + ', '.join(sorted(data_exts)))

    def _scan_and_add_resources(self, script_dir):
        """扫描并添加资源文件到 data_files"""
        resource_exts = {'.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg',
                    '.txt', '.json', '.xml', '.yaml', '.yml', '.conf', '.ini', '.cfg'}
        pass

    def _update_data_count(self):
        """更新依赖数据按钮旁边的数字（数据文件数量）"""
        count = len(self.data_files_list)
        self.adv_count_label.setText(f"({count})")
        if count > 0:
            self.adv_count_label.setStyleSheet("color: green;")
        else:
            self.adv_count_label.setStyleSheet("color: gray;")

    def _on_log_drop(self, files):
        """日志区域拖拽文件 """
        self.safe_log(f"📎 日志拖拽接收到 {len(files)} 个文件")
        added_count = 0
        for f in files:
            if os.path.exists(f):
                # 检查是否已存在相同的源文件路径
                existing = [src for src, _ in self.data_files_list if src == f]
                if existing:
                    self.safe_log(f"⚠️ 文件已存在，跳过: {os.path.basename(f)}")
                    continue
                # 添加到数据文件列表
                self.data_files_list.append((f, "."))
                # 显示路径用反斜杠
                display_f = self._format_path(f)
                self.data_listbox.addItem(f"{os.path.basename(f)} -> .")
                self.safe_log(f"✅ 已添加数据文件: {os.path.basename(f)}")
                added_count += 1
        if added_count == 0:
            self.safe_log("📌 没有新文件被添加（所有文件已存在）")
        self._update_data_count()
        self._refresh_data_list()  

    def _on_data_drop(self, files):
        """处理数据文件拖拽（带去重）"""
        self.safe_log(f"📁 数据区拖拽接收到 {len(files)} 个文件")
        added_count = 0
        for f in files:
            if not os.path.exists(f):
                self.safe_log(f"⚠️ 文件不存在: {f}")
                continue
            # 检查是否已存在相同的源文件路径
            existing = [src for src, _ in self.data_files_list if src == f]
            if existing:
                self.safe_log(f"⚠️ 文件已存在，跳过: {os.path.basename(f)}")
                continue
            # 如果是文件夹，递归添加所有文件（也带去重）
            if os.path.isdir(f):
                count = self._add_directory_files_with_check(f)
                added_count += count
            else:
                # 单个文件
                self.data_files_list.append((f, "."))
                # 显示路径用反斜杠
                display_f = self._format_path(f)
                self.data_listbox.addItem(f"{os.path.basename(f)} -> .")
                self.safe_log(f"✅ 已添加数据文件: {os.path.basename(f)}")
                added_count += 1
        if added_count == 0:
            self.safe_log("📌 没有新文件被添加（所有文件已存在）")
        else:
            self.safe_log(f"📊 共添加 {added_count} 个新文件")
        self._update_data_count()
        self._refresh_data_list() 

    def _add_directory_files_with_check(self, directory, target_dir="."):
        """递归添加目录中的所有文件"""
        count = 0
        skipped = 0
        for root, dirs, files in os.walk(directory):
            # 跳过常见的忽略目录
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'dist', 'build'}]
            for file in files:
                src = os.path.join(root, file)
                # 检查是否已存在
                existing = [s for s, _ in self.data_files_list if s == src]
                if existing:
                    skipped += 1
                    continue
                # 计算相对路径
                rel_path = os.path.relpath(root, directory)
                if rel_path == ".":
                    tgt = target_dir
                else:
                    tgt = os.path.join(target_dir, rel_path).replace("\\", "/")
                self.data_files_list.append((src, tgt))
                self.data_listbox.addItem(f"{os.path.basename(src)} -> {tgt}")
                count += 1
                # 每添加20个文件输出一次进度
                if count % 20 == 0:
                    self.safe_log(f"📁 已添加 {count} 个文件...")
        if count > 0:
            self.safe_log(f"✅ 从目录 '{os.path.basename(directory)}' 添加了 {count} 个文件")
            if skipped > 0:
                self.safe_log(f"📌 跳过了 {skipped} 个已存在的文件")
        elif skipped > 0:
            self.safe_log(f"📌 目录 '{os.path.basename(directory)}' 中没有新文件（所有文件都已存在）")
        return count

    def _on_uv_switch(self, state):
        if state == Qt.CheckState.Checked.value:
            try:
                self._run_hidden(['uv', '--version'], capture_output=True, check=True)
                self.safe_log("⚡ uv已安装")
            except:
                reply = QMessageBox.question(self, "安装uv", "未找到uv。是否自动安装？")
                if reply == QMessageBox.StandardButton.Yes:
                    self._run_hidden(['pip', 'install', 'uv'])
    # ==================== 虚拟环境 ====================

    def _on_venv_switch(self, state):
        self.use_venv = state == Qt.CheckState.Checked.value
        script = self.input_file.text()
        if self.use_venv:
            self.safe_log("🐍 已启用虚拟环境")
            exe_dir = get_exe_directory()
            venv_dir = os.path.join(exe_dir, "common_venv")
            if sys.platform == 'win32':
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
                venv_site = os.path.join(venv_dir, "Lib", "site-packages")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")
                py_ver = sys.version_info
                venv_site = os.path.join(venv_dir, "lib", f"python{py_ver.major}.{py_ver.minor}", "site-packages")
            # 清理环境变量
            python_env_keys = [
                'PYTHONPATH', 'PYTHONHOME', 'PYTHONNOUSERSITE',
                'PYTHONSAFEPATH', 'PYTHONSTARTUP', 'PYTHONEXECUTABLE',
                'PYTHONINSPECT', 'PYTHONOPTIMIZE', 'PYTHONUNBUFFERED',
                'PYTHONVERBOSE', 'PYTHONWARNINGS', 'VIRTUAL_ENV',
                '_OLD_VIRTUAL_PATH', 'PYTHONIOENCODING', 'PYTHONUTF8'
            ]
            for key in python_env_keys:
                if key in os.environ:
                    del os.environ[key]
            self._last_target_python = None
            self._venv_site_packages = None
            def check_and_switch():
                if os.path.exists(venv_python):
                    self._do_switch_to_venv(venv_python, venv_site)
                    if script and os.path.exists(script):
                        cache_data = self._load_project_cache()
                        if cache_data:
                            self._restore_from_project_cache(cache_data, script, self.app_name.text() or os.path.splitext(os.path.basename(script))[0])
                            #self.safe_log(f"✅ 从缓存恢复虚拟环境配置")
                        else:
                            self._last_analyzed_file = None
                            self._last_analyzed_time = 0
                            self.analyzed_modules = []
                            self.real_imports = []
                            self.extra_deps = []
                            self._analyze_used(script, auto_add=True)
                            if self.analyzed_modules:
                                self._save_project_cache((
                                    self.analyzed_modules,
                                    self.real_imports,
                                    self.extra_deps,
                                    getattr(self, 'uses_tkinter', False)
                                ))
                            #self.safe_log(f"✅ 已为虚拟环境生成新缓存")
                else:
                    self._create_venv_sync(venv_dir, venv_python)
            threading.Thread(target=check_and_switch, daemon=True).start()
        else:
            self.safe_log("🐍 已禁用虚拟环境")
            def disable_and_refresh():
                self._do_disable_venv()
                if script and os.path.exists(script):
                    cache_data = self._load_project_cache()
                    if cache_data:
                        self._restore_from_project_cache(cache_data, script, self.app_name.text() or os.path.splitext(os.path.basename(script))[0])
                        #self.safe_log(f"✅ 从缓存恢复主环境配置")
                    else:
                        self._last_analyzed_file = None
                        self._last_analyzed_time = 0
                        self.analyzed_modules = []
                        self.real_imports = []
                        self.extra_deps = []
                        self._analyze_used(script, auto_add=True)
                        if self.analyzed_modules:
                            self._save_project_cache((
                                self.analyzed_modules,
                                self.real_imports,
                                self.extra_deps,
                                getattr(self, 'uses_tkinter', False)
                            ))
                        #self.safe_log(f"✅ 已为主环境生成新缓存")
            QTimer.singleShot(10, disable_and_refresh)
            self.venv_pkg_count_label.setText("")
            if 'VIRTUAL_ENV' in os.environ:
                del os.environ['VIRTUAL_ENV']

    def _do_switch_to_venv(self, venv_python, venv_site):
        """切换到虚拟环境"""
        if not venv_python or not os.path.exists(venv_python):
            self.safe_log("❌ 虚拟环境Python不存在")
            return
        display_path = self._format_path(venv_python)
        idx = self.python_path.findText(display_path)
        if idx < 0:
            self.python_path.addItem(display_path)
            idx = self.python_path.findText(display_path)
        if idx >= 0:
            self.python_path.setCurrentIndex(idx)
        self._last_target_python = venv_python
        self._venv_site_packages = venv_site if os.path.exists(venv_site) else None
        # 更新版本
        try:
            result = self._run_hidden([venv_python, '--version'], capture_output=True, text=True, timeout=2)
            ver = result.stdout.strip() or result.stderr.strip()
            if ver:
                self.python_version.setText(ver)
                self.status_python.setText(f"🐍 {ver}")
        except:
            pass
        self._on_python_selected()
        # 安装依赖
        script = self.input_file.text()
        if script and os.path.exists(script):
            QTimer.singleShot(100, lambda: self._install_missing_deps_with_progress(venv_python, script))
        self._update_venv_pkg_count()
        # 保存虚拟环境状态到全局缓存
        try:
            cache = load_cache()
            cache['venv_enabled'] = True
            cache['venv_python'] = venv_python
            cache['venv_site'] = venv_site
            save_cache(cache)
            #self.safe_log("💾 虚拟环境状态已缓存")
        except Exception as e:
            pass
            #self.safe_log(f"⚠️ 缓存虚拟环境状态失败: {e}")

    def _check_venv_valid(self, venv_dir):
        """检查虚拟环境是否完整有效"""
        if sys.platform == 'win32':
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")
        if not os.path.exists(venv_python):
            return False
        try:
            result = subprocess.run(
                [venv_python, '-c', 'print("ok")'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and 'ok' in result.stdout:
                return True
        except:
            pass
        return False

    def _do_enable_venv(self):
        exe_dir = get_exe_directory()
        venv_dir = os.path.join(exe_dir, "common_venv")
        if sys.platform == 'win32':
            venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            venv_python = os.path.join(venv_dir, "bin", "python")
        if not os.path.exists(venv_python):
            self.safe_log("🔧 正在创建虚拟环境...")
            self.status_label.setText("创建虚拟环境...")
            threading.Thread(
                target=self._create_venv_sync,
                args=(venv_dir, venv_python),
                daemon=True
            ).start()
            return
        # ===== 切换到虚拟环境Python =====
        display_path = self._format_path(venv_python)
        if self.python_path.findText(display_path) < 0:
            self.python_path.addItem(display_path)
        self.python_path.setCurrentText(display_path)
        if os.path.exists(venv_python):
            # ===== 检测并复制 tk 相关文件 =====
            need_tk = False
            if 'tk' in self.hidden_imports_list or 'tkinter' in self.hidden_imports_list:
                need_tk = True
            if hasattr(self, 'analyzed_modules'):
                if 'tk' in self.analyzed_modules or 'tkinter' in self.analyzed_modules:
                    need_tk = True
            if need_tk:
                system_python = self.python_path.currentText()
                if system_python and os.path.exists(system_python):
                    venv_dir = os.path.dirname(os.path.dirname(venv_python))
                    threading.Thread(
                        target=self._copy_tk_to_venv,
                        args=(system_python, venv_dir),
                        daemon=True
                    ).start()
        # 手动更新版本显示
        try:
            result = self._run_hidden([venv_python, '--version'], capture_output=True, text=True, timeout=2)
            ver = result.stdout.strip() or result.stderr.strip()
            if ver:
                self.python_version.setText(ver)
                self.status_python.setText(f"🐍 {ver}")
        except:
            pass
        script = self.input_file.text()
        if script and os.path.exists(script):
            QTimer.singleShot(100, lambda: self._install_missing_deps_with_progress(venv_python, script))

    def _do_disable_venv(self):
        """实际禁用虚拟环境（延迟执行）"""
        self._restore_previous_python()
        # 清除虚拟环境状态
        try:
            cache = load_cache()
            cache['venv_enabled'] = False
            save_cache(cache)
            self.safe_log("💾 虚拟环境状态已清除")
        except Exception as e:
            self.safe_log(f"⚠️ 清除虚拟环境状态失败: {e}")

    def _restore_previous_python(self):
        """取消虚拟时，切换到下拉列表中第一个非虚拟环境的Python"""
        for i in range(self.python_path.count()):
            path = self.python_path.itemText(i)
            if path and 'common_venv' not in path.lower():
                self.python_path.setCurrentIndex(i)
                try:
                    result = self._run_hidden([path, '--version'], capture_output=True, text=True, timeout=2)
                    ver = result.stdout.strip() or result.stderr.strip()
                    if ver:
                        self.python_version.setText(ver)
                        self.status_python.setText(f"🐍 {ver}")
                except:
                    pass
                self.safe_log(f"🐍 已切换回: {path}")
                return
        if self.python_path.count() > 0:
            self.python_path.setCurrentIndex(0)
            self.safe_log("🐍 已切换到第一个Python")

    def _restore_system_python(self):
        """恢复使用系统Python（关闭虚拟环境时调用）"""
        try:
            # 获取系统Python路径
            system_python = sys.executable
            # 如果是打包模式，查找系统Python
            if getattr(sys, 'frozen', False):
                system_python = self._find_system_python() or sys.executable
            # 如果当前选中的是虚拟环境Python，切换到系统Python
            current_py = self.python_path.currentText()
            venv_dir = os.path.join(get_exe_directory(), "common_venv")
            if sys.platform == 'win32':
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")
            # 如果当前选中的是虚拟环境Python，切换到系统Python
            if current_py and current_py == self._format_path(venv_python):
                # 查找系统Python在列表中的位置
                display_path = self._format_path(system_python)
                idx = self.python_path.findText(display_path)
                if idx >= 0:
                    self.python_path.setCurrentIndex(idx)
                else:
                    # 如果不在列表中，添加并选中
                    self.python_path.addItem(display_path)
                    self.python_path.setCurrentText(display_path)
                # 更新版本信息
                try:
                    result = self._run_hidden(
                        [system_python, '--version'],
                        capture_output=True, text=True,
                        startupinfo=get_startupinfo()
                    )
                    ver = result.stdout.strip() or result.stderr.strip()
                    if ver:
                        self.python_version.setText(ver)
                        self.status_python.setText(f"🐍 {ver}")
                        self.safe_log(f"🐍 已切换回系统Python: {ver}")
                except:
                    pass
            else:
                if current_py and os.path.exists(current_py):
                    try:
                        result = self._run_hidden(
                            [current_py, '--version'],
                            capture_output=True, text=True,
                            startupinfo=get_startupinfo()
                        )
                        ver = result.stdout.strip() or result.stderr.strip()
                        if ver:
                            self.python_version.setText(ver)
                            self.status_python.setText(f"🐍 {ver}")
                    except:
                        pass
        except Exception as e:
            self.safe_log(f"⚠️ 恢复系统Python失败: {e}")

    def _auto_create_venv_for_script_async(self):
        """异步调用自动创建虚拟环境"""
        script = self.input_file.text()
        if script and os.path.exists(script):
            self._auto_create_venv_for_script(script)

    def _manage_venv(self):
        """管理虚拟环境"""
        script = self.input_file.text()
        if not script or not os.path.exists(script):
            QMessageBox.warning(self, "提示", "请先选择Python脚本")
            return
        exe_dir = get_exe_directory()
        venv_dir = os.path.join(exe_dir, "common_venv")
        self.stop_venv = False
        self.status_start("虚拟环境", color="blue")
        threading.Thread(
            target=self._do_manage_venv_common,
            args=(venv_dir, script),
            daemon=True
        ).start()

    def _do_manage_venv_common(self, venv_dir, script):
        """在后台线程管理公用虚拟环境"""
        try:
            # 获取系统Python
            py = self._find_system_python()
            if not py or not os.path.exists(py):
                py = sys.executable
            if not py or not os.path.exists(py):
                self.safe_log("❌ 未找到系统 Python")
                self.status_finish("失败")
                return
            self.safe_log(f"📦 管理公用虚拟环境: {self._format_path(venv_dir)}")
            self.safe_log(f"🔧 使用当前使用 Python: {py}")
            # ===== 检查虚拟环境是否已存在 =====
            if sys.platform == 'win32':
                venv_py = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_py = os.path.join(venv_dir, "bin", "python")
            if os.path.exists(venv_py):
                # ===== 虚拟环境已存在，切换并补充依赖 =====
                self.safe_log("✅ 虚拟环境已存在，检查依赖...")
                QTimer.singleShot(0, lambda: self._switch_to_venv_python(venv_py, "common_venv"))
                # 直接调用 _analyze_deps 分析并安装缺失依赖
                self._analyze_deps()
                self.safe_log(f"✅ 公用虚拟环境就绪: {self._format_path(venv_dir)}")
                self.status_finish("就绪")
                return
            # ===== 虚拟环境不存在，创建 =====
            self.status_set_target(20, "创建虚拟环境")
            self.safe_log("🔧 创建虚拟环境...")
            result = self._run_hidden(
                [py, "-m", "venv", venv_dir],
                capture_output=True, text=True,
                startupinfo=get_startupinfo()
            )
            if result.returncode != 0:
                self.safe_log(f"❌ 创建失败: {result.stderr}")
                self.status_finish("失败")
                return
            self.safe_log("✅ 虚拟环境创建成功")
            self.status_set_target(30, "创建完成")
            if not os.path.exists(venv_py):
                self.safe_log(f"❌ 虚拟环境Python不存在: {venv_py}")
                self.status_finish("失败")
                return
            # ===== 切换到虚拟环境Python =====
            QTimer.singleShot(0, lambda: self._switch_to_venv_python(venv_py, "common_venv"))
            # ===== 安装依赖 =====
            self.safe_log("📦 安装依赖...")
            self._analyze_deps()
            # ===== 安装打包器 =====
            self._install_packers_in_venv(venv_py)
            self.status_set_target(100, "完成")
            self.safe_log(f"✅ 公用虚拟环境就绪: {self._format_path(venv_dir)}")
            self.status_finish("就绪")
        except Exception as e:
            self.safe_log(f"❌ 管理失败: {e}")
            self.status_finish("失败")

    def _do_manage_venv(self):
        """管理虚拟环境"""
        try:
            venv_dir = os.path.join(self.current_dir, "common_venv")
            script = self.input_file.text()
            if not script or not os.path.exists(script):
                return
            self._do_manage_venv_common(venv_dir, script)
        except Exception as e:
            self.safe_log(f"❌ 管理失败: {e}")
            self._venv_finish(False)

    def _on_venv_progress(self, value, text):
        """主线程中更新UI - 彩色版"""
        self.status_progress.setValue(value)
        self.status_pct.setText(f"{value}%")
        if text:
            self.status_label.setText(text)
        if value < 30:
            color = "#f44336"
        elif value < 60:
            color = "#ff9800"
        elif value < 90:
            color = "#2196f3"
        else:
            color = "#4caf50"
        self.status_progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: #e0e0e0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)

    def _on_venv_finish(self, success):
        """虚拟环境完成（主线程）"""
        if self._venv_finishing:
            return
        self._venv_finishing = True
        try:
            self.progress_container.setVisible(False)
            if not success:
                self.venv_mode.setChecked(False)
                self.use_venv = False
            else:
                self._refresh_temp_path()
            self._hide_venv_progress()
        finally:
            self._venv_finishing = False

    def _hide_venv_progress(self):
        """隐藏虚拟环境进度条"""
        self.status_progress.setVisible(False)
        self.status_pct.setVisible(False)
        self.status_label.setText("就绪")
        self.status_progress.setValue(0)

    def _venv_log(self, msg):
        """虚拟环境日志"""
        self.venv_log_signal.emit(msg)

    def _venv_progress(self, value, text):
        """子线程中调用"""
        self.venv_progress_signal.emit(value, text)
        if value >= 100:
            QTimer.singleShot(500, lambda: self._venv_finish(True))

    def _on_venv_finish(self, success):
        """虚拟环境完成（主线程）"""
        self.status_progress.setVisible(False)
        self.status_pct.setVisible(False)
        self.status_label.setText("就绪")
        self.status_progress.setValue(0)
        self.progress_container.setVisible(False)
        if success:
            self.safe_log("✅ 虚拟环境创建完成")
        else:
            self.safe_log("❌ 虚拟环境创建失败")

    def _rename_and_delete(self, path):
        """重命名后异步删除"""
        if not os.path.exists(path):
            return False
        try:
            import uuid
            temp_name = f"{path}_deleting_{uuid.uuid4().hex[:8]}"
            os.rename(path, temp_name)
            threading.Thread(target=lambda: shutil.rmtree(temp_name, ignore_errors=True), daemon=True).start()
            return True
        except Exception:
            shutil.rmtree(path, ignore_errors=True)
            return False
    # ==================== 代码注入 ====================

    def _open_inject_selector(self):
        dialog = InjectSelectorDialog(self, self.inject_selected)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.inject_selected = dialog.get_selected()
            self.safe_log(f"💉 注入选项: {self.inject_selected}")
    # ==================== 版本信息 ====================

    def _open_version_dialog(self):
        """打开版本信息设置弹窗"""
        current_name = self.app_name.text() or "我的应用程序"
        dialog = VersionInfoDialog(self, self.version_info, current_name, self.output_dir.text())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.version_info = dialog.get_result()
            self.safe_log(f"📋 版本信息已更新")
    # ==================== 钩子管理 ====================

    def _open_hook_manager(self):
        dialog = HookManagerDialog(self)
        dialog.exec()

    def _edit_spec_file(self):
        script = self.input_file.text()
        if not script:
            show_msg(self, "警告", "请先选择Python脚本",1)
            return
        spec_file = os.path.splitext(script)[0] + '.spec'
        # 如果spec不存在，先提示生成
        if not os.path.exists(spec_file):
            show_msg(self, "信息", f"spec文件不存在: {spec_file}\\n\\n先运行一次打包生成spec文件",1)
            return
        # 自动更新spec文件中的hiddenimports
        try:
            with open(spec_file, 'r', encoding='utf-8-sig') as f:
                spec_content = f.read()
            # 获取当前所有hidden imports（用户手动添加的）
            all_hidden = self.hidden_imports_list.copy()
            # 重新分析脚本依赖，确保没有遗漏
            imports = self._parse_imports(script)
            for mod in imports:
                if mod not in STANDARD_LIBS and mod not in all_hidden:
                    all_hidden.append(mod)
            if all_hidden:
                hidden_str = repr(all_hidden)
                # 替换或添加 hiddenimports
                if 'hiddenimports=' in spec_content:
                    spec_content = re.sub(
                        r'hiddenimports\\s*=\\s*\\[[^\\]]*\\]',
                        f'hiddenimports={hidden_str}',
                        spec_content
                    )
                else:
                    # 在 Analysis 调用中添加
                    spec_content = re.sub(
                        r'(a\\s*=\\s*Analysis\\()',
                        f'\\\\1\\n    hiddenimports={hidden_str},',
                        spec_content
                    )
                self.safe_log(f"📝 已更新spec文件，添加 {len(all_hidden)} 个hidden imports")
            # 确保pathex包含脚本目录
            script_dir = os.path.dirname(os.path.abspath(script))
            if f'pathex=[{repr(script_dir)}]' not in spec_content and f'pathex=[{repr(script_dir)}' not in spec_content:
                if 'pathex=' not in spec_content:
                    spec_content = re.sub(
                        r'(a\\s*=\\s*Analysis\\()',
                        f'\\\\1\\n    pathex=[{repr(script_dir)}],',
                        spec_content
                    )
            # 写回文件
            with open(spec_file, 'w', encoding='utf-8-sig') as f:
                f.write(spec_content)
            self.safe_log(f"✅ Spec文件已更新: {spec_file}")
        except Exception as e:
            self.safe_log(f"❌ 更新spec文件失败: {e}")
        # 打开文件供用户编辑
        if sys.platform == 'win32':
            os.startfile(spec_file)
        else:
            self._run_hidden(['xdg-open', spec_file])

    def _inject_version_to_exe(self):
        """手动注入版本信息到已生成的 exe"""
        try:
            script = self.input_file.text()
            if not script:
                self.safe_log("❌ 请先选择脚本文件")
                return
            proj_name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
            proj_name = re.sub(r'[\\/:*?"<>|]', '_', proj_name)
            output_path = os.path.join(self.output_dir.text(), proj_name)
            version_file = os.path.join(output_path, 'version.txt')
            if not os.path.exists(version_file):
                self.safe_log("❌ 版本文件不存在: version.txt")
                return
            exe_path = None
            possible_paths = [
                os.path.join(output_path, f'{proj_name}.exe'),
                os.path.join(output_path, proj_name, f'{proj_name}.exe'),
                os.path.join(self.output_dir.text(), f'{proj_name}.exe'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    exe_path = path
                    break
            if not exe_path:
                self.safe_log("❌ 未找到生成的 exe 文件")
                return
            # 执行版本注入
            self.safe_log(f"📋 注入版本: {os.path.basename(exe_path)}")
            # 直接用 pyi-set_version
            cmd = f'pyi-set_version "{version_file}" "{exe_path}"'
            self.safe_log(f"> {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            if result.returncode == 0:
                self.safe_log(f"✅ 版本注入成功!")
                QMessageBox.information(self, "完成", f"版本信息已注入:\n{exe_path}")
            else:
                self.safe_log(f"❌ 注入失败: {result.stderr}")
                QMessageBox.warning(self, "失败", f"版本注入失败:\n{result.stderr}")
        except Exception as e:
            self.safe_log(f"❌ 异常: {e}")
            QMessageBox.critical(self, "错误", str(e))

    def _normalize_exe_path(self, path):
        """统一 exe 文件路径后缀为小写"""
        if not path:
            return path
        import re
        return re.sub(r'\.exe$', '.exe', path, flags=re.IGNORECASE)

    def _get_empty_lines_to_delete(self, content, lines):
        """获取需要删除的空行位置（优化版）"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return set()
        delete_empty_lines = set()
        # ===== 缓存空行判断 =====
        empty_cache = {}

        def is_empty(idx):
            if idx not in empty_cache:
                empty_cache[idx] = idx < len(lines) and not lines[idx].strip()
            return empty_cache[idx]

        def is_if_main(node):
            if not isinstance(node, ast.If):
                return False
            if isinstance(node.test, ast.Compare):
                if (isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'):
                    return True
            return False

        def collect_deletions_for_items(items, is_module=False):
            """检查一个语句列表，返回需要删除的空行"""
            if not items or len(items) < 2:
                return
            sorted_items = sorted(items, key=lambda x: x.lineno)
            for i in range(len(sorted_items) - 1):
                prev_stmt = sorted_items[i]
                next_stmt = sorted_items[i + 1]
                prev_end = getattr(prev_stmt, 'end_lineno', None) or prev_stmt.lineno
                next_start = next_stmt.lineno
                empty_lines = []
                for line_idx in range(prev_end, next_start - 1):
                    if line_idx < len(lines):
                        stripped = lines[line_idx].strip()
                        if stripped.startswith('#'):
                            continue
                        if is_empty(line_idx):
                            empty_lines.append(line_idx + 1)
                if not empty_lines:
                    continue
                # 判断规则（与 _check_body_empty_lines 保持一致）
                if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    # 嵌套函数/类定义前面：保留1个空行，删除多余的
                    if len(empty_lines) > 1:
                        for line_no in empty_lines[:-1]:
                            delete_empty_lines.add(line_no)
                elif is_if_main(next_stmt):
                    if len(empty_lines) > 1:
                        for line_no in empty_lines[:-1]:
                            delete_empty_lines.add(line_no)
                else:
                    # 普通语句之间：删除所有空行
                    for line_no in empty_lines:
                        delete_empty_lines.add(line_no)

        def collect_deletions(node, is_module=False):
            """收集一个节点内部需要删除的空行"""
            body = getattr(node, 'body', None)
            if not body:
                return
            if isinstance(node, ast.Try):
                all_items = list(body)
                if hasattr(node, 'handlers') and node.handlers:
                    all_items.extend(node.handlers)
                if hasattr(node, 'orelse') and node.orelse:
                    all_items.extend(node.orelse)
                if hasattr(node, 'finalbody') and node.finalbody:
                    all_items.extend(node.finalbody)
                collect_deletions_for_items(all_items, is_module)
            else:
                collect_deletions_for_items(body, is_module)
        # 遍历所有节点收集空行
        for node in ast.walk(tree):
            if isinstance(node, ast.Module):
                collect_deletions(node, is_module=True)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                collect_deletions(node, is_module=False)
            elif isinstance(node, ast.ClassDef):
                collect_deletions(node, is_module=False)
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                if not is_if_main(node):
                    collect_deletions(node, is_module=False)
            elif hasattr(node, 'handlers'):
                for handler in node.handlers:
                    handler_body = getattr(handler, 'body', None)
                    if handler_body:
                        collect_deletions_for_items(handler_body, is_module=False)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                body = getattr(node, 'body', None)
                if body and len(body) > 0:
                    def_line = node.lineno
                    first_stmt_line = body[0].lineno
                    for line_idx in range(def_line, first_stmt_line - 1):
                        if line_idx < len(lines) and is_empty(line_idx):
                            delete_empty_lines.add(line_idx + 1)
        return delete_empty_lines

    def _get_need_insert_lines(self, content, lines):
        """获取需要插入空行的位置（顶层特殊块之间缺少空行时）（优化版）"""
        insert_lines = set()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return insert_lines
        # ===== 缓存空行判断 =====
        empty_cache = {}

        def is_empty(idx):
            if idx not in empty_cache:
                empty_cache[idx] = idx < len(lines) and not lines[idx].strip()
            return empty_cache[idx]

        def collect_inserts(node):
            """收集顶层特殊块之间缺少空行的位置"""
            body = getattr(node, 'body', None)
            if not body or len(body) < 2:
                return
            for i in range(1, len(body)):
                prev_stmt = body[i - 1]
                next_stmt = body[i]
                prev_end = getattr(prev_stmt, 'end_lineno', None) or prev_stmt.lineno
                next_start = next_stmt.lineno
                # 检查是否有空行
                has_empty = False
                for line_idx in range(prev_end, next_start - 1):
                    if line_idx < len(lines):
                        stripped = lines[line_idx].strip()
                        if stripped.startswith('#'):
                            continue
                        if is_empty(line_idx):
                            has_empty = True
                            break
                # 判断 next_stmt 是否是特殊块（需要前面有空行）
                is_special = False
                if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    is_special = True
                elif self._is_if_main(next_stmt):
                    is_special = True
                # 如果是特殊块且前面没有空行，需要插入
                if is_special and not has_empty:
                    insert_lines.add(next_start)
        for node in ast.walk(tree):
            if isinstance(node, ast.Module):
                collect_inserts(node)
            elif isinstance(node, ast.ClassDef):
                body = getattr(node, 'body', None)
                if body and len(body) >= 2:
                    for i in range(1, len(body)):
                        prev_stmt = body[i - 1]
                        next_stmt = body[i]
                        prev_end = getattr(prev_stmt, 'end_lineno', None) or prev_stmt.lineno
                        next_start = next_stmt.lineno
                        has_empty = False
                        for line_idx in range(prev_end, next_start - 1):
                            if line_idx < len(lines):
                                stripped = lines[line_idx].strip()
                                if stripped.startswith('#'):
                                    continue
                                if is_empty(line_idx):
                                    has_empty = True
                                    break
                        if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not has_empty:
                                insert_lines.add(next_start)
        return insert_lines

    def _check_code_formatting(self, content, lines, file_path):
        """检查代码格式：顶层块之间空行 + 函数体内部空行（优化版）"""
        errors = []
        warnings = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return errors, warnings
        # ===== 缓存空行判断，避免重复计算 =====
        empty_cache = {}

        def is_empty(idx):
            if idx not in empty_cache:
                empty_cache[idx] = idx < len(lines) and not lines[idx].strip()
            return empty_cache[idx]

        def is_special_top_block(node):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                return True
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Compare):
                    if (isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__'):
                        return True
            return False

        def get_block_name(node):
            if isinstance(node, ast.FunctionDef):
                return f"函数 '{node.name}'"
            elif isinstance(node, ast.AsyncFunctionDef):
                return f"异步函数 '{node.name}'"
            elif isinstance(node, ast.ClassDef):
                return f"类 '{node.name}'"
            elif isinstance(node, ast.If):
                return "if __name__"
            return "未知块"

        def get_stmt_desc(stmt):
            if isinstance(stmt, ast.FunctionDef):
                return f"函数 '{stmt.name}'"
            elif isinstance(stmt, ast.AsyncFunctionDef):
                return f"异步函数 '{stmt.name}'"
            elif isinstance(stmt, ast.ClassDef):
                return f"类 '{stmt.name}'"
            elif isinstance(stmt, ast.ExceptHandler):
                return f"except {stmt.name}" if stmt.name else "except"
            elif isinstance(stmt, ast.Return):
                return "return 语句"
            elif isinstance(stmt, ast.Assign):
                return "赋值语句"
            elif isinstance(stmt, ast.Expr):
                return "表达式"
            elif isinstance(stmt, ast.If):
                return "if 语句"
            elif isinstance(stmt, ast.For):
                return "for 循环"
            elif isinstance(stmt, ast.While):
                return "while 循环"
            elif isinstance(stmt, ast.Import):
                return "import 语句"
            elif isinstance(stmt, ast.ImportFrom):
                return "from import 语句"
            elif isinstance(stmt, ast.Try):
                return "try 块"
            elif isinstance(stmt, ast.With):
                return "with 语句"
            return type(stmt).__name__

        def is_if_main(node):
            if not isinstance(node, ast.If):
                return False
            if isinstance(node.test, ast.Compare):
                if (isinstance(node.test.left, ast.Name) and node.test.left.id == '__name__'):
                    return True
            return False
        # ===== 检查顶层块之间的空行 =====
        top_blocks = []
        for node in tree.body:
            if is_special_top_block(node):
                end = getattr(node, 'end_lineno', None) or node.lineno
                top_blocks.append((node.lineno, end, node))
        for idx in range(len(top_blocks) - 1):
            curr_end = top_blocks[idx][1]
            next_start = top_blocks[idx + 1][0]
            next_node = top_blocks[idx + 1][2]
            empty_lines = []
            has_comment = False
            for line_idx in range(curr_end, next_start - 1):
                if line_idx >= len(lines):
                    break
                stripped = lines[line_idx].strip()
                if stripped.startswith('#'):
                    has_comment = True
                    continue
                if is_empty(line_idx):
                    empty_lines.append(line_idx + 1)
            curr_name = get_block_name(top_blocks[idx][2])
            next_name = get_block_name(next_node)
            if has_comment:
                if len(empty_lines) > 2:
                    errors.append((next_start, f"【顶层块之间】{next_name} 前有多余空行（与{curr_name}之间有注释，空行{len(empty_lines)}行，超过2行）"))
                continue
            if len(empty_lines) == 0:
                errors.append((next_start, f"【顶层块之间】{next_name} 前缺少空行（与{curr_name}之间应有1行空行）"))
            elif len(empty_lines) > 1:
                errors.append((empty_lines[0], f"【顶层块之间】{next_name} 前有 {len(empty_lines)} 个空行（与{curr_name}之间，应只有1行）"))
        # ===== 检查函数/类体内部（使用缓存，合并遍历） =====

        def check_body_items(items, block_name, block_type):
            if not items or len(items) < 2:
                return
            sorted_items = sorted(items, key=lambda x: x.lineno)
            for i in range(len(sorted_items) - 1):
                prev_stmt = sorted_items[i]
                next_stmt = sorted_items[i + 1]
                prev_end = getattr(prev_stmt, 'end_lineno', None) or prev_stmt.lineno
                next_start = next_stmt.lineno
                empty_lines = []
                for line_idx in range(prev_end, next_start - 1):
                    if line_idx < len(lines):
                        stripped = lines[line_idx].strip()
                        if stripped.startswith('#'):
                            continue
                        if is_empty(line_idx):
                            empty_lines.append(line_idx + 1)
                if not empty_lines:
                    continue
                next_desc = get_stmt_desc(next_stmt)
                prev_desc = get_stmt_desc(prev_stmt)
                if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if len(empty_lines) == 0:
                        errors.append((next_start, f"【{block_type}体内部】{block_type} '{block_name}' 内，{next_desc} 前缺少空行"))
                    elif len(empty_lines) > 1:
                        errors.append((empty_lines[0], f"【{block_type}体内部】{block_type} '{block_name}' 内，{next_desc} 前有 {len(empty_lines)} 个空行，应只有1个"))
                elif is_if_main(next_stmt):
                    if len(empty_lines) == 0:
                        errors.append((next_start, f"【{block_type}体内部】{block_type} '{block_name}' 内，if __name__ 前缺少空行"))
                    elif len(empty_lines) > 1:
                        errors.append((empty_lines[0], f"【{block_type}体内部】{block_type} '{block_name}' 内，if __name__ 前有 {len(empty_lines)} 个空行，应只有1个"))
                else:
                    if len(empty_lines) >= 1:
                        errors.append((empty_lines[0], f"【{block_type}体内部】{block_type} '{block_name}' 内，{prev_desc} -> {next_desc} 之间有多余空行 ({len(empty_lines)} 行)，应删除"))

        def check_body(node, block_name, block_type):
            body = getattr(node, 'body', None)
            if not body:
                return
            if isinstance(node, ast.Try):
                all_items = list(body)
                if hasattr(node, 'handlers') and node.handlers:
                    all_items.extend(node.handlers)
                if hasattr(node, 'orelse') and node.orelse:
                    all_items.extend(node.orelse)
                if hasattr(node, 'finalbody') and node.finalbody:
                    all_items.extend(node.finalbody)
                check_body_items(all_items, block_name, block_type)
            else:
                check_body_items(body, block_name, block_type)
        # 一次遍历所有节点，完成函数/类体检查
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                check_body(node, node.name, '函数')
            elif isinstance(node, ast.ClassDef):
                check_body(node, node.name, '类')
            elif isinstance(node, ast.If) and not is_if_main(node):
                check_body(node, f'if(行{node.lineno})', 'if块')
            elif isinstance(node, ast.For):
                check_body(node, f'for(行{node.lineno})', 'for块')
            elif isinstance(node, ast.While):
                check_body(node, f'while(行{node.lineno})', 'while块')
            elif isinstance(node, ast.With):
                check_body(node, f'with(行{node.lineno})', 'with块')
            elif isinstance(node, ast.Try):
                check_body(node, f'try(行{node.lineno})', 'try块')
            elif hasattr(node, 'handlers'):
                for handler in node.handlers:
                    handler_body = getattr(handler, 'body', None)
                    if handler_body:
                        check_body_items(handler_body, f'except(行{handler.lineno})', 'except块')
        return errors, warnings

    def _extract_block_name(self, stripped_line):
        """从行文本中提取函数/类名称"""
        if stripped_line.startswith('class '):
            # class MyClass(Base): -> MyClass
            name = stripped_line[6:].split('(')[0].split(':')[0].strip()
            return name
        elif stripped_line.startswith('def ') or stripped_line.startswith('async def '):
            # def my_func(args): -> my_func
            # async def my_func(args): -> my_func
            start = stripped_line.find('def ') + 4
            name = stripped_line[start:].split('(')[0].strip()
            return name
        elif stripped_line.startswith('if '):
            return '__main__'
        return 'unknown'

    def _check_body_empty_lines(self, tree, lines):
        """检查所有代码块内部的空行（递归AST）"""
        errors = []

        def is_if_main(node):
            if not isinstance(node, ast.If):
                return False
            if isinstance(node.test, ast.Compare):
                if (isinstance(node.test.left, ast.Name) and
                        node.test.left.id == '__name__'):
                    return True
            return False

        def get_stmt_desc(stmt):
            """获取语句描述（与 _get_stmt_desc 保持一致）"""
            if isinstance(stmt, ast.FunctionDef):
                return f"函数 '{stmt.name}'"
            elif isinstance(stmt, ast.AsyncFunctionDef):
                return f"异步函数 '{stmt.name}'"
            elif isinstance(stmt, ast.ClassDef):
                return f"类 '{stmt.name}'"
            elif isinstance(stmt, ast.ExceptHandler):
                if stmt.name:
                    return f"except {stmt.name}"
                return "except"
            elif isinstance(stmt, ast.Return):
                return "return 语句"
            elif isinstance(stmt, ast.Assign):
                return "赋值语句"
            elif isinstance(stmt, ast.Expr):
                return "表达式/注释"
            elif isinstance(stmt, ast.If):
                return "if 语句"
            elif isinstance(stmt, ast.For):
                return "for 循环"
            elif isinstance(stmt, ast.While):
                return "while 循环"
            elif isinstance(stmt, ast.Import):
                return "import 语句"
            elif isinstance(stmt, ast.ImportFrom):
                return "from import 语句"
            elif isinstance(stmt, ast.Try):
                return "try 块"
            elif isinstance(stmt, ast.With):
                return "with 语句"
            else:
                return type(stmt).__name__

        def check_body_items(items, block_name, block_type):
            """检查语句列表内部的空行（与 _get_empty_lines_to_delete 逻辑一致）"""
            if not items or len(items) < 2:
                return
            # 按行号排序
            sorted_items = sorted(items, key=lambda x: x.lineno)
            for i in range(len(sorted_items) - 1):
                prev_stmt = sorted_items[i]
                next_stmt = sorted_items[i + 1]
                # 获取结束行号：优先用 end_lineno，否则用 lineno
                prev_end = getattr(prev_stmt, 'end_lineno', None)
                if prev_end is None:
                    prev_end = prev_stmt.lineno
                next_start = next_stmt.lineno
                empty_lines = []
                for line_idx in range(prev_end, next_start - 1):
                    if line_idx < len(lines):
                        stripped = lines[line_idx].strip()
                        if stripped.startswith('#'):
                            continue
                        if self._is_really_empty(lines[line_idx]):
                            empty_lines.append(line_idx + 1)
                if not empty_lines:
                    continue
                next_desc = get_stmt_desc(next_stmt)
                prev_desc = get_stmt_desc(prev_stmt)
                # 判断规则（与 _get_empty_lines_to_delete 完全一致）
                if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if len(empty_lines) == 0:
                        errors.append((next_start,
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，{next_desc} 前缺少空行"))
                    elif len(empty_lines) > 1:
                        errors.append((empty_lines[0],
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，{next_desc} 前有 {len(empty_lines)} 个空行，应只有1个"))
                elif is_if_main(next_stmt):
                    if len(empty_lines) == 0:
                        errors.append((next_start,
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，if __name__ 前缺少空行"))
                    elif len(empty_lines) > 1:
                        errors.append((empty_lines[0],
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，if __name__ 前有 {len(empty_lines)} 个空行，应只有1个"))
                else:
                    # 普通语句之间：不能有空行
                    if len(empty_lines) == 1:
                        errors.append((empty_lines[0],
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，{prev_desc} -> {next_desc} 之间有多余空行 (1 行)，应删除"))
                    else:
                        errors.append((empty_lines[0],
                                       f"【{block_type}体内部】{block_type} '{block_name}' 内，{prev_desc} -> {next_desc} 之间有 {len(empty_lines)} 个空行（第{empty_lines[0]}-{empty_lines[-1]}行），应删除"))

        def check_body(node, block_name, block_type):
            """检查一个节点的 body（与 _get_empty_lines_to_delete 的 collect_deletions 逻辑一致）"""
            body = getattr(node, 'body', None)
            if not body:
                return
            # 如果是 Try 节点，把 body 和 handlers 合并（与修复逻辑一致）
            if isinstance(node, ast.Try):
                all_items = list(body)
                if hasattr(node, 'handlers') and node.handlers:
                    all_items.extend(node.handlers)
                if hasattr(node, 'orelse') and node.orelse:
                    all_items.extend(node.orelse)
                if hasattr(node, 'finalbody') and node.finalbody:
                    all_items.extend(node.finalbody)
                check_body_items(all_items, block_name, block_type)
            else:
                check_body_items(body, block_name, block_type)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                check_body(node, node.name, '函数')
            elif isinstance(node, ast.ClassDef):
                check_body(node, node.name, '类')
            elif isinstance(node, ast.If) and not is_if_main(node):
                check_body(node, f'if(行{node.lineno})', 'if块')
            elif isinstance(node, ast.For):
                check_body(node, f'for(行{node.lineno})', 'for块')
            elif isinstance(node, ast.While):
                check_body(node, f'while(行{node.lineno})', 'while块')
            elif isinstance(node, ast.With):
                check_body(node, f'with(行{node.lineno})', 'with块')
            elif isinstance(node, ast.Try):
                check_body(node, f'try(行{node.lineno})', 'try块')
            elif hasattr(node, 'handlers'):
                for handler in node.handlers:
                    handler_body = getattr(handler, 'body', None)
                    if handler_body:
                        check_body_items(handler_body, f'except(行{handler.lineno})', 'except块')
        return errors

    def _get_stmt_desc(self, stmt):
        """获取AST语句的描述"""
        if isinstance(stmt, ast.FunctionDef):
            return f"函数 '{stmt.name}'"
        elif isinstance(stmt, ast.AsyncFunctionDef):
            return f"异步函数 '{stmt.name}'"
        elif isinstance(stmt, ast.ClassDef):
            return f"类 '{stmt.name}'"
        elif isinstance(stmt, ast.Return):
            return "return 语句"
        elif isinstance(stmt, ast.Assign):
            return "赋值语句"
        elif isinstance(stmt, ast.Expr):
            return "表达式/注释"
        elif isinstance(stmt, ast.If):
            return "if 语句"
        elif isinstance(stmt, ast.For):
            return "for 循环"
        elif isinstance(stmt, ast.While):
            return "while 循环"
        elif isinstance(stmt, ast.Import):
            return "import 语句"
        elif isinstance(stmt, ast.ImportFrom):
            return "from import 语句"
        elif isinstance(stmt, ast.Try):
            return "try 块"
        elif isinstance(stmt, ast.With):
            return "with 语句"
        else:
            return type(stmt).__name__

    def _get_real_special_lines(self, content):
        """用AST获取真正的特殊块行号集合"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return set()
        real_lines = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                real_lines.add(node.lineno)
            elif isinstance(node, ast.If):
                if self._is_if_main(node):
                    real_lines.add(node.lineno)
        return real_lines

    def _is_if_main(self, node):
        """检查是否是 if __name__ == '__main__':"""
        if not isinstance(node, ast.If):
            return False
        if isinstance(node.test, ast.Compare):
            if (isinstance(node.test.left, ast.Name) and
                    node.test.left.id == '__name__'):
                return True
        return False

    def _is_really_empty(self, line):
        """检查一行是否只包含空白/隐藏字符"""
        if not line:
            return True
        stripped = line.strip()
        if not stripped:
            return True
        for char in stripped:
            if char not in '\u200B\u200C\u200D\uFEFF':
                return False
        return True

    def _auto_fix_formatting(self, file_path):
        """自动修复格式问题"""
        self._auto_fix_indentation(file_path)
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            original_content = f.read()
            lines = original_content.split('\n')
        original_count = len(lines)
        changes = []
        # 获取需要删除的空行
        delete_empty_lines = self._get_empty_lines_to_delete(original_content, lines)
        # 获取需要插入空行的位置
        need_insert_lines = self._get_need_insert_lines(original_content, lines)
        result = []
        for i, line in enumerate(lines):
            line_no = i + 1
            stripped = line.strip()
            # 删除多余空行
            if self._is_really_empty(line) and line_no in delete_empty_lines:
                changes.append(f"删除第{line_no}行空行")
                continue
            # 插入缺少的空行（在特殊块前面插入）
            if line_no in need_insert_lines and result and result[-1] != '':
                result.append('')
                changes.append(f"在第{line_no}行前插入空行")
            result.append(line.rstrip('\n'))
        # Tab转空格
        result = [line.replace('\t', '    ') for line in result]
        new_content = '\n'.join(result)
        new_count = len(result)
        self._backup_file(file_path)
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write(new_content)
        self.safe_log(f"   ✅ 已修复: {original_count} → {new_count}")
        return original_content, new_content, changes

    def _preview_fix_changes(self, file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            lines = content.split('\n')
        original_count = len(lines)
        changes = []
        delete_empty_lines = self._get_empty_lines_to_delete(content, lines)
        need_empty_before = set()
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Module):
                    for i in range(1, len(node.body)):
                        next_stmt = node.body[i]
                        if isinstance(next_stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            need_empty_before.add(next_stmt.lineno)
                        elif self._is_if_main(next_stmt):
                            need_empty_before.add(next_stmt.lineno)
        except SyntaxError:
            pass
        result = []
        for i, line in enumerate(lines):
            line_no = i + 1
            stripped = line.strip()
            if self._is_really_empty(line) and line_no in delete_empty_lines:
                changes.append(f"第{line_no}行: 删除多余空行")
                continue
            is_special = False
            # 按优先级判断特殊块
            if stripped.startswith('if __name__'):
                is_special = True
            elif stripped.startswith('def main') or stripped.startswith('async def main'):
                is_special = True
            elif stripped.startswith('class '):
                is_special = True
            elif stripped.startswith('def ') or stripped.startswith('async def '):
                is_special = True
            if is_special and line_no in need_empty_before and result and result[-1] != '':
                result.append('')
                changes.append(f"在函数/类前插入空行")
            result.append(line.rstrip('\n'))
        new_count = len(result)
        return changes, result

    def _auto_fix_indentation(self, file_path):
        """修复缩进：Tab转空格，保持缩进级别不变"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        new_lines = []
        changes = []
        for i, line in enumerate(lines):
            # 计算原缩进级别（按Tab=4空格）
            indent_spaces = 0
            for char in line:
                if char == ' ':
                    indent_spaces += 1
                elif char == '\t':
                    indent_spaces += 4
                else:
                    break
            # 计算缩进级别（多少级）
            level = indent_spaces // 4
            # 新缩进 = 级别 * 4
            new_indent = level * 4
            # 只有缩进不是4的倍数时才记录变化
            if indent_spaces != new_indent:
                changes.append(f"第{i + 1}行: 缩进 {indent_spaces} → {new_indent}")
            # 重新构建行
            new_line = ' ' * new_indent + line.lstrip()
            new_lines.append(new_line.rstrip('\n'))
        if not changes:
            return False
        self._backup_file(file_path)
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(new_lines))
        self.safe_log(f"   🔧 已修复缩进: {len(changes)}处")
        return True

    def _backup_file(self, file_path):
        """备份文件"""
        import shutil
        backup_path = f"{os.path.splitext(file_path)[0]}.bak.py"
        shutil.copy2(file_path, backup_path)
        self.safe_log(f"📦 已备份: {os.path.basename(backup_path)}")
        return backup_path

    def _restore_backup(self, file_path=None):
        """从备份恢复文件"""
        import shutil
        import os
        from PyQt6.QtWidgets import QMessageBox
        if file_path is None:
            file_path = self.input_file.text()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "提示", "请先选择要恢复的文件")
            return False
        backup_path = f"{os.path.splitext(file_path)[0]}.bak.py"
        if not os.path.exists(backup_path):
            QMessageBox.warning(self, "提示", f"没有找到备份文件:\n{backup_path}")
            return False
        try:
            shutil.copy2(backup_path, file_path)
            self.safe_log(f"✅ 已从备份恢复: {os.path.basename(backup_path)}")
            show_msg(self, "成功", "文件已恢复，请重新加载查看",1)
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"恢复失败: {e}")
            return False

    def _get_ast_special_blocks(self, content):
        """用AST获取所有真正的特殊块，按父节点分组"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return {}
        blocks = []
        class Visitor(ast.NodeVisitor):
            def __init__(self):
                self.parent_id = id(tree)

            def visit_FunctionDef(self, node):
                end = getattr(node, 'end_lineno', node.lineno)
                blocks.append((node.lineno, '函数', end, node.name, self.parent_id))
                old = self.parent_id
                self.parent_id = id(node)
                self.generic_visit(node)
                self.parent_id = old

            def visit_AsyncFunctionDef(self, node):
                end = getattr(node, 'end_lineno', node.lineno)
                blocks.append((node.lineno, '异步函数', end, node.name, self.parent_id))
                old = self.parent_id
                self.parent_id = id(node)
                self.generic_visit(node)
                self.parent_id = old

            def visit_ClassDef(self, node):
                end = getattr(node, 'end_lineno', node.lineno)
                blocks.append((node.lineno, '类', end, node.name, self.parent_id))
                old = self.parent_id
                self.parent_id = id(node)
                self.generic_visit(node)
                self.parent_id = old

            def visit_If(self, node):
                is_main = False
                if isinstance(node.test, ast.Compare):
                    if (isinstance(node.test.left, ast.Name) and
                            node.test.left.id == '__name__'):
                        is_main = True
                if is_main:
                    end = getattr(node, 'end_lineno', node.lineno)
                    blocks.append((node.lineno, 'if块', end, '__main__', self.parent_id))
                self.generic_visit(node)
        Visitor().visit(tree)
        from collections import defaultdict
        groups = defaultdict(list)
        for lineno, typ, end, name, parent_id in blocks:
            groups[parent_id].append((lineno, typ, end, name))
        for parent_id in groups:
            groups[parent_id].sort(key=lambda x: x[0])
        return groups

    def _reorganize_class_functions(self, file_path):
        """将类中的函数按关键词分组排列特殊关键词映射：pack 和 package 视为同一类"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            # ===== 特殊关键词映射（同义词归为一类） =====
            KEYWORD_GROUPS = {
                'package': ['package', 'pack'],
                'build': ['build', 'compile'],
                'init': ['init', 'setup', 'initialize'],
                'config': ['config', 'configure'],
                'get': ['get', 'fetch', 'retrieve'],
                'set': ['set', 'update', 'modify'],
                'load': ['load', 'read', 'import'],
                'save': ['save', 'write', 'export'],
                'parse': ['parse', 'convert', 'transform'],
                'handle': ['handle', 'process'],
                'create': ['create', 'make', 'new'],
                'delete': ['delete', 'remove', 'del'],
                'find': ['find', 'search', 'lookup'],
                'start': ['start', 'begin', 'launch'],
                'stop': ['stop', 'end', 'terminate'],
                'run': ['run', 'execute', 'call'],
                'check': ['check', 'validate', 'verify'],
                'test': ['test', 'benchmark'],
                'error': ['error', 'exception', 'fail'],
                'log': ['log', 'debug', 'info'],
                'file': ['file', 'dir', 'path', 'folder'],
                'data': ['data', 'info', 'record'],
                'time': ['time', 'date', 'duration'],
                'main': ['main', 'app', 'gui', 'window'],
            }
            # 构建反向映射：关键词 -> 组名
            KEYWORD_TO_GROUP = {}
            for group_name, keywords in KEYWORD_GROUPS.items():
                for kw in keywords:
                    KEYWORD_TO_GROUP[kw] = group_name
            # 特殊组优先级（用于排序）
            GROUP_PRIORITY = {group: i for i, group in enumerate(KEYWORD_GROUPS.keys())}
            def extract_keywords(name):
                parts = name.strip('_').split('_')
                return [p for p in parts if p and not p.isdigit()]
            def get_group_name(keywords):
                for kw in keywords:
                    if kw in KEYWORD_TO_GROUP:
                        return KEYWORD_TO_GROUP[kw]
                return None
            def find_class_functions(lines, class_start, class_indent):
                functions = []
                i = class_start + 1
                func_start = None
                func_name = None
                func_indent = None
                while i < len(lines):
                    line = lines[i]
                    if not line.strip():
                        i += 1
                        continue
                    indent = len(line) - len(line.lstrip())
                    if indent <= class_indent and line.strip():
                        break
                    stripped = line.lstrip()
                    if stripped.startswith('def ') or stripped.startswith('async def '):
                        if func_start is not None:
                            functions.append({
                                'name': func_name,
                                'start': func_start,
                                'end': i - 1,
                                'indent': func_indent
                            })
                        func_start = i
                        func_indent = indent
                        parts = stripped.split('(')[0].split()
                        func_name = parts[-1] if parts else ''
                    i += 1
                if func_start is not None:
                    functions.append({
                        'name': func_name,
                        'start': func_start,
                        'end': i - 1,
                        'indent': func_indent
                    })
                return functions
            def find_all_classes(lines):
                classes = []
                for i, line in enumerate(lines):
                    stripped = line.lstrip()
                    if stripped.startswith('class '):
                        indent = len(line) - len(stripped)
                        name = stripped.split('(')[0].split()[1] if ' ' in stripped else ''
                        classes.append({'start': i, 'name': name, 'indent': indent})
                return classes
            classes = find_all_classes(lines)
            if not classes:
                return True, "没有类需要整理"
            modified = False
            changes = []
            for cls in reversed(classes):
                funcs = find_class_functions(lines, cls['start'], cls['indent'])
                if len(funcs) <= 1:
                    continue
                # 提取每个函数的关键词和组名
                func_keywords = {}
                func_group = {}
                for f in funcs:
                    keywords = extract_keywords(f['name'])
                    func_keywords[f['name']] = keywords if keywords else [f['name']]
                    func_group[f['name']] = get_group_name(func_keywords[f['name']])
                # 分组：相同组名的归为一组
                groups = {}
                used = set()
                for f in funcs:
                    if f['name'] in used:
                        continue
                    group_name = func_group[f['name']]
                    if group_name is None:
                        keys1 = set(func_keywords[f['name']])
                        group = []
                        for f2 in funcs:
                            if f2['name'] in used:
                                continue
                            keys2 = set(func_keywords[f2['name']])
                            if keys1 & keys2:
                                group.append(f2)
                                used.add(f2['name'])
                        if group:
                            common_keys = keys1
                            for f2 in group:
                                common_keys &= set(func_keywords[f2['name']])
                            gname = max(common_keys, key=len) if common_keys else group[0]['name']
                            groups[gname] = group
                    else:
                        group = [f]
                        used.add(f['name'])
                        for f2 in funcs:
                            if f2['name'] in used:
                                continue
                            if func_group[f2['name']] == group_name:
                                group.append(f2)
                                used.add(f2['name'])
                        groups[group_name] = group
                # 处理剩余未分组的
                remaining = [f for f in funcs if f['name'] not in used]
                if remaining:
                    groups['_other'] = remaining
                # 每组内按函数名排序
                for gname in groups:
                    groups[gname].sort(key=lambda f: f['name'])
                # 按优先级排序组
                def get_group_order(gname):
                    if gname in GROUP_PRIORITY:
                        return GROUP_PRIORITY[gname]
                    elif gname == '_other':
                        return 9999
                    else:
                        return 5000
                sorted_funcs = []
                for gname in sorted(groups.keys(), key=get_group_order):
                    sorted_funcs.extend(groups[gname])
                original_order = [f['name'] for f in funcs]
                new_order = [f['name'] for f in sorted_funcs]
                if original_order == new_order:
                    continue
                # 重新构建类体
                prefix_lines = lines[cls['start'] + 1:funcs[0]['start']]
                new_lines = []
                new_lines.append(lines[cls['start']])
                new_lines.extend(prefix_lines)
                if prefix_lines and not prefix_lines[-1].strip():
                    new_lines.append('\n')
                for i, func in enumerate(sorted_funcs):
                    if i > 0:
                        new_lines.append('\n')
                    for j in range(func['start'], func['end'] + 1):
                        new_lines.append(lines[j])
                last_end = sorted_funcs[-1]['end'] if sorted_funcs else funcs[-1]['end']
                new_lines.extend(lines[last_end + 1:])
                cls_end = cls['start'] + 1
                while cls_end < len(lines):
                    if len(lines[cls_end]) - len(lines[cls_end].lstrip()) <= cls['indent'] and lines[cls_end].strip():
                        break
                    cls_end += 1
                lines = lines[:cls['start']] + new_lines + lines[cls_end:]
                modified = True
                changes.append(f"类 {cls['name']}: 函数按关键词分组排列")
                for gname, gfuncs in groups.items():
                    if gname in KEYWORD_GROUPS:
                        label = f"📦 {gname}"
                    elif gname == '_other':
                        label = f"📄 其他"
                    else:
                        label = f"🔹 {gname}"
                    changes.append(f"  {label}: {len(gfuncs)} 个函数")
            if not modified:
                return True, "无需修改，函数已按关键词分组排列"
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.writelines(lines)
            self.safe_log(f"✅ 已按关键词分组排列类内函数（缩进保留）")
            return True, "\n".join(changes)
        except Exception as e:
            import traceback
            error_msg = f"整理失败: {e}\n{traceback.format_exc()}"
            self.safe_log(error_msg)
            return False, error_msg

    def _check_syntax(self):
        """检查Python文件语法错误（自动识别文件/文件夹）"""
        try:
            self._clear_log()
            f = self.input_file.text()
            if not f or not os.path.exists(f):
                QMessageBox.warning(self, "提示", "请先选择Python文件或文件夹")
                return
            self.safe_log("=" * 60)
            self.safe_log("🔍 开始语法检查...")
            py_files = []
            if os.path.isdir(f):
                exclude_dirs = {"venv", "common_venv", "__pycache__", ".venv", "env", "dist", "build", "site-packages", "Lib", "lib"}
                for root, dirs, files in os.walk(f):
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                    for file in files:
                        if file.endswith(".py"):
                            py_files.append(os.path.join(root, file))
                self.safe_log(f"📁 文件夹模式，扫描到 {len(py_files)} 个Python文件")
            else:
                py_files = [f]
                self.safe_log(f"📄 单文件模式: {os.path.basename(f)}")
            if not py_files:
                self.safe_log("⚠️ 未找到任何Python文件")
                self.safe_log("=" * 60)
                QMessageBox.warning(self, "提示", "未找到任何Python文件")
                return
            errors = []
            warnings = []
            file_details = []
            all_imports = set()
            total_import_count = 0
            fixable_files = set()
            for py_file in py_files:
                line_count = 0
                func_count = 0
                class_count = 0
                file_import_count = 0
                has_format_issue = False
                try:
                    with open(py_file, 'r', encoding='utf-8-sig') as fp:
                        content = fp.read()
                        lines = content.split('\n')
                        line_count = len(lines)
                        # ===== 当前文件的空行缓存 =====
                        empty_cache = {}
                        def is_empty(idx):
                            if idx not in empty_cache:
                                empty_cache[idx] = idx < len(lines) and not lines[idx].strip()
                            return empty_cache[idx]
                        # ===== 1. 混合缩进检查 =====
                        mixed_lines = []
                        for line_num, line in enumerate(lines, 1):
                            if line.strip():
                                stripped = line.lstrip()
                                if stripped:
                                    whitespace = line[:len(line) - len(stripped)]
                                    if '\t' in whitespace and ' ' in whitespace:
                                        mixed_lines.append(line_num)
                        if mixed_lines:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            for line_num in mixed_lines:
                                self.safe_log(f"❌ {rel_path}")
                                self.safe_log(f"   第 {line_num} 行: Tab和空格混用")
                                self.safe_log(f"   {lines[line_num - 1].rstrip()}")
                                self.safe_log("   💡 建议: 将制表符(Tab)统一替换为空格")
                                self.safe_log("")
                                errors.append(rel_path)
                                fixable_files.add(py_file)
                        # ===== 2. 格式检查（已优化） =====
                        format_errors, format_warnings = self._check_code_formatting(content, lines, py_file)
                        for line_num, error_msg in format_errors:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            self.safe_log(f"⚠️ {rel_path}")
                            self.safe_log(f"   第 {line_num} 行: {error_msg}")
                            self.safe_log("")
                            warnings.append(rel_path)
                            fixable_files.add(py_file)
                            has_format_issue = True
                        for line_num, warning_msg in format_warnings:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            self.safe_log(f"⚠️ {rel_path}")
                            self.safe_log(f"   第 {line_num} 行: {warning_msg}")
                            self.safe_log("")
                            warnings.append(rel_path)
                            fixable_files.add(py_file)
                        # ===== 3. AST解析 =====
                        try:
                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    func_count += 1
                                elif isinstance(node, ast.ClassDef):
                                    class_count += 1
                                elif isinstance(node, ast.Import):
                                    for alias in node.names:
                                        file_import_count += 1
                                        total_import_count += 1
                                        module_name = alias.name.split('.')[0].split('==')[0].split(' ')[0].strip()
                                        all_imports.add(module_name)
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        file_import_count += 1
                                        total_import_count += 1
                                        module_name = node.module.split('.')[0].split('==')[0].split(' ')[0].strip()
                                        all_imports.add(module_name)
                        except SyntaxError as e:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            self.safe_log(f"❌ {rel_path}")
                            self.safe_log(f"   第 {e.lineno} 行: {e.msg}")
                            if e.text:
                                self.safe_log(f"   {e.text.rstrip()}")
                                if e.offset:
                                    self.safe_log(f"   {' ' * (e.offset + 2)}^")
                            self.safe_log("")
                            errors.append(rel_path)
                            continue
                        # ===== 4. 编译检查 =====
                        try:
                            compile(content, py_file, 'exec')
                        except IndentationError as e:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            self.safe_log(f"❌ {rel_path}")
                            if 'tab' in str(e).lower() or 'inconsistent' in str(e).lower():
                                self.safe_log(f"   第 {e.lineno} 行: Tab/空格混合错误")
                                self.safe_log(f"   💡 建议: 将制表符(Tab)统一替换为空格")
                            else:
                                self.safe_log(f"   第 {e.lineno} 行: 缩进错误 - {e.msg}")
                            if e.text:
                                self.safe_log(f"   {e.text.rstrip()}")
                            self.safe_log("")
                            errors.append(rel_path)
                            continue
                        except SyntaxError as e:
                            rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                            self.safe_log(f"❌ {rel_path}")
                            self.safe_log(f"   第 {e.lineno} 行: {e.msg}")
                            if e.text:
                                self.safe_log(f"   {e.text.rstrip()}")
                                if e.offset:
                                    self.safe_log(f"   {' ' * (e.offset + 2)}^")
                            self.safe_log("")
                            errors.append(rel_path)
                            continue
                        # 通过所有检查
                        rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                        file_details.append(f"   ✅ {rel_path}: {line_count} 行, {func_count} 函数, {class_count} 类, {file_import_count} 导入")
                        self.safe_log(file_details[-1])
                except Exception as e:
                    rel_path = os.path.relpath(py_file, self.current_dir) if os.path.isdir(f) else os.path.basename(py_file)
                    warnings.append(rel_path)
                    self.safe_log(f"⚠️ {rel_path}: {e}")
            # ===== 过滤标准库 =====
            def is_standard_module(module_name):
                try:
                    import importlib.util
                    spec = importlib.util.find_spec(module_name)
                    if spec and spec.origin:
                        return 'site-packages' not in spec.origin and 'dist-packages' not in spec.origin
                except:
                    pass
                return module_name in STANDARD_LIBS
            EXCLUDE_IMPORTS = {'PyInstaller', 'pyi_hooks_contrib', 'pyi_hooks', 'module'}
            filtered_imports = [imp for imp in all_imports if imp in EXCLUDE_IMPORTS]
            third_party_imports = [imp for imp in all_imports if not is_standard_module(imp) and imp not in EXCLUDE_IMPORTS]
            standard_imports = [imp for imp in all_imports if is_standard_module(imp)]
            # ===== 延迟弹出结果对话框 =====
            QTimer.singleShot(100, lambda: self._show_check_result_dialog(
                errors, warnings, fixable_files, py_files, file_details,
                all_imports, standard_imports, third_party_imports, filtered_imports,
            ))
        except Exception as e:
            self.safe_log(f"❌ 语法检查异常: {e}")
            import traceback
            self.safe_log(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"语法检查出错:\n{e}")

    def _show_check_result_dialog(self, errors, warnings, fixable_files, py_files,
                                  file_details, all_imports, standard_imports,
                                  third_party_imports, filtered_imports):
        """显示检查结果对话框"""
        # 输出总结
        self.safe_log("=" * 60)
        self.safe_log(f"📊 检查完成:")
        self.safe_log(f"   总文件数: {len(py_files)}")
        self.safe_log(f"   ✅ 通过: {len(file_details)}")
        self.safe_log(f"   ❌ 语法错误: {len(errors)}")
        self.safe_log(f"   ⚠️ 格式警告: {len(warnings)}")
        self.safe_log("=" * 60)
        self.safe_log(f"📦 导入模块统计:")
        self.safe_log(f"   导入模块数: {len(all_imports)}")
        self.safe_log(f"   📚 标准库: {len(standard_imports)}")
        if standard_imports[:10]:
            self.safe_log(
                f"      {', '.join(standard_imports[:10])}" + ('...' if len(standard_imports) > 10 else ''))
        self.safe_log(f"   🔧 第三方库: {len(third_party_imports)}")
        if third_party_imports[:10]:
            self.safe_log(
                f"      {', '.join(third_party_imports[:10])}" + ('...' if len(third_party_imports) > 10 else ''))
        if filtered_imports:
            self.safe_log(f"   🚫 已过滤: {len(filtered_imports)} ({', '.join(filtered_imports)})")
        self.safe_log("=" * 60)
        # 检查备份
        has_backup_files = []
        for pf in py_files:
            backup_path = f"{os.path.splitext(pf)[0]}.bak.py"
            if os.path.exists(backup_path):
                has_backup_files.append(pf)
        has_backup = len(has_backup_files) > 0
        # ===== 弹窗逻辑 =====
        if errors or warnings or has_backup:
            dlg = QDialog(self)
            dlg.setModal(False)
            if errors:
                dlg.setWindowTitle("语法检查结果")
                msg = f"发现 {len(errors)} 个语法错误"
                if warnings:
                    msg += f"，另有 {len(warnings)} 个格式警告"
            elif warnings:
                dlg.setWindowTitle("格式检查结果")
                msg = f"发现 {len(warnings)} 个格式问题"
            elif has_backup:
                dlg.setWindowTitle("备份/还原")
                msg = "✅ 语法正确\n\n✅ 有备份文件可还原"
            layout = QVBoxLayout()
            layout.addWidget(QLabel(msg))
            # ===== 复选框：同一行水平排列 =====
            chk_layout = QHBoxLayout()
            chk_layout.setSpacing(15)
            chk_reorganize = QCheckBox("分组函数")
            chk_reorganize.setChecked(False)
            chk_layout.addWidget(chk_reorganize)
            chk_skip_preview = QCheckBox("跳过预览")
            chk_skip_preview.setChecked(False)
            chk_layout.addWidget(chk_skip_preview)
            chk_layout.addStretch()
            layout.addLayout(chk_layout)
            btn_layout = QHBoxLayout()
            # 修复按钮
            btn_fix = None
            if errors or warnings:
                btn_fix = QPushButton("修复")
                btn_layout.addWidget(btn_fix)
            btn_indent = QPushButton("缩进")
            btn_layout.addWidget(btn_indent)
            btn_restore = None
            if has_backup:
                btn_restore = QPushButton("还原")
                btn_layout.addWidget(btn_restore)
            btn_cancel = QPushButton("取消")
            btn_layout.addWidget(btn_cancel)
            layout.addLayout(btn_layout)
            dlg.setLayout(layout)
            def on_fix():
                self._clear_log()
                fixed_count = 0
                failed = []
                do_reorganize = chk_reorganize.isChecked()
                enable_preview = chk_skip_preview.isChecked()
                self.safe_log(f"📌 预览模式: {'开启' if enable_preview else '关闭'}")
                for file_path in fixable_files:
                    try:
                        original_content, new_content, changes, backup_path = self._auto_fix_formatting_preview(
                            file_path)
                        if not changes:
                            if os.path.exists(backup_path):
                                os.remove(backup_path)
                            self.safe_log(f"ℹ️ {os.path.basename(file_path)} 无需修改")
                            continue
                        if enable_preview:
                            dlg_preview = CodePreviewDialog(self, original_content, new_content, changes, file_path,
                                                            backup_path)
                            if dlg_preview.exec() == QDialog.DialogCode.Accepted:
                                self._apply_fix(file_path)
                                if do_reorganize:
                                    success, msg2 = self._reorganize_class_functions(file_path)
                                    if success:
                                        self.safe_log(f"✅ 已整理类函数: {os.path.basename(file_path)}")
                                    else:
                                        self.safe_log(f"⚠️ 整理类函数: {msg2}")
                                fixed_count += 1
                            else:
                                self.safe_log(f"↩️ 已取消修复: {os.path.basename(file_path)}")
                        else:
                            self._apply_fix(file_path)
                            if do_reorganize:
                                success, msg2 = self._reorganize_class_functions(file_path)
                                if success:
                                    self.safe_log(f"✅ 已整理类函数: {os.path.basename(file_path)}")
                                else:
                                    self.safe_log(f"⚠️ 整理类函数: {msg2}")
                            fixed_count += 1
                    except Exception as e:
                        failed.append(f"{os.path.basename(file_path)}: {e}")
                        self.safe_log(f"❌ {os.path.basename(file_path)} 修复失败: {e}")
                if failed:
                    #QMessageBox.warning(dlg, "修复结果",f"成功 {fixed_count} 个，失败 {len(failed)} 个:\n" + "\n".join(failed))
                    show_msg(self, "修复结果",f"成功 {fixed_count} 个，失败 {len(failed)} 个:\n" + "\n".join(failed),1)
                else:
                    #show_msg(dlg, "完成", f"已修复 {fixed_count} 个文件")
                    show_msg(self, "完成", f"已修复 {fixed_count} 个文件",1)
                dlg.accept()
            def on_restore():
                restored_count = 0
                failed = []
                for file_path in has_backup_files:
                    try:
                        if self._restore_backup(file_path):
                            restored_count += 1
                    except Exception as e:
                        failed.append(f"{os.path.basename(file_path)}: {e}")
                if failed:
                    #QMessageBox.warning(dlg, "还原结果",f"成功 {restored_count} 个，失败 {len(failed)} 个:\n" + "\n".join(failed))
                    show_msg(self, "还原结果",f"成功 {restored_count} 个，失败 {len(failed)} 个:\n" + "\n".join(failed),2)
                else:
                    #show_msg(dlg, "完成", f"已还原 {restored_count} 个文件")
                    show_msg(self, "完成", f"已还原 {restored_count} 个文件",1)
                dlg.accept()
            def on_cancel():
                dlg.reject()
            def on_indent_adjust():
                from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                             QPushButton, QLabel, QLineEdit,
                                             QSpinBox, QComboBox, QTextEdit)
                input_dlg = QDialog(dlg)
                input_dlg.setWindowTitle("缩进调整 - 批量/区域")
                input_dlg.setMinimumWidth(450)
                vbox = QVBoxLayout()
                # 模式选择
                mode_layout = QHBoxLayout()
                mode_layout.addWidget(QLabel("模式:"))
                mode_combo = QComboBox()
                mode_combo.addItems(["单个函数", "批量函数", "按行号区域"])
                mode_layout.addWidget(mode_combo)
                vbox.addLayout(mode_layout)
                # 单个函数模式
                single_widget = QWidget()
                single_layout = QVBoxLayout(single_widget)
                single_layout.addWidget(QLabel("函数名（如 main 或 MyClass.method）:"))
                single_edit = QLineEdit()
                single_layout.addWidget(single_edit)
                vbox.addWidget(single_widget)
                # 批量函数模式
                batch_widget = QWidget()
                batch_widget.setVisible(False)
                batch_layout = QVBoxLayout(batch_widget)
                batch_layout.addWidget(QLabel("函数名（多个用逗号、分号或换行分隔）:"))
                batch_edit = QTextEdit()
                batch_edit.setMaximumHeight(80)
                batch_edit.setPlaceholderText("main\nget_data\nMyClass.init\nMyClass.save")
                batch_layout.addWidget(batch_edit)
                vbox.addWidget(batch_widget)
                # 按行号区域模式
                region_widget = QWidget()
                region_widget.setVisible(False)
                region_layout = QHBoxLayout(region_widget)
                region_layout.addWidget(QLabel("起始行:"))
                start_spin = QSpinBox()
                start_spin.setRange(1, 99999)
                start_spin.setValue(1)
                region_layout.addWidget(start_spin)
                region_layout.addWidget(QLabel("结束行:"))
                end_spin = QSpinBox()
                end_spin.setRange(1, 99999)
                end_spin.setValue(10)
                region_layout.addWidget(end_spin)
                vbox.addWidget(region_widget)
                # 缩进量
                indent_layout = QHBoxLayout()
                indent_layout.addWidget(QLabel("缩进量:"))
                spin = QSpinBox()
                spin.setRange(-99, 99)
                spin.setValue(4)
                indent_layout.addWidget(spin)
                indent_layout.addWidget(QLabel("（正数增加，负数减少）"))
                vbox.addLayout(indent_layout)
                # 按钮
                hbox = QHBoxLayout()
                btn_ok = QPushButton("确定")
                btn_cancel = QPushButton("取消")
                hbox.addWidget(btn_ok)
                hbox.addWidget(btn_cancel)
                vbox.addLayout(hbox)
                input_dlg.setLayout(vbox)

                def on_mode_changed(index):
                    single_widget.setVisible(index == 0)
                    batch_widget.setVisible(index == 1)
                    region_widget.setVisible(index == 2)
                    input_dlg.adjustSize()
                mode_combo.currentIndexChanged.connect(on_mode_changed)

                def on_ok():
                    mode = mode_combo.currentIndex()
                    offset = spin.value()
                    if mode == 0:
                        func_name = single_edit.text().strip()
                        if not func_name:
                            #QMessageBox.warning(input_dlg, "提示", "请输入函数名")
                            show_msg(self, "提示", "请输入函数名", 1)
                            return
                        input_dlg.accept()
                        self._adjust_function_indent(func_name, offset)
                    elif mode == 1:
                        func_names = batch_edit.toPlainText().strip()
                        if not func_names:
                            #QMessageBox.warning(input_dlg, "提示", "请输入至少一个函数名")
                            show_msg(self, "提示", "请输入至少一个函数名", 1)
                            return
                        input_dlg.accept()
                        self._adjust_indent_batch(func_names, offset)
                    else:
                        start = start_spin.value()
                        end = end_spin.value()
                        if start > end:
                            #QMessageBox.warning(input_dlg, "提示", "起始行不能大于结束行")
                            show_msg(self, "提示", "起始行不能大于结束行", 1)
                            return
                        input_dlg.accept()
                        self._adjust_indent_by_lines(start, end, offset)
                btn_ok.clicked.connect(on_ok)
                btn_cancel.clicked.connect(input_dlg.reject)
                input_dlg.exec()
            btn_indent.clicked.connect(on_indent_adjust)
            if btn_fix:
                btn_fix.clicked.connect(on_fix)
            if btn_restore:
                btn_restore.clicked.connect(on_restore)
            btn_cancel.clicked.connect(on_cancel)
            dlg.show()
        else:
            show_msg(self, "完成", "✅ 所有文件语法正确！", 1)

    def _adjust_indent_by_lines(self, start_line, end_line, offset):
        """按行号区域调整缩进"""
        if start_line < 1 or end_line < start_line:
            QMessageBox.warning(self, "提示", "无效的行号范围")
            return False
        script_path = self.input_file.text()
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "提示", "请先选择Python脚本")
            return False
        try:
            with open(script_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            # 备份
            backup_path = os.path.splitext(script_path)[0] + '.bak.py'
            if not os.path.exists(backup_path):
                with open(backup_path, 'w', encoding='utf-8-sig') as f:
                    f.writelines(lines)
            # 调整指定行范围（行号从1开始，转为0索引）
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            new_lines = lines[:]
            for i in range(start_idx, end_idx):
                if lines[i].strip():  # 非空行
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    new_indent = max(0, current_indent + offset)
                    new_lines[i] = ' ' * new_indent + lines[i].lstrip()
            with open(script_path, 'w', encoding='utf-8-sig') as f:
                f.writelines(new_lines)
            self.safe_log(f"✅ 已调整第 {start_line} 行到第 {end_line} 行缩进 {offset:+d} 个空格")
            show_msg(self, "完成", f"已调整第 {start_line} 行到第 {end_line} 行缩进 {offset:+d} 个空格",1)
            return True
        except Exception as e:
            self.safe_log(f"❌ 缩进调整失败: {e}")
            QMessageBox.critical(self, "错误", f"调整失败: {e}")
            return False

    def _adjust_indent_batch(self, function_names, offset):
        """批量调整多个函数的缩进"""
        if not function_names:
            QMessageBox.warning(self, "提示", "请输入要调整的函数名")
            return False
        script_path = self.input_file.text()
        if not script_path or not os.path.exists(script_path):
            QMessageBox.warning(self, "提示", "请先选择Python脚本")
            return False
        try:
            with open(script_path, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
            # 备份
            backup_path = os.path.splitext(script_path)[0] + '.bak.py'
            if not os.path.exists(backup_path):
                with open(backup_path, 'w', encoding='utf-8-sig') as f:
                    f.writelines(lines)
            # 解析函数名列表（支持逗号、分号、换行分隔）
            import re
            func_list = re.split(r'[,;\n]+', function_names)
            func_list = [f.strip() for f in func_list if f.strip()]
            if not func_list:
                QMessageBox.warning(self, "提示", "未找到有效的函数名")
                return False
            # 收集所有需要调整的函数体行范围
            ranges_to_adjust = []
            for func_name in func_list:
                range_info = self._find_function_range(lines, func_name)
                if range_info:
                    ranges_to_adjust.append(range_info)
                else:
                    self.safe_log(f"⚠️ 未找到函数 '{func_name}'，跳过")
            if not ranges_to_adjust:
                QMessageBox.warning(self, "提示", "未找到任何匹配的函数")
                return False
            # 合并重叠或相邻的范围（避免重复调整）
            ranges_to_adjust.sort(key=lambda x: x[0])
            merged_ranges = []
            for start, end in ranges_to_adjust:
                if not merged_ranges or start > merged_ranges[-1][1] + 1:
                    merged_ranges.append([start, end])
                else:
                    merged_ranges[-1][1] = max(merged_ranges[-1][1], end)
            # 执行调整
            new_lines = lines[:]
            for start, end in merged_ranges:
                for i in range(start, end + 1):
                    if lines[i].strip():
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        new_indent = max(0, current_indent + offset)
                        new_lines[i] = ' ' * new_indent + lines[i].lstrip()
            with open(script_path, 'w', encoding='utf-8-sig') as f:
                f.writelines(new_lines)
            self.safe_log(f"✅ 已调整 {len(ranges_to_adjust)} 个函数缩进 {offset:+d} 个空格")
            show_msg(self, "完成", f"已调整 {len(ranges_to_adjust)} 个函数缩进 {offset:+d} 个空格",1)
            return True
        except Exception as e:
            self.safe_log(f"❌ 批量缩进调整失败: {e}")
            QMessageBox.critical(self, "错误", f"调整失败: {e}")
            return False

    def _find_function_range(self, lines, function_name):
        """查找函数在文件中的行范围，返回 (start_line, end_line) 或 None"""
        parts = function_name.split('.')
        if len(parts) == 1:
            target_name = parts[0]
            class_name = None
        elif len(parts) == 2:
            class_name, target_name = parts
        else:
            return None
        start_line = None
        base_indent = None
        in_class = False
        class_indent = None
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if not stripped:
                continue
            indent = len(line) - len(stripped)
            if stripped.startswith('class ') and class_name is not None:
                class_def = stripped.split('(')[0].split()[1]
                if class_def == class_name:
                    in_class = True
                    class_indent = indent
                    continue
            if in_class:
                if stripped.startswith('def ') and stripped.split('(')[0].split()[1] == target_name:
                    if indent > class_indent:
                        start_line = i
                        base_indent = indent
                        break
                elif stripped and indent <= class_indent and not stripped.startswith('#'):
                    in_class = False
                    continue
            else:
                if stripped.startswith('def ') and stripped.split('(')[0].split()[1] == target_name:
                    start_line = i
                    base_indent = indent
                    break
        if start_line is None:
            return None
        # 确定结束行
        end_line = len(lines) - 1
        for j in range(start_line + 1, len(lines)):
            stripped = lines[j].lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            current_indent = len(lines[j]) - len(stripped)
            if current_indent <= base_indent:
                end_line = j - 1
                break
        return (start_line, end_line)
    # ==================== 预估大小 ====================

    def _format_size(self, size):
        """格式化大小显示"""
        try:
            if size <= 0:
                return "0 B"
            if size < 1024:
                return f"{int(size)} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.0f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.2f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.3f} GB"
        except Exception:
            return "0 B"

    def _get_dir_size(self, path, keep_cache=False):
        """计算目录实际大小（递归）"""
        total = 0
        processed = set()
        if not os.path.exists(path):
            return 0
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            for root, dirs, files in os.walk(path):
                # 排除无关目录
                dirs[:] = [d for d in dirs if d not in {
                    '__pycache__', '.git', 'tests', 'test', 'docs', 'examples',
                    'demos', 'samples', '.pytest_cache'
                }]
                for f in files:
                    fp = os.path.join(root, f)
                    abs_path = os.path.abspath(fp)
                    if abs_path in processed:
                        continue
                    processed.add(abs_path)
                    try:
                        if not os.path.exists(fp):
                            continue
                        size = os.path.getsize(fp)
                        ext = os.path.splitext(f)[1].lower()
                        if ext in ['.pyd', '.dll', '.so', '.dylib']:
                            total += size
                        elif ext in ['.py', '.pyc']:
                            total += int(size * 0.5)
                        elif ext in ['.qm', '.png', '.jpg', '.qml', '.js', '.css']:
                            total += int(size * 0.3)
                        else:
                            total += int(size * 0.5)
                    except OSError:
                        pass
        except (OSError, PermissionError):
            pass
        return total

    def _get_package_size(self, package_name, site_packages_paths):
        """获取指定包的大小（只扫描顶层文件夹）"""
        total = 0
        # 特殊处理：PIL → 尝试 PIL 和 Pillow
        search_names = [package_name]
        if package_name.lower() == 'pillow':
            search_names = ['PIL', 'Pillow']
        elif package_name.lower() == 'pil':
            search_names = ['PIL', 'Pillow']
        for site_path in site_packages_paths:
            if not os.path.exists(site_path):
                continue
            for item in os.listdir(site_path):
                item_lower = item.lower()
                for search in search_names:
                    if item_lower == search.lower() or item_lower.startswith(search.lower() + '-'):
                        full_path = os.path.join(site_path, item)
                        if os.path.isdir(full_path):
                            size = self._get_dir_size(full_path, keep_cache=True)
                            total += size
                            self.safe_log(f"   📁 找到 {item}: {self._format_size(size)}")
                            break
        return total

    def _get_packer_config(self):
        """获取打包器配置：压缩比、运行时、打包系数"""
        packer = self.packer_combo.currentText() if hasattr(self, 'packer_combo') else "PyInstaller"
        configs = {
            "PyInstaller": {
                "compress_ratio": 1.0,
                "runtime_mb": 10,
                "dep_pack_ratio": 0.18,
                "overhead_mb": 2.0,  
                "factor": 1.0,
                "desc": "常规打包"
            },
            "PyInstaller-spec": {
                "compress_ratio": 1.0,
                "runtime_mb": 10,
                "dep_pack_ratio": 0.18,
                "overhead_mb": 2.0,  
                "factor": 0.95,
                "desc": "spec文件定制"
            },
            "PyInstaller-cmd": {
                "compress_ratio": 1.0,
                "runtime_mb": 10,
                "dep_pack_ratio": 0.18,
                "overhead_mb": 2.0,  
                "factor": 1.0,
                "desc": "命令行模式"
            },
            "Nuitka": {
                "compress_ratio": 0.50,
                "runtime_mb": 6,
                "dep_pack_ratio": 0.25,
                "overhead_mb": 2.0,  
                "factor": 0.55,
                "desc": "编译为C，体积最小"
            },
            "PyApp": {
                "compress_ratio": 0.90,
                "runtime_mb": 8,
                "dep_pack_ratio": 0.20,
                "overhead_mb": 2.0,  
                "factor": 0.85,
                "desc": "Rust打包"
            },
            "Py2exe": {
                "compress_ratio": 1.0,
                "runtime_mb": 12,
                "dep_pack_ratio": 0.15,
                "overhead_mb": 2.0,  
                "factor": 1.0,
                "desc": "传统打包"
            },
            "Cx_Freeze": {
                "compress_ratio": 1.0,
                "runtime_mb": 11,
                "dep_pack_ratio": 0.16,
                "overhead_mb": 2.0,  
                "factor": 0.95,
                "desc": "冻结打包"
            },
            "Pynsist": {
                "compress_ratio": 0.80,
                "runtime_mb": 15,
                "dep_pack_ratio": 0.18,
                "overhead_mb": 2.0,  
                "factor": 0.85,
                "desc": "生成安装程序"
            },
            "PyOxidizer": {
                "compress_ratio": 0.85,
                "runtime_mb": 7,
                "dep_pack_ratio": 0.22,
                "overhead_mb": 2.0,  
                "factor": 0.80,
                "desc": "Rust打包"
            },
            "Py2app": {
                "compress_ratio": 1.0,
                "runtime_mb": 12,
                "dep_pack_ratio": 0.17,
                "overhead_mb": 2.0,  
                "factor": 0.95,
                "desc": "macOS应用"
            },
        }
        return configs.get(packer, configs["PyInstaller"])

    def _estimate_size(self):
        self._clear_log()
        import random, json, os
        try:
            f = self.input_file.text()
            if not f or not os.path.exists(f):
                QMessageBox.warning(self, "提示", "请先选择Python文件或文件夹")
                return
            self.safe_log("=" * 50)
            self.safe_log("📊 开始预估打包大小...")
            packer = self.packer_combo.currentText() if hasattr(self, 'packer_combo') else "PyInstaller"
            config = self._get_packer_config()
            self.safe_log(f"📦 打包器: {packer}")
            self.safe_log(
                f"📋 配置: 压缩比 {int(config['compress_ratio'] * 100)}%, 运行时 {config['runtime_mb']}MB, 依赖比例 {int(config['dep_pack_ratio'] * 100)}%")
            big_deps = {
                'PyQt6': 38, 'PyQt5': 38, 'PySide6': 38, 'PySide2': 38,
                'tkinter': 6, 'wxPython': 40, 'PyAutoGUI': 4,
                'Pillow': 8, 'PIL': 8, 'opencv-python': 40,
                'numpy': 28, 'pandas': 25, 'scipy': 38, 'scikit-learn': 30,
                'matplotlib': 20, 'seaborn': 16, 'plotly': 25,
                'torch': 300, 'tensorflow': 380, 'keras': 40,
                'django': 10, 'flask': 2, 'fastapi': 2.5,
                'requests': 0.8, 'sqlalchemy': 4,
                'click': 0.8, 'rich': 1.5, 'pydantic': 1.5,
                'PyYAML': 0.8, 'lxml': 4, 'beautifulsoup4': 1.5,
                'grpcio': 8, 'protobuf': 4,
            }
            cache_file = None
            try:
                project_name = os.path.splitext(os.path.basename(f))[0]
                dist_dir = os.path.join(os.path.dirname(f), 'dist', project_name)
                os.makedirs(dist_dir, exist_ok=True)
                cache_file = os.path.join(dist_dir, '.size_cache.json')
            except:
                pass
            cache = {}
            if cache_file and os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8-sig') as cf:
                        all_cache = json.load(cf)
                        cache = all_cache.get(packer, {})
                except:
                    pass
            exe_size = None
            try:
                output_dir = self.output_dir.text() if hasattr(self, 'output_dir') else os.path.join(os.path.dirname(f),
                                                                                                     'dist')
                if not output_dir:
                    output_dir = os.path.join(os.path.dirname(f), 'dist')
                project_name = os.path.splitext(os.path.basename(f))[0]
                for path in [
                    os.path.join(output_dir, f'{project_name}.exe'),
                    os.path.join(output_dir, project_name, f'{project_name}.exe'),
                    os.path.join(os.path.dirname(f), 'dist', f'{project_name}.exe'),
                    os.path.join(os.path.dirname(f), 'dist', project_name, f'{project_name}.exe'),
                ]:
                    if os.path.exists(path):
                        exe_size = os.path.getsize(path)
                        break
            except:
                pass
            use_exe_reference = False
            if exe_size:
                reply = QMessageBox.question(
                    self,
                    "参考已有exe",
                    f"发现已打包的exe文件 ({self._format_size(exe_size)})，是否参考预估？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    use_exe_reference = True
                else:
                    exe_size = None
            # ===== 1. 代码大小 =====
            total_code_size = 0
            if os.path.isdir(f):
                for root, dirs, files in os.walk(f):
                    dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "build", "dist"}]
                    for file in files:
                        if file.endswith(".py"):
                            try:
                                total_code_size += os.path.getsize(os.path.join(root, file))
                            except:
                                pass
            else:
                total_code_size = os.path.getsize(f)
            self.safe_log(f"📁 代码文件: {self._format_size(total_code_size)}")
            # ===== 2. 数据文件大小 =====
            total_data_size = 0
            data_file_list = []
            if hasattr(self, 'data_files_list'):
                for src, tgt in self.data_files_list:
                    if os.path.exists(src):
                        if os.path.isfile(src):
                            size = os.path.getsize(src)
                            total_data_size += size
                            data_file_list.append(f"{os.path.basename(src)} ({self._format_size(size)})")
                        elif os.path.isdir(src):
                            size = self._get_dir_size(src, keep_cache=False)
                            total_data_size += size
                            data_file_list.append(f"{os.path.basename(src)}/ ({self._format_size(size)})")
            # ===== 图标文件已经在 data_files_list 中，不再单独计算 =====
            if total_data_size > 0:
                self.safe_log(f"📦 数据文件总计: {self._format_size(total_data_size)}")
                for item in data_file_list[:10]:
                    self.safe_log(f"   📄 {item}")
            # ===== 3. Python运行时 =====
            runtime_mb = config['runtime_mb']
            python_runtime = runtime_mb * 1024 * 1024
            self.safe_log(f"🐍 Python运行时: {runtime_mb} MB")
            # ===== 4. UPX压缩 =====
            upx_path = self.upx_path.text() if hasattr(self, 'upx_path') else ""
            compress_level = self.compress_combo.currentText() if hasattr(self, 'compress_combo') else "默认"
            compress_ratio = 1.0
            upx_enabled = upx_path and os.path.exists(upx_path) and compress_level != "不压"
            if upx_enabled:
                if compress_level == '最快':
                    compress_ratio = 0.98
                elif compress_level == '默认':
                    compress_ratio = 0.96
                elif compress_level == '最好':
                    compress_ratio = 0.94
                elif compress_level == '极致':
                    compress_ratio = 0.92
                else:
                    compress_ratio = 0.97
                self.safe_log(f"🗜️ UPX压缩: {compress_level}模式, 压缩率 {int(compress_ratio * 100)}%")
            # ===== 5. 基础开销 =====
            overhead_mb = config.get('overhead_mb', 2.0)
            overhead = int(overhead_mb * 1024 * 1024)
            # ===== 6. 依赖大小 =====
            dep_size = 0
            dep_details = []
            if exe_size and exe_size > 0:
                # ===== 分支1：有已打包exe参考 =====
                total_before = int(exe_size / (config['compress_ratio'] * compress_ratio)) if (config[
                                                                                                   'compress_ratio'] * compress_ratio) > 0 else exe_size
                dep_size = max(5 * 1024 * 1024,
                               total_before - total_code_size - total_data_size - python_runtime - overhead)
                dep_size = int(dep_size * (1 + random.uniform(-0.05, 0.05)))
                total_weight = 0
                dep_weights = {}
                for dep in self.hidden_imports_list:
                    if dep and dep.strip():
                        dep = dep.strip()
                        weight = big_deps.get(dep, 0.5) * config.get("factor", 1.0)
                        dep_weights[dep] = weight
                        total_weight += weight
                if total_weight > 0:
                    dep_size_mb = dep_size / (1024 * 1024)
                    new_cache = {}
                    for dep, weight in dep_weights.items():
                        dep_mb = max(0.5, dep_size_mb * weight / total_weight)
                        new_cache[dep] = dep_mb
                    actual_dep_size = sum(mb * 1024 * 1024 for mb in new_cache.values())
                    diff = dep_size - actual_dep_size
                    if diff != 0 and new_cache:
                        largest_dep = max(new_cache, key=new_cache.get)
                        new_cache[largest_dep] = max(0.5, new_cache[largest_dep] + diff / (1024 * 1024))
                    dep_size = sum(mb * 1024 * 1024 for mb in new_cache.values())
                    dep_details = []
                    for dep, mb in new_cache.items():
                        dep_details.append(f"{dep}: {mb:.2f}MB")
                        self.safe_log(f"   📦 {dep}: {mb:.2f}MB")
                    if cache_file:
                        try:
                            all_cache = {}
                            if os.path.exists(cache_file):
                                with open(cache_file, 'r', encoding='utf-8-sig') as cf:
                                    all_cache = json.load(cf)
                            all_cache[packer] = {k: round(v, 1) for k, v in new_cache.items()}
                            with open(cache_file, 'w', encoding='utf-8-sig') as cf:
                                json.dump(all_cache, cf, ensure_ascii=False, indent=2)
                        except:
                            pass
                total_before = total_code_size + total_data_size + dep_size + python_runtime + overhead
                total = int(total_before * config['compress_ratio'] * compress_ratio)
                total = max(total, 5 * 1024 * 1024)
                self.safe_log(
                    f"📊 预估: {self._format_size(total)}, 参考exe: {self._format_size(exe_size)}, 误差: {((total - exe_size) / exe_size * 100):.2f}%")
            else:
                # ===== 分支2：无exe参考，扫描依赖 =====
                site_packages_paths = []
                # ===== 获取Python路径（优先虚拟环境） =====
                py = self.python_path.currentText() if hasattr(self, 'python_path') else sys.executable
                # 如果启用虚拟环境，优先使用虚拟环境的Python
                if self.venv_mode.isChecked() and hasattr(self, 'use_venv') and self.use_venv:
                    venv_dir = os.path.join(get_exe_directory(), "common_venv")
                    if sys.platform == 'win32':
                        venv_py = os.path.join(venv_dir, "Scripts", "python.exe")
                    else:
                        venv_py = os.path.join(venv_dir, "bin", "python")
                    if os.path.exists(venv_py):
                        py = venv_py
                        self.safe_log(f"🐍 使用虚拟环境Python: {py}")
                    else:
                        self.safe_log(f"⚠️ 虚拟环境不存在，使用系统Python")
                try:
                    cmd = [py, "-c", "import site; print('\\n'.join(site.getsitepackages()))"]
                    result = self._run_hidden(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for p in result.stdout.strip().split('\n'):
                            p = p.strip()
                            if p and os.path.exists(p):
                                site_packages_paths.append(p)
                                self.safe_log(f"📁 site-packages: {p}")
                except Exception as e:
                    self.safe_log(f"⚠️ 获取site-packages失败: {e}")
                # 使用配置的依赖打包比例
                dep_pack_ratio = config['dep_pack_ratio']
                # 扫描依赖
                scan_results = {}
                dep_original_size = 0
                for dep in self.hidden_imports_list:
                    if dep and dep.strip():
                        dep = dep.strip()
                        package_name = MODULE_TO_PACKAGE.get(dep, dep.lower())
                        actual_size = self._get_package_size(package_name, site_packages_paths)
                        if actual_size > 0:
                            dep_mb = actual_size / (1024 * 1024)
                            scan_results[dep] = dep_mb
                            self.safe_log(f"   📦 {dep}: {self._format_size(actual_size)} (扫描)")
                        else:
                            # 尝试用预估值
                            dep_mb = big_deps.get(dep, 0.5) * config.get("factor", 1.0)
                            scan_results[dep] = dep_mb
                            self.safe_log(f"   📦 {dep}: {dep_mb:.2f}MB (预估值)")
                        dep_original_size += scan_results[dep] * 1024 * 1024
                # 应用打包比例
                dep_size = dep_original_size * dep_pack_ratio
                # 生成详情
                dep_details = []
                for dep in self.hidden_imports_list:
                    if dep and dep.strip():
                        dep = dep.strip()
                        mb = scan_results.get(dep, 0)
                        packed_mb = mb * dep_pack_ratio
                        dep_details.append(f"{dep}: {self._format_size(mb * 1024 * 1024)} → {self._format_size(packed_mb * 1024 * 1024)}")
                self.safe_log(f"📦 依赖原始(扫描): {dep_original_size / (1024 * 1024):.2f} MB")
                self.safe_log(f"📦 依赖打包后({int(dep_pack_ratio * 100)}%): {dep_size / (1024 * 1024):.2f} MB")
                # 计算最终大小
                total_before = total_code_size + total_data_size + dep_size + python_runtime + overhead
                total = int(total_before * config['compress_ratio'] * compress_ratio)
                total = max(total, 5 * 1024 * 1024)
            # ===== 计算占比 =====
            total_before_for_pct = total_before
            code_pct = total_code_size / total_before_for_pct * 100 if total_before_for_pct > 0 else 0
            data_pct = total_data_size / total_before_for_pct * 100 if total_before_for_pct > 0 else 0
            dep_pct = dep_size / total_before_for_pct * 100 if total_before_for_pct > 0 else 0
            runtime_pct = python_runtime / total_before_for_pct * 100 if total_before_for_pct > 0 else 0
            overhead_pct = overhead / total_before_for_pct * 100 if total_before_for_pct > 0 else 0
            self.safe_log(f"{'=' * 50}")
            self.safe_log(f"🎯 最终预估: {self._format_size(total)} ({total / 1024:.0f} KB)")
            # ===== 显示结果 =====
            result = f"📊 打包大小预估\n\n"
            result += f"打包器: {packer}\n"
            if config.get('desc'):
                result += f"说明: {config['desc']}\n"
            result += f"代码文件: {self._format_size(total_code_size)} ({code_pct:.0f}%)\n"
            if total_data_size > 0:
                result += f"数据文件: {self._format_size(total_data_size)} ({data_pct:.2f}%)\n"
                for item in data_file_list[:5]:
                    result += f"  • {item}\n"
                if len(data_file_list) > 5:
                    result += f"  • ... 还有 {len(data_file_list) - 5} 个文件\n"
            result += f"依赖库(打包后): {self._format_size(dep_size)} ({dep_pct:.2f}%)\n"
            result += f"Python运行时: {self._format_size(python_runtime)} ({runtime_pct:.2f}%)\n"
            result += f"基础开销: {self._format_size(overhead)} ({overhead_pct:.2f}%)\n"
            result += f"{'─' * 30}\n"
            result += f"压缩前合计: {self._format_size(total_before)}\n"
            if upx_enabled:
                result += f"UPX压缩({compress_level}): {int(compress_ratio * 100)}%\n"
            result += f"{'─' * 30}\n"
            result += f"✅ 预估打包后大小: {self._format_size(total)} ({total / 1024:.0f} KB)\n"
            if exe_size:
                error = (total - exe_size) / exe_size * 100 if exe_size > 0 else 0
                result += f"\n✅ 参考exe: {self._format_size(exe_size)}，误差率: {error:.2f}%"
            else:
                result += f"\n⚠️ 首次打包估算，实际大小可能有±20%偏差"
            if dep_details:
                result += f"\n\n📦 依赖详情:\n"
                for detail in dep_details[:10]:
                    result += f"  • {detail}\n"
                if len(dep_details) > 10:
                    result += f"  • ... 还有 {len(dep_details) - 10} 个模块\n"          
            show_msg(self, "大小预估", f"{result}", 3)
        except Exception as e:
            #show_msg(self, "错误", f"预估大小失败: {str(e)}",1)
            self.safe_log(f"⚠️ 预估大小失败: {e}")
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("错误")
            msg_box.setText(f"预估大小失败: {str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.setModal(False)
            msg_box.show()
    # ==================== 音乐播放器 ====================

    def _toggle_music_panel(self):
        """切换音乐面板"""
        self.music_visible = not self.music_visible
        #MEDIA_AVAILABLE = False
        if MEDIA_AVAILABLE:
            # 有多媒体库：使用右侧完整播放器
            if self.music_visible:
                self._show_full_player()
                self.music_toggle_btn.setText("🎵✖🎬")
            else:
                self._hide_full_player()
                self.music_toggle_btn.setText("🎵🎬")
        else:
            # 无多媒体库：使用状态栏简单面板
            if getattr(self, 'full_player_container', None):
                self.full_player_container.setVisible(False)
            self.music_frame.setVisible(self.music_visible)
            self.music_toggle_btn.setText("🎵✖🎬" if self.music_visible else "🎵🎬")
            if not self.music_visible:
                self._music_stop()

    def _show_full_player(self):
        if not getattr(self, 'full_player_container', None):
            self._create_full_player_container()
        if self.full_player_container:
            self.full_player_container.setVisible(True)
            total = self.log_splitter.width()
            pw = max(250, min(400, int(total * 0.3)))
            self.log_splitter.setSizes([total - pw, pw])
            self.music_toggle_btn.setText("🎵✖🎬")
        self.music_frame.setVisible(False)

    def _hide_full_player(self):
        """隐藏完整播放器"""
        if getattr(self, 'full_player_container', None):
            self.log_splitter.setSizes([10000, 0])
            self.full_player_container.setVisible(False)
        self.music_toggle_btn.setText("🎵🎬")
        self._music_stop()

    def _create_full_player_container(self):
        """创建完整播放器容器（日志右侧）"""
        if not hasattr(self, 'log_splitter'):
            return
        self.full_player_container = QFrame()
        self.full_player_container.setVisible(False)
        self.full_player_container.setMinimumWidth(180)
        self.full_player_container.setStyleSheet("QFrame{background:#2d3436;border-radius:8px;}")
        layout = QVBoxLayout(self.full_player_container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)  # 压缩间距
        # media_stack - 占主要空间
        self.media_stack = QFrame()
        self.media_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.full_cover = QLabel(self.media_stack)
        self.full_cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.full_cover.setText("🎵🎬")
        self.full_cover.setFont(QFont("Segoe UI Emoji", 32))
        self.full_cover.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2d3436, stop:1 #636e72);
            border-radius: 6px;
        """)
        if MEDIA_AVAILABLE:
            from PyQt6.QtMultimediaWidgets import QVideoWidget
            self.video_widget = QVideoWidget(self.media_stack)
            self.video_widget.setStyleSheet("background:#000000;border-radius:6px;")
            self.video_widget.setVisible(False)
            self.video_widget.mouseDoubleClickEvent = lambda e: self._toggle_fullscreen()
        layout.addWidget(self.media_stack, stretch=1)  # 主要拉伸空间
        # 歌名 - 压缩高度
        self.full_song = QLabel("未选择")
        self.full_song.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.full_song.setStyleSheet("font-size: 9px; color: #dfe6e9;")
        self.full_song.setMaximumHeight(16)  # 限制高度
        layout.addWidget(self.full_song)
        # 音量行 - 压缩
        vol_widget = QWidget()
        vol_widget.setMaximumHeight(24)
        vol_layout = QHBoxLayout(vol_widget)
        vol_layout.setContentsMargins(0, 0, 0, 0)
        vol_layout.setSpacing(2)
        vol_layout.addWidget(QLabel("🔊"))
        self.full_volume = QSlider(Qt.Orientation.Horizontal)
        self.full_volume.setRange(0, 100)
        self.full_volume.setValue(50)  # 初始 0.5
        self.full_volume.valueChanged.connect(self._set_volume)
        vol_layout.addWidget(self.full_volume)
        layout.addWidget(vol_widget)
        # 按钮行
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)
        # 创建按钮并保存引用
        self.btn_choose = EmojiButton("📁")
        self.btn_choose.clicked.connect(self._music_choose_folder)
        btn_layout.addWidget(self.btn_choose)
        self.btn_prev = EmojiButton("⏮")
        self.btn_prev.clicked.connect(self._music_prev)
        btn_layout.addWidget(self.btn_prev)
        self.full_play_btn = EmojiButton("▶")
        self.full_play_btn.clicked.connect(self._music_play_pause)
        btn_layout.addWidget(self.full_play_btn)
        self.btn_stop = EmojiButton("⏹")
        self.btn_stop.clicked.connect(self._music_stop)
        btn_layout.addWidget(self.btn_stop)
        self.btn_next = EmojiButton("⏭")
        self.btn_next.clicked.connect(self._music_next)
        btn_layout.addWidget(self.btn_next)
        self.btn_fs = EmojiButton("⛶")
        self.btn_fs.clicked.connect(self._toggle_fullscreen)
        btn_layout.addWidget(self.btn_fs)
        layout.addWidget(btn_widget)
        self.log_splitter.addWidget(self.full_player_container)
        self.log_splitter.setSizes([800, 0])
        # 初始化 Qt 播放器
        if MEDIA_AVAILABLE:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            self._player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._player.setAudioOutput(self._audio_output)
            self._audio_output.setVolume(0.5)  # 初始 0.5
            if hasattr(self, 'video_widget'):
                self._player.setVideoOutput(self.video_widget)
            self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        # 监听 media_stack 大小变化
        self.media_stack.resizeEvent = lambda e: self._resize_media_stack()

    def _set_volume(self, value):
        if getattr(self, '_audio_output', None):
            self._audio_output.setVolume(value / 100.0)

    def _resize_media_stack(self):
        """media_stack 4:3 + 同步按钮大小"""
        w = self.media_stack.width()
        h = self.media_stack.height()
        if w <= 0 or h <= 0:
            return
        # 4:3 视频/封面
        target_w = int(h * 4 / 3)
        target_h = h
        if target_w > w:
            target_w = w
            target_h = int(w * 3 / 4)
        x = (w - target_w) // 2
        y = (h - target_h) // 2
        if hasattr(self, 'full_cover'):
            self.full_cover.setGeometry(x, y, target_w, target_h)
        if hasattr(self, 'video_widget') and not self.video_widget.isFullScreen():
            self.video_widget.setGeometry(x, y, target_w, target_h)
        # 同步按钮大小：高度 = media_stack 高度的 8%
        btn_h = max(20, int(h * 0.08))
        btn_w = int(btn_h * 1.5)  
        for btn_name in ['btn_choose', 'btn_prev', 'full_play_btn', 
                'btn_stop', 'btn_next', 'btn_fs']:
            btn = getattr(self, btn_name, None)
            if btn:
                btn.setFixedSize(btn_w, btn_h)
        # 同步音量条高度
        if hasattr(self, 'full_volume'):
            vol_h = max(12, int(h * 0.05))
            self.full_volume.setFixedHeight(vol_h)

    def _init_qt_player(self):
        """初始化 QMediaPlayer"""
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.7)
        if getattr(self, 'video_widget', None):
            self._player.setVideoOutput(self.video_widget)
        self._player.positionChanged.connect(self._update_progress)
        self._player.durationChanged.connect(self._update_duration)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.errorOccurred.connect(self._on_player_error)

    def _update_progress(self, pos):
        """更新进度条"""
        if getattr(self, '_duration', 0) > 0 and getattr(self, 'full_progress', None):
            self.full_progress.setValue(int(pos / self._duration * 1000))

    def _update_duration(self, duration):
        """更新总时长"""
        self._duration = duration

    def _seek_position(self):
        """拖动进度条跳转"""
        if getattr(self, '_player', None) and getattr(self, '_duration', 0) > 0:
            pos = int(self.full_progress.value() / 1000 * self._duration)
            self._player.setPosition(pos)

    def _set_volume(self, val):
        """设置音量"""
        if getattr(self, '_audio_output', None):
            self._audio_output.setVolume(val / 100)

    def _on_media_status_changed(self, status):
        """播放结束自动下一首"""
        from PyQt6.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._music_next()

    def _on_player_error(self, error, msg):
        self.safe_log(f"❌ 播放器错误: {msg}")

    def _update_full_player_display(self):
        """更新完整播放器显示"""
        name = ""
        if self.music_files and 0 <= self.current_music_index < len(self.music_files):
            name = os.path.basename(self.music_files[self.current_music_index])[:30]
        if getattr(self, 'full_song', None):
            self.full_song.setText(name or "未选择")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'video_widget') and self.video_widget.isFullScreen():
            return
        if hasattr(self, 'media_stack'):
            self._resize_media_stack()

    def _music_choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择音乐/视频文件夹", "")
        if not folder:
            return
        exts = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma',
                '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
        self.music_files = [
            os.path.join(r, f) for r, _, files in os.walk(folder) for f in files
            if os.path.splitext(f)[1].lower() in exts
        ]
        if not self.music_files:
            self.safe_log("⚠️ 未找到音视频文件")
            return
        import random
        random.shuffle(self.music_files)
        self.current_music_index = 0
        self.safe_log(f"🎵 已加载 {len(self.music_files)} 个文件")
        self._music_play_current()
        self._update_full_player_display()

    def _music_play_current(self):
        if not self.music_files: return
        music_file = self.music_files[self.current_music_index]
        self.music_label.setText(os.path.basename(music_file)[:20])
        if self.music_play_btn:
            self.music_play_btn.setText("⏸")
        if hasattr(self, 'full_play_btn'):
            self.full_play_btn.setText("⏸")
        if MEDIA_AVAILABLE and getattr(self, '_player', None):
            from PyQt6.QtCore import QUrl
            self._player.setSource(QUrl.fromLocalFile(music_file))
            self._player.play()
            if hasattr(self, 'video_widget'):
                self.video_widget.setVisible(True)
                self.full_cover.setVisible(False)
            return
        try:
            if sys.platform == "win32":
                os.startfile(music_file)
            elif sys.platform == "darwin":
                self._popen_hidden(["open", music_file])
            else:
                self._popen_hidden(["xdg-open", music_file])
        except Exception as e:
            self.safe_log(f"❌ 播放失败: {e}")

    def _music_stop(self):
        if getattr(self, '_player', None):
            self._player.stop()
            # 停止时显示封面，隐藏视频
            if hasattr(self, 'video_widget'):
                self.video_widget.setVisible(False)
                self.full_cover.setVisible(True)
        if self.music_play_btn:
            self.music_play_btn.setText("▶")
        if hasattr(self, 'full_play_btn'):
            self.full_play_btn.setText("▶")
        self.music_label.setText("")

    def _toggle_fullscreen(self):
        """切换视频全屏"""
        if not MEDIA_AVAILABLE or not getattr(self, 'video_widget', None):
            return
        if self.video_widget.isFullScreen():
            self.video_widget.setFullScreen(False)
            self.video_widget.setParent(self.media_stack)
            self.video_widget.setGeometry(0, 0, self.media_stack.width(), self.media_stack.height())
            self.video_widget.setVisible(True)
            self.video_widget.raise_()
        else:
            # 进入全屏
            self.video_widget.setParent(None)  
            self.video_widget.setFullScreen(True)

    def _music_play_pause(self):
        # 有Qt播放器：真正的暂停/播放
        if MEDIA_AVAILABLE and hasattr(self, '_player') and self._player:
            from PyQt6.QtMultimedia import QMediaPlayer
            state = self._player.playbackState()
            if state == QMediaPlayer.PlaybackState.PlayingState:
                self._player.pause()
                if self.music_play_btn:
                    self.music_play_btn.setText("▶")
                if hasattr(self, 'full_play_btn'):
                    self.full_play_btn.setText("▶")
            else:
                self._player.play()
                if self.music_play_btn:
                    self.music_play_btn.setText("⏸")
                if hasattr(self, 'full_play_btn'):
                    self.full_play_btn.setText("⏸")
            return
        self._music_stop()
        self._music_play_current()

    def _music_prev(self):
        if self.music_files:
            self._music_stop()
            self.current_music_index = (self.current_music_index - 1) % len(self.music_files)
            self._music_play_current()
            self._update_full_player_display()

    def _music_next(self):
        if self.music_files:
            self._music_stop()
            self.current_music_index = (self.current_music_index + 1) % len(self.music_files)
            self._music_play_current()
            self._update_full_player_display()

    def _next_theme(self):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(self.themes)
        self._apply_theme()
        self.theme_btn.setText(self.themes[self.current_theme_idx])
        # 切换进度条样式
        self._switch_progress_bar()
        self.safe_log(f"🎨 主题: {self.themes[self.current_theme_idx]}")

    def _reset(self):
        self.app_name.clear()
        self.output_dir.setText(self.dist_dir)
        self.icon_label.setText("")
        self.single_mode.setChecked(True)
        self.venv_mode.setChecked(False)
        self.debug_mode.setChecked(False)
        self.uv_mode.setChecked(False)
        # 清空所有列表
        self.exclude_list.clear()
        self.exclude_listbox.clear()
        self.hidden_imports_list.clear()
        self.hidden_listbox.clear()
        self.data_files_list.clear()
        self.data_listbox.clear()
        # 更新所有计数
        self._update_exclude_count()
        self._update_hidden_count()
        self._update_data_count()
        self.log_text.clear()
        self.safe_log("🔄 已恢复默认设置")

    def _update_progress(self, value):
        """更新进度条"""
        try:
            if self.progress_bar:
                self.progress_bar.setValue(value)
                self.progress_label.setText(f"{value}% - 编译中...")
        except Exception as e:
            # 忽略进度条更新错误，避免崩溃
            pass

    def _on_build_finished(self, success, msg):
        """打包完成回调"""
        try:
            if hasattr(self, 'time_timer') and self.time_timer.isActive():
                self.time_timer.stop()
            if self.start_time:
                elapsed = time.time() - self.start_time
                self.time_label.setText(f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}")
                self.start_time = None
            self.btn_build.setText("▶ 开始打包")
            self.btn_build.setStyleSheet("")
            self.is_building = False
            if msg == "用户取消":
                self.safe_log("⏹️ 打包已取消")
                self.progress_label.setText("已取消")
                self.progress_bar.setValue(0)
                # 直接隐藏
                self.progress_container.setVisible(False)
                self.placeholder_widget.setVisible(True)
                self.progress_bar.setVisible(False)
                return
            # 检查exe是否新生成
            exe_info = self._check_exe_generated_with_time()
            if exe_info and exe_info.get('is_new', False):
                size = exe_info.get('size', 0)
                size_mb = size / (1024 * 1024)
                size_kb = int(size / 1024)
                self.safe_log(
                    f"✅ exe已生成: {os.path.basename(exe_info['path'])} {size_mb:.2f} MB ({size_kb:,} KB)")
                success = True
            if success and hasattr(self, '_injected_this_build') and self._injected_this_build:
                try:
                    self._restore_original_script()
                except Exception as e:
                    self.safe_log(f"⚠️ 恢复源码出错: {e}")
                finally:
                    self._injected_this_build = False
            if success:
                self.progress_bar.setValue(100)
                self.safe_log("✅ 打包完成！")
                # ===== 检查是否需要注入版本 =====
                if self.inject_selected.get('inject_version', False):
                    self.safe_log("📋 正在注入版本信息...")
                    self._inject_version_to_exe()
                try:
                    # 从 output_dir 和 app_name 获取项目目录
                    script = self.input_file.text()
                    if script:
                        proj_name = self.app_name.text() or os.path.splitext(os.path.basename(script))[0]
                        proj_dir = os.path.join(self.output_dir.text(), proj_name)
                        if os.path.exists(proj_dir):
                            import glob
                            for f in glob.glob(os.path.join(proj_dir, '*.spec')):
                                try: os.remove(f)
                                except: pass
                            for f in glob.glob(os.path.join(proj_dir, '*.rsp')):
                                try: os.remove(f)
                                except: pass
                        if show_msg(self, "打包完成",
                                    f"✅ 打包完成！\n\n输出目录: {proj_dir}\n\n是否打开编译目录？",
                                    timeout=3, buttons='yes_no'):
                            # 用户点击"是" → 打开目录
                            self._open_output()
                except Exception as e:
                    self.safe_log(f"⚠️ 清理临时文件失败: {e}")
            else:
                self.safe_log(f"❌ 打包失败: {msg}")
            self.progress_container.setVisible(False)
            self.placeholder_widget.setVisible(True)
            self.progress_bar.setVisible(False)
            self.progress_label.setText("")
            self.time_label.setText("⏰ 00:00")
        except Exception as e:
            self.safe_log(f"⚠️ 打包完成回调出错: {e}")
            try:
                self.btn_build.setText("▶ 开始打包")
                self.btn_build.setStyleSheet("")
                self.is_building = False
                self.progress_container.setVisible(False)
                self.placeholder_widget.setVisible(True)
                self.progress_bar.setVisible(False)
            except:
                pass
        finally:
            self.use_response_file_cb.blockSignals(True)
            self.use_response_file_cb.setChecked(False)
            self.use_response_file_cb.blockSignals(False)
            self._cleanup_worker()

    def _hide_progress(self):
        """隐藏进度条"""
        self.progress_container.setVisible(False)
        self.placeholder_widget.setVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("")
        self.time_label.setText("⏰ 00:00")

    def _kill_mingw_processes(self):
        """清理残留的 MinGW 编译器进程"""
        try:
            if sys.platform != 'win32':
                return
            import psutil
            killed = 0
            proc_names = ['c1.exe', 'cc1.exe', 'cc1plus.exe', 'gcc.exe', 'g++.exe', 'as.exe']
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name']
                    if name and name.lower() in proc_names:
                        try:
                            parent = proc.parent()
                            if parent and 'nuitka' in parent.name().lower():
                                proc.kill()
                                killed += 1
                        except:
                            pass
                except:
                    pass
            if killed > 0:
                self.safe_log(f"🧹 清理了 {killed} 个残留编译器进程")
        except Exception as e:
            pass

    def _cleanup_worker(self):
        """清理 worker 进程"""
        try:
            if hasattr(self, 'worker') and self.worker is not None:
                worker = self.worker
                if worker.isRunning():
                    worker.stop()
                    def check_finished():
                        try:
                            if worker.isRunning():
                                QTimer.singleShot(500, check_finished)
                            else:
                                try:
                                    worker.deleteLater()
                                    self.worker = None
                                    import gc
                                    gc.collect()
                                except:
                                    pass
                        except:
                            pass
                    QTimer.singleShot(500, check_finished)
                self.btn_build.setText("▶ 开始打包")
                self.btn_build.setStyleSheet("")
                self.progress_container.setVisible(False)
                self.placeholder_widget.setVisible(True)
                self.is_building = False
            self._kill_mingw_processes()
        except Exception:
            pass

    def _check_exe_generated_with_time(self):
        """检查exe是否新生成（根据时间戳判断）"""
        try:
            script = self.input_file.text()
            if not script:
                return None
            project_name = os.path.splitext(os.path.basename(script))[0]
            output_dir = self.output_dir.text()
            start_time = getattr(self, 'pack_start_time', time.time())
            if start_time is None:
                start_time = time.time()
            possible_paths = [
                os.path.join(output_dir, f'{project_name}.exe'),
                os.path.join(output_dir, project_name, f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', project_name, f'{project_name}.exe'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    mtime = os.path.getmtime(path)
                    size = os.path.getsize(path)
                    is_new = mtime > start_time - 5
                    if is_new and size > 100000:
                        return {
                            'path': path,
                            'mtime': mtime,
                            'size': size,
                            'is_new': is_new
                        }
                    elif is_new:
                        return {
                            'path': path,
                            'mtime': mtime,
                            'size': size,
                            'is_new': True
                        }
            return None
        except Exception as e:
            self.safe_log(f"⚠️ 检查exe失败: {e}")
            return None

    def _check_exe_generated(self):
        """检查exe是否已生成"""
        try:
            script = self.input_file.text()
            if not script:
                return False
            project_name = os.path.splitext(os.path.basename(script))[0]
            output_dir = self.output_dir.text()
            possible_paths = [
                os.path.join(output_dir, f'{project_name}.exe'),
                os.path.join(output_dir, project_name, f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', f'{project_name}.exe'),
                os.path.join(os.path.dirname(script), 'dist', project_name, f'{project_name}.exe'),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    if size > 100000:  # 大于100KB
                        #self.safe_log(f"📁 找到生成的exe: {path} ({size / 1024:.1f} KB)")
                        return True
            return False
        except:
            return False

    def _stop_build(self):
        """停止打包"""
        try:
            if not self.is_building:
                return
        except:
            return
        try:
            self.safe_log("⏹️ 正在停止打包...")
        except:
            pass
        try:
            if hasattr(self, 'time_timer') and self.time_timer.isActive():
                self.time_timer.stop()
        except:
            pass
        try:
            self.btn_build.setText("▶ 开始打包")
            self.btn_build.setStyleSheet("")
            self.progress_container.setVisible(False)
            self.placeholder_widget.setVisible(True)
            self.is_building = False
            self.start_time = None
            self.pack_start_time = None
        except:
            pass
        try:
            if hasattr(self, '_injected_this_build') and self._injected_this_build:
                try:
                    self._restore_original_script()
                except:
                    pass
                self._injected_this_build = False
        except:
            pass
        # ===== 清理 worker =====
        try:
            if hasattr(self, 'worker') and self.worker is not None:
                worker = self.worker
                # 1. 断开所有信号连接（阻止日志输出）
                try:
                    worker.log_signal.disconnect()
                    worker.progress_signal.disconnect()
                    worker.finished_signal.disconnect()
                except:
                    pass
                # 2. 标记停止
                worker._is_running = False
                # 3. 终止进程
                if hasattr(worker, 'process') and worker.process:
                    try:
                        worker.process.terminate()
                        worker.process.wait(timeout=1)
                    except subprocess.TimeoutExpired:
                        try:
                            worker.process.kill()
                            worker.process.wait(timeout=0.5)
                        except:
                            pass
                    except:
                        pass
                # 4. 等待线程退出
                worker.quit()
                worker.wait(500)
                self.worker = None
        except:
            pass
        try:
            self.safe_log("⏹️ 打包已停止")
        except:
            pass

    def _save_config(self):
        config = {
            'input': self.input_file.text(),
            'output': self.output_dir.text(),
            'name': self.app_name.text(),
            'packer': self.packer_combo.currentText(),
            'platform': self.platform_combo.currentText(),
            'onefile': self.single_mode.isChecked(),
            'debug': self.debug_mode.isChecked(),
            'venv': self.venv_mode.isChecked(),
            'uv': self.uv_mode.isChecked(),
            'auto_exclude': self.auto_exclude_cb.isChecked() if hasattr(self, 'auto_exclude_cb') else True,
            'hidden_imports': self.hidden_imports_list,
            'excludes': self.exclude_list,
            'version_info': self.version_info,
            'packer_panel_visible': self.packer_opt_row.isVisible() if hasattr(self, 'packer_opt_row') else False,
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8-sig') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.safe_log(f"❌ 保存配置失败: {e}")

    def _load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                # 先阻塞信号，避免触发不必要的更新
                self.packer_combo.blockSignals(True)
                output = config.get('output', '')
                if output and os.path.exists(output) and not self.input_file.text():
                    self.output_dir.setText(output)
                self.app_name.setText(config.get('name', ''))
                self.single_mode.setChecked(config.get('onefile', True))
                self.debug_mode.setChecked(config.get('debug', False))
                auto_exclude = config.get('auto_exclude', True)
                if hasattr(self, 'auto_exclude_cb'):
                    self.auto_exclude_cb.setChecked(auto_exclude)
                # 加载 venv 状态，但阻止信号触发
                self.venv_mode.blockSignals(True)
                self.venv_mode.setChecked(False)
                self.venv_mode.blockSignals(False)
                self.uv_mode.setChecked(config.get('uv', False))
                self.packer_combo.blockSignals(False)
                hidden_list = config.get('hidden_imports', [])
                for mod in hidden_list:
                    if mod not in self.hidden_imports_list:
                        self.hidden_imports_list.append(mod)
                        self.hidden_listbox.addItem(mod)
                exclude_list = config.get('excludes', [])
                for mod in exclude_list:
                    if mod not in self.exclude_list:
                        self.exclude_list.append(mod)
                        self.exclude_listbox.addItem(mod)
                self.version_info = config.get('version_info')
                self._update_exclude_count()
                self._update_hidden_count()
                self._update_data_count()
                packer_panel_visible = config.get('packer_panel_visible', False)
                if hasattr(self, 'packer_opt_row'):
                    current_packer = self.packer_combo.currentText()
                    if current_packer in ["Nuitka", "PyInstaller-spec", "PyInstaller-cmd"]:
                        self.packer_opt_row.setVisible(True)
                        self._update_packer_ui(current_packer)
        except Exception as e:
            pass

    def _auto_detect_current_dir(self):
        """延迟扫描当前目录（最后执行）"""
        if self._auto_detected:
            return  
        self._auto_detected = True
        QTimer.singleShot(100, self._do_auto_detect)

    def _do_auto_detect(self):
        """实际执行目录扫描"""
        if getattr(sys, 'frozen', False):
            current = os.path.dirname(sys.executable)
        else:
            current = os.getcwd()
        candidates = ['main.py', 'app.py', 'run.py', 'start.py', 'index.py',
                      'manage.py', 'server.py', 'entry.py', 'cli.py', '__main__.py']
        for cand in candidates:
            main_file = os.path.join(current, cand)
            if os.path.exists(main_file):
                self.input_file.setText(self._format_path(main_file))
                base = os.path.splitext(os.path.basename(main_file))[0]
                self.app_name.setText(base)
                self.safe_log(f"🎯 加载主文件: {cand}")
                self._auto_load_tool_icon(main_file, base)
                #threading.Thread(target=self._analyze_used, args=(main_file, True), daemon=True).start()
                if self.venv_mode.isChecked():
                    threading.Thread(target=self._auto_create_venv_for_script, args=(main_file,), daemon=True).start()
                return
        # 没有主文件，加载当前脚本自身
        try:
            main_file = sys.modules['__main__'].__file__
            if main_file and os.path.exists(main_file) and main_file.endswith('.py'):
                self.input_file.setText(self._format_path(main_file))
                base = os.path.splitext(os.path.basename(main_file))[0]
                self.app_name.setText(base)
                self.safe_log(f"🎯 加载源码: {os.path.basename(main_file)}")
                self._auto_load_tool_icon(main_file, base)
                #threading.Thread(target=self._analyze_used, args=(main_file, True), daemon=True).start()
                if self.venv_mode.isChecked():
                    threading.Thread(target=self._auto_create_venv_for_script, args=(main_file,), daemon=True).start()
                return
        except:
            pass
        py_files = [f for f in os.listdir(current) if f.endswith('.py')]
        if py_files:
            main_file = os.path.join(current, py_files[0])
            self.input_file.setText(self._format_path(main_file))
            base = os.path.splitext(os.path.basename(main_file))[0]
            self.app_name.setText(base)
            self.safe_log(f"🎯 自动选择: {os.path.basename(main_file)}")
            self._auto_load_tool_icon(main_file, base)
            threading.Thread(target=self._analyze_used, args=(main_file, True), daemon=True).start()
            if self.venv_mode.isChecked():
                threading.Thread(target=self._auto_create_venv_for_script, args=(main_file,), daemon=True).start()
        else:
            self.input_file.setText("")
            self.input_file.setPlaceholderText("选择Python文件")

    def closeEvent(self, event):
        """关闭事件 - 彻底清理所有资源"""
        # ===== 1. 停止监控线程 =====
        if hasattr(self, 'monitor_thread') and self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait(2000)
            self.monitor_thread = None
        # 兼容旧变量名
        if hasattr(self, 'monitor') and self.monitor:
            self.monitor.stop()
            self.monitor.join(2000)
            self.monitor = None
        # ===== 2. 关闭关于对话框 =====
        if self.about_dialog is not None and self.about_dialog.isVisible():
            self.about_dialog.close()
            self.about_dialog = None
        # ===== 3. 清理所有后台进程 =====
        self._cleanup_all_processes()
        # ===== 4. 保存缓存 =====
        self._save_cache()
        # ===== 5. 处理打包进行中的情况 =====
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            reply = QMessageBox.question(self, "确认", "打包正在进行中，确定要退出吗？")
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait(3000)
                self.worker = None
                event.accept()
            else:
                event.ignore()
                return
        else:
            event.accept()
        # ===== 6. 强制垃圾回收 =====
        import gc
        gc.collect()

    def _save_cache(self):
        """保存缓存（closeEvent 调用）"""
        try:
            old_cache = {}
            if os.path.exists(self.global_cache_file):
                try:
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        old_cache = json.load(f)
                except:
                    pass
            cache = {}
            # ===== 保留 upx 字段 =====
            if old_cache.get('upx'):
                cache['upx'] = old_cache['upx']
            if self.python_path and self.python_path.count() > 0:
                cache['python'] = {
                    'path': self.python_path.currentText() if self.python_path else '',
                    'version': self.python_version.text() if self.python_version else '',
                    'time': time.time()
                }
                cache['python_list'] = [self.python_path.itemText(i) for i in range(self.python_path.count())]
                cache['python_types'] = self._python_types_cache if hasattr(self, '_python_types_cache') else {}
            if self._cached_has_msvc or self._cached_has_mingw:
                cache['compiler'] = {
                    'msvc': self._cached_has_msvc,
                    'mingw': self._cached_has_mingw,
                    'msvc_path': self._cached_msvc_path,
                    'mingw_path': self._cached_mingw_path,
                    'msvc_version': self._cached_msvc_version,
                    'mingw_version': self._cached_mingw_version,
                }
            if self._cached_has_cargo or self._cached_has_rustc:
                cache['rust_compiler'] = {
                    'has_cargo': self._cached_has_cargo,
                    'has_rustc': self._cached_has_rustc,
                    'cargo_path': self._cached_cargo_path,
                    'rustc_path': self._cached_rustc_path,
                    'rust_version': self._cached_rust_version,
                }
            if self._cached_has_nsis:
                cache['nsis'] = {
                    'has_nsis': self._cached_has_nsis,
                    'nsis_path': self._cached_nsis_path,
                    'nsis_version': self._cached_nsis_version,
                }
            if self._packer_versions_cache:
                cache['packer_versions'] = self._packer_versions_cache
            # ===== 添加空值检查 =====
            if hasattr(self, 'nuitka_backend_combo') and self.nuitka_backend_combo is not None:
                cache['compiler_backend'] = self.nuitka_backend_combo.currentText()
            else:
                cache['compiler_backend'] = 'auto'
            cache['theme_index'] = self.current_theme_idx
            if not cache:
                return
            temp_file = self.global_cache_file + '.tmp'
            with open(temp_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.global_cache_file)
        except Exception as e:
            pass  

    def _cleanup_all_processes(self):
        """清理所有后台进程和线程"""
        import psutil
        import gc
        # ===== 1. 停止打包 worker =====
        if hasattr(self, 'worker') and self.worker is not None:
            if self.worker.isRunning():
                self.worker._is_running = False
                if hasattr(self.worker, 'process') and self.worker.process:
                    try:
                        self.worker.process.terminate()
                        import time
                        time.sleep(0.3)
                        if self.worker.process.poll() is None:
                            self.worker.process.kill()
                    except:
                        pass
                self.worker.wait(2000)
            self.worker = None
        # ===== 2. 停止 PyOxidizer worker =====
        if hasattr(self, 'pyoxidizer_worker') and self.pyoxidizer_worker is not None:
            if self.pyoxidizer_worker.isRunning():
                self.pyoxidizer_worker.stop()
                self.pyoxidizer_worker.wait(2000)
            self.pyoxidizer_worker = None
        # ===== 3. 停止加载器 =====
        if hasattr(self, 'loader') and self.loader is not None:
            if self.loader.isRunning():
                self.loader.quit()
                self.loader.wait(1000)
            self.loader = None
        # ===== 4. 终止所有子进程（使用 psutil） =====
        try:
            current_pid = os.getpid()
            current_process = psutil.Process(current_pid)
            children = current_process.children(recursive=True)
            if children:
                self.safe_log(f"🧹 发现 {len(children)} 个子进程，正在终止...")
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                time.sleep(0.5)
                for child in children:
                    try:
                        if child.is_running():
                            child.kill()
                    except:
                        pass
        except Exception as e:
            self.safe_log(f"⚠️ 清理子进程失败: {e}")
        # ===== 5. 强制垃圾回收 =====
        gc.collect()

    def _kill_multi_instances(self):
        """批量结束多开的程序 + 清理临时残留"""
        from PyQt6.QtWidgets import QInputDialog
        import tempfile
        import glob
        import shutil
        # 弹出输入框
        process_name, ok = QInputDialog.getText(
            self, "结束多开程序",
            "请输入要结束的进程名（不含.exe）:\n\n例如: PyPackTool_GUI-pyqt6_v66\n\n留空则结束当前程序同名进程",
            text=self.app_name.text() or "PyPackTool"
        )
        if not ok:
            return
        if not process_name.strip():
            process_name = os.path.splitext(os.path.basename(sys.executable))[0]
        if not process_name.lower().endswith('.exe'):
            process_name += '.exe'
        self.safe_log(f"🔍 正在查找并结束进程: {process_name}")
        killed_count = 0
        current_pid = os.getpid()
        # ===== 1. 结束进程 =====
        try:
            if sys.platform == 'win32':
                result = self._run_hidden(
                    ['tasklist', '/fi', f'IMAGENAME eq {process_name}', '/fo', 'csv'],
                    capture_output=True, text=True,
                    startupinfo=get_startupinfo()
                )
                pids = []
                for line in result.stdout.splitlines():
                    if '.exe' in line:
                        parts = line.replace('"', '').split(',')
                        if len(parts) >= 2:
                            try:
                                pid = int(parts[1])
                                if pid != current_pid:
                                    pids.append(pid)
                            except:
                                pass
                if pids:
                    for pid in pids:
                        self._run_hidden(
                            ['taskkill', '/f', '/pid', str(pid)],
                            capture_output=True,
                            startupinfo=get_startupinfo()
                        )
                        self.safe_log(f"  ✅ 已结束进程: PID {pid}")
                        killed_count += 1
                else:
                    self.safe_log(f"  ℹ️ 未找到其他 {process_name} 进程")
            else:
                result = self._run_hidden(
                    ['pgrep', '-f', process_name],
                    capture_output=True, text=True
                )
                pids = [int(p) for p in result.stdout.strip().split() if p and int(p) != current_pid]
                for pid in pids:
                    self._run_hidden(['kill', '-9', str(pid)], capture_output=True)
                    self.safe_log(f"  ✅ 已结束进程: PID {pid}")
                    killed_count += 1
            self.safe_log(f"📊 共结束 {killed_count} 个进程")
        except Exception as e:
            self.safe_log(f"❌ 结束进程失败: {e}")
        # ===== 2. 清理临时残留目录 =====
        temp_dir = tempfile.gettempdir()
        cleaned = 0
        # 清理 PyInstaller 残留 (_MEI*)
        for path in glob.glob(os.path.join(temp_dir, '_MEI*')):
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    cleaned += 1
                except:
                    pass
        # 清理 Nuitka onefile 残留 (onefile_*)
        for path in glob.glob(os.path.join(temp_dir, 'onefile_*')):
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    cleaned += 1
                except:
                    pass
        if cleaned > 0:
            self.safe_log(f"🧹 清理了 {cleaned} 个临时残留目录")
        else:
            self.safe_log("🧹 没有临时残留需要清理")
        if killed_count > 0 or cleaned > 0:
            show_msg(self, "完成", f"已结束 {killed_count} 个进程\n已清理 {cleaned} 个临时残留",1)
        else:
            show_msg(self, "提示", f"没有找到其他 {process_name} 进程\n也没有临时残留需要清理",1)

    def _get_base_path(self):
        """兼容 PyInstaller 和 Nuitka (--onefile / --onedir)"""
        if getattr(sys, 'frozen', False):
            # 1. PyInstaller 标准路径
            if hasattr(sys, '_MEIPASS'):
                return sys._MEIPASS
            # 2. Nuitka --onefile 模式
            nuitka_temp = os.environ.get('NUITKA_ONEFILE_TEMP')
            if nuitka_temp and os.path.exists(nuitka_temp):
                return nuitka_temp
            if hasattr(sys, '__compiled__'):        
                pass
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def _get_icon_path(self):
        """获取图标路径（优先外部，其次内部）"""
        exe_dir = os.path.dirname(sys.executable)
        for name in ["tool.ico", "icon.ico", "app.ico"]:
            test_path = os.path.join(exe_dir, name)
            if os.path.exists(test_path):
                return test_path
        if getattr(sys, 'frozen', False):
            # PyInstaller
            if hasattr(sys, '_MEIPASS'):
                base = sys._MEIPASS
                for name in ["tool.ico", "icon.ico", "app.ico"]:
                    test_path = os.path.join(base, name)
                    if os.path.exists(test_path):
                        return test_path
        # Nuitka onefil
        base = os.path.dirname(os.path.abspath(__file__))
        if base:
            for name in ["tool.ico", "icon.ico", "app.ico"]:
                test_path = os.path.join(base, name)
                if os.path.exists(test_path):
                    return test_path
        else:
            for name in ["tool.ico", "icon.ico", "app.ico"]:
                if os.path.exists(name):
                    return os.path.abspath(name)
            return None

    def _set_window_icon(self, icon_path=None):
        """设置窗口图标"""
        if not icon_path:
            icon_path = self._get_icon_path()
            if not icon_path:
                return False
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                QApplication.instance().setWindowIcon(icon)
                return True
            except Exception as e:
                pass
        return False

    def _background_prepare_environment(self):
        """后台静默准备环境（启动时执行）"""

        def prepare():
            try:
                import time
                # 先等待界面完全加载
                time.sleep(3)
                exe_dir = get_exe_directory()
                venv_dir = os.path.join(exe_dir, "common_venv")
                if sys.platform == 'win32':
                    venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
                else:
                    venv_python = os.path.join(venv_dir, "bin", "python")
                if not os.path.exists(venv_python):
                    self._create_venv_sync(venv_dir, venv_python)
                    return
                # ===== 启动时检测包数量，超过阈值则清理 =====
                if self.use_venv:
                   self._clean_venv_packages(venv_python)
            except Exception:
                pass
        threading.Thread(target=prepare, daemon=True).start()

    def _create_venv_sync(self, venv_dir, venv_python):
        """创建虚拟环境，升级pip，安装打包器，写入缓存，加入列表"""
        import subprocess
        import shutil
        import json
        import os
        import time
        import glob
        # 1. 使用界面选中的Python
        system_python = self.python_path.currentText()
        if not system_python or not os.path.exists(system_python):
            system_python = shutil.which('python') or shutil.which('python3')
            if not system_python:
                self.safe_log("❌ 未找到系统Python，无法创建虚拟环境")
                return
        self.safe_log(f"🔧 使用系统Python创建虚拟环境: {system_python}")
        system_dir = os.path.dirname(system_python)
        # 2. 创建虚拟环境（使用 --clear 强制覆盖）
        result = subprocess.run(
            [system_python, "-m", "venv", "--clear", venv_dir],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            self.safe_log(f"❌ 创建虚拟环境失败: {result.stderr}")
            return
        if not os.path.exists(venv_python):
            self.safe_log("❌ 虚拟环境Python不存在")
            return
        self.safe_log("✅ 虚拟环境创建成功")
        # ===== 3. 补全 DLLs 目录 =====
        src = os.path.join(system_dir, 'DLLs')
        dst = os.path.join(venv_dir, 'DLLs')
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
            self.safe_log("📦 已复制 DLLs 目录")
        # ===== 4. 补全 tcl 目录 =====
        src = os.path.join(system_dir, 'tcl')
        dst = os.path.join(venv_dir, 'tcl')
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
            self.safe_log("📦 已复制 tcl 目录")
        # ===== 5. 补全 Include 目录 =====
        src = os.path.join(system_dir, 'Include')
        dst = os.path.join(venv_dir, 'Include')
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
            self.safe_log("📦 已复制 Include 目录")
        # 7. 升级pip
        subprocess.run(
            [venv_python, "-m", "pip", "install", "--upgrade", "pip", "-q"],
            capture_output=True, text=True, timeout=60
        )
        self.safe_log("✅ pip升级完成")
        # 8. 安装打包器
        packers = ['pyinstaller', 'nuitka']
        clean_env = os.environ.copy()
        for var in ['PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV']:
            clean_env.pop(var, None)
        if sys.platform == 'win32':
            clean_env.setdefault('SYSTEMROOT', os.environ.get('SYSTEMROOT', ''))
            clean_env.setdefault('COMSPEC', os.environ.get('COMSPEC', ''))
        self.safe_log("📦 安装打包器到虚拟环境...")
        for pkg in packers:
            check = subprocess.run(
                [venv_python, '-m', 'pip', 'show', pkg],
                capture_output=True, text=True,
                env=clean_env, timeout=5
            )
            if check.returncode == 0:
                continue
            pip_install(venv_python, pkg, env=clean_env, quiet=True, timeout=300)
        self.safe_log("✅ 打包器安装完成")
        # 9. 读取打包器版本并写入缓存
        packer_versions = {}
        for pkg in packers:
            show = subprocess.run(
                [venv_python, '-m', 'pip', 'show', pkg],
                capture_output=True, text=True,
                env=clean_env, timeout=5
            )
            if show.returncode == 0:
                version = ''
                for line in show.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        break
                display_name = {
                    'pyinstaller': 'PyInstaller',
                    'nuitka': 'Nuitka',
                }.get(pkg, pkg)
                packer_versions[f"{display_name}@{venv_python}"] = version
        # 10. 更新 global_cache.json
        try:
            cache = {}
            if os.path.exists(self.global_cache_file):
                with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                    cache = json.load(f)
            if 'packer_versions' not in cache:
                cache['packer_versions'] = {}
            cache['packer_versions'].update(packer_versions)
            display_path = self._format_path(venv_python)
            if 'python_list' not in cache:
                cache['python_list'] = []
            if display_path not in cache['python_list']:
                cache['python_list'].append(display_path)
            if 'python_types' not in cache:
                cache['python_types'] = {}
            cache['python_types'][display_path] = "common_venv"
            # 获取包数量
            try:
                result = subprocess.run(
                    [venv_python, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0 and result.stdout.strip():
                    data = json.loads(result.stdout)
                    pkg_count = len(data)
                else:
                    pkg_count = 0
            except:
                pkg_count = 0
            cache['python'] = {
                'path': display_path,
                'version': self.python_version.text() or '',
                'time': time.time(),
                'pkg_count': pkg_count  
            }
            with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
            self.safe_log(f"✅ 缓存已更新")
        except Exception as e:
            self.safe_log(f"❌ 写入缓存失败: {e}")
        # 11. 加入界面列表并切换
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._on_venv_created(venv_python))

    def _on_venv_created(self, venv_python):
        """虚拟环境创建完成（主线程）"""
        self.safe_log("✅ 虚拟环境已就绪")
        self._do_enable_venv()

    def _copy_tk_to_venv(self, system_python, venv_dir):
        """从系统Python完整复制所有 tk/tcl 相关文件到虚拟环境（如果不存在）"""
        python_dir = os.path.dirname(system_python)
        copied = []
        skipped = []
        # ===== 1. 复制整个 tcl 目录 =====
        tcl_src = os.path.join(python_dir, 'tcl')
        if os.path.exists(tcl_src):
            dest_path = os.path.join(venv_dir, 'tcl')
            if os.path.exists(dest_path):
                skipped.append('tcl (已存在)')
            else:
                shutil.copytree(tcl_src, dest_path)
                self.safe_log(f"📦 复制 tcl 目录")
                copied.append('tcl')
        # ===== 2. 复制 DLLs 目录下所有 .pyd 文件 =====
        dlls_src = os.path.join(python_dir, 'DLLs')
        if os.path.exists(dlls_src):
            dest_dir = os.path.join(venv_dir, 'DLLs')
            os.makedirs(dest_dir, exist_ok=True)
            pyd_count = 0
            for item in os.listdir(dlls_src):
                if item.endswith('.pyd'):
                    src_file = os.path.join(dlls_src, item)
                    dest_file = os.path.join(dest_dir, item)
                    if not os.path.exists(dest_file):
                        shutil.copy2(src_file, dest_file)
                        pyd_count += 1
            if pyd_count > 0:
                self.safe_log(f"📦 复制 {pyd_count} 个 .pyd 文件到 DLLs")
                copied.append(f'DLLs ({pyd_count}个)')
            else:
                skipped.append('DLLs (已存在)')
        tkinter_src = os.path.join(python_dir, 'Lib', 'tkinter')
        if os.path.exists(tkinter_src):
            # 复制到 Lib
            dest_path = os.path.join(venv_dir, 'Lib', 'tkinter')
            if os.path.exists(dest_path):
                skipped.append('tkinter (Lib已存在)')
            else:
                shutil.copytree(tkinter_src, dest_path)
                self.safe_log(f"📦 复制 tkinter 到 Lib")
                copied.append('tkinter (Lib)')
            # 复制到 site-packages
            try:
                if sys.platform == 'win32':
                    venv_python = os.path.join(venv_dir, 'Scripts', 'python.exe')
                else:
                    venv_python = os.path.join(venv_dir, 'bin', 'python')
                if os.path.exists(venv_python):
                    result = subprocess.run(
                        [venv_python, '-c', 'import site; print(site.getsitepackages()[0])'],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        site_packages = result.stdout.strip()
                        dest_path_site = os.path.join(site_packages, 'tkinter')
                        if os.path.exists(dest_path_site):
                            skipped.append('tkinter (site-packages已存在)')
                        else:
                            shutil.copytree(tkinter_src, dest_path_site)
                            self.safe_log(f"📦 复制 tkinter 到 site-packages")
                            copied.append('tkinter (site-packages)')
            except:
                pass
        if copied:
            self.safe_log(f"✅ 新增: {', '.join(copied)}")
        if skipped:
            self.safe_log(f"⏭️ 跳过: {', '.join(skipped)}")

    def _check_packer_install_status(self, venv_python):
        """检查打包器安装状态"""
        import subprocess
        check = subprocess.run(
            [venv_python, '-m', 'pip', 'show', 'pyinstaller'],
            capture_output=True, text=True,
            timeout=5
        )
        if check.returncode == 0:
            # 安装完成
            self.safe_log("✅ 打包器安装完成")
            self.progress_bar.setValue(100)
            self.progress_label.setText("100% - 环境就绪")
            self.status_finish("就绪")
            self._packer_install_check_timer.stop()
            QTimer.singleShot(1000, lambda: self.progress_container.setVisible(False))

    def _silent_install_packers(self, venv_python):
        """后台静默安装打包器，安装完成后写入缓存"""
        import subprocess
        packers = [
            'pyinstaller',
            'nuitka',
            'pyapp',
            'py2exe',
            'cx-freeze',
            'pynsist',
            'pyoxidizer',
            'py2app',
        ]
        self._packers_installing = True
        clean_env = {'PATH': os.environ.get('PATH', '')}
        if sys.platform == 'win32':
            clean_env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
        for pkg in packers:
            check = subprocess.run(
                [venv_python, '-m', 'pip', 'show', pkg],
                capture_output=True, text=True,
                env=clean_env,
                timeout=5
            )
            if check.returncode == 0:
                continue
            pip_install(venv_python, pkg, env=clean_env, quiet=True, timeout=300)
        self._packers_installing = False
        self._packers_installed = True
        packer_versions = {}
        for pkg in packers:
            show = subprocess.run(
                [venv_python, '-m', 'pip', 'show', pkg],
                capture_output=True, text=True,
                env=clean_env,
                timeout=5
            )
            if show.returncode == 0:
                version = ''
                for line in show.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        break
                # 映射为界面显示的名称
                display_name = {
                    'pyinstaller': 'PyInstaller',
                    'nuitka': 'Nuitka',
                    'pyapp': 'PyApp',
                    'py2exe': 'Py2exe',
                    'cx-freeze': 'Cx_Freeze',
                    'pynsist': 'Pynsist',
                    'pyoxidizer': 'PyOxidizer',
                    'py2app': 'Py2app',
                }.get(pkg, pkg)
                packer_versions[f"{display_name}@{venv_python}"] = version
        # 写入 global_cache.json
        if packer_versions:
            try:
                cache = {}
                if os.path.exists(self.global_cache_file):
                    with open(self.global_cache_file, 'r', encoding='utf-8-sig') as f:
                        cache = json.load(f)
                if 'packer_versions' not in cache:
                    cache['packer_versions'] = {}
                cache['packer_versions'].update(packer_versions)
                with open(self.global_cache_file, 'w', encoding='utf-8-sig') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except:
                pass

    def _on_venv_created(self, venv_python):
        """虚拟环境创建完成（主线程）"""
        display_path = self._format_path(venv_python)
        if self.python_path.findText(display_path) < 0:
            self.python_path.addItem(display_path)
        if self.venv_mode.isChecked():
            self.python_path.setCurrentText(display_path)
            self._on_python_selected()
        self.status_finish("就绪")

    def _on_environment_ready(self):
        """环境准备完成"""
        self.status_label.setText("✅ 环境就绪")

    def _install_missing_deps_with_progress(self, python_exe, script_path):
        """利用 InstallDepsThread 异步安装缺失依赖，状态栏显示进度"""
        if not python_exe or not os.path.exists(python_exe):
            self.safe_log("❌ Python路径无效")
            return
        # 状态栏初始化
        self.status_start("检查依赖", color="blue")
        self.status_progress.setVisible(True)
        self.status_pct.setVisible(True)
        self.status_progress.setValue(0)
        self.status_pct.setText("0%")
        self.status_label.setText("检查依赖...")
        # 创建线程并连接信号
        self.deps_thread = InstallDepsThread(python_exe, script_path, self.hidden_imports_list)
        self.deps_thread.log_signal.connect(self.safe_log)
        self.deps_thread.progress_signal.connect(self._on_deps_progress)
        self.deps_thread.status_signal.connect(self._on_deps_status)
        self.deps_thread.finished_signal.connect(self._on_deps_finished)
        self.deps_thread.start()

    def _install_missing_deps_only(self, script_path):
        """安装缺失依赖（使用当前界面选择的Python）"""
        python_exe = self.python_path.currentText()
        if not python_exe or not os.path.exists(python_exe):
            self.safe_log("❌ 没有有效的Python")
            return
        import subprocess
        # 分析依赖
        self._analyze_used(script_path, auto_add=False)
        needed_modules = self.analyzed_modules
        all_needed = set(needed_modules)
        for mod in self.hidden_imports_list:
            if mod not in STANDARD_LIBS:
                all_needed.add(mod)
        # 获取已安装的包
        installed = self._get_installed_packages(python_exe)
        self.safe_log(f"📋 当前环境已安装 {len(installed)} 个包")
        missing = []
        for mod in all_needed:
            if mod in STANDARD_LIBS:
                continue
            pkg = MODULE_TO_PACKAGE.get(mod, mod)
            if pkg.lower() not in installed:
                missing.append(pkg)
        if not missing:
            self.safe_log("✅ 所有依赖已存在")
            return
        self.safe_log(f"📦 安装缺失依赖: {', '.join(missing)}")
        clean_env = {'PATH': os.environ.get('PATH', '')}
        if sys.platform == 'win32':
            clean_env['SYSTEMROOT'] = os.environ.get('SYSTEMROOT', '')
        for pkg in missing:
            success, result = pip_install(python_exe, pkg, env=clean_env, timeout=180)
            if success:
                self.safe_log(f"   ✅ {pkg} 安装成功")
            else:
                self.safe_log(f"   ❌ {pkg} 安装失败: {result.stderr[:100] if result else '未知错误'}")
        self.safe_log("✅ 依赖安装完成")

    def _copy_package_from_system(self, venv_python, pkg_name, system_python=None):
        """从系统Python拷贝包到虚拟环境（pip install 失败时兜底）"""
        import shutil
        import subprocess
        import os
        import re
        if not system_python:
            system_python = self.python_path.currentText()
            if not system_python or not os.path.exists(system_python):
                return False
        try:
            result = subprocess.run(
                [system_python, '-c', 'import site; print(site.getsitepackages()[0])'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False
            sys_site = result.stdout.strip()
            if not sys_site or not os.path.exists(sys_site):
                return False
        except:
            return False
        try:
            result = subprocess.run(
                [venv_python, '-c', 'import site; print(site.getsitepackages()[0])'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False
            venv_site = result.stdout.strip()
            if not venv_site or not os.path.exists(venv_site):
                return False
        except:
            return False
        pkg_base = pkg_name.replace('-', '_').replace('.', '_')
        patterns = [
            re.compile(r'^{}.*'.format(re.escape(pkg_base)), re.IGNORECASE),
            re.compile(r'^{}.*'.format(re.escape(pkg_name)), re.IGNORECASE),
        ]
        found_items = []
        for item in os.listdir(sys_site):
            if item.endswith('.dist-info') or item.endswith('.egg-info'):
                continue
            for pat in patterns:
                if pat.match(item):
                    found_items.append(item)
                    break
        for item in os.listdir(sys_site):
            if item.endswith('.dist-info') or item.endswith('.egg-info'):
                for pat in patterns:
                    if pat.match(item):
                        found_items.append(item)
                        break
        if not found_items:
            return False
        copied = 0
        for item in found_items:
            src = os.path.join(sys_site, item)
            dst = os.path.join(venv_site, item)
            if not os.path.exists(src):
                continue
            try:
                if os.path.isdir(dst):
                    shutil.rmtree(dst, ignore_errors=True)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                copied += 1
            except:
                pass
        if copied == 0:
            return False
        deps = []
        try:
            result = subprocess.run(
                [system_python, '-m', 'pip', 'show', pkg_name],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Requires:'):
                        reqs = line.split('Requires:', 1)[1].strip()
                        if reqs:
                            deps = [r.strip() for r in reqs.split(',') if r.strip()]
                        break
        except:
            pass
        if deps:
            for dep in deps:
                self._copy_package_from_system(venv_python, dep, system_python)
        return True

    def _clean_venv_packages(self, venv_python):
        """清理虚拟环境：包数量超过阈值时，询问用户是否清理"""
        import subprocess
        import json
        import threading
        import shutil
        import os

        def clean():
            try:
                clean_env = {
                    'PATH': os.environ.get('PATH', ''),
                    'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                    'SystemRoot': os.environ.get('SystemRoot', ''),
                    'COMSPEC': os.environ.get('COMSPEC', ''),
                }
                for key in list(os.environ.keys()):
                    if key.upper().startswith('PYTHON') or key.upper() in ('VIRTUAL_ENV', 'CONDA_PREFIX'):
                        continue
                clean_env['PYTHONNOUSERSITE'] = '1'
                clean_env['PYTHONSAFEPATH'] = '1'
                startupinfo = None
                creationflags = 0
                if sys.platform == 'win32':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creationflags = subprocess.CREATE_NO_WINDOW
                result = subprocess.run(
                    [venv_python, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True, text=True,
                    env=clean_env,
                    startupinfo=startupinfo,
                    creationflags=creationflags,
                    timeout=30
                )
                if result.returncode != 0:
                    return
                data = json.loads(result.stdout)
                pkg_count = len(data)
                QMetaObject.invokeMethod(self, "_update_pkg_count_display",
                                         Qt.ConnectionType.QueuedConnection,
                                         Q_ARG(int, pkg_count))
                # 获取阈值
                threshold = 100
                if hasattr(self, 'clean_threshold_spin'):
                    threshold = self.clean_threshold_spin.value()
                else:
                    cache = load_cache()
                    threshold = cache.get('clean_threshold', 100)
                if pkg_count < threshold:
                    return
                if not QMessageBox.warning(
                        self,
                        "清理虚拟环境",
                        f"虚拟环境包数量 {pkg_count} 超过阈值 {threshold}，\n是否清理不需要的包？\n\n将保留：打包工具、项目依赖、基础工具",
                        timeout=3,
                        buttons='yes_no'
                ):
                    self.safe_log("⏭️ 用户取消清理")
                    return
                self.safe_log(f"🧹 开始清理...")
                # ===== 构建保留包列表 =====
                keep_packages = set()
                keep_packages.add('pyinstaller')
                keep_packages.add('nuitka')
                keep_packages.add('pip')
                #keep_packages.add('pillow')
                keep_packages.add('setuptools')
                keep_packages.add('pkg_resources')
                keep_packages.add('wheel')
                # 打包工具依赖
                for dep in ['altgraph', 'macholib', 'pefile', 'pywin32_ctypes', 'orderedset', 'zstandard']:
                    keep_packages.add(dep)
                # 工具需要的库
                for lib in ['psutil', 'clr', 'pythonnet', 'pyqt6', 'pyqt5', 'pyside6', 'pyside2',
                            'pil', 'librehardwaremonitor','Pylibrehardwaremonitor']:
                    keep_packages.add(lib)
                for mod in self.hidden_imports_list:
                    if mod in STANDARD_LIBS:
                        continue
                    pkg = MODULE_TO_PACKAGE.get(mod, mod.lower())
                    if pkg == 'pil':
                        pkg = 'pillow'
                    elif pkg == 'opencv':
                        pkg = 'opencv-python'
                    keep_packages.add(pkg)
                self.safe_log(f"📦 保留 {len(keep_packages)} 个包")
                venv_dir = os.path.dirname(os.path.dirname(venv_python))
                site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
                if not os.path.exists(site_packages):
                    return
                cleaned = 0
                for item in os.listdir(site_packages):
                    item_lower = item.lower()
                    is_keep = False
                    for keep in keep_packages:
                        if item_lower.startswith(keep.lower()) or item_lower.replace('_', '-').startswith(keep.lower()):
                            is_keep = True
                            break
                    if is_keep:
                        continue
                    item_path = os.path.join(site_packages, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                        cleaned += 1
                    except:
                        pass
                if cleaned > 0:
                    self.safe_log(f"✅ 已清理 {cleaned} 个不需要的包")
                    QTimer.singleShot(500, self._update_venv_pkg_count)
                else:
                    self.safe_log("📌 没有需要清理的包")
            except Exception as e:
                self.safe_log(f"⚠️ 清理失败: {e}")
        threading.Thread(target=clean, daemon=True).start()

    def _update_venv_pkg_count(self):
        """更新虚拟环境已安装包数量显示（强制隔离环境）"""
        try:
            if not self.use_venv:
                self.venv_pkg_count_label.setText("0")
                return
            exe_dir = get_exe_directory()
            venv_dir = os.path.join(exe_dir, "common_venv")
            if sys.platform == 'win32':
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")
            if not os.path.exists(venv_python):
                self.venv_pkg_count_label.setText("0")
                return
            import subprocess
            clean_env = {
                'PATH': os.environ.get('PATH', ''),
                'SYSTEMROOT': os.environ.get('SYSTEMROOT', ''),
                'SystemRoot': os.environ.get('SystemRoot', ''),
                'COMSPEC': os.environ.get('COMSPEC', ''),
            }
            for key in list(os.environ.keys()):
                if key.upper().startswith('PYTHON') or key.upper() in ('VIRTUAL_ENV', 'CONDA_PREFIX'):
                    continue
            clean_env['PYTHONNOUSERSITE'] = '1'
            clean_env['PYTHONSAFEPATH'] = '1'
            startupinfo = None
            creationflags = 0
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            result = subprocess.run(
                [venv_python, '-m', 'pip', 'list', '--format=json'],
                capture_output=True, text=True,
                env=clean_env,
                startupinfo=startupinfo,
                creationflags=creationflags,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                count = len(data)
                self.venv_pkg_count_label.setText(str(count))
            else:
                self.venv_pkg_count_label.setText("?")
        except Exception as e:
            self.venv_pkg_count_label.setText("?")

    def _update_pkg_count_display(self, count):
         """主线程更新包数量显示"""
         if hasattr(self, 'venv_pkg_count_label'):
            self.venv_pkg_count_label.setText(str(count))

    def _auto_fix_filename_spaces(self, file_path):
        """自动修复文件名中的空格"""
        if not file_path or not os.path.exists(file_path):
            return file_path
        script_name = os.path.basename(file_path)
        if ' ' not in script_name:
            return file_path
        self.safe_log(f"📝 检测到文件名包含空格，将自动修复: {script_name}")
        name, ext = os.path.splitext(script_name)
        if ext:
            ext = ext.replace(' ', '')
        name = name.strip()
        import re
        name = re.sub(r'\s+', '_', name)
        new_name = name + ext
        script_dir = os.path.dirname(file_path)
        new_path = os.path.join(script_dir, new_name)
        counter = 1
        base_name = name
        while os.path.exists(new_path):
            new_name = f"{base_name}_{counter}{ext}"
            new_path = os.path.join(script_dir, new_name)
            counter += 1
        try:
            os.rename(file_path, new_path)
            self.safe_log(f"📝 已自动修复文件名: {script_name} → {new_name}")
            return new_path
        except Exception as e:
            self.safe_log(f"❌ 重命名失败: {e}")
            return file_path

def main():
    import time
    import traceback
    import os
    try:
        patch_subprocess_hide_window()
        _stderr_devnull = open(os.devnull, 'w')
        sys.stderr = _stderr_devnull
        try:
            os.dup2(_stderr_devnull.fileno(), 2)
        except Exception:
            pass
        os.environ['QT_LOGGING_RULES'] = '*.debug=false;*.warning=false'
        t_start = time.time()
        print(f"[Main] 程序启动: {now_str()}")
        global APP_BASE_PATH
        is_frozen = getattr(sys, 'frozen', False)
        is_nuitka_onefile = os.environ.get('NUITKA_ONEFILE_PARENT') is not None
        if is_frozen or is_nuitka_onefile:
            APP_BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
        temp_markers = ['\\temp\\', '\\tmp\\', 'onefile_']
        current_lower = APP_BASE_PATH.lower().replace('/', '\\')
        if any(m in current_lower for m in temp_markers):
            APP_BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
            print(f"[Main] 路径已修正: {APP_BASE_PATH}")
        print(f"[Main] APP_BASE_PATH: {APP_BASE_PATH}")
        def global_exception_handler(exc_type, exc_value, exc_tb):
            error_msg = f"程序崩溃:\n类型: {exc_type.__name__}\n消息: {exc_value}\n"
            error_msg += "".join(traceback.format_tb(exc_tb))
            print(error_msg)
            try:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(None, "程序崩溃", f"{exc_type.__name__}: {exc_value}")
            except:
                pass
        sys.excepthook = global_exception_handler
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        if is_frozen or is_nuitka_onefile:
            if not ensure_python_on_startup():
                if os.path.exists(os.path.join(tempfile.gettempdir(), "python-3.12.10-amd64.exe")):
                    sys.exit(0)
                else:
                    sys.exit(1)
        window = PackageMainWindow()
        window.show()
        app.processEvents()
        print(f"[Main] 窗口显示: {now_str()}")
        print(f"总耗时: {time.time() - t_start:.2f}秒")
        sys.exit(app.exec())
    except Exception as e:
        print(f"异常: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()