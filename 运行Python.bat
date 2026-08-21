@echo off
setlocal enabledelayedexpansion
title PytRunner

rem ================================================
rem ANSI 颜色 (Windows 10 1709+ 控制台原生支持; 不支持时自动无色)
rem 用法: 在 echo 内容前加 !C_OK!/!C_ERR!/!C_WARN!/!C_INFO!/!C_TITLE!/!C_DIM!,
rem       行尾加 !C_RST! 复位。
rem ================================================
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
if defined ESC (
 set "C_RST=!ESC![0m"
 set "C_DIM=!ESC![90m"
 set "C_TITLE=!ESC![95m"
 set "C_OK=!ESC![92m"
 set "C_WARN=!ESC![93m"
 set "C_ERR=!ESC![91m"
 set "C_INFO=!ESC![96m"
) else (
 set "C_RST="
 set "C_DIM="
 set "C_TITLE="
 set "C_OK="
 set "C_WARN="
 set "C_ERR="
 set "C_INFO="
)

rem ================================================
rem 可自定义: 要运行的 Python 脚本文件名(放在本批处理同目录下)
rem ================================================
set "PY_SCRIPT_NAME=PyPackTool_Qt6.py"
rem 运行脚本前自动检查的必需依赖(逗号分隔)
set "PY_REQUIRE=PyQt6,Pillow,psutil"
rem ===== 包名->import模块名 映射(import名与pip包名不一致的特殊包,如 Pillow->PIL) =====
set "MOD_IMPORT_Pillow=PIL"
rem ================================================

rem ---- 获取本批处理所在目录 ----
set "BAT_DIR=%~dp0"
set "BAT_DIR=%BAT_DIR:~0,-1%"
rem 不写任何缓存文件

set "PY_FILE=%~1"

rem ---- 包管理模式: 运行Python.bat pip 包名 [--upgrade] [其它pip参数] ----
rem 示例: 运行Python.bat pip urllib3 --upgrade  (升级 urllib3)
rem       运行Python.bat pip requests==2.31.0   (安装指定版本)
if /i "%~1"=="pip" (
 set "PY_DIR=%BAT_DIR%\"
 call :DETECT_PYTHONS
 call :RESTORE_CHOICE
 for /f "tokens=1,* delims= " %%a in ("%*") do (
  if "%%b"=="" (
   echo.
   echo !C_ERR![错误] 缺少包名。!C_RST!
   echo !C_DIM!用法: %~nx0 pip 包名 [--upgrade] [其它pip参数]!C_RST!
   echo !C_DIM!示例: %~nx0 pip urllib3 --upgrade!C_RST!
   pause <con
   exit /b 1
  )
  echo.
  echo !C_INFO![执行] pip install %%b!C_RST!
  echo.
  if exist "!PY_CMD!" (
   "!PY_CMD!" -m pip install %%b
  ) else (
   !PY_CMD! -m pip install %%b
  )
  echo.
  if "!ERRORLEVEL!"=="0" (
   echo !C_OK![完成] 安装/升级成功。!C_RST!
  ) else (
   echo !C_ERR![失败] 请检查包名、参数或网络。!C_RST!
  )
  echo.
 )
 pause <con
 exit /b 0
)

rem ---- 拖拽 .py 到本批处理: 直接快速运行(不进入菜单) ----
if not "%PY_FILE%"=="" goto :RUN_DIRECT

set "PY_FILE=%BAT_DIR%\%PY_SCRIPT_NAME%"
set "PY_FILE=%PY_FILE:"=%"

if not exist "%PY_FILE%" (
 echo.
 echo !C_ERR![错误] 文件不存在: %PY_FILE%!C_RST!
 echo !C_DIM!请将本批处理与 %PY_SCRIPT_NAME% 放在同一目录下,!C_RST!
 echo !C_DIM!或拖拽 .py 文件到本批处理上运行。!C_RST!
 pause <con
 exit /b 1
)

for %%i in ("%PY_FILE%") do (
 set "PY_NAME=%%~nxi"
 set "PY_DIR=%%~dpi"
)
cd /d "%PY_DIR%"

rem ================================================
rem 自动最小化: 双击运行时自动最小化窗口(1=开 0=关)
rem ================================================
set "AUTO_MIN=1"
rem ================================================


call :DETECT_PYTHONS
call :RESTORE_CHOICE

rem ---- 防重复由主程序内部单实例锁负责, 启动器不做进程/窗口判断 ----
rem ---- 启动前清理主程序残留进程(主程序自身无法清理; 排除打包进程) ----
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process | Where-Object { (($_.Name -eq 'python.exe') -and ($_.CommandLine -match 'PyPackTool_Qt6\.py') -and ($_.CommandLine -notmatch 'PyInstaller') -and ($_.CommandLine -notmatch 'nuitka')) -or ($_.Name -eq 'PyPackTool_Qt6.exe') }; if ($p) { $p | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } }" >nul 2>nul
rem ===== 启动前检查主程序必需依赖 =====
call :CHECK_INSTALL_DEPS
rem ===== 直接启动脚本 =====
echo.
echo !C_TITLE!============================================!C_RST!
echo !C_INFO!正在启动: %PY_NAME%!C_RST!
echo !C_INFO!Python  : !PY_CMD!!C_RST!
echo !C_TITLE!============================================!C_RST!
echo.
start "" /min "!PY_CMD!" -u "%PY_FILE%"
set "STARTED=1"
echo !C_OK!脚本已启动, 本窗口保留为"依赖补充"菜单。!C_RST!
echo !C_DIM!打包后如运行 exe 提示缺少依赖, 切回本窗口手动安装即可。!C_RST!
echo.

rem ===================== 主菜单 =====================
:MAIN_MENU
call :CHECK_DEPS_STATUS
cls
echo.
echo  !C_TITLE!==========================================!C_RST!
echo             !C_TITLE!Python 脚本运行器!C_RST!
echo  !C_TITLE!==========================================!C_RST!
echo.
echo   !C_INFO!当前Python: !PY_CMD!!C_RST!
echo   !C_INFO!必需依赖  : !DEPS_STATUS!!C_RST!
echo   !C_WARN!提示: 关闭主程序后, 本窗口将自动关闭; 其余依赖由主程序自动检测补装!C_RST!
echo.
echo   !C_WARN![1] 选择 Python 解释器 ^(共 !PY_COUNT! 个^)!C_RST!
echo.
for /l %%n in (1,1,!PY_COUNT!) do call echo       [%%n] %%PY_%%n%%  %%PYVER_%%n%%
echo.
echo   !C_WARN![2] 安装/升级依赖 ^(如 pandas; 升级: urllib3 --upgrade^)!C_RST!
echo.
echo   !C_WARN![3] 重新启动脚本!C_RST!
echo.
echo   !C_WARN![4] 退出!C_RST!
echo.
echo   !C_WARN!按数字键 1-4 选择：!C_RST!
:MENU_LOOP
choice /c 1234Q /t 2 /d Q >nul
if errorlevel 5 goto :CHECK_EXIT
if errorlevel 4 exit /b 0
if errorlevel 3 goto :RUN_SCRIPT
if errorlevel 2 goto :INSTALL_PKG
if errorlevel 1 goto :SELECT_PY
goto :MENU_LOOP

:CHECK_EXIT
rem 主程序进程已退出则自动关闭本窗口
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'PyPackTool_Qt6' }) { exit 1 } else { exit 0 }" >nul 2>nul
if errorlevel 1 goto :MENU_LOOP
echo.
echo !C_WARN![提示] 主程序已退出, 本窗口即将关闭。!C_RST!
timeout /t 1 /nobreak >nul
exit /b 0

:SELECT_PY
rem 用户主动查看解释器：删除版本缓存强制刷新
rem 版本号实时查询，不写缓存文件
call :GET_VERSIONS
cls
echo.
echo  !C_TITLE!==========================================!C_RST!
echo   !C_TITLE!可用 Python 解释器 ^(!PY_COUNT! 个^)!C_RST!
echo  !C_TITLE!==========================================!C_RST!
echo.
for /l %%n in (1,1,!PY_COUNT!) do call echo   [%%n] %%PY_%%n%%  %%PYVER_%%n%%
echo.
set /p CHOICE=请输入编号, 回车默认 1: <con
if "!CHOICE!"=="" set "CHOICE=1"
rem ---- 纯数字校验(修复字符串比较误判) ----
echo !CHOICE!|findstr /r "^[0-9][0-9]*$" >nul
if not "!ERRORLEVEL!"=="0" set "CHOICE=1"
if !CHOICE! geq 1 (
 if !CHOICE! leq !PY_COUNT! (
  call set "PY_CMD=%%PY_!CHOICE!%%"
  rem 不再写选择缓存
  echo.
  echo !C_OK!已选择: !PY_CMD!!C_RST!
  pause <con
  goto :MAIN_MENU
 )
)
echo !C_WARN![提示] 无效编号, 请输入 1-!PY_COUNT!!C_RST!
pause <con
goto :SELECT_PY

:INSTALL_PKG
cls
echo.
echo  !C_TITLE!==========================================!C_RST!
echo   !C_TITLE!安装 / 升级依赖 - 手动补充安装!C_RST!
echo   !C_INFO!Python: !PY_CMD!!C_RST!
echo  !C_TITLE!==========================================!C_RST!
echo.
echo  !C_DIM!用法示例(输入后回车):!C_RST!
echo    !C_DIM!pandas               安装!C_RST!
echo    !C_DIM!urllib3 --upgrade    升级 ^(简写 -U^)!C_RST!
echo    !C_DIM!requests==2.31.0     安装指定版本!C_RST!
echo    !C_DIM!-r requirements.txt  按清单安装!C_RST!
echo.
echo  !C_WARN!提示: 指定版本请用 == ^(如 pandas==2.0.3^), 不要用 ^>= ^< 等符号!C_RST!
echo  !C_WARN!输入 0 或留空返回主菜单。!C_RST!
echo.
:INSTALL_LOOP
set /p PKG_INPUT=请输入: <con
if "!PKG_INPUT!"=="" goto :MAIN_MENU
if "!PKG_INPUT!"=="0" goto :MAIN_MENU
echo.
echo !C_INFO![执行] pip install !PKG_INPUT!!C_RST!
echo.
if exist "!PY_CMD!" (
 "!PY_CMD!" -m pip install !PKG_INPUT!
) else (
 !PY_CMD! -m pip install !PKG_INPUT!
)
echo.
if "!ERRORLEVEL!"=="0" (
 echo !C_OK![完成] 安装/升级成功。!C_RST!
) else (
 echo !C_ERR![失败] 请检查包名、参数或网络。!C_RST!
)
echo.
echo !C_WARN![1] 继续   [2] 返回主菜单!C_RST!
set /p AGAIN=请输入: <con
if "!AGAIN!"=="1" goto :INSTALL_LOOP
goto :MAIN_MENU

:RUN_SCRIPT
echo.
echo !C_INFO!正在启动: %PY_NAME%  ^(Python: !PY_CMD!^)!C_RST!
start "" /min "!PY_CMD!" -u "%PY_FILE%"
set "STARTED=1"
echo !C_OK!脚本已启动。!C_RST!
pause <con
goto :MAIN_MENU

:CHECK_DEPS_STATUS
rem 只检查必需依赖缺不缺, 不安装(供主菜单显示)
set "DEPS_STATUS=已满足"
if not defined PY_REQUIRE (
 exit /b 0
)
set "DEPS_MISS="
for %%m in (%PY_REQUIRE%) do (
 set "IMPORT_MOD=!MOD_IMPORT_%%m!"
 if "!IMPORT_MOD!"=="" set "IMPORT_MOD=%%m"
 if exist "!PY_CMD!" (
 "!PY_CMD!" -c "import !IMPORT_MOD!" >nul 2>nul
 ) else (
 !PY_CMD! -c "import !IMPORT_MOD!" >nul 2>nul
 )
 if not "!ERRORLEVEL!"=="0" (
 if defined DEPS_MISS (
 set "DEPS_MISS=!DEPS_MISS! %%m"
 ) else (
 set "DEPS_MISS=%%m"
 )
 )
)
if defined DEPS_MISS (
 set "DEPS_STATUS=缺: !DEPS_MISS!"
)
exit /b 0


:ANALYZE_AND_INSTALL
rem ===== 分析被拖py的import依赖, 缺失自动补偿安装 =====
echo !C_INFO![依赖分析] 扫描 %PY_NAME% 的 import 依赖...!C_RST!
set "DEPCHK=%TEMP%\pypack_depcheck.py"
echo import ast, sys > "!DEPCHK!"
echo src = open(sys.argv[1], encoding='utf-8', errors='ignore').read() >> "!DEPCHK!"
echo tree = ast.parse(src) >> "!DEPCHK!"
echo mods = set() >> "!DEPCHK!"
echo for node in ast.walk(tree): >> "!DEPCHK!"
echo     if isinstance(node, ast.Import): >> "!DEPCHK!"
echo         for a in node.names: mods.add(a.name.split('.')[0]) >> "!DEPCHK!"
echo     elif isinstance(node, ast.ImportFrom): >> "!DEPCHK!"
echo         if node.module and node.level == 0: mods.add(node.module.split('.')[0]) >> "!DEPCHK!"
echo std = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set() >> "!DEPCHK!"
echo print(' '.join(sorted(m for m in mods if m not in std))) >> "!DEPCHK!"
set "DEPLIST="
if exist "!PY_CMD!" (
 for /f "delims=" %%d in ('"!PY_CMD!" "!DEPCHK!" "%PY_FILE%" 2^>nul') do set "DEPLIST=%%d"
) else (
 for /f "delims=" %%d in ('!PY_CMD! "!DEPCHK!" "%PY_FILE%" 2^>nul') do set "DEPLIST=%%d"
)
if not defined DEPLIST (
 echo !C_OK![依赖分析] 未发现第三方依赖, 跳过安装。!C_RST!
 exit /b 0
)
echo !C_INFO![依赖分析] 第三方依赖: !DEPLIST!!C_RST!
set "MISSING="
for %%m in (!DEPLIST!) do (
 set "PKG=%%m"
 if /i "%%m"=="PIL" set "PKG=Pillow"
 if /i "%%m"=="cv2" set "PKG=opencv-python"
 if /i "%%m"=="sklearn" set "PKG=scikit-learn"
 if /i "%%m"=="yaml" set "PKG=PyYAML"
 if /i "%%m"=="Crypto" set "PKG=pycryptodome"
 if /i "%%m"=="win32api" set "PKG=pywin32"
 if /i "%%m"=="dotenv" set "PKG=python-dotenv"
 if exist "!PY_CMD!" (
 "!PY_CMD!" -c "import %%m" >nul 2>nul
 ) else (
 !PY_CMD! -c "import %%m" >nul 2>nul
 )
 if not "!ERRORLEVEL!"=="0" (
 if defined MISSING (
 set "MISSING=!MISSING! !PKG!"
 ) else (
 set "MISSING=!PKG!"
 )
 )
)
if defined MISSING (
 echo !C_WARN![依赖分析] 缺失: !MISSING!, 自动补偿安装...!C_RST!
 if exist "!PY_CMD!" (
 "!PY_CMD!" -m pip install !MISSING! -q -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 30
 ) else (
 !PY_CMD! -m pip install !MISSING! -q -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 30
 )
 if not "!ERRORLEVEL!"=="0" (
 echo !C_WARN![依赖分析] 镜像安装失败, 改用官方源...!C_RST!
 if exist "!PY_CMD!" (
 "!PY_CMD!" -m pip install !MISSING! -q --timeout 30
 ) else (
 !PY_CMD! -m pip install !MISSING! -q --timeout 30
 )
 )
) else (
 echo !C_OK![依赖分析] 依赖已满足。!C_RST!
)
exit /b 0

:CHECK_INSTALL_DEPS
if not defined PY_REQUIRE (
 exit /b 0
)
echo !C_INFO![检查依赖] 检查必需模块: %PY_REQUIRE%!C_RST!
set "MISSING="
for %%m in (%PY_REQUIRE%) do (
 set "MOD=%%m"
 set "IMPORT_MOD=!MOD_IMPORT_%%m!"
 if "!IMPORT_MOD!"=="" set "IMPORT_MOD=%%m"
 if exist "!PY_CMD!" (
 "!PY_CMD!" -c "import !IMPORT_MOD!" >nul 2>nul
 ) else (
 !PY_CMD! -c "import !IMPORT_MOD!" >nul 2>nul
 )
 if not "!ERRORLEVEL!"=="0" (
 if defined MISSING (
 set "MISSING=!MISSING! !MOD!"
 ) else (
 set "MISSING=!MOD!"
 )
 )
)
if defined MISSING (
 echo !C_WARN![检查依赖] 缺失: !MISSING!, 自动安装...!C_RST!
 if exist "!PY_CMD!" (
 "!PY_CMD!" -m pip install !MISSING! -q -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 30
 ) else (
 !PY_CMD! -m pip install !MISSING! -q -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 30
 )
 if not "!ERRORLEVEL!"=="0" (
 echo !C_WARN![检查依赖] 镜像安装失败, 改用官方源...!C_RST!
 if exist "!PY_CMD!" (
 "!PY_CMD!" -m pip install !MISSING! -q --timeout 30
 ) else (
 !PY_CMD! -m pip install !MISSING! -q --timeout 30
 )
 )
 if not "!ERRORLEVEL!"=="0" (
 echo !C_ERR![警告] 必需依赖安装失败, 可稍后在菜单 [2] 手动安装。!C_RST!
 )
) else (
 echo !C_OK![检查依赖] 所有依赖已满足。!C_RST!
)
exit /b 0

:GET_VERSIONS
rem 为每个解释器缓存版本号：优先读缓存秒开，无缓存才逐个查询(首次约2-3秒)
rem 实时查询每个解释器的版本号
for /l %%n in (1,1,!PY_COUNT!) do (
 call set "PYPATH=%%PY_%%n%%"
 set "PVER="
 if exist "!PYPATH!" (
 for /f "delims=" %%v in ('"!PYPATH!" --version 2^>^&1') do set "PVER=%%v"
 ) else (
 for /f "delims=" %%v in ('!PYPATH! --version 2^>^&1') do set "PVER=%%v"
 )
 set "PYVER_%%n=!PVER!"
)
rem 不再写版本缓存文件
exit /b 0

:RESTORE_CHOICE
rem 不再读取“上次选择的 Python 编号”（不写缓存文件），每次默认第一个解释器
exit /b 0

:DETECT_PYTHONS
rem ===== 按优先级查找可用的 Python 解释器 =====
rem 命令型(py -3/python等)自动解析真实路径, 相同环境去重
set "PY_COUNT=0"
set "PY_CMD="
rem 规范化上一级目录(让路径显示更干净)
pushd "%BAT_DIR%\.."
set "PARENT_DIR=!CD!"
popd
for %%p in (
 "%PY_DIR%.venv\python.exe"
 "%PY_DIR%venv\python.exe"
 "%PARENT_DIR%\.venv\python.exe"
 "%PARENT_DIR%\venv\python.exe"
 "%PY_DIR%.venv\Scripts\python.exe"
 "%PY_DIR%venv\Scripts\python.exe"
 "%PARENT_DIR%\.venv\Scripts\python.exe"
 "%PARENT_DIR%\venv\Scripts\python.exe"
 "%PY_DIR%common_venv\Scripts\python.exe"
 "%PY_DIR%.venv\bin\python"
 "py -3"
 "python"
 "python3"
) do (
 set "TRY=%%~p"
 if not "!TRY!"=="" (
 set "AVAIL=0"
 if exist "!TRY!" set "AVAIL=1"
 if "!AVAIL!"=="0" (
 for /f %%w in ("!TRY!") do set "TRY_EXE=%%w"
 where "!TRY_EXE!" >nul 2>nul && set "AVAIL=1"
 )
 if "!AVAIL!"=="1" (
 set "TRY_REAL=!TRY!"
 if not exist "!TRY!" (
  for /f "delims=" %%e in ('!TRY! -c "import sys; print(sys.executable)" 2^>^&1') do set "TRY_REAL=%%e"
 )
 rem 校验真实路径必须存在(坏别名/报错文本直接跳过)
 if exist "!TRY_REAL!" (
 set "DUP=0"
 if !PY_COUNT! gtr 0 (
 for /l %%m in (1,1,!PY_COUNT!) do (
 call set "PREV=%%PY_%%m%%"
 if /i "!PREV!"=="!TRY_REAL!" set "DUP=1"
 )
 )
 if "!DUP!"=="0" (
 if not defined PY_CMD set "PY_CMD=!TRY_REAL!"
 set /a PY_COUNT+=1
 set "PY_!PY_COUNT!=!TRY_REAL!"
 )
 )
 )
 )
 )
if not defined PY_CMD (
 echo.
 echo !C_ERR![错误] 未找到 Python。请安装 Python 并勾选 "Add python.exe to PATH"。!C_RST!
 pause <con
 exit /b 1
)
call :GET_VERSIONS
exit /b 0

:RUN_DIRECT
rem ---- 拖拽 .py 到本批处理: 检测解释器并自动检查依赖后直接运行 ----
set "PY_FILE=%PY_FILE:"=%"
if not exist "%PY_FILE%" (
 echo.
 echo !C_ERR![错误] 文件不存在: %PY_FILE%!C_RST!
 pause <con
 exit /b 1
)
for %%i in ("%PY_FILE%") do (
 set "PY_NAME=%%~nxi"
 set "PY_DIR=%%~dpi"
)
cd /d "%PY_DIR%"
call :DETECT_PYTHONS
call :RESTORE_CHOICE
echo.
echo !C_TITLE!============================================!C_RST!
echo !C_INFO!脚本 : %PY_NAME%!C_RST!
echo !C_INFO!Python: !PY_CMD!!C_RST!
echo !C_INFO!目录 : %PY_DIR%!C_RST!
echo !C_TITLE!============================================!C_RST!
echo.
call :ANALYZE_AND_INSTALL
echo.
if exist "!PY_CMD!" (
 "!PY_CMD!" -u "%PY_FILE%" %2 %3 %4 %5 %6 %7 %8 %9
) else (
 !PY_CMD! -u "%PY_FILE%" %2 %3 %4 %5 %6 %7 %8 %9
)
set "EXIT_CODE=!ERRORLEVEL!"
echo.
echo !C_TITLE!============================================!C_RST!
if "!EXIT_CODE!"=="0" (
 echo !C_OK![完成] 退出码 0, 运行成功!C_RST!
) else (
 echo !C_ERR![错误] 退出码 !EXIT_CODE!!C_RST!
)
echo !C_TITLE!============================================!C_RST!
echo.
pause <con
exit /b 0
