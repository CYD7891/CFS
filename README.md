# Compressible Flow Studio (CFS)

Reliable compressible-flow calculator for isentropic flow, normal shocks, and oblique shocks — with batch CSV input, automated HTML reporting, optional PDF export, and test-backed engineering validation.

## Why this project
Compressible-flow formulas are easy to find, but reliable engineering tools are harder to build well.

This project focuses on turning standard gas-dynamics relations into a more professional workflow:
- batch case execution from CSV
- validation-aware computation
- graceful handling of bad cases
- automated report generation
- reproducible tests and CI

Instead of being just a collection of formulas, CFS is designed as a small engineering toolchain.

## Current capabilities
- Isentropic flow
  - `T/T0`
  - `P/P0`
  - `rho/rho0`
  - `A/A*`
  - inverse `A/A* -> M` for subsonic and supersonic branches
- Normal shock
  - `M2`
  - `p2/p1`
  - `rho2/rho1`
  - `T2/T1`
  - `p02/p01`
- Oblique shock
  - weak / strong branch
  - shock angle `beta`
  - `Mn1`, `Mn2`, `M2`
  - `p2/p1`, `rho2/rho1`, `T2/T1`, `p02/p01`
  - attached-shock validity check through `theta_max`
- Batch runner from CSV
- HTML report generation
- Optional PDF generation with graceful fallback
- Error summary for failed cases
- pytest test suite
- GitHub Actions CI

## Quickstart

### 1. Create a virtual environment
Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install
```bash
pip install -e ".[dev]"
```

### 3. Run the demo
```bash
python -m cfs demo --out build/demo
```

### 4. Run a batch case file
```bash
python -m cfs run examples/inputs_demo.csv --out build/run1
```

### 5. Run tests
```bash
pytest -q
```

## Example input format

**examples/inputs_demo.csv**

```csv
case_id,model,gamma,M,M1,theta_deg,branch
iso_1,isentropic,1.4,2.0,,,
ns_1,normal_shock,1.4,,2.0,,
os_1,oblique_shock,1.4,,3.0,15,weak
```

## Outputs

Each run produces:
- `results.csv`
- `report.html`
- `assets/isentropic_area_ratio.png`
- _optional_ `report.pdf` if PDF dependencies are available

## Example workflow

```bash
python -m cfs run examples/inputs_demo.csv --out build/run1
```

Then open:
- `build/run1/report.html`

## Engineering assumptions

CFS currently assumes:
- ideal gas
- calorically perfect gas (gamma = constant)
- steady, inviscid, adiabatic flow
- 1D relations for isentropic flow and normal shocks
- 2D attached oblique-shock model for wedge deflection cases

## Known limitations / failure modes

This tool does not currently model:
- real-gas effects
- variable-gamma effects
- chemistry / dissociation / ionization
- shock-boundary-layer interaction
- detached bow shocks beyond attached oblique-shock limits
- viscous duct effects such as Fanno flow
- heat-addition effects such as Rayleigh flow

Numerically sensitive regions:
- M → 1
- invalid shock inputs such as M₁ ≤ 1 for normal shock
- oblique-shock cases where theta > theta_max(M1, gamma)

These cases are either rejected or marked as ERROR in batch output.

## Reliability features

What makes this project more than a formula script:
- validation-aware functions
- branch-aware inverse area-ratio solver
- error isolation at the row level for batch jobs
- explicit reporting of failed cases
- unit tests for core relations and edge cases
- CI automation

## Verification philosophy

The project is verified through:
- closed-form compressible-flow relations
- regression-style numerical checks
- branch consistency checks
- batch workflow smoke tests
- report-generation smoke tests

## Repository structure

```
compressible-flow-studio/
  .github/workflows/ci.yml
  examples/
    inputs_demo.csv
  src/
    cfs/
      cli.py
      errors.py
      io/
      models/
      report/
  tests/
```

## Development roadmap

Planned next steps:
- better plots for oblique-shock behavior
- Fanno flow support
- Rayleigh flow support
- unit-aware user inputs with pint
- more formal golden-data validation tables
- richer report conclusions and comparison views

## Why this is a good portfolio project

This project demonstrates:
- physics / fluid mechanics knowledge
- numerical implementation
- CLI design
- test-driven engineering workflow
- report automation
- error handling and reliability thinking