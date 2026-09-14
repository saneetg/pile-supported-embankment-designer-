# Pile-Supported Embankment Designer

A Windows desktop application for preliminary design checks of pile-supported and geosynthetic-reinforced embankments.

## Start the application

The easiest way to use the program is to download the Windows application:

[**Download Pile-Supported Embankment Designer**](https://github.com/saneetg/pile-supported-embankment-designer-/raw/main/dist/Pile_Supported_Embankment_Designer.exe)

After downloading:

1. Open the downloaded file.
2. If Windows shows a security message, select **More info** and then **Run anyway** if you trust the file.
3. The application will open. No Python installation is required.

The program works offline and does not need an internet connection after it has been downloaded.

## Using the program

1. Enter a project or design name.
2. Choose a design method.
3. Choose a strain method.
4. Enter the project values in the **Inputs** tab.
5. Select **Calculate**.
6. Review the results and design checks.
7. Open **Calculation Details** to review the equations and substitutions.
8. Select **Save Report** to save a text copy of the calculation sheet.

If you are trying the program for the first time, select **Load Example**. This fills the form with a complete example so you can see how the application works.

## Design methods

The application provides the following choices:

- Adapted Terzaghi method for vertical stress above the geosynthetic.
- Hewlett and Randolph method for vertical stress above the geosynthetic.
- Giroud simplified method for geosynthetic strain.
- Catenary method for geosynthetic strain.
- Foundation bearing-capacity and soil-arching checks.

When the Hewlett and Randolph method is selected, enter the `Kp` value requested by the form. This value depends on the embankment material and should come from the responsible engineer or the project design basis.

## What the results mean

The **Results** tab reports the main design values, including:

- Equivalent column width.
- Vertical stress above the geosynthetic.
- Foundation soil resistance.
- Geosynthetic tensile strain.
- Required geosynthetic tension.
- Soil arching and foundation bearing status.

The **Calculation Details** tab shows how each value was obtained. Use this tab when checking inputs, reviewing assumptions, or preparing a project record.

## Engineering notice

This application is intended for preliminary design and engineering review. It does not replace a site investigation, project-specific geotechnical assessment, structural design, construction checks, or approval by a qualified engineer.

Before using the results for construction, confirm:

- The design code and project requirements.
- Soil and groundwater conditions.
- Embankment and platform material properties.
- Column or pile layout and construction tolerances.
- Settlement, loading, and factor-of-safety assumptions.
- Geosynthetic properties and installation requirements.

## For users running the source code

The repository includes the complete application source. Python 3.9 or newer is required for this option.

```powershell
py -3 standalone_app.py
```

You can also double-click [`run_project.bat`](run_project.bat) in the project folder.

To create a new Windows executable from the source:

```powershell
py -3 -m pip install -r requirements.txt
py -3 -m PyInstaller --onefile --windowed --name Pile_Supported_Embankment_Designer standalone_app.py
```

The new executable will be placed in `dist\Pile_Supported_Embankment_Designer.exe`.

## Project files

- [`standalone_app.py`](standalone_app.py): complete single-file application.
- [`run_project.bat`](run_project.bat): Windows launch file for the source version.
- [`dist/`](dist/): downloadable Windows executable.
- [`worked_example_test.py`](worked_example_test.py): calculation check for the example values.
- [`requirements.txt`](requirements.txt): package used to build the executable.

## Support and changes

Keep a copy of the input values and saved report with each design review. When changing an equation or design method, run the worked-example check and have the change reviewed by a qualified engineer.
