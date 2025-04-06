# Django E-commerce Application

## Установка

```bash
pip install -r requirements.txt
```

## Использование

```bash
python main.py <путь к логам> [<путь к логам> ...] --report <название отчета>
```

### Пример:

```bash
python main.py logs/app1.log logs/app2.log logs/app3.log --report handlers
```

### Использование
```bash
python main.py <путь к логам> [<путь к логам> ...] --report <название отчета> --<формат отчета> <название отсчета>.<формат отчета>
```

### Пример:

```bash
python main.py ./log1.log ./log2.log --report handlers --csv example.csv
```

## Доступные отчеты

### handlers
Отчет о состоянии ручек API по каждому уровню логирования. Показывает количество запросов к каждому эндпоинту с разбивкой по уровням логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL).

## Разработка

### Запуск тестов

```bash
pytest
```

### Пример вывода

![img.png](pict/img.png)
