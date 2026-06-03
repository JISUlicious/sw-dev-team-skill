# Agent Skills — Specification & Architecture

This is a curated summary. The full, unmodified source page is mirrored at
[raw/agent-skills-overview.md](raw/agent-skills-overview.md) — drill into it for anything
not covered here. Provenance: [raw/SOURCES.md](raw/SOURCES.md).

Captured from the official Agent Skills overview on 2026-06-03.
Source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Open standard: https://agentskills.io · Reference implementation: https://github.com/anthropics/skills

## Contents
- What Agent Skills are
- How Skills work (progressive disclosure, three loading levels)
- The Skills architecture
- Skill structure & frontmatter spec (exact field rules and limits)
- Where Skills work (surfaces)
- Runtime environment constraints
- Security considerations

## What Agent Skills are

Agent Skills are modular capabilities that extend Claude's functionality. Each Skill
packages instructions, metadata, and optional resources (scripts, templates) that Claude
uses automatically when relevant. They are reusable, filesystem-based resources that give
Claude domain-specific expertise — workflows, context, and best practices — that turn a
general-purpose agent into a specialist.

Unlike prompts (conversation-level instructions for one-off tasks), Skills load on demand
and remove the need to repeatedly paste the same guidance across conversations.

Key benefits: **specialize** Claude for a domain, **reduce repetition** (create once, use
automatically), and **compose** capabilities into complex workflows.

Skills follow the [Agent Skills](https://agentskills.io) open standard, which works across
multiple AI tools; Claude Code extends it with features documented in
`claude-code-features.md`.

## How Skills work

Claude operates in a VM-like environment with filesystem access, so Skills exist as
directories containing instructions, executable code, and reference materials — organized
like an onboarding guide for a new teammate. This enables **progressive disclosure**:
Claude loads information in stages as needed, rather than consuming context upfront.

### The three loading levels

| Level | When loaded | Token cost | Content |
| :-- | :-- | :-- | :-- |
| **1: Metadata** | Always, at startup | ~100 tokens per skill | `name` + `description` from YAML frontmatter |
| **2: Instructions** | When the skill is triggered | Under ~5k tokens | The SKILL.md body |
| **3+: Resources** | As needed | Effectively unlimited | Bundled files; scripts run via bash without loading their source |

- **Level 1 — Metadata (always loaded).** The frontmatter `name` and `description` are
  loaded into the system prompt at startup. Lightweight, so you can install many skills
  without a context penalty — Claude only knows each skill exists and when to use it.
- **Level 2 — Instructions (loaded when triggered).** When a request matches a skill's
  description, Claude reads `SKILL.md` from the filesystem via bash; only then does the
  body enter context.
- **Level 3+ — Resources and code (loaded as needed).** Additional markdown files
  (specialized guidance), executable scripts (deterministic operations Claude runs via
  bash — only output enters context), and reference resources (schemas, API docs,
  templates, examples). Read only when referenced.

Progressive disclosure ensures only relevant content occupies the context window at any
given time.

## The Skills architecture

Skills run in a code execution environment with filesystem access, bash, and code
execution. Claude interacts with a skill the way you'd navigate files on your computer.

- **On-demand file access:** Claude reads only the files a task needs. A skill can bundle
  dozens of reference files; unused ones stay on disk consuming zero tokens.
- **Efficient script execution:** When Claude runs `validate_form.py`, the script's source
  never enters context — only its output ("Validation passed", or specific errors). This is
  far cheaper than having Claude generate equivalent code.
- **No practical limit on bundled content:** because files cost nothing until read, skills
  can include comprehensive API docs, large datasets, or extensive examples.

Example load sequence for a PDF skill:
1. Startup: system prompt includes `PDF Processing — Extract text and tables…`.
2. User: "Extract the text from this PDF and summarize it."
3. Claude runs bash to read `pdf-skill/SKILL.md` → instructions enter context.
4. Form filling isn't needed, so `FORMS.md` is **not** read.
5. Claude completes the task from the SKILL.md instructions.

## Skill structure

Every Skill requires a `SKILL.md` file with YAML frontmatter followed by a Markdown body:

```yaml
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
[Clear, step-by-step guidance for Claude to follow]

## Examples
[Concrete examples of using this Skill]
```

A typical directory:

```text
my-skill/
├── SKILL.md              # Main instructions (required)
├── FORMS.md              # Form-filling guide (loaded as needed)
├── reference.md          # API reference (loaded as needed)
├── examples.md           # Usage examples (loaded as needed)
└── scripts/
    └── validate.py       # Script Claude executes (not loaded into context)
```

Only `SKILL.md` is required. Everything else is optional and supports more powerful skills:
templates to fill in, example outputs, scripts to execute, or detailed reference docs.
Reference supporting files from `SKILL.md` so Claude knows what they contain and when to load them.

### Required frontmatter fields

**`name`** and **`description`** are the two required/recommended fields.

`name`:
- Maximum **64 characters**.
- Only **lowercase letters, numbers, and hyphens**.
- Cannot contain XML tags.
- Cannot contain the reserved words **"anthropic"** or **"claude"**.

`description`:
- Must be **non-empty**.
- Maximum **1024 characters**.
- Cannot contain XML tags.
- Should describe **both what the Skill does and when to use it**, in the third person.

The `description` is critical for skill selection — Claude uses it to choose the right
skill from potentially 100+ available. (Claude Code may truncate the combined
`description` + `when_to_use` at ~1,536 characters in the listing, so put the key use case
first.)

## Where Skills work

- **Claude API:** supports pre-built and custom Skills via the `container` parameter +
  code execution tool (beta headers required). Custom skills are workspace-wide.
- **Claude Code:** custom, filesystem-based skills only — directories with `SKILL.md`,
  discovered automatically. No API upload needed. (See `claude-code-features.md`.)
- **claude.ai:** pre-built skills work behind the scenes; custom skills upload as zip files
  (per-user, not org-managed).

Custom Skills **do not sync across surfaces** — manage/upload separately for each.

## Runtime environment constraints

The runtime depends on the surface:
- **claude.ai:** network access varies by user/admin settings (full, partial, or none).
- **Claude API:** **no network access** and **no runtime package installation** — only
  pre-installed packages are available.
- **Claude Code:** **full network access** (same as any program on the user's machine);
  install packages locally, not globally, to avoid interfering with the user's system.

List required packages in your SKILL.md and don't assume tools are installed.

## Security considerations

Use Skills only from trusted sources — ones you created or obtained from Anthropic. Skills
give Claude new capabilities through instructions and code; a malicious skill can direct
Claude to invoke tools or run code in ways that don't match its stated purpose.

- **Audit thoroughly:** review every bundled file (SKILL.md, scripts, images, resources)
  for unusual patterns — unexpected network calls, odd file access, operations unrelated to
  the stated purpose.
- **External sources are risky:** skills that fetch external URLs can ingest malicious
  instructions; even trustworthy skills can be compromised if dependencies change.
- **Tool misuse / data exposure:** a malicious skill can misuse file/bash/code-exec tools or
  leak sensitive data.
- **Treat like installing software:** be especially careful integrating skills into
  production systems with sensitive data or critical operations.
