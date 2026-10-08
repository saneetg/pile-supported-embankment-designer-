"""
report.py

Generates a simple, readable text calculation sheet for academic/project
documentation, suitable for a viva or project report appendix.
"""

import datetime


def build_report_text(project_name, stress_method, strain_method, inputs, result):
    lines = []
    lines.append("=" * 72)
    lines.append("PILE-SUPPORTED EMBANKMENT DESIGN -- CALCULATION SHEET")
    lines.append("=" * 72)
    lines.append(f"Project / Design Name: {project_name}")
    lines.append(f"Date: {datetime.date.today().isoformat()}")
    lines.append(f"Stress method used: {result['stress_method']}")
    lines.append(f"Strain method used: {result['strain_method']}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("INPUT DATA")
    lines.append("-" * 72)
    labels = {
        "H": ("Embankment height", "m"),
        "H1": ("Load transfer platform thickness", "m"),
        "gamma1": ("Platform fill unit weight", "kN/m3"),
        "gamma2": ("Embankment fill unit weight", "kN/m3"),
        "phi1": ("Platform fill friction angle", "deg"),
        "phi2": ("Embankment fill friction angle", "deg"),
        "K1": ("Platform lateral earth pressure coeff. K1", ""),
        "K2": ("Embankment lateral earth pressure coeff. K2", ""),
        "d": ("Column diameter", "m"),
        "s": ("Column spacing", "m"),
        "p": ("Surcharge", "kPa"),
        "Ec": ("Column modulus", "MPa"),
        "Es": ("Soil modulus", "MPa"),
        "cu": ("Undrained shear strength", "kPa"),
        "FS": ("Factor of safety", ""),
        "n": ("Stress concentration ratio", ""),
        "dS_allow": ("Allowable differential settlement", "m"),
        "Kp": ("Coefficient of passive earth pressure (Hewlett & Randolph only)", ""),
    }
    for key, (label, unit) in labels.items():
        if key in inputs and inputs[key] is not None:
            lines.append(f"  {label:<55}{inputs[key]:>10} {unit}")
    lines.append("")

    lines.append("-" * 72)
    lines.append("CALCULATIONS")
    lines.append("-" * 72)
    for step in result["all_steps"]:
        lines.append(f"* {step['title']} ({step['symbol']})")
        lines.append(f"  Equation:     {step['equation']}")
        lines.append(f"  Substitution: {step['substitution']}")
        r = step["result"]
        if isinstance(r, float):
            lines.append(f"  Result:       {r:.4f} {step['unit']}")
        else:
            lines.append(f"  Result:       {r} {step['unit']}")
        lines.append("")

    lines.append("-" * 72)
    lines.append("DESIGN CHECKS")
    lines.append("-" * 72)
    for check in result["checks"]:
        lines.append(f"  {check['name']}")
        lines.append(f"    Required:   {check['required']}")
        lines.append(f"    Calculated: {check['calculated']}")
        lines.append(f"    Status:     {check['status']}")
        lines.append("")

    lines.append("-" * 72)
    lines.append("FINAL RESULTS")
    lines.append("-" * 72)
    lines.append(f"  Equivalent column width, a:            {result['a']:.4f} m")
    if "Hcr" in result["stress_result"]:
        lines.append(f"  Critical height, Hcr:                   {result['stress_result']['Hcr']:.4f} m")
    lines.append(f"  Vertical stress above geosynthetic, p_sl: {result['psl']:.3f} kPa")
    lines.append(f"  Foundation soil resistance, delta_sigma_s: {result['dsigma_s']:.3f} kPa")
    lines.append(f"  Tensile strain, epsilon_g:               {result['epsilon_g']*100:.3f} %")
    lines.append(f"  Required tension, T_g:                  {result['Tg']:.2f} kN/m")
    lines.append("")
    lines.append("=" * 72)
    lines.append("Academic/project calculation tool. Results should be independently")
    lines.append("checked by a qualified geotechnical engineer before use in real")
    lines.append("construction.")
    lines.append("=" * 72)

    return "\n".join(lines)


def save_report(filepath, project_name, stress_method, strain_method, inputs, result):
    text = build_report_text(project_name, stress_method, strain_method, inputs, result)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath
