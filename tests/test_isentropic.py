import math
import pytest

from cfs.errors import ValidationError
from cfs.models.isentropic import (
    temperature_ratio,
    pressure_ratio,
    density_ratio,
    area_ratio,
    mach_from_area_ratio,
)


def test_isentropic_ratios_at_M2_gamma14():
    M = 2.0
    gamma = 1.4

    assert math.isclose(temperature_ratio(M, gamma), 0.5555555555555556, rel_tol=1e-10)
    assert math.isclose(pressure_ratio(M, gamma), 0.12780452546295096, rel_tol=1e-10)
    assert math.isclose(density_ratio(M, gamma), 0.23004814583331168, rel_tol=1e-10)
    assert math.isclose(area_ratio(M, gamma), 1.6875, rel_tol=1e-10)


def test_area_ratio_inverse_subsonic():
    gamma = 1.4
    M_true = 0.5
    aa = area_ratio(M_true, gamma)
    M_calc = mach_from_area_ratio(aa, gamma, branch="subsonic")
    assert math.isclose(M_calc, M_true, rel_tol=1e-9, abs_tol=1e-9)


def test_area_ratio_inverse_supersonic():
    gamma = 1.4
    M_true = 2.0
    aa = area_ratio(M_true, gamma)
    M_calc = mach_from_area_ratio(aa, gamma, branch="supersonic")
    assert math.isclose(M_calc, M_true, rel_tol=1e-9, abs_tol=1e-9)


def test_invalid_gamma():
    with pytest.raises(ValidationError):
        temperature_ratio(2.0, gamma=1.0)


def test_invalid_mach():
    with pytest.raises(ValidationError):
        pressure_ratio(0.0, gamma=1.4)


def test_invalid_area_ratio():
    with pytest.raises(ValidationError):
        mach_from_area_ratio(0.9, gamma=1.4, branch="subsonic")


def test_invalid_branch():
    with pytest.raises(ValidationError):
        mach_from_area_ratio(1.5, gamma=1.4, branch="banana")