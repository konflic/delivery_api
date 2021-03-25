import requests
import pytest
import random

from data_generators import random_couriers_sample, manual_courier, manual_order


@pytest.mark.api
def test_add_duplicate_courier(base_url):
    """Нельзя добавить дублирующихся курьеров"""
    stable_sample = random_couriers_sample(2)

    response = requests.post(base_url + "/couriers", json=stable_sample)
    assert response.status_code == 201, response.text

    response = requests.post(base_url + "/couriers", json=stable_sample)
    assert response.status_code == 400, response.text


@pytest.mark.api
def test_assign_order(base_url):
    courier_id = random.randint(9999, 9999999)
    order_id = random.randint(9999, 9999999)

    courier = manual_courier(courier_id, "car", [999], ["10:00-18:00"])
    order = manual_order(order_id, 49.0, 999, ["11:00-15:00"])

    # Добавляю курьера
    response = requests.post(base_url + "/couriers", json=courier)
    assert response.status_code == 201, response.text
    assert response.json() == {"couriers": [{"id": courier_id}]}

    # Добавляю заказы
    response = requests.post(base_url + "/orders", json=order)
    assert response.status_code == 201, response.text
    assert response.json() == {"orders": [{"id": order_id}]}

    # Вешаю заказы на курьера
    response = requests.post(base_url + "/orders/assign", json={"courier_id": courier_id})
    assert response.status_code == 200, response.text
    assert response.json()["orders"][0]["id"] == order_id
