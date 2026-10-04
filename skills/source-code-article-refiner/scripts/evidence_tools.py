#!/usr/bin/env python3
"""Read-only source excerpts and editorial preservation checks (stdlib only)."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import textwrap
from urllib.parse import quote


def digest(value):
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def relative_path(value):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value:
        raise ValueError(f"Expected a safe relative path: {value}")
    if str(path) == ".":
        raise ValueError("Expected a file path")
    return str(path)


def local_file(root, value):
    root = Path(root).resolve()
    path = (root / relative_path(value)).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"File escapes root: {value}")
    return path


def git(repo, *args):
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, check=True
    )
    return result.stdout.decode("utf-8")


def extract(repo, rev, path, start, end, base_url=None):
    path = relative_path(path)
    sha = git(repo, "rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}").strip()
    lines = git(repo, "show", f"{sha}:{path}").splitlines()
    if not 1 <= start <= end <= len(lines):
        raise ValueError(f"Invalid range {start}-{end}; file has {len(lines)} lines")
    raw = "\n".join(lines[start - 1:end])
    code = textwrap.dedent(raw)
    result = {
        "sha": sha, "path": path, "start": start, "end": end,
        "normalization": "LF-joined selected lines, no final newline; code is dedented raw",
        "raw": raw, "code": code, "raw_sha256": digest(raw), "code_sha256": digest(code),
    }
    if base_url:
        if not re.fullmatch(r"https://github\.com/[^/]+/[^/#?]+/?", base_url):
            raise ValueError("base-url must be an explicit https://github.com/owner/repo URL")
        result["url"] = f"{base_url.rstrip('/')}/blob/{sha}/{quote(path, safe='/')}#L{start}-L{end}"
    return result


def markdown_inventory(content):
    headings, steps, codes, images = [], [], [], []
    marker, width, block = None, 0, []
    for line in content.splitlines():
        if marker:
            if re.fullmatch(rf" {{0,3}}{re.escape(marker)}{{{width},}}\s*", line):
                codes.append(digest("\n".join(block)))
                marker, width, block = None, 0, []
            else:
                block.append(line)
            continue
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            marker, width = fence[1][0], len(fence[1])
            continue
        heading = re.match(r"^ {0,3}##\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append(heading[1])
        step = re.match(
            r"^ {0,3}###\s+((?:步骤\s*\d+|第[一二三四五六七八九十百零两\d]+步|Step\s+\d+).*?)\s*#*\s*$",
            line,
        )
        if step:
            steps.append(step[1])
        images.extend(re.findall(r"!\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)", line))
    if marker:
        raise ValueError("Unclosed Markdown code fence")
    return {"h2": headings, "steps": steps, "code_sha256": codes, "images": images}


def file_record(root, path, inventory=True):
    data = local_file(root, path).read_bytes()
    result = {"sha256": digest(data)}
    if inventory and Path(path).suffix.lower() == ".md":
        result["markdown"] = markdown_inventory(data.decode("utf-8"))
    return result


def snapshot(root, files, protected):
    files = [relative_path(path) for path in files]
    protected = [relative_path(path) for path in protected]
    if len(set(files + protected)) != len(files + protected):
        raise ValueError("Selected and protected paths must be distinct, without duplicates")
    return {
        "schema_version": 1,
        "root_at_capture": str(Path(root).resolve()),
        "files": {path: file_record(root, path) for path in files},
        "protected": {path: file_record(root, path, False) for path in protected},
    }


def compare(root, baseline, headings="same", steps="same", code_policy="retain", images=None):
    if baseline.get("schema_version") != 1:
        raise ValueError("Unsupported snapshot schema")
    if images is not None and images < 0:
        raise ValueError("Image count must be nonnegative")
    checks, failures = [], []
    for path, old in baseline["files"].items():
        try:
            current = file_record(root, path)
        except (OSError, ValueError) as error:
            failures.append({"path": path, "check": "read", "error": str(error)})
            continue
        check = {"path": path, "changed": current["sha256"] != old["sha256"]}
        if "markdown" in old:
            before, after = old["markdown"], current["markdown"]
            check["before"] = before
            check["after"] = after
            for key, policy in (("h2", headings), ("steps", steps)):
                passed = policy == "any" or (
                    before[key] == after[key] if policy == "same"
                    else len(before[key]) == len(after[key])
                )
                if not passed:
                    failures.append({"path": path, "check": key, "policy": policy})
            missing = Counter(before["code_sha256"]) - Counter(after["code_sha256"])
            check["removed_code_blocks"] = dict(missing)
            if missing and code_policy == "retain":
                failures.append({"path": path, "check": "code_retention", "missing": dict(missing)})
            if images is not None and len(after["images"]) != images:
                failures.append({"path": path, "check": "image_count", "expected": images,
                                 "actual": len(after["images"])})
        checks.append(check)
    for path, old in baseline["protected"].items():
        try:
            unchanged = file_record(root, path, False)["sha256"] == old["sha256"]
            if not unchanged:
                failures.append({"path": path, "check": "protected_bytes"})
        except (OSError, ValueError) as error:
            failures.append({"path": path, "check": "protected_read", "error": str(error)})
    return {
        "passed": not failures, "files": checks, "failures": failures,
        "protected_files": len(baseline["protected"]),
        "limitations": "Structural and byte checks only; no semantic, source-truth, link or diagram validation",
    }


def write_result(result, out=None):
    encoded = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if out:
        with Path(out).open("x", encoding="utf-8") as handle:
            handle.write(encoded)
    else:
        sys.stdout.write(encoded)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    source = commands.add_parser("extract", help="Extract lines from a fixed local Git commit")
    source.add_argument("--repo", required=True)
    source.add_argument("--rev", required=True)
    source.add_argument("--path", required=True)
    source.add_argument("--start", type=int, required=True)
    source.add_argument("--end", type=int, required=True)
    source.add_argument("--base-url")
    source.add_argument("--out")
    capture = commands.add_parser("snapshot", help="Capture article structure and protected bytes")
    capture.add_argument("--root", required=True)
    capture.add_argument("--files", nargs="+", required=True)
    capture.add_argument("--protect", nargs="*", default=[])
    capture.add_argument("--out", required=True)
    check = commands.add_parser("compare", help="Compare current files to a saved snapshot")
    check.add_argument("--root", required=True)
    check.add_argument("--baseline", required=True)
    check.add_argument("--headings", choices=["same", "same-count", "any"], default="same")
    check.add_argument("--steps", choices=["same", "same-count", "any"], default="same")
    check.add_argument("--code-policy", choices=["retain", "any"], default="retain")
    check.add_argument("--images", type=int)
    check.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.command == "extract":
            result = extract(args.repo, args.rev, args.path, args.start, args.end, args.base_url)
        elif args.command == "snapshot":
            result = snapshot(args.root, args.files, args.protect)
        else:
            baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
            result = compare(args.root, baseline, args.headings, args.steps, args.code_policy, args.images)
        write_result(result, args.out)
        return 1 if result.get("passed") is False else 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
