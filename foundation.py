"""
foundation.py

Foundation soil resistance and bearing capacity check.
Shared by BOTH the adapted Terzaghi method and the Hewlett & Randolph
method, since foundation soil resistance is a separate step in the design
procedure that comes after the vertical-stress-above-geosynthetic
calculation (Source: supplied PDF, p.362, Design Procedure step 4).
"""

import math


def foundation_soil_resistance(gamma1, H1, gamma2, H2, a, s, n):
    """
    Eq. (10.27), supplied PDF p.361:

        dsigma_s = (gamma1*H1 + gamma2*H2) / (1 + (a^2/s^2)(n-1))

    Note: the equation's symbol definition in the text uses "gamma_e * H"
    (a single weighted embankment unit weight times total height), but the
    worked example (p.363, step 4) substitutes gamma1*H1 + gamma2*H2
    directly. This module follows the worked example's actual substitution.

    n = stress concentration ratio (assume 25 for rigid columns, per PDF
    p.361 note under Eq. 10.27).
    """
    numerator = gamma1 * H1 + gamma2 * H2
    denominator = 1 + (a ** 2 / s ** 2) * (n - 1)
    return numerator / denominator


def bearing_check(cu, FS, dsigma_s):
    """
    Eq. (10.28), supplied PDF p.361:

        q_ult = 5.14 * cu
        q_a   = q_ult / FS  >=  dsigma_s   (required)
    """
    q_ult = 5.14 * cu
    q_a = q_ult / FS
    passed = q_a >= dsigma_s
    return q_ult, q_a, passed


def run(inputs):
    """
    inputs: gamma1, H1, gamma2, H2, a, s, n, cu, FS, dsigma_target(optional
    for check) -- dsigma_s computed here.
    """
    steps = []

    dsigma_s = foundation_soil_resistance(
        inputs["gamma1"], inputs["H1"], inputs["gamma2"], inputs["H2"],
        inputs["a"], inputs["s"], inputs["n"]
    )
    steps.append({
        "title": "Foundation soil resistance",
        "symbol": "delta_sigma_s",
        "equation": "delta_sigma_s = (gamma1*H1 + gamma2*H2) / (1 + (a^2/s^2)(n-1))",
        "substitution": (
            f"delta_sigma_s = ({inputs['gamma1']}*{inputs['H1']} + "
            f"{inputs['gamma2']}*{inputs['H2']}) / "
            f"(1 + ({inputs['a']:.4f}^2/{inputs['s']}^2)*({inputs['n']}-1))"
        ),
        "result": dsigma_s,
        "unit": "kPa",
        "source": "Supplied PDF, p.361, Eq. (10.27)",
    })

    q_ult, q_a, passed = bearing_check(inputs["cu"], inputs["FS"], dsigma_s)
    steps.append({
        "title": "Ultimate bearing capacity of soft soil",
        "symbol": "q_ult",
        "equation": "q_ult = 5.14 * cu",
        "substitution": f"q_ult = 5.14 * {inputs['cu']}",
        "result": q_ult,
        "unit": "kPa",
        "source": "Supplied PDF, p.363, worked step 4 (standard undrained bearing capacity form used in source)",
    })
    steps.append({
        "title": "Allowable bearing capacity",
        "symbol": "q_a",
        "equation": "q_a = q_ult / FS",
        "substitution": f"q_a = {q_ult:.3f} / {inputs['FS']}",
        "result": q_a,
        "unit": "kPa",
        "source": "Supplied PDF, p.361, Eq. (10.28)",
    })
    steps.append({
        "title": "Foundation bearing check",
        "symbol": "q_a vs delta_sigma_s",
        "equation": "q_a >= delta_sigma_s  (required)",
        "substitution": f"{q_a:.3f} >= {dsigma_s:.3f} ?",
        "result": "PASS" if passed else "FAIL",
        "unit": "",
        "source": "Supplied PDF, p.361, Eq. (10.28)",
    })

    return {
        "dsigma_s": dsigma_s,
        "q_ult": q_ult,
        "q_a": q_a,
        "passed": passed,
        "steps": steps,
    }
