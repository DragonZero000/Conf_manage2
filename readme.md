## 1. Общее описание

Этот проект — минимальное CLI-приложение для визуализации графа зависимостей пакетов в формате Alpine Linux (apk). Оно анализирует репозиторий, извлекает прямые и транзитивные зависимости, строит граф с помощью NetworkX, визуализирует его через Matplotlib и сохраняет в файл. Поддерживает режимы работы: remote (удаленный репозиторий), local (локальный) и test (тестовый файл). Обнаруживает циклы, выводит порядок загрузки (если нет циклов). Разработано без использования менеджеров пакетов или библиотек для получения зависимостей. Результаты сохраняются в репозитории коммитами.

## 2. Описание всех функций и настроек

### Настройки (аргументы командной строки)
Приложение использует `argparse` для парсинга. Параметры:
- `--package` (обязательный): Имя пакета (например, "busybox").
- `--repo` (обязательный): URL/путь к репозиторию или тестовому файлу.
- `--mode` (по умолчанию "remote"): "local", "remote" или "test".
- `--version` (по умолчанию "latest"): Версия пакета.
- `--output` (по умолчанию "graph.png"): Имя файла графа.
- `--print-order` (флаг): Выводит порядок загрузки.

Обработка ошибок: Вывод помощи при неверных аргументах; исключения при fetching/parsing.

### Функции
- `parse_arguments()`: Парсер аргументов.
- `fetch_apkindex(repo, mode)`: Загрузка APKINDEX по режиму.
- `parse_apkindex(data, mode)`: Парсинг в словарь пакетов/версий/зависимостей.
- `get_deps(pkg, ver, all_entries)`: Получение зависимостей для пакета/версии.
- `build_graph_recursive(level, visited, G, all_entries)`: Рекурсивный BFS для графа.
- `main()`: Парсинг, загрузка, парсинг, зависимости, граф, циклы, визуализация, порядок (если флаг).

Зависимости: `argparse`, `sys`, `os`, `urllib.request`, `tarfile`, `io`, `networkx`, `matplotlib.pyplot`, `collections.defaultdict`.

## 3. Описание команд для сборки проекта и запуска тестов

Скрипт не требует сборки. Требования: Python 3.12+, `pip install networkx matplotlib`.

Запуск: `python main.py --package <пакет> --repo <репо> [опции]`.

Тесты: Режим "test" для файлов. Пример: `python main.py --package A --repo path/to/testfile --mode test --print-order`. Проверять циклы/порядок вручную. Автотесты не реализованы.

## 4. Примеры использования

### Пример 1: Удаленный репозиторий
`python main.py --package busybox --repo https://dl-cdn.alpinelinux.org/alpine/v3.18/main/x86_64 --mode remote --output graph.png`

Вывод: Параметры, зависимости, граф сохранен.

### Пример 2: Тестовый режим с циклом
Файл:
```
P:A
V:1.0
D:B

P:B
V:1.0
D:A
```
`python main.py --package A --repo test_repo.txt --mode test --print-order`

Вывод: Зависимости, warning о цикле, Cannot compute load order due to cyclic dependencies.

### Пример 3: Порядок загрузки
Файл без циклов:
```
P:A
V:1.0
D:B C

P:B
V:1.0
D:D

P:C
V:1.0

P:D
V:1.0
```
`python main.py --package W --repo test_repo.txt --mode test --print-order`

Вывод: Зависимости, граф, порядок: C G W.