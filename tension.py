"""
tension.py

Tension developed in the geosynthetic reinforcement, using the Catenary-
method tension formula (Eq. 10.24), which is the formula used in
Design Example 10.3's final step (p.363, step 6).

Source: supplied PDF, p.361, Eq. (10.24):

    T_g = [(p_sl - dsigma_s)(s^2 - a^2) / (4a)] * sqrt(1 + (s-a)^2/(16*dS_g^2))

Note: Eq. (10.24) is expressed in terms of the deflection dS_g, while
Eq. (10.25) (see strain_methods/parabolic.py) is the numerically identical
formula expressed in terms of strain epsilon_g. The PDF states: "When
Equation (10.26) is substituted into Equation (10.25), it yields the same
equation as Equation (10.24)." The worked example's final step (p.363,
step 6) is written using the epsilon_g form, so this module implements
that form (identical to strain_methods/parabolic.tension) for direct
comparability with the source.
"""

import math


def tension_from_strain(psl, dsigma_s, s, a, epsilon_g):
    """
    T_g = [(p_sl - dsigma_s)(s^2-a^2)/(4a)] * sqrt(1 + 1/(6*epsilon_g))
    Source: supplied PDF, p.363, worked step 6 (uses this exact form,
    algebraically identical to Eq. 10.24 substituted with Eq. 10.26 per
    the source's own remark on p.361).
    """
    return ((psl - dsigma_s) * (s ** 2 - a ** 2) / (4 * a)) * math.sqrt(1 + 1 / (6 * epsilon_g))


def run(inputs):
    Tg = tension_from_strain(
        inputs["psl"], inputs["dsigma_s"], inputs["s"], inputs["a"], inputs["epsilon_g"]
    )
    step = {
        "title": "Tension in geosynthetic reinforcement",
        "symbol": "T_g",
        "equation": "T_g = [(p_sl - delta_sigma_s)(s^2-a^2)/(4a)] * sqrt(1 + 1/(6*epsilon_g))",
        "substitution": (
            f"T_g = [({inputs['psl']:.3f}-{inputs['dsigma_s']:.3f})"
            f"({inputs['s']}^2-{inputs['a']:.4f}^2)/(4*{inputs['a']:.4f})] "
            f"* sqrt(1 + 1/(6*{inputs['epsilon_g']:.5f})) = {Tg:.3f} kN/m"
        ),
        "result": Tg,
        "unit": "kN/m",
        "source": "Supplied PDF, p.363, worked step 6 (Eq. 10.24 form)",
    }
    return {"Tg": Tg, "steps": [step]}
