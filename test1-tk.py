#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包程序 - 用于验证 PyInstaller/Nuitka 打包功能
"""

import sys
import os
import datetime
import json
import hashlib
import tkinter as tk
from tkinter import messagebox

# ========== 第三方模块导入 ==========
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# ========== 自定义模块模拟 ==========
class ConfigManager:
    """配置管理器"""
    def __init__(self):
        self.config = {
            "app_name": "测试应用程序",
            "version": "1.0.0",
            "author": "PyPackTool"
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def save(self, filename="config.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        return True

class DataProcessor:
    """数据处理类"""
    def __init__(self):
        self.data = []
    
    def load_data(self, data_list):
        self.data = data_list
        return len(self.data)
    
    def process(self):
        """处理数据"""
        if NUMPY_AVAILABLE:
            arr = np.array(self.data)
            return arr.sum(), arr.mean()
        else:
            return sum(self.data), sum(self.data) / len(self.data) if self.data else 0
    
    def to_dataframe(self):
        """转换为 DataFrame"""
        if PANDAS_AVAILABLE:
            return pd.DataFrame({'values': self.data})
        return None

# ========== 工具函数 ==========
def get_app_path():
    """获取应用程序路径（支持打包环境）"""
    if getattr(sys, 'frozen', False):
        # 打包后的 exe
        return os.path.dirname(sys.executable)
    else:
        # 开发环境
        return os.path.dirname(os.path.abspath(__file__))

def check_environment():
    """检查运行环境"""
    info = {
        "platform": sys.platform,
        "python_version": sys.version,
        "is_frozen": getattr(sys, 'frozen', False),
        "executable": sys.executable,
        "app_path": get_app_path(),
    }
    return info

def http_test():
    """HTTP 请求测试"""
    if not REQUESTS_AVAILABLE:
        return "requests 模块未安装"
    
    try:
        r = requests.get("https://httpbin.org/get", timeout=5)
        return f"HTTP 测试成功: {r.status_code}"
    except Exception as e:
        return f"HTTP 测试失败: {e}"

# ========== GUI 界面 ==========
class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 打包测试工具")
        self.root.geometry("550x500")
        self.root.resizable(True, True)
        
        # 获取应用路径
        self.app_path = get_app_path()
        
        # 初始化配置
        self.config_mgr = ConfigManager()
        self.processor = DataProcessor()
        
        # 创建界面
        self._create_widgets()
        self._load_info()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = tk.Label(
            self.root, 
            text="🐍 Python 打包测试工具", 
            font=("微软雅黑", 16, "bold"),
            fg="#2196f3"
        )
        title_label.pack(pady=10)
        
        # 信息框架
        info_frame = tk.LabelFrame(self.root, text="环境信息", padx=10, pady=5)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.info_text = tk.Text(info_frame, height=8, width=65, font=("Consolas", 9))
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 测试按钮框架
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="📊 测试 NumPy", command=self.test_numpy, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📈 测试 Pandas", command=self.test_pandas, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🌐 测试 Requests", command=self.test_requests, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="🎨 测试 PIL", command=self.test_pil, width=15).pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = tk.LabelFrame(self.root, text="测试日志", padx=10, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=65, font=("Consolas", 9))
        scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 底部按钮
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(bottom_frame, text="运行所有测试", command=self.run_all_tests, bg="#4caf50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="保存配置", command=self.save_config, bg="#2196f3", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="清除日志", command=self.clear_log, bg="#ff9800", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(bottom_frame, text="关闭", command=self.root.destroy, bg="#f44336", fg="white").pack(side=tk.RIGHT, padx=5)
    
    def _log(self, msg):
        """输出日志"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _load_info(self):
        """加载环境信息"""
        info = check_environment()
        info_text = f"""
平台: {info['platform']}
Python: {info['python_version'].split()[0]}
打包状态: {'是 (exe)' if info['is_frozen'] else '否 (源码)'}
可执行文件: {info['executable']}
应用路径: {info['app_path']}
        """
        self.info_text.insert(tk.END, info_text)
        self.info_text.configure(state='disabled')
        self._log("应用启动完成")
    
    def test_numpy(self):
        """测试 NumPy"""
        self._log("=" * 40)
        self._log("测试 NumPy...")
        
        if not NUMPY_AVAILABLE:
            self._log("❌ NumPy 模块未安装")
            return
        
        try:
            arr = np.array([1, 2, 3, 4, 5])
            self._log(f"数组: {arr}")
            self._log(f"求和: {arr.sum()}")
            self._log(f"平均值: {arr.mean()}")
            self._log(f"标准差: {arr.std():.2f}")
            self._log("✅ NumPy 测试通过")
        except Exception as e:
            self._log(f"❌ NumPy 测试失败: {e}")
    
    def test_pandas(self):
        """测试 Pandas"""
        self._log("=" * 40)
        self._log("测试 Pandas...")
        
        if not PANDAS_AVAILABLE:
            self._log("❌ Pandas 模块未安装")
            return
        
        try:
            data = {'name': ['A', 'B', 'C'], 'value': [10, 20, 30]}
            df = pd.DataFrame(data)
            self._log(f"DataFrame:\n{df}")
            self._log(f"描述统计:\n{df.describe()}")
            self._log("✅ Pandas 测试通过")
        except Exception as e:
            self._log(f"❌ Pandas 测试失败: {e}")
    
    def test_requests(self):
        """测试 Requests"""
        self._log("=" * 40)
        self._log("测试 Requests...")
        
        result = http_test()
        self._log(result)
    
    def test_pil(self):
        """测试 PIL"""
        self._log("=" * 40)
        self._log("测试 PIL...")
        
        if not PIL_AVAILABLE:
            self._log("❌ PIL 模块未安装")
            return
        
        try:
            # 创建一个简单的图像
            img = Image.new('RGB', (100, 100), color='red')
            self._log(f"图像模式: {img.mode}")
            self._log(f"图像大小: {img.size}")
            self._log("✅ PIL 测试通过")
        except Exception as e:
            self._log(f"❌ PIL 测试失败: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        self._log("=" * 40)
        self._log("开始运行所有测试")
        self.test_numpy()
        self.test_pandas()
        self.test_requests()
        self.test_pil()
        self._log("=" * 40)
        self._log("所有测试完成")
    
    def save_config(self):
        """保存配置"""
        config_file = os.path.join(self.app_path, "test_config.json")
        self.config_mgr.save(config_file)
        self._log(f"配置已保存到: {config_file}")
        messagebox.showinfo("成功", f"配置已保存到:\n{config_file}")
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
        self._log("日志已清除")

# ========== 程序入口 ==========
def main():
    """主函数"""
    try:
        root = tk.Tk()
        app = TestApp(root)
        root.mainloop()
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 键退出...")

if __name__ == "__main__":
    main()