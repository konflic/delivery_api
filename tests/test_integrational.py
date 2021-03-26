import requests
import pytest
import random
import arrow

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
def test_assign_order(api_client):
    """Распределение заказа курьеру"""
    courier_id = random.randint(555555, 666666)
    order_id = random.randint(555555, 666666)
    courier = manual_courier(courier_id, "car", [999], ["10:00-18:00"])
    order = manual_order(order_id, 49.0, 999, ["11:00-15:00"])

    # TODO: Копипаста
    # Добавляю курьера
    response = api_client.add_couriers(couriers_data=courier)
    assert response.status_code == 201, response.text
    assert response.json() == {"couriers": [{"id": courier_id}]}

    # Добавляю заказы
    response = api_client.add_orders(orders_data=order)
    assert response.status_code == 201, response.text
    assert response.json() == {"orders": [{"id": order_id}]}

    # Вешаю заказы на курьера
    response = api_client.assign_orders(courier_id=courier_id)
    assert response.status_code == 200, response.text
    assert response.json()["orders"][0]["id"] == order_id


@pytest.mark.api
def test_valid_complete_order(api_client):
    """Распределение заказа курьеру"""
    courier_id = random.randint(3333333, 4444444)
    order_id = random.randint(3333333, 4444444)
    courier = manual_courier(courier_id, "car", [999], ["10:00-18:00"])
    order = manual_order(order_id, 49.0, 999, ["11:00-15:00"])

    # TODO: Копипаста
    # Добавляю курьера
    response = api_client.add_couriers(couriers_data=courier)
    assert response.status_code == 201, response.text
    assert response.json() == {"couriers": [{"id": courier_id}]}

    # Добавляю заказы
    response = api_client.add_orders(orders_data=order)
    assert response.status_code == 201, response.text
    assert response.json() == {"orders": [{"id": order_id}]}

    # Вешаю заказы на курьера
    response = api_client.assign_orders(courier_id=courier_id)
    assert response.status_code == 200, response.text
    assert response.json()["orders"][0]["id"] == order_id

    # Завершаю заказ выданный курьеру
    c_data = {
        "courier_id": courier_id,
        "order_id": order_id,
        "complete_time": arrow.utcnow().shift(hours=1).for_json()
    }
    response = api_client.complete_orders(complete_data=c_data)
    assert response.status_code == 200, f"Ошибка завершения заказа: {response.text}"
    assert response.json()["order_id"] == order_id


@pytest.mark.api
def test_assign_wrong_courier_id_order(base_url):
    """Проверка передачи не существующего id курьера"""
    response = requests.post(base_url + "/orders/assign", json={"courier_id": "-1"})
    assert response.status_code == 400, response.text


@pytest.mark.api
@pytest.mark.parametrize(
    "field,new_data", [
        ("working_hours", ["00:00-20:00"]),
        ("regions", [100, 150, 1]),
        ("courier_type", "bike")
    ])
def test_valid_courier_update(api_client, field, new_data):
    """Валидное обновление данных курьера"""
    courier_id = random.randint(888888, 999999)
    courier_data = manual_courier(
        courier_id=courier_id,
        courier_type="car",
        regions=[999],
        working_hours=["10:00-18:00"]
    )

    response = api_client.add_couriers(couriers_data=courier_data)
    assert response.status_code == 201, f"Ошибка добавления курьеров: {response.text}"

    response = api_client.update_courier(courier_id, {field: new_data})
    updated_data = api_client.get_courier_data(courier_id)

    assert response.status_code == 200, f"Ошибка обновления курьера: {response.text}"
    assert updated_data.json()[field] == new_data, f"Ошибка обновления курьера: {updated_data.text}"


@pytest.mark.api
@pytest.mark.parametrize(
    "field,new_data", [
        ("no_field", ["00:00-20:00"]),
        ("courier_id", 232323),
        ("", [100, 150, 1]),
    ])
def test_invalid_courier_update(api_client, field, new_data):
    """Невалидное обновление данных курьера"""
    courier_id = random.randint(888888, 999999)
    courier_data = manual_courier(
        courier_id=courier_id,
        courier_type="car",
        regions=[999],
        working_hours=["10:00-18:00"]
    )

    response = api_client.add_couriers(couriers_data=courier_data)
    assert response.status_code == 201, f"Ошибка добавления курьеров: {response.text}"

    response = api_client.update_courier(courier_id, {field: new_data})
    assert response.status_code == 400, f"Неверный код ответа при неправильном поле запроса: {response.text}"
