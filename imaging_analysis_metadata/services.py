from pathlib import Path


def get_analysis_inputs(analysis_run):
    mesc_file_path = Path(
        analysis_run.imaging_session.mesc_file_path
    )

    if not mesc_file_path.exists():
        raise FileNotFoundError(
            f"MESC file does not exist: {mesc_file_path}"
        )
        
    if analysis_run.default_diameter <= 0:
        raise ValueError(
            "Default diameter must be greater than 0."
        )
        
    if analysis_run.tau <= 0:
        raise ValueError(
            "Tau must be greater than 0."
        )

    return {
        "analysis_run_id": analysis_run.pk,
        "mesc_file_path": str(mesc_file_path),
        "unit_indices": analysis_run.unit_indices,
        "default_diameter": analysis_run.default_diameter,
        "tau": analysis_run.tau,
    }