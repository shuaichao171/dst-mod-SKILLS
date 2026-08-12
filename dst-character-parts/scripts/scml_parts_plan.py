#!/usr/bin/env python3
"""Extract a deterministic part plan from a Spriter SCML file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from PIL import Image
except ImportError:  # The plan still works; source alpha metadata is optional.
    Image = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scml", type=Path, help="Input Spriter .scml file")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON plan")
    return parser.parse_args()


def number(value: str | None, default: float = 0.0) -> int | float:
    if value is None:
        return default
    parsed = float(value)
    return int(parsed) if parsed.is_integer() else parsed


def main() -> int:
    args = parse_args()
    scml = args.scml.resolve()
    root = ET.parse(scml).getroot()
    folders = []
    total_files = 0

    for folder in sorted(root.findall("folder"), key=lambda node: int(node.get("id", "0"))):
        files = []
        for file_node in sorted(folder.findall("file"), key=lambda node: int(node.get("id", "0"))):
            name = (file_node.get("name") or "").replace("\\", "/")
            file_data = {
                "id": int(file_node.get("id", "0")),
                "path": name,
                "width": int(number(file_node.get("width"), 0)),
                "height": int(number(file_node.get("height"), 0)),
                "pivot_x": number(file_node.get("pivot_x"), 0.0),
                "pivot_y": number(file_node.get("pivot_y"), 1.0),
            }
            source_png = scml.parent.joinpath(*name.split("/"))
            if Image is not None and source_png.is_file():
                with Image.open(source_png) as source_image:
                    file_data["source_mode"] = source_image.mode
                    if "A" in source_image.getbands():
                        source_bbox = source_image.getchannel("A").getbbox()
                        file_data["source_alpha_bbox"] = list(source_bbox) if source_bbox else None
                        file_data["allow_empty_alpha"] = source_bbox is None
            files.append(file_data)
        total_files += len(files)
        folders.append(
            {
                "id": int(folder.get("id", "0")),
                "name": folder.get("name") or "",
                "files": files,
            }
        )

    payload = {
        "schema_version": 1,
        "source_scml": scml.name,
        "source_sha256": hashlib.sha256(scml.read_bytes()).hexdigest(),
        "folder_count": len(folders),
        "file_count": total_files,
        "folders": folders,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"folders={len(folders)} files={total_files} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
