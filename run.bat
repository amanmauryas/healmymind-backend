@echo off
setlocal

REM Check if Git Bash exists
where bash >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Git Bash not found. Please install Git for Windows.
    echo Visit: https://gitforwindows.org/
    exit /b 1
)

REM Get the script name from argument
set SCRIPT=%1
set ARGS=%2 %3 %4 %5 %6 %7 %8 %9

if "%SCRIPT%"=="" (
    echo Usage: run.bat [script-name] [arguments]
    echo.
    echo Available scripts:
    echo   init     - Initialize the project
    echo   manage   - Run management commands
    echo   db       - Database management
    echo   test     - Run tests and code quality checks
    echo   deploy   - Deployment commands
    echo   monitor  - Monitoring and maintenance
    echo.
    echo Example: run.bat test --coverage
    exit /b 1
)

REM Map script names to actual script files
if "%SCRIPT%"=="init" (
    bash ./scripts/init.sh %ARGS%
) else if "%SCRIPT%"=="manage" (
    bash ./scripts/manage.sh %ARGS%
) else if "%SCRIPT%"=="db" (
    bash ./scripts/db.sh %ARGS%
) else if "%SCRIPT%"=="test" (
    bash ./scripts/test.sh %ARGS%
) else if "%SCRIPT%"=="deploy" (
    bash ./scripts/deploy.sh %ARGS%
) else if "%SCRIPT%"=="monitor" (
    bash ./scripts/monitor.sh %ARGS%
) else (
    echo Unknown script: %SCRIPT%
    echo Run 'run.bat' without arguments to see available scripts
    exit /b 1
)

endlocal
