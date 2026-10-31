#!/usr/bin/env python3
"""DST 模组静态检查：Lua 5.1 语法 + 组件/replica 冒号调用的方法声明核对。

    python dst_lua_check.py <模组目录或 .lua 文件> [...]
    python dst_lua_check.py <模组目录> --json > lua-check.json
    python dst_lua_check.py <模组目录> --strict        # NEEDS_REVIEW 也返回非零

语法：优先用 lupa 自带的 Lua 5.1（与游戏同版本，只编译不执行），其次 luaparser；都没有时跳过并注明。
声明核对：扫描 `components.X:Method(` 与 `replica.X:Method(`，到模组自己的 scripts/components/
和原版源码里找 X.lua / X_replica.lua 的方法定义。
- DECLARED：查到了定义，只说明方法存在，不检查参数、端别或运行时是否已添加该组件。
- NEEDS_REVIEW：没查到或无法确定（引擎原生组件、继承、依赖模组、PostInit 补丁等），需要人工追踪，不等于 Bug。

组件定义的查找顺序：被测模组自己的 scripts/ > --with 指定的依赖模组 > 原版源码。
原版源码：--source-dir（含 components/ 的 scripts 目录）> --zip > --game-home/DST_GAME_HOME 下的
scripts.zip > DST_DATA_DIR/scripts。都没有时只能核对模组自带的组件。
退出码：0 正常；1 有语法错误（--strict 时 NEEDS_REVIEW 也算）；2 参数或环境错误。
"""
import argparse
import fnmatch
import json
import os
import re
import sys
import zipfile
from pathlib import Path

DEFAULT_EXCLUDES = ("_ai_work", ".git", "node_modules")
CALL_RE = re.compile(r"\b(components|replica)\s*\.\s*([A-Za-z_]\w*)\s*:\s*([A-Za-z_]\w*)\s*\(")
DECL_RES = (
    re.compile(r"\bfunction\s+[A-Za-z_][\w.]*[:.]([A-Za-z_]\w*)\s*\("),   # function Health:DoDelta(
    # Health.DoDelta = function / Combat.CancelAttack = Combat.ResetCooldown / self.Foo = function
    re.compile(r"^[ \t]*[A-Za-z_]\w*\s*\.\s*([A-Za-z_]\w*)\s*=(?!=)", re.M),
)
BASE_RE = re.compile(r"\bClass\s*\(\s*([A-Za-z_]\w*)\s*,")
REQUIRE_RE = re.compile(r"""\blocal\s+([A-Za-z_]\w*)\s*=\s*require\s*\(?\s*["']components/(\w+)["']""")
MODIMPORT_RE = re.compile(r"""\bmodimport\s*\(?\s*["']([^"']+)["']""")
# 标准 Lua 5.1 的编译期上限，DST 引擎放宽了（原版 weather.lua 也会触发），只作提示
ENGINE_LIMIT_ERRORS = ("has more than 60 upvalues",)


# ---------------------------------------------------------------- 词法：去掉注释与字符串

def _long_bracket(text, i):
    """text[i] == '['：返回长括号的等号层级，不是长括号返回 None。"""
    m = re.match(r"\[(=*)\[", text[i:])
    return len(m.group(1)) if m else None


def strip_lua(text):
    """把注释和字符串内容替换成空格（保留换行，行号不变），便于正则扫描代码。"""
    out, i, n = [], 0, len(text)

    def blank(seg):
        return re.sub(r"[^\n]", " ", seg)

    while i < n:
        c = text[i]
        if c == "-" and text.startswith("--", i):
            j = i + 2
            level = _long_bracket(text, j) if j < n and text[j] == "[" else None
            if level is not None:
                end = text.find("]" + "=" * level + "]", j)
                end = n if end < 0 else end + level + 2
            else:
                end = text.find("\n", i)
                end = n if end < 0 else end
            out.append(blank(text[i:end]))
            i = end
        elif c == "[" and _long_bracket(text, i) is not None:
            level = _long_bracket(text, i)
            end = text.find("]" + "=" * level + "]", i)
            end = n if end < 0 else end + level + 2
            out.append(blank(text[i:end]))
            i = end
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            j = min(j, n)
            if j < n and text[j] == c:  # 正常闭合
                out.append(c + blank(text[i + 1:j]) + c)
                i = j + 1
            else:  # 未闭合：不吞掉换行，保持行号
                out.append(c + blank(text[i + 1:j]))
                i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


# ---------------------------------------------------------------- 语法

def make_syntax_checker():
    try:
        from lupa import lua51
        # encoding=None：收发 bytes。Lua 报错会截断源码片段，可能切在多字节字符中间
        lua = lua51.LuaRuntime(encoding=None, unpack_returned_tuples=True)
        compile_fn = lua.eval(b"function(s, n) local f, e = loadstring(s, n); return e end")

        def check(src, name):
            err = compile_fn(src.encode("utf-8"), ("@" + name).encode("utf-8"))
            return err.decode("utf-8", "replace") if err else None
        return "lupa.lua51", check
    except Exception:  # noqa: BLE001 - 任何导入/初始化失败都退回下一种方式
        pass
    try:
        from luaparser import ast

        def check(src, name):
            try:
                ast.parse(src)
                return None
            except Exception as e:  # noqa: BLE001
                return f"{name}: {e}"
        return "luaparser", check
    except ImportError:
        return None, None


# ---------------------------------------------------------------- 原版源码

class VanillaSource:
    def __init__(self, source_dir=None, zip_path=None, game_home=None):
        self.dir, self.zip, self.label = None, None, "无"
        home = game_home or os.environ.get("DST_GAME_HOME")
        data = os.environ.get("DST_DATA_DIR")
        if source_dir:
            self.dir = Path(source_dir)
        elif zip_path or home:
            z = Path(zip_path) if zip_path else Path(home) / "data/databundles/scripts.zip"
            if z.is_file():
                self.zip = zipfile.ZipFile(z)
        if self.dir is None and self.zip is None and data and (Path(data) / "scripts").is_dir():
            self.dir = Path(data) / "scripts"
        if self.dir is not None:
            if not (self.dir / "components").is_dir():
                raise ValueError(f"{self.dir} 下没有 components/，不像 DST scripts 目录")
            self.label = f"目录 {self.dir}"
        elif self.zip is not None:
            self.label = f"scripts.zip {self.zip.filename}"

    def read(self, rel):
        if self.dir is not None:
            p = self.dir / rel
            return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else None
        if self.zip is not None:
            try:
                return self.zip.read("scripts/" + rel).decode("utf-8", "replace")
            except KeyError:
                return None
        return None


def declared_methods(text):
    """返回 (方法名集合, 父类变量名, 父类对应的 components 模块名或 None)。"""
    code = strip_lua(text)
    names = set()
    for rx in DECL_RES:
        names.update(rx.findall(code))
    base = BASE_RE.search(code)
    base_name = base.group(1) if base else None
    requires = dict(REQUIRE_RE.findall(text))
    return names, base_name, requires.get(base_name)


# ---------------------------------------------------------------- 主流程

def loaded_scope(root):
    """游戏实际会加载的范围：根目录的 *.lua、scripts/ 全部，以及 modimport 字面量引用的文件。"""
    picked = set(root.glob("*.lua")) | set((root / "scripts").rglob("*.lua"))
    queue = list(picked)
    while queue:
        f = queue.pop()
        for target in MODIMPORT_RE.findall(f.read_text(encoding="utf-8", errors="replace")):
            cand = root / target
            for c in (cand, cand.with_name(cand.name + ".lua")):
                if c.is_file() and c not in picked:
                    picked.add(c)
                    queue.append(c)
    return picked


def collect_files(targets, excludes, scan_all=False):
    files = []
    for t in targets:
        p = Path(t)
        if p.is_file():
            files.append((p, p.parent))
            continue
        if not p.is_dir():
            raise ValueError(f"不存在：{t}")
        scope = p.rglob("*.lua") if scan_all or not (p / "modinfo.lua").is_file() else loaded_scope(p)
        for f in sorted(scope):
            rel = f.relative_to(p)
            if any(part in excludes for part in rel.parts[:-1]) or any(
                    fnmatch.fnmatch(rel.as_posix(), g) for g in excludes):
                continue
            files.append((f, p))
    return files


def find_mod_root(path):
    for d in [path, *path.parents]:
        if (d / "modinfo.lua").is_file():
            return d
    return None


def run_check(targets, vanilla, excludes=DEFAULT_EXCLUDES, scan_all=False, deps=()):
    files = collect_files(targets, excludes, scan_all)
    engine, syntax = make_syntax_checker()
    report = {"syntax_engine": engine or "skipped（未安装 lupa 或 luaparser）", "vanilla": vanilla.label,
              "scope": "全部 .lua" if scan_all else "游戏加载范围（根目录、scripts/、modimport 引用）",
              "files": len(files), "syntax_errors": [], "warnings": [], "calls": []}
    stripped, mod_assigned = {}, set()
    for f, _ in files:
        raw = f.read_bytes()
        if raw.startswith(b"\x1bLua"):
            report["warnings"].append({"file": str(f), "warning": "预编译字节码，跳过"})
            stripped[f] = ""
            continue
        text = raw.decode("utf-8", "replace").lstrip("\ufeff")
        if syntax:
            err = syntax(text, f.as_posix())
            if err and any(s in err for s in ENGINE_LIMIT_ERRORS):
                report["warnings"].append({"file": str(f), "warning": f"{err}（DST 引擎上限更高，原版也有此情况）"})
            elif err:
                report["syntax_errors"].append({"file": str(f), "error": str(err)})
        code = strip_lua(text)
        stripped[f] = code
        for rx in DECL_RES:  # 模组里任何方法定义/赋值都可能是对组件的补丁
            mod_assigned.update(rx.findall(code))

    cache = {}

    def module(rel, mod_root, depth=0):
        key = (rel, mod_root)
        if key not in cache:
            text, origin = None, None
            dep_hit = next((d for d in deps if (Path(d) / "scripts" / rel).is_file()), None)
            if mod_root is not None and (mod_root / "scripts" / rel).is_file():
                text, origin = (mod_root / "scripts" / rel).read_text(encoding="utf-8", errors="replace"), "mod"
            elif dep_hit is not None:
                text, origin = (Path(dep_hit) / "scripts" / rel).read_text(encoding="utf-8", errors="replace"), "dep"
            else:
                text = vanilla.read(rel)
                origin = "vanilla" if text is not None else None
            names, base, base_mod = declared_methods(text) if text is not None else (set(), None, None)
            if base_mod and depth < 4:  # 合并父类方法：Class(Base, ...) 且 Base = require("components/x")
                names = names | module(f"components/{base_mod}.lua", mod_root, depth + 1)[0][0]
                base = None
            cache[key] = ((names, base, base_mod), origin)
        return cache[key]

    for f, root in files:
        mod_root = find_mod_root(f.parent) or root
        for m in CALL_RE.finditer(stripped[f]):
            kind, comp, method = m.groups()
            line = stripped[f].count("\n", 0, m.start()) + 1
            rel = f"components/{comp}.lua" if kind == "components" else f"components/{comp}_replica.lua"
            (names, base, _), origin = module(rel, mod_root)
            entry = {"file": str(f), "line": line, "call": f"{kind}.{comp}:{method}"}
            if method in names:
                entry.update(status="DECLARED", where=f"{origin}:{rel}")
            else:
                entry["status"] = "NEEDS_REVIEW"
                if origin is None:
                    entry["reason"] = f"找不到 {rel}（引擎原生组件、依赖模组或拼写错误）"
                elif kind == "replica" and method in module(f"components/{comp}.lua", mod_root)[0][0]:
                    entry["reason"] = f"主组件 {comp}.lua 有 {method}，replica 没有：客户端调用会失败，确认是否只在服务端执行"
                elif kind == "components" and method in module(f"components/{comp}_replica.lua", mod_root)[0][0]:
                    entry["reason"] = f"只有 {comp}_replica.lua 有 {method}，主组件没有：可能应改用 inst.replica.{comp}"
                elif base:
                    entry["reason"] = f"{rel} 继承自 {base}，未解析父类"
                elif method in mod_assigned:
                    entry["reason"] = "模组里有同名方法定义或赋值，可能是对该组件的补丁，需人工确认"
                else:
                    entry["reason"] = f"{origin}:{rel} 中没有找到 {method} 的定义"
            report["calls"].append(entry)
    report["summary"] = {
        "syntax_errors": len(report["syntax_errors"]),
        "warnings": len(report["warnings"]),
        "calls": len(report["calls"]),
        "declared": sum(c["status"] == "DECLARED" for c in report["calls"]),
        "needs_review": sum(c["status"] == "NEEDS_REVIEW" for c in report["calls"]),
    }
    return report


def print_text(report):
    s = report["summary"]
    print(f"语法引擎：{report['syntax_engine']}；原版源码：{report['vanilla']}；"
          f"范围：{report['scope']}，Lua 文件 {report['files']} 个")
    for e in report["syntax_errors"]:
        print(f"[语法错误] {e['error']}")
    for w in report["warnings"]:
        print(f"[提示] {w['file']}：{w['warning']}")
    seen = set()
    for c in report["calls"]:
        if c["status"] != "NEEDS_REVIEW":
            continue
        key = (c["call"], c["reason"])
        first = key not in seen
        seen.add(key)
        if first:
            print(f"[NEEDS_REVIEW] {c['call']} — {c['reason']}")
        print(f"    {c['file']}:{c['line']}")
    print(f"汇总：语法错误 {s['syntax_errors']}；组件调用 {s['calls']}，DECLARED {s['declared']}，"
          f"NEEDS_REVIEW {s['needs_review']}（DECLARED 只表示查到声明，不代表端别和参数正确）")


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="DST 模组 Lua 语法与组件方法声明检查")
    p.add_argument("targets", nargs="+", help="模组目录或 .lua 文件")
    p.add_argument("--source-dir", help="原版 scripts 目录（含 components/）")
    p.add_argument("--zip", help="原版 scripts.zip")
    p.add_argument("--game-home", help="DST 安装根目录（默认环境变量 DST_GAME_HOME）")
    p.add_argument("--exclude", action="append", default=[], help="额外排除的目录名或相对路径 glob")
    p.add_argument("--with", dest="deps", action="append", default=[], metavar="MOD_DIR",
                   help="依赖模组目录（查找组件定义时在原版之前搜索），可重复")
    p.add_argument("--all", action="store_true", help="扫描目录下全部 .lua（默认只扫游戏加载范围）")
    p.add_argument("--json", action="store_true", help="输出完整 JSON")
    p.add_argument("--strict", action="store_true", help="NEEDS_REVIEW 也返回退出码 1")
    args = p.parse_args(argv)
    try:
        vanilla = VanillaSource(args.source_dir, args.zip, args.game_home)
        report = run_check(args.targets, vanilla, DEFAULT_EXCLUDES + tuple(args.exclude), args.all,
                           tuple(args.deps))
    except ValueError as e:
        print(f"[错误] {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    s = report["summary"]
    return 1 if s["syntax_errors"] or (args.strict and s["needs_review"]) else 0


if __name__ == "__main__":
    sys.exit(main())
