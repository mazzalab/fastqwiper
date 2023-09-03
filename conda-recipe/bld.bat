"%PYTHON%" setup.py --ver %vars.FASTQWIPER_VER%%github.run_number% install --single-version-externally-managed --record=%TEMP%\record.txt
if errorlevel 1 exit 1
