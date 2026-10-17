"""Table 10.4 suggested critical-height conditions."""

METHODS = (
    "Hewlett and Randolph (1988)",
    "Han and Gabr (2002)",
    "Chen et al. (2008a)",
    "Chen et al. (2010)",
    "British Standard BS8006 (2010)",
    "Filz et al. (2015)",
)
CHEN_2008_FACTORS = (1.4, 1.5, 1.6)
# Chen et al. (2010): Hcr >= (1.1 to 1.5)(s-a).
CHEN_2010_FACTORS = (1.1, 1.2, 1.3, 1.4, 1.5)


def _validate_spacing_width(s, a):
    if s <= 0:
        raise ValueError("Column spacing s must be greater than zero.")
    if a < 0:
        raise ValueError("Square column width a cannot be negative.")
    if s <= a:
        raise ValueError("Column spacing s must be greater than square column width a.")


def _validate_positive(value, label):
    if value <= 0:
        raise ValueError(f"{label} must be greater than zero.")


def calculate_hewlett_randolph(s, a):
    _validate_spacing_width(s, a)
    return _result("Hewlett and Randolph (1988)", "Hcr >= 1.0(s-a)", 1.0 * (s - a), {"s": s, "a": a}, 1.0)


def calculate_han_gabr(s, a):
    _validate_spacing_width(s, a)
    return _result("Han and Gabr (2002)", "Hcr >= 1.3(s-a)", 1.3 * (s - a), {"s": s, "a": a}, 1.3)


def calculate_chen_2008(s, a, factor=1.4):
    _validate_spacing_width(s, a)
    if factor not in CHEN_2008_FACTORS:
        raise ValueError("Chen et al. (2008a) factor must be 1.4, 1.5, or 1.6.")
    return _result("Chen et al. (2008a)", f"Hcr >= {factor:.1f}(s-a)", factor * (s - a), {"s": s, "a": a}, factor)


def calculate_chen_2010(s, a, factor=1.1):
    _validate_spacing_width(s, a)
    if factor not in CHEN_2010_FACTORS:
        raise ValueError("Chen et al. (2010) factor must be between 1.1 and 1.5.")
    return _result("Chen et al. (2010)", f"Hcr >= {factor:.1f}(s-a)", factor * (s - a), {"s": s, "a": a}, factor)


def calculate_bs8006(s, a):
    _validate_spacing_width(s, a)
    return _result("British Standard BS8006 (2010)", "Hcr >= 1.4(s-a)", 1.4 * (s - a), {"s": s, "a": a}, 1.4)


def calculate_filz(s_prime, d):
    _validate_positive(s_prime, "Distance s'")
    _validate_positive(d, "Column diameter d")
    return _result("Filz et al. (2015)", "Hcr >= 1.15s' + 1.44d", 1.15 * s_prime + 1.44 * d, {"s_prime": s_prime, "d": d}, None)


def calculate(method, *, s=None, a=None, d=None, s_prime=None, factor=None):
    if method == METHODS[0]:
        return calculate_hewlett_randolph(s, a)
    if method == METHODS[1]:
        return calculate_han_gabr(s, a)
    if method == METHODS[2]:
        return calculate_chen_2008(s, a, 1.4 if factor is None else factor)
    if method == METHODS[3]:
        return calculate_chen_2010(s, a, 1.1 if factor is None else factor)
    if method == METHODS[4]:
        return calculate_bs8006(s, a)
    if method == METHODS[5]:
        return calculate_filz(s_prime, d)
    raise ValueError(f"Unknown Table 10.4 critical-height method: {method}")


def _result(reference, formula, hcr, inputs, factor):
    return {
        "reference": reference,
        "formula": formula,
        "factor": factor,
        "hcr": hcr,
        "inputs": inputs,
        "condition": f"{formula}; applied Hcr = {hcr:.4f} m",
    }
