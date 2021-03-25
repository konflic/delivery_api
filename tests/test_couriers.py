import requests

from data_generators import random_couriers_sample


def test_add_duplicate_courier(base_url):
    sample = random_couriers_sample(2)
    response = requests.post(base_url + "/couriers", json=sample)
    assert response.status_code == 201, response.text
    response = requests.post(base_url + "/couriers", json=sample)
    assert response.status_code == 400, response.text
