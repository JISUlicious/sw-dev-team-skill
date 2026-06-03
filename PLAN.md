# Goal

Build a portable, self-contained Agent Skill — `skill-creator` — that guides Claude
through authoring *new* Agent Skills correctly, with the official Agent Skills
documentation bundled in as a progressive-disclosure reference so the skill works
offline as portable documentation.

Success criteria:
- A skill at `.claude/skills/skill-creator/` that loads in Claude Code (valid frontmatter, `/skill-creator` works).
- Bundles the official spec, Claude Code features, and authoring best practices as
  reference files (one level deep from SKILL.md), captured verbatim-where-possible
  from official docs with source URLs + fetch date.
- Ships a template (`assets/SKILL.template.md`) and a validator (`scripts/validate_skill.py`)
  that enforces the documented frontmatter rules.
- `SKILL.md` body stays concise (< 500 lines) and points to the references.

## Steps

1. Research official docs — DONE. Sources captured:
   - code.claude.com/docs/en/skills (Claude Code features)
   - platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (spec/architecture)
   - platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
   Verify: all frontmatter rules + limits recorded.
2. Write `reference/` files (specification, claude-code-features, best-practices).
   Verify: each is self-contained, has a TOC if >100 lines, links nowhere deeper.
3. Write `assets/SKILL.template.md`. Verify: passes the validator.
4. Write `scripts/validate_skill.py`. Verify: catches bad name/description/missing frontmatter; passes on a good skill.
5. Write `SKILL.md` (the orchestrating workflow). Verify: < 500 lines, references resolve, validator passes.
6. Run validator against the skill itself + the template. Verify: clean.
7. Commit + push to `claude/agent-skill-creator-307BM`.

Status: Steps 1–6 done. Validator passes on the skill + template (0 warnings) and fails
correctly on a malformed skill. SKILL.md body is 141 lines. Step 7 (commit/push) in progress.

## Out of scope

- Uploading the skill to the API / claude.ai.
- A general skill registry or installer.
- Editing the existing AGENTS.md team-coordination templates.
