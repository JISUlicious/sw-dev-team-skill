#!/usr/bin/env python3
"""Validate an Agent Skill against the official SKILL.md rules.

Usage:
    python3 validate_skill.py <path-to-skill-dir-or-SKILL.md>

Checks the frontmatter rules and structural guidance documented at:
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
  - https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
  - https://code.claude.com/docs/en/skills

Exit code 0 if there are no errors (warnings are allowed), 1 otherwise.
Uses only the Python standard library, so it runs anywhere Python 3 is available.
"""

import re
import sys
from pathlib import Path

# Documented limits.
NAME_MAX = 64
DESCRIPTION_MAX = 1024
BODY_MAX_LINES = 500
TOC_THRESHOLD_LINES = 100  # reference files longer than this should carry a table of contents
RESERVED_WORDS = ("anthropic", "claude")
NAME_PATTERN = re.compile(r"^[a-z0-9-]+$")
XML_TAG = re.compile(r"<[^>]+>")


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str) or (None, reason) if no valid frontmatter block."""
    if not text.startswith("---"):
        return None, "SKILL.md must start with a YAML frontmatter block delimited by '---'."
    # Split on the first two '---' fences.
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "Frontmatter block is not closed with a second '---'."
    raw, body = parts[1], parts[2]
    fm = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            continue
        # Only treat top-level (non-indented) keys as fields.
        if line[0] in (" ", "\t"):
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, body


def check(skill_md: Path):
    errors = []
    warnings = []

    text = skill_md.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if fm is None:
        return [body], []  # body holds the reason string here

    # --- name (optional in Claude Code, but validate when present) ---
    name = fm.get("name")
    if name is not None:
        # Strip surrounding quotes if any.
        name = name.strip().strip("'\"")
        if not name:
            errors.append("frontmatter 'name' is present but empty.")
        else:
            if len(name) > NAME_MAX:
                errors.append(f"'name' is {len(name)} chars; max is {NAME_MAX}.")
            if not NAME_PATTERN.match(name):
                errors.append("'name' must contain only lowercase letters, numbers, and hyphens.")
            if XML_TAG.search(name):
                errors.append("'name' must not contain XML tags.")
            for word in RESERVED_WORDS:
                if word in name.lower():
                    errors.append(f"'name' must not contain the reserved word '{word}'.")
    else:
        warnings.append("no 'name' field; the command name will default to the directory name.")

    # --- description (required/recommended) ---
    desc = fm.get("description")
    if desc is None:
        errors.append("missing 'description' — Claude needs it to know when to use the skill.")
    else:
        desc = desc.strip().strip("'\"")
        if not desc:
            errors.append("'description' must be non-empty.")
        else:
            if len(desc) > DESCRIPTION_MAX:
                errors.append(f"'description' is {len(desc)} chars; max is {DESCRIPTION_MAX}.")
            if XML_TAG.search(desc):
                errors.append("'description' must not contain XML tags.")
            lowered = desc.lower()
            if not any(w in lowered for w in ("use when", "use for", "use to", "when ")):
                warnings.append(
                    "'description' should say *when* to use the skill (e.g. 'Use when ...'), "
                    "not just what it does."
                )
            for opener in ("i can ", "i will ", "i help", "you can ", "you should ", "we "):
                if lowered.startswith(opener) or f" {opener}" in lowered:
                    warnings.append(
                        "write 'description' in the third person (e.g. 'Processes X'), "
                        "not first/second person."
                    )
                    break

    # --- body length ---
    body_lines = body.strip("\n").count("\n") + 1 if body.strip() else 0
    if body_lines > BODY_MAX_LINES:
        warnings.append(
            f"SKILL.md body is {body_lines} lines; keep it under {BODY_MAX_LINES} and move "
            "detail into reference files."
        )

    # --- Windows-style paths anywhere in the file ---
    for m in re.finditer(r"[\w.]+\\[\w./\\-]+", text):
        warnings.append(
            f"possible Windows-style path '{m.group(0)}' — use forward slashes."
        )
        break  # one nudge is enough

    return errors, warnings


def check_reference_files(skill_dir: Path):
    """Warn about reference files >100 lines without an apparent table of contents."""
    warnings = []
    for md in sorted(skill_dir.rglob("*.md")):
        if md.name == "SKILL.md":
            continue
        # Skip verbatim source mirrors — they are reproduced as-is, not authored here.
        if "raw" in md.relative_to(skill_dir).parts:
            continue
        lines = md.read_text(encoding="utf-8").splitlines()
        if len(lines) > TOC_THRESHOLD_LINES:
            head = "\n".join(lines[:40]).lower()
            if "contents" not in head and "table of contents" not in head:
                rel = md.relative_to(skill_dir)
                warnings.append(
                    f"{rel} is {len(lines)} lines but has no table of contents near the top; "
                    "add one so partial reads still show its scope."
                )
    return warnings


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2

    target = Path(argv[1])
    if target.is_dir():
        skill_dir = target
        skill_md = target / "SKILL.md"
    elif target.is_file() and target.suffix == ".md":
        # Accept SKILL.md or an explicitly-passed skill markdown file (e.g. a template).
        skill_md = target
        skill_dir = target.parent
    else:
        print(f"error: expected a skill directory or a SKILL.md file, got {target}")
        return 2

    if not skill_md.is_file():
        print(f"error: no SKILL.md found at {skill_md}")
        return 2

    errors, warnings = check(skill_md)
    warnings += check_reference_files(skill_dir)

    for w in warnings:
        print(f"  warning: {w}")
    for e in errors:
        print(f"  ERROR:   {e}")

    name = skill_dir.name
    if errors:
        print(f"\n✗ {name}: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"\n✓ {name}: valid ({len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
