"""
methods/hewlett_randolph.py

Hewlett and Randolph (1988) method for the average vertical stress above
the geosynthetic reinforcement in a geosynthetic-reinforced column-supported
(GRCS) embankment.

Source: supplied PDF, "Principles and Practice of Ground Improvement"
(Jie Han, Wiley, 2015), Section 10.4.3, p.360, "2. The Hewlett and Randolph
Method".

Hewlett and Randolph (1988) assumed the soil above the columns forms a
semispherical soil arch. The design considers possible failure of soil
arching either at the crown of the arch or at the top of the column.
The vertical stress above the reinforcement is the GREATER of the two.

This module ONLY implements the Hewlett & Randolph equations. It does not
mix in any adapted-Terzaghi equations (see methods/adapted_terzaghi.py).

NOTE: this method requires Kp (coefficient of passive earth pressure of the
embankment fill), which is NOT given a numeric value or default anywhere in
the supplied PDF excerpt. It must be supplied by the user.
"""

import math


def equivalent_column_width(d):
    """
    a = sqrt(pi*d^2/4)
    Same definition as used in the adapted Terzaghi method
    (Source: supplied PDF, p.363 worked step 1; Figure 10.30(b) geometry
    is shared by both methods).
    """
    return math.sqrt(math.pi * d ** 2 / 4)


def stress_at_crown(gamma_e, H, p, a, s, Kp):
    """
    Eq. (10.21), supplied PDF p.360.

    p_sl (crown) = (gamma_e*H + p) * { (1 - a/s)^(2(Kp-1))
                    * [1 - (s/sqrt(2)H) * (2Kp-2)/(2Kp-3)]
                    + (s-a)/(sqrt(2)H) * (2Kp-2)/(2Kp-3) }
    """
    term_a = (1 - a / s) ** (2 * (Kp - 1))
    bracket_inner = 1 - (s / (math.sqrt(2) * H)) * ((2 * Kp - 2) / (2 * Kp - 3))
    term_b = ((s - a) / (math.sqrt(2) * H)) * ((2 * Kp - 2) / (2 * Kp - 3))
    psl_crown = (gamma_e * H + p) * (term_a * bracket_inner + term_b)
    return psl_crown


def stress_at_column_top(gamma_e, H, p, a, s, Kp):
    """
    Eq. (10.22), supplied PDF p.360.

    p_sl (column top) = (gamma_e*H + p) /
        { (2Kp/(Kp+1)) * [ (1-a/s)^(1-Kp) - (1-a/s)(1+(a/s)Kp) ]
          + (1 - a^2/s^2) }
    """
    ratio = a / s
    numerator = gamma_e * H + p
    bracket = (2 * Kp / (Kp + 1)) * (
        (1 - ratio) ** (1 - Kp) - (1 - ratio) * (1 + ratio * Kp)
    ) + (1 - ratio ** 2)
    psl_top = numerator / bracket
    return psl_top


def run(inputs):
    """
    Full Hewlett & Randolph calculation chain.

    inputs: dict with keys H, gamma_e (weighted/embankment unit weight used
    for this method), p, d, s, Kp.

    Returns dict with intermediate values and final psl (max of the two).
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
        "source": "Supplied PDF, p.363 worked step 1 (shared geometry definition)",
    })

    psl_crown = stress_at_crown(inputs["gamma_e"], inputs["H"], inputs["p"], a, inputs["s"], inputs["Kp"])
    steps.append({
        "title": "Vertical stress at crown of arch",
        "symbol": "p_sl (crown)",
        "equation": "Eq. (10.21), supplied PDF p.360",
        "substitution": "See Eq. (10.21)",
        "result": psl_crown,
        "unit": "kPa",
        "source": "Supplied PDF, p.360, Eq. (10.21)",
    })

    psl_top = stress_at_column_top(inputs["gamma_e"], inputs["H"], inputs["p"], a, inputs["s"], inputs["Kp"])
    steps.append({
        "title": "Vertical stress at top of column",
        "symbol": "p_sl (column top)",
        "equation": "Eq. (10.22), supplied PDF p.360",
        "substitution": "See Eq. (10.22)",
        "result": psl_top,
        "unit": "kPa",
        "source": "Supplied PDF, p.360, Eq. (10.22)",
    })

    psl = max(psl_crown, psl_top)
    governing = "crown" if psl_crown >= psl_top else "column top"
    steps.append({
        "title": "Governing vertical stress above geosynthetic",
        "symbol": "p_sl",
        "equation": "p_sl = max(p_sl(crown), p_sl(column top))",
        "substitution": f"p_sl = max({psl_crown:.3f}, {psl_top:.3f})",
        "result": psl,
        "unit": "kPa",
        "source": "Supplied PDF, p.360 (\"the greater of the values\")",
    })

    return {
        "method": "Hewlett and Randolph",
        "a": a,
        "psl_crown": psl_crown,
        "psl_top": psl_top,
        "psl": psl,
        "governing": governing,
        "steps": steps,
    }
