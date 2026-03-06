from __future__ import annotations

import math

from cfs.errors import ValidationError


def _validate_gamma(gamma: float) -> None:
    if gamma <= 1.0:
        raise ValidationError("gamma must be > 1.")


def _validate_mach(M: float) -> None:
    if M <= 0.0:
        raise ValidationError("Mach number must be > 0.")


def temperature_ratio(M: float, gamma: float = 1.4) -> float:
    """
    Return T / T0 for isentropic flow.
    """
    _validate_gamma(gamma)
    _validate_mach(M)
    return 1.0 / (1.0 + 0.5 * (gamma - 1.0) * M**2)


def pressure_ratio(M: float, gamma: float = 1.4) -> float:
    """
    Return p / p0 for isentropic flow.
    """
    _validate_gamma(gamma)
    _validate_mach(M)
    return temperature_ratio(M, gamma) ** (gamma / (gamma - 1.0))


def density_ratio(M: float, gamma: float = 1.4) -> float:
    """
    Return rho / rho0 for isentropic flow.
    """
    _validate_gamma(gamma)
    _validate_mach(M)
    return temperature_ratio(M, gamma) ** (1.0 / (gamma - 1.0))


def area_ratio(M: float, gamma: float = 1.4) -> float:
    """
    Return A / A* for isentropic quasi-1D flow.
    """
    _validate_gamma(gamma)
    _validate_mach(M)

    term1 = 1.0 / M
    term2 = (2.0 / (gamma + 1.0)) * (1.0 + 0.5 * (gamma - 1.0) * M**2)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return term1 * (term2 ** exponent)


def mach_from_area_ratio(AA_star: float, gamma: float = 1.4, branch: str = "subsonic") -> float:
    """
    Solve M from A/A* using bisection.
    branch: 'subsonic' or 'supersonic'
    """
    _validate_gamma(gamma)

    if AA_star < 1.0:
        raise ValidationError("A/A* must be >= 1 for isentropic flow.")

    if branch not in {"subsonic", "supersonic"}:
        raise ValidationError("branch must be 'subsonic' or 'supersonic'.")

    if math.isclose(AA_star, 1.0, rel_tol=0.0, abs_tol=1e-12):
        return 1.0

    def f(M: float) -> float:
        return area_ratio(M, gamma) - AA_star

    if branch == "subsonic":
        lo, hi = 1e-8, 1.0 - 1e-8
    else:
        lo, hi = 1.0 + 1e-8, 50.0

    f_lo = f(lo)
    f_hi = f(hi)

    if f_lo * f_hi > 0:
        raise ValidationError("Could not bracket Mach solution for the requested branch.")

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