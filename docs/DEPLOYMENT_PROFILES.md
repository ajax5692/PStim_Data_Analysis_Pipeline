# Deployment Profiles in PStim_DAP

PStim_DAP supports environment-driven deployment profiles via the `PSTIM_PROFILE` environment variable. This allows different experimental setups (e.g. standalone behavioral training computers, 2-photon imaging workstations, core animal tracking stations) to run only the relevant Django applications from a single codebase.

---

| Profile                | Active Modules                                                                        | Description                                                                                     |
| :--------------------- | :------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------- |
| **`CORE`**             | `animals_metadata`, `virus_metadata`                                                  | Base animal identification, health, vision checks, and viral injection tracking.                |
| **`IMAGING`**          | `animals_metadata`, `virus_metadata`, `imaging_metadata`                              | Core modules plus 2-photon acquisition sessions and MESC metadata.                              |
| **`IMAGING_ANALYSIS`** | `animals_metadata`, `virus_metadata`, `imaging_metadata`, `imaging_analysis_metadata` | Core modules, 2-photon acquisition, and Suite2P automated analysis runs.                        |
| **`TRAINING`**         | `animals_metadata`, `virus_metadata`, `training_metadata`                             | Core modules plus Bpod behavioral training, body weight tracking, and lick kinematics analysis. |
| **`FULL`** _(Default)_ | All 5 domain metadata apps                                                            | Complete laboratory pipeline with imaging, analysis, and behavioral training.                   |

> [!NOTE]
>
> - `training_data_processing` is an internal Python subpackage of `training_metadata`, not a separate Django app.
> - `imaging_analysis_metadata` depends on `imaging_metadata` and requires `imaging_metadata` to be active.
> - `PSTIM_PROFILE` accepts both `IMAGING_ANALYSIS` and `IMAGING ANALYSIS`.

---

## How to Select a Profile

Set `PSTIM_PROFILE` in your `.env` file or environment:

```ini
# .env
PSTIM_PROFILE=TRAINING
```

If `PSTIM_PROFILE` is omitted or empty, PStim_DAP defaults to **`FULL`** (the standard profile used in the primary laboratory).

If an invalid profile name is provided (e.g. `PSTIM_PROFILE=INVALID`), Django startup will fail immediately with an `ImproperlyConfigured` error listing valid choices.

---

## Architecture Principles

- **Single Source of Truth**: `INSTALLED_APPS` is dynamically populated at startup based on `PSTIM_PROFILE`. Templates, admin views, and URL routers automatically adapt to active apps without hard-coded profile checks.
- **No Git Forks**: Deployment profiles are configuration choices. Different laboratory workstations should never maintain long-lived Git branches simply to enable or disable apps.
