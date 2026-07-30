@echo off
title Binance Quant Bot 24/7 (Local HFT)
color 0A

echo ========================================================
echo     BINANCE QUANT TRADING BOT - MODO LOCAL 24/7
echo ========================================================
echo.
echo Presiona CTRL+C en cualquier momento para detener el bot.
echo El bot se ejecutara cada 5 minutos usando tu PC.
echo ¡Esto es 100%% GRATIS y no consume cuota de GitHub!
echo.

:loop
echo [%time%] Iniciando ciclo de analisis...
python data_fetcher.py
python pipeline_processor.py
echo.
echo [%time%] Ciclo completado. Esperando 5 minutos...
echo.
timeout /t 300 /nobreak
goto loop
