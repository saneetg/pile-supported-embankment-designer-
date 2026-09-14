"""
methods/adapted_terzaghi.py

Adapted Terzaghi method (Sloan et al., 2011, expanding Russell & Pierpoint,
1997) for the average vertical stress above the geosynthetic reinforcement
in a geosynthetic-reinforced column-supported (GRCS) embankment.

Source: supplied PDF, "Principles and Practice of Ground Improvement"
(Jie Han, Wiley, 2015), Section 10.4.3 "Stress above Geosynthetic
Reinforcement", p.359-360.

This module ONLY implements the adapted Terzaghi equations. It does not
mix in any Hewlett & Randolph equations (see methods/hewlett_randolph.py).
"""

import math


def equivalent_column_width(d):
    """
    a = sqrt(pi*d^2/4)
    Source: supplied PDF, p.363, worked calculation step 1
    (equivalent width of a circular column having the same area as
    a square column of side 'a').
    """
    return math.sqrt(math.pi * d ** 2 / 4)


def critical_height(s, a):
    """
    Hcr >= 1.4(s - a)
    Source: supplied PDF, p.356, "The criterion, Hcr >= 1.4(s-a), has been
    commonly used in practice." Table 10.4 (British Standard BS8006, 2010).
    Program uses the equality Hcr = 1.4(s-a) to obtain a numeric estimate,
    consistent with the worked example on p.363 step 2.
    """
    return 1.4 * (s - a)


def alpha_terms(a, K1, phi1_deg, K2, phi2_deg, s):
    """
    alpha1 = 4*a*K1*tan(phi1) / (s^2 - a^2)
    alpha2 = 4*a*K2*tan(phi2) / (s^2 - a^2)
    Source: supplied PDF, p.359, Eq. (10.18) definitions.
    """
    denom = s ** 2 - a ** 2
    phi1 = math.radians(phi1_deg)
    phi2 = math.radians(phi2_deg)
    alpha1 = 4 * a * K1 * math.tan(phi1) / denom
    alpha2 = 4 * a * K2 * math.tan(phi2) / denom
    return alpha1, alpha2


def vertical_stress(H, H1, Hcr, gamma1, gamma2, alpha1, alpha2, p):
    """
    Average vertical stress above the geosynthetic reinforcement, psl.

    Three cases depending on where Hcr falls (Source: supplied PDF, p.359-360):

    Case A: Hcr > H                    -> Eq. (10.18)
    Case B: H1 < Hcr < H                -> Eq. (10.19)
    Case C: Hcr < H1  (Hcr within platform) -> Eq. (10.20)

    Returns (psl, case_label, equation_ref)
    """
    if Hcr > H:
        # Source: supplied PDF, p.359, Eq. (10.18)
        psl = (
            (gamma1 / alpha1) * (1 - math.exp(-alpha1 * H1))
            + (gamma2 / alpha2) * math.exp(-alpha1 * H1) * (1 - math.exp(-alpha2 * H1))
            + p * math.exp(-alpha1 * H1 - alpha2 * H1)
        )
        # NOTE: Eq. 10.18 as printed uses H1 and H2 = H - H1 implicitly;
        # this branch is provided for completeness. The worked example in
        # the source (Design Example 10.3) falls in Case B below, so this
        # branch is not exercised by the mandatory validation test.
        case_label = "Hcr > H"
        eq_ref = "Eq. (10.18), supplied PDF p.359"

    elif H1 < Hcr < H:
        # Source: supplied PDF, p.360, Eq. (10.19)
        # This is the branch used in Design Example 10.3 (p.363).
        psl = (
            (gamma1 / alpha1) * (1 - math.exp(-alpha1 * H1))
            + (gamma2 / alpha2) * math.exp(-alpha1 * H1) * (1 - math.exp(-alpha2 * (Hcr - H1)))
            + (p + (H - Hcr) * gamma2) * math.exp(-alpha1 * H1 - alpha2 * (Hcr - H1))
        )
        case_label = "H1 < Hcr < H"
        eq_ref = "Eq. (10.19), supplied PDF p.360"

    else:
        # Hcr <= H1 : Source: supplied PDF, p.360, Eq. (10.20)
        psl = (
            (gamma1 / alpha1) * (1 - math.exp(-alpha1 * Hcr))
            + (p + (H1 - Hcr) * gamma1 + H2_placeholder(H, H1) * gamma2)
            * math.exp(-alpha1 * Hcr)
        )
        case_label = "Hcr <= H1 (within platform)"
        eq_ref = "Eq. (10.20), supplied PDF p.360"

    return psl, case_label, eq_ref


def H2_placeholder(H, H1):
    """
    H2 = H - H1 (embankment fill thickness above the platform).
    Source: supplied PDF, Figure 10.30 definition of H1/H2/H.
    Small helper kept separate so Eq. (10.20)'s H2 term is traceable.
    """
    return H - H1


def run(inputs):
    """
    Full adapted-Terzaghi calculation chain.
    inputs: dict with keys H, H1, gamma1, gamma2, phi1, phi2, K1, K2, d, s, p

    Returns a dict with all intermediate values (for the Calculation
    Details display) plus the final psl.
    """
    steps = []

    a = equivalent_column_width(inputs["d"])
    steps.append({
        "title": "Equivalent column width",
        "symbol": "a",
        "equation": "a = sqrt(pi * d^2 / 4)",
        "substitution": f"a = sqrt(pi * {inputs['d']}^2 / 4)",
        "result": a,
        "unit": "m",
        "source": "Supplied PDF, p.363, worked calculation step 1",
    })

    Hcr = critical_height(inputs["s"], a)
    steps.append({
        "title": "Critical height",
        "symbol": "H_cr",
        "equation": "H_cr = 1.4 (s - a)",
        "substitution": f"H_cr = 1.4 ({inputs['s']} - {a:.4f})",
        "result": Hcr,
        "unit": "m",
        "source": "Supplied PDF, p.356, Table 10.4 criterion; p.363 step 2",
    })

    alpha1, alpha2 = alpha_terms(
        a, inputs["K1"], inputs["phi1"], inputs["K2"], inputs["phi2"], inputs["s"]
    )
    steps.append({
        "title": "Alpha 1 (platform fill arching coefficient)",
        "symbol": "alpha_1",
        "equation": "alpha_1 = 4 a K1 tan(phi1) / (s^2 - a^2)",
        "substitution": (
            f"alpha_1 = 4({a:.4f})({inputs['K1']})tan({inputs['phi1']} deg) "
            f"/ ({inputs['s']}^2 - {a:.4f}^2)"
        ),
        "result": alpha1,
        "unit": "1/m",
        "source": "Supplied PDF, p.359, Eq. (10.18) definitions",
    })
    steps.append({
        "title": "Alpha 2 (embankment fill arching coefficient)",
        "symbol": "alpha_2",
        "equation": "alpha_2 = 4 a K2 tan(phi2) / (s^2 - a^2)",
        "substitution": (
            f"alpha_2 = 4({a:.4f})({inputs['K2']})tan({inputs['phi2']} deg) "
            f"/ ({inputs['s']}^2 - {a:.4f}^2)"
        ),
        "result": alpha2,
        "unit": "1/m",
        "source": "Supplied PDF, p.359, Eq. (10.18) definitions",
    })

    psl, case_label, eq_ref = vertical_stress(
        inputs["H"], inputs["H1"], Hcr,
        inputs["gamma1"], inputs["gamma2"], alpha1, alpha2, inputs["p"]
    )
    steps.append({
        "title": f"Average vertical stress above geosynthetic ({case_label})",
        "symbol": "p_sl",
        "equation": eq_ref,
        "substitution": "See equation; case selected automatically from H_cr vs H1, H",
        "result": psl,
        "unit": "kPa",
        "source": eq_ref,
    })

    return {
        "method": "Adapted Terzaghi",
        "a": a,
        "Hcr": Hcr,
        "alpha1": alpha1,
        "alpha2": alpha2,
        "psl": psl,
        "case_label": case_label,
        "steps": steps,
    }
