#!/usr/bin/env python3
"""Audit DST character PNG parts against an SCML-derived plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: install the 'Pillow' package.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parts_root", type=Path, help="Root containing part PNG paths")
    parser.add_argument("--plan", type=Path, required=True, help="JSON from scml_parts_plan.py")
    parser.add_argument("--report", type=Path, required=True, help="Audit JSON output")
    parser.add_argument("--contact-sheet", type=Path, help="Optional PNG preview")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on errors")
    parser.add_argument("--columns", type=int, default=6)
    return parser.parse_args()


def expected_files(plan: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for folder in plan.get("folders", []):
        result.extend(folder.get("files", []))
    return sorted(result, key=lambda item: item["path"].casefold())


def edge_touches(alpha: Image.Image) -> list[str]:
    width, height = alpha.size
    edges = []
    if alpha.crop((0, 0, width, 1)).getbbox():
        edges.append("top")
    if alpha.crop((0, height - 1, width, height)).getbbox():
        edges.append("bottom")
    if alpha.crop((0, 0, 1, height)).getbbox():
        edges.append("left")
    if alpha.crop((width - 1, 0, width, height)).getbbox():
        edges.append("right")
    return edges


def checkerboard(size: tuple[int, int], cell: int = 12) -> Image.Image:
    image = Image.new("RGBA", size, (46, 46, 46, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=(72, 72, 72, 255))
    return image


def make_contact_sheet(items: list[dict[str, Any]], output: Path, columns: int) -> None:
    tile_w, tile_h, label_h = 180, 180, 30
    rows = max(1, math.ceil(len(items) / columns))
    sheet = Image.new("RGB", (columns * tile_w, rows * (tile_h + label_h)), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, item in enumerate(items):
        col, row = index % columns, index // columns
        x, y = col * tile_w, row * (tile_h + label_h)
        tile = checkerboard((tile_w, tile_h))
        with Image.open(item["absolute_path"]) as source:
            rgba = source.convert("RGBA")
            preview = ImageOps.contain(rgba, (tile_w - 16, tile_h - 16))
            px = (tile_w - preview.width) // 2
            py = (tile_h - preview.height) // 2
            tile.alpha_composite(preview, (px, py))
        sheet.paste(tile.convert("RGB"), (x, y))
        label = Path(item["path"]).name
        if len(label) > 26:
            label = label[:23] + "..."
        draw.text((x + 5, y + tile_h + 7), label, fill=(235, 235, 235), font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def main() -> int:
    args = parse_args()
    root = args.parts_root.resolve()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    expected = expected_files(plan)
    expected_paths = {item["path"].replace("\\", "/") for item in expected}
    results: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    contact_items: list[dict[str, Any]] = []

    for item in expected:
        relative = item["path"].replace("\\", "/")
        path = root.joinpath(*relative.split("/"))
        result: dict[str, Any] = {"path": relative, "status": "ok"}
        if not path.is_file():
            result["status"] = "missing"
            errors.append(f"missing: {relative}")
            results.append(result)
            continue

        with Image.open(path) as image:
            result["mode"] = image.mode
            result["width"], result["height"] = image.size
            expected_size = (int(item["width"]), int(item["height"]))
            result["expected_width"], result["expected_height"] = expected_size
            if image.size != expected_size:
                result["status"] = "size_mismatch"
                errors.append(f"size mismatch: {relative} {image.size} != {expected_size}")

            if "A" not in image.getbands():
                result["status"] = "no_alpha"
                errors.append(f"no alpha channel: {relative}")
            else:
                alpha = image.getchannel("A")
                bbox = alpha.getbbox()
                result["alpha_bbox"] = list(bbox) if bbox else None
                result["alpha_extrema"] = list(alpha.getextrema())
                if bbox is None:
                    if item.get("allow_empty_alpha", False):
                        result["status"] = "template_blank"
                        warnings.append(f"template blank placeholder: {relative}")
                    else:
                        result["status"] = "empty_alpha"
                        errors.append(f"empty alpha: {relative}")
                elif alpha.getextrema()[0] == 255:
                    result["status"] = "opaque_canvas"
                    errors.append(f"fully opaque canvas: {relative}")
                touches = edge_touches(alpha)
                result["edge_touches"] = touches
                if touches:
                    warnings.append(f"edge touch ({','.join(touches)}): {relative}")

        result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        result["absolute_path"] = str(path)
        results.append(result)
        contact_items.append({"path": relative, "absolute_path": str(path)})

    actual_paths = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*.png")
        if path.is_file()
    }
    unexpected = sorted(actual_paths - expected_paths, key=str.casefold)
    for relative in unexpected:
        warnings.append(f"unexpected png: {relative}")

    hashes: dict[str, list[str]] = {}
    for item in results:
        if item.get("sha256") and item.get("status") != "template_blank":
            hashes.setdefault(item["sha256"], []).append(item["path"])
    duplicate_groups = [paths for paths in hashes.values() if len(paths) > 1]
    for paths in duplicate_groups:
        warnings.append("duplicate png: " + ", ".join(paths))

    report = {
        "schema_version": 1,
        "parts_root": str(root),
        "plan": str(args.plan.resolve()),
        "expected_count": len(expected),
        "present_count": len(contact_items),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "duplicate_groups": duplicate_groups,
        "unexpected_pngs": unexpected,
        "files": [{k: v for k, v in item.items() if k != "absolute_path"} for item in results],
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    if args.contact_sheet:
        make_contact_sheet(contact_items, args.contact_sheet, max(1, args.columns))

    print(
        f"expected={len(expected)} present={len(contact_items)} "
        f"errors={len(errors)} warnings={len(warnings)} report={args.report}"
    )
    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
