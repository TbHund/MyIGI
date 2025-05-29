import os
import sys
import coverage
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Запускаем coverage
    cov = coverage.Coverage(
        source=['main'],
        omit=[
            '*/migrations/*',
            '*/tests/*',
            '*/admin.py',
            '*/apps.py',
            '*/__init__.py',
        ]
    )
    cov.start()

    # Настраиваем Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Hotel.settings'
    django.setup()

    # Получаем и запускаем тест-раннер
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Запускаем тесты
    failures = test_runner.run_tests(["main.tests"])
    
    # Останавливаем coverage и генерируем отчет
    cov.stop()
    cov.save()
    
    # Выводим отчет в консоль
    print('\nCoverage Report:')
    cov.report()
    
    # Генерируем HTML отчет
    cov.html_report(directory='htmlcov')
    
    print('\nHTML coverage report generated in htmlcov/index.html')
    
    sys.exit(bool(failures)) 