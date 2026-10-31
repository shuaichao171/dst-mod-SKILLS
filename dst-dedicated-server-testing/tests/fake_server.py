"""测试用假专服：按 dst_headless_run.py 传入的参数找到集群目录，写出与原生日志同格式的行。

FAKE_MODE：pass（默认）/ fail / nodone / luaerror / missing / invalid / noassert
"""
import os
import re
import sys
import time
from pathlib import Path


def arg(name):
    return sys.argv[sys.argv.index(name) + 1]


master = Path(arg("-persistent_storage_root")) / arg("-conf_dir") / arg("-cluster") / "Master"
keys = re.findall(r'\["([^"]+)"\]=\{', (master / "modoverrides.lua").read_text(encoding="utf-8"))
runner = next(k for k in keys if k.endswith("_runner"))
run_id = runner[len("_altwf_"):-len("_runner")]
mode = os.environ.get("FAKE_MODE", "pass")
log = open(master / "server_log.txt", "w", encoding="utf-8")


def say(line):
    log.write(f"[00:00:01]: {line}\n")
    log.flush()


tag = f"[ALTTEST {run_id}] "
for i, k in enumerate(keys):
    if mode == "missing" and i == 0:
        continue
    say(f"Loading mod: {k} (Fake) Version:1")
say(tag + 'READY {"dedicated":true}')
say(tag + "START {}")
if mode == "luaerror":
    say("[string \"scripts/components/foo.lua\"]:3: attempt to index a nil value")
    say("LUA ERROR stack traceback:")
    say("    scripts/components/foo.lua:3 in (method) Bar")
if mode == "invalid":
    say(tag + 'INVALID {"reason":"no ground"}')
if mode not in ("noassert", "invalid"):
    ok = "false" if mode == "fail" else "true"
    say(tag + f'CHECK {{"name":"rabbit has health","ok":{ok},"detail":"actual=1 expected=1"}}')
    say(tag + 'METRIC {"name":"hp","value":25}')
if mode != "nodone":
    say(tag + 'DONE {"passed":1,"failed":0}')

for line in sys.stdin:
    if "c_shutdown" in line:
        say("Shutting down")
        break
time.sleep(0.2)
sys.exit(0)
