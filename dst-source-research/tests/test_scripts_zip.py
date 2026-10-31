"""dst_scripts_zip.py 的离线测试：用桩 scripts.zip，不需要游戏安装。

    python -m unittest discover -s dst-source-research/tests
"""
import io
import json
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import dst_scripts_zip as dz  # noqa: E402

HEALTH = "local Health = Class(function(self, inst) end)\n\nfunction Health:DoDelta(amount)\nend\n\nreturn Health\n"


class ScriptsZipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "game"
        bundles = self.home / "data" / "databundles"
        bundles.mkdir(parents=True)
        (self.home / "version.txt").write_text("761239\n", encoding="utf-8")
        with zipfile.ZipFile(bundles / "scripts.zip", "w") as z:
            z.writestr("scripts/components/health.lua", HEALTH)
            z.writestr("scripts/components/health_replica.lua", "-- replica\n")
            z.writestr("scripts/main.lua", "print('main')\n")

    def tearDown(self):
        self.tmp.cleanup()

    def cli(self, *argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = dz.main(["--game-home", str(self.home), *argv])
        return code, buf.getvalue()

    def test_info(self):
        code, out = self.cli("info")
        info = json.loads(out)
        self.assertEqual((code, info["entries"], info["build"]), (0, 3, "761239"))

    def test_list_and_member_names(self):
        _, out = self.cli("list", "--glob", "components/*_replica.lua")
        self.assertEqual(out.split(), ["scripts/components/health_replica.lua"])
        self.assertEqual(dz.normalize_member("scripts\\components\\health.lua"), "scripts/components/health.lua")
        with self.assertRaises(ValueError):
            dz.normalize_member("../secret")

    def test_grep_and_show(self):
        _, out = self.cli("grep", r"^function Health:DoDelta")
        self.assertIn("scripts/components/health.lua:3:", out)
        _, out = self.cli("show", "components/health.lua", "--lines", "3:3")
        self.assertEqual(out.strip(), "3  function Health:DoDelta(amount)")

    def test_extract_refuses_overwrite(self):
        target = Path(self.tmp.name) / "out" / "health.lua"
        self.assertEqual(self.cli("extract", "components/health.lua", "--to", str(target))[0], 0)
        self.assertEqual(target.read_text(encoding="utf-8"), HEALTH)
        self.assertEqual(self.cli("extract", "components/health.lua", "--to", str(target))[0], 2)

    def test_missing_zip(self):
        self.assertEqual(dz.main(["--game-home", str(Path(self.tmp.name) / "nope"), "info"]), 2)


if __name__ == "__main__":
    unittest.main()
