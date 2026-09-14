"""
gui.py

Simple Tkinter GUI for the Pile-Supported Embankment Designer.
Kept plain and straightforward on purpose -- ordinary frames, labels,
entry boxes and buttons, default grey/white Tk styling.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from calculation_engine import run_design, CalculationError
from validation import ValidationError
import report as report_module


# Worked example values from the supplied PDF, Design Example 10.3 (p.362)
EXAMPLE_VALUES = {
    "H": "5.0",
    "H1": "0.60",
    "gamma1": "20.0",
    "gamma2": "18.0",
    "phi1": "38.0",
    "phi2": "30.0",
    "K1": "0.75",
    "K2": "0.75",
    "d": "1.0",
    "s": "2.5",
    "p": "13.0",
    "Ec": "1000.0",
    "Es": "4.0",
    "cu": "20.0",
    "FS": "2.0",
    "n": "25",
    "dS_allow": "0.15",
    "Kp": "",
}

FIELD_LABELS = [
    # (key, label, symbol, unit)
    ("H", "Embankment height", "H", "m"),
    ("gamma2", "Embankment fill unit weight", "gamma2", "kN/m3"),
    ("phi2", "Embankment fill friction angle", "phi2", "deg"),
    ("H1", "Load transfer platform thickness", "H1", "m"),
    ("gamma1", "Platform fill unit weight", "gamma1", "kN/m3"),
    ("phi1", "Platform fill friction angle", "phi1", "deg"),
    ("K1", "Platform lateral earth pressure coeff.", "K1", ""),
    ("K2", "Embankment lateral earth pressure coeff.", "K2", ""),
    ("d", "Column diameter", "d", "m"),
    ("s", "Column spacing (center to center)", "s", "m"),
    ("Ec", "Column (concrete) modulus", "Ec", "MPa"),
    ("Es", "Soft soil modulus", "Es", "MPa"),
    ("cu", "Undrained shear strength of soft soil", "cu", "kPa"),
    ("n", "Stress concentration ratio (n)", "n", ""),
    ("FS", "Factor of safety (bearing check)", "FS", ""),
    ("p", "Surcharge on embankment", "p", "kPa"),
    ("dS_allow", "Allowable differential settlement", "dS", "m"),
    ("Kp", "Passive earth pressure coeff. (Hewlett & Randolph only)", "Kp", ""),
]


class PSEDesignerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pile-Supported Embankment Designer")
        self.geometry("880x720")
        self.resizable(True, True)

        self.entries = {}
        self.result = None
        self.last_inputs = None

        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        # top frame - project name and method
        top_frame = tk.Frame(self, padx=8, pady=6)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Project / Design Name:").grid(row=0, column=0, sticky="w")
        self.project_name_var = tk.StringVar(value="Untitled Project")
        tk.Entry(top_frame, textvariable=self.project_name_var, width=40).grid(
            row=0, column=1, sticky="w", padx=4
        )

        tk.Label(top_frame, text="Design Method:").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.stress_method_var = tk.StringVar(value="adapted_terzaghi")
        method_frame = tk.Frame(top_frame)
        method_frame.grid(row=1, column=1, sticky="w", pady=(6, 0))
        tk.Radiobutton(
            method_frame, text="Method 1 - Adapted Terzaghi",
            variable=self.stress_method_var, value="adapted_terzaghi",
            command=self._on_method_change,
        ).pack(side="left")
        tk.Radiobutton(
            method_frame, text="Method 2 - Hewlett and Randolph",
            variable=self.stress_method_var, value="hewlett_randolph",
            command=self._on_method_change,
        ).pack(side="left")

        tk.Label(top_frame, text="Strain Method:").grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.strain_method_var = tk.StringVar(value="giroud")
        strain_frame = tk.Frame(top_frame)
        strain_frame.grid(row=2, column=1, sticky="w", pady=(6, 0))
        tk.Radiobutton(
            strain_frame, text="Giroud (simplified)",
            variable=self.strain_method_var, value="giroud",
        ).pack(side="left")
        tk.Radiobutton(
            strain_frame, text="Catenary (John, 1987)",
            variable=self.strain_method_var, value="catenary",
        ).pack(side="left")

        # notebook: inputs / results / calc details / checks
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=6)

        self.inputs_tab = tk.Frame(self.notebook)
        self.results_tab = tk.Frame(self.notebook)
        self.details_tab = tk.Frame(self.notebook)

        self.notebook.add(self.inputs_tab, text="Inputs")
        self.notebook.add(self.results_tab, text="Results")
        self.notebook.add(self.details_tab, text="Calculation Details")

        self._build_inputs_tab()
        self._build_results_tab()
        self._build_details_tab()

        # bottom buttons
        btn_frame = tk.Frame(self, padx=8, pady=6)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Load Example", width=14, command=self._load_example).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Calculate", width=14, command=self._calculate).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Clear", width=14, command=self._clear).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Save Report", width=14, command=self._save_report).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Exit", width=14, command=self.destroy).pack(side="left", padx=4)

        # disclaimer
        disclaimer = tk.Label(
            self,
            text=("Academic/project calculation tool. Results should be independently "
                  "checked by a qualified geotechnical engineer before use in real construction."),
            font=("Arial", 8), fg="gray20", wraplength=860, justify="left",
        )
        disclaimer.pack(fill="x", padx=8, pady=(0, 6))

        self._on_method_change()

    # ------------------------------------------------------------------
    def _build_inputs_tab(self):
        frame = tk.Frame(self.inputs_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Parameter", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Symbol", font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w")
        tk.Label(frame, text="Value", font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w")
        tk.Label(frame, text="Unit", font=("Arial", 9, "bold")).grid(row=0, column=3, sticky="w")

        self.kp_row_widgets = []

        for i, (key, label, symbol, unit) in enumerate(FIELD_LABELS, start=1):
            lbl = tk.Label(frame, text=label)
            lbl.grid(row=i, column=0, sticky="w", pady=2)
            sym = tk.Label(frame, text=symbol)
            sym.grid(row=i, column=1, sticky="w", padx=6)
            var = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var, width=12)
            entry.grid(row=i, column=2, sticky="w")
            unit_lbl = tk.Label(frame, text=unit)
            unit_lbl.grid(row=i, column=3, sticky="w", padx=6)
            self.entries[key] = var

            if key == "Kp":
                self.kp_row_widgets = [lbl, sym, entry, unit_lbl]
                self.kp_note_label = tk.Label(
                    frame,
                    text="(Required only for Hewlett & Randolph method - no default given in source)",
                    font=("Arial", 8), fg="gray30",
                )
                self.kp_note_label.grid(row=i, column=4, sticky="w", padx=6)

        note = tk.Label(
            frame,
            text=(
                "Notes: K1, K2 default to 0.75 per Sloan et al. (2011) as used in the source's "
                "worked example. n=25 is the source's suggested value for rigid columns."
            ),
            font=("Arial", 8), fg="gray30", wraplength=760, justify="left",
        )
        note.grid(row=len(FIELD_LABELS) + 1, column=0, columnspan=4, sticky="w", pady=(10, 0))

    # ------------------------------------------------------------------
    def _build_results_tab(self):
        frame = tk.Frame(self.results_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        self.results_text = tk.Text(frame, wrap="word", height=30, font=("Courier New", 10))
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert("1.0", "Enter inputs and click Calculate to see results here.")
        self.results_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _build_details_tab(self):
        frame = tk.Frame(self.details_tab, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.details_text = tk.Text(frame, wrap="word", font=("Courier New", 9), yscrollcommand=scrollbar.set)
        self.details_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.details_text.yview)

        self.details_text.insert("1.0", "Calculation Details will appear here after you click Calculate.")
        self.details_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _on_method_change(self):
        method = self.stress_method_var.get()
        state = "normal" if method == "hewlett_randolph" else "disabled"
        for w in self.kp_row_widgets:
            try:
                w.config(state=state)
            except tk.TclError:
                pass

    # ------------------------------------------------------------------
    def _load_example(self):
        for key, val in EXAMPLE_VALUES.items():
            if key in self.entries:
                self.entries[key].set(val)
        self.project_name_var.set("Design Example 10.3 (source PDF)")
        self.stress_method_var.set("adapted_terzaghi")
        self.strain_method_var.set("giroud")
        self._on_method_change()
        messagebox.showinfo("Example Loaded", "Worked example values from the source PDF have been loaded.")

    # ------------------------------------------------------------------
    def _clear(self):
        for var in self.entries.values():
            var.set("")
        self.project_name_var.set("Untitled Project")
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Enter inputs and click Calculate to see results here.")
        self.results_text.config(state="disabled")
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "Calculation Details will appear here after you click Calculate.")
        self.details_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _parse_inputs(self):
        """Parse string entries into floats. Raises ValidationError with a
        human-readable message on bad/missing input (never a raw traceback)."""
        values = {}
        stress_method = self.stress_method_var.get()

        for key, label, symbol, unit in FIELD_LABELS:
            raw = self.entries[key].get().strip()

            if key == "Kp" and stress_method != "hewlett_randolph":
                values[key] = None
                continue

            if raw == "":
                if key == "Kp":
                    values[key] = None
                    continue
                raise ValidationError(f"{label} ({symbol}) must be entered.")

            try:
                if key == "n":
                    values[key] = int(float(raw))
                else:
                    values[key] = float(raw)
            except ValueError:
                raise ValidationError(f"{label} ({symbol}) must be a number.")

        return values

    # ------------------------------------------------------------------
    def _calculate(self):
        try:
            inputs = self._parse_inputs()
            stress_method = self.stress_method_var.get()
            strain_method = self.strain_method_var.get()
            result = run_design(inputs, stress_method=stress_method, strain_method=strain_method)
        except ValidationError as e:
            messagebox.showerror("Input Error", str(e))
            return
        except CalculationError as e:
            messagebox.showerror("Calculation Error", str(e))
            return
        except Exception as e:
            # Catch-all so a user never sees a raw Python traceback.
            messagebox.showerror(
                "Unexpected Error",
                f"Calculation could not be completed because: {e}",
            )
            return

        self.result = result
        self.last_inputs = inputs
        self._display_results(result)
        self._display_details(result)
        self.notebook.select(self.results_tab)

    # ------------------------------------------------------------------
    def _display_results(self, result):
        lines = []
        lines.append("FINAL DESIGN RESULTS")
        lines.append("=" * 60)
        lines.append(f"Method Used: {result['stress_method']}")
        lines.append(f"Strain Method Used: {result['strain_method']}")
        lines.append("")
        lines.append(f"Equivalent column width, a:              {result['a']:.4f} m")
        if "Hcr" in result["stress_result"]:
            lines.append(f"Critical height, Hcr:                    {result['stress_result']['Hcr']:.4f} m")
        lines.append(f"Vertical stress above geosynthetic, p_sl: {result['psl']:.3f} kPa")
        lines.append(f"Foundation soil resistance, dsigma_s:     {result['dsigma_s']:.3f} kPa")
        lines.append(f"Tensile strain, epsilon_g:                {result['epsilon_g']*100:.3f} %")
        lines.append(f"Required tension, T_g:                    {result['Tg']:.2f} kN/m")
        lines.append("")
        lines.append("DESIGN CHECKS")
        lines.append("-" * 60)
        for check in result["checks"]:
            lines.append(f"{check['name']}")
            lines.append(f"   Required:   {check['required']}")
            lines.append(f"   Calculated: {check['calculated']}")
            lines.append(f"   STATUS: {check['status']}")
            lines.append("")

        text = "\n".join(lines)
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", text)
        self.results_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _display_details(self, result):
        lines = []
        for i, step in enumerate(result["all_steps"], start=1):
            lines.append(f"{i}. {step['title'].upper()}")
            lines.append("")
            lines.append(f"Source: {step['source']}")
            lines.append(f"Equation:")
            lines.append(f"  {step['equation']}")
            lines.append("")
            lines.append(f"Substitution:")
            lines.append(f"  {step['substitution']}")
            lines.append("")
            r = step["result"]
            if isinstance(r, float):
                lines.append(f"Result:  {step['symbol']} = {r:.4f} {step['unit']}")
            else:
                lines.append(f"Result:  {step['symbol']} = {r} {step['unit']}")
            lines.append("")
            lines.append("-" * 60)
            lines.append("")

        text = "\n".join(lines)
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", text)
        self.details_text.config(state="disabled")

    # ------------------------------------------------------------------
    def _save_report(self):
        if self.result is None:
            messagebox.showwarning("No Results", "Please click Calculate first.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt")],
            initialfile="calculation_report.txt",
        )
        if not filepath:
            return

        try:
            report_module.save_report(
                filepath,
                self.project_name_var.get(),
                self.stress_method_var.get(),
                self.strain_method_var.get(),
                self.last_inputs,
                self.result,
            )
            messagebox.showinfo("Saved", f"Report saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save report: {e}")


def main():
    app = PSEDesignerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
