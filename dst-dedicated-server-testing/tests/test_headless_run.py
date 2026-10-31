"""dst_headless_run.py 的离线测试：用假专服跑完整流程，不启动游戏。

    python -m unittest discover -s dst-dedicated-server-testing/tests
"""
import argparse
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import dst_headless_run as hr  # noqa: E402

FAKE = [sys.executable, str(HERE / "fake_server.py")]


def make_mod(root, name, extra=None):
    d = root / name
    (d / "scripts").mkdir(parents=True)
    (d / "modinfo.lua").write_text('name = "x"\n', encoding="utf-8")
    (d / "modmain.lua").write_text("-- main\n", encoding="utf-8")
    (d / "_ai_work").mkdir()
    (d / "_ai_work" / "notes.txt").write_text("not staged", encoding="utf-8")
    for rel, text in (extra or {}).items():
        (d / rel).write_text(text, encoding="utf-8")
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "game"
        (self.home / "mods").mkdir(parents=True)
        (self.home / "version.txt").write_text("761239\n", encoding="utf-8")
        self.mod = make_mod(self.root, "sample_mod")
        self.behavior = self.root / "case.lua"
        self.behavior.write_text("TEST.Done()\n", encoding="utf-8")

    def tearDown(self):
        os.environ.pop("FAKE_MODE", None)
        self.tmp.cleanup()

    def args(self, **kw):
        base = dict(mod=[str(self.mod)], behavior=str(self.behavior), out=str(self.root / "out"),
                    game_home=str(self.home), mod_config=None, start_delay=0, timeout=20, startup_timeout=15,
                    shutdown_timeout=5, x86=False, allow_sandbox_escape=False, keep_staged=False, dry_run=False)
        base.update(kw)
        return argparse.Namespace(**base)

    def run_fake(self, mode, **kw):
        os.environ["FAKE_MODE"] = mode
        return hr.run(self.args(**kw), server_cmd_override=FAKE)


class FlowTests(Base):
    def test_pass_flow_stages_and_cleans(self):
        result, run_dir = self.run_fake("pass")
        self.assertEqual(result["status"], "passed", result.get("reason"))
        self.assertEqual(result["build"], "761239")
        self.assertTrue(result["staged_removed"])
        self.assertEqual(hr.stale_dirs(self.home), [])
        self.assertEqual(result["metrics"][0]["value"], 25)
        self.assertEqual(result["process"]["exit_code"], 0)
        self.assertFalse(result["process"].get("forced_kill", False))
        saved = json.loads((run_dir / "results" / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "passed")
        events = (run_dir / "results" / "events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertIn("DONE", [json.loads(e)["kind"] for e in events])
        # 集群配置：离线、空服不暂停、modoverrides 含被测模组与驱动
        cluster = run_dir / "storage" / hr.CONF_DIR / hr.CLUSTER
        self.assertIn("offline_cluster = true", (cluster / "cluster.ini").read_text(encoding="utf-8"))
        self.assertIn("pause_when_empty = false", (cluster / "cluster.ini").read_text(encoding="utf-8"))
        overrides = (cluster / "Master" / "modoverrides.lua").read_text(encoding="utf-8")
        self.assertIn(result["mods"][0]["key"], overrides)
        self.assertIn(result["runner"]["key"], overrides)

    def test_failed_check(self):
        result, _ = self.run_fake("fail")
        self.assertEqual(result["status"], "failed")

    def test_lua_error_after_ready_fails_even_if_checks_pass(self):
        result, _ = self.run_fake("luaerror")
        self.assertEqual(result["status"], "failed")
        self.assertIn("LUA ERROR", "\n".join(result["first_error"]["lines"]))

    def test_no_done_times_out_and_is_interrupted(self):
        result, _ = self.run_fake("nodone", timeout=3)
        self.assertEqual(result["status"], "interrupted")
        self.assertEqual(hr.stale_dirs(self.home), [])

    def test_missing_mod_is_invalid(self):
        result, _ = self.run_fake("missing")
        self.assertEqual(result["status"], "invalid")
        self.assertIn(result["mods"][0]["key"], result["reason"])

    def test_invalid_and_no_assert(self):
        self.assertEqual(self.run_fake("invalid")[0]["status"], "invalid")
        self.assertEqual(self.run_fake("noassert")[0]["status"], "invalid")

    def test_keep_staged(self):
        result, _ = self.run_fake("pass", keep_staged=True)
        self.assertEqual(len(hr.stale_dirs(self.home)), 2)  # 被测模组 + 驱动
        staged = Path(result["mods"][0]["staged"])
        self.assertFalse((staged / "_ai_work").exists())
        self.assertIn("TEST.Done", (Path(result["runner"]["staged"]) / "scripts" / hr.BEHAVIOR_NAME).read_text())

    def test_mod_config_written(self):
        cfg = self.root / "cfg.json"
        cfg.write_text(json.dumps({"sample_mod": {"language": "zh", "hard": True, "n": 3}}), encoding="utf-8")
        result, run_dir = self.run_fake("pass", mod_config=str(cfg))
        overrides = (run_dir / "storage" / hr.CONF_DIR / hr.CLUSTER / "Master" / "modoverrides.lua").read_text(
            encoding="utf-8")
        self.assertIn('["configuration_options"]={["language"]="zh", ["hard"]=true, ["n"]=3}', overrides)

    def test_dry_run_touches_nothing(self):
        result, run_dir = hr.run(self.args(dry_run=True))
        self.assertEqual(result["status"], "not_run")
        self.assertEqual(hr.stale_dirs(self.home), [])
        self.assertIn("-offline", result["plan"]["command"])


class UnitTests(Base):
    def test_remove_owned_refuses_foreign_dirs(self):
        other = self.home / "mods" / "someone_elses_mod"
        other.mkdir()
        with self.assertRaises(ValueError):
            hr.remove_owned(other, self.home / "mods")
        self.assertTrue(other.exists())

    def test_stage_refuses_non_mod(self):
        with self.assertRaises(ValueError):
            hr.stage_mod(self.root, self.home / "mods" / "_altwf_x_0")

    def test_lua_value(self):
        self.assertEqual(hr.lua_value({"a": [1, "b", None, False]}), '{["a"]={1, "b", nil, false}}')

    def test_parse_event_ignores_other_runs(self):
        self.assertIsNone(hr.parse_event('[ALTTEST other] DONE {}', "mine"))
        self.assertEqual(hr.parse_event('x [ALTTEST mine] CHECK {"ok":true}', "mine")["ok"], True)

    def test_free_ports_distinct(self):
        used = set()
        ports = {hr.free_port(used) for _ in range(3)}
        self.assertEqual(len(ports), 3)
        lan = hr.free_port(used, *hr.LAN_PORT_RANGE)
        self.assertTrue(hr.LAN_PORT_RANGE[0] <= lan <= hr.LAN_PORT_RANGE[1])


if __name__ == "__main__":
    unittest.main()
