import pytest

from unittest.mock import Mock, MagicMock
from controller.controllers import order_fits_courier, delivery_time_fits


@pytest.mark.parametrize(
    "courier,order", [
        (['11:35-14:05', '09:00-11:00'], ['09:00-18:00']),
        (['09:00-11:00'], ['10:30-10:50']),
        (['09:00-11:00'], ['08:00-10:00']),
        (['09:00-11:00'], ['08:05-12:00']),
    ], ids=[
        "left overlap",
        "inner overlap",
        "right overlap",
        "outer overlap"]
)
def test_intervals_has_overlaps(courier, order):
    """Тесты для пересекающихся интервалов"""
    assert delivery_time_fits(courier, order) == True


@pytest.mark.parametrize(
    "courier,order", [
        (['09:00-11:00'], ['08:30-08:45']),
        (['09:00-11:00'], ['11:05-12:00']),
        (['11:00-12:00', '14:00-15:00'], ['12:30-13:30'])
    ], ids=[
        "left shift",
        "right shift",
        "middle shift"]
)
def test_intervals_not_overlap(courier, order):
    """Тесты для не пересекающихся интервалов"""
    assert delivery_time_fits(courier, order) == False


@pytest.mark.parametrize(
    "courier_regions,order_region,courier_weight,order_weight,courier_wh,order_dh",
    [
        ((10, 20), 10, 10.0, 9.00, ["10:00-18:00"], ["10:00-18:00"]),
        ((1,), 1, 1.0, 0.5, ["9:00-10:00"], ["09:30-11:00"])
    ]
)
def test_order_fits_courier(courier_regions, order_region, courier_weight, order_weight, courier_wh, order_dh):
    courier = Mock()
    order = Mock()

    courier.get_regions = MagicMock(return_value=courier_regions)
    order.region_id = order_region
    courier.available_weight = courier_weight
    order.weight = order_weight
    courier.get_working_hours = MagicMock(return_value=courier_wh)
    order.get_delivery_hours = MagicMock(return_value=order_dh)

    assert order_fits_courier(courier, order) == True


@pytest.mark.parametrize(
    "courier_regions,order_region,courier_weight,order_weight,courier_wh,order_dh",
    [
        ((10, 20), 1, 10.0, 9.00, ["10:00-18:00"], ["10:00-18:00"]),
        ((1,), 1, 1.0, 1.5, ["9:00-10:00"], ["09:30-11:00"]),
        ((1,), 1, 1.5, 1.5, ["9:00-10:00"], ["11:00-11:30"]),
    ]
)
def test_order_not_fits_courier(courier_regions, order_region, courier_weight, order_weight, courier_wh, order_dh):
    courier = Mock()
    order = Mock()

    courier.get_regions = MagicMock(return_value=courier_regions)
    order.region_id = order_region
    courier.available_weight = courier_weight
    order.weight = order_weight
    courier.get_working_hours = MagicMock(return_value=courier_wh)
    order.get_delivery_hours = MagicMock(return_value=order_dh)

    assert order_fits_courier(courier, order) == False
