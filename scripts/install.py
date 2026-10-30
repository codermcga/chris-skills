#!/usr/bin/env python3
"""Install portable skills and a managed reply footer; Python 3.9+, stdlib only."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
BEGIN = b"<!-- chris-skills:recap-and-learn:begin -->"
END = b"<!-- chris-skills:recap-and-learn:end -->"
OWNER = ".chris-skills-source"
OWNER_BYTES = b"codermcga/chris-skills\n"


def skill_body(data):
    text = data.decode("utf-8-sig").replace("\r\n", "\n")
    parts = text.split("\n---\n", 1)
    if not text.startswith("---\n") or len(parts) != 2:
        raise ValueError("SKILL.md must have YAML frontmatter")
    return parts[1].strip()


def merge_rules(original, body, preamble=""):
    original.decode("utf-8-sig")  # Reject unknown encodings without overwriting them.
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    block = BEGIN + newline + body.encode("utf-8").replace(b"\n", newline) + newline + END
    if original.count(BEGIN) != original.count(END) or original.count(BEGIN) > 1:
        raise ValueError("Broken or duplicate chris-skills markers; repair them first")
    if BEGIN in original:
        start = original.index(BEGIN)
        end = original.index(END)
        if end < start:
            raise ValueError("Reversed chris-skills markers")
        return original[:start] + block + original[end + len(END):]
    if original and original != b"\xef\xbb\xbf":
        separator = newline if original.endswith(b"\n") else newline + newline
        return original + separator + block + newline
    return original + preamble.encode("utf-8") + block + newline


def paths_for(args):
    if args.agent == "generic":
        if not args.skills_dir or not args.rules_file:
            raise ValueError("generic requires --skills-dir and --rules-file")
        return Path(args.skills_dir).expanduser(), Path(args.rules_file).expanduser(), ""
    config = json.loads((ROOT / "adapters" / (args.agent + ".json")).read_text(encoding="utf-8"))
    if args.project:
        project = Path(args.project).expanduser().resolve()
        skills = project / config["project_skills_dir"]
        rules = project / config["project_rules_file"]
    elif args.agent == "trae":
        raise ValueError("TRAE requires --project; see docs/installation.md for global UI setup")
    else:
        skills = Path(config["skills_dir"]).expanduser()
        if args.agent == "codex":
            codex_dir = Path(args.codex_home or os.environ.get("CODEX_HOME") or "~/.codex").expanduser()
            override = codex_dir / "AGENTS.override.md"
            rules = override if override.is_file() and override.read_bytes().strip() else codex_dir / "AGENTS.md"
        else:
            rules = Path(config["rules_file"]).expanduser()
    return (Path(args.skills_dir).expanduser() if args.skills_dir else skills,
            Path(args.rules_file).expanduser() if args.rules_file else rules,
            config.get("rules_preamble", ""))


def overlaps_source(path):
    return path == ROOT or ROOT in path.parents or path in ROOT.parents


def make_plan(args):
    skills_dir, rules_file, preamble = paths_for(args)
    skills_dir, rules_file = skills_dir.resolve(), rules_file.resolve()
    if overlaps_source(skills_dir) or overlaps_source(rules_file):
        raise ValueError("Installation targets must be outside the source repository")
    available = {p.name: p for p in ROOT.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()}
    selected = args.skill or sorted(available)
    missing = set(selected) - available.keys()
    if missing:
        raise ValueError("Unknown skills: " + ", ".join(sorted(missing)))
    plan = {}
    for name in dict.fromkeys(selected):
        source, target = available[name], skills_dir / name
        # Do not silently replace a symlinked or independently maintained skill.
        if target.is_symlink():
            raise ValueError("Skill target is a symlink: " + str(target))
        owner = target / OWNER
        if target.exists() and (not owner.is_file() or owner.read_bytes() != OWNER_BYTES):
            raise ValueError("Unmanaged skill already exists; choose another --skills-dir: " + str(target))
        if overlaps_source(target.resolve()):
            raise ValueError("Skill target overlaps source: " + str(target))
        for file in sorted(source.rglob("*")):
            if file.is_symlink():
                raise ValueError("Source skill contains symlink: " + str(file))
            if not file.is_file() or "__pycache__" in file.parts:
                continue
            data = file.read_bytes()
            if args.agent == "claude" and file.name == "SKILL.md":
                metadata = source / "agents" / "openai.yaml"
                if metadata.is_file() and re.search(r"^\s*allow_implicit_invocation:\s*false\s*$", metadata.read_text(encoding="utf-8"), re.M):
                    text = data.decode("utf-8-sig").replace("\r\n", "\n")
                    if "disable-model-invocation:" not in text.split("\n---\n", 1)[0]:
                        data = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1).encode("utf-8")
            destination = target / file.relative_to(source)
            if destination.is_symlink() or target.resolve() not in destination.resolve().parents:
                raise ValueError("Unsafe installed file path: " + str(destination))
            plan[destination] = data
        plan[owner] = OWNER_BYTES
    original = rules_file.read_bytes() if rules_file.exists() else b""
    # Selecting only another skill does not implicitly enable the reply footer.
    if "recap-and-learn" in selected:
        body = skill_body((ROOT / "recap-and-learn" / "SKILL.md").read_bytes())
        plan[rules_file] = merge_rules(original, body, preamble)
    return plan, skills_dir, rules_file


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=["codex", "claude", "trae", "generic"])
    parser.add_argument("--project", help="Target project; required for TRAE")
    parser.add_argument("--codex-home", help="Override CODEX_HOME for Codex global instructions")
    parser.add_argument("--skills-dir", help="Override the host skill discovery directory")
    parser.add_argument("--rules-file", help="Override the host always-on instruction file")
    parser.add_argument("--skill", action="append", help="Install one skill; repeat to select several; default: all")
    parser.add_argument("--check", action="store_true", help="Read-only check; exit 0 if current, 1 if changes needed")
    args = parser.parse_args(argv)
    try:
        plan, skills_dir, rules_file = make_plan(args)
        changes = [(path, data) for path, data in plan.items() if not path.is_file() or path.read_bytes() != data]
        print("Skills: " + str(skills_dir))
        print("Rules:  " + str(rules_file))
        if not changes:
            print("Up to date; no files changed.")
            return 0
        if args.check:
            for path, _ in changes:
                print("NEEDS UPDATE: " + str(path))
            return 1
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        # Preflight is complete. Back up changed files beside their originals.
        for path, data in changes:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                backup = path.with_name(path.name + ".chris-skills.bak." + stamp)
                shutil.copy2(path, backup)
                print("BACKUP: " + str(backup))
            path.write_bytes(data)
            print("WROTE:  " + str(path))
        print("Installed. Start a new agent session to verify loading and behavior.")
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
