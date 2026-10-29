@echo off
rem Open Cloud Agents: Windows Command Launcher (ocagents)
setlocal

if exist "%~dp0..\src\ocagents\cli.py" (
    set "OCAGENTS_CLI=%~dp0..\src\ocagents\cli.py"
    if not defined OCAGENTS_HOME set "OCAGENTS_HOME=%~dp0.."
) else if exist "%USERPROFILE%\.open-cloud-agents\src\ocagents\cli.py" (
    set "OCAGENTS_CLI=%USERPROFILE%\.open-cloud-agents\src\ocagents\cli.py"
    if not defined OCAGENTS_HOME set "OCAGENTS_HOME=%USERPROFILE%\.open-cloud-agents"
) else if defined OCAGENTS_HOME (
    set "OCAGENTS_CLI=%OCAGENTS_HOME%\src\ocagents\cli.py"
) else (
    echo [ERROR] Open Cloud Agents assets not found.
    echo Please install via: irm https://ibrahimng.github.io/open-cloud-agents/install.ps1 | iex
    exit /b 1
)

python "%OCAGENTS_CLI%" %*
exit /b %ERRORLEVEL%

