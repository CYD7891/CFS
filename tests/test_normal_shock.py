import math
import pytest

from cfs.errors import ValidationError
from cfs.models.normal_shock import (
    downstream_mach,
    static_pressure_ratio,
    static_density_ratio,
    static_temperature_ratio,
    total_pressure_ratio,
)


def test_normal_shock_values_at_M1_2_gamma_14():
    M1 = 2.0
    gamma = 1.4

    assert math.isclose(downstream_mach(M1, gamma), 0.5773502691896257, rel_tol=1e-10)
    assert math.isclose(static_pressure_ratio(M1, gamma), 4.5, rel_tol=1e-10)
    assert math.isclose(static_density_ratio(M1, gamma), 2.666666666666667, rel_tol=1e-10)
    assert math.isclose(static_temperature_ratio(M1, gamma), 1.6875, rel_tol=1e-10)
    assert math.isclose(total_pressure_ratio(M1, gamma), 0.7208738614847454, rel_tol=1e-10)


def test_total_pressure_drops_across_shock():
    val = total_pressure_ratio(2.0, 1.4)
    assert val < 1.0


def test_temperature_ratio_is_pressure_over_density():
    M1 = 3.0
    gamma = 1.4
    lhs = static_temperature_ratio(M1, gamma)
    rhs = static_pressure_ratio(M1, gamma) / static_density_ratio(M1, gamma)
    assert math.isclose(lhs, rhs, rel_tol=1e-12)


def test_invalid_gamma():
    with pytest.raises(ValidationError):
        downstream_mach(2.0, gamma=1.0)


def test_invalid_upstream_mach_equal_one():
    with pytest.raises(ValidationError):
        static_pressure_ratio(1.0, gamma=1.4)


def test_invalid_upstream_mach_subsonic():
    with pytest.raises(ValidationError):
        total_pressure_ratio(0.8, gamma=1.4)