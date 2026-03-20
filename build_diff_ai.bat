@echo off

REM ===============================
REM 自動打包 diff_ai.py 成 diff_ai.exe
REM ===============================

REM 1️⃣ 設置變數
set PYTHON_EXE=c:\PortableApps\WinPython_3.13.11_x64\python\python.exe
set SOURCE=diff_ai.py
set EXE_NAME=diff_ai
set DEST_DIR=dist_exe

REM 2️⃣ 刪除舊 build/dist 資料夾，清理上一次打包
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %EXE_NAME%.spec del /f %EXE_NAME%.spec

REM 3️⃣ 使用 PyInstaller 打包
%PYTHON_EXE% -m PyInstaller --onefile --name %EXE_NAME% --console %SOURCE%

REM 4️⃣ 建立目標資料夾
if not exist %DEST_DIR% mkdir %DEST_DIR%

REM 5️⃣ 移動生成的 .exe 到目標資料夾
move dist\%EXE_NAME%.exe %DEST_DIR%\%EXE_NAME%.exe

REM 6️⃣ 清理 build/spec 目錄（可選）
rmdir /s /q build
del /f %EXE_NAME%.spec

REM delete diff_ai.exe and copy dist_exe\diff_ai.exe to current directory. 
del /f %EXE_NAME%.exe
copy %DEST_DIR%\%EXE_NAME%.exe ./

REM 7️⃣ 完成提示
echo.
echo [OK] 打包完成，生成的 .exe 位於 %DEST_DIR%\%EXE_NAME%.exe
pause
@echo on
