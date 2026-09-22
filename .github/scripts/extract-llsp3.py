#!/usr/bin/env python3
"""Extract projectbody.json Python code from .llsp3 archives into code/txt."""

from __future__ import annotations

import json
import pathlib
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "code" / "txt"


def extract_archive(source: pathlib.Path) -> None:
    """Write the Python in projectbody.json to a same-named .txt file."""
    destination = OUTPUT_DIR / f"{source.stem}.txt"

    with zipfile.ZipFile(source) as archive:
        try:
            raw_projectbody = archive.read("projectbody.json")
        except KeyError as error:
            raise ValueError("projectbody.json is missing") from error

    try:
        projectbody = json.loads(raw_projectbody.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("projectbody.json is not valid UTF-8 JSON") from error

    if not isinstance(projectbody, dict) or not isinstance(projectbody.get("main"), str):
        raise ValueError("projectbody.json does not contain a string-valued 'main' field")

    destination.write_text(projectbody["main"].rstrip() + "\n", encoding="utf-8")
    print(f"Wrote {destination.relative_to(ROOT)}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    archives = sorted(
        path
        for path in ROOT.rglob("*.llsp3")
        if ".git" not in path.parts and OUTPUT_DIR not in path.parents
    )
    generated_names = {f"{archive.stem}.txt" for archive in archives}

    for archive in archives:
        try:
            extract_archive(archive)
        except (OSError, zipfile.BadZipFile, ValueError) as error:
            raise SystemExit(f"Could not extract {archive}: {error}") from error

    # Remove generated files whose source LLSP3 file was deleted.
    for generated in OUTPUT_DIR.glob("*.txt"):
        if generated.name not in generated_names:
            generated.unlink()
            print(f"Removed {generated.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
