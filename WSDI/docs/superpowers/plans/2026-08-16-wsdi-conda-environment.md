# WSDI Conda Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install and verify an isolated Windows Conda environment that can execute the WSDI construction workflow without changing the existing Python 3.8 installation.

**Architecture:** Install Miniforge for the current Windows user and create a named `wsdi` environment pinned to Python 3.11. Install all packages from the construction document through `conda-forge`, then verify imports and read the supplied CSV, NetCDF, and GeoPackage files.

**Tech Stack:** Miniforge/Conda, Python 3.11, xarray, netCDF4, pandas, NumPy, GeoPandas, Pyogrio, Shapely, PyArrow, Matplotlib, JupyterLab

## Global Constraints

- Preserve `C:\Environment_tools\3.8.10\python.exe` and its installed packages.
- Install Miniforge for the current user without requiring administrator privileges.
- Create the environment with the exact name `wsdi` and Python 3.11.
- Use `conda-forge` for the scientific, NetCDF, and GIS dependency stack.
- Do not modify the supplied PDF, CSV, NetCDF, or GeoPackage inputs.

---

### Task 1: Install Miniforge

**Files:**
- Create outside workspace: `C:\Users\chenyu\miniforge3\`

**Interfaces:**
- Consumes: Windows Package Manager (`winget`)
- Produces: `C:\Users\chenyu\miniforge3\Scripts\conda.exe`

- [ ] **Step 1: Confirm the package identifier**

Run: `winget search --id CondaForge.Miniforge3 --exact`

Expected: one exact Miniforge3 package result.

- [ ] **Step 2: Install for the current user**

Run: `winget install --id CondaForge.Miniforge3 --exact --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity`

Expected: installation succeeds or reports that the package is already installed.

- [ ] **Step 3: Verify Conda directly**

Run: `C:\Users\chenyu\miniforge3\Scripts\conda.exe --version`

Expected: a Conda version is printed with exit code 0.

### Task 2: Create the isolated WSDI environment

**Files:**
- Create outside workspace: `C:\Users\chenyu\miniforge3\envs\wsdi\`
- Create: `environment.yml`

**Interfaces:**
- Consumes: Miniforge Conda executable
- Produces: `wsdi` environment with the documented dependency set

- [ ] **Step 1: Create the environment and install all dependencies**

Run:

```powershell
& 'C:\Users\chenyu\miniforge3\Scripts\conda.exe' create -n wsdi -c conda-forge --strict-channel-priority python=3.11 xarray netcdf4 pandas numpy geopandas pyogrio shapely pyarrow matplotlib jupyterlab -y
```

Expected: dependency resolution and installation complete with exit code 0.

- [ ] **Step 2: Verify the environment identity**

Run: `C:\Users\chenyu\miniforge3\Scripts\conda.exe run -n wsdi python --version`

Expected: Python 3.11.x.

- [ ] **Step 3: Save a portable environment specification**

Create `environment.yml` with the `wsdi` name, only the `conda-forge` channel, Python 3.11, and the ten documented Python packages.

Expected: `conda env create -f environment.yml` can reproduce the top-level dependency specification without embedding a machine-specific prefix.

### Task 3: Configure PowerShell access

**Files:**
- Modify outside workspace: current user's PowerShell profile through `conda init powershell`

**Interfaces:**
- Consumes: working Miniforge installation
- Produces: future PowerShell sessions in which `conda activate wsdi` is available

- [ ] **Step 1: Initialize Conda for PowerShell**

Run: `C:\Users\chenyu\miniforge3\Scripts\conda.exe init powershell`

Expected: Conda reports the user PowerShell profile as modified or unchanged.

- [ ] **Step 2: Verify activation without depending on profile reload**

Run: `C:\Users\chenyu\miniforge3\Scripts\conda.exe run -n wsdi python -c "import sys; print(sys.executable)"`

Expected: the executable path is inside `miniforge3\envs\wsdi`.

### Task 4: Verify imports and real input compatibility

**Files:**
- Read: `invest_panel_weo.csv`
- Read: `HadEX3-0-4_wsdi_ann_1961-1990.nc`
- Read: `World Bank Official Boundaries - Admin 0.gpkg`

**Interfaces:**
- Consumes: completed `wsdi` environment and the three supplied data inputs
- Produces: evidence that the environment can run the documented workflow

- [ ] **Step 1: Import every documented package**

Run a Python check inside `conda run -n wsdi` importing `xarray`, `netCDF4`, `pandas`, `numpy`, `geopandas`, `pyogrio`, `shapely`, `pyarrow`, `matplotlib`, and `jupyterlab`.

Expected: every import succeeds and package versions are printed.

- [ ] **Step 2: Read the three real data inputs**

Run a Python smoke test that reads the CSV, opens the NetCDF, and reads the `WB_GAD_ADM0` GeoPackage layer.

Expected: 1,827 CSV rows, HadEX3 version `3.0.4` with maximum year 2018, and 251 boundary features.

- [ ] **Step 3: Verify JupyterLab**

Run: `C:\Users\chenyu\miniforge3\Scripts\conda.exe run -n wsdi jupyter lab --version`

Expected: a JupyterLab version is printed with exit code 0.

- [ ] **Step 4: Record the handoff commands**

Document for the user that a new PowerShell window can run:

```powershell
conda activate wsdi
cd C:\Users\chenyu\Desktop\WSDI
jupyter lab
```

Expected: the user has concise commands to enter the verified environment and start work.
