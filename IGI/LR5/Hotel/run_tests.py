import os
import sys
import coverage
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # coverage для тестирования
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

    #Настройка джанго
    os.environ['DJANGO_SETTINGS_MODULE'] = 'Hotel.settings'
    django.setup()

    #тест раннер
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    #запуск тестов
    failures = test_runner.run_tests(["main.tests"])
    
    #остановка coverage и создание отчета
    cov.stop()
    cov.save()
    
    #вывод отчета в консоль
    print('\nCoverage Report:')
    cov.report()
    
    #html отчет
    cov.html_report(directory='htmlcov')
    print('\nHTML coverage report generated in htmlcov/index.html')
    
    sys.exit(bool(failures)) 