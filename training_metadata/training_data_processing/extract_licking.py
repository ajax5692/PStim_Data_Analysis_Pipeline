"""
Python conversion of MATLAB function extractLicking_lickTriggeredReward.m

Extracts, corrects, aligns, and analyzes lick port data from Bpod SessionData files
for lick-triggered reward protocols (Go / No-Go tasks).
"""

import os
import sys
from pathlib import Path
import numpy as np
import scipy.io as sio
from scipy.signal import windows
import matplotlib.pyplot as plt
import pandas as pd


def _get_field(obj, field_name, default=None):
    """Safely get a field from a mat_struct or dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(field_name, default)
    if hasattr(obj, field_name):
        return getattr(obj, field_name)
    return default


def _has_field(obj, field_name):
    """Check if a field exists in a mat_struct or dict."""
    if obj is None:
        return False
    if isinstance(obj, dict):
        return field_name in obj
    return hasattr(obj, field_name)


def _to_1d_array(val):
    """Ensure value is a 1D numpy array of floats."""
    if val is None:
        return np.array([], dtype=float)
    arr = np.atleast_1d(val).astype(float).flatten()
    return arr


def _to_2d_array(val):
    """Ensure value is a 2D numpy array of floats."""
    if val is None:
        return np.empty((0, 0), dtype=float)
    arr = np.atleast_2d(val).astype(float)
    return arr


def _integrate_trapz(x, y, t1, t2):
    """
    Calculate the trapezoidal integral of y(x) between x ~= t1 and x ~= t2,
    matching MATLAB: in = trapz(x(ix1:ix2), y(ix1:ix2)).
    """
    if len(x) == 0 or len(y) == 0 or t1 is None or t2 is None or t1 >= t2:
        return 0.0
    ix1 = np.argmin(np.abs(x - t1))
    ix2 = np.argmin(np.abs(x - t2))
    if ix1 > ix2:
        ix1, ix2 = ix2, ix1
    if ix1 == ix2:
        return 0.0
    return float(np.trapezoid(y[ix1 : ix2 + 1], x[ix1 : ix2 + 1]))


def load_bpod_session(sessionfilename):
    """
    Load a Bpod .mat session file and extract SessionData.
    """
    if not os.path.exists(sessionfilename):
        raise FileNotFoundError(f"Session file not found: {sessionfilename}")

    try:
        mat = sio.loadmat(sessionfilename, squeeze_me=True, struct_as_record=False)
        if "SessionData" in mat:
            return mat["SessionData"]
    except Exception as e:
        raise ValueError(f"Could not load SessionData from {sessionfilename}: {e}")

    raise KeyError("SessionData struct not found in MAT file.")


def extractLicking_lickTriggeredReward(
    sessionfilename=None,
    start_trial=21,
    show_plots=True,
    save_plots=False,
    output_dir=None,
    export_excel=False,
    smooth_traces=True,
    smooth_window=6500,
    block_plots=True,
):
    """
    Python implementation of extractLicking_lickTriggeredReward.m

    Parameters
    ----------
    sessionfilename : str or Path, optional
        Path to the Bpod .mat session data file. If None, opens a file picker GUI.
    start_trial : int, default=21
        1-based trial index from which length and onset determination begins (MATLAB default: 21).
    show_plots : bool, default=True
        Whether to display matplotlib plot windows.
    save_plots : bool, default=False
        Whether to save figures as PNG/PDF files.
    output_dir : str or Path, optional
        Directory where exported figures and Excel files will be saved.
    export_excel : bool, default=False
        Whether to export downsampled licking traces to Excel (.xlsx).
    smooth_traces : bool, default=True
        Whether to apply Gaussian smoothing to averaged licking traces.
    smooth_window : int, default=6500
        Gaussian smoothing kernel size (6500 points = 0.65s at 10 kHz).
    block_plots : bool, default=True
        Whether to keep matplotlib plot windows open on screen.

    Returns
    -------
    dict
        Contains computed results, arrays, integrals, and figures.
    """
    if sessionfilename is None:
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            sessionfilename = filedialog.askopenfilename(
                title="Select the Bpod file",
                filetypes=[("MATLAB Files", "*.mat"), ("All Files", "*.*")],
            )
            root.destroy()
        except Exception:
            raise ValueError("No sessionfilename provided and GUI file picker unavailable.")

    if not sessionfilename:
        print("No file selected.")
        return None

    sessionfilename = str(sessionfilename)
    SessionData = load_bpod_session(sessionfilename)

    nTrials = int(SessionData.nTrials)
    trial_types_raw = _to_1d_array(SessionData.TrialTypes).astype(int)
    max_trial_type = int(np.max(trial_types_raw)) if len(trial_types_raw) > 0 else 1

    # Colors for raster plot
    tp = np.array([
        [0.0, 0.4, 0.2],  # Dark green - Go trial
        [0.85, 0.2, 0.15],  # Red - No-Go trial
    ])
    if max_trial_type > 2:
        extra_colors = plt.cm.tab10(np.linspace(0, 1, max_trial_type))[:, :3]
        tp = np.vstack([tp, extra_colors[2:]])

    lengthOfTrial = 0.0
    ro = 0.0  # reward onset
    po = 0.0  # punishment onset
    so = 0.0  # stim onset
    so2 = 0.0  # stim off / duration
    fileType = 1

    # Start index in 0-based indexing (MATLAB `for i=21:SessionData.nTrials`)
    start_idx = max(0, min(start_trial - 1, nTrials - 1))

    # PASS 1: Determine trial lengths and event onsets starting from start_trial
    for i in range(start_idx, nTrials):
        trial = SessionData.RawEvents.Trial[i]
        states = trial.States
        events = trial.Events

        # Prioritize WaitingForTrigger_Start (measurement sessions) over InitialDelay
        if _has_field(states, "WaitingForTrigger_Start"):
            wfts = _to_1d_array(_get_field(states, "WaitingForTrigger_Start"))
            lagInit = float(wfts[1]) if len(wfts) > 1 else 0.0
            fileType = 2
        elif _has_field(states, "WaitingForTrigger"):
            wft = _to_1d_array(_get_field(states, "WaitingForTrigger"))
            lagInit = float(wft[1]) if len(wft) > 1 else 0.0
            fileType = 3
        elif _has_field(states, "InitialDelay"):
            init_delay = _to_2d_array(_get_field(states, "InitialDelay"))
            lagInit = float(init_delay[-1, 0]) if init_delay.size > 0 else 0.0
            fileType = 1
        else:
            lagInit = 0.0

        tup = _to_1d_array(_get_field(events, "Tup"))
        curTrialLength = (tup[-1] - lagInit) if len(tup) > 0 else 0.0
        if lengthOfTrial < curTrialLength:
            lengthOfTrial = curTrialLength

        # Reward onset
        if _has_field(states, "DeliverReward"):
            rew = _to_1d_array(_get_field(states, "DeliverReward"))
            if len(rew) > 0 and not np.isnan(rew[0]):
                calc_ro = round(float(rew[0] - lagInit), 2)
                if ro != 0.0 and ro != calc_ro:
                    print(f"Reward onset differs across trials (trial {i+1}): {ro} vs {calc_ro}")
                ro = calc_ro

        # Punishment onset
        if _has_field(states, "DeliverPunish"):
            pun = _to_1d_array(_get_field(states, "DeliverPunish"))
            if len(pun) > 0 and not np.isnan(pun[0]):
                calc_po = round(float(pun[0] - lagInit), 2)
                if po != 0.0 and po != calc_po:
                    print(f"Punishment onset differs across trials (trial {i+1}): {po} vs {calc_po}")
                po = calc_po

        # Stimulus period
        if _has_field(states, "SummonVideo"):
            sv = _to_1d_array(_get_field(states, "SummonVideo"))
            if len(sv) > 0 and not np.isnan(sv[0]):
                calc_so = round(float(sv[0] - lagInit), 2)
                calc_so2 = round(float(sv[1] - sv[0]), 2) if len(sv) > 1 else 0.0
                if so != 0.0 and so != calc_so:
                    print(f"Stimulus onset differs across trials (trial {i+1}): {so} vs {calc_so}")
                if so2 != 0.0 and so2 != calc_so2:
                    print(f"Stimulus duration differs across trials (trial {i+1}): {so2} vs {calc_so2}")
                so = calc_so
                so2 = calc_so2
        elif _has_field(states, "DeliverStimulus"):
            ds = _to_1d_array(_get_field(states, "DeliverStimulus"))
            if len(ds) > 0 and not np.isnan(ds[0]):
                calc_so = round(float(ds[0] - lagInit), 2)
                if so != 0.0 and so != calc_so:
                    print(f"Stimulus delivery differs across trials (trial {i+1}): {so} vs {calc_so}")
                so = calc_so

    # Visual stimulus onset/offset relative to trial start
    if so > 0:
        visStimStart = so
        visStimEnd = so + (so2 if so2 > 0 else 3.0)
    else:
        visStimStart = 3.55
        visStimEnd = 6.55

    # Time axis: 0.1ms resolution
    dt = 0.0001
    x = np.arange(0, lengthOfTrial + dt, dt)
    Ylicktr = np.zeros((nTrials, len(x)), dtype=float)
    Excluded = np.zeros(nTrials, dtype=bool)
    trialsWithLick = 0
    trial_lick_events = {}

    # PASS 2: Extracting licking data across all trials
    for i in range(nTrials):
        trial = SessionData.RawEvents.Trial[i]
        states = trial.States
        events = trial.Events

        # Extract per-trial lag offset and end of trial
        if _has_field(states, "WaitingForTrigger_Start"):
            wfts = _to_1d_array(_get_field(states, "WaitingForTrigger_Start"))
            trial_lag = float(wfts[1]) if len(wfts) > 1 else 0.0
            endOfTrial = _to_1d_array(_get_field(states, "StillDrinking"))
            if len(endOfTrial) == 0:
                endOfTrial = _to_1d_array(_get_field(states, "ITI"))
        elif _has_field(states, "WaitingForTrigger"):
            wft = _to_1d_array(_get_field(states, "WaitingForTrigger"))
            trial_lag = float(wft[1]) if len(wft) > 1 else 0.0
            endOfTrial = _to_1d_array(_get_field(states, "StillDrinking"))
            if len(endOfTrial) == 0:
                endOfTrial = _to_1d_array(_get_field(states, "ITI"))
        elif _has_field(states, "InitialDelay"):
            init_delay = _to_2d_array(_get_field(states, "InitialDelay"))
            trial_lag = float(init_delay[-1, 0]) if init_delay.size > 0 else 0.0
            endOfTrial = _to_1d_array(_get_field(states, "ITI"))
            if len(endOfTrial) == 0:
                endOfTrial = _to_1d_array(_get_field(states, "StillDrinking"))
        else:
            trial_lag = 0.0
            endOfTrial = np.array([0.0, 0.0])

        if not _has_field(events, "Port1In"):
            continue

        PortIn = list(_to_1d_array(_get_field(events, "Port1In")))
        if len(PortIn) == 0:
            continue

        trialsWithLick += 1

        if _has_field(events, "Port1Out"):
            PortOut = list(_to_1d_array(_get_field(events, "Port1Out")))
        else:
            # Correction Case 2.1
            if len(PortIn) == 1 and len(endOfTrial) > 0 and PortIn[0] >= endOfTrial[0]:
                PortOut = [float(endOfTrial[-1])]
            else:
                Excluded[i] = True
                continue

        # Correction Case 1: Lick started before or at trial boundary
        corrOneNeeded = False
        if len(PortIn) > 0 and len(PortOut) > 0 and PortIn[0] > PortOut[0]:
            if len(PortOut) - 1 > 0:
                PortOut.pop(0)
            elif len(PortOut) - 1 == 0:
                corrOneNeeded = True

        # Correction Case 2: Lick ended after trial boundary (use final timestamp of StillDrinking/ITI)
        if len(PortIn) > 0 and len(PortOut) > 0 and PortIn[-1] > PortOut[-1]:
            if len(endOfTrial) > 0:
                PortOut.append(float(endOfTrial[-1]))

        if corrOneNeeded and len(PortOut) > 0:
            PortOut.pop(0)

        # Consistency checks
        if len(PortIn) != len(PortOut) or len(PortIn) == 0:
            Excluded[i] = True
            continue

        if not all(p_in < p_out for p_in, p_out in zip(PortIn, PortOut)):
            Excluded[i] = True
            continue

        licks = np.array(PortIn, dtype=float)
        licksOUT = np.array(PortOut, dtype=float)

        # Align licks with trial start (subtract trial_lag offset)
        licks = licks - trial_lag
        licksOUT = licksOUT - trial_lag

        valid_mask = licks >= 0
        licks = licks[valid_mask]
        licksOUT = licksOUT[valid_mask]

        if len(licks) == 0:
            trialsWithLick -= 1
            continue

        trial_lick_events[i] = licks

        y = np.zeros(len(x), dtype=float)
        for k in range(len(licks)):
            i1 = int(np.round(licks[k] * 1e4))
            i2 = int(np.round(licksOUT[k] * 1e4))
            i1 = max(0, min(i1, len(x) - 1))
            i2 = max(0, min(i2, len(x) - 1))
            if i2 >= i1:
                y[i1 : i2 + 1] = 1.0
        Ylicktr[i, :] = y

    # Gaussian Smoothing Kernel
    gw = windows.gaussian(smooth_window, std=(smooth_window - 1) / 5.0)
    gw = gw / np.sum(gw)

    # Average traces and calculate integrals per trial type
    intgrStimulus = {}
    intgrStimulus_mod = {}
    intgrPostReward = {}
    Ylicktr_avg = {}
    maxAmpl = 0.0

    for tt in range(1, max_trial_type + 1):
        type_mask = (trial_types_raw == tt) & (~Excluded)
        if np.any(type_mask):
            subset = Ylicktr[type_mask, :]
            y_mean = np.mean(subset, axis=0) if subset.shape[0] > 1 else subset[0, :]
            if smooth_traces:
                ygf = np.convolve(y_mean, gw, mode="same")
                Ylicktr_avg[tt] = ygf
                intgrStimulus[tt] = _integrate_trapz(x, ygf, so, ro)
                intgrStimulus_mod[tt] = _integrate_trapz(x, ygf, 5.0, 8.0)
                intgrPostReward[tt] = _integrate_trapz(x, ygf, ro, ro + (ro - so))
            else:
                Ylicktr_avg[tt] = y_mean
                intgrStimulus[tt] = _integrate_trapz(x, y_mean, so, ro)
                intgrStimulus_mod[tt] = _integrate_trapz(x, y_mean, 5.0, 8.0)
                intgrPostReward[tt] = _integrate_trapz(x, y_mean, ro, ro + (ro - so))

            if np.max(Ylicktr_avg[tt]) > maxAmpl:
                maxAmpl = float(np.max(Ylicktr_avg[tt]))

    # Console summary matching MATLAB format
    filename_base = os.path.basename(sessionfilename)
    print("\n" + "=" * 60)
    print(f"File: {filename_base}")
    print(f"Number of trials: {nTrials} trials")
    print(f"Licked in: {trialsWithLick - int(np.sum(Excluded))} trials")
    print(f"No lick in: {nTrials - trialsWithLick} trials")
    print(f"Excluded trials: {int(np.sum(Excluded))}")
    print("-" * 60)
    for tt in intgrStimulus_mod:
        label = "go trial" if tt == 1 else "no-go trial"
        print(f"Integral Stimulus period ({ro - so:.1f}s), {label} (type {tt}) curve: {intgrStimulus_mod[tt]:.3f}")
    for tt in intgrPostReward:
        label = "go trial" if tt == 1 else "no-go trial"
        print(f"Integral After Reward period ({ro - so:.1f}s), {label} (type {tt}) curve: {intgrPostReward[tt]:.3f}")
    print("=" * 60 + "\n")

    figs = []

    if show_plots or save_plots:
        # FIGURE 1: Individual lick occurrences / Raster Plot
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        if hasattr(fig1.canvas, "manager") and fig1.canvas.manager:
            fig1.canvas.manager.set_window_title(f"licks occurrence file: {filename_base}")

        # Visual Stimulus span
        ax1.axvspan(visStimStart, visStimEnd, color="#cccccc", alpha=0.8, label="Video", zorder=0)

        if ro > 0:
            ax1.axvline(ro, color="#777777", linestyle="--", linewidth=1.5, label="Reward", zorder=1)
        if po > 0:
            ax1.axvline(po, color="darkgray", linestyle="--", linewidth=1.5, label="Punishment", zorder=1)

        lgnd_plotted = set()
        for i in range(nTrials):
            if i in trial_lick_events and not Excluded[i]:
                tt = trial_types_raw[i]
                color = tp[tt - 1] if tt <= len(tp) else "blue"
                label = ("Go trials" if tt == 1 else "NoGo trials") if tt not in lgnd_plotted else None
                if label:
                    lgnd_plotted.add(tt)
                ax1.vlines(trial_lick_events[i], ymin=0, ymax=1, color=color, linewidth=1.2, label=label, zorder=2)

        ax1.set_ylim(0, 3)
        ax1.set_xlim(0, max(lengthOfTrial, 1.0))
        ax1.set_ylabel("Licking", fontsize=11)
        ax1.set_xlabel("Time (s)", fontsize=11)
        clean_stem = Path(sessionfilename).stem.replace("_", " ")
        ax1.set_title(f"Lick Occurrences - {clean_stem}", fontsize=12, fontweight="bold")
        ax1.legend(loc="upper right", frameon=False, fontsize=10)
        ax1.spines["top"].set_visible(False)
        ax1.spines["right"].set_visible(False)
        ax1.tick_params(direction="out")
        figs.append(fig1)

        # FIGURE 2: Averaged Licking Traces (Styled to match publication reference)
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        if hasattr(fig2.canvas, "manager") and fig2.canvas.manager:
            fig2.canvas.manager.set_window_title(f"licks traces file: {filename_base}")

        color_go = "#006837"    # Dark Green matching reference
        color_nogo = "#d73027"  # Crimson Red matching reference

        n_go = int(np.sum((trial_types_raw == 1) & (~Excluded)))
        n_nogo = int(np.sum((trial_types_raw == 2) & (~Excluded)))

        # Visual Stimulus span & Reward line
        ax2.axvspan(visStimStart, visStimEnd, color="#cccccc", alpha=0.8, label="Video", zorder=0)
        if ro > 0:
            ax2.axvline(ro, color="#777777", linestyle="--", linewidth=1.5, label="Reward", zorder=1)
        if po > 0:
            ax2.axvline(po, color="darkgray", linestyle="--", linewidth=1.5, label="Punishment", zorder=1)

        # Plot averaged traces
        if 1 in Ylicktr_avg:
            ax2.plot(x, Ylicktr_avg[1], color=color_go, linewidth=2.0, label=f"Go trials (={n_go})", zorder=3)
        if 2 in Ylicktr_avg:
            ax2.plot(x, Ylicktr_avg[2], color=color_nogo, linewidth=2.0, label=f"NoGo trials (={n_nogo})", zorder=3)

        for tt in range(3, max_trial_type + 1):
            if tt in Ylicktr_avg:
                ax2.plot(x, Ylicktr_avg[tt], linewidth=2.0, label=f"Trial type {tt}", zorder=3)

        # Exact matching axes limits and ticks
        x_max_view = 20.0 if lengthOfTrial >= 18.0 else max(lengthOfTrial, 1.0)
        ax2.set_xlim(0, x_max_view)
        ax2.set_xticks(np.arange(0, x_max_view + 1, 5))

        y_max_view = 0.30 if maxAmpl <= 0.295 else float(np.ceil(maxAmpl * 10) / 10)
        ax2.set_ylim(0, y_max_view)
        ax2.set_yticks(np.arange(0, y_max_view + 0.01, 0.05))

        ax2.set_ylabel("Licking", fontsize=11)
        ax2.set_xlabel("Time (s)", fontsize=11)
        clean_name = Path(sessionfilename).stem.replace("_", " ")
        ax2.set_title(f"Average licking trace - {clean_name}", fontsize=12, fontweight="bold")
        ax2.legend(loc="upper right", frameon=False, fontsize=10)
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.tick_params(direction="out")
        figs.append(fig2)

        if save_plots and output_dir:
            os.makedirs(output_dir, exist_ok=True)
            stem = Path(sessionfilename).stem
            fig1.savefig(os.path.join(output_dir, f"{stem}_lick_occurrence.png"), dpi=300, bbox_inches="tight")
            fig2.savefig(os.path.join(output_dir, f"{stem}_lick_traces.png"), dpi=300, bbox_inches="tight")

        if show_plots:
            plt.show(block=block_plots)

    # Optional Excel Export
    if export_excel:
        target_dir = output_dir if output_dir else os.path.dirname(sessionfilename)
        xls_name = f"Individual_licking_traces_{Path(sessionfilename).stem}.xlsx"
        xls_path = os.path.join(target_dir, xls_name)

        step = 500
        x_down = x[::step]
        Y_down = Ylicktr[:, ::step]

        data_dict = {"t": x_down}
        for i in range(nTrials):
            data_dict[f"Trial_{i+1}"] = Y_down[i, :]
        df_export = pd.DataFrame(data_dict)

        df_export.to_excel(xls_path, index=False)
        print(f"Licking data exported to: {xls_path}")

    return {
        "sessionfilename": sessionfilename,
        "nTrials": nTrials,
        "trialsWithLick": trialsWithLick,
        "excludedTrials": int(np.sum(Excluded)),
        "lengthOfTrial": lengthOfTrial,
        "time_axis": x,
        "Ylicktr": Ylicktr,
        "Ylicktr_avg": Ylicktr_avg,
        "Excluded": Excluded,
        "intgrStimulus": intgrStimulus,
        "intgrStimulus_mod": intgrStimulus_mod,
        "intgrPostReward": intgrPostReward,
        "stimulus_onset": so,
        "stimulus_duration": so2,
        "reward_onset": ro,
        "punish_onset": po,
        "figures": figs,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        extractLicking_lickTriggeredReward(sys.argv[1], show_plots=True)
    else:
        extractLicking_lickTriggeredReward()
