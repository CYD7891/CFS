from __future__ import annotations

import math

from cfs.errors import ValidationError


def _validate_gamma(gamma: float) -> None:
    if gamma <= 1.0:
        raise ValidationError("gamma must be > 1.")


def _validate_upstream_mach(M1: float) -> None:
    if M1 <= 1.0:
        raise ValidationError("Normal shock requires upstream Mach number M1 > 1.")


def downstream_mach(M1: float, gamma: float = 1.4) -> float:
    """
    Return downstream Mach number M2 for a normal shock.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    numerator = 1.0 + 0.5 * (gamma - 1.0) * M1**2
    denominator = gamma * M1**2 - 0.5 * (gamma - 1.0)
    return math.sqrt(numerator / denominator)


def static_pressure_ratio(M1: float, gamma: float = 1.4) -> float:
    """
    Return p2 / p1 across a normal shock.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    return 1.0 + (2.0 * gamma / (gamma + 1.0)) * (M1**2 - 1.0)


def static_density_ratio(M1: float, gamma: float = 1.4) -> float:
    """
    Return rho2 / rho1 across a normal shock.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    return ((gamma + 1.0) * M1**2) / ((gamma - 1.0) * M1**2 + 2.0)


def static_temperature_ratio(M1: float, gamma: float = 1.4) -> float:
    """
    Return T2 / T1 across a normal shock.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    return static_pressure_ratio(M1, gamma) / static_density_ratio(M1, gamma)


def total_pressure_ratio(M1: float, gamma: float = 1.4) -> float:
    """
    Return p02 / p01 across a normal shock.

    This should always be < 1 for a real shock.
    """
    _validate_gamma(gamma)
    _validate_upstream_mach(M1)

    M2 = downstream_mach(M1, gamma)

    p01_over_p1 = (1.0 + 0.5 * (gamma - 1.0) * M1**2) ** (gamma / (gamma - 1.0))
    p02_over_p2 = (1.0 + 0.5 * (gamma - 1.0) * M2**2) ** (gamma / (gamma - 1.0))
    p2_over_p1 = static_pressure_ratio(M1, gamma)

    return (p02_over_p2 * p2_over_p1) / p01_over_p1