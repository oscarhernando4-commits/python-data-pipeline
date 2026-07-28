@echo off
cd /d "c:\Users\hosca\Documents\Antigravity\BINANCE"
echo 📥 Descargando ultimas operaciones y datos desde la Nube (GitHub)...
git pull origin main
echo 📝 Generando reportes locales de Obsidian con los nuevos datos...
python master_dashboard_generator.py
echo ✅ Sincronizacion completada! Revisa tu Obsidian.
