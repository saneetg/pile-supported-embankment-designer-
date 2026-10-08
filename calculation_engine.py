"""
calculation_engine.py

Orchestrates the full design calculation chain:

    1. Validate inputs
    2. Modulus ratio check (Ec/Es > 100 -> full soil arching methods apply)
    3. Run selected stress method (adapted Terzaghi OR Hewlett & Randolph)
    4. Foundation soil resistance + bearing check
    5. Strain in geosynthetic (Giroud simplified OR Catenary)
    6. Tension in geosynthetic
    7. Assemble final results + calculation trace + design checks

This module does NOT contain any equations itself (other than the modulus
ratio, which is a simple ratio, and unit handling) -- all engineering
equations live in methods/, strain_methods/, foundation.py, and tension.py,
per the requested architecture (separate module per method).
"""

from validation import validate_common_inputs, validate_hewlett_randolph_inputs, ValidationError
from methods import adapted_terzaghi, hewlett_randolph
from methods import critical_height_conditions
from strain_methods import giroud, catenary
import foundation
import tension as tension_module


class CalculationError(Exception):
    """Raised when the calculation cannot proceed for an engineering reason
    (e.g. modulus ratio too low for the selected methods)."""
    pass


def modulus_ratio_check(Ec, Es):
    """
    Source: supplied PDF, p.363, worked step 1:
    "The modulus ratio of columns to soil is Ec/Es = 1000/4 = 250 > 100;
    therefore, the methods for fully mobilized soil arching can be used."

    Also Source: supplied PDF, p.360: "When the columns have a modulus
    more than 100 times that of the soft soil, they can be considered as
    rigid columns or rigid supports."
    """
    m = Ec / Es
    fully_mobilized = m > 100
    return m, fully_mobilized


def run_design(
    inputs, stress_method="adapted_terzaghi", strain_method="giroud",
    hcr_method="table_10_4",
):
    """
    inputs: dict of raw float inputs (already parsed from the GUI), keys:
        H, H1, gamma1, gamma2, phi1, phi2, K1, K2, d, s, p,
        Ec, Es, cu, FS, n, dS_allow, Kp (only needed for Hewlett & Randolph)

    stress_method: "adapted_terzaghi" or "hewlett_randolph"
    strain_method: "giroud" or "catenary"

    Returns a dict with:
        modulus_ratio, arching_ok,
        stress_result (full dict from the chosen method module),
        foundation_result,
        strain_result,
        tension_result,
        checks (list of dicts: {name, required, calculated, status}),
        all_steps (flattened ordered list for Calculation Details display)
    """
    all_steps = []
    inputs = dict(inputs)
    inputs.setdefault("Hcr_method", hcr_method)
    inputs.setdefault("Hcr_condition", critical_height_conditions.METHODS[0])
    inputs.setdefault("Hcr_factor", 1.4)
    inputs.setdefault("Hcr_value", None)
    hcr_method = inputs["Hcr_method"]

    # --- Step 0: validate ---
    validate_common_inputs(inputs)
    if stress_method == "hewlett_randolph":
        validate_hewlett_randolph_inputs(inputs)

    # --- Step 1: modulus ratio ---
    m, arching_ok = modulus_ratio_check(inputs["Ec"], inputs["Es"])
    all_steps.append({
        "title": "Modulus ratio of columns to soil",
        "symbol": "E_c / E_s",
        "equation": "m = Ec / Es",
        "substitution": f"m = {inputs['Ec']} / {inputs['Es']}",
        "result": m,
        "unit": "(dimensionless)",
        "source": "Supplied PDF, p.363, worked step 1",
    })
    if not arching_ok:
        raise CalculationError(
            f"Modulus ratio Ec/Es = {m:.1f} is not greater than 100. "
            "Per the source document (p.363), the adapted Terzaghi and "
            "Hewlett & Randolph methods assume fully mobilized soil arching "
            "and require Ec/Es > 100. This method should not be used, or "
            "should be used with great caution, for the entered conditions."
        )

    # --- Step 2: stress method ---
    if stress_method == "adapted_terzaghi":
        if hcr_method == "user_input":
            hcr_result = {
                "reference": "User input",
                "formula": "Hcr = user-entered value",
                "factor": None,
                "hcr": inputs["Hcr_value"],
                "inputs": {"H": inputs["H"]},
            }
        else:
            hcr_result = critical_height_conditions.calculate(
                inputs["Hcr_condition"],
                s=inputs["s"], a=inputs["a"], d=inputs["d"],
                s_prime=inputs.get("s_prime"),
                factor=inputs.get("Hcr_factor"),
            )
        stress_inputs = dict(inputs)
        stress_inputs["Hcr_value"] = hcr_result["hcr"]
        stress_result = adapted_terzaghi.run(stress_inputs, "user_input")
    elif stress_method == "hewlett_randolph":
        hr_inputs = dict(inputs)
        # Hewlett & Randolph uses a single embankment unit weight (gamma_e)
        # applied over the full height H (Eq. 10.21/10.22). The source does
        # not define how gamma_e is obtained when two fill layers exist for
        # this particular method's crown/column-top equations; as a
        # reasonable, explicitly labeled default we take gamma_e = gamma2
        # (embankment fill unit weight), since H in Eq. 10.21/10.22 spans
        # the embankment height above the platform in Figure 10.24(b).
        # ASSUMPTION NOT SPECIFIED IN SOURCE: gamma_e = gamma2 (embankment
        # fill unit weight) is used directly in Eq. (10.21)/(10.22).
        hr_inputs["gamma_e"] = inputs["gamma2"]
        stress_result = hewlett_randolph.run(hr_inputs)
    else:
        raise CalculationError(f"Unknown stress method: {stress_method}")

    all_steps.extend(stress_result["steps"])
    a = stress_result["a"]
    psl = stress_result["psl"]

    # --- Step 3: foundation soil resistance + bearing check ---
    H2 = inputs["H"] - inputs["H1"]
    foundation_inputs = dict(inputs)
    foundation_inputs["a"] = a
    foundation_inputs["H2"] = H2
    foundation_result = foundation.run(foundation_inputs)
    all_steps.extend(foundation_result["steps"])
    dsigma_s = foundation_result["dsigma_s"]

    # --- Step 4: strain in geosynthetic ---
    strain_inputs = {"dS_g": inputs["dS_allow"], "s": inputs["s"], "a": a}
    if strain_method == "giroud":
        strain_result = giroud.run(strain_inputs)
    elif strain_method == "catenary":
        strain_result = catenary.run(strain_inputs)
    else:
        raise CalculationError(f"Unknown strain method: {strain_method}")

    all_steps.extend(strain_result["steps"])
    epsilon_g = strain_result["epsilon_g"]

    # --- Step 5: tension in geosynthetic ---
    tension_inputs = {
        "psl": psl, "dsigma_s": dsigma_s, "s": inputs["s"], "a": a,
        "epsilon_g": epsilon_g,
    }
    tension_result = tension_module.run(tension_inputs)
    all_steps.extend(tension_result["steps"])
    Tg = tension_result["Tg"]

    # --- Design checks ---
    checks = [
        {
            "name": "Soil arching fully mobilized (Ec/Es > 100)",
            "required": "> 100",
            "calculated": f"{m:.1f}",
            "status": "PASS" if arching_ok else "FAIL",
        },
        {
            "name": "Foundation bearing capacity (q_a >= delta_sigma_s)",
            "required": f">= {dsigma_s:.2f} kPa",
            "calculated": f"q_a = {foundation_result['q_a']:.2f} kPa",
            "status": "PASS" if foundation_result["passed"] else "FAIL",
        },
    ]

    return {
        "modulus_ratio": m,
        "arching_ok": arching_ok,
        "stress_method": stress_result["method"],
        "stress_result": stress_result,
        "critical_height_result": hcr_result,
        "foundation_result": foundation_result,
        "strain_method": strain_result["method"],
        "strain_result": strain_result,
        "tension_result": tension_result,
        "a": a,
        "psl": psl,
        "dsigma_s": dsigma_s,
        "epsilon_g": epsilon_g,
        "Tg": Tg,
        "checks": checks,
        "all_steps": all_steps,
    }
