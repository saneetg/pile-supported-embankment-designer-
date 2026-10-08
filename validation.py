"""
validation.py

Basic engineering input validation for the Pile-Supported Embankment Designer.
Every check here raises a ValidationError with a plain-English message so the
GUI can show something a user understands (never a Python traceback).
"""


class ValidationError(Exception):
    """Raised when an input value fails a sanity check."""
    pass


def require_positive(value, name):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value <= 0:
        raise ValidationError(f"{name} must be greater than zero.")
    return value


def require_nonnegative(value, name):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value < 0:
        raise ValidationError(f"{name} cannot be negative.")
    return value


def require_range(value, name, low, high):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value < low or value > high:
        raise ValidationError(f"{name} must be between {low} and {high}.")
    return value


def validate_common_inputs(inp):
    """
    inp: dict of raw input values (floats already parsed).
    Raises ValidationError on the first problem found.
    This covers checks that apply to BOTH design methods (Terzaghi and
    Hewlett & Randolph), since both share embankment / platform / column /
    soil / loading inputs (Design Parameters, PDF p.362).
    """

    require_positive(inp["H"], "Embankment height (H)")
    require_nonnegative(inp["gamma2"], "Embankment fill unit weight (gamma2)")
    require_range(inp["phi2"], "Embankment fill friction angle (phi2)", 0, 60)

    require_positive(inp["H1"], "Load transfer platform thickness (H1)")
    require_nonnegative(inp["gamma1"], "Platform fill unit weight (gamma1)")
    require_range(inp["phi1"], "Platform fill friction angle (phi1)", 0, 60)

    require_positive(inp["d"], "Column diameter (d)")
    require_positive(inp["s"], "Column spacing (s)")
    if inp["s"] <= inp["d"]:
        raise ValidationError(
            "Column spacing (s) must be greater than column diameter (d)."
        )

    require_positive(inp["Ec"], "Column modulus (Ec)")
    require_positive(inp["Es"], "Soil modulus (Es)")
    require_positive(inp["cu"], "Undrained shear strength (cu)")

    require_nonnegative(inp["p"], "Surcharge (p)")

    require_positive(inp["dS_allow"], "Allowable differential settlement")

    if inp["K1"] <= 0:
        raise ValidationError("K1 (platform lateral earth pressure coefficient) must be greater than zero.")
    if inp["K2"] <= 0:
        raise ValidationError("K2 (embankment lateral earth pressure coefficient) must be greater than zero.")

    if inp["n"] <= 1:
        raise ValidationError(
            "Stress concentration ratio (n) must be greater than 1 "
            "(n=1 implies no stress concentration on columns)."
        )

    require_positive(inp["FS"], "Factor of safety (FS)")
    if inp.get("Hcr_method") == "user_input":
        require_positive(inp.get("Hcr_value"), "Critical height (Hcr)")
    else:
        require_positive(inp.get("a"), "Square column width (a)")
        if inp.get("Hcr_condition") == "Filz et al. (2015)":
            require_positive(inp.get("s_prime"), "Distance from column edge to array centroid (s')")
    if inp.get("Hcr_method") == "table_10_4":
        require_positive(inp.get("Hcr_factor"), "Table 10.4 critical-height factor")
    elif inp.get("Hcr_method") == "user_input":
        require_positive(inp.get("Hcr_value"), "Critical height (Hcr)")


def validate_hewlett_randolph_inputs(inp):
    """Extra check needed only by the Hewlett & Randolph method (Kp)."""
    if inp.get("Kp") is None:
        raise ValidationError(
            "Kp (coefficient of passive earth pressure of embankment fill) "
            "must be entered for the Hewlett and Randolph method. "
            "This value is not given a default in the source document."
        )
    require_positive(inp["Kp"], "Kp (coefficient of passive earth pressure)")
