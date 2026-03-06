from __future__ import annotations

import math

from cfs.errors import ValidationError
from cfs.models.normal_shock import (
    downstream_mach,
    static_pressure_ratio,
    static_density_ratio,
    static_temperature_ratio,
    total_pressure_ratio,
)


def _validate_gamma(gamma: float) -> None:
    if gamma <= 1.0:
        raise ValidationError("gamma must be > 1.")


def _validate_upstream_mach(M1: float) -> None:
    if M1 <= 1.0:
        raise ValidationError("Oblique shock requires upstream Mach number M1 > 1.")


def _validate_theta(theta_rad: float) -> None:
    if theta_rad < 0.0:
        raise ValidationError("Deflection angle theta must be >= 0.")


def mach_angle(M1: float) -> float:
    """
    Return Mach angle mu in radians.
    """
    _validate_upstream_mach(M1)
    return math.asin(1.0 / M1)


def theta_from_beta(M1: float, beta_rad: float, gamma: float = 1.4) -> float:
    """
    Return theta (radians) from given M1 and beta using the theta-beta-M relation.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    mu = mach_angle(M1)
    if not (mu < beta_rad < 0.5 * math.pi):
        raise ValidationError("beta must satisfy mu < beta < pi/2.")

    sin_beta = math.sin(beta_rad)
    cos_2beta = math.cos(2.0 * beta_rad)
    cot_beta = 1.0 / math.tan(beta_rad)

    numerator = 2.0 * cot_beta * (M1**2 * sin_beta**2 - 1.0)
    denominator = M1**2 * (gamma + cos_2beta) + 2.0

    tan_theta = numerator / denominator

    if tan_theta < 0.0:
        raise ValidationError("Computed tan(theta) < 0; invalid attached oblique shock state.")

    return math.atan(tan_theta)


def theta_max(M1: float, gamma: float = 1.4) -> float:
    """
    Return maximum attached deflection angle theta_max in radians.

    Uses a dense scan over beta, which is simple and robust for MVP.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    mu = mach_angle(M1)
    beta_min = mu + 1e-6
    beta_max = 0.5 * math.pi - 1e-6

    n = 2000
    best_theta = -1.0

    for i in range(n + 1):
        beta = beta_min + (beta_max - beta_min) * i / n
        try:
            theta = theta_from_beta(M1, beta, gamma)
        except ValidationError:
            continue
        if theta > best_theta:
            best_theta = theta

    if best_theta <= 0.0:
        raise ValidationError("Could not determine theta_max.")

    return best_theta


def shock_angle(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    """
    Solve shock angle beta (radians) from M1, theta, gamma, and branch.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)
    _validate_theta(theta_rad)

    if branch not in {"weak", "strong"}:
        raise ValidationError("branch must be 'weak' or 'strong'.")

    if math.isclose(theta_rad, 0.0, rel_tol=0.0, abs_tol=1e-14):
        return mach_angle(M1)

    tmax = theta_max(M1, gamma)
    if theta_rad > tmax:
        raise ValidationError(
            f"No attached oblique shock solution: theta exceeds theta_max "
            f"({math.degrees(tmax):.6f} deg)."
        )

    mu = mach_angle(M1)
    beta_min = mu + 1e-6
    beta_max = 0.5 * math.pi - 1e-6

    # Find beta_peak where theta is maximum.
    n = 2000
    beta_peak = beta_min
    best_theta = -1.0
    for i in range(n + 1):
        beta = beta_min + (beta_max - beta_min) * i / n
        try:
            theta = theta_from_beta(M1, beta, gamma)
        except ValidationError:
            continue
        if theta > best_theta:
            best_theta = theta
            beta_peak = beta

    def f(beta: float) -> float:
        return theta_from_beta(M1, beta, gamma) - theta_rad

    if branch == "weak":
        lo, hi = beta_min, beta_peak - 1e-8
    else:
        lo, hi = beta_peak + 1e-8, beta_max

    f_lo = f(lo)
    f_hi = f(hi)

    if f_lo * f_hi > 0:
        raise ValidationError("Could not bracket oblique shock solution.")

    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)

        if abs(f_mid) < 1e-12:
            return mid

        if f_lo * f_mid < 0:
            hi = mid
            f_hi = f_mid
        else:
            lo = mid
            f_lo = f_mid

    return 0.5 * (lo + hi)


def normal_mach_upstream(M1: float, beta_rad: float) -> float:
    """
    Return upstream normal Mach number M_n1.
    """
    _validate_upstream_mach(M1)
    return M1 * math.sin(beta_rad)


def normal_mach_downstream(M1: float, beta_rad: float, gamma: float = 1.4) -> float:
    """
    Return downstream normal Mach number M_n2.
    """
    Mn1 = normal_mach_upstream(M1, beta_rad)
    return downstream_mach(Mn1, gamma)


def downstream_mach_oblique(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    """
    Return downstream Mach number M2 for an oblique shock.
    """
    beta = shock_angle(M1, theta_rad, gamma, branch)
    Mn2 = normal_mach_downstream(M1, beta, gamma)
    return Mn2 / math.sin(beta - theta_rad)


def static_pressure_ratio_oblique(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    beta = shock_angle(M1, theta_rad, gamma, branch)
    Mn1 = normal_mach_upstream(M1, beta)
    return static_pressure_ratio(Mn1, gamma)


def static_density_ratio_oblique(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    beta = shock_angle(M1, theta_rad, gamma, branch)
    Mn1 = normal_mach_upstream(M1, beta)
    return static_density_ratio(Mn1, gamma)


def static_temperature_ratio_oblique(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    beta = shock_angle(M1, theta_rad, gamma, branch)
    Mn1 = normal_mach_upstream(M1, beta)
    return static_temperature_ratio(Mn1, gamma)


def total_pressure_ratio_oblique(
    M1: float,
    theta_rad: float,
    gamma: float = 1.4,
    branch: str = "weak",
) -> float:
    beta = shock_angle(M1, theta_rad, gamma, branch)
    Mn1 = normal_mach_upstream(M1, beta)
    return total_pressure_ratio(Mn1, gamma)