# PStim_DAP (PhotoStim Data Analysis Pipeline)
⚙️🏗️ _**Workflow Construction Under Progress**_

PStim_DAP is a research-grade Django web application and data pipeline framework designed for optogenetics based experimental workflows. It integrates biological metadata tracking with automated two-photon calcium imaging analysis, connecting laboratory experiment logs directly to headless compute pipelines (Suite2p, OASIS, and neuronal ensemble estimation).

---

## 🔬 Experimental Workflow

1. **Vision Check:** Preliminary sweep visual stimulus screening.
2. **Viral Injection:** Stereotaxic delivery of optogenetic and calcium indicator constructs (e.g., GCaMP).
3. **Expression Check:** Fluorescence validation prior to behavioral tasks.
4. **Behavioral Training:** Tracking longitudinal task metrics and performance criteria.
5. **Multiplane Imaging:** High-speed, multiplane functional acquisition linked to institute storage.
6. **Post-Processing & Analysis:**
   * Automated/semi-automated ROI detection via **Suite2P**.
   * Calcium deconvolution and spike inference via **OASIS**.
   * Visually responsive neuronal ensemble identification.

---

## 📁 Architecture & Apps

The project is structured into three modular Django applications:

* `anjmals metadata`: Manages animal records, baseline visual checks, viral injection parameters, and expression quality.
* `imaging metadata`: Handles file pointers to raw multiplane HDF5 datasets on the institute server.
* `imaging analysis metadata`: Tracks auto-analysis processing states (`PENDING`, `RUNNING`, `COMPLETED/FAILED`), Suite2P configuration paths, OASIS spike matrices, and extracted ensemble metrics.

---

## 🛠️ Tech Stack

* **Backend & Web Dashboard:** Python, Django, Django REST Framework
* **Data Storage Model:** Relational SQL metadata indexing pointers to large-array files (HDF5, NumPy, Zarr)
* **Computational Pipeline:** Suite2P (ROI detection & custom classifier integration), OASIS (spike deconvolution), NumPy/SciPy

---
