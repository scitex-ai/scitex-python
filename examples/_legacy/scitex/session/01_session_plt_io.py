#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-22 03:25:05 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io.py


"""Minimal Demonstration for scitex.{session,io,plt}"""

import numpy as np

import scitex as stx


def demo(filename, verbose=False):
    """Show metadata without QR code (just embedded)."""

    # matplotlib.pyplot wrapper.
    fig, ax = stx.plt.subplots()

    t = np.linspace(0, 2, 1000)
    signal = np.sin(2 * np.pi * 5 * t) * np.exp(-t / 2)

    ax.stx_line(t, signal)  # Original plot for automatic CSV export
    ax.set_xyt(
        "Time (s)",
        "Amplitude",
        "Clean Figure (metadata embedded, no QR overlay)",
    )

    # Saving: stx.io.save(obj, rel_path, **kwargs)
    stx.io.save(
        fig,
        filename,
        metadata={"exp": "s01", "subj": "S001"},  # with meatadata embedding
        symlink_to="./data",  # Symlink for centralized outputs
        verbose=verbose,  # Automatic terminal logging (no manual print())
    )
    fig.close()

    # Loading: stx.io.load(path)
    ldir = __file__.replace(".py", "_out")
    img, meta = stx.io.load(
        f"{ldir}/{filename}",
        verbose=verbose,
    )


@stx.session
def main(filename="demo.jpg", verbose=True):
    """Run demo for scitex.{session,plt,io}."""

    demo(filename, verbose=verbose)

    return 0


if __name__ == "__main__":
    main()


# (.env-3.11) (wsl) scitex-code $ ./examples/demo_session_plt_io.py -h
#
# usage: demo_session_plt_io.py [-h] [-f FILENAME] [-v VERBOSE]
#
# Run demo for scitex.{session,plt,io}.
#
# options:
#  -h, --help            show this help message and exit
#  -f FILENAME, --filename FILENAME
#                        (default: demo.jpg)
#  -v VERBOSE, --verbose VERBOSE
#                        (default: True)
#
# Global Variables Injected by @session Decorator:
#
#    CONFIG (DotDict)
#        Session configuration with ID, paths, timestamps
#        Access: CONFIG['key'] or CONFIG.key (both work!)
#
#        - CONFIG.ID
#            <SESSION_ID> (created at runtime, e.g., '2025Y-11M-18D-07h53m37s_Z5MR')
#        - CONFIG.FILE
#            /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io.py
#        - CONFIG.SDIR_OUT
#            /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out
#        - CONFIG.SDIR_RUN
#            /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/RUNNING/<SESSION_ID>
#        - CONFIG.PID
#            465420 (current Python process)
#        - CONFIG.ARGS
#            {'arg1': '<value>'} (parsed from command line)
#
#        CONFIG from YAML files:
#        - CONFIG.DEMO.demo (from ./config/DEMO.yaml)
#            {'xxx': 111, 'yyy': 222}
#        - CONFIG.CAPTURE.capture (from ./config/capture.yaml)
#            {'screenshot': {'quality': 85, 'monitor_id': 0,...
#
#    plt (module)
#        matplotlib.pyplot configured for session
#
#    COLORS (DotDict)
#        Color palette for consistent plotting
#        Access: COLORS.blue or COLORS['blue'] (both work!)
#
#        Available keys:
#            'black', 'blue', 'brown', 'gray', 'green', 'grey', 'lightblue', 'navy', 'orange', 'pink', 'purple', 'red', 'white', 'yellow'
#
#        Usage:
#            plt.plot(x, y, color=COLORS.blue)
#            plt.plot(x, y, color=COLORS['blue'])
#
#    rng (RandomStateManager)
#        Manages reproducible randomness
#
#    logger (SciTeXLogger)
#        Logger configured for your script

# (.env-3.11) (wsl) scitex-code $ ./examples/demo_session_plt_io.py
# ========================================
# SciTeX v2.1.3
# 2025Y-11M-18D-09h12m03s_HmH5 (PID: 466633)
#
# /home/ywatanabe/proj/scitex-code/./examples/demo_session_plt_io.py
#
# Arguments:
#     filename: demo.jpg
#     verbose: True
# ========================================
#
# INFO: ============================================================
# INFO: Injected Global Variables (available in your function):
# INFO:   • CONFIG - Session configuration dict
# INFO:       - CONFIG['ID']: 2025Y-11M-18D-09h12m03s_HmH5
# INFO:       - CONFIG['SDIR_RUN']: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/RUNNING/2025Y-11M-18D-09h12m03s_HmH5-main
# INFO:       - CONFIG['PID']: 466633
# INFO:   • plt - matplotlib.pyplot (configured for session)
# INFO:   • COLORS - CustomColors (for consistent plotting)
# INFO:   • rng - RandomStateManager (for reproducibility)
# INFO:   • logger - SciTeX logger (configured for your script)
# INFO: ============================================================
# INFO: Running main with injected parameters:
# INFO:     {'filename': 'str', 'verbose': 'bool'}
# INFO: 📝 Saving figure with metadata to: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/demo.jpg
# INFO:   • Auto-added URL: https://scitex.ai
# INFO:   • Embedded metadata: {'exp': 's01', 'subj': 'S001', 'url': 'https://scitex.ai'}
# SUCC: Saved to: ./examples/demo_session_plt_io_out/demo.csv (38.0 KiB)
# SUCC: Symlinked: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/demo.csv -> /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/demo.csv/demo.csv
# SUCC: Saved to: ./examples/demo_session_plt_io_out/demo.jpg (241.6 KiB)
# SUCC: Symlinked: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/demo.jpg -> /home/ywatanabe/proj/scitex-code/data/demo.jpg
# INFO: ✅ Loading image with metadata from: /home/ywatanabe/proj/scitex-code/./examples/demo_session_plt_io_out/demo.jpg
# INFO:   • Embedded metadata found:
# INFO:     - exp: s01
# INFO:     - subj: S001
# INFO:     - url: https://scitex.ai
#
# SUCC: Congratulations! The script completed: /home/ywatanabe/proj/scitex-code/examples/demo_session_plt_io_out/FINISHED_SUCCESS/2025Y-11M-18D-09h12m03s_HmH5-main

# (.env-3.11) (wsl) scitex-code $ ls -al ./data/demo.jpg
# lrwxrwxrwx 1 ywatanabe ywatanabe 44 Nov 18 09:12 ./data/demo.jpg -> ../examples/demo_session_plt_io_out/demo.jpg

# (.env-3.11) (wsl) scitex-code $ tree ./examples/demo_session_plt_io*
# ./examples/demo_session_plt_io_out
# ├── demo.csv
# ├── demo.jpg
# └── FINISHED_SUCCESS
#     └── 2025Y-11M-18D-09h12m03s_HmH5-main
#         ├── CONFIGS
#         │   ├── CONFIG.pkl
#         │   └── CONFIG.yaml
#         └── logs
#             ├── stderr.log
#             └── stdout.log
# ./examples/demo_session_plt_io.py  [error opening dir]
#
# 5 directories, 7 files
#
# (.env-3.11) (wsl) scitex-code $ head ./examples/demo_session_plt_io_out/demo.csvax_00_plot_line_0_line_x,ax_00_plot_line_0_line_y
# 0.0,0.0
# 0.06279040531731951,0.002002002002002002
# 0.12520711420365782,0.004004004004004004
# 0.18700423504710992,0.006006006006006006
# 0.24793881631482095,0.008008008008008008
# 0.30777180069339666,0.01001001001001001
# 0.3662689619330633,0.012012012012012012
# 0.4232018207282413,0.014014014014014014
# 0.4783485360573639,0.016016016016016016

# EOF
