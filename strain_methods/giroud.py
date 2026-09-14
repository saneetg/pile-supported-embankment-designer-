"""
strain_methods/giroud.py

Giroud (1995) simplified strain formula, valid for the parabolic method
when the deflection-to-clear-span ratio is small.

Source: supplied PDF, p.358 (Eq. 10.26 reference) and p.361, Eq. (10.26):

    epsilon_g = 8 * dS_g^2 / (3 * (s - a)^2)

This is the formula used in Design Example 10.3, step 5 (p.363).
"""


def strain(dS_g, s, a):
    """
    dS_g : maximum deflection of the geosynthetic reinforcement (m)
           (in the worked example, taken equal to the allowable
           differential settlement between columns).
    s    : column spacing (m)
    a    : equivalent column width (m)
    """
    return 8 * dS_g ** 2 / (3 * (s - a) ** 2)


def run(inputs):
    eps = strain(inputs["dS_g"], inputs["s"], inputs["a"])
    step = {
        "title": "Tensile strain in geosynthetic (Giroud simplified formula)",
        "symbol": "epsilon_g",
        "equation": "epsilon_g = 8 * dS_g^2 / (3 * (s - a)^2)",
        "substitution": f"epsilon_g = 8*({inputs['dS_g']})^2 / (3*({inputs['s']}-{inputs['a']:.4f})^2)",
        "result": eps,
        "unit": "(fraction; multiply by 100 for %)",
        "source": "Supplied PDF, p.361, Eq. (10.26)",
    }
    return {"method": "Giroud (simplified parabolic)", "epsilon_g": eps, "steps": [step]}
