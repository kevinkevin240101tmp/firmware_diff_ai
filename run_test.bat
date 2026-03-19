@echo off

REM ===============================
REM 一鍵啟動 Flask server + CLI 測試
REM ===============================

REM 1️⃣ 設置 OpenAI API key (只在本 cmd 視窗有效)
REM set OPENAI_API_KEY=sk-你的真實APIkey
set OPENAI_API_KEY=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

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
