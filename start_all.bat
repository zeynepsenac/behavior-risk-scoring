@echo off
title FULL SYSTEM START

cd /d C:\Users\User\OneDrive\Belgeler\behavior-risk-scoring

echo =========================
echo VENV AKTIF EDILIYOR
echo =========================

call venv\Scripts\activate.bat

echo =========================
echo BACKEND BASLIYOR
echo =========================

REM ❗ BURASI DEĞİŞTİ
start cmd /k "uvicorn src.api:app --reload"

timeout /t 3 >nul

echo =========================
echo FRONTEND BASLIYOR
echo =========================

REM ❗ klasör adı risk-dashboard senin
start cmd /k "cd risk-dashboard && npm run dev"

echo =========================
echo SISTEM CALISIYOR
echo =========================

pause