#!/usr/bin/env python3
"""CLI entry point for scitex.media.render.

Usage:
    python -m scitex.media.render show figure.png --target terminal
    python -m scitex.media.render classify data.csv
    python -m scitex.media.render detect "Saved to /proj/fig.png" --root /proj
"""

import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description="SciTeX Media Render — detect, classify, and display media"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # show
    show_p = subparsers.add_parser("show", help="Display a media file")
    show_p.add_argument("path", help="File path to display")
    show_p.add_argument(
        "-t",
        "--target",
        choices=["terminal", "chat", "markdown"],
        default="terminal",
        help="Render target (default: terminal)",
    )
    show_p.add_argument("--root", help="Project root for chat target")
    show_p.add_argument("--alt", default="", help="Alt text for markdown images")

    # classify
    cls_p = subparsers.add_parser("classify", help="Classify a file by media type")
    cls_p.add_argument("path", help="File path to classify")

    # detect
    det_p = subparsers.add_parser("detect", help="Detect media refs in text")
    det_p.add_argument("text", help="Text to scan for media paths")
    det_p.add_argument("--root", required=True, help="Project root path")

    args = parser.parse_args()

    if args.command == "show":
        from . import show

        result = show(args.path, target=args.target, root_path=args.root, alt=args.alt)
        if args.target != "terminal":
            print(result)

    elif args.command == "classify":
        from . import classify

        ref = classify(args.path)
        print(json.dumps(ref, indent=2) if ref else "null")

    elif args.command == "detect":
        from . import detect

        refs = detect(args.text, root_path=args.root)
        print(json.dumps(refs, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

# EOF
