@echo off
REM ===== FirmwareDiff API 測試 =====

SET URL=[https://firmware-diff-ai.onrender.com/analyze](https://firmware-diff-ai.onrender.com/analyze)
SET KEY=%1
IF "%KEY%"=="" (
SET KEY=ABCDEFGH
)

REM ===== 建立 JSON payload =====
SET PAYLOAD={"key":"%KEY%","diff":["int timeout=30;","int timeout=60;"]}

REM ===== 使用 curl 呼叫 API =====
curl -s -X POST %URL% -H "Content-Type: application/json" -d "%PAYLOAD%"

echo.
echo ===== 結束 =====
