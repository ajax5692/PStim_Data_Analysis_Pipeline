from pathlib import Path

from django.db import transaction

from .models import AnalysisRun


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
    
def execute_analysis(analysis_run):
    try:
        inputs = get_analysis_inputs(analysis_run)

        # Temporary placeholder.
        # Your Suite2p pipeline will eventually be called here.
        print("Analysis inputs:")
        print(inputs)

        analysis_run.mark_completed()

    except Exception as exc:
        analysis_run.mark_failed(str(exc))
        raise
    
def claim_next_pending_analysis():
    with transaction.atomic():
        analysis_run = (
            AnalysisRun.objects
            .select_for_update(skip_locked=True)
            .filter(status=AnalysisRun.StatusChoices.PENDING)
            .order_by("created_at")
            .first()
        )

        if analysis_run is None:
            return None

        analysis_run.mark_running()

        return analysis_run
    
def process_next_analysis():
    analysis_run = claim_next_pending_analysis()

    if analysis_run is None:
        return None

    execute_analysis(analysis_run)

    return analysis_run