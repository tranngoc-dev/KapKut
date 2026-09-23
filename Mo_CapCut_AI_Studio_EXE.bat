@echo off
chcp 65001 > nul
title CapCut AI Studio (Desktop EXE)
cd /d "%~dp0\dist\CapCut_AI_Studio"
start "" "CapCut_AI_Studio.exe"
exit
