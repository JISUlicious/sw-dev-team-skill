---
name: skill-creator
description: Create, structure, and validate new Agent Skills (SKILL.md files) following the official Agent Skills standard and Anthropic's authoring best practices. Use when the user wants to build, author, scaffold, write, or fix a skill, a SKILL.md, or a Claude Code slash command.
allowed-tools: Read Write Edit Glob Grep Bash(python3 *) Bash(mkdir *)
---

# Skill Creator

Author a new Agent Skill that Claude can discover and use reliably. This skill bundles
the official documentation as offline reference (`reference/`), a starting template
(`assets/`), and a validator (`scripts/`), so you can create a correct skill without
network access.

A Skill is a directory whose entrypoint is a `SKILL.md` file: YAML frontmatter (`name` +
`description`) followed by a Markdown body of instructions. Files alongside it
(`reference/`, `scripts/`, `assets/`) load only when needed — this is *progressive
disclosure*, and getting it right is most of what makes a good skill.

## Workflow

Copy this checklist into your response and tick items off as you go:

```
Skill creation progress:
- [ ] Step 1: Clarify what the skill does and when it should trigger
- [ ] Step 2: Choose name + location
- [ ] Step 3: Scaffold the directory
- [ ] Step 4: Write the description (discovery hinges on this)
- [ ] Step 5: Write a concise SKILL.md body
- [ ] Step 6: Split heavy material into reference/ and scripts/
- [ ] Step 7: Validate
- [ ] Step 8: Test by triggering it
```

### Step 1 — Clarify intent

Pin down two things before writing anything:
- **What** the skill does (the capability).
- **When** Claude should reach for it (the triggers — phrases, file types, tasks).

If either is vague, ask. A skill whose triggers are fuzzy either never fires or fires
constantly. Also decide the content shape (see `reference/claude-code-features.md`
§ Types of skill content):
- **Reference content** — standing knowledge applied inline (conventions, domain facts).
- **Task content** — step-by-step actions, often `/invoked` directly; consider
  `disable-model-invocation: true` for anything with side effects (deploy, commit, send).

### Step 2 — Name and location

Pick a `name`: lowercase letters/numbers/hyphens only, ≤ 64 chars, no XML, and it must
**not** contain the reserved words `anthropic` or `claude`. Prefer gerund form
(`processing-pdfs`, `analyzing-logs`) or a clear noun phrase. Avoid `helper`, `utils`, `tools`.
(Exact rules: `reference/specification.md` § Required frontmatter fields. Naming guidance:
`reference/best-practices.md` § Naming conventions.)

Choose where it lives (this also sets the `/command` name — the directory name wins):

| Location | Path | Scope |
| :-- | :-- | :-- |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This repo (commit it to share) |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where the plugin is enabled |

### Step 3 — Scaffold

```bash
mkdir -p .claude/skills/<name>
cp "${CLAUDE_SKILL_DIR}/assets/SKILL.template.md" .claude/skills/<name>/SKILL.md
```

Add `reference/`, `scripts/`, or `assets/` subdirectories only when Step 6 calls for them.

### Step 4 — Write the description

This is the single most important field — Claude selects among many skills using only
`name` + `description`. Requirements: non-empty, ≤ 1024 chars, no XML tags, **third
person**, and it must state **both what the skill does and when to use it**, key terms first.

- Good: `Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDFs or when the user mentions forms or document extraction.`
- Avoid: `Helps with documents` · `I can help you process PDFs`

Note: the field's hard cap is 1,024 chars (`reference/specification.md` § Required
frontmatter fields); separately, the Claude Code listing truncates combined `description` +
`when_to_use` at ~1,536 chars, so front-load the primary use case. Full guidance:
`reference/best-practices.md` § Writing effective descriptions.

### Step 5 — Write a concise body

The body loads in full when the skill triggers and **stays in context for the rest of the
session** (`reference/claude-code-features.md` § Skill content lifecycle), so every line is
a recurring token cost. Write standing instructions, not one-time narration. Assume Claude
is already smart — add only what it doesn't know. Match instruction specificity to task
fragility — high freedom for open-ended judgment, low freedom / exact commands for fragile
sequences (`reference/best-practices.md` § Set appropriate degrees of freedom). Keep it
under 500 lines.

Use the structural patterns — template, examples, workflow-with-checklist, validation
feedback loop — in `reference/best-practices.md` (§ Common patterns, § Workflows and
feedback loops).

### Step 6 — Split heavy material out

Move large reference docs, API specs, long examples, and scripts into bundled files so
they cost nothing until read:
- `reference/*.md` — detailed docs Claude reads on demand. Keep links **one level deep**
  from SKILL.md. Give any file > 100 lines a table of contents.
- `scripts/*` — deterministic utilities Claude **executes** (output only enters context).
  Reference them with `${CLAUDE_SKILL_DIR}/scripts/...` so paths resolve at any install level.
- Use forward slashes in every path. State whether Claude should *run* a script or *read* it.

The one-level-deep and table-of-contents rules are in `reference/best-practices.md`
§ Progressive disclosure patterns; `${CLAUDE_SKILL_DIR}` and the other substitutions are in
`reference/claude-code-features.md` § String substitutions.

### Step 7 — Validate

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_skill.py" .claude/skills/<name>
```

The validator checks the frontmatter rules (name/description limits, reserved words, XML),
body length, and path style. Fix every error; weigh each warning.

### Step 8 — Test

Trigger the skill the way a user would (a request matching the description) and via
`/<name>` directly. If it doesn't fire, strengthen the description's keywords; if it fires
too eagerly, narrow the description or set `disable-model-invocation: true`. Iterate by
observing real behavior — see `reference/best-practices.md` § Evaluation and iteration.
For triggering problems (won't fire, fires too often, or description cut short), see
`reference/claude-code-features.md` § Troubleshooting.

## Frontmatter quick reference

`name` and `description` are the core fields. Claude Code adds optional fields:
`disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`,
`argument-hint`, `arguments`, `model`, `effort`, `context: fork`, `agent`, `paths`, `hooks`.
Full table, string substitutions (`$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, …), and dynamic
context injection (`` !`cmd` ``) are in `reference/claude-code-features.md`.

## Bundled reference (portable docs)

This skill ships the official documentation offline so it works without network access.
**Look things up here rather than relying on memory** — frontmatter field names, character
limits, and syntax drift over time. Read the file that owns the topic; if the answer isn't
in the summary, open the matching mirror in `reference/raw/`. Route by topic:

| When you need… | Read |
| :-- | :-- |
| What a skill is, the architecture, progressive disclosure, the **exact** `name`/`description` rules and limits, security, runtime/surface differences | [reference/specification.md](reference/specification.md) |
| A Claude Code feature — content types, full frontmatter field table, invocation control, `$ARGUMENTS`/`${CLAUDE_SKILL_DIR}`, dynamic `` !`cmd` `` injection, `context: fork`, locations, command names, troubleshooting | [reference/claude-code-features.md](reference/claude-code-features.md) |
| How to author well — descriptions, conciseness, degrees of freedom, progressive-disclosure patterns, workflows, feedback loops, anti-patterns, evaluation, the checklist | [reference/best-practices.md](reference/best-practices.md) |
| The complete source for any row above, or anything a summary omits | [reference/raw/](reference/raw/) — verbatim mirrors; provenance + checksums in `reference/raw/SOURCES.md` |

The three `reference/*.md` files are curated summaries — the fast reading layer. The
`reference/raw/*.md` files are byte-for-byte copies of the official pages; treat the raw
page as the authority if a summary and its source ever disagree.

## Security note

Skills grant Claude new instructions and code. When creating one that runs scripts or
fetches external data, keep its behavior matched to its stated purpose, and only build on
skills from trusted sources. See `reference/specification.md` § Security considerations.
