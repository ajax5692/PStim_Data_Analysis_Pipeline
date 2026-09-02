import json
import os
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import TrainingSession
from .training_data_processing.extract_licking import (
    extractLicking_lickTriggeredReward,
)


def get_analysis_inputs(training_session):
    """
    Validate and retrieve analysis inputs from a TrainingSession instance.
    """
    bpod_file_path = Path(training_session.bpod_file_path)

    if not bpod_file_path.exists():
        raise FileNotFoundError(
            f"BPod session file does not exist on disk: {bpod_file_path}"
        )

    return {
        "training_session_id": training_session.pk,
        "bpod_file_path": str(bpod_file_path),
        "training_unit_range": training_session.training_unit_range,
        "animal_id": training_session.animal.animal_id,
        "training_date": str(training_session.training_date),
    }


def execute_training_analysis(training_session, output_dir=None):
    """
    Execute lick extraction and analysis for a given TrainingSession instance.
    Generates high-res plot figures and exported Excel trace data.
    """
    try:
        inputs = get_analysis_inputs(training_session)
        bpod_file = inputs["bpod_file_path"]

        if output_dir is None:
            media_root = getattr(settings, "MEDIA_ROOT", Path(settings.BASE_DIR) / "media")
            output_dir = (
                Path(media_root)
                / "training_analysis"
                / str(inputs["animal_id"])
                / str(inputs["training_date"])
                / f"session_{training_session.pk}"
            )

        output_dir = Path(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        result = extractLicking_lickTriggeredReward(
            sessionfilename=bpod_file,
            show_plots=False,
            save_plots=True,
            output_dir=str(output_dir),
            export_excel=True,
            smooth_traces=True,
            smooth_window=6500,
            block_plots=False,
        )

        stem = Path(bpod_file).stem
        plot_file = output_dir / f"{stem}_lick_traces.png"
        raster_file = output_dir / f"{stem}_lick_occurrence.png"
        excel_file = output_dir / f"Individual_licking_traces_{stem}.xlsx"

        # Construct relative media URLs or relative paths if under MEDIA_ROOT
        media_root_str = str(getattr(settings, "MEDIA_ROOT", ""))
        def to_relative_media_path(full_path):
            p = str(full_path)
            if media_root_str and p.startswith(media_root_str):
                rel = os.path.relpath(p, media_root_str).replace("\\", "/")
                return f"{settings.MEDIA_URL.rstrip('/')}/{rel}"
            return p

        training_session.output_plot_path = to_relative_media_path(plot_file) if plot_file.exists() else ""
        training_session.output_raster_path = to_relative_media_path(raster_file) if raster_file.exists() else ""
        training_session.output_excel_path = to_relative_media_path(excel_file) if excel_file.exists() else ""
        training_session.output_log_path = str(output_dir)

        # Also store images at the same folder location as the raw input file
        raw_input_dir = Path(bpod_file).parent
        if raw_input_dir.exists():
            try:
                import shutil
                if plot_file.exists():
                    shutil.copy2(plot_file, raw_input_dir / f"{stem}_lick_traces.png")
                if raster_file.exists():
                    shutil.copy2(raster_file, raw_input_dir / f"{stem}_lick_occurrence.png")
            except Exception as copy_err:
                print(f"Notice: Could not copy plot image to raw input folder {raw_input_dir}: {copy_err}")

        # Store structured metrics (stimulus onset to reward onset integral)
        intgr_stim = {str(k): round(float(v), 4) for k, v in result.get("intgrStimulus", {}).items()}

        training_session.metrics_json = {
            "n_trials": int(result.get("nTrials", 0)),
            "trials_with_lick": int(result.get("trialsWithLick", 0)),
            "excluded_trials": int(result.get("excludedTrials", 0)),
            "length_of_trial": round(float(result.get("lengthOfTrial", 0.0)), 2),
            "stimulus_onset": round(float(result.get("stimulus_onset", 0.0)), 2),
            "stimulus_duration": round(float(result.get("stimulus_duration", 0.0)), 2),
            "reward_onset": round(float(result.get("reward_onset", 0.0)), 2),
            "punish_onset": round(float(result.get("punish_onset", 0.0)), 2),
            "integral_stimulus": intgr_stim,
        }

        training_session.mark_completed()
        return training_session

    except KeyboardInterrupt:
        training_session.mark_failed("Analysis interrupted by user or worker shutdown.")
        raise

    except Exception as exc:
        training_session.mark_failed(str(exc))
        raise


def claim_next_pending_training_session():
    """
    Atomically find and claim the oldest pending TrainingSession.
    """
    with transaction.atomic():
        session = (
            TrainingSession.objects
            .select_for_update(skip_locked=True)
            .filter(status=TrainingSession.StatusChoices.PENDING)
            .order_by("created_at")
            .first()
        )

        if session is None:
            return None

        session.mark_running()
        return session


def process_next_training_analysis():
    """
    Fetch and execute the next pending training analysis job.
    """
    session = claim_next_pending_training_session()
    if session is None:
        return None

    execute_training_analysis(session)
    return session