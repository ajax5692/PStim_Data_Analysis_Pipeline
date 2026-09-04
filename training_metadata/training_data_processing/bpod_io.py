"""
Low-level MATLAB struct deserialization and timing extraction utilities
for Bpod SessionData files.
"""

from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import numpy.typing as npt
import scipy.io as sio


def _get_field(obj: Any, field_name: str, default: Any = None) -> Any:
    """Safely retrieve a field from a MATLAB struct or dictionary."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(field_name, default)
    if hasattr(obj, field_name):
        return getattr(obj, field_name)
    return default


def _has_field(obj: Any, field_name: str) -> bool:
    """Check if a field exists in a MATLAB struct or dictionary."""
    if obj is None:
        return False
    if isinstance(obj, dict):
        return field_name in obj
    return hasattr(obj, field_name)


def _to_1d_array(val: Any) -> npt.NDArray[np.float64]:
    """Ensure input is converted to a 1D numpy array of floats."""
    if val is None:
        return np.array([], dtype=np.float64)
    return np.atleast_1d(val).astype(np.float64).flatten()


def _to_2d_array(val: Any) -> npt.NDArray[np.float64]:
    """Ensure input is converted to a 2D numpy array of floats."""
    if val is None:
        return np.empty((0, 0), dtype=np.float64)
    return np.atleast_2d(val).astype(np.float64)


def _integrate_trapz(
    x: npt.NDArray[np.float64],
    y: npt.NDArray[np.float64],
    t1: Optional[float],
    t2: Optional[float],
) -> float:
    """
    Calculate the trapezoidal integral of y(x) between x ~= t1 and x ~= t2.
    Matches MATLAB trapz(x(ix1:ix2), y(ix1:ix2)).

    Args:
        x: 1D array of timestamps.
        y: 1D array of signal amplitudes.
        t1: Lower bound integration timestamp.
        t2: Upper bound integration timestamp.

    Returns:
        Computed scalar area under the curve.
    """
    if len(x) == 0 or len(y) == 0 or t1 is None or t2 is None or t1 >= t2:
        return 0.0
    ix1 = int(np.argmin(np.abs(x - t1)))
    ix2 = int(np.argmin(np.abs(x - t2)))
    if ix1 > ix2:
        ix1, ix2 = ix2, ix1
    if ix1 == ix2:
        return 0.0
    return float(np.trapezoid(y[ix1 : ix2 + 1], x[ix1 : ix2 + 1]))


def load_bpod_session(sessionfilename: Union[str, Path]) -> Any:
    """
    Load a Bpod .mat session file and extract the SessionData struct.

    Args:
        sessionfilename: Absolute or relative path to the Bpod .mat file.

    Returns:
        SessionData object parsed from MATLAB format.

    Raises:
        FileNotFoundError: If the file does not exist on disk.
        ValueError: If MATLAB parsing fails.
        KeyError: If SessionData key is absent.
    """
    file_path = Path(sessionfilename)
    if not file_path.exists():
        raise FileNotFoundError(f"Session file not found: {file_path}")

    try:
        mat = sio.loadmat(str(file_path), squeeze_me=True, struct_as_record=False)
        if "SessionData" in mat:
            return mat["SessionData"]
    except Exception as e:
        raise ValueError(f"Could not load SessionData from {file_path}: {e}")

    raise KeyError("SessionData struct not found in MAT file.")


def determine_session_timing(
    session_data: Any,
    selected_trials: List[int],
) -> Tuple[float, float, float, float, float, float, float]:
    """
    Determine trial length, event onsets, and stimulus boundaries across selected trials.

    Args:
        session_data: The Bpod SessionData object.
        selected_trials: List of 1-based trial numbers to evaluate.

    Returns:
        Tuple of (lengthOfTrial, so, so2, ro, po, visStimStart, visStimEnd).
    """
    length_of_trial = 0.0
    ro = 0.0
    po = 0.0
    so = 0.0
    so2 = 0.0

    for trial_num in selected_trials:
        idx = trial_num - 1
        trial = session_data.RawEvents.Trial[idx]
        states = trial.States
        events = trial.Events

        if _has_field(states, "WaitingForTrigger_Start"):
            wfts = _to_1d_array(_get_field(states, "WaitingForTrigger_Start"))
            lag_init = float(wfts[1]) if len(wfts) > 1 else 0.0
        elif _has_field(states, "WaitingForTrigger"):
            wft = _to_1d_array(_get_field(states, "WaitingForTrigger"))
            lag_init = float(wft[1]) if len(wft) > 1 else 0.0
        elif _has_field(states, "InitialDelay"):
            init_delay = _to_2d_array(_get_field(states, "InitialDelay"))
            lag_init = float(init_delay[-1, 0]) if init_delay.size > 0 else 0.0
        else:
            lag_init = 0.0

        tup = _to_1d_array(_get_field(events, "Tup"))
        cur_trial_len = (tup[-1] - lag_init) if len(tup) > 0 else 0.0
        if length_of_trial < cur_trial_len:
            length_of_trial = cur_trial_len

        if _has_field(states, "DeliverReward"):
            rew = _to_1d_array(_get_field(states, "DeliverReward"))
            if len(rew) > 0 and not np.isnan(rew[0]):
                ro = round(float(rew[0] - lag_init), 2)

        if _has_field(states, "DeliverPunish"):
            pun = _to_1d_array(_get_field(states, "DeliverPunish"))
            if len(pun) > 0 and not np.isnan(pun[0]):
                po = round(float(pun[0] - lag_init), 2)

        if _has_field(states, "SummonVideo"):
            sv = _to_1d_array(_get_field(states, "SummonVideo"))
            if len(sv) > 0 and not np.isnan(sv[0]):
                so = round(float(sv[0] - lag_init), 2)
                so2 = round(float(sv[1] - sv[0]), 2) if len(sv) > 1 else 0.0
        elif _has_field(states, "DeliverStimulus"):
            ds = _to_1d_array(_get_field(states, "DeliverStimulus"))
            if len(ds) > 0 and not np.isnan(ds[0]):
                so = round(float(ds[0] - lag_init), 2)

    if so > 0:
        vis_stim_start = so
        vis_stim_end = so + (so2 if so2 > 0 else 3.0)
    else:
        vis_stim_start = 3.55
        vis_stim_end = 6.55

    return length_of_trial, so, so2, ro, po, vis_stim_start, vis_stim_end

