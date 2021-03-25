import pytest

from controllers import delivery_time_fits


@pytest.mark.parametrize("courier,order,result", [
    (['11:35-14:05', '09:00-11:00'], ['09:00-18:00'], True),
    (['11:35-14:05', '09:00-11:00'], ['11:10-11:20'], False),
    (['09:00-11:00'], ['10:50-10:51'], True),
])
def test_intervals(courier, order, result):
    """Test for interval defining function"""
    assert delivery_time_fits(courier, order) == result
