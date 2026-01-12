@echo off
echo ========================================
echo   UPLOAD TO GITHUB
echo ========================================
echo.
echo 1. Create repository on GitHub first
echo 2. Copy repository URL
echo 3. Run this script
echo.
set /p repo_url="Enter GitHub repository URL: "
echo.
echo Removing old origin...
git remote remove origin 2>nul
echo.
echo Adding new origin...
git remote add origin %repo_url%
echo.
echo Adding files...
git add .
echo.
echo Creating commit...
git commit -m "WORKING VERSION: Ultra-fast payment creation 15-20 seconds"
echo.
echo Pushing to GitHub...
git push -u origin master
echo.
if %errorlevel% == 0 (
    echo SUCCESS! Code uploaded to GitHub
    echo Repository: %repo_url%
) else (
    echo ERROR! Check URL and access rights
)
echo.
pause