"""Single-file desktop application for the Pile-Supported Embankment Designer."""

import datetime
import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class ValidationError(Exception):
    pass


class CalculationError(Exception):
    pass


def require_positive(value, name):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value <= 0:
        raise ValidationError(f"{name} must be greater than zero.")
    return value


def require_nonnegative(value, name):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value < 0:
        raise ValidationError(f"{name} cannot be negative.")
    return value


def require_range(value, name, low, high):
    if value is None:
        raise ValidationError(f"{name} must be entered.")
    if value < low or value > high:
        raise ValidationError(f"{name} must be between {low} and {high}.")
    return value


def validate_inputs(values, stress_method):
    require_positive(values["H"], "Embankment height (H)")
    require_nonnegative(values["gamma2"], "Embankment fill unit weight (gamma2)")
    require_range(values["phi2"], "Embankment fill friction angle (phi2)", 0, 60)
    require_positive(values["H1"], "Load transfer platform thickness (H1)")
    require_nonnegative(values["gamma1"], "Platform fill unit weight (gamma1)")
    require_range(values["phi1"], "Platform fill friction angle (phi1)", 0, 60)
    require_positive(values["d"], "Column diameter (d)")
    require_positive(values["s"], "Column spacing (s)")
    if values["s"] <= values["d"]:
        raise ValidationError("Column spacing (s) must be greater than column diameter (d).")
    require_positive(values["Ec"], "Column modulus (Ec)")
    require_positive(values["Es"], "Soil modulus (Es)")
    require_positive(values["cu"], "Undrained shear strength (cu)")
    require_nonnegative(values["p"], "Surcharge (p)")
    require_positive(values["dS_allow"], "Allowable differential settlement")
    if values["K1"] <= 0 or values["K2"] <= 0:
        raise ValidationError("K1 and K2 must be greater than zero.")
    if values["n"] <= 1:
        raise ValidationError("Stress concentration ratio (n) must be greater than 1.")
    require_positive(values["FS"], "Factor of safety (FS)")
    if stress_method == "hewlett_randolph":
        require_positive(values.get("Kp"), "Kp (coefficient of passive earth pressure)")


def step(title, symbol, equation, substitution, result, unit, source):
    return {
        "title": title, "symbol": symbol, "equation": equation,
        "substitution": substitution, "result": result, "unit": unit,
        "source": source,
    }


def adapted_terzaghi(values):
    d, s = values["d"], values["s"]
    a = math.sqrt(math.pi * d ** 2 / 4)
    hcr = 1.4 * (s - a)
    denominator = s ** 2 - a ** 2
    alpha1 = 4 * a * values["K1"] * math.tan(math.radians(values["phi1"])) / denominator
    alpha2 = 4 * a * values["K2"] * math.tan(math.radians(values["phi2"])) / denominator
    h, h1 = values["H"], values["H1"]
    gamma1, gamma2, surcharge = values["gamma1"], values["gamma2"], values["p"]
    if hcr > h:
        psl = ((gamma1 / alpha1) * (1 - math.exp(-alpha1 * h1))
               + (gamma2 / alpha2) * math.exp(-alpha1 * h1) * (1 - math.exp(-alpha2 * h1))
               + surcharge * math.exp(-alpha1 * h1 - alpha2 * h1))
        case = "Hcr > H"
        equation = "Engineering reference Eq. (10.18)"
    elif h1 < hcr < h:
        psl = ((gamma1 / alpha1) * (1 - math.exp(-alpha1 * h1))
               + (gamma2 / alpha2) * math.exp(-alpha1 * h1) * (1 - math.exp(-alpha2 * (hcr - h1)))
               + (surcharge + (h - hcr) * gamma2) * math.exp(-alpha1 * h1 - alpha2 * (hcr - h1)))
        case = "H1 < Hcr < H"
        equation = "Engineering reference Eq. (10.19)"
    else:
        psl = ((gamma1 / alpha1) * (1 - math.exp(-alpha1 * hcr))
               + (surcharge + (h1 - hcr) * gamma1 + (h - h1) * gamma2) * math.exp(-alpha1 * hcr))
        case = "Hcr <= H1 (within platform)"
        equation = "Engineering reference Eq. (10.20)"
    steps = [
        step("Equivalent column width", "a", "a = sqrt(pi * d^2 / 4)", f"a = sqrt(pi * {d}^2 / 4)", a, "m", "Engineering reference: equivalent circular-column geometry"),
        step("Critical height", "H_cr", "H_cr = 1.4 (s - a)", f"H_cr = 1.4 ({s} - {a:.4f})", hcr, "m", "Engineering reference: arching critical-height criterion"),
        step("Alpha 1 (platform fill arching coefficient)", "alpha_1", "alpha_1 = 4 a K1 tan(phi1) / (s^2 - a^2)", f"alpha_1 = 4({a:.4f})({values['K1']})tan({values['phi1']} deg) / ({s}^2 - {a:.4f}^2)", alpha1, "1/m", "Engineering reference: arching coefficient definition"),
        step("Alpha 2 (embankment fill arching coefficient)", "alpha_2", "alpha_2 = 4 a K2 tan(phi2) / (s^2 - a^2)", f"alpha_2 = 4({a:.4f})({values['K2']})tan({values['phi2']} deg) / ({s}^2 - {a:.4f}^2)", alpha2, "1/m", "Engineering reference: arching coefficient definition"),
        step(f"Average vertical stress above geosynthetic ({case})", "p_sl", equation, "See equation; case selected automatically from H_cr vs H1, H", psl, "kPa", equation),
    ]
    return {"method": "Adapted Terzaghi", "a": a, "Hcr": hcr, "alpha1": alpha1, "alpha2": alpha2, "psl": psl, "steps": steps}


def hewlett_randolph(values):
    a = math.sqrt(math.pi * values["d"] ** 2 / 4)
    gamma, h, surcharge, s, kp = values["gamma2"], values["H"], values["p"], values["s"], values["Kp"]
    term = (2 * kp - 2) / (2 * kp - 3)
    crown = (gamma * h + surcharge) * ((1 - a / s) ** (2 * (kp - 1)) * (1 - s / (math.sqrt(2) * h) * term) + (s - a) / (math.sqrt(2) * h) * term)
    ratio = a / s
    bracket = (2 * kp / (kp + 1)) * ((1 - ratio) ** (1 - kp) - (1 - ratio) * (1 + ratio * kp)) + (1 - ratio ** 2)
    top = (gamma * h + surcharge) / bracket
    psl = max(crown, top)
    steps = [
        step("Equivalent column width", "a", "a = sqrt(pi * d^2 / 4)", f"a = sqrt(pi * {values['d']}^2 / 4)", a, "m", "Engineering reference: equivalent circular-column geometry"),
        step("Vertical stress at crown of arch", "p_sl (crown)", "Engineering reference Eq. (10.21)", "See governing arch-crown equation", crown, "kPa", "Engineering reference: arch-crown stress method"),
        step("Vertical stress at top of column", "p_sl (column top)", "Engineering reference Eq. (10.22)", "See governing column-top equation", top, "kPa", "Engineering reference: column-top stress method"),
        step("Governing vertical stress above geosynthetic", "p_sl", "p_sl = max(p_sl(crown), p_sl(column top))", f"p_sl = max({crown:.3f}, {top:.3f})", psl, "kPa", "Engineering criterion: governing arching stress"),
    ]
    return {"method": "Hewlett and Randolph", "a": a, "psl": psl, "psl_crown": crown, "psl_top": top, "steps": steps}


def run_design(values, stress_method="adapted_terzaghi", strain_method="giroud"):
    validate_inputs(values, stress_method)
    modulus_ratio = values["Ec"] / values["Es"]
    if modulus_ratio <= 100:
        raise CalculationError(f"Modulus ratio Ec/Es = {modulus_ratio:.1f} is not greater than 100.")
    if stress_method == "adapted_terzaghi":
        stress = adapted_terzaghi(values)
    elif stress_method == "hewlett_randolph":
        stress = hewlett_randolph(values)
    else:
        raise CalculationError(f"Unknown stress method: {stress_method}")
    a = stress["a"]
    h2 = values["H"] - values["H1"]
    dsigma = (values["gamma1"] * values["H1"] + values["gamma2"] * h2) / (1 + (a ** 2 / values["s"] ** 2) * (values["n"] - 1))
    q_ult = 5.14 * values["cu"]
    q_a = q_ult / values["FS"]
    passed = q_a >= dsigma
    foundation_steps = [
        step("Foundation soil resistance", "delta_sigma_s", "delta_sigma_s = (gamma1*H1 + gamma2*H2) / (1 + (a^2/s^2)(n-1))", f"delta_sigma_s = ({values['gamma1']}*{values['H1']} + {values['gamma2']}*{h2}) / (1 + ({a:.4f}^2/{values['s']}^2)*({values['n']}-1))", dsigma, "kPa", "Engineering reference: foundation stress distribution"),
        step("Ultimate bearing capacity of soft soil", "q_ult", "q_ult = 5.14 * cu", f"q_ult = 5.14 * {values['cu']}", q_ult, "kPa", "Engineering reference: undrained bearing capacity"),
        step("Allowable bearing capacity", "q_a", "q_a = q_ult / FS", f"q_a = {q_ult:.3f} / {values['FS']}", q_a, "kPa", "Engineering reference: factor-of-safety bearing resistance"),
        step("Foundation bearing check", "q_a vs delta_sigma_s", "q_a >= delta_sigma_s (required)", f"{q_a:.3f} >= {dsigma:.3f} ?", "PASS" if passed else "FAIL", "", "Engineering criterion: allowable bearing resistance"),
    ]
    if strain_method == "giroud":
        epsilon = 8 * values["dS_allow"] ** 2 / (3 * (values["s"] - a) ** 2)
        strain_name = "Giroud (simplified parabolic)"
        strain_equation = "epsilon_g = 8 * dS_g^2 / (3 * (s - a)^2)"
        strain_source = "Engineering reference: simplified geosynthetic strain method"
    elif strain_method == "catenary":
        span = values["s"] - a
        ratio = values["dS_allow"] / span
        root = math.sqrt(1 + 16 * ratio ** 2)
        epsilon = 0.5 * root + span / (8 * values["dS_allow"]) * math.log(4 * ratio + root) - 1
        strain_name = "Catenary (John, 1987)"
        strain_equation = "Engineering reference: catenary strain equation"
        strain_source = "Engineering reference: catenary geosynthetic strain method"
    else:
        raise CalculationError(f"Unknown strain method: {strain_method}")
    strain_steps = [step(f"Tensile strain in geosynthetic ({strain_name})", "epsilon_g", strain_equation, f"dS_g={values['dS_allow']}, s={values['s']}, a={a:.4f}", epsilon, "(fraction; multiply by 100 for %)", strain_source)]
    tension = ((stress["psl"] - dsigma) * (values["s"] ** 2 - a ** 2) / (4 * a)) * math.sqrt(1 + 1 / (6 * epsilon))
    tension_steps = [step("Tension in geosynthetic reinforcement", "T_g", "T_g = [(p_sl - delta_sigma_s)(s^2-a^2)/(4a)] * sqrt(1 + 1/(6*epsilon_g))", f"T_g = [({stress['psl']:.3f}-{dsigma:.3f})({values['s']}^2-{a:.4f}^2)/(4*{a:.4f})] * sqrt(1 + 1/(6*{epsilon:.5f}))", tension, "kN/m", "Engineering reference: geosynthetic tensile demand equation")]
    return {"modulus_ratio": modulus_ratio, "arching_ok": True, "stress_method": stress["method"], "stress_result": stress, "strain_method": strain_name, "psl": stress["psl"], "a": a, "dsigma_s": dsigma, "epsilon_g": epsilon, "Tg": tension, "foundation_result": {"dsigma_s": dsigma, "q_ult": q_ult, "q_a": q_a, "passed": passed}, "checks": [{"name": "Soil arching fully mobilized (Ec/Es > 100)", "required": "> 100", "calculated": f"{modulus_ratio:.1f}", "status": "PASS"}, {"name": "Foundation bearing capacity (q_a >= delta_sigma_s)", "required": f">= {dsigma:.2f} kPa", "calculated": f"q_a = {q_a:.2f} kPa", "status": "PASS" if passed else "FAIL"}], "all_steps": stress["steps"] + foundation_steps + strain_steps + tension_steps}


def build_report(project_name, values, result):
    lines = ["=" * 72, "PILE-SUPPORTED EMBANKMENT DESIGN -- CALCULATION SHEET", "=" * 72, f"Project / Design Name: {project_name}", f"Date: {datetime.date.today().isoformat()}", f"Stress method used: {result['stress_method']}", f"Strain method used: {result['strain_method']}", "", "INPUT DATA"]
    for key, value in values.items():
        if value is not None:
            lines.append(f"  {key}: {value}")
    lines.extend(["", "CALCULATIONS"])
    for item in result["all_steps"]:
        lines.extend([f"* {item['title']} ({item['symbol']})", f"  Reference: {item['source']}", f"  Equation: {item['equation']}", f"  Substitution: {item['substitution']}", f"  Result: {item['result']} {item['unit']}", ""])
    lines.extend(["DESIGN CHECKS"])
    for check in result["checks"]:
        lines.append(f"  {check['name']}: {check['status']} ({check['calculated']})")
    lines.extend(["", "FINAL RESULTS", f"  Equivalent column width, a: {result['a']:.4f} m", f"  Vertical stress, p_sl: {result['psl']:.3f} kPa", f"  Foundation resistance: {result['dsigma_s']:.3f} kPa", f"  Tensile strain: {result['epsilon_g'] * 100:.3f} %", f"  Required tension, T_g: {result['Tg']:.2f} kN/m"])
    return "\n".join(lines)


EXAMPLE_VALUES = {"H": "5.0", "H1": "0.60", "gamma1": "20.0", "gamma2": "18.0", "phi1": "38.0", "phi2": "30.0", "K1": "0.75", "K2": "0.75", "d": "1.0", "s": "2.5", "p": "13.0", "Ec": "1000.0", "Es": "4.0", "cu": "20.0", "FS": "2.0", "n": "25", "dS_allow": "0.15", "Kp": ""}
FIELD_LABELS = [("H", "Embankment height", "H", "m"), ("gamma2", "Embankment fill unit weight", "gamma2", "kN/m3"), ("phi2", "Embankment fill friction angle", "phi2", "deg"), ("H1", "Load transfer platform thickness", "H1", "m"), ("gamma1", "Platform fill unit weight", "gamma1", "kN/m3"), ("phi1", "Platform fill friction angle", "phi1", "deg"), ("K1", "Platform lateral earth pressure coeff.", "K1", ""), ("K2", "Embankment lateral earth pressure coeff.", "K2", ""), ("d", "Column diameter", "d", "m"), ("s", "Column spacing (center to center)", "s", "m"), ("Ec", "Column (concrete) modulus", "Ec", "MPa"), ("Es", "Soft soil modulus", "Es", "MPa"), ("cu", "Undrained shear strength of soft soil", "cu", "kPa"), ("n", "Stress concentration ratio (n)", "n", ""), ("FS", "Factor of safety (bearing check)", "FS", ""), ("p", "Surcharge on embankment", "p", "kPa"), ("dS_allow", "Allowable differential settlement", "dS", "m"), ("Kp", "Passive earth pressure coeff. (Hewlett & Randolph only)", "Kp", "")]


class PSEDesignerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pile-Supported Embankment Designer")
        self.geometry("900x720")
        self.entries = {}
        self.result = None
        self.last_inputs = None
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, padx=8, pady=6)
        top.pack(fill="x")
        tk.Label(top, text="Project / Design Name:").grid(row=0, column=0, sticky="w")
        self.project_name_var = tk.StringVar(value="Untitled Project")
        tk.Entry(top, textvariable=self.project_name_var, width=40).grid(row=0, column=1, sticky="w")
        tk.Label(top, text="Design Method:").grid(row=1, column=0, sticky="w")
        self.stress_method_var = tk.StringVar(value="adapted_terzaghi")
        for col, (label, value) in enumerate((("Adapted Terzaghi", "adapted_terzaghi"), ("Hewlett and Randolph", "hewlett_randolph")), 1):
            tk.Radiobutton(top, text=label, variable=self.stress_method_var, value=value, command=self._method_changed).grid(row=1, column=col, sticky="w")
        tk.Label(top, text="Strain Method:").grid(row=2, column=0, sticky="w")
        self.strain_method_var = tk.StringVar(value="giroud")
        for col, (label, value) in enumerate((("Giroud", "giroud"), ("Catenary", "catenary")), 1):
            tk.Radiobutton(top, text=label, variable=self.strain_method_var, value=value).grid(row=2, column=col, sticky="w")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=6)
        self.inputs_tab, self.results_tab, self.details_tab = (tk.Frame(self.notebook) for _ in range(3))
        self.notebook.add(self.inputs_tab, text="Inputs")
        self.notebook.add(self.results_tab, text="Results")
        self.notebook.add(self.details_tab, text="Calculation Details")
        self._build_inputs()
        self.results_text = tk.Text(self.results_tab, wrap="word", font=("Courier New", 10))
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.results_text.insert("1.0", "Enter inputs and click Calculate to see results here.")
        self.results_text.config(state="disabled")
        self.details_text = tk.Text(self.details_tab, wrap="word", font=("Courier New", 9))
        self.details_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.details_text.insert("1.0", "Calculation details will appear here after Calculate.")
        self.details_text.config(state="disabled")
        buttons = tk.Frame(self, padx=8, pady=6)
        buttons.pack(fill="x")
        for label, command in (("Load Example", self._load_example), ("Calculate", self._calculate), ("Clear", self._clear), ("Save Report", self._save_report), ("Exit", self.destroy)):
            tk.Button(buttons, text=label, width=14, command=command).pack(side="left", padx=4)
        tk.Label(self, text="Preliminary design tool. Confirm governing code requirements, project criteria, and geotechnical assumptions before issue for construction.", fg="gray20", wraplength=880, justify="left").pack(fill="x", padx=8, pady=(0, 6))
        self._method_changed()

    def _build_inputs(self):
        frame = tk.Frame(self.inputs_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        for col, text in enumerate(("Parameter", "Symbol", "Value", "Unit")):
            tk.Label(frame, text=text, font=("Arial", 9, "bold")).grid(row=0, column=col, sticky="w")
        self.kp_widgets = []
        for row, (key, label, symbol, unit) in enumerate(FIELD_LABELS, 1):
            tk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=2)
            tk.Label(frame, text=symbol).grid(row=row, column=1, sticky="w", padx=6)
            variable = tk.StringVar()
            entry = tk.Entry(frame, textvariable=variable, width=12)
            entry.grid(row=row, column=2, sticky="w")
            tk.Label(frame, text=unit).grid(row=row, column=3, sticky="w", padx=6)
            self.entries[key] = variable
            if key == "Kp":
                self.kp_widgets = [entry]

    def _method_changed(self):
        state = "normal" if self.stress_method_var.get() == "hewlett_randolph" else "disabled"
        for widget in self.kp_widgets:
            widget.config(state=state)

    def _load_example(self):
        for key, value in EXAMPLE_VALUES.items():
            self.entries[key].set(value)
        self.project_name_var.set("Design Example 10.3")
        self._method_changed()

    def _clear(self):
        for variable in self.entries.values():
            variable.set("")
        self.project_name_var.set("Untitled Project")
        for widget, text in ((self.results_text, "Enter inputs and click Calculate to see results here."), (self.details_text, "Calculation details will appear here after Calculate.")):
            widget.config(state="normal")
            widget.delete("1.0", "end")
            widget.insert("1.0", text)
            widget.config(state="disabled")

    def _parse_inputs(self):
        values = {}
        for key, label, symbol, _unit in FIELD_LABELS:
            raw = self.entries[key].get().strip()
            if key == "Kp" and self.stress_method_var.get() != "hewlett_randolph":
                values[key] = None
            elif raw == "":
                if key == "Kp":
                    values[key] = None
                else:
                    raise ValidationError(f"{label} ({symbol}) must be entered.")
            else:
                try:
                    values[key] = int(float(raw)) if key == "n" else float(raw)
                except ValueError as error:
                    raise ValidationError(f"{label} ({symbol}) must be a number.") from error
        return values

    def _calculate(self):
        try:
            self.last_inputs = self._parse_inputs()
            self.result = run_design(self.last_inputs, self.stress_method_var.get(), self.strain_method_var.get())
        except (ValidationError, CalculationError) as error:
            messagebox.showerror("Calculation Error", str(error))
            return
        self._show_results()
        self._show_details()
        self.notebook.select(self.results_tab)

    def _show_results(self):
        result = self.result
        lines = ["FINAL DESIGN RESULTS", "=" * 60, f"Method Used: {result['stress_method']}", f"Strain Method Used: {result['strain_method']}", "", f"Equivalent column width, a: {result['a']:.4f} m", f"Vertical stress above geosynthetic, p_sl: {result['psl']:.3f} kPa", f"Foundation soil resistance, dsigma_s: {result['dsigma_s']:.3f} kPa", f"Tensile strain, epsilon_g: {result['epsilon_g'] * 100:.3f} %", f"Required tension, T_g: {result['Tg']:.2f} kN/m", "", "DESIGN CHECKS"]
        for check in result["checks"]:
            lines.extend([check["name"], f"   Required: {check['required']}", f"   Calculated: {check['calculated']}", f"   STATUS: {check['status']}", ""])
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "\n".join(lines))
        self.results_text.config(state="disabled")

    def _show_details(self):
        lines = []
        for index, item in enumerate(self.result["all_steps"], 1):
            value = f"{item['result']:.4f}" if isinstance(item["result"], float) else str(item["result"])
            lines.extend([f"{index}. {item['title'].upper()}", "", f"Reference: {item['source']}", f"Equation: {item['equation']}", f"Substitution: {item['substitution']}", f"Result: {item['symbol']} = {value} {item['unit']}", "", "-" * 60, ""])
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "\n".join(lines))
        self.details_text.config(state="disabled")

    def _save_report(self):
        if self.result is None:
            messagebox.showwarning("No Results", "Please click Calculate first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text file", "*.txt")], initialfile="calculation_report.txt")
        if path:
            with open(path, "w", encoding="utf-8") as report_file:
                report_file.write(build_report(self.project_name_var.get(), self.last_inputs, self.result))
            messagebox.showinfo("Saved", f"Report saved to:\n{path}")


def main():
    PSEDesignerApp().mainloop()


if __name__ == "__main__":
    main()
