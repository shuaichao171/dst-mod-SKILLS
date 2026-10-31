#!/usr/bin/env python3
"""直接读取当前安装的 DST scripts.zip：不解包、不写游戏目录、不生成缓存。

    python dst_scripts_zip.py info
    python dst_scripts_zip.py list --glob "components/*_replica.lua"
    python dst_scripts_zip.py grep "function Health:DoDelta" --glob "components/*.lua"
    python dst_scripts_zip.py show components/health.lua --lines 1:80
    python dst_scripts_zip.py extract components/health.lua --to ./health.lua

源码包位置：--zip 显式指定；否则取 --game-home 或环境变量 DST_GAME_HOME 下的
data/databundles/scripts.zip。成员名可写成 components/health.lua 或 scripts/components/health.lua。
只用 Python 标准库。
"""
import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

ZIP_REL = Path("data/databundles/scripts.zip")


def locate_zip(zip_path=None, game_home=None):
    if zip_path:
        path = Path(zip_path)
    else:
        home = game_home or os.environ.get("DST_GAME_HOME")
        if not home:
            raise ValueError("需要 --zip、--game-home 或环境变量 DST_GAME_HOME")
        path = Path(home) / ZIP_REL
    path = path.resolve()
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise ValueError(f"不是有效的 ZIP：{path}")
    return path


def normalize_member(name):
    """把用户输入统一成包内的 scripts/... 形式，拒绝绝对路径和 ..。"""
    p = PurePosixPath(name.replace("\\", "/").lstrip("/"))
    if any(part == ".." for part in p.parts):
        raise ValueError(f"成员名不能包含 ..：{name}")
    return str(p) if p.parts and p.parts[0] == "scripts" else str(PurePosixPath("scripts") / p)


class ScriptsZip:
    def __init__(self, path):
        self.path = Path(path)
        self.zf = zipfile.ZipFile(self.path)
        self.names = [n for n in self.zf.namelist() if not n.endswith("/")]

    def close(self):
        self.zf.close()

    def match(self, pattern=None):
        if not pattern:
            return list(self.names)
        pat = normalize_member(pattern)
        return [n for n in self.names if fnmatch.fnmatchcase(n, pat)]

    def read_text(self, member):
        name = normalize_member(member)
        try:
            return self.zf.read(name).decode("utf-8", "replace")
        except KeyError:
            raise ValueError(f"包内没有 {name}") from None

    def info(self):
        h = hashlib.sha256()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        build = None
        version = self.path.parents[2] / "version.txt"  # <home>/data/databundles/scripts.zip
        if version.is_file():
            build = version.read_text(encoding="utf-8", errors="replace").strip()
        return {"zip": str(self.path), "bytes": self.path.stat().st_size, "sha256": h.hexdigest(),
                "entries": len(self.names), "lua_files": sum(n.endswith(".lua") for n in self.names),
                "build": build}

    def grep(self, regex, pattern=None, ignore_case=False, context=0, limit=200):
        rx = re.compile(regex, re.I if ignore_case else 0)
        hits = []
        for name in self.match(pattern or "*.lua"):
            lines = self.zf.read(name).decode("utf-8", "replace").splitlines()
            for i, line in enumerate(lines):
                if rx.search(line):
                    lo, hi = max(0, i - context), min(len(lines), i + context + 1)
                    hits.append({"file": name, "line": i + 1,
                                 "text": line if not context else "\n".join(lines[lo:hi])})
                    if len(hits) >= limit:
                        return hits, True
        return hits, False


def parse_lines(spec, total):
    if not spec:
        return 1, total
    a, _, b = spec.partition(":")
    start = int(a) if a else 1
    end = int(b) if b else total
    return max(1, start), min(total, end)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="直接读取 DST scripts.zip（只读）")
    p.add_argument("--zip", help="scripts.zip 路径")
    p.add_argument("--game-home", help="DST 安装根目录（默认环境变量 DST_GAME_HOME）")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("info", help="源码包路径、大小、SHA-256、条目数与游戏 build")
    s = sub.add_parser("list", help="列出成员")
    s.add_argument("--glob", help="如 components/*.lua")
    s = sub.add_parser("grep", help="按正则搜索")
    s.add_argument("regex")
    s.add_argument("--glob", help="限定成员，默认 *.lua")
    s.add_argument("-i", "--ignore-case", action="store_true")
    s.add_argument("-C", "--context", type=int, default=0)
    s.add_argument("--max", type=int, default=200, help="最多返回条数")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("show", help="打印单个文件（带行号）")
    s.add_argument("member")
    s.add_argument("--lines", help="行范围，如 20:80")
    s = sub.add_parser("extract", help="导出单个文件；目标已存在时拒绝覆盖")
    s.add_argument("member")
    s.add_argument("--to", required=True)
    args = p.parse_args(argv)

    try:
        sz = ScriptsZip(locate_zip(args.zip, args.game_home))
    except ValueError as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 2
    try:
        if args.cmd == "info":
            print(json.dumps(sz.info(), ensure_ascii=False, indent=2))
        elif args.cmd == "list":
            for n in sz.match(args.glob):
                print(n)
        elif args.cmd == "grep":
            hits, truncated = sz.grep(args.regex, args.glob, args.ignore_case, args.context, args.max)
            if args.json:
                print(json.dumps({"hits": hits, "truncated": truncated}, ensure_ascii=False, indent=2))
            else:
                for h in hits:
                    print(f"{h['file']}:{h['line']}: {h['text']}")
                if truncated:
                    print(f"... 已达上限 {args.max} 条，缩小 --glob 或提高 --max", file=sys.stderr)
        elif args.cmd == "show":
            lines = sz.read_text(args.member).splitlines()
            start, end = parse_lines(args.lines, len(lines))
            width = len(str(end))
            for i in range(start, end + 1):
                print(f"{i:>{width}}  {lines[i - 1]}")
        elif args.cmd == "extract":
            target = Path(args.to)
            if target.exists():
                print(f"[错误] 目标已存在，不覆盖：{target}", file=sys.stderr)
                return 2
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(sz.read_text(args.member), encoding="utf-8", newline="")
            print(f"已导出 {normalize_member(args.member)} → {target}")
    except (ValueError, re.error) as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 2
    finally:
        sz.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
