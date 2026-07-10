# Low-Cost Internet-Enabled I–V Curve Tracer (Ćuk Converter Based)

A University of Southampton research project under Dr. Vun Jack.

This project presents the design and implementation of a **portable, low-cost, internet-enabled I–V curve tracer** for photovoltaic (PV) modules/cells, using a **Ćuk-converter-based electronic load** and a cloud-connected software stack for data visualization and access.

---

## Project Overview

Characterizing the **I–V (current–voltage)** and **P–V (power–voltage)** behavior of solar devices is essential for:

- performance assessment,
- fault detection,
- aging analysis,
- and validating PV operating conditions against expected characteristics.

Conventional laboratory tracers are often expensive and non-portable.  
This project focuses on a practical alternative that is:

- **low-cost**,
- **portable**,
- **internet-enabled**,
- and suitable for **field and educational use**.

---

## Images

## Device Setup
![Device setup](Picture/Picture1-coloured.jpg)

## System Block Diagram
![System block diagram](Picture/system-diagram.png)

---

## Key Features

- Portable IV tracing hardware
- Ćuk converter based controllable load behavior
- Automated sweep for I–V data acquisition
- Computation of P–V characteristics from sampled data
- Cloud-connected data upload and storage
- Web interface for remote data display and access
- Low-cost architecture suitable for research and teaching environments

---

## System Architecture

The system is composed of:

1. **PV under test**
2. **Power stage / electronic load (Ćuk converter based)**
3. **Sensing and embedded control**
4. **Data transfer to cloud**
5. **Web-based visualization layer**

High-level flow:

- The controller performs an electrical sweep of operating points.
- Voltage/current samples are measured across the sweep.
- I–V and derived P–V data are transmitted to cloud services.
- The web app retrieves and displays curves and related metadata.

---

## Repository Scope

This repository contains the software/web components used to support:

- data handling,
- cloud-connected access,
- and user-facing visualization of I–V characteristics.

Language composition:
- Python (primary backend/processing)
- JavaScript, HTML, CSS (frontend/web interface)
- Batchfile (auxiliary scripts)

---

## Typical Workflow

1. Connect PV device/module to the tracer hardware.
2. Run measurement sweep from the controller side.
3. Acquire and package sampled electrical data.
4. Upload data to cloud endpoint/storage.
5. Open web interface to inspect:
   - I–V curve,
   - P–V curve,
   - measurement session records.

---

## Getting Started

> Note: Steps below are generic and may be adapted to your local folder structure and runtime scripts in this repository.

### 1) Clone repository
```bash
git clone https://github.com/tanyc-2003/Low_Cost_IV_Curve_Tracer.git
cd Low_Cost_IV_Curve_Tracer
```

### 2) Create Python environment (recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3) Install dependencies
If a requirements file exists:
```bash
pip install -r requirements.txt
```

### 4) Run application
Use the project’s main Python/web startup script (check root files and run scripts in this repo).

---

## Research Context

This implementation is associated with the project/paper:

**“Design and implementation of a Portable Low-Cost Internet-Enabled I-V Curve Tracer Utilizing Ćuk Converter”**

The objective is to bridge hardware measurement and cloud software access in a compact, economical platform.

---

## Future Improvements

- richer experiment metadata and annotations
- multi-device comparison view
- automated fault classification support
- calibration assistant workflow
- exportable reports for lab/research submissions


---

## Acknowledgements

- University of Southampton
- Supervising research support under Dr. Vun Jack