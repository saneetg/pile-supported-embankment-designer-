# Pile-Supported Embankment Designer: Project Guide

This document explains the project in everyday language. It is intended for
someone who wants to understand what each file is for without needing to be a
programmer.

## What the project does

This is a Windows desktop tool for preliminary checks of an embankment that is
supported by piles or columns and geosynthetic reinforcement.

The user enters information about the embankment, soil, columns, loading, and
settlement. The program then estimates:

- how much load reaches the geosynthetic layer;
- how much load the foundation soil must carry;
- whether the soil bearing check passes;
- the strain in the geosynthetic; and
- the geosynthetic tension required by the calculation.

The results are for engineering review and preliminary design. They must be
checked by a qualified geotechnical engineer before being used for construction.

## The main ways to use it

### Ready-made Windows application

Open:

`dist/Pile Supported Embankment Designer.exe`

This is the easiest option. Python is not needed because the program has been
packaged into a Windows executable.

### Run the source version

The source version can be started by double-clicking:

`run_project.bat`

It starts `standalone_app.py`. Python 3.9 or newer must be installed with
Tkinter, which is the part of Python used to display the windows and buttons.

The modular version can also be started from a terminal with:

```text
py -3 main.py
```

## How the calculation flows

1. The screen collects the design values.
2. `validation.py` checks that the values are present and sensible.
3. `calculation_engine.py` coordinates the calculation.
4. The selected critical-height option supplies Hcr. The Table 10.4 option
   calculates it from the entered factor and geometry; the user-input option
   accepts Hcr directly.
5. One stress method calculates the vertical stress above the geosynthetic:
   Adapted Terzaghi or Hewlett and Randolph.
6. `foundation.py` calculates the foundation soil resistance and bearing check.
7. One strain method calculates geosynthetic strain: Giroud or Catenary.
8. `tension.py` calculates the required geosynthetic tension.
9. `report.py` creates a readable text calculation sheet.
10. The GUI shows the results and can save the report.

## Source files

### User interface and starting files

| File | What it does |
|---|---|
| `main.py` | Small starting point for the modular application. It opens the GUI from `gui.py`. |
| `gui.py` | Builds the desktop window, input form, method choices, results page, calculation details, and buttons such as Calculate, Clear, and Save Report. |
| `standalone_app.py` | A complete one-file version of the application. It contains its own user interface, validation, calculation formulas, and report creation. This is the version used by the batch launcher and packaged executable. |
| `run_project.bat` | Windows helper file. It checks that Python and Tkinter are available, then starts `standalone_app.py`. |

There are therefore two versions of the application in the project:

- the modular version, spread across several files and easier to study or
  extend; and
- the standalone version, kept in one file and used to make the downloadable
  executable.

### Calculation coordination and safety checks

| File | What it does |
|---|---|
| `calculation_engine.py` | Acts as the traffic controller. It calls validation, the selected stress method, the foundation check, the selected strain method, and the tension calculation in the correct order. It also collects intermediate steps and pass/fail checks for display. |
| `validation.py` | Checks common inputs, such as positive dimensions, valid friction angles, column spacing greater than column diameter, and a valid factor of safety. It gives plain-English error messages. |
| `foundation.py` | Calculates the load carried by the foundation soil, the ultimate and allowable bearing capacity, and whether the allowable capacity is sufficient. |
| `tension.py` | Calculates the tensile force required in the geosynthetic reinforcement. |
| `report.py` | Converts the inputs, equations, intermediate results, design checks, and final values into a text report that can be saved. |

### Vertical stress methods

| File | What it does |
|---|---|
| `methods/adapted_terzaghi.py` | Implements the Adapted Terzaghi method. It calculates an equivalent column width, critical height, arching coefficients, and vertical stress above the geosynthetic. It automatically selects the relevant height case. |
| `methods/critical_height.py` | Calculates Hcr either from the Table 10.4 factor and column spacing/width or from a user-entered critical height. |
| `methods/critical_height_conditions.py` | Provides the six selectable Table 10.4 critical-height conditions, including Chen factor ranges and Filz inputs. |
| `methods/hewlett_randolph.py` | Implements the Hewlett and Randolph method. It calculates stress at the crown of the soil arch and at the top of the column, then uses the greater value. This method needs the additional `Kp` value. |
| `methods/__init__.py` | Marks `methods` as a Python package so its calculation modules can be imported together. |

### Geosynthetic strain methods

| File | What it does |
|---|---|
| `strain_methods/giroud.py` | Calculates strain using the simplified Giroud formula. This is the default strain option used by the example. |
| `strain_methods/catenary.py` | Calculates strain using the Catenary method associated with John (1987). |
| `strain_methods/parabolic.py` | Contains a parabolic-method tension formula and supporting notes. It documents an additional stiffness-based calculation that is not used by the main calculation engine. |
| `strain_methods/__init__.py` | Marks `strain_methods` as a Python package so its modules can be imported. |

## Documentation, testing, and build files

| File or folder | What it does |
|---|---|
| `README.md` | Main project instructions: how to run the application, what the results mean, engineering cautions, and how to build the executable. |
| `README.txt` | Plain-text version of the project information for readers or tools that do not use Markdown. |
| `PROJECT_GUIDE.md` | This plain-language file-by-file guide. |
| `worked_example_test.py` | Runs the supplied worked example and compares the program's values with the printed reference values. It is a calculation check, not part of the normal user interface. |
| `requirements.txt` | Lists the extra package needed to build the executable. PyInstaller is listed here; Tkinter normally comes with Python on Windows. |
| `Pile_Supported_Embankment_Designer.spec` | PyInstaller recipe. It tells PyInstaller to package `standalone_app.py` as a windowed executable with the chosen name. |

## Generated and packaged folders

These folders are produced by running or building the project. They are not
where the main source code lives.

### `dist/`

Contains the finished Windows application:

`dist/Pile Supported Embankment Designer.exe`

This is the file an ordinary user opens.

### `build/`

Contains PyInstaller's temporary working files, such as:

- `.toc` files, which are lists of files and dependencies;
- `PYZ-00.pyz`, a bundled Python-code archive;
- `.pkg`, the packaged application data;
- `base_library.zip`, bundled standard-library files;
- `localpycs/`, PyInstaller support bytecode;
- `warn-...txt`, packaging warnings; and
- `xref-...html`, a report showing module relationships.

These files help create the executable. They are not normally opened by the
end user.

### `__pycache__/`

Python may create this folder automatically. It contains temporary compiled
copies of Python modules that help Python start them faster. It can normally be
deleted and will be recreated when needed.

## Important engineering terms in simple language

- **Embankment:** the raised earth structure being designed.
- **Column or pile:** a stiff support carrying part of the embankment load.
- **Load transfer platform:** a layer above the columns that spreads load.
- **Geosynthetic:** a strong manufactured sheet or grid that helps span between
  supports.
- **Soil arching:** the way soil transfers some load toward the columns instead
  of sending all of it to the soft soil.
- **Surcharge:** an additional load placed on top of the embankment.
- **Differential settlement:** the difference in settlement between supported
  points.
- **Factor of safety:** a margin used so the allowable capacity is lower than
  the theoretical failure capacity.
- **`Kp`:** a soil pressure coefficient needed only by the Hewlett and Randolph
  stress method. The application does not provide a universal default for it.

## Important limitations

The program is an academic and preliminary design tool. It does not replace a
site investigation, project-specific geotechnical assessment, structural
design, construction checks, or approval by a qualified engineer.

The worked-example test also records a known difference between some printed
values in the supplied reference and the values produced when its equation is
implemented as written. That difference is deliberately reported rather than
silently changing the formula to force a match.