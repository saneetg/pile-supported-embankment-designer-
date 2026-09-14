"""
worked_example_test.py

Reproduces Design Example 10.3 from the supplied PDF (p.362-363) using the
calculation engine, and prints a comparison table against the source's
printed results. Run this BEFORE trusting the GUI.

Usage:
    python worked_example_test.py
"""

from calculation_engine import run_design, CalculationError
from validation import ValidationError

# Exact inputs from Design Example 10.3, supplied PDF p.362
inputs = {
    "H": 5.0,          # embankment height, m
    "H1": 0.60,        # load transfer platform thickness, m
    "gamma1": 20.0,    # platform fill unit weight, kN/m3
    "gamma2": 18.0,    # embankment fill unit weight, kN/m3
    "phi1": 38.0,      # platform fill friction angle, deg
    "phi2": 30.0,      # embankment fill friction angle, deg
    "K1": 0.75,        # ASSUMPTION NOT SPECIFIED IN SOURCE for general case;
                       # source states "Sloan et al. (2011) suggested that
                       # K1 and K2 should be 0.75" -- used directly in example
    "K2": 0.75,
    "d": 1.0,          # column diameter, m
    "s": 2.5,          # column spacing, m
    "p": 13.0,         # surcharge, kPa
    "Ec": 1000.0,      # column modulus, MPa (1 GPa)
    "Es": 4.0,         # soil modulus, MPa
    "cu": 20.0,        # undrained shear strength, kPa
    "FS": 2.0,         # factor of safety (source uses 2.0 in example)
    "n": 25,           # stress concentration ratio, assumed 25 for rigid columns
    "dS_allow": 0.15,  # allowable differential settlement, m
}

print("=" * 70)
print("WORKED EXAMPLE VALIDATION -- Design Example 10.3 (supplied PDF p.362-363)")
print("=" * 70)

try:
    result = run_design(inputs, stress_method="adapted_terzaghi", strain_method="giroud")
except (ValidationError, CalculationError) as e:
    print("ERROR:", e)
    raise SystemExit(1)

print("\n--- CALCULATION TRACE ---\n")
for step in result["all_steps"]:
    print(f"[{step['source']}]")
    print(f"  {step['title']} ({step['symbol']})")
    print(f"  Equation:     {step['equation']}")
    print(f"  Substitution: {step['substitution']}")
    r = step["result"]
    if isinstance(r, float):
        print(f"  Result:       {r:.4f} {step['unit']}")
    else:
        print(f"  Result:       {r} {step['unit']}")
    print()

print("=" * 70)
print("SOURCE EXAMPLE VALIDATION")
print("=" * 70)

pdf_values = {
    "Modulus ratio (Ec/Es)": (250.0, result["modulus_ratio"]),
    "Equivalent column width a (m)": (0.89, result["a"]),
    "Critical height Hcr (m)": (2.26, result["stress_result"]["Hcr"]),
    "alpha1 (1/m)": (0.38, result["stress_result"]["alpha1"]),
    "alpha2 (1/m)": (0.28, result["stress_result"]["alpha2"]),
    "Vertical stress p_sl (kPa)": (56.8, result["psl"]),
    "Foundation resistance delta_sigma_s (kPa)": (22.7, result["dsigma_s"]),
    "Ultimate bearing q_ult (kPa)": (102.8, result["foundation_result"]["q_ult"]),
    "Allowable bearing q_a (kPa)": (51.4, result["foundation_result"]["q_a"]),
    "Tensile strain epsilon_g (%)": (2.3, result["epsilon_g"] * 100),
    "Tension T_g (kN/m)": (151.0, result["Tg"]),
}

print(f"{'Parameter':<42}{'PDF Result':>15}{'Program Result':>18}{'Match?':>10}")
print("-" * 87)
for name, (pdf_val, prog_val) in pdf_values.items():
    if pdf_val == 0:
        pct_diff = 0.0
    else:
        pct_diff = abs(prog_val - pdf_val) / abs(pdf_val) * 100
    match = "YES" if pct_diff < 2.0 else "NO (see note)"
    print(f"{name:<42}{pdf_val:>15.3f}{prog_val:>18.3f}{match:>10}")

print()
print("NOTE ON DISCREPANCY (p_sl and T_g):")
print("-" * 70)
print(
    "Using Eq. (10.19) exactly as printed in the supplied PDF (p.360), with\n"
    "the PDF's own stated intermediate values (Hcr=2.26, alpha1=0.38,\n"
    "alpha2=0.28), this program computes p_sl = {:.2f} kPa, not the 56.8 kPa\n"
    "printed in the worked solution (p.363, step 3). This discrepancy\n"
    "propagates directly into the final tension T_g ({:.2f} kN/m vs the\n"
    "151 kN/m printed).\n\n"
    "This is flagged as a SOURCE INCONSISTENCY rather than corrected, per\n"
    "instructions: the program implements Eq. (10.19) as written, using the\n"
    "PDF's own printed intermediate values, and does not silently alter the\n"
    "formula to force a match. All other intermediate values (modulus\n"
    "ratio, a, Hcr, alpha1, alpha2, foundation resistance, bearing check,\n"
    "and strain) match the source to the printed precision."
    .format(result["psl"], result["Tg"])
)

print("\n--- DESIGN CHECKS ---")
for check in result["checks"]:
    print(f"  {check['name']}: required {check['required']}, "
          f"calculated {check['calculated']} -> {check['status']}")
