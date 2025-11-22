#!/usr/bin/env python3

import argparse
import sys
import unicodedata
from pathlib import Path


def build_explicit_map() -> dict[str, str]:
    mapping: dict[str, str] = {}

    # Quotes
    mapping["“"] = '"'
    mapping["”"] = '"'
    mapping["„"] = '"'
    mapping["«"] = '"'
    mapping["»"] = '"'
    mapping["‘"] = "'"
    mapping["’"] = "'"
    mapping["‚"] = "'"
    mapping["′"] = "'"
    mapping["″"] = '"'

    # Dashes / hyphens
    mapping["–"] = "-"
    mapping["—"] = "-"
    mapping["‐"] = "-"
    mapping["‑"] = "-"
    mapping["‒"] = "-"
    mapping["→"] = "->"

    # Ellipsis
    mapping["…"] = "..."

    # Misc symbols
    mapping["®"] = "(R)"
    mapping["©"] = "(C)"
    mapping["™"] = "TM"
    mapping["·"] = "*"
    mapping["•"] = "*"
    mapping["✓"] = "v"
    mapping["✗"] = "x"

    return mapping


def replace_non_ascii(
    text: str,
    explicit_map: dict[str, str],
) -> tuple[str, list[tuple[int, int, str]]]:
    out_chars: list[str] = []
    issues: list[tuple[int, int, str]] = []

    line: int = 1
    col: int = 1

    for ch in text:
        if ch == "\n":
            out_chars.append(ch)
            line += 1
            col = 1
            continue

        if ord(ch) < 128:
            out_chars.append(ch)
            col += 1
            continue

        replacement: str | None = None

        if ch in explicit_map:
            replacement = explicit_map[ch]
        else:
            decomposed: str = unicodedata.normalize("NFKD", ch)
            ascii_only: list[str] = [c for c in decomposed if ord(c) < 128]
            if len(ascii_only) > 0:
                replacement = "".join(ascii_only)

        if replacement is None:
            issues.append((line, col, ch))
            out_chars.append(ch)
            col += 1
        else:
            out_chars.append(replacement)
            col += len(replacement)

    return "".join(out_chars), issues


def process_file(path: Path, explicit_map: dict[str, str]) -> list[tuple[int, int, str]]:
    try:
        original_text: str = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"Error reading {path}: {exc}", file=sys.stderr)
        return []

    new_text, issues = replace_non_ascii(text=original_text, explicit_map=explicit_map)

    try:
        path.write_text(new_text, encoding="utf-8")
    except Exception as exc:
        print(f"Error writing {path}: {exc}", file=sys.stderr)

    return issues


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace non-ASCII characters in files with ASCII equivalents.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Files to process.",
    )
    args = parser.parse_args()

    explicit_map: dict[str, str] = build_explicit_map()
    all_issues: list[tuple[str, int, int, str]] = []

    for path_str in args.files:
        path = Path(path_str)
        if not path.is_file():
            print(f"Skipping non-file: {path}", file=sys.stderr)
            continue

        issues = process_file(path=path, explicit_map=explicit_map)
        for line, col, ch in issues:
            all_issues.append((str(path), line, col, ch))

    if len(all_issues) > 0:
        print("Non-ASCII characters without automatic replacement:", file=sys.stderr)
        for filename, line, col, ch in all_issues:
            codepoint: int = ord(ch)
            display: str = ascii(ch)[1:-1]
            print(
                f"{filename}:{line}:{col}: '{display}' U+{codepoint:04X}",
                file=sys.stderr,
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
