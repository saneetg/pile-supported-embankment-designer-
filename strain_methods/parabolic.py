"""
strain_methods/parabolic.py

Parabolic method (British Standard BS8006, 2010; Russell & Pierpoint, 1997)
for the tension in the geosynthetic reinforcement under a plane-strain,
square-column-pattern assumption, considering foundation soil resistance.

Source: supplied PDF, p.361, Eq. (10.25):

    T_g = [(p_sl - dsigma_s)*(s^2 - a^2) / (4a)] * sqrt(1 + 1/(6*epsilon_g))

This equation gives Tg directly as a function of epsilon_g (it is not a
strain formula on its own -- epsilon_g must be obtained independently,
e.g. from tension-strain compatibility with the reinforcement's stiffness
J, per the cubic in Tg given on p.361:

    96*Tg^3/a^2 - 6*(p_sl-dsigma_s)^2*(s^2-a^2)^2/a^2 * Tg
        - (p_sl-dsigma_s)^2*(s^2-a^2)^2/a^2 * J = 0

That cubic requires knowing J (reinforcement tensile stiffness), which is
not part of the worked Design Example 10.3 and is NOT implemented here to
avoid inventing an input the source example does not use. If the user
wants a rigid, fully consistent parabolic-method-with-compatibility
solution, J must be supplied and the cubic solved; this is left as a
documented gap (see README) rather than guessed at.

For consistency with the worked example, this module exposes only the
direct Tg formula (Eq. 10.25) taking epsilon_g as an input (e.g. computed
via the Giroud or Catenary strain formula).
"""

import math


def tension(psl, dsigma_s, s, a, epsilon_g):
    return ((psl - dsigma_s) * (s ** 2 - a ** 2) / (4 * a)) * math.sqrt(1 + 1 / (6 * epsilon_g))


def run(inputs):
    Tg = tension(inputs["psl"], inputs["dsigma_s"], inputs["s"], inputs["a"], inputs["epsilon_g"])
    step = {
        "title": "Tension in geosynthetic (Parabolic method, BS8006/Russell & Pierpoint)",
        "symbol": "T_g",
        "equation": "T_g = [(p_sl - dsigma_s)(s^2-a^2)/(4a)] * sqrt(1 + 1/(6*epsilon_g))",
        "substitution": (
            f"T_g = [({inputs['psl']:.3f}-{inputs['dsigma_s']:.3f})"
            f"({inputs['s']}^2-{inputs['a']:.4f}^2)/(4*{inputs['a']:.4f})] "
            f"* sqrt(1+1/(6*{inputs['epsilon_g']:.5f}))"
        ),
        "result": Tg,
        "unit": "kN/m",
        "source": "Supplied PDF, p.361, Eq. (10.25) — note: same numeric form as Eq. (10.24)",
    }
    return {"method": "Parabolic (BS8006 / Russell & Pierpoint)", "Tg": Tg, "steps": [step]}
