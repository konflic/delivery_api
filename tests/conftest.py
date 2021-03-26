import pytest
import requests


def pytest_addoption(parser):
    parser.addoption("--url", action="store", default=f"http://127.0.0.1:5000")


@pytest.fixture
def base_url(request):
    return request.config.getoption("--url")


@pytest.fixture
def api_client(base_url):
    class ApiClient:

        def __init__(self, base_url):
            self.url = base_url

        def get_courier_data(self, courier_id):
            return requests.get(f"{base_url}/couriers/{courier_id}")

        def update_courier(self, courier_id: int, update_data: dict):
            return requests.patch(f"{base_url}/couriers/{courier_id}", json=update_data)

        def add_couriers(self, couriers_data: dict):
            return requests.post(f"{base_url}/couriers", json=couriers_data)

        def add_orders(self, orders_data: dict):
            return requests.post(base_url + "/orders", json=orders_data)

        def assign_orders(self, courier_id):
            return requests.post(f"{base_url}/orders/assign", json={"courier_id": courier_id})

        def complete_orders(self, complete_data: dict):
            return requests.post(f"{base_url}/orders/complete", json=complete_data)

    return ApiClient(base_url)
