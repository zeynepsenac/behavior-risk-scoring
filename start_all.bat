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

start cmd /k "uvicorn src.api:app --reload"

timeout /t 3 >nul

echo =========================
echo FRONTEND BASLIYOR
echo =========================

start cmd /k "cd risk-dashboard && npm run dev"

REM 🔥 FRONTEND'İN AÇILMASINI BEKLE
timeout /t 5 >nul

echo =========================
echo TARAYICI ACILIYOR
echo =========================

start http://localhost:5173

echo =========================
echo SISTEM CALISIYOR
echo =========================

pause