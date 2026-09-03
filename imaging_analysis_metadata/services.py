import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.db import transaction

from .models import AnalysisRun


def get_analysis_inputs(analysis_run: AnalysisRun) -> Dict[str, Any]:
    """
    Validate and retrieve input parameters for an AnalysisRun instance.

    Args:
        analysis_run: The AnalysisRun database model instance.

    Returns:
        A dictionary containing validated paths and numerical parameters.

    Raises:
        FileNotFoundError: If the raw .mesc file cannot be found on disk.
        ValueError: If default diameter or tau are less than or equal to zero.
    """
    mesc_file_path = Path(analysis_run.imaging_session.mesc_file_path)

    if not mesc_file_path.exists():
        raise FileNotFoundError(
            f"MESC file does not exist on disk: {mesc_file_path}"
        )

    if analysis_run.default_diameter <= 0:
        raise ValueError("Default diameter must be greater than 0.")

    if analysis_run.tau <= 0:
        raise ValueError("Tau must be greater than 0.")

    return {
        "analysis_run_id": analysis_run.pk,
        "mesc_file_path": str(mesc_file_path),
        "unit_indices": analysis_run.unit_indices,
        "default_diameter": analysis_run.default_diameter,
        "tau": analysis_run.tau,
    }


def build_analysis_command(analysis_run: AnalysisRun, result_file: Path) -> List[str]:
    """
    Construct the CLI command list to execute the Suite2P analysis runner.

    Args:
        analysis_run: The target AnalysisRun model instance.
        result_file: Path where the runner will write its JSON result.

    Returns:
        A list of command-line arguments ready for subprocess invocation.
    """
    inputs = get_analysis_inputs(analysis_run)

    default_python = (
        r"C:\Users\abhrajyoti.chakrabarti\Documents"
        r"\suite2p_venv\suite2p\.venv\Scripts\python.exe"
    )
    default_runner = (
        r"C:\Users\abhrajyoti.chakrabarti\Documents"
        r"\suite2p_venv\suite2p\customScripts\analysis_runner.py"
    )

    suite2p_python = getattr(settings, "SUITE2P_PYTHON_PATH", default_python)
    analysis_runner = getattr(settings, "SUITE2P_RUNNER_SCRIPT", default_runner)

    command = [
        str(suite2p_python),
        str(analysis_runner),
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


def run_suite2p_analysis(analysis_run: AnalysisRun) -> Dict[str, Any]:
    """
    Execute Suite2P registration as an isolated subprocess and parse JSON output.

    Args:
        analysis_run: The target AnalysisRun model instance.

    Returns:
        Parsed JSON dictionary with output paths and calculated frame rate.

    Raises:
        RuntimeError: If Suite2P exits with a non-zero code or omits result JSON.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        result_file = Path(temp_dir) / "imaging_analysis_result.json"
        command = build_analysis_command(analysis_run, result_file)

        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if proc.returncode != 0:
            error_details = proc.stderr.strip() or proc.stdout.strip() or f"Process exited with code {proc.returncode}"
            raise RuntimeError(f"Suite2P analysis failed: {error_details}")

        if not result_file.exists():
            raise RuntimeError(
                "Suite2P completed without producing an analysis result file."
            )

        result: Dict[str, Any] = json.loads(
            result_file.read_text(encoding="utf-8")
        )

        return result


def execute_analysis(analysis_run: AnalysisRun) -> AnalysisRun:
    """
    Execute analysis and update AnalysisRun instance fields and status.

    Args:
        analysis_run: The AnalysisRun database instance to process.

    Returns:
        The updated AnalysisRun instance.
    """
    try:
        result = run_suite2p_analysis(analysis_run)

        analysis_run.frame_rate = round(float(result["frame_rate"]), 2)
        analysis_run.output_log_path = result.get("parameter_log_path", "")
        analysis_run.output_path = result.get("output_path", "")

        analysis_run.save(
            update_fields=[
                "frame_rate",
                "output_log_path",
                "output_path",
            ]
        )

        analysis_run.mark_completed()
        return analysis_run

    except KeyboardInterrupt:
        analysis_run.mark_failed("Analysis interrupted by user or worker shutdown.")
        raise

    except Exception as exc:
        analysis_run.mark_failed(str(exc))
        raise


def claim_next_pending_analysis() -> Optional[AnalysisRun]:
    """
    Atomically find and claim the oldest pending AnalysisRun using row-level locking.

    Returns:
        The claimed AnalysisRun in RUNNING status, or None if queue is empty.
    """
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


def process_next_analysis() -> Optional[AnalysisRun]:
    """
    Claim and execute the next pending analysis job in the queue.

    Returns:
        The processed AnalysisRun, or None if no pending jobs were found.
    """
    analysis_run = claim_next_pending_analysis()
    if analysis_run is None:
        return None

    execute_analysis(analysis_run)
    return analysis_run