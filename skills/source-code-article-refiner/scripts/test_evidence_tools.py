"""Exercise evidence boundaries with isolated fixtures; no repository mutation."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import evidence_tools as tools


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def baseline(self, content, protected=None):
        self.put("article.md", content)
        return tools.snapshot(self.root, ["article.md"], protected or [])

    def test_extract_reads_commit_not_dirty_worktree(self):
        self.put("file.ts", "function run() {\n    return 1\n}\n")
        for args in (
            ["init", "-q"], ["add", "file.ts"],
            ["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "commit", "-qm", "fixture"],
        ):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        self.put("file.ts", "uncommitted replacement\n")
        result = tools.extract(self.root, "HEAD", "file.ts", 2, 2)
        self.assertEqual(result["raw"], "    return 1")
        self.assertEqual(result["code"], "return 1")
        self.assertEqual(len(result["sha"]), 40)
        with self.assertRaises(ValueError):
            tools.extract(self.root, "HEAD", "file.ts", 0, 2)
        with self.assertRaises(ValueError):
            tools.extract(self.root, "HEAD", "file.ts", 2, 4)

    def test_rejects_escape_and_duplicate_scope(self):
        for path in ("../outside.md", "/absolute.md", "a/../../escape", "..\\escape"):
            with self.assertRaises(ValueError):
                tools.relative_path(path)
        self.put("a.md", "# A")
        with self.assertRaises(ValueError):
            tools.snapshot(self.root, ["a.md"], ["a.md"])
        outside = self.root.parent / f"{self.root.name}-outside.md"
        outside.write_text("outside", encoding="utf-8")
        self.addCleanup(outside.unlink)
        (self.root / "link.md").symlink_to(outside)
        with self.assertRaises(ValueError):
            tools.local_file(self.root, "link.md")

    def test_code_fences_exclude_fake_headings_and_images(self):
        content = "## Real\n````md\n## Fake\n![fake](fake.png)\n```\n````\n![real](real.png)\n"
        inventory = tools.markdown_inventory(content)
        self.assertEqual(inventory["h2"], ["Real"])
        self.assertEqual(inventory["images"], ["real.png"])
        self.assertEqual(len(inventory["code_sha256"]), 1)
        self.assertEqual(len(tools.markdown_inventory("~~~ts\nx\n~~~")["code_sha256"]), 1)
        with self.assertRaises(ValueError):
            tools.markdown_inventory("```ts\nnever closed")

    def test_duplicate_excerpt_removal_is_detected(self):
        block = "```ts\nconst x = 1\n```\n"
        baseline = self.baseline("## Topic\n" + block + block)
        self.put("article.md", "## Topic\n" + block)
        result = tools.compare(self.root, baseline)
        self.assertFalse(result["passed"])
        self.assertEqual(result["failures"][0]["check"], "code_retention")
        self.assertTrue(tools.compare(self.root, baseline, code_policy="any")["passed"])

    def test_title_and_step_policies(self):
        baseline = self.baseline("## Old\n### 步骤1：进入\n")
        self.put("article.md", "## New\n### 步骤1：准入\n")
        self.assertFalse(tools.compare(self.root, baseline)["passed"])
        self.assertTrue(tools.compare(self.root, baseline, headings="same-count", steps="same-count")["passed"])
        self.put("article.md", "## New\n")
        self.assertFalse(tools.compare(self.root, baseline, headings="same-count", steps="same-count")["passed"])

    def test_chinese_ordinals_and_english_steps(self):
        content = "### 第一步：进入\n### 第十一步：返回\n### 第12步：退出\n### Step 13: clean up\n### 心得\n"
        inventory = tools.markdown_inventory(content)
        self.assertEqual(len(inventory["steps"]), 4)
        self.assertEqual(inventory["steps"][1], "第十一步：返回")

    def test_protected_binary_mutation_fails(self):
        (self.root / "image.png").write_bytes(b"original\x00")
        baseline = self.baseline("## Topic\n", ["image.png"])
        (self.root / "image.png").write_bytes(b"changed\x00")
        self.assertEqual(tools.compare(self.root, baseline)["failures"][0]["check"], "protected_bytes")

    def test_image_requirement_is_explicit(self):
        baseline = self.baseline("## Topic\n![one](one.png)\n")
        self.assertTrue(tools.compare(self.root, baseline)["passed"])
        self.assertFalse(tools.compare(self.root, baseline, images=4)["passed"])
        self.assertTrue(tools.compare(self.root, baseline, images=1)["passed"])

    def test_cli_report_status_and_no_overwrite(self):
        baseline = self.baseline("## Topic\n")
        capture = self.root / "before.json"
        tools.write_result(baseline, capture)
        with self.assertRaises(FileExistsError):
            tools.write_result({}, capture)
        self.put("article.md", "## Changed\n")
        report = self.root / "report.json"
        self.assertEqual(tools.main([
            "compare", "--root", str(self.root), "--baseline", str(capture), "--out", str(report)
        ]), 1)
        self.assertFalse(json.loads(report.read_text())["passed"])


if __name__ == "__main__":
    unittest.main()
