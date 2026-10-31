"""dst_lua_check.py 的离线测试：用桩模组和桩原版源码目录，不需要游戏安装。

    python -m unittest discover -s dst-debugging-testing/tests
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dst_lua_check as lc  # noqa: E402

VANILLA = {
    "components/health.lua": "local Health = Class(function(self, inst) end)\n"
                             "function Health:DoDelta(n) end\nfunction Health:Kill() end\n"
                             "Health.Revive = Health.Kill\nreturn Health\n",
    "components/health_replica.lua": "local Health = Class(function(self, inst) end)\n"
                                     "function Health:GetPercent() end\nreturn Health\n",
    "components/dryingrack.lua": "local Rack = Class(function(self, inst) end)\nfunction Rack:GetContainer() end\n",
    "components/wobyrack.lua": 'local DryingRack = require("components/dryingrack")\n'
                               "local W = Class(DryingRack, function(self, inst) end)\nreturn W\n",
}

MODMAIN = """-- components.health:FromComment() 注释里的不算
local s = "inst.components.health:FromString()"
inst.components.health:DoDelta(-1)
inst.components.health:Revive()
inst.replica.health:GetPercent()
inst.replica.health:DoDelta(5)
inst.components.health:GetPercent()
inst.components.wobyrack:GetContainer()
inst.components.mymeter:Tick()
inst.components.ghost:Boo()
inst.components.health:Patched()
modimport("main/extra")
"""


class LuaCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.vanilla = root / "vanilla"
        for rel, text in VANILLA.items():
            (self.vanilla / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.vanilla / rel).write_text(text, encoding="utf-8")
        self.mod = root / "mod"
        (self.mod / "scripts" / "components").mkdir(parents=True)
        (self.mod / "main").mkdir()
        (self.mod / "modinfo.lua").write_text('name = "m"\n', encoding="utf-8")
        (self.mod / "modmain.lua").write_text(MODMAIN, encoding="utf-8")
        (self.mod / "scripts" / "components" / "mymeter.lua").write_text(
            "local M = Class(function(self) end)\nfunction M:Tick() end\nreturn M\n", encoding="utf-8")
        (self.mod / "main" / "extra.lua").write_text(
            "local Health = require('components/health')\nfunction Health:Patched() end\n", encoding="utf-8")
        (self.mod / "_ai_work").mkdir()
        (self.mod / "_ai_work" / "broken.lua").write_text("local = 1\n", encoding="utf-8")
        (self.mod / "unused").mkdir()
        (self.mod / "unused" / "old.lua").write_text("x = = 1\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, **kw):
        report = lc.run_check([str(self.mod)], lc.VanillaSource(source_dir=str(self.vanilla)), **kw)
        return report, {c["call"]: c for c in report["calls"]}

    def test_declarations(self):
        report, calls = self.check()
        self.assertEqual(calls["components.health:DoDelta"]["status"], "DECLARED")
        self.assertEqual(calls["components.health:Revive"]["status"], "DECLARED")  # 别名赋值
        self.assertEqual(calls["replica.health:GetPercent"]["status"], "DECLARED")
        self.assertEqual(calls["components.wobyrack:GetContainer"]["status"], "DECLARED")  # 父类
        self.assertEqual(calls["components.mymeter:Tick"]["where"], "mod:components/mymeter.lua")
        self.assertIn("replica 没有", calls["replica.health:DoDelta"]["reason"])
        self.assertIn("inst.replica.health", calls["components.health:GetPercent"]["reason"])
        self.assertIn("找不到", calls["components.ghost:Boo"]["reason"])
        self.assertIn("补丁", calls["components.health:Patched"]["reason"])
        self.assertNotIn("components.health:FromComment", calls)
        self.assertNotIn("components.health:FromString", calls)

    def test_scope_and_syntax(self):
        report, _ = self.check()
        files = report["files"]
        self.assertEqual(report["syntax_errors"], [])  # _ai_work 与未加载的 unused/ 不扫
        self.assertEqual(files, 4)  # modinfo、modmain、scripts/components/mymeter、modimport 的 main/extra
        report, _ = self.check(scan_all=True)
        self.assertEqual(len(report["syntax_errors"]), 1)  # unused/old.lua；_ai_work 仍排除
        if report["syntax_engine"] != "lupa.lua51":
            self.skipTest("未安装 lupa，跳过 Lua 5.1 专项检查")
        self.assertIn("old.lua", report["syntax_errors"][0]["file"])

    def test_strip_keeps_line_numbers(self):
        src = 'a = "x\nb = [[\nlong]] -- c\n--[==[\nblock]==] d = 1\n'
        out = lc.strip_lua(src)
        self.assertEqual(out.count("\n"), src.count("\n"))
        self.assertIn("d = 1", out)
        self.assertNotIn("long", out)


if __name__ == "__main__":
    unittest.main()
