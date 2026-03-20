REM @echo off

REM ===============================
REM 一鍵啟動 Flask server + CLI 測試
REM ===============================

REM 1️⃣ 設置 OpenAI API key (只在本 cmd 視窗有效)
set OPENAI_API_KEY=sk-你的真實APIkey
REM 在 github 不能放 open ai api key, 否則會被 open ai disabled api key
REM set OPENAI_API_KEY=

REM 2️⃣ 啟動 Flask server (新視窗)
start "" c:\PortableApps\WinPython_3.13.11_x64\python\python.exe server.py

REM 3️⃣ 暫停 3 秒等待 server 完全啟動
timeout /t 3 >nul

REM 4️⃣ 呼叫 diff_ai.exe 測試
diff_ai.exe old.txt new.txt --key ABCD-1234

REM 5️⃣ 完成提示
echo.
echo [OK] CLI 測試完成，server 視窗仍保持開啟
pause
@echo on
