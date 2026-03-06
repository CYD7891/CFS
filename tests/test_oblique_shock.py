import math
import pytest

from cfs.errors import ValidationError
from cfs.models.oblique_shock import (
    mach_angle,
    theta_max,
    shock_angle,
    normal_mach_upstream,
    normal_mach_downstream,
    downstream_mach_oblique,
    static_pressure_ratio_oblique,
    static_density_ratio_oblique,
    static_temperature_ratio_oblique,
    total_pressure_ratio_oblique,
)


def test_mach_angle_for_M2():
    mu = mach_angle(2.0)
    assert math.isclose(mu, math.asin(0.5), rel_tol=1e-12)


def test_oblique_shock_weak_solution_M3_theta15():
    M1 = 3.0
    gamma = 1.4
    theta_deg = 15.0
    theta_rad = math.radians(theta_deg)

    beta = shock_angle(M1, theta_rad, gamma, branch="weak")
    Mn1 = normal_mach_upstream(M1, beta)
    Mn2 = normal_mach_downstream(M1, beta, gamma)
    M2 = downstream_mach_oblique(M1, theta_rad, gamma, branch="weak")
    p2_p1 = static_pressure_ratio_oblique(M1, theta_rad, gamma, branch="weak")
    rho2_rho1 = static_density_ratio_oblique(M1, theta_rad, gamma, branch="weak")
    T2_T1 = static_temperature_ratio_oblique(M1, theta_rad, gamma, branch="weak")
    p02_p01 = total_pressure_ratio_oblique(M1, theta_rad, gamma, branch="weak")

    assert math.isclose(math.degrees(beta), 32.24040018274467, rel_tol=1e-9)
    assert math.isclose(Mn1, 1.600418424201603, rel_tol=1e-9)
    assert math.isclose(Mn2, 0.668311462098548, rel_tol=1e-9)
    assert math.isclose(M2, 2.254902312264938, rel_tol=1e-9)
    assert math.isclose(p2_p1, 2.821562321277495, rel_tol=1e-9)
    assert math.isclose(rho2_rho1, 2.0324488190583185, rel_tol=1e-9)
    assert math.isclose(T2_T1, p2_p1 / rho2_rho1, rel_tol=1e-9)
    assert math.isclose(p02_p01, 0.895044329829952, rel_tol=1e-9)

    assert M2 > 1.0
    assert p02_p01 < 1.0


def test_strong_solution_has_larger_beta_and_subsonic_M2():
    M1 = 3.0
    gamma = 1.4
    theta_rad = math.radians(15.0)

    beta_weak = shock_angle(M1, theta_rad, gamma, branch="weak")
    beta_strong = shock_angle(M1, theta_rad, gamma, branch="strong")
    M2_strong = downstream_mach_oblique(M1, theta_rad, gamma, branch="strong")

    assert beta_strong > beta_weak
    assert M2_strong < 1.0


def test_theta_above_theta_max_raises():
    M1 = 2.0
    gamma = 1.4
    tmax = theta_max(M1, gamma)

    with pytest.raises(ValidationError):
        shock_angle(M1, tmax + math.radians(1.0), gamma, branch="weak")


def test_invalid_branch():
    with pytest.raises(ValidationError):
        shock_angle(3.0, math.radians(15.0), 1.4, branch="banana")


def test_invalid_upstream_mach():
    with pytest.raises(ValidationError):
        shock_angle(1.0, math.radians(10.0), 1.4, branch="weak")