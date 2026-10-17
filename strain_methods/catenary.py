"""
strain_methods/catenary.py

Catenary method (John, 1987) for the tensile strain developed in the
geosynthetic reinforcement.

Source: supplied PDF, p.361, Eq. (10.23):

    epsilon_g = 0.5*sqrt(1 + 16*dS_g^2/(s-a)^2)
                + (s-a)/(8*dS_g) * ln( 4*dS_g/(s-a) + sqrt(1+16*dS_g^2/(s-a)^2) )
                - 1

This is an alternative to the Giroud simplified formula (strain_methods/
giroud.py) and to the parabolic method (strain_methods/parabolic.py).
Only ONE strain method should be used per calculation run, matching the
method the user selects in the GUI.
"""

import math


def strain(dS_g, s, a):
    span = s - a
    ratio = dS_g / span
    sqrt_term = math.sqrt(1 + 16 * ratio ** 2)
    eps = 0.5 * sqrt_term + (span / (8 * dS_g)) * math.log(4 * ratio + sqrt_term) - 1
    return eps


def run(inputs):
    eps = strain(inputs["dS_g"], inputs["s"], inputs["a"])
    step = {
        "title": "Tensile strain in geosynthetic (Catenary method)",
        "symbol": "epsilon_g",
        "equation": (
            "epsilon_g = 0.5*sqrt(1+16 dS_g^2/(s-a)^2) + "
            "(s-a)/(8 dS_g) * ln(4 dS_g/(s-a) + sqrt(1+16 dS_g^2/(s-a)^2)) - 1"
        ),
        "substitution": (
            f"span = s-a = {inputs['s']}-{inputs['a']:.4f}; "
            f"ratio = dS_g/span = {inputs['dS_g']}/{inputs['s']-inputs['a']:.4f}; "
            f"epsilon_g = 0.5*sqrt(1+16*ratio^2) + "
            f"span/(8*dS_g)*ln(4*ratio+sqrt(1+16*ratio^2)) - 1 = {eps:.6f}"
        ),
        "result": eps,
        "unit": "(fraction; multiply by 100 for %)",
        "source": "Supplied PDF, p.361, Eq. (10.23) (John, 1987)",
    }
    return {"method": "Catenary (John, 1987)", "epsilon_g": eps, "steps": [step]}
