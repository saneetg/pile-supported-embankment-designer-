PILE-SUPPORTED EMBANKMENT DESIGNER
====================================
Academic / final-year civil engineering project tool.
Based strictly on: "Principles and Practice of Ground Improvement"
(Jie Han, Wiley, 2015), Section 10.4 "Geosynthetic-Reinforced
Column-Supported Embankments", pages 353-364.


1. WHAT THIS PROGRAM DOES
--------------------------
Calculates the design of a geosynthetic-reinforced column/pile-supported
(GRCS) embankment: vertical stress above the geosynthetic reinforcement,
foundation soil resistance, bearing capacity check, tensile strain in the
reinforcement, and the required tension/tensile strength of the
geosynthetic.

Two independent stress methods are implemented (pick one per run):
  - Method 1: Adapted Terzaghi method (Sloan et al., 2011)
  - Method 2: Hewlett and Randolph method (1988)

Two independent strain methods are implemented (pick one per run):
  - Giroud (1995) simplified formula
  - Catenary method (John, 1987)

The program is a reusable calculator: change any input (height, spacing,
diameter, moduli, etc.) and every dependent value recalculates. Nothing
is hard-coded to the worked example.


2. HOW TO RUN THE PYTHON VERSION
----------------------------------
Requirements: Python 3.9+ (Tkinter is included with standard Python on
Windows -- no separate install needed).

    cd pse_app
    python main.py

No third-party packages are required to RUN the program. PyInstaller is
only needed to build the .exe (see below).


3. HOW TO BUILD THE WINDOWS .EXE
-----------------------------------
On a WINDOWS machine with Python installed:

    cd pse_app
    pip install -r requirements.txt
    pyinstaller --onefile --windowed --name Pile_Supported_Embankment_Designer main.py

This produces:

    dist\Pile_Supported_Embankment_Designer.exe

Copy that single .exe anywhere on a Windows PC -- it does not require
Python to be installed to run.

Notes:
  --onefile   packages everything into a single .exe
  --windowed  suppresses the console window (GUI-only app)

If you want a taskbar icon, add:  --icon=youricon.ico


4. HOW TO USE THE APPLICATION
--------------------------------
1. Choose a Design Method (Adapted Terzaghi or Hewlett & Randolph).
2. Choose a Strain Method (Giroud or Catenary).
3. Enter all required inputs on the "Inputs" tab (or click "Load Example"
   to auto-fill the worked example from the source book).
4. Click "Calculate".
5. View final numbers on the "Results" tab.
6. View every equation, substitution, and source page reference on the
   "Calculation Details" tab.
7. Click "Save Report" to export a plain-text calculation sheet suitable
   for a project appendix or viva defense.

The Hewlett & Randolph method requires one additional input, Kp
(coefficient of passive earth pressure of the embankment fill). This
value is NOT given anywhere in the supplied source excerpt and has no
default -- you must supply a value appropriate to your embankment fill's
friction angle (Kp = tan^2(45 + phi/2) for a cohesionless fill, if you
choose to use that standard relationship; this relationship itself is
NOT stated in the supplied source and is left to the user's judgment).


5. VALIDATION AGAINST THE SOURCE WORKED EXAMPLE
--------------------------------------------------
Run:
    python worked_example_test.py

This reproduces Design Example 10.3 from the source (p.362-363) using the
Adapted Terzaghi + Giroud method combination and prints a side-by-side
comparison against the book's printed results.

RESULT OF VALIDATION (9 of 11 checked quantities match the source to
printed precision):

  Modulus ratio (Ec/Es):        MATCH   (250 vs 250)
  Equivalent column width a:    MATCH   (0.886 m vs 0.89 m)
  Critical height Hcr:          MATCH   (2.259 m vs 2.26 m)
  alpha1:                       MATCH   (0.380 vs 0.38)
  alpha2:                       MATCH   (0.281 vs 0.28)
  Foundation resistance:        MATCH   (22.71 kPa vs 22.7 kPa)
  Ultimate bearing q_ult:       MATCH   (102.8 kPa vs 102.8 kPa)
  Allowable bearing q_a:        MATCH   (51.4 kPa vs 51.4 kPa)
  Tensile strain epsilon_g:     MATCH   (2.304% vs 2.3%)

  Vertical stress p_sl:         DOES NOT MATCH (60.87 kPa vs 56.8 kPa)
  Tension T_g:                  DOES NOT MATCH (168.80 kN/m vs 151 kN/m)

DISCREPANCY EXPLANATION:
The program implements Equation (10.19) of the source EXACTLY as printed,
substituting the source's own stated intermediate values (Hcr = 2.26 m,
alpha1 = 0.38, alpha2 = 0.28). Doing so produces p_sl = 60.87 kPa, not the
56.8 kPa printed in the book's worked solution. This has been verified by
hand and by code, including checking whether 2-decimal rounding of
alpha1/alpha2 (as printed) explains the gap -- it does not (still gives
~60.9 kPa either way).

This appears to be a genuine arithmetic inconsistency in the source
textbook's own worked solution (i.e. the printed answer of 56.8 kPa does
not follow from the printed equation and the printed intermediate values).
Per the project's explicit instruction not to alter equations to force a
match, the program reports its own computed value (60.87 kPa) using the
book's stated formula, and flags this discrepancy plainly rather than
silently "fixing" it. The error carries through to the final tension
(168.80 kN/m vs 151 kN/m), since tension depends directly on p_sl.

If you can locate a different edition/printing of this textbook with a
corrected Design Example 10.3, or if there is an errata sheet, that would
help resolve which value (56.8 or 60.87) is correct. Until then, this
tool computes from the stated equation, not from the possibly-erroneous
printed answer.


6. IMPORTANT ASSUMPTIONS (explicitly flagged, all editable in the GUI)
--------------------------------------------------------------------------
- K1 = K2 = 0.75: suggested by Sloan et al. (2011) in the source text as
  giving a reasonable match with field data; used directly (not derived)
  in the source's own worked example. Editable in the GUI.
- n = 25 (stress concentration ratio): the source states "assume 25 for
  rigid columns" for use in Eq. (10.27). Editable in the GUI.
- FS = 2.0: used in the source's worked example for the bearing check
  (Eq. 10.28 states "typically use 2.0"). Editable in the GUI.
- gamma_e (Hewlett & Randolph method only): the source's Eq. (10.21) and
  (10.22) use a single embankment unit weight gamma_e over the full
  height H, but does not specify how to obtain gamma_e when the
  embankment has two separate fill layers (platform + embankment fill).
  ASSUMPTION NOT SPECIFIED IN SOURCE: this program uses gamma_e = gamma2
  (the embankment fill unit weight) directly. This enters
  methods/hewlett_randolph.py via calculation_engine.py.
- Kp (Hewlett & Randolph method only): NOT specified anywhere in the
  supplied source excerpt. No default is provided; the GUI requires the
  user to enter it explicitly for this method.
- Design checks NOT implemented (out of scope, mentioned but not detailed
  with equations in the supplied excerpt): edge slope stability, global
  slope stability, lateral spreading. The source references "simplified
  Bishop method" and other slope-stability techniques for these but does
  not give the working equations in the pages provided.
- The full tension-strain compatibility cubic (for a reinforcement of
  known stiffness J, mentioned on p.361) is NOT implemented, since the
  worked example does not use it and J is not part of the example's given
  data. See strain_methods/parabolic.py docstring for detail.


7. CODE STRUCTURE
--------------------
main.py                    - entry point
gui.py                      - Tkinter GUI
calculation_engine.py       - orchestrates the full calculation chain
validation.py               - input validation / human-readable errors
foundation.py                - foundation soil resistance + bearing check (Eq 10.27/10.28)
tension.py                   - tension in geosynthetic (Eq 10.24 form)
report.py                    - text report / calculation sheet export
worked_example_test.py       - reproduces Design Example 10.3, prints comparison
methods/
    adapted_terzaghi.py       - Method 1 (Eq 10.18/10.19/10.20)
    hewlett_randolph.py       - Method 2 (Eq 10.21/10.22)
strain_methods/
    giroud.py                 - Giroud simplified strain (Eq 10.26)
    catenary.py                - Catenary method strain (Eq 10.23)
    parabolic.py                - Parabolic method tension (Eq 10.25), direct-Tg form only

Every equation in every file carries a comment referencing its exact page
and equation number in the supplied source, e.g.:
    # Source: supplied PDF, p.361, Eq. (10.27)

To add a new design method later: create a new file in methods/ (or
strain_methods/) with a run(inputs) function returning the same structure
(method, ..., steps), then add a branch for it in calculation_engine.py
and a radio button in gui.py. No other files need to change.
