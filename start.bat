@echo off
title 火星简历 MarsResume

echo ========================================
echo   🔵 火星简历 · MarsResume 启动中...
echo ========================================
echo.

:: 启动后端
echo [1/2] 启动后端服务...
cd /d "%~dp0backend"
start "MarsResume-Backend" cmd /c "python -m uvicorn main:app --reload --port 8000 && pause"

:: 等几秒让后端启动
timeout /t 3 /nobreak >nul

:: 启动前端
echo [2/2] 启动前端服务...
cd /d "%~dp0frontend"
start "MarsResume-Frontend" cmd /c "npm run dev && pause"

:: 打开浏览器
echo.
echo 正在打开浏览器...
start http://localhost:5173

echo ========================================
echo   ✅ 启动完成！
echo.
echo   前端：http://localhost:5173
echo   后端：http://localhost:8000/docs
echo.
echo   关闭程序时请关闭两个黑色窗口
echo ========================================
pause