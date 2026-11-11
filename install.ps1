# PowerShell One-Line Installer for agy-memory-pkm
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\install.py" @args
