@echo off
title Push Kaushal Sarathi to GitHub
echo ======================================================================
echo    Pushing Kaushal Sarathi to GitHub:
echo    https://github.com/Lewayaroan/Kaushal-sarathi.git
echo ======================================================================
echo.

cd /d "%~dp0"
set "PATH=C:\Program Files\Git\cmd;%PATH%"

echo Pushing main branch to GitHub...
echo (If prompted, your browser will open asking you to sign in to GitHub)
echo.
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo  SUCCESS! Successfully pushed to GitHub:
    echo  https://github.com/Lewayaroan/Kaushal-sarathi
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo  [NOTICE] If GitHub asks for authentication, sign in with your browser
    echo  or provide a Personal Access Token.
    echo ======================================================================
)

echo.
pause
