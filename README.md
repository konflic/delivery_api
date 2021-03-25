# API сервиса распределения заказов курьерской службы

## Конфигурация

Перед запуском нужно настроить конфигурацию проекта в файле ```.env``` все пояснения указанны в комментариях.

## Установка

Для развёртывания сервиса можно воспользоваться как docker так и развернуть используя venv модуль.

1. venv

```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python app.py
```

2. docker

Если конфигурация по умолчанию то порты можно не менять.

```bash
docker build -t api .
docker run -p 5000:5000 api -d
```

## OpenApi

Спецификацию в формате OpenApi можно найти в папке spec.