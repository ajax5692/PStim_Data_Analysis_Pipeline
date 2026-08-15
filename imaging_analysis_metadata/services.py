import json
import subprocess
import tempfile
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


def build_analysis_command(analysis_run, result_file):
    inputs = get_analysis_inputs(analysis_run)

    suite2p_python = (
        r"C:\Users\abhrajyoti.chakrabarti\Documents"
        r"\suite2p_venv\suite2p\.venv\Scripts\python.exe"
    )

    analysis_runner = (
        r"C:\Users\abhrajyoti.chakrabarti\Documents"
        r"\suite2p_venv\suite2p\customScripts\analysis_runner.py"
    )

    command = [
        suite2p_python,
        analysis_runner,
        "--mesc-file",
        inputs["mesc_file_path"],
        "--units",
        *[str(unit) for unit in inputs["unit_indices"]],
        "--diameter",
        str(inputs["default_diameter"]),
        "--tau",
        str(inputs["tau"]),
        "--result-file",
        str(result_file),
    ]

    return command


def run_suite2p_analysis(analysis_run):
    with tempfile.TemporaryDirectory() as temp_dir:
        result_file = Path(temp_dir) / "analysis_result.json"

        command = build_analysis_command(
            analysis_run,
            result_file,
        )

        subprocess.run(
            command,
            check=True,
        )

        if not result_file.exists():
            raise RuntimeError(
                "Suite2p completed without producing an analysis result file."
            )

        result = json.loads(
            result_file.read_text(encoding="utf-8")
        )

        return result


def execute_analysis(analysis_run):
    try:
        result = run_suite2p_analysis(analysis_run)

        analysis_run.frame_rate = round(
            float(result["frame_rate"]),
            2,
        )
        analysis_run.output_log_path = result["parameter_log_path"]
        analysis_run.output_path = result["output_path"]

        analysis_run.save(
            update_fields=[
                "frame_rate",
                "output_log_path",
                "output_path",
            ]
        )

        analysis_run.mark_completed()

    except KeyboardInterrupt:
        analysis_run.mark_failed(
            "Analysis interrupted by user or worker shutdown."
        )
        raise

    except Exception as exc:
        analysis_run.mark_failed(str(exc))
        raise


def claim_next_pending_analysis():
    with transaction.atomic():
        analysis_run = (
            AnalysisRun.objects
            .select_for_update(skip_locked=True)
            .filter(
                status=AnalysisRun.StatusChoices.PENDING
            )
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