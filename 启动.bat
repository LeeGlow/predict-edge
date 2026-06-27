@echo off
chcp 65001 >nul
echo ========================================
echo   PredictEdge 套利工具 启动脚本
echo ========================================
echo.

echo [1/3] 启动后端服务...
cd /d "%~dp0backend"
start "PredictEdge Backend" cmd /k "python main.py"
echo 后端已启动 (端口 8002)
echo.

echo [2/3] 启动前端...
cd /d "%~dp0frontend"
start "PredictEdge Frontend" cmd /k "python -m http.server 8080"
echo 前端已启动 (端口 8080)
echo.

echo [3/3] 完成！
echo.
echo ========================================
echo   打开浏览器访问:
echo   http://localhost:8080
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul
