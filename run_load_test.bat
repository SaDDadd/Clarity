@echo off
echo === Заполнение тестовой БД ===
python tests/load/seed_data.py
if errorlevel 1 exit /b 1

echo === Запуск нагрузочного теста ===
if "%~1"=="" (
    locust -f tests/load/locustfile.py --host=http://localhost:8000
) else (
    locust -f tests/load/locustfile.py --host=http://localhost:8000 %*
)