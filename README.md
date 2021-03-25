# API сервиса распределения заказов курьерской службы

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

```bash
docker build -t api .
docker run -p 5000:5000 api -d
```

После чего сервис окажется доступен на порту 5000