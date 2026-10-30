import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SOURCE_ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", SOURCE_ROOT / "scripts" / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.skills = self.base / "skills"
        self.rules = self.base / "instructions.md"

    def call(self, *extra, agent="generic"):
        args = ["--agent", agent, "--skills-dir", str(self.skills), "--rules-file", str(self.rules), *extra]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return installer.run(args)

    def snapshot(self):
        return {str(p.relative_to(self.base)): (p.read_bytes(), p.stat().st_mtime_ns)
                for p in self.base.rglob("*") if p.is_file()}

    def test_fresh_check_is_read_only_install_and_repeat_are_idempotent(self):
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(list(self.base.iterdir()), [])
        self.assertEqual(self.call(), 0)
        before = self.snapshot()
        self.assertEqual(self.call(), 0)
        self.assertEqual(self.call("--check"), 0)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.rules.read_bytes().count(installer.BEGIN), 1)

    def test_existing_bom_crlf_prefix_suffix_are_preserved_on_update(self):
        original = b"\xef\xbb\xbf# Personal\r\nKeep these rules.\r\n"
        self.rules.write_bytes(original)
        self.assertEqual(self.call(), 0)
        installed = self.rules.read_bytes()
        self.assertTrue(installed.startswith(original))
        self.rules.write_bytes(installed + b"\r\n# Other rules\r\n")
        stale = self.rules.read_bytes().replace(b"# ", b"# OLD ", 1)
        # Corrupt only generated content, not the preserved prefix.
        start = stale.index(installer.BEGIN) + len(installer.BEGIN)
        stale = stale[:start] + b"\r\nold body\r\n" + stale[stale.index(installer.END):]
        self.rules.write_bytes(stale)
        self.assertEqual(self.call("--check"), 1)
        self.assertEqual(self.call(), 0)
        result = self.rules.read_bytes()
        self.assertEqual(result[:result.index(installer.BEGIN)], stale[:stale.index(installer.BEGIN)])
        self.assertTrue(result.endswith(b"\r\n# Other rules\r\n"))
        backups = list(self.base.glob("instructions.md.chris-skills.bak.*"))
        self.assertTrue(any(p.read_bytes() == original for p in backups))
        self.assertTrue(any(p.read_bytes() == stale for p in backups))

    def test_broken_markers_fail_before_any_installation(self):
        for content in (installer.BEGIN, installer.END + installer.BEGIN,
                        installer.BEGIN + installer.END + installer.BEGIN + installer.END):
            with self.subTest(content=content):
                self.rules.write_bytes(content)
                before = self.snapshot()
                self.assertEqual(self.call(), 2)
                self.assertEqual(self.snapshot(), before)

    def test_unmanaged_skill_is_not_overwritten(self):
        target = self.skills / "recap-and-learn"
        target.mkdir(parents=True)
        (target / "SKILL.md").write_text("local skill", encoding="utf-8")
        before = self.snapshot()
        self.assertEqual(self.call(), 2)
        self.assertEqual(self.snapshot(), before)

    def test_claude_manual_only_metadata_is_added_to_copy(self):
        source = SOURCE_ROOT / "evolution" / "SKILL.md"
        before = source.read_bytes()
        self.assertEqual(self.call(agent="claude"), 0)
        copied = (self.skills / "evolution" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("disable-model-invocation: true", copied.split("\n---\n", 1)[0])
        self.assertEqual(source.read_bytes(), before)

    def test_installing_only_evolution_does_not_enable_footer(self):
        self.assertEqual(self.call("--skill", "evolution"), 0)
        self.assertFalse(self.rules.exists())
        self.assertFalse((self.skills / "recap-and-learn").exists())

    def test_codex_home_selects_effective_override_and_preserves_base(self):
        codex_dir = self.base / "codex-home"
        codex_dir.mkdir()
        base = codex_dir / "AGENTS.md"
        override = codex_dir / "AGENTS.override.md"
        base.write_bytes(b"Base agreements\n")
        override.write_bytes(b"Temporary agreements\n")
        args = ["--agent", "codex", "--skills-dir", str(self.skills)]
        with patch.dict(os.environ, {"CODEX_HOME": str(codex_dir)}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.run(args), 0)
        self.assertEqual(base.read_bytes(), b"Base agreements\n")
        self.assertTrue(override.read_bytes().startswith(b"Temporary agreements\n"))
        self.assertIn(installer.BEGIN, override.read_bytes())

    def test_trae_project_paths_and_always_apply(self):
        project = self.base / "business project"
        args = ["--agent", "trae", "--project", str(project)]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(installer.run(args), 0)
            self.assertEqual(installer.run(args + ["--check"]), 0)
        self.assertTrue((project / ".trae" / "skills" / "recap-and-learn" / "SKILL.md").is_file())
        rule = (project / ".trae" / "rules" / "chris-skills.md").read_text(encoding="utf-8")
        self.assertTrue(rule.startswith("---\nalwaysApply: true\n---\n"))

    def test_unsafe_paths_unknown_skills_and_trae_global_fail_without_writes(self):
        before = self.snapshot()
        self.assertEqual(self.call("--skill", "unknown"), 2)
        self.assertEqual(self.call("--skills-dir", str(SOURCE_ROOT)), 2)
        self.assertEqual(self.call(agent="trae"), 2)
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
